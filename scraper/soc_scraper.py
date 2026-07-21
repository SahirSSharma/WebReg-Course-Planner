#!/usr/bin/env python3
"""Scrape UCSD's legacy Schedule of Classes into data/parsed/<TERM>/<SUBJ>.json.

Request recipe and HTML schema per docs/research/SOC_FORMAT.md (verified against
the captured CSE SP15 results page in data/samples/):
  - Chrome User-Agent mandatory (default curl/requests UA hangs forever).
  - Session flow: GET form page (cookies) -> POST scheduleOfClassesStudentResult.htm
    with tabNum=tabs-sub, _selectedSubjects=1, ALL schedOption1-13 true/_on pairs
    -> page 1. Pages 2..N via GET ?page=N on the same session (query is
    server-side session state).
  - Success is detected by crsheader/sectxt in the body, never HTTP status:
    an invalid query bounces back HTTP 200 with the search form (socFacSearch).
  - The server intermittently throws HTTP 500 "Max Sessions Exceeded" or hangs;
    every fetch retries with long backoff under a global time budget.
  - Every fetched page is cached under data/samples/<TERM>/ so parsing is
    offline-repeatable (--parse-only rebuilds JSON from cache alone).

HTML schema (13 logical columns after colspan expansion):
  0 restriction | 1 course# | 2 sectionID | 3 meeting type (span#insTyp) |
  4 section code (or exam DATE) | 5 days | 6 time | 7 bldg | 8 room |
  9 instructor | 10 avail | 11 limit | 12 action
  - td.crsheader rows: course header (repeats per lecture family -> dedupe);
    units live in the title cell as "( N Units)".
  - tr.sectxt with span#insTyp: section/meeting row. Blank sectionID = extra
    meeting of the family. "FULL Waitlist(N)" in span.ertext = full section.
    Merged colspan cell whose text is "Cancelled" = cancelled section.
  - tr.nonenrtxt with insTyp: FI/MI exam row, date in the section-code column.
  - nonenrtxt WITHOUT insTyp: free-text course note.

Usage:
  python3 soc_scraper.py --term FA25 --subjects CSE,MATH     # scrape + parse
  python3 soc_scraper.py --term FA25 --all-subjects
  python3 soc_scraper.py --term FA25 --parse-only            # from cache only
  python3 soc_scraper.py --term FA25 --probe                 # subject-list check
"""
import argparse
import html as htmllib
import json
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://act.ucsd.edu/scheduleOfClasses"
FORM_URL = f"{BASE}/scheduleOfClassesStudent.htm"
RESULT_URL = f"{BASE}/scheduleOfClassesStudentResult.htm"
SUBJLIST_URL = f"{BASE}/subject-list.json"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

session = None
DEADLINE = None  # wall-clock time after which we stop retrying


class Budget(Exception):
    """Raised when the global retry budget is exhausted."""


def remaining():
    return 1e9 if DEADLINE is None else DEADLINE - time.time()


def new_session():
    global session
    session = requests.Session()
    session.headers.update({"User-Agent": UA,
                            "Accept": "text/html,application/xhtml+xml,*/*"})
    session.get(FORM_URL, timeout=45)


def search_body(term, subject):
    """Form body for the subject-search tab (coursetable-ucsd recipe)."""
    body = [("selectedTerm", term), ("xsoc_term", ""), ("loggedIn", "false"),
            ("tabNum", "tabs-sub"), ("_selectedSubjects", "1"),
            ("selectedSubjects", subject.ljust(4)),
            ("_schDay", "on"), ("_hideFullSec", "on"), ("_showPopup", "on")]
    for n in range(1, 14):
        if n == 6:  # option 6 does not exist in the form
            continue
        body.append((f"schedOption{n}", "true"))
        body.append((f"_schedOption{n}", "on"))
    return body


def looks_like_results(text):
    return "crsheader" in text or "sectxt" in text or "No Result Found" in text


def _attempt_loop(what, do_request):
    """Run do_request() with patient backoff until success or budget out.

    do_request returns (ok, text_or_reason)."""
    delay = 20
    attempt = 0
    while True:
        attempt += 1
        if remaining() <= 0:
            raise Budget(f"{what}: retry budget exhausted")
        try:
            if session is None:
                new_session()
            ok, payload = do_request()
            if ok:
                return payload
            reason = payload
        except requests.RequestException as e:
            reason = type(e).__name__
        print(f"    {what}: {reason} (attempt {attempt}), "
              f"retry in {delay}s ({int(max(0, remaining()))}s left)", flush=True)
        if remaining() <= delay:
            raise Budget(f"{what}: retry budget exhausted")
        time.sleep(delay)
        delay = min(int(delay * 1.5), 90)
        try:
            new_session()
        except requests.RequestException:
            pass


def classify(r):
    if r.status_code != 200:
        if "Max Sessions Exceeded" in r.text:
            return "Max Sessions Exceeded (500)"
        return f"HTTP {r.status_code}"
    if looks_like_results(r.text):
        return None  # success
    if 'id="socFacSearch"' in r.text or "socFacSearch" in r.text:
        return "bounced to search form"
    return "unrecognized 200 body"


