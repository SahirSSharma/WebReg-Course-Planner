# TSS Recon — UCSD's WebReg Replacement (Triton Student System)

**Date:** 2026-07-21
**Purpose:** Understand UCSD's new student registration system so we can (a) capture a logged-in session and (b) discover the API that returns Fall 2026 (FA26) class data for our WebReg-lookalike planner.
**Status:** Research complete, unauthenticated probing done. No login performed yet (user will do SSO+Duo in a headed browser).

---

## 1. What TSS is

**Triton Student System (TSS)** is UC San Diego's new student information system that replaced My TritonLink / ISIS / WebReg. It went **live mid-July 2026**. Fall 2026 (FA26) enrollment happens in TSS; Summer Session 2026 was the last term booked in legacy WebReg.

- It's the system students use to **"book" courses** (not "enroll" — see below), view schedule, grades, billing, financial aid.
- Delivered by UCSD's **Enterprise Systems Renewal (ESR)** program, whose Student Information System (SIS) project (started 2019) set out to replace the 1980s mainframe ISIS.

### Vendor / platform — CONFIRMED
**The underlying system is SAP.** Two independent confirmations:
- UCSD's own ESR FAQ states the term "booking" comes from **"the underlying system (SAP Student Lifecycle Management)"** (SAP SLcM), which uses European-higher-ed terminology. Source: esr.ucsd.edu core-sis page.
- Unauthenticated HTTP probing of `tss.ucsd.edu` returns **`sap-server: true`**, sets a **`sap-usercontext: sap-client=500`** cookie, and the login bootstrap uses SAP's SSF/SAML certificate flow. This is a classic **SAP NetWeaver Gateway + SAP Fiori front-end server**.

So: SAP SLcM back end, surfaced through an **SAP Fiori Launchpad** front end. This matters enormously for data access — SAP Fiori apps are driven by **OData services** (see §3).

### The "booking" terminology
TSS says **"book courses"** instead of "enroll." Continuing students keep their PID **and** get a new **Triton Student Number (TSN)**; new FA26 students get only a TSN.

---

## 2. URLs & auth flow

### Primary URLs (verified via HTTP)
| URL | What it is | Verified |
|---|---|---|
| `https://sis.ucsd.edu` | Marketing/entry hostname; **302 → `https://tss.ucsd.edu/fiori`** | ✅ redirect confirmed |
| `https://tss.ucsd.edu/fiori` | **SAP Fiori Launchpad** — the real app shell (HTTP 200) | ✅ |
| `https://tss.ucsd.edu/fiori#YSchedule-view` | **Schedule of Classes** Fiori app (deep link cited on students.ucsd.edu enroll page) | ✅ URL cited by UCSD |
| `https://tss.ucsd.edu/sap/opu/odata/` | OData service root (SAP Gateway) — HTTP 200, behind SSO | ✅ path live |
| `https://tss.ucsd.edu/sap/bc/ui2/start_up` | Fiori launchpad bootstrap (lists all tiles + their OData services) — HTTP 200, behind SSO | ✅ path live |
| `https://tritonlink.ucsd.edu` | Portal; has a TSS icon top-right that launches TSS | ✅ cited |

- The Fiori app hash `YSchedule` tells us the custom SAP app id is **`YSchedule`** (SAP custom objects use the Y/Z namespace). Its backing OData service is therefore almost certainly a **`Y*`-named service** under `/sap/opu/odata/` (e.g. `.../sap/YSCHEDULE_SRV/` or a UCSD custom namespace — exact name to be confirmed post-login via start_up).
- SAP client is **500** (`sap-usercontext=sap-client=500`). Front end sits behind an **AWS ALB** (`AWSALBTG` cookies present).

### Auth flow
1. Hit `sis.ucsd.edu` → redirect to `tss.ucsd.edu/fiori`.
2. Fiori bootstrap auto-submits a form → **UCSD SSO (Shibboleth) at `a.ucsd.edu`** (Active Directory / AD SSO). Login page offers **"Extended Studies"** vs **"UCSD SSO"** — main-campus students pick UCSD SSO.
3. Enter **UCSD email (TritonLink username) + password**.
4. **Duo two-factor** (two-step login).
5. SAML assertion posts back to `tss.ucsd.edu`; SAP issues session cookies (`MYSAPSSO2` / `SAP_SESSIONID_*`, plus `sap-usercontext`, and the AWS ALB cookies). Fiori launchpad renders.

**Cookies that matter for a captured session:** the SAP session cookie(s) (`SAP_SESSIONID_<SID>_500`, possibly `MYSAPSSO2`), `sap-usercontext`, and the ALB stickiness cookies (`AWSALB`, `AWSALBCORS`). `storage_state` from Playwright captures all of them for the `tss.ucsd.edu` domain.

**Note on session lifetime:** SAP Gateway sessions are typically short (30–60 min idle timeout) and single-host. Plan to capture and immediately exercise the API in the same run; don't expect `state.json` to last for days.

