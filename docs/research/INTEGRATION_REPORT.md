# Integration Report — 2026-07-21

Integrator pass over all four builder deliverables (scraper, backend, frontend,
TSS bridge). Seeded the DB, diffed frontend fetches against backend routes,
ran a 19-step headless-Playwright end-to-end, and screenshotted every view at
1336 / 1600 / 2560 px.

## Environment

- `python3 seed.py` → `data/webreg.db` from `data/parsed/DEMO/CSE.json`
  (real SP15 CSE data: 4 courses, 39 section rows). Terms: DEMO (default,
  source soc) + FA26 (tss placeholder, empty until a TSS import runs).
- App: `python3 app.py` → **http://localhost:5070** (see bug #1).

## Bugs found and fixed

1. **Port 5060 is browser-blocked** (`app.py`, README, DESIGN.md, PROGRESS.md,
   tss/README.md). Chromium refused `http://localhost:5060` with
   `ERR_UNSAFE_PORT` — 5060 is SIP, on Chrome's and Firefox's restricted-port
   lists, so the app was unreachable in a real browser. Default port moved to
   **5070** (`WEBREG_PORT` env still overrides).
2. **`/api/appointment` shape mismatch** (`app.py`). Backend returned
   `first_pass`/`second_pass` as flat strings; the frontend renders
   `{start, end}` objects and fell back to "TBA" everywhere. Backend now
   returns structured objects; modal shows real pass windows.
3. **Final-exam date never reached the UI** (`seed.py`). The scraper's frozen
   format puts the exam date in the section-code field and only a weekday
   letter in `days` (with bare `S` for Saturday). The frontend derives both
   weekday and date from `days`, so the Finals tab rendered zero blocks and
   final-vs-final conflicts could never fire. seed.py now normalizes FI/MI
   rows at import ("S" → "Sa", days becomes e.g. `Th 06/11/2015`), matching
   the schema comment. Scraper output format untouched.
4. **Waitlist position showed the queue length, not your position**
   (`static/js/webreg.js`). List view printed `Waitlist (N)` from the
   section's `waitlist_ct` instead of the API's stored `position`
   (ct + 1 at add time). Now prefers `it.position`.
5. **Component rows rendered DI-before-LE** (`static/js/webreg.js`). Results
   drawer and confirm dialog listed non-enrollable parents first (A01 DI above
   A00 LE). UI_SPEC §7 / §11 want section-code order; rows are now sorted
   (A00, A01, ...) regardless of which row carries the buttons.

## API contract verification (curl, all endpoints + error paths)

- `GET /api/terms`, `/api/subjects` — shapes match, DEMO `is_default:1`.
- `GET /api/search` — q parser: `CSE` (subject), `cse 101` (case-insensitive
  subject+number), `algorithm 101` (title word + number); `subjects=`,
  `courseno=`, `instructor=`, `sectionid=`, `onlyopen=1`/`hidefull=1`
  (both drop full letter-groups) all verified.
- `GET /api/appointment` — structured pass windows.
- `POST /api/schedule/add` — 400 invalid/non-enrollable pk; 409 duplicate
  ("You are already enrolled in ..."); 409 full-as-enrolled ("no seats ...
  waitlist" wording); waitlist add returns `position` (ct+1); conflicting add
  allowed with `conflict:true`.
- `POST /api/schedule/change` — grade/units update; section swap with
  position recompute; 400 cross-course pk; 400 bad item_id.
- `POST /api/schedule/drop` — ok; `GET /api/schedule` reflects all of it,
  meetings FI-last, `position` only when waitlisted.

## End-to-end (headless Chromium, 19 checks, all passing)

Term select (DEMO default) → Go → simple search "CSE" (4 courses) → expand
CSE 101 drawer (FULL Waitlist(21) red state, FINAL rows with dates) → Enroll
C00 → confirm dialog → green "Request Successful" → List view teal
`#41788D` enrolled row with DI C01 + Final Exam sub-rows → Calendar renders
4 blocks → temporarily opened seats on CSE 150 A00 via sqlite (restored to 0
after), enrolled it → yellow conflict Alert inside the confirm dialog → pink
"You have scheduling conflicts!" banner (CSE 101 and CSE 150) → 4
red-bordered calendar blocks → dropped CSE 150 from its calendar block →
waitlisted genuinely-full CSE 190 A00 → pale-cyan `#CEEBEE` row, "Waitlist
(9)" → Change dialog: grading → P/NP reflected in list → Finals tab: 2 blocks
on the Sat–Sat dated grid → Drop CSE 101 through the classic W-grade warning
dialog → row gone → Advanced search: CSE subject chip + "only seats
available" → 2 courses, full groups hidden → term switch to FA26 (0 courses,
empty schedule) and back (schedule intact) → Appointment modal.

## Screenshots (`docs/research/verify/final_*.png`)

`term`, `search` (drawer expanded), `list`, `calendar`, `finals` — each at
1336 / 1600 / 2560. Programmatic `scrollWidth <= innerWidth` assertion passed
at every width (no horizontal scroll at 1336); content stays a centered
~950–1000px column at 2560 per UI_SPEC. All 15 reviewed visually.
`05_calendar_conflict` (E2E artifact) confirms the red-border + banner state.

The DB ships with a showcase schedule (enrolled CSE 101 C00, waitlisted
CSE 190 A00, planned CSE 110 A00) so the first launch isn't empty; drop them
or `DELETE FROM schedule_items` for a clean slate.

## Remaining gaps

- **No live term data.** act.ucsd.edu answered 500 "Max Sessions Exceeded"
  for the scraper's whole retry budget (all-day outage, see SOC_FORMAT.md §5).
  Only the DEMO term (SP15 CSE) is seeded. Retry off-peak:
  `python3 scraper/soc_scraper.py --term FA25 --probe`, then the 10-subject
  scrape, then `python3 seed.py`.
- **FA26 is an empty placeholder** until Sahir does the TSS SSO capture
  (`tss/connect.py` → `import_tss.py --inspect` → field-map edit → import).
- `hidefull` and `onlyopen` share one semantics (drop letter-groups with no
  open enrollable section) — intentional simplification.
- Chrome-only nits: "Add Event", "Create new, copy, rename ...", Book/Send-
  email links are static chrome (planning tool scope), matching the pinned UI
  but not functional.
- `static/dev_stub.py` (port 5062) is the frontend builder's sanctioned
  fixture server; harmless, kept for UI work without real data.
