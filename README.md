# WebReg Course Planner

UCSD's classic **WebReg**, brought back as a class-planning tool — for everyone who misses it now that TSS is the only option. It looks and works like the WebReg you know, loaded with **real Fall 2026 courses, professors, times, rooms, and seat counts**.

### ▶︎ Use it now — no install, nothing to download:

## **https://sahirssharma.github.io/WebReg-Course-Planner/**

Just open the link. It runs entirely in your browser, and your planned schedule is saved privately on your own device.

![Search results and schedule](docs/research/verify/fb_results.png)

---

## What it does

- **Search Fall 2026 classes** the WebReg way — by subject, course number, instructor, title, or section ID, plus advanced filters for units, days, and times. Type `cse11` or `cse 11` — both work.
- **Plan your schedule.** Hit **Plan** on any section and it drops onto your weekly **Calendar**, **List**, and **Finals** views.
- **Compare options.** Plan several sections of the same course side-by-side to find the combination that fits.
- **See conflicts instantly** — overlapping classes get a red highlight and a warning banner, exams included.
- **Real data:** 1,766 courses, 8,000+ sections across 150+ departments — actual professors, buildings, rooms, seat counts, waitlists, and final-exam dates pulled straight from UCSD's registration system.

It's a **planning tool** — it helps you build the perfect schedule, but it never enrolls you or touches your real registration. When the time comes, you still book your classes in TSS.

![Weekly calendar with conflict detection](docs/research/verify/fb_calendar.png)

---

## How it works

The hard part of a UCSD planner is the data. Fall 2026 lives only inside **TSS** (UCSD's new SAP-based system), behind SSO — and its own class-search page is unreliable. This project gets the data by capturing an authenticated session and reading TSS's backend course-search API directly, then maps every course, section, meeting, instructor, and final into the classic WebReg layout.

The public site is a **fully static build**: the Fall 2026 catalog is baked into the page, and all searching and schedule-building happen in your browser. That's why it's free to host, needs no server, and keeps each person's schedule private — nothing is uploaded anywhere.

> **Note:** seat and waitlist counts are a **snapshot** from when the data was last captured; they don't update live. Everything else (times, rooms, instructors, finals) is stable for the term.

---

## For developers

The repo contains both the **static site** (what's deployed) and a small **Flask + SQLite app** used for local development and data work.

### Run the full app locally

```bash
pip3 install -r requirements.txt
python3 seed.py          # builds data/webreg.db from the committed course data
python3 app.py           # serves http://localhost:5070  (5060 is browser-blocked as a SIP port)
```

Parsed course data (all of FA26 + sample FA25 departments) is committed under `data/parsed/`, so seeding works offline — no scraping required.

### Build & preview the static site

```bash
python3 scripts/export_static.py         # bakes FA26 into site/data/catalog.json
cd site && python3 -m http.server 5090   # preview at http://localhost:5090
```

The static build (`site/`) reuses the exact same frontend. `site/js/localdb.js` overrides `fetch` for the `/api/*` routes, so the UI runs unchanged with client-side search and a `localStorage` schedule instead of the Flask backend.

### Refresh the Fall 2026 data

```bash
python3 tss/connect.py               # opens a browser; log in with UCSD SSO + Duo
python3 tss/import_fa26.py           # maps the captured TSS data into WebReg's format
python3 seed.py                      # rebuild the database
python3 scripts/export_static.py     # re-bake the static bundle
# then redeploy: push the contents of site/ to the gh-pages branch
```

Your session cookies live in `tss/state.json`, which is git-ignored and never leaves your machine.

### Data sources

- **TSS** (`tss.ucsd.edu`) — SAP Student system; the only source of Fall 2026 offerings. Class-search data comes from its OData service `yucsd_con_module` (course list, events/sections, seats, meeting times, finals).
- **Legacy Schedule of Classes** (`act.ucsd.edu/scheduleOfClasses`) — public, still live for terms through Summer 2026; used for older terms and as a schema reference. `scraper/soc_scraper.py` pulls it with patient retry/backoff.

### Layout

```
site/               the deployed static site (index.html, css, js, data, localdb.js)
scripts/            export_static.py — build the static data bundle
app.py              Flask server + JSON API (local dev)
seed.py             build data/webreg.db from data/parsed/
schema.sql          SQLite schema
data/parsed/        committed course data (per term, per subject)
scraper/            legacy Schedule of Classes scraper
tss/                TSS SSO capture + FA26 importer
templates/ static/  the WebReg UI (source of the static build)
docs/               DESIGN.md, UI spec, research notes, screenshots
PROGRESS.md         changelog / build log
```

### Deployment

The site is served by **GitHub Pages** from the `gh-pages` branch (root). To redeploy, push the current contents of `site/` to that branch.

---

## Disclaimer

Not affiliated with, endorsed by, or connected to the University of California, San Diego. This is an independent, non-commercial planning tool made by a student. It does not perform enrollment and does not access your UCSD account — data is read from UCSD's own systems using your own login and stays on your device. Course data may be out of date; always confirm details in TSS before enrolling.