def post_search(term, subject):
    """POST the search; returns page-1 HTML."""
    def do():
        r = session.post(RESULT_URL, data=search_body(term, subject),
                         timeout=60)
        reason = classify(r)
        return (reason is None, r.text if reason is None else reason)
    return _attempt_loop(f"{subject} POST", do)


def get_page(term, subject, page):
    """GET page N of the session's last search; re-POSTs if session lost."""
    def do():
        r = session.get(RESULT_URL, params={"page": str(page)}, timeout=60)
        reason = classify(r)
        if reason is not None and "bounced" in reason:
            # session lost its query state -> rebuild it and retry the GET
            post_search(term, subject)
            r = session.get(RESULT_URL, params={"page": str(page)}, timeout=60)
            reason = classify(r)
        return (reason is None, r.text if reason is None else reason)
    return _attempt_loop(f"{subject} p{page}", do)


def fetch_subject_list(term):
    """GET subject-list.json for a term. Returns list (may be empty)."""
    def do():
        r = session.get(SUBJLIST_URL, params={"selectedTerm": term},
                        timeout=45)
        if r.status_code != 200:
            return (False, f"HTTP {r.status_code}")
        try:
            return (True, r.json())
        except ValueError:
            return (False, "non-JSON body")
    return _attempt_loop(f"subject-list {term}", do)


# ---------------------------------------------------------------- parsing ---

CLEAN = re.compile(r"\s+")
UNITS_RE = re.compile(r"\(\s*([\d][\d./,\s\-–to]*?)\s*Units?\s*\)", re.I)
TBA_RE = re.compile(r"^(tba|tbd|arr|arranged|arrange)$", re.I)


def txt(el):
    if el is None:
        return ""
    return CLEAN.sub(" ", el.get_text(" ", strip=True)).strip()


def logical_cells(tr):
    """Expand every colspan=N cell into N logical slots (same td repeated)."""
    out = []
    for td in tr.find_all("td", recursive=False):
        try:
            span = int(td.get("colspan", 1))
        except (TypeError, ValueError):
            span = 1
        out.extend([td] * max(span, 1))
    return out


def parse_int(s):
    s = s.strip()
    return int(s) if s.isdigit() else None


def parse_pages(pages, subject):
    """Parse SOC result pages (one subject) into seed.py course dicts."""
    from bs4 import BeautifulSoup
    courses = {}          # (subject, number) -> course dict, insertion-ordered
    cur = None
    group = "A"
    for html_text in pages:
        soup = BeautifulSoup(html_text, "html.parser")
        root = soup.find("form", id="socDisplayCVO") or soup
        for tr in root.find_all("tr"):
            tds = tr.find_all("td", recursive=False)
            if not tds:
                continue
            cells = logical_cells(tr)
            klass = tr.get("class") or []
            ins = tr.find("span", id="insTyp")

            if any("crsheader" in (td.get("class") or []) for td in tds):
                # --- course header (simple 3-cell or full 4-cell variant) ---
                if len(cells) < 3:
                    continue
                restriction = txt(cells[0])
                number = txt(cells[1])
                title_cell = txt(cells[2])
                if not number:
                    continue
                m = UNITS_RE.search(title_cell)
                units = CLEAN.sub("", m.group(1)) if m else ""
                title = title_cell
                bold = cells[2].find("span", class_="boldtxt")
                if bold:
                    title = txt(bold)
                elif m:
                    title = title_cell[:m.start()].strip()
                # strip trailing "Prerequisites | Resources ..." junk if any
                key = (subject, number)
                if key in courses:
                    cur = courses[key]
                    if units and not cur["units"]:
                        cur["units"] = units
                    if restriction and not cur["restriction"]:
                        cur["restriction"] = restriction
                    if title and (not cur["title"] or bold):
                        cur["title"] = title
                else:
                    cur = {"subject": subject, "number": number,
                           "title": title, "units": units,
                           "restriction": restriction, "sections": []}
                    courses[key] = cur
                group = "A"
                continue

            is_sec = "sectxt" in klass or "nonenrtxt" in klass or \
                any("nonenrtxt" in (td.get("class") or []) for td in tds)
            if not is_sec or cur is None:
                continue

            if ins is None:
                # ------ course-note row (nonenrtxt without insTyp) ------
                note = txt(tr)
                if note:
                    cur["note"] = (cur.get("note", "") + " " + note).strip()
                continue

            # ---------------- section / meeting / exam row ----------------
            if len(cells) < 5:
                continue
            mtype = txt(ins) or "LE"
            code = txt(cells[4])
            if re.match(r"^[A-Z]\d{2}$", code):
                group = code[0]
            sec_id = txt(cells[2])
            if not sec_id.isdigit():
                sec_id = ""

            cancelled = any("Cancelled" in txt(td) for td in tds
                            if td.find("span", class_="ertext"))
            days = t0 = t1 = building = room = instructor = ""
            avail = limit = None
            wl = 0
            if not cancelled and len(cells) >= 12:
                days = txt(cells[5])
                time_s = txt(cells[6])
                if "-" in time_s:
                    t0, t1 = [p.strip() for p in time_s.split("-", 1)]
                elif time_s and not TBA_RE.match(time_s):
                    t0 = time_s
                building = txt(cells[7])
                room = txt(cells[8])
                # instructor cell may hold several staff names on <br> lines
                names = [CLEAN.sub(" ", ln).strip()
                         for ln in cells[9].get_text("\n").split("\n")]
                instructor = "; ".join(n for n in names if n)
                avail_raw = txt(cells[10])
                mwl = re.search(r"FULL\s*.*?\((\d+)\)", avail_raw, re.I)
                if mwl:
                    wl = int(mwl.group(1))
                if "FULL" in avail_raw.upper():
                    avail = 0
                else:
                    avail = parse_int(avail_raw)
                limit = parse_int(txt(cells[11]))

            enrollable = bool(sec_id) and not cancelled
            cur["sections"].append({
                "section_id": sec_id, "group": group, "type": mtype,
                "code": code, "days": "" if TBA_RE.match(days) else days,
                "time_start": t0, "time_end": t1,
                "building": building, "room": room,
                "instructor": instructor, "avail": avail, "limit": limit,
                "waitlist": wl, "enrollable": enrollable,
                "cancelled": cancelled, "note": "",
            })
    return [c for c in courses.values() if c["sections"]]


