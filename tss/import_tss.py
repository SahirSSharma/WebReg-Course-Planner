#!/usr/bin/env python3
"""Map raw TSS OData captures (data/tss_raw/) into the FROZEN parsed format.

Input : data/tss_raw/*.json — bodies recorded by tss/connect.py while
        browsing the TSS Schedule of Classes (SAP SLcM OData v2).
Output: data/parsed/FA26/<SUBJ>.json  (frozen format, see seed.py header):
          [{subject, number, title, units, restriction, sections: [
             {section_id, group, type, code, days, time_start, time_end,
              building, room, instructor, avail, limit, waitlist,
              enrollable, cancelled, note}]}]
        + data/terms.json gains {"code": "FA26", ..., "source": "tss"}.

Because the exact SAP entity schema is unknowable before the first real
capture, all field-name guesses live in CONFIG below. Workflow:
  1. python3 tss/import_tss.py --inspect     # dump the keys the captures use
  2. edit CONFIG["field_map"] (2-minute job: put the real key names FIRST
     in each candidate list — matching is case-insensitive)
  3. python3 tss/import_tss.py               # writes data/parsed/FA26/
  4. python3 seed.py

Usage:
  python3 tss/import_tss.py [--inspect] [--raw-dir DIR] [--out-dir DIR]
                            [--terms-json FILE] [--term FA26]
"""
import argparse
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ============================================================================
# CONFIG — EDIT AFTER FIRST CAPTURE (run --inspect to see the real key names).
# Every entry maps our frozen field -> candidate source keys, tried in order,
# matched case-insensitively against each OData entity's property names.
# The pre-filled names are educated guesses for SAP SLcM / a UCSD custom
# Y-namespace OData service; expect to replace a handful of them.
# ============================================================================
CONFIG = {
    "term_code": "FA26",
    "term_name": "Fall Quarter 2026",

    "field_map": {
        # ---- course-level -------------------------------------------------
        "subject":     ["Subject", "SubjectCode", "SubjectArea", "SubjArea",
                        "DeptCode", "Department", "OrgText", "CourseSubject"],
        "number":      ["CourseNumber", "CourseNo", "CourseNr", "Catalognr",
                        "CatalogNumber", "CatalogNbr", "ModuleNumber",
                        "CourseCode"],
        "title":       ["CourseTitle", "Title", "ShortText", "Stext",
                        "CourseName", "ModuleText", "Description", "Name"],
        "units":       ["Units", "Credits", "CreditHours", "CreditValue",
                        "Cpattempt", "MinUnits", "UnitsMin"],
        "restriction": ["Restriction", "Restrictions",
                        "EnrollmentRestriction", "ConsentRequired"],
        # combined "CSE 101"-style field, used only when subject/number
        # both come up empty:
        "course_combined": ["Course", "CourseId", "Otjid", "CourseText"],

        # ---- section-level ------------------------------------------------
        "section_id":  ["SectionId", "SectionNumber", "ClassNumber",
                        "ClassNbr", "EventId", "PackageId", "Objid",
                        "SectionNr"],
        "group":       ["GroupCode", "SectionGroup", "Group"],
        "type":        ["MeetingType", "SectionType", "EventType",
                        "ActivityType", "Category", "EventCategory"],
        "code":        ["SectionCode", "SectionLabel", "Code",
                        "EventPackageCode"],
        "days":        ["Days", "MeetingDays", "DayPattern", "Weekday",
                        "DaysOfWeek", "DayText"],
        "time_start":  ["StartTime", "TimeStart", "BeginTime", "Begtm",
                        "TimeFrom", "Beguz"],
        "time_end":    ["EndTime", "TimeEnd", "Endtm", "TimeTo", "Enduz"],
        "building":    ["Building", "Bldg", "BuildingCode", "BuildingText"],
        "room":        ["Room", "RoomNumber", "RoomNr", "RoomText",
                        "Location", "Venue"],
        "instructor":  ["Instructor", "InstructorName", "Instructors",
                        "Professor", "Lecturer", "Teacher", "FacultyName"],
        "avail":       ["SeatsAvailable", "AvailableSeats", "SeatsAvail",
                        "Available", "FreeSeats", "FreePlaces", "Optcap"],
        "limit":       ["SeatsLimit", "Capacity", "MaxSeats", "SeatLimit",
                        "TotalSeats", "MaxPlaces", "Maxcap"],
        "waitlist":    ["Waitlist", "WaitlistCount", "WaitlistTotal",
                        "WaitlistedSeats", "WaitlistNum"],
        "cancelled":   ["Cancelled", "IsCancelled", "CancelFlag",
                        "CancelInd"],
        "note":        ["Note", "Notes", "SectionNote", "Comment",
                        "Remarks", "InfoText"],
        # nested section list on a course entity (from $expand), if any:
        "sections_list": ["Sections", "Meetings", "Events", "SectionSet",
                          "toSections", "to_Sections", "NavSections",
                          "MeetingSet"],
    },

    # meeting-type normalization: TSS value (upper) -> WebReg code
    "type_map": {
        "LECTURE": "LE", "LEC": "LE", "LE": "LE",
        "DISCUSSION": "DI", "DIS": "DI", "DI": "DI",
        "LAB": "LA", "LABORATORY": "LA", "LA": "LA",
        "SEMINAR": "SE", "SEM": "SE", "SE": "SE",
        "STUDIO": "ST", "ST": "ST",
        "FINAL": "FI", "FINAL EXAM": "FI", "FI": "FI",
        "MIDTERM": "MI", "MI": "MI",
        "TUTORIAL": "TU", "TU": "TU",
        "INDEPENDENT STUDY": "IN", "IN": "IN",
    },
}

