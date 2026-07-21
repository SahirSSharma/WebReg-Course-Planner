#!/usr/bin/env python3
"""Offline parser test against the captured real SOC results page
(data/samples/REFERENCE_CSE_SP15_from_github.html, CSE SP15 page 1 of 2).

Run: python3 scraper/test_parse.py   -> prints OK and exits 0, or asserts.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from soc_scraper import page_count, parse_pages  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "data" / "samples" / "REFERENCE_CSE_SP15_from_github.html"


def main():
    html = SAMPLE.read_text()

    # pagination marker "Page  (1&nbsp;of&nbsp;2)"
    assert page_count(html) == 2, page_count(html)

    courses = parse_pages([html], "CSE")
    by_num = {c["number"]: c for c in courses}

    # ---- course-level invariants -------------------------------------
    assert sorted(by_num) == ["101", "110", "150", "190"], sorted(by_num)
    for c in courses:
        assert c["subject"] == "CSE"
        assert c["units"] == "4", (c["number"], c["units"])
        assert c["title"], c["number"]
        assert c["sections"], c["number"]
    assert by_num["101"]["title"] == "Design & Analysis of Algorithm"
    assert by_num["110"]["title"] == "Software Engineering"
    # course note captured (nonenrtxt without insTyp)
    assert "MATH 188" in by_num["101"].get("note", "")

    # section-row total: 30 tr.sectxt + 9 FI exam rows in the sample
    n_secs = sum(len(c["sections"]) for c in courses)
    assert n_secs == 39, n_secs

    # ---- CSE 101 A00 lecture: full section with waitlist --------------
    a00 = by_num["101"]["sections"][0]
    assert a00 == {
        "section_id": "839503", "group": "A", "type": "LE", "code": "A00",
        "days": "MW", "time_start": "5:00p", "time_end": "6:20p",
        "building": "CENTR", "room": "115",
        "instructor": "Glick, John Edward",
        "avail": 0, "limit": 146, "waitlist": 21,
        "enrollable": True, "cancelled": False, "note": "",
    }, a00

    # ---- non-enrollable DI meeting: blank section ID, attached to A ---
    a01 = by_num["101"]["sections"][1]
    assert a01["type"] == "DI" and a01["code"] == "A01"
    assert a01["section_id"] == "" and not a01["enrollable"]
    assert a01["group"] == "A"
    assert a01["avail"] is None and a01["limit"] is None

    # ---- FI exam rows attached to every family ------------------------
    for num, fam_ct in [("101", 3), ("110", 2), ("150", 1), ("190", 3)]:
        fis = [s for s in by_num[num]["sections"] if s["type"] == "FI"]
        assert len(fis) == fam_ct, (num, len(fis))
        for fi in fis:
            assert "/" in fi["code"], fi  # date in section-code column
            assert fi["time_start"] and fi["time_end"], fi
            assert not fi["enrollable"]
    fi_a = [s for s in by_num["101"]["sections"]
            if s["type"] == "FI" and s["group"] == "A"][0]
    assert (fi_a["code"], fi_a["days"], fi_a["time_start"]) == \
        ("06/06/2015", "S", "8:00a"), fi_a

    # ---- cancelled sections (3 in sample: CSE 110 A01, B01, B02) ------
    cancelled = [s for c in courses for s in c["sections"] if s["cancelled"]]
    assert sorted(s["code"] for s in cancelled) == ["A01", "B01", "B02"], \
        cancelled
    for s in cancelled:
        assert not s["enrollable"]
        assert s["days"] == "" and s["time_start"] == ""

    # ---- groups: family letter = leading letter of section code -------
    for c in courses:
        for s in c["sections"]:
            if s["code"] and s["code"][0].isalpha():
                assert s["group"] == s["code"][0], s

    # ---- open (non-full) section parses numeric seats -----------------
    c00 = [s for s in by_num["101"]["sections"] if s["code"] == "C00"][0]
    assert c00["avail"] == 63 and c00["limit"] == 146 and c00["waitlist"] == 0
    assert c00["instructor"] == "Staff"

    # every enrollable section has a 6-digit ID
    for c in courses:
        for s in c["sections"]:
            if s["enrollable"]:
                assert len(s["section_id"]) == 6 and s["section_id"].isdigit()

    print(f"OK — {len(courses)} courses, {n_secs} sections, "
          "all invariants hold")


if __name__ == "__main__":
    main()
