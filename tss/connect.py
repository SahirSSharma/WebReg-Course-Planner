#!/usr/bin/env python3
"""TSS (Triton Student System) session capture + OData discovery.

TSS is SAP Student Lifecycle Management behind a SAP Fiori launchpad at
https://tss.ucsd.edu/fiori (https://sis.ucsd.edu redirects there). All class
data is served by OData v2 services under /sap/opu/odata/, behind UCSD SSO.
See docs/research/TSS_RECON.md for the full recon.

What this script does:
  1. Opens a REAL (headed) Chromium window at https://sis.ucsd.edu. You log in
     yourself with UCSD SSO + Duo — we never touch credentials.
  2. Detects login success (URL lands on tss.ucsd.edu/fiori, or the Fiori
     shell DOM appears), then:
       - saves cookies (storage_state) to tss/state.json, and keeps re-saving
         every few seconds while the window stays open
       - fetches the two discovery endpoints with your session
         (/sap/bc/ui2/start_up and the IWFND CATALOGSERVICE ServiceCollection)
       - navigates you straight to the Schedule of Classes app
         (#YSchedule-view)
  3. Records EVERY /sap/opu/odata/ response the app makes while you browse —
     JSON bodies and XML $metadata alike — into data/tss_raw/ with a
     manifest.jsonl mapping each file back to its full request URL.

Usage:
  python3 tss/connect.py            # normal run
  python3 tss/connect.py --url URL  # alternate entry point if sis.ucsd.edu moves

IMPORTANT — SAP sessions expire after ~30-60 minutes of idle time. Capture
everything you need in ONE sitting: log in, pick Fall 2026, search several
departments, then close the window. Everything is saved live as you browse.
"""
import argparse
import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "tss" / "state.json"
RAW = ROOT / "data" / "tss_raw"
MANIFEST = RAW / "manifest.jsonl"

ENTRY_URL = "https://sis.ucsd.edu"          # 302 -> https://tss.ucsd.edu/fiori
FIORI_URL = "https://tss.ucsd.edu/fiori"
SCHEDULE_URL = "https://tss.ucsd.edu/fiori#YSchedule-view"

# Post-login discovery endpoints (recon §3A). start_up maps every launchpad
# tile to its OData service; the catalog lists all activated OData services.
DISCOVERY = [
    ("startup", "https://tss.ucsd.edu/sap/bc/ui2/start_up"),
    ("catalog_services",
     "https://tss.ucsd.edu/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/"
     "ServiceCollection?$format=json"),
]

# What we capture off the wire: all SAP OData traffic + the launchpad bootstrap.
CAPTURE_URL = re.compile(r"/sap/opu/odata/|/sap/bc/ui2/start_up", re.I)

FETCH_JS = """async (u) => {
  const r = await fetch(u, {credentials: 'include',
                            headers: {'Accept': 'application/json, */*'}});
  return {status: r.status,
          ct: r.headers.get('content-type') || '',
          text: await r.text()};
}"""


def banner(lines):
    width = max(len(l) for l in lines) + 4
    print("\n" + "=" * width)
    for l in lines:
        print("  " + l)
    print("=" * width + "\n")