# ---------------------------------------------------------------------------
# Heuristics for spotting class-search result sets inside arbitrary captures.
# A list of dicts qualifies when its entries' keys (case-insensitive) hit at
# least MIN_CATEGORIES of these patterns, including COURSE or SECTION.
# ---------------------------------------------------------------------------
CATEGORY_PATTERNS = OrderedDict([
    ("COURSE",     re.compile(r"course|catalog|module|subject", re.I)),
    ("SECTION",    re.compile(r"section|event|package|class(id|no|nbr|nr)|group",
                              re.I)),
    ("INSTRUCTOR", re.compile(r"instr|professor|teacher|lecturer|faculty",
                              re.I)),
    ("ROOM",       re.compile(r"room|bldg|building|location|venue", re.I)),
    ("DAY",        re.compile(r"day", re.I)),
    ("TIME",       re.compile(r"time|begin|end|start|beguz|enduz", re.I)),
    ("SEAT",       re.compile(r"seat|capac|enroll|avail|book|waitl|limit|"
                              r"places|occupied", re.I)),
    ("TITLE",      re.compile(r"title|stext|shorttext|name|descr", re.I)),
    ("UNIT",       re.compile(r"unit|credit", re.I)),
])
MIN_CATEGORIES = 3

DAY_MAP = {
    "m": "M", "mo": "M", "mon": "M", "monday": "M",
    "t": "Tu", "tu": "Tu", "tue": "Tu", "tues": "Tu", "tuesday": "Tu",
    "w": "W", "we": "W", "wed": "W", "wednesday": "W",
    "r": "Th", "th": "Th", "thu": "Th", "thur": "Th", "thurs": "Th",
    "thursday": "Th",
    "f": "F", "fr": "F", "fri": "F", "friday": "F",
    "sa": "Sa", "sat": "Sa", "saturday": "Sa",
    "su": "Su", "sun": "Su", "sunday": "Su",
}
WEBREG_DAYS = re.compile(r"^(M|Tu|W|Th|F|Sa|Su)+$")


# ============================ helpers ======================================

def load_captures(raw_dir):
    """Yield (filename, parsed-json-body) for every capture file."""
    for f in sorted(Path(raw_dir).glob("*.json")):
        try:
            obj = json.loads(f.read_text())
        except Exception:
            continue
        # tolerate the older wrapper format {"url","status","body"}
        if isinstance(obj, dict) and set(obj) >= {"url", "body"}:
            obj = obj["body"]
        yield f.name, obj


