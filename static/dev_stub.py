#!/usr/bin/env python3
"""Throwaway dev stub for frontend work — serves the pinned WebReg API shapes
with fixture data on port 5062. NOT part of the real app (app.py + webreg.db).

Run:  python3 static/dev_stub.py
"""
import itertools
import re
from pathlib import Path

from flask import Flask, jsonify, render_template, request

ROOT = Path(__file__).resolve().parent.parent
app = Flask(__name__, template_folder=str(ROOT / "templates"),
            static_folder=str(ROOT / "static"), static_url_path="/static")

TERMS = [
    {"code": "FA25", "name": "Fall Quarter 2025", "source": "soc", "is_default": 1},
    {"code": "SP26", "name": "Spring Quarter 2026", "source": "soc", "is_default": 0},
    {"code": "WI26", "name": "Winter Quarter 2026", "source": "soc", "is_default": 0},
]
SUBJECTS = [
    {"code": "BILD", "name": "Biology/Lower Division"},
    {"code": "CSE", "name": "Computer Science & Engineering"},
    {"code": "MATH", "name": "Mathematics"},
    {"code": "MUS", "name": "Music"},
]

_pk = itertools.count(1)


def sec(section_id, group, mtype, code, days, t1, t2, bldg, room, instr,
        avail=None, limit=None, wl=0, enrollable=0, note=""):
    return {
        "id": next(_pk), "section_id": section_id, "group_code": group,
        "meeting_type": mtype, "section_code": code, "days": days,
        "time_start": t1, "time_end": t2, "building": bldg, "room": room,
        "instructor": instr, "seats_avail": avail, "seats_limit": limit,
        "waitlist_ct": wl, "enrollable": enrollable, "cancelled": 0, "note": note,
    }


_cid = itertools.count(1)


def course(subj, num, title, units, sections, restriction=""):
    return {"id": next(_cid), "term_code": "FA25", "subject_code": subj,
            "course_num": num, "title": title, "units": units,
            "restriction": restriction, "sections": sections}


COURSES = [
    course("BILD", "3", "Organismic&Evolutionary Biol", "4", [
        sec("101205", "A", "LE", "A00", "TuTh", "9:30a", "10:50a", "PETER", "108",
            "Woodruff, David S.", avail=0, limit=300, wl=17, enrollable=1),
        sec("", "A", "FI", "", "Th 12/11/2025", "8:00a", "10:59a", "TBA", "TBA", ""),
        sec("101206", "B", "LE", "B00", "TuTh", "2:00p", "3:20p", "YORK", "2722",
            "Woodruff, David S.", avail=25, limit=300, wl=0, enrollable=1),
        sec("", "B", "FI", "", "Th 12/11/2025", "3:00p", "5:59p", "TBA", "TBA", ""),
    ]),
    course("CSE", "100", "Advanced Data Structures", "4", [
        sec("", "A", "LE", "A00", "MWF", "10:00a", "10:50a", "CENTR", "115",
            "Alvarado, Christine"),
        sec("204101", "A", "DI", "A01", "W", "5:00p", "5:50p", "CENTR", "113",
            "", avail=12, limit=60, wl=0, enrollable=1),
        sec("204102", "A", "DI", "A02", "W", "6:00p", "6:50p", "CENTR", "113",
            "", avail=0, limit=60, wl=5, enrollable=1),
        sec("", "A", "FI", "", "Sa 12/06/2025", "3:00p", "5:59p", "TBA", "TBA", ""),
    ]),
    course("CSE", "199", "Independent Study", "1-4", [
        sec("204990", "A", "IN", "A00", "", "", "", "TBA", "TBA",
            "Staff", avail=99, limit=99, wl=0, enrollable=1),
    ]),
    course("MATH", "20C", "Calculus&Analyt Geom/Sci&Engnr", "4", [
        sec("", "A", "LE", "A00", "MWF", "1:00p", "1:50p", "PCYNH", "109",
            "Rogalski, Daniel S."),
        sec("103301", "A", "DI", "A01", "Th", "5:00p", "5:50p", "APM", "B402",
            "", avail=3, limit=35, wl=0, enrollable=1),
        sec("103302", "A", "DI", "A02", "Th", "6:00p", "6:50p", "APM", "B402",
            "", avail=0, limit=35, wl=2, enrollable=1),
        sec("", "A", "FI", "", "F 12/12/2025", "11:30a", "2:29p", "TBA", "TBA", ""),
        sec("", "B", "LE", "B00", "MWF", "10:00a", "10:50a", "PCYNH", "109",
            "Eggers, John W."),
        sec("103311", "B", "DI", "B01", "Th", "7:00p", "7:50p", "APM", "B402",
            "", avail=10, limit=35, wl=0, enrollable=1),
        sec("", "B", "FI", "", "F 12/12/2025", "11:30a", "2:29p", "TBA", "TBA", ""),
    ]),
    course("MUS", "95G", "Gospel Choir", "2/4 by 2", [
        sec("187110", "A", "ST", "A00", "Tu", "7:00p", "9:50p", "CPMC", "136",
            "Anderson, Kenneth E.", avail=40, limit=100, wl=0, enrollable=1,
            note="Students can enroll in either section of 95G for 2 or 4 units. "
                 "Students enrolled in the MUS 95G ensembles will be charged a $10 "
                 "lab fee which will be assessed with registration fees."),
        sec("", "A", "FI", "", "Sa 12/06/2025", "7:00p", "9:59p", "TBA", "TBA", ""),
    ]),
]

