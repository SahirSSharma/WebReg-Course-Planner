# WebReg Revival

A faithful rebuild of UCSD's classic **WebReg** as a local class-planning website — for everyone who misses it now that TSS is the only option.

Classic WebReg UI/UX, real UCSD course data (classes, professors, sections, times, seats), running on localhost. Plan your schedule the way you always did: search, expand a course, pick your discussion, hit Enroll (here it plans — no live registration), and see it land on the weekly calendar.

## Quick start

```bash
pip3 install -r requirements.txt
python3 seed.py          # builds data/webreg.db from bundled/scraped UCSD data
python3 app.py           # serves http://localhost:5060
```

## Data sources

- **Legacy Schedule of Classes** (`act.ucsd.edu/scheduleOfClasses`) — public, still live, terms through Summer 2026. `scraper/soc_scraper.py` pulls it (the server is overloaded in enrollment season; the scraper retries patiently).
- **TSS (the new system)** — the only home of Fall 2026 data. `python3 tss/connect.py` opens a real browser window; log in with UCSD SSO + Duo and it captures your session, discovers TSS's JSON endpoints, and imports FA26 into the same database. Cookies stay in `tss/state.json`, which is git-ignored and never leaves your machine.

## Layout

```
app.py            Flask server + JSON API
seed.py           build/refresh data/webreg.db
schema.sql        SQLite schema
scraper/          legacy Schedule of Classes scraper
tss/              TSS SSO capture + importer
templates/        WebReg pages
static/           css/js/img — the classic WebReg look
docs/             DESIGN.md, research notes
PROGRESS.md       changelog / session handoffs
```

## Status

See [PROGRESS.md](PROGRESS.md). Not affiliated with UC San Diego. Planning tool only — it never touches real registration.
