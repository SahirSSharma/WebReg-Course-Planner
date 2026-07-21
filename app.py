#!/usr/bin/env python3
"""WebReg Revival — Flask server + JSON API.

Serves the classic-WebReg UI and a small API over data/webreg.db.
Planning tool only: 'enroll' writes to local schedule tables, never to UCSD.
"""
import sqlite3
from pathlib import Path

from flask import Flask, g, jsonify, render_template, request

DB_PATH = Path(__file__).parent / "data" / "webreg.db"
PORT = 5060

app = Flask(__name__)


def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def rows(cursor):
    return [dict(r) for r in cursor.fetchall()]


# ---------------------------------------------------------------- pages

@app.route("/")
def page_term_select():
    """Classic WebReg landing: pick a term, hit Go."""
    return render_template("index.html")


# ---------------------------------------------------------------- api: catalog

@app.route("/api/terms")
def api_terms():
    return jsonify(rows(db().execute(
        "SELECT code, name, source, is_default FROM terms ORDER BY sort_key DESC")))


@app.route("/api/subjects")
def api_subjects():
    return jsonify(rows(db().execute(
        "SELECT code, name FROM subjects ORDER BY code")))


@app.route("/api/search")
def api_search():
    """Search courses like WebReg's Enroll tab.

    Params: term (required), subjects (CSV), courseno, instructor, title,
    sectionid, hidefull (1/0). Returns courses with nested section rows.
    """
    term = request.args.get("term", "")
    q = ["c.term_code = ?"]
    args = [term]

    subjects = [s for s in request.args.get("subjects", "").split(",") if s]
    if subjects:
        q.append("c.subject_code IN (%s)" % ",".join("?" * len(subjects)))
        args += subjects
    courseno = request.args.get("courseno", "").strip()
    if courseno:
        q.append("UPPER(c.course_num) = UPPER(?)")
        args.append(courseno)
    title = request.args.get("title", "").strip()
    if title:
        q.append("c.title LIKE ?")
        args.append(f"%{title}%")
    instructor = request.args.get("instructor", "").strip()
    sectionid = request.args.get("sectionid", "").strip()
    if sectionid:
        q.append("c.id IN (SELECT course_id FROM sections WHERE section_id = ?)")
        args.append(sectionid)
    if instructor:
        q.append("c.id IN (SELECT course_id FROM sections WHERE instructor LIKE ?)")
        args.append(f"%{instructor}%")

    courses = rows(db().execute(
        "SELECT c.* FROM courses c WHERE %s ORDER BY c.subject_code, "
        "CAST(REPLACE(REPLACE(c.course_num,'L',''),'R','') AS INTEGER), c.course_num"
        % " AND ".join(q), args))

    hidefull = request.args.get("hidefull") == "1"
    for c in courses:
        secs = rows(db().execute(
            "SELECT * FROM sections WHERE course_id = ? ORDER BY group_code, "
            "CASE meeting_type WHEN 'FI' THEN 1 ELSE 0 END, section_code", (c["id"],)))
        if hidefull:
            groups_open = {s["group_code"] for s in secs
                           if s["enrollable"] and (s["seats_avail"] or 0) > 0}
            secs = [s for s in secs if s["group_code"] in groups_open]
        c["sections"] = secs
    return jsonify([c for c in courses if c["sections"]])


# ---------------------------------------------------------------- api: schedule

def _get_schedule(term):
    conn = db()
    row = conn.execute(
        "SELECT id FROM schedules WHERE term_code=? AND name='My Schedule'",
        (term,)).fetchone()
    if row:
        return row["id"]
    cur = conn.execute(
        "INSERT INTO schedules (term_code, name) VALUES (?, 'My Schedule')", (term,))
    conn.commit()
    return cur.lastrowid


@app.route("/api/schedule")
def api_schedule():
    term = request.args.get("term", "")
    sid = _get_schedule(term)
    items = rows(db().execute("""
        SELECT si.id AS item_id, si.status, si.units, si.grade_option,
               c.id AS course_id, c.subject_code, c.course_num, c.title,
               s.id AS section_pk, s.group_code, s.section_code, s.section_id
        FROM schedule_items si
        JOIN courses c ON c.id = si.course_id
        JOIN sections s ON s.id = si.section_pk
        WHERE si.schedule_id = ?
        ORDER BY c.subject_code, c.course_num""", (sid,)))
    for it in items:
        it["meetings"] = rows(db().execute(
            "SELECT * FROM sections WHERE course_id=? AND group_code=? "
            "AND (enrollable=0 OR id=?) ORDER BY section_code",
            (it["course_id"], it["group_code"], it["section_pk"])))
    return jsonify(items)


@app.route("/api/schedule/add", methods=["POST"])
def api_schedule_add():
    d = request.get_json(force=True)
    term, section_pk = d["term"], d["section_pk"]
    conn = db()
    sec = conn.execute("SELECT * FROM sections WHERE id=?", (section_pk,)).fetchone()
    if not sec or not sec["enrollable"]:
        return jsonify({"error": "Invalid section."}), 400
    sid = _get_schedule(term)
    dup = conn.execute(
        "SELECT 1 FROM schedule_items WHERE schedule_id=? AND course_id=?",
        (sid, sec["course_id"])).fetchone()
    if dup:
        return jsonify({"error": "You are already enrolled in this class."}), 409
    conn.execute(
        "INSERT INTO schedule_items (schedule_id, course_id, section_pk, status,"
        " units, grade_option) VALUES (?,?,?,?,?,?)",
        (sid, sec["course_id"], section_pk, d.get("status", "enrolled"),
         d.get("units", "4"), d.get("grade_option", "L")))
    conn.commit()
    return jsonify({"ok": True})


@app.route("/api/schedule/drop", methods=["POST"])
def api_schedule_drop():
    d = request.get_json(force=True)
    conn = db()
    conn.execute("DELETE FROM schedule_items WHERE id=?", (d["item_id"],))
    conn.commit()
    return jsonify({"ok": True})


@app.route("/api/schedule/change", methods=["POST"])
def api_schedule_change():
    """Change units/grading option, WebReg 'Change' flow."""
    d = request.get_json(force=True)
    conn = db()
    conn.execute(
        "UPDATE schedule_items SET units=COALESCE(?,units),"
        " grade_option=COALESCE(?,grade_option) WHERE id=?",
        (d.get("units"), d.get("grade_option"), d["item_id"]))
    conn.commit()
    return jsonify({"ok": True})


if __name__ == "__main__":
    if not DB_PATH.exists():
        raise SystemExit("data/webreg.db missing — run: python3 seed.py")
    app.run(host="127.0.0.1", port=PORT, debug=False)
