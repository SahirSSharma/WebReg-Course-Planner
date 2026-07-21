# Progress Log

## 2026-07-21 — Integration pass (all builders merged, E2E green)
- Seeded `data/webreg.db` (DEMO term = real SP15 CSE data, 4 courses / 39 sections; FA26 placeholder awaits TSS import).
- Fixed 5 integration bugs: default port 5060→**5070** (browsers block 5060/SIP as unsafe), `/api/appointment` response shape, final-exam dates lost between scraper format and UI (seed.py now normalizes FI rows into `days`), waitlist position display (queue length vs your position), DI-before-LE row ordering in results/confirm.
- Verified every API endpoint incl. error paths via curl; 19-step headless-Playwright E2E all passing (enroll → list/calendar → conflict banner + red blocks → waitlist → change → drop → finals → advanced search → term switch → appointment).
- Screenshots of all 5 views at 1336/1600/2560 in `docs/research/verify/final_*.png`, no horizontal scroll at any width. Full detail: `docs/research/INTEGRATION_REPORT.md`.

## 2026-07-21 — Project start (ultracode build)
- Recon: legacy Schedule of Classes still live (browser UA required; terms end at SU26/S326 — **FA26 exists only in TSS**). Server intermittently 500s "Max Sessions Exceeded" (enrollment-season load) → scraper needs retry/backoff.
- Scaffold: Flask app (`app.py`, port 5070 — moved off 5060 during integration: Chrome/Firefox block 5060 as an unsafe SIP port), SQLite schema (`schema.sql`), repo `SahirSSharma/webreg-revival` (private) created and pushed.
- Research workflow launched: WebReg UI spec from real screenshots, SOC HTML format, TSS recon, feature inventory → `docs/research/`.