---

## 3. Candidate data endpoints

### A. TSS OData (the real prize — requires login)
Because TSS is SAP Fiori, the Schedule-of-Classes data is served by an **OData v2 service** under:
```
https://tss.ucsd.edu/sap/opu/odata/<namespace>/<SERVICE_NAME>/<EntitySet>?$filter=...&$format=json
```
- **Discovery step (post-login):** GET `https://tss.ucsd.edu/sap/bc/ui2/start_up` returns JSON listing every launchpad tile and the OData service each app targets. This is the single best map — find the entry for app `YSchedule` and read its `serviceUrl`.
- Alternatively, GET the service catalog: `https://tss.ucsd.edu/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection?$format=json` lists all activated OData services.
- Once the service is known, its `$metadata` (`.../<SERVICE>/$metadata`) gives the full EntityType schema (terms, subjects, courses, sections, meetings, seats).
- OData supports `$format=json`, `$filter`, `$expand`, `$top/$skip` — ideal for scripted extraction of the whole FA26 catalog.
- **Best discovery in practice:** don't guess the service name — let the browser tell us. Record all XHR to `**/sap/opu/odata/**` while the user (or the script) drives the YSchedule search UI, then replay those exact request URLs with the captured cookies. (See playbook §5.)

### B. Legacy UCSD course APIs (do NOT contain FA26 — but useful for schema/fallback)
- `https://act.ucsd.edu/scheduleOfClasses/scheduleOfClassesStudent.htm` — **legacy WebReg Schedule of Classes** (HTTP 200, still up as of 2026-07-21). Public, no login. **Stops at Summer 2026** — will NOT have FA26. Useful only as a schema/UX reference and for pre-FA26 terms.
- `https://api.ucsd.edu:8243/enhancedcourse/v1/ucsdcourse?...` — UCSD's official **Enhanced Course API** (seen in search results; requires an API key / SSO developer credential). Legacy data source.
- `api-qa.ucsd.edu` — non-prod "ScheduleOfClasses-EKS v1" API referenced in results (QA only).
- Third-party mirrors: `github.com/rantaoca/ucsd-api`, `coursicle.com/ucsd` — all scrape the **legacy** SoC, so no FA26.

**Bottom line:** FA26 real class data lives **only in TSS OData behind SSO**. Everything public is legacy (≤ Summer 2026).

---

## 4. Known UX complaints / limitations (useful for our pitch)

From UCSD's own ESR notices (esr.ucsd.edu) and Guardian coverage:
- **No side-by-side section comparison** — "Viewing multiple sections side-by-side is not available in TSS." UCSD literally suggests the workaround of opening duplicate browser tabs. *(Huge opening for a WebReg-lookalike planner with a real grid/compare view.)*
- **Section notes hidden** — only shown after you click into a section, not in the listing.
- **Variable-unit courses** show raw approval ranges, not department-set values, in listings.
- **Multiple meeting locations** display badly (formatting fix in progress).
- **Multiple instructors** not fully shown (fix promised "2–3 weeks" out from late July).
- **Intermittent slow loading**; login/access disruptions ("use incognito, go directly to sis.ucsd.edu"); a July 14–19 data migration caused slowness.
- **Terminology confusion** — "booking" instead of "enrollment," new TSN numbers alongside old PID.
- **Course-approval backlog** — some courses aren't loaded yet; no ETA per course.
- Booking windows pushed from May to **mid-July** for continuing students to ease the transition.

These are all points our planner can beat: fast client-side search, side-by-side/compare, a familiar WebReg look, notes visible inline, a real schedule grid.

---

## 5. COOKIE-CAPTURE PLAYBOOK (Playwright)

Goal: launch a **headed** Chromium at the TSS login, let the user finish SSO+Duo, detect success, save `storage_state`, then record JSON XHRs while exercising the class search to discover the OData shape and dump raw JSON.

**Prereqs**
```bash
cd /Users/sahir/Desktop/WebReg
python3 -m pip install playwright && python3 -m playwright install chromium
# dirs already created: tss/  data/tss_raw/
```

**Script outline (`/Users/sahir/Desktop/WebReg/tss/capture.py`)**

Phase 1 — capture session:
1. Launch **headed** Chromium: `p.chromium.launch(headless=False)`, new context, `page = context.new_page()`.
2. `page.goto("https://sis.ucsd.edu")` — it redirects through `a.ucsd.edu` (Shibboleth) → Duo → back to `tss.ucsd.edu/fiori`.
3. **Wait for the user** to finish SSO + Duo. Do NOT automate credentials. Detect success by polling for either:
   - URL host is `tss.ucsd.edu` AND path contains `/fiori`, OR
   - a Fiori shell DOM node is present (e.g. `#shell-header` / `.sapUshellShell`), OR
   - simplest: print "Log in, then press ENTER here" and block on `input()`.
   Use a generous wait: `page.wait_for_url("**tss.ucsd.edu/fiori**", timeout=300000)` wrapped so it also tolerates the manual-ENTER fallback.
