# tss/ — getting Fall 2026 data out of TSS

FA26 class data exists only inside TSS (SAP Fiori at `tss.ucsd.edu/fiori`,
behind UCSD SSO + Duo). These two scripts get it into the planner:

- `connect.py` — opens a real browser, you log in, it records every OData
  response TSS makes while you browse the Schedule of Classes.
- `import_tss.py` — turns those raw captures into `data/parsed/FA26/*.json`
  (the frozen format `seed.py` eats) and registers FA26 in `data/terms.json`.

Background/recon: `docs/research/TSS_RECON.md`.

## The 5-step flow

**1. Start the capture** (from the repo root):

```bash
python3 tss/connect.py
```

A Chromium window opens at `sis.ucsd.edu`. Log in with your UCSD SSO
username/password and approve Duo. The script never sees your credentials.

**2. Let it detect the login.** Once you land on the Fiori launchpad, the
terminal prints "Login detected", saves your session to `tss/state.json`,
auto-fetches the two API discovery endpoints, and jumps the browser to the
Schedule of Classes app (`#YSchedule-view`).

**3. Browse — this IS the capture.** In the Schedule of Classes app:
   - pick term **Fall 2026**
   - search several departments back-to-back (CSE, MATH, BILD, ECON, COGS,
     PHYS, …every subject you care about)
   - page through all results; click a few sections open (notes and seat
     details fire extra API calls)

   Every response lands in `data/tss_raw/` as it happens (the terminal
   echoes each one). **Do it all in one sitting** — SAP sessions expire
   after ~30–60 minutes idle.

**4. Close the browser window** when you're done. The script exits cleanly
and prints how many responses it captured.

**5. Inspect, map, import:**

```bash
python3 tss/import_tss.py --inspect   # shows the real field names TSS used
# → open tss/import_tss.py, put those names first in CONFIG["field_map"]
#   (2-minute job; only needed once)
python3 tss/import_tss.py             # writes data/parsed/FA26/<SUBJ>.json
python3 seed.py                       # loads FA26 into data/webreg.db
```

Then restart the app (`python3 app.py`, port 5070) and FA26 shows up in the
term picker (source `tss`).

## Notes

- `tss/state.json` and everything under `data/` are git-ignored — cookies
  and captures never get committed.
- If the import says it can't resolve subject/number for most entities,
  that's the signal `CONFIG["field_map"]` still has guesses where it needs
  the real key names from step 5's `--inspect` output.
- Sessions die fast; `state.json` is a convenience for a quick re-run, not
  a durable login. If a later run bounces you back to SSO, just log in again.
- `data/tss_raw/manifest.jsonl` maps every captured file back to its full
  request URL — useful for replaying a specific OData query later.