# in-memory schedule
ITEMS = []
_item_pk = itertools.count(1)


def find_section(pk):
    for c in COURSES:
        for s in c["sections"]:
            if s["id"] == pk:
                return c, s
    return None, None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/terms")
def terms():
    return jsonify(TERMS)


@app.route("/api/subjects")
def subjects():
    return jsonify(SUBJECTS)


@app.route("/api/search")
def search():
    out = []
    q = request.args.get("q", "").strip()
    subs = [s for s in request.args.get("subjects", "").split(",") if s]
    courseno = request.args.get("courseno", "").strip()
    instructor = request.args.get("instructor", "").strip().lower()
    title = request.args.get("title", "").strip().lower()
    sectionid = request.args.get("sectionid", "").strip()
    hidefull = request.args.get("hidefull") == "1" or request.args.get("onlyopen") == "1"

    q_subj = q_num = q_word = None
    if q:
        toks = q.split()
        for t in toks:
            if t.upper() in {s["code"] for s in SUBJECTS}:
                q_subj = t.upper()
            elif re.match(r"^\d+[A-Za-z]*$", t):
                q_num = t.upper()
            else:
                q_word = t.lower()

    for c in COURSES:
        if c["term_code"] != request.args.get("term"):
            continue
        if subs and c["subject_code"] not in subs:
            continue
        if courseno and c["course_num"].upper() != courseno.upper():
            continue
        if title and title not in c["title"].lower():
            continue
        if instructor and not any(
                instructor in (s["instructor"] or "").lower() for s in c["sections"]):
            continue
        if sectionid and not any(s["section_id"] == sectionid for s in c["sections"]):
            continue
        if q_subj and c["subject_code"] != q_subj:
            continue
        if q_num and c["course_num"].upper() != q_num and not c["course_num"].upper().startswith(q_num):
            continue
        if q_word:
            subj_name = next((s["name"] for s in SUBJECTS
                              if s["code"] == c["subject_code"]), "")
            if q_word not in c["title"].lower() and q_word not in subj_name.lower() \
                    and not c["subject_code"].lower().startswith(q_word):
                continue
        secs = c["sections"]
        if hidefull:
            open_groups = {s["group_code"] for s in secs
                           if s["enrollable"] and (s["seats_avail"] or 0) > 0}
            secs = [s for s in secs if s["group_code"] in open_groups]
            if not secs:
                continue
        out.append({**c, "sections": secs})
    return jsonify(out)


@app.route("/api/schedule")
def schedule():
    term = request.args.get("term")
    out = []
    for it in ITEMS:
        if it["term"] != term:
            continue
        c, s = find_section(it["section_pk"])
        meetings = [m for m in c["sections"]
                    if m["group_code"] == s["group_code"]
                    and (not m["enrollable"] or m["id"] == s["id"])]
        out.append({
            "item_id": it["id"], "status": it["status"], "units": it["units"],
            "grade_option": it["grade_option"], "course_id": c["id"],
            "subject_code": c["subject_code"], "course_num": c["course_num"],
            "title": c["title"], "section_pk": s["id"],
            "group_code": s["group_code"], "section_code": s["section_code"],
            "section_id": s["section_id"], "meetings": meetings,
        })
    return jsonify(out)


@app.route("/api/schedule/add", methods=["POST"])
def add():
    d = request.get_json(force=True)
    c, s = find_section(d["section_pk"])
    if not s or not s["enrollable"]:
        return jsonify({"error": "Invalid section."}), 400
    for it in ITEMS:
        oc, _ = find_section(it["section_pk"])
        if it["term"] == d["term"] and oc["id"] == c["id"]:
            return jsonify({"error": "You are already enrolled in this class."}), 409
    ITEMS.append({"id": next(_item_pk), "term": d["term"],
                  "section_pk": d["section_pk"],
                  "status": d.get("status", "enrolled"),
                  "units": d.get("units", "4"),
                  "grade_option": d.get("grade_option", "L")})
    return jsonify({"ok": True})


@app.route("/api/schedule/drop", methods=["POST"])
def drop():
    d = request.get_json(force=True)
    global ITEMS
    ITEMS = [i for i in ITEMS if i["id"] != d["item_id"]]
    return jsonify({"ok": True})


@app.route("/api/schedule/change", methods=["POST"])
def change():
    d = request.get_json(force=True)
    for it in ITEMS:
        if it["id"] == d["item_id"]:
            if d.get("units") is not None:
                it["units"] = d["units"]
            if d.get("grade_option") is not None:
                it["grade_option"] = d["grade_option"]
            if d.get("section_pk") is not None:
                it["section_pk"] = d["section_pk"]
    return jsonify({"ok": True})


@app.route("/api/appointment")
def appointment():
    return jsonify({
        "first_pass": {"start": "Saturday, 05/17/2025 8:00 a.m. PT",
                       "end": "Monday, 05/19/2025 11:59 p.m. PT"},
        "second_pass": {"start": "Thursday, 05/29/2025 5:20 p.m. PT",
                        "end": "Thursday, 08/21/2025 11:59 p.m. PT"},
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5062, debug=False)