def find_record_lists(obj, path="$"):
    """Recursively find every list-of-dicts in a JSON blob.

    Returns [(json_path, records)]. OData v2 wraps results as
    {"d": {"results": [...]}} but we don't assume that shape.
    """
    out = []
    if isinstance(obj, list):
        dicts = [x for x in obj if isinstance(x, dict)]
        if dicts and len(dicts) == len(obj):
            out.append((path, dicts))
        else:
            for i, v in enumerate(obj):
                out.extend(find_record_lists(v, f"{path}[{i}]"))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k == "__metadata":
                continue
            out.extend(find_record_lists(v, f"{path}.{k}"))
    return out


def entry_keys(records, limit=40):
    """Union of property names across sample records (minus OData noise)."""
    keys = OrderedDict()
    for r in records[:limit]:
        for k, v in r.items():
            if k in ("__metadata", "__deferred"):
                continue
            keys.setdefault(k, []).append(v)
    return keys


def score_records(records):
    """How class-search-like is this record list? -> (score, matched cats)."""
    keys = " ".join(entry_keys(records).keys())
    matched = [c for c, pat in CATEGORY_PATTERNS.items() if pat.search(keys)]
    core = ("COURSE" in matched) or ("SECTION" in matched)
    return (len(matched) if core else 0), matched


def is_class_data(records):
    score, _ = score_records(records)
    return score >= MIN_CATEGORIES


def pick(entity, field):
    """Case-insensitive candidate-list lookup of one field on one entity."""
    lower = {k.lower(): k for k in entity}
    for cand in CONFIG["field_map"].get(field, []):
        k = lower.get(cand.lower())
        if k is not None:
            v = entity[k]
            if v not in (None, "", {},):
                return v
    return None


def as_str(v):
    return "" if v is None else str(v).strip()


def as_int(v):
    if v in (None, ""):
        return None
    m = re.search(r"-?\d+", str(v))
    return int(m.group()) if m else None


def as_bool(v):
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in ("x", "true", "yes", "y", "1")


def norm_units(v):
    s = as_str(v)
    # "4.0" -> "4", "1.00 - 4.00" -> "1-4"
    s = re.sub(r"(\d+)\.0+\b", r"\1", s)
    s = re.sub(r"\s*-\s*", "-", s)
    return s


def norm_time(v):
    """Normalize SAP/OData times to WebReg style: 'PT10H00M00S' -> '10:00a'."""
    s = as_str(v)
    if not s:
        return ""
    h = mn = None
    m = re.match(r"^PT(\d+)H(?:(\d+)M)?(?:\d+S)?$", s)          # Edm.Time
    if m:
        h, mn = int(m.group(1)), int(m.group(2) or 0)
    if h is None:
        m = re.match(r"^(\d{1,2}):(\d{2})(?::\d{2})?\s*([AaPp])?\.?[Mm]?\.?$",
                     s)                                          # 10:00[:00][ AM]
        if m:
            h, mn, ap = int(m.group(1)), int(m.group(2)), m.group(3)
            if ap:
                if ap.lower() == "p" and h != 12:
                    h += 12
                if ap.lower() == "a" and h == 12:
                    h = 0
    if h is None:
        m = re.match(r"^(\d{2})(\d{2})(?:\d{2})?$", s)           # 1330 / 133000
        if m:
            h, mn = int(m.group(1)), int(m.group(2))
    if h is None or h > 23:
        return s  # unknown format: keep raw so --inspect shows it
    suffix = "a" if h < 12 else "p"
    return f"{(h % 12) or 12}:{mn:02d}{suffix}"


def norm_days(v):
    """'MO WE FR' / 'Mon,Wed,Fri' / 'MWF' -> 'MWF' (WebReg day letters)."""
    s = as_str(v)
    if not s or WEBREG_DAYS.match(s):
        return s
    tokens = [t for t in re.split(r"[^A-Za-z]+", s) if t]
    mapped = [DAY_MAP.get(t.lower()) for t in tokens]
    if mapped and all(mapped):
        return "".join(mapped)
    # single run-together token like 'MOWEFR'
    if len(tokens) == 1:
        t, out = tokens[0].lower(), []
        while t:
            for ln in (2, 1):
                if t[:ln] in DAY_MAP:
                    out.append(DAY_MAP[t[:ln]])
                    t = t[ln:]
                    break
            else:
                return s
        return "".join(out)
    return s


