# WebReg Course Planner

UCSD's classic **WebReg**, rebuilt as a class-planning website that runs on your own computer — for everyone who misses it now that TSS is the only option. Real Fall 2026 courses, professors, times, and seat counts included.

## Get it running (no experience needed)

You don't need to know how to code. Just follow these steps top to bottom — it takes about 5 minutes.

**1. Install Python** (the program that runs the website)

Go to [python.org/downloads](https://www.python.org/downloads/) and click the big yellow download button, then open the installer.
- **Windows:** on the first screen, check the box that says **"Add Python to PATH"** before clicking Install.
- **Mac:** just click through the installer.

**2. Download this project**

At the top of this page, click the green **"Code"** button → **"Download ZIP"**. When it finishes, double-click the ZIP file to unzip it. You'll get a folder called `WebReg-Course-Planner-main`.

**3. Open a terminal**

- **Mac:** press `Cmd + Space`, type `Terminal`, press Enter.
- **Windows:** press the Windows key, type `cmd`, press Enter.

A window with a text prompt appears. That's where you'll paste the commands below.

**4. Point the terminal at the folder you downloaded**

Type `cd ` (with a space after it), then **drag the unzipped folder from your Downloads into the terminal window**, and press Enter.

**5. Copy and paste these three commands, one at a time** (press Enter after each — the first two take a minute)

On **Mac**:

```
pip3 install -r requirements.txt
python3 seed.py
python3 app.py
```

On **Windows**:

```
pip install -r requirements.txt
python seed.py
python app.py
```

**6. Open the website**

When the last command says it's running, open your browser and go to:

**http://localhost:5070**

That's it — WebReg is back. Search for classes, expand a course, pick your discussion, and watch it land on the weekly calendar.

**Stopping and restarting:** to stop, just close the terminal window. To use it again later, repeat steps 3–4 and run only the last command (`python3 app.py` on Mac, `python app.py` on Windows) — no need to redo the install.

**Something went wrong?** The most common fix: close the terminal, reopen it, and try step 5 again. If Windows says "python is not recognized", reinstall Python and make sure the **"Add Python to PATH"** box is checked.

---

## Technical README

A faithful rebuild of classic WebReg's UI/UX served by a small Flask app over SQLite, on localhost. Planning only — it never touches real registration.

### Quick start

```bash
pip3 install -r requirements.txt
python3 seed.py          # builds data/webreg.db from the bundled course data
python3 app.py           # serves http://localhost:5070 (5060 is browser-blocked: SIP)
```

The parsed course data (FA25 sample departments + all of FA26) is committed under `data/parsed/`, so seeding works offline with no scraping required.

### Data sources

- **Legacy Schedule of Classes** (`act.ucsd.edu/scheduleOfClasses`) — public, still live, terms through Summer 2026. `scraper/soc_scraper.py` pulls it (the server is overloaded in enrollment season; the scraper retries patiently).
- **TSS (the new system)** — the only home of Fall 2026 data. `python3 tss/connect.py` opens a real browser window; log in with UCSD SSO + Duo and it captures your session, discovers TSS's JSON endpoints, and imports FA26 into the same database. Cookies stay in `tss/state.json`, which is git-ignored and never leaves your machine. Refreshing data is optional — a full FA26 snapshot already ships in the repo.

### Layout

```
app.py            Flask server + JSON API
seed.py           build/refresh data/webreg.db
schema.sql        SQLite schema
data/parsed/      committed course data (per term, per subject)
scraper/          legacy Schedule of Classes scraper
tss/              TSS SSO capture + importer
templates/        WebReg pages
static/           css/js/img — the classic WebReg look
docs/             DESIGN.md, research notes
PROGRESS.md       changelog / session handoffs
```

### Status

See [PROGRESS.md](PROGRESS.md). Not affiliated with UC San Diego. Planning tool only — it never touches real registration.