4. Save cookies: `context.storage_state(path="/Users/sahir/Desktop/WebReg/tss/state.json")`.

Phase 2 — record network + exercise search (same run, session is fresh):
5. Attach a response listener BEFORE navigating the search:
   ```python
   import json, pathlib, itertools
   OUT = pathlib.Path("/Users/sahir/Desktop/WebReg/data/tss_raw")
   ctr = itertools.count()
   def on_response(resp):
       url = resp.url
       if "/sap/opu/odata/" in url or "odata" in url.lower():
           ct = (resp.headers.get("content-type") or "")
           if "json" in ct or "$metadata" in url:
               try:
                   body = resp.body()
               except Exception:
                   return
               n = next(ctr)
               (OUT / f"{n:03d}_resp.json").write_bytes(body)
               (OUT / f"{n:03d}_meta.txt").write_text(f"{resp.status} {resp.request.method} {url}\n")
   page.on("response", on_response)
   ```
6. Navigate to the Schedule of Classes app: `page.goto("https://tss.ucsd.edu/fiori#YSchedule-view")`.
7. **Drive the search UI** so the app fires its OData calls: pick term = Fall 2026, pick a subject (e.g. CSE), click Search, page through results. Do this either manually (leave the window open, tell the user to click around) or programmatically once selectors are known. Every OData response is auto-saved to `data/tss_raw/`.
8. **Also grab the discovery artifacts explicitly** using the page's own authenticated fetch (inherits cookies, avoids CORS):
   ```python
   for u in [
     "https://tss.ucsd.edu/sap/bc/ui2/start_up",
     "https://tss.ucsd.edu/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection?$format=json",
   ]:
       data = page.evaluate("""async (u) => (await fetch(u, {credentials:'include'})).text()""", u)
       # write to data/tss_raw/
   ```
   From `start_up`/catalog, read the exact `YSchedule` service URL, then fetch its `$metadata` and its class/section entity sets with `$format=json` + `$filter` for term=FA26.

Phase 3 — reuse later:
9. Subsequent runs: `context = browser.new_context(storage_state="/Users/sahir/Desktop/WebReg/tss/state.json")` to skip login — **but** SAP sessions expire fast (~30–60 min idle); if calls 401/redirect to Shibboleth, re-run Phase 1.

**Robustness notes**
- Keep the ALB cookies (`AWSALB*`) — they pin you to the right backend; a mismatch can 500. `storage_state` keeps them.
- SAP OData needs an `X-CSRF-Token` for writes but **not for reads** (GET). We only read, so no CSRF dance needed.
- If a response is gzipped, `resp.body()` returns decoded bytes already.
- Save `$metadata` (XML) too — it documents every field name so we can map TSS → our WebReg schema.

---

## 6. Fallback FA26 data sources

Ranked by usefulness:
1. **TSS OData** (this playbook) — the only source with authoritative FA26 sections/seats/times. Primary.
2. **Per-department course-offering pages** — some departments publish FA26 lists (e.g. `literature.ucsd.edu/courses/courseofferings/fa2026u.html`, `ece.ucsd.edu/ece-tentative-course-list`, `ph.ucsd.edu/.../fall.html`). Public, HTML, incomplete, no live seats — usable to seed catalog names if TSS access slips.
3. **`catalog.ucsd.edu` (2026-27 Catalog of Record)** — official course *descriptions* and requirements, **not** term offerings or times/seats. Good for enriching course metadata (titles, units, descriptions, prereqs), not for the schedule grid.
4. **Legacy `act.ucsd.edu/scheduleOfClasses`** — schema/UX reference only; ≤ Summer 2026, no FA26.
5. **UCSD Mobile app / `api.ucsd.edu:8243` enhanced course API** — official but key-gated and legacy-backed; unclear if repointed to TSS. Low priority; investigate only if OData capture fails.

---

## 7. Open questions / to confirm post-login
- Exact OData service name + namespace for the `YSchedule` app (get from `start_up`).
- Entity model: how term / subject / course / section / meeting / seat-count are named and related.
- Whether any TSS OData read is reachable **without** login (unlikely — everything under `/sap/opu/odata/` sits behind Shibboleth) — a public guest search was NOT found.
- Duo device-remembered sessions could let `state.json` last longer; test empirically.

## Confidence
**High** on: TSS identity, SAP/Fiori platform, URLs (`sis.ucsd.edu` → `tss.ucsd.edu/fiori`), auth = Shibboleth `a.ucsd.edu` + Duo, OData-under-Fiori data model, FA26-only-in-TSS. Verified by live HTTP probes (`sap-server: true`, client 500, redirect chain) plus UCSD's own docs.
**Medium/guess (marked as such above):** exact OData service names/paths and session lifetime — resolvable only after the user logs in and we read `start_up`.