def main():
    ap = argparse.ArgumentParser(
        description="Capture a logged-in TSS session and record its OData "
                    "traffic to data/tss_raw/ (see module docstring).")
    ap.add_argument("--url", default=ENTRY_URL,
                    help=f"entry URL (default: {ENTRY_URL})")
    ap.add_argument("--login-timeout", type=int, default=600,
                    help="seconds to wait for you to finish SSO+Duo "
                         "(default: 600)")
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright  # import after --help

    RAW.mkdir(parents=True, exist_ok=True)
    state = {"n": 0, "logged_in": False}

    def record(kind, url, status, content_type, body_bytes):
        """Write one captured response + a manifest line."""
        state["n"] += 1
        n = state["n"]
        is_xml = ("$metadata" in url or "xml" in content_type.lower())
        ext = "xml" if is_xml else "json"
        slug = re.sub(r"[^A-Za-z0-9_.-]+", "_",
                      re.sub(r"^https?://[^/]+", "", url))[:110].strip("_")
        fname = f"{n:04d}_{slug or 'root'}.{ext}"
        (RAW / fname).write_bytes(body_bytes)
        with MANIFEST.open("a") as mf:
            mf.write(json.dumps({
                "n": n, "file": fname, "kind": kind, "status": status,
                "content_type": content_type, "url": url,
                "ts": datetime.datetime.now().isoformat(timespec="seconds"),
            }) + "\n")
        print(f"  [{n:04d}] captured {fname}")

    def on_response(resp):
        try:
            url = resp.url
            if not CAPTURE_URL.search(url):
                return
            if resp.status in (204, 301, 302, 303, 307, 308):
                return
            ct = resp.headers.get("content-type", "")
            # Keep JSON and XML ($metadata / Atom); skip images/scripts.
            if not ("json" in ct.lower() or "xml" in ct.lower()
                    or "$metadata" in url):
                return
            body = resp.body()
            if not body:
                return
            record("xhr", url, resp.status, ct, body)
        except Exception:
            pass  # never let a capture error break browsing

    def save_state(ctx):
        try:
            ctx.storage_state(path=str(STATE))
            return True
        except Exception:
            return False

    def looks_logged_in(ctx, page):
        """True only once SAP has issued a real session.

        The Fiori URL alone is NOT proof — sis.ucsd.edu bounces through
        tss.ucsd.edu/fiori BEFORE auth, which used to false-positive and
        yank the page away mid-login. Require a SAP_SESSIONID cookie on
        tss.ucsd.edu and that we're not sitting on an SSO/Duo page."""
        try:
            url = page.url
            if ("a.ucsd.edu" in url or "duosecurity" in url
                    or "shibboleth" in url.lower()):
                return False
            if page.query_selector("input[type=password]") is not None:
                return False
            cookies = ctx.cookies("https://tss.ucsd.edu")
            has_sap = any(c["name"].startswith("SAP_SESSIONID")
                          for c in cookies)
            return has_sap and "tss.ucsd.edu" in url
        except Exception:
            return False

    def run_discovery(page):
        """Fetch start_up + service catalog with the page's own cookies."""
        for name, url in DISCOVERY:
            try:
                r = page.evaluate(FETCH_JS, url)
                record(f"discovery:{name}", url, r["status"], r["ct"],
                       r["text"].encode("utf-8", "replace"))
                if r["status"] != 200:
                    print(f"  WARNING: {name} returned HTTP {r['status']}")
            except Exception as e:
                print(f"  WARNING: discovery fetch {name} failed: {e}")

    banner([
        "TSS CAPTURE — a Chromium window is opening at sis.ucsd.edu.",
        "1. Log in with your UCSD SSO username + password, then approve Duo.",
        "   (This script never sees or stores your credentials.)",
        "2. After login I will jump you to the Schedule of Classes app.",
        "",
        "NOTE: SAP sessions expire after ~30-60 min idle.",
        "Capture everything in ONE sitting.",
    ])

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context(
            storage_state=str(STATE) if STATE.exists() else None,
            viewport={"width": 1500, "height": 950})
        ctx.on("response", on_response)
        page = ctx.new_page()

        try:
            page.goto(args.url, timeout=120000)
        except Exception as e:
            print(f"Could not open {args.url}: {e}")

        # ---- Phase 1: wait for the user to finish SSO + Duo -------------
        waited = 0
        try:
            while not state["logged_in"] and waited < args.login_timeout:
                if not ctx.pages:
                    break
                pg = ctx.pages[-1]
                if looks_logged_in(ctx, pg):
                    state["logged_in"] = True
                    break
                pg.wait_for_timeout(2000)
                waited += 2
        except KeyboardInterrupt:
            pass
        except Exception:
            pass  # window closed mid-login

        if state["logged_in"] and ctx.pages:
            page = ctx.pages[-1]
            print("\nLogin detected — saving session to tss/state.json")
            save_state(ctx)

            # ---- Phase 2: discovery + jump to Schedule of Classes ------
            try:  # let the post-SAML redirect dance settle first
                page.wait_for_load_state("networkidle", timeout=20000)
            except Exception:
                pass
            print("Fetching discovery endpoints (start_up + OData catalog)…")
            run_discovery(page)
            try:
                print("Opening Schedule of Classes (#YSchedule-view)…")
                page.goto(SCHEDULE_URL, timeout=60000)
            except Exception as e:
                print(f"  WARNING: could not open {SCHEDULE_URL}: {e}\n"
                      f"  Navigate there manually inside the window.")

            banner([
                "YOU'RE IN — now browse so I can record the API:",
                "  1. In Schedule of Classes, pick term  Fall 2026.",
                "  2. Search several departments one after another",
                "     (e.g. CSE, MATH, BILD, ECON, COGS, PHYS…).",
                "  3. Page through results; click a few sections open",
                "     (notes/seat counts fire extra API calls).",
                "  4. LEAVE THIS WINDOW OPEN while you do it — every",
                "     response is saved to data/tss_raw/ as it happens.",
                "  5. Close the browser window when you're done.",
                "",
                "Reminder: the SAP session dies after ~30-60 min idle —",
                "finish the whole capture in this one sitting.",
            ])
        elif not state["logged_in"]:
            print("\nLogin was not detected (window closed or timed out).")

        # ---- Phase 3: keep recording + re-saving cookies until close ----
        # Exit ONLY when every tab is closed (or Ctrl-C) — a single tab
        # closing or navigating must not end the capture.
        try:
            while ctx.pages:
                try:
                    ctx.pages[-1].wait_for_timeout(3000)
                except Exception:
                    continue  # that tab went away; re-check remaining tabs
                save_state(ctx)
        except KeyboardInterrupt:
            print("\nCtrl-C — wrapping up.")

        save_state(ctx)  # best-effort final save
        try:
            browser.close()
        except Exception:
            pass

    print(f"\nSession state → {STATE} "
          f"({'saved' if STATE.exists() else 'NOT saved — login incomplete?'})")
    print(f"Captured {state['n']} responses → {RAW}")
    print(f"Manifest (file → URL map) → {MANIFEST}")
    if state["n"] == 0:
        print("No OData traffic captured — did you reach the Schedule of "
              "Classes app and run a search?")
    else:
        print("Next: python3 tss/import_tss.py --inspect   "
              "(then fill CONFIG and run the import)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
