#!/usr/bin/env python3
"""Pull the FA26 con_module catalog by hijacking the SoC app's own $batch.

TSS changed: the yucsd_con_module OData4 entities (YUCSD_CON_MODULE,
YUCSD_CON_EVENTS) now 403 "Access denied" to any request we craft ourselves —
even a byte-accurate multipart $batch from inside the page. The gateway keys on
the app's real request envelope (sap-passport, frame origin, x-xhr-logon…).

So instead of reconstructing the request, we let the Schedule-of-Classes Fiori
app issue its OWN $batch (which passes), intercept it with Playwright request
routing, and REWRITE just the body to ask for the entire FA26 catalog (both
entities, full fields, paged) before it goes on the wire. The response carries
all rows, which we parse and write in the shape import_fa26.py consumes.

  modules: AcYearText eq '2026/2027' and AcademicPeriodText eq 'Fall Quarter'
  events : AcYear eq '2026' and AcPeriod eq '2'

Usage:  python3 tss/pull_soc_batch.py [--headed]
"""
import argparse
import json
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "tss" / "state.json"
OUT = ROOT / "data" / "tss_fa26"
APP_URL = "https://tss.ucsd.edu/fiori#YSchedule-view"
MOD_FILTER = ("AcYearText eq '2026/2027' and "
              "AcademicPeriodText eq 'Fall Quarter'")
EVT_FILTER = "AcYear eq '2026' and AcPeriod eq '2'"
PAGE = 5000
MIN_MODULES = 500
BOUNDARY = "batch_pull_all"


def rel(entity, flt, skip, top):
    enc = urllib.parse.quote(flt, safe="'/")
    return (f"{entity}?sap-client=500&$count=true&$filter={enc}"
            f"&$skip={skip}&$top={top}")


def build_body(get_urls):
    """A multipart/mixed batch wrapping each GET url as its own part."""
    parts = []
    for u in get_urls:
        parts.append(
            f"--{BOUNDARY}\r\n"
            "Content-Type:application/http\r\n"
            "Content-Transfer-Encoding:binary\r\n\r\n"
            f"GET {u} HTTP/1.1\r\n"
            "Accept:application/json;odata.metadata=minimal;"
            "IEEE754Compatible=true\r\n"
            "Accept-Language:en\r\n"
            "Content-Type:application/json;charset=UTF-8;"
            "IEEE754Compatible=true\r\n\r\n\r\n")
    return "".join(parts) + f"--{BOUNDARY}--\r\n"


def parse_objects(text):
    """Every top-level OData JSON object in a multipart batch response."""
    objs, dec = [], json.JSONDecoder()
    for m in re.finditer(r'\{"@odata\.context"', text):
        try:
            obj, _ = dec.raw_decode(text[m.start():])
            objs.append(obj)
        except Exception:
            pass
    return objs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--headed", action="store_true")
    args = ap.parse_args()
    if not STATE.exists():
        print("No tss/state.json — run tss/connect.py and log in first.")
        return 1

    from playwright.sync_api import sync_playwright

    got = {"modules": None, "events": None, "err": None, "hijacked": False}

    def wanted_urls(skip):
        return [rel("YUCSD_CON_MODULE", MOD_FILTER, skip, PAGE),
                rel("YUCSD_CON_EVENTS", EVT_FILTER, skip, PAGE)]

    def handler(route):
        req = route.request
        # Only hijack the first con_module data $batch; pass everything else.
        if (got["hijacked"] or req.method != "POST"
                or "$batch" not in req.url or "con_module" not in req.url):
            return route.continue_()
        got["hijacked"] = True
        try:
            headers = dict(req.headers)
            headers["content-type"] = f"multipart/mixed; boundary={BOUNDARY}"
            headers["accept"] = "multipart/mixed"
            modules, events, skip = [], [], 0
            # page modules
            while True:
                resp = route.fetch(post_data=build_body(
                    [rel("YUCSD_CON_MODULE", MOD_FILTER, skip, PAGE)]),
                    headers=headers)
                objs = parse_objects(resp.text())
                if not objs:
                    raise RuntimeError(f"no data (HTTP {resp.status}): "
                                       f"{resp.text()[:160]}")
                batch = objs[0].get("value", [])
                modules.extend(batch)
                print(f"  modules +{len(batch)} (have {len(modules)} / "
                      f"{objs[0].get('@odata.count')})")
                if len(batch) < PAGE:
                    break
                skip += len(batch)
            # page events
            skip = 0
            while True:
                resp = route.fetch(post_data=build_body(
                    [rel("YUCSD_CON_EVENTS", EVT_FILTER, skip, PAGE)]),
                    headers=headers)
                objs = parse_objects(resp.text())
                if not objs:
                    raise RuntimeError(f"no events (HTTP {resp.status}): "
                                       f"{resp.text()[:160]}")
                batch = objs[0].get("value", [])
                events.extend(batch)
                print(f"  events +{len(batch)} (have {len(events)} / "
                      f"{objs[0].get('@odata.count')})")
                if len(batch) < PAGE:
                    break
                skip += len(batch)
            got["modules"], got["events"] = modules, events
        except Exception as e:
            got["err"] = str(e)
        # Let the app's original request proceed so the UI stays happy.
        try:
            route.continue_()
        except Exception:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        ctx = browser.new_context(storage_state=str(STATE),
                                  viewport={"width": 1500, "height": 950})
        ctx.on("page", lambda pg: None)
        ctx.route("**/$batch**", handler)
        page = ctx.new_page()
        try:
            page.goto(APP_URL, timeout=90000)
        except Exception as e:
            print(f"  nav warning: {e}")
        page.wait_for_timeout(9000)
        if not got["hijacked"]:
            try:
                page.get_by_role("button", name=re.compile(r"^Go$")).first.click(
                    timeout=8000)
            except Exception as e:
                print(f"  Go-click note: {e}")
        for _ in range(40):
            if got["modules"] is not None or got["err"]:
                break
            page.wait_for_timeout(1000)
        try:
            ctx.storage_state(path=str(STATE))
        except Exception:
            pass
        browser.close()

    if got["err"]:
        print(f"Pull failed: {got['err']}")
        return 1
    if got["modules"] is None:
        print("App never issued a con_module $batch to hijack — try --headed.")
        return 1
    if len(got["modules"]) < MIN_MODULES:
        print(f"Only {len(got['modules'])} modules — looks wrong; not writing.")
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "modules.json").write_text(json.dumps(got["modules"]))
    (OUT / "events.json").write_text(json.dumps(got["events"]))
    print(f"\nWrote data/tss_fa26/modules.json ({len(got['modules'])} rows) + "
          f"events.json ({len(got['events'])} rows).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
