#!/usr/bin/env python3
"""Geocode the FA26 class buildings to lat/lng for the campus map.

Source: UCSD's public "Building Points" layer (the same data behind the
official campus map at experience.arcgis.com):
  admin-enterprise-gis.ucsd.edu/.../AdministrationServices/Buildings_Public/MapServer/0

Matches each distinct building name in data/webreg.db to a building point
(exact → distinctive-token overlap, with a UCSD-area bounds filter and manual
overrides for a few tricky names), and writes site/data/buildings.json:
  { "<building name as stored>": {"lat": .., "lng": ..}, ... }

Committed output — run only when buildings change: python3 scripts/geocode_buildings.py
"""
import json
import re
import sqlite3
import ssl
import urllib.request
from pathlib import Path

# UCSD's GIS host presents an internal cert chain Python doesn't trust; this is
# a public, read-only endpoint, so skip verification (same data curl fetches).
_SSL = ssl.create_default_context()
_SSL.check_hostname = False
_SSL.verify_mode = ssl.CERT_NONE

ROOT = Path(__file__).resolve().parent.parent
SVC = ("https://admin-enterprise-gis.ucsd.edu/server/rest/services/"
       "AdministrationServices/Buildings_Public/MapServer/0/query"
       "?where=1%3D1&outFields=FacilityLongName,BuildingAliases,Longitude,Latitude"
       "&returnGeometry=false&resultRecordCount=3000&f=json")

# A few buildings whose names don't cleanly match a point (verified by hand).
OVERRIDES = {
    "MCTF - Marine Conservation and Technology": (32.87100, -117.25213),
    "Ridgewalk Academic Complex": (32.88042, -117.24095),
    "Robinson Building 1": (32.88460, -117.24110),
    "Biomedical Research Facility II": (32.87428, -117.23504),
    "Leichtag Biomedical Research Building": (32.87665, -117.23686),
    "Ledden Auditorium": (32.87668, -117.24054),   # in the Humanities/HSS area
}
GENERIC = {"building", "bldg", "hall", "center", "centre", "the", "of", "and"}


def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", (s or "").lower())).strip()


def distinctive(s):
    return set(norm(s).split()) - GENERIC


def on_campus(lat, lng):
    return lat and lng and 32.70 <= lat <= 32.92 and -117.30 <= lng <= -117.10


def main():
    raw = json.loads(urllib.request.urlopen(SVC, timeout=60, context=_SSL).read())
    cands = []
    for f in raw["features"]:
        a = f["attributes"]
        lat, lng = a.get("Latitude"), a.get("Longitude")
        if not on_campus(lat, lng):
            continue
        names = [a.get("FacilityLongName") or ""]
        names += [x.strip() for x in (a.get("BuildingAliases") or "").split("|")]
        for n in filter(None, names):
            cands.append((norm(n), lat, lng))

    conn = sqlite3.connect(ROOT / "data" / "webreg.db")
    mine = [r[0] for r in conn.execute(
        "SELECT DISTINCT building FROM sections s JOIN courses c ON c.id=s.course_id "
        "WHERE c.term_code='FA26' AND building NOT IN ('','TBA','RCLAS','ONLINE')")]

    out, misses = {}, []
    for name in sorted(mine):
        if name in OVERRIDES:
            lat, lng = OVERRIDES[name]
            out[name] = {"lat": round(lat, 5), "lng": round(lng, 5)}
            continue
        nf = norm(name)
        hit = next((c for c in cands if c[0] == nf), None)
        if not hit:
            myd, best = distinctive(name), None
            for cnf, lat, lng in cands:
                cd = distinctive(cnf)
                if not myd or not cd or not (cd <= myd or myd <= cd):
                    continue
                score = len(myd & cd) / max(1, len(myd | cd))
                if score > 0 and (not best or score > best[0]):
                    best = (score, lat, lng)
            hit = (None, best[1], best[2]) if best else None
        if hit:
            out[name] = {"lat": round(hit[1], 5), "lng": round(hit[2], 5)}
        else:
            misses.append(name)

    dst = ROOT / "site" / "data" / "buildings.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, separators=(",", ":")))
    print(f"geocoded {len(out)}/{len(mine)} buildings -> {dst}")
    if misses:
        print("MISSES (no coordinates):", misses)


if __name__ == "__main__":
    main()