def norm_type(v):
    s = as_str(v).upper()
    return CONFIG["type_map"].get(s, s[:2] or "LE")


def extract_section(entity):
    code = as_str(pick(entity, "code"))
    sid = as_str(pick(entity, "section_id"))
    group = as_str(pick(entity, "group"))
    if not group:
        group = code[0] if re.match(r"^[A-Z]\d\d", code) else "A"
    avail = as_int(pick(entity, "avail"))
    cancelled = as_bool(pick(entity, "cancelled"))
    return {
        "section_id": sid,
        "group": group,
        "type": norm_type(pick(entity, "type")),
        "code": code,
        "days": norm_days(pick(entity, "days")),
        "time_start": norm_time(pick(entity, "time_start")),
        "time_end": norm_time(pick(entity, "time_end")),
        "building": as_str(pick(entity, "building")),
        "room": as_str(pick(entity, "room")),
        "instructor": as_str(pick(entity, "instructor")),
        "avail": avail,
        "limit": as_int(pick(entity, "limit")),
        "waitlist": as_int(pick(entity, "waitlist")) or 0,
        "enrollable": bool(sid) and not cancelled,
        "cancelled": cancelled,
        "note": as_str(pick(entity, "note")),
    }


def course_key_of(entity):
    """(SUBJ, NUMBER) for an entity, via mapped fields or a combined field."""
    subj = as_str(pick(entity, "subject")).upper()
    num = as_str(pick(entity, "number")).upper()
    if subj and num:
        return subj, num
    combined = as_str(pick(entity, "course_combined"))
    m = re.match(r"^([A-Z]{2,6})\s+(\d+[A-Z]{0,2})$", combined.upper())
    if m:
        return m.group(1), m.group(2)
    return subj, num  # possibly incomplete; caller decides


def nested_sections(entity):
    """Return a nested list of section entities from a course entity, if any."""
    v = pick(entity, "sections_list")
    if isinstance(v, dict):
        v = v.get("results")
    if isinstance(v, list) and v and all(isinstance(x, dict) for x in v):
        return v
    return None


def build_courses(all_records):
    """Fold every qualifying record list into {(subj,num): course_dict}."""
    courses = OrderedDict()
    skipped = 0

    def course_for(entity, subj, num):
        key = (subj, num)
        if key not in courses:
            courses[key] = {
                "subject": subj, "number": num,
                "title": as_str(pick(entity, "title")),
                "units": norm_units(pick(entity, "units")),
                "restriction": as_str(pick(entity, "restriction")),
                "sections": [],
            }
        c = courses[key]
        if not c["title"]:
            c["title"] = as_str(pick(entity, "title"))
        if not c["units"]:
            c["units"] = norm_units(pick(entity, "units"))
        return c

    def add_section(course, entity):
        s = extract_section(entity)
        dedupe = (s["section_id"], s["code"], s["type"], s["days"],
                  s["time_start"])
        if dedupe not in {(x["section_id"], x["code"], x["type"], x["days"],
                           x["time_start"]) for x in course["sections"]}:
            course["sections"].append(s)

    for records in all_records:
        for entity in records:
            subj, num = course_key_of(entity)
            if not subj or not num or not re.match(r"^[A-Z&]{2,6}$", subj):
                skipped += 1
                continue
            course = course_for(entity, subj, num)
            nested = nested_sections(entity)
            if nested:
                for sec in nested:
                    add_section(course, sec)
            else:
                add_section(course, entity)

    if skipped:
        print(f"  note: skipped {skipped} entities with no resolvable "
              f"subject/number (fix CONFIG['field_map'] if that's most of "
              f"them — run --inspect)")
    return courses


# ============================ modes ========================================

