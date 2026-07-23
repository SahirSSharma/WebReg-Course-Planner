# Refreshing the FA26 catalog

**TL;DR — the only thing you do by hand is log in. Everything else is automatic.**

```bash
cd ~/Desktop/WebReg
python3 scripts/refresh.py
```

1. A Chromium window opens at `sis.ucsd.edu`. **Log in with UCSD SSO + Duo.**
2. Then **stop** — do not click into Schedule of Classes, do not close the
   window. The script detects your login and takes over: it pulls the fresh
   catalog, imports it, stamps today's date, and rebuilds the site.
3. When it prints `Refresh built locally`, the new data is in your working tree
   (`data/` + `site/`) but **not pushed**. Review, then deploy (below).

You do **not** need to fight the Schedule-of-Classes popup that steals focus —
that only affects a human clicking around. The puller loads the app under
Playwright's control, where it behaves, so you never touch it.

## Deploying after a refresh

- Preview first: `git checkout staging && git add -A && git commit && git push origin staging`
  → https://sahirssharma.github.io/WebReg-Course-Planner/preview/
- Ship to production: merge `staging` into `main` and push
  → https://sahirssharma.github.io/WebReg-Course-Planner/
  (production deploy runs automatically on push to `main`).

Per project rule, **production ships only on your explicit OK** — approving the
preview is not approval to ship.

## How the pull actually works (so a future refresh isn't a mystery)

TSS changed in July 2026. The con_module OData4 service (`YUCSD_CON_MODULE`,
`YUCSD_CON_EVENTS`) now returns **HTTP 403 "Access denied"** to any request we
craft ourselves — even a byte-accurate multipart `$batch` from inside the page.
The gateway keys on the Schedule-of-Classes Fiori app's real request envelope
(`sap-passport`, frame origin, `x-xhr-logon`). A useful tell: `/sap/bc/ui2/start_up`
returns 200 (session alive) while con_module 403s.

So the direct-GET approach in `tss/fetch_soc.py` is **dead**. The working method,
in **`tss/pull_soc_batch.py`**:

1. Load the SoC app in Playwright using the logged-in session (`tss/state.json`).
2. Click **Go** so the app issues its own con_module `$batch` POST.
3. **Intercept that request** with `ctx.route` and rewrite its body to page the
   entire FA26 catalog:
   - `GET YUCSD_CON_MODULE?$filter=AcYearText eq '2026/2027' and AcademicPeriodText eq 'Fall Quarter'&$top=5000`
   - `GET YUCSD_CON_EVENTS?$filter=AcYear eq '2026' and AcPeriod eq '2'&$top=5000`
   - both with `$count=true`, paged by 5000.

Because it reuses the app's own request (headers, passport, cookies), it passes.

### If a future term changes (e.g. Winter 2027)

Update the two filters at the top of `tss/pull_soc_batch.py`:

- `MOD_FILTER` uses the display strings: `AcYearText eq '2026/2027'` +
  `AcademicPeriodText eq 'Fall Quarter'`.
- `EVT_FILTER` uses the codes: `AcYear eq '2026'` + `AcPeriod eq '2'`
  (period code: Fall=2, Winter=3, Spring=4 — confirm from the module rows'
  `AcademicYear`/`AcademicPeriod` fields).

Seats are a **point-in-time snapshot** from when you pulled — not real-time.
They drift as students enroll, so the site is for planning; official WebReg is
the source of truth for live seat counts.