def page_count(html_text):
    decoded = htmllib.unescape(html_text)
    m = re.search(r"[Pp]age\s*\(\s*\d+\s+of\s+(\d+)\s*\)", decoded)
    return int(m.group(1)) if m else 1


# --------------------------------------------------------------- pipeline ---

def scrape_subject(term, subject, cache_dir, parse_only=False):
    pages = []
    p = 1
    total = None
    while True:
        cache = cache_dir / f"{subject}_p{p}.html"
        if cache.exists():
            html_text = cache.read_text()
        elif parse_only:
            break
        else:
            if p == 1:
                html_text = post_search(term, subject)
            else:
                html_text = get_page(term, subject, p)
            if "No Result Found" in html_text and "crsheader" not in html_text:
                return []
            cache.write_text(html_text)
            time.sleep(3)
        pages.append(html_text)
        if total is None:
            total = page_count(html_text)
        if p >= total:
            break
        p += 1
    return parse_pages(pages, subject)


def refresh_subjects(term):
    """Fetch subject-list.json for term; save + refresh data/subjects.json."""
    subs = fetch_subject_list(term)
    if not subs:
        print(f"  subject-list for {term}: EMPTY (term retired?)", flush=True)
        return None
    (ROOT / "data" / f"subjects_{term}.json").write_text(
        json.dumps(subs, indent=1))
    norm = [{"code": s["code"].strip(),
             "name": s["value"].split("-", 1)[-1].strip()
             if "-" in s.get("value", "") else s.get("value", "").strip()}
            for s in subs]
    (ROOT / "data" / "subjects.json").write_text(json.dumps(norm, indent=1))
    print(f"  subject-list for {term}: {len(subs)} subjects saved", flush=True)
    return norm


def main():
    global DEADLINE
    ap = argparse.ArgumentParser()
    ap.add_argument("--term", required=True)
    ap.add_argument("--subjects", default="")
    ap.add_argument("--all-subjects", action="store_true")
    ap.add_argument("--parse-only", action="store_true")
    ap.add_argument("--probe", action="store_true",
                    help="only fetch subject-list.json and report")
    ap.add_argument("--budget", type=float, default=20,
                    help="total network retry budget in minutes")
    args = ap.parse_args()

    if not args.parse_only:
        DEADLINE = time.time() + args.budget * 60

    if args.probe:
        try:
            subs = refresh_subjects(args.term)
        except Budget as e:
            print(f"BUDGET: {e}")
            return 2
        return 0 if subs else 1

    if args.all_subjects:
        subs = [s["code"] for s in
                json.loads((ROOT / "data" / "subjects.json").read_text())]
    else:
        subs = [s.strip() for s in args.subjects.split(",") if s.strip()]
    if not subs:
        ap.error("give --subjects or --all-subjects")

    cache_dir = ROOT / "data" / "samples" / args.term
    out_dir = ROOT / "data" / "parsed" / args.term
    cache_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not args.parse_only:
        try:
            refresh_subjects(args.term)
        except Budget as e:
            print(f"BUDGET during subject-list: {e}")
            return 2

    failed = []
    for sub in subs:
        print(f"[{args.term}] {sub} ...", flush=True)
        try:
            courses = scrape_subject(args.term, sub, cache_dir,
                                     args.parse_only)
        except Budget as e:
            print(f"    BUDGET EXHAUSTED: {e}", flush=True)
            failed.append(sub)
            break
        except Exception as e:
            print(f"    FAILED: {e}", flush=True)
            failed.append(sub)
            continue
        if courses:
            (out_dir / f"{sub}.json").write_text(json.dumps(courses, indent=1))
        nsec = sum(len(c["sections"]) for c in courses)
        print(f"    {len(courses)} courses, {nsec} section rows", flush=True)
    if failed:
        print("FAILED subjects:", ",".join(failed))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