def cmd_inspect(raw_dir):
    print(f"Inspecting captures in {raw_dir}\n")
    found_any = False
    for fname, obj in load_captures(raw_dir):
        for path, records in find_record_lists(obj):
            score, cats = score_records(records)
            if score == 0:
                continue
            found_any = True
            flag = "CLASS-DATA?" if score >= MIN_CATEGORIES else "weak"
            print(f"{fname}  @ {path}  ({len(records)} entities) "
                  f"[{flag}: {'/'.join(cats)}]")
            for k, vals in entry_keys(records).items():
                samples = []
                for v in vals:
                    if isinstance(v, (dict, list)):
                        v = f"<{type(v).__name__}>"
                    v = str(v)
                    if v not in samples:
                        samples.append(v)
                    if len(samples) == 3:
                        break
                print(f"    {k:32s} {' | '.join(s[:40] for s in samples)}")
            print()
    if not found_any:
        print("No candidate record lists found. Did connect.py capture "
              "anything? Check data/tss_raw/manifest.jsonl.")
    else:
        print("Now put the REAL key names first in CONFIG['field_map'] "
              "(top of this file), then rerun without --inspect.")


def cmd_import(raw_dir, out_dir, terms_json, term):
    all_records = []
    used_files = []
    for fname, obj in load_captures(raw_dir):
        hit = False
        for _path, records in find_record_lists(obj):
            if is_class_data(records):
                all_records.append(records)
                hit = True
        if hit:
            used_files.append(fname)
    if not all_records:
        print("No class-search-looking captures found in "
              f"{raw_dir} — run with --inspect to see what IS there.")
        return 1
    print(f"Using {len(all_records)} record list(s) from "
          f"{len(used_files)} file(s): {', '.join(used_files[:8])}"
          f"{'…' if len(used_files) > 8 else ''}")

    courses = build_courses(all_records)
    courses = OrderedDict((k, c) for k, c in courses.items() if c["sections"])
    if not courses:
        print("Captures matched the heuristics but no courses could be "
              "mapped — CONFIG['field_map'] needs the real key names. "
              "Run --inspect and fill it in.")
        return 1

    term_dir = Path(out_dir) / term
    term_dir.mkdir(parents=True, exist_ok=True)
    by_subject = OrderedDict()
    for (subj, _num), c in sorted(courses.items()):
        by_subject.setdefault(subj, []).append(c)
    for subj, clist in by_subject.items():
        (term_dir / f"{subj}.json").write_text(json.dumps(clist, indent=1))
        n_sec = sum(len(c["sections"]) for c in clist)
        print(f"  {term}/{subj}.json: {len(clist)} courses, "
              f"{n_sec} sections")

    # ---- add the term to terms.json (idempotent) ----
    terms_path = Path(terms_json)
    terms = json.loads(terms_path.read_text()) if terms_path.exists() else []
    if not any(t.get("code") == term for t in terms):
        terms.insert(0, {"code": term, "name": CONFIG["term_name"],
                         "source": "tss", "is_default": 1})
        terms_path.write_text(json.dumps(terms, indent=2) + "\n")
        print(f"  added {term} (source tss, default) → {terms_path}")
    else:
        print(f"  {term} already present in {terms_path}")

    print(f"\nDone: {len(courses)} courses across {len(by_subject)} "
          f"subjects → {term_dir}\nNext: python3 seed.py")
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="Import TSS OData captures into data/parsed/<TERM>/ "
                    "(see module docstring).")
    ap.add_argument("--inspect", action="store_true",
                    help="dump distinct keys + sample values found in the "
                         "captures, so CONFIG['field_map'] can be filled in")
    ap.add_argument("--raw-dir", default=str(ROOT / "data" / "tss_raw"))
    ap.add_argument("--out-dir", default=str(ROOT / "data" / "parsed"))
    ap.add_argument("--terms-json", default=str(ROOT / "data" / "terms.json"))
    ap.add_argument("--term", default=CONFIG["term_code"])
    args = ap.parse_args()

    if args.inspect:
        cmd_inspect(args.raw_dir)
        return 0
    return cmd_import(args.raw_dir, args.out_dir, args.terms_json, args.term)


if __name__ == "__main__":
    sys.exit(main())
