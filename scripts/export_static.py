#!/usr/bin/env python3
"""Export the FA26 catalog from webreg.db into the static-site data bundle.

Writes site/data/{catalog.json, subjects.json, terms.json} in exactly the
shape the frontend's /api/* responses used, so the browser-only build (see
site/js/localdb.js) needs no server. FA26 only — that's the one term the UI
shows. Run after any data refresh: python3 scripts/export_static.py
"""
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "webreg.db"
OUT = ROOT / "site" / "data"
TERM = "FA26"


def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    OUT.mkdir(parents=True, exist_ok=True)

    terms = [{"code": TERM, "name": "Fall 2026", "source": "tss", "is_default": 1}]
    (OUT / "terms.json").write_text(json.dumps(terms))

    subjects = [dict(r) for r in conn.execute(
        "SELECT DISTINCT s.code, s.name FROM subjects s "
        "JOIN courses c ON c.subject_code = s.code WHERE c.term_code=? "
        "ORDER BY s.code", (TERM,))]
    (OUT / "subjects.json").write_text(json.dumps(subjects))

    courses = [dict(r) for r in conn.execute(
        "SELECT * FROM courses WHERE term_code=? ORDER BY subject_code, "
        "CAST(REPLACE(REPLACE(course_num,'L',''),'R','') AS INTEGER), course_num",
        (TERM,))]
    for c in courses:
        c["sections"] = [dict(r) for r in conn.execute(
            "SELECT * FROM sections WHERE course_id=? ORDER BY group_code, "
            "CASE meeting_type WHEN 'FI' THEN 1 ELSE 0 END, section_code",
            (c["id"],))]
    (OUT / "catalog.json").write_text(json.dumps(courses, separators=(",", ":")))

    size = (OUT / "catalog.json").stat().st_size
    print(f"{len(courses)} courses, {sum(len(c['sections']) for c in courses)} "
          f"sections, {len(subjects)} subjects -> {OUT} "
          f"(catalog.json {size/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
