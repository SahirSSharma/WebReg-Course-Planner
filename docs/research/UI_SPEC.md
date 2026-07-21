# UCSD WebReg — Visual UI Specification (for pixel-faithful clone)

Compiled 2026-07-21 from primary-source screenshots. WebReg ("WebReg 2.0", `act.ucsd.edu/webreg2`)
launched Feb 2015 and kept essentially the same UI until its 2026 retirement (replaced by Triton
Student System). A 2023 video frame confirms the 2015 layout survived unchanged.

## Reference images (all in `docs/research/refs/`)

| Ref | File | What it shows | Era |
|---|---|---|---|
| **D** | `webreg2_demo.pdf` (22 slides) + rendered `webreg2_p03..p19-*.png` | Official Registrar demo deck of WebReg 2.0 — every screen: landing, main page, search, advanced search, results drawers, confirm dialog, success dialog, List/Calendar/Finals views, drop warning, term dropdown, appointment popup | May 2015 |
| **R** | `revelle_enroll.pdf` p.6–15 + `revelle_p06/09/10/13-*.png` | Student-facing WebReg screenshots: populated List view (enrolled/waitlist rows), Calendar view, Enroll confirm w/ yellow Alert box, conflict warning, email-confirmation dialog | Fall 2017/2018 |
| **T** | `roosevelt_enroll.pdf` p.8–20 | Legacy **WebReg 1.5** (yellow-bar UI) + old Class Pre-Planner + old Schedule of Classes — predecessor look only | Fall 2013 |
| **Y** | `yt_lPqnlCvBd8Q_maxres.jpg` | Real WebReg session frame (results drawer, My Schedule bar) proving layout unchanged | Nov 2023 |

Citations below use D-pN (demo slide N), R-pN, T-pN, Y.

---

## 1. Extracted color palette (sampled from pixels; JPEG-fuzzed, round to these)

| Token | Hex | Where seen |
|---|---|---|
| `--banner-blue` | `#136A95` → `#1A719C` (subtle gradient, darker at top ~`#0D648F`) | MY TRITONLINK header band (D-p3, D-p12) |
| `--dark-teal` | `#0A4A65` | Tab-strip band, pagination buttons (First/Last/page nums), List-view outer frame, calendar header row (D-p8, D-p12, D-p15) |
| `--enrolled-teal` | `#41788D` | Enrolled rows in List view; calendar/finals course blocks (D-p15, D-p16, R-p9) |
| `--waitlist-cyan` | `#CEEBEE` (≈`#D1F5F5`) | Waitlisted rows in List view (D-p15, R-p10) |
| `--title-orange` | `#CB6C12` (≈`#C86E16`) | "Course Enrollment" page title, active-tab label text, "WebReg Enrollment"/"Class Pre-Planner" titles (D-p3, T-p14) |
| `--link-blue` | `#1B65A6`-ish bold links ("Appointment time", "Advanced Search", Catalog/Resources/Evaluations) | D-p3, D-p8. (Not pixel-sampled — small anti-aliased text; standard TritonLink link blue.) |
| `--btn-gray` | `#EFEFEF` → `#E2E2E2` vertical gradient, 1px `#AAA` border, ~3px radius | Every button: Search, Plan, Enroll, Drop, Change, Close, Confirm, Cancel (D-p8, D-p10) |
| `--success-green` | border `#7BB661`-ish, check icon green, bg white/very pale green | "Request Successful" box (D-p10, D-p19, R-p12) |
| `--error-pink` | bg `#F9EBEB`-ish, border + text red `#C00` | Conflict banner, drop warning box (D-p16, D-p18) |
| `--alert-yellow` | bg `#FEF8E3`-ish, border tan, "Alert:" label orange-brown | Corequisite/conflict alert inside confirm dialog (R-p8, R-p13) |
| Table header gray | `#E9E9E9`/`#D0D0D0` gradient, black bold text | Column-header rows (D-p12) |
| Drawer bar gray | `#E9E9E9` gradient bars, 1px `#C7C7C7` borders | Collapsed course drawers (D-p6) |

Page background: white. Footer text gray `#666`.

## 2. Typography

- Everything is small **Arial/Helvetica sans-serif**. Table cells ≈ **11px**, labels ≈ 12px bold,
  page title ≈ 20–22px bold orange. (Consistent across D/R/Y; exact px not measurable from
  screenshots — 11–12px is the safe classic-TritonLink value.)
- "UC San Diego" wordmark in header is the serif (Garamond-style) white logotype (D-p1).
- "MY TRITONLINK" is white, letter-spaced caps, ~14px, top-left of banner (D-p3).
- Links are bold blue, no underline until hover; external links carry a small "popout" icon glyph (D-p3 "Enrollment Information ↗", "View Book List ↗").

## 3. Overall page chrome (D-p2, D-p3, D-p12)

Top to bottom:
1. **Banner** (~55px): steel-blue gradient `#0D648F→#1A719C`. Left: "MY TRITONLINK". Right: white serif "UC San Diego" wordmark.
2. **Nav strip** (~28px): pale blue-gray gradient bar with 7 tabs separated by thin vertical rules: `Current Students | Advising & Grades | Classes & Enrollment | Financial Tools | Personal Tools | Student Forms | Help`. Active tab ("Current Students") sits on a white rounded bump with a thin curved swoosh over it; dark navy 11px text.
3. **Decorative shard graphic** (~70px): overlapping teal/navy/gold translucent triangles with a white Triton-statue silhouette at center, fading into white page. (Bake as one PNG strip.)
4. **Content area**, max-width ~950–1000px, white.
5. **Footer** (D-p2): thin gray rule, then left: "UC San Diego 9500 Gilman Dr. La Jolla, CA 92093 (858) 534-2230" / "Copyright ©2012 Regents of the University of California. All rights reserved." and links `Terms & Conditions | Feedback`; right: pale gray "UC San Diego" wordmark.

**Uncertainty — logout/top bar:** none of the WebReg screenshots show a logout control; the
TritonLink *portal* (T-p13) has a thin navy top bar with "You are logged in (LOG OUT)" at right.
Best-knowledge fallback: act.ucsd.edu pages showed no separate logout bar; session logout lived in
the portal. Also note students.ucsd.edu got a navy `#182B49` redesign later, but legacy
act.ucsd.edu/webreg2 kept this 2015 decorator — the 2023 frame (Y) shows the same content UI; its
header is cropped, so header persistence is inferred, not proven.

## 4. Landing screen (D-p2)

Orange bold title **"Course Enrollment"** top-left. Centered in page: bold label
`Select a term to begin:` + native select (e.g. "Fall Quarter 2015") + gray `Go` button. Nothing else.
(WebReg 1.5 equivalent, T-p14: title "WebReg Enrollment", term + level selects + `Submit`.)

## 5. Main page header row (D-p3, D-p12)

One row: orange **"Course Enrollment"** left; right-aligned: bold blue links
`Appointment time | Enrollment Information ↗` then `|` then the **term dropdown** (native select,
~220px, e.g. "Fall Quarter 2015"). Term dropdown open (D-p14) lists terms newest-first:
"Summer Session II 2015, Summer Session I 2015, Special Summer Session 2015, Summer Med School
2015, Spring Quarter 2015, Winter Quarter 2015" — selection highlighted OS-blue.

Below: plain 12px status sentence, e.g. *"You can plan your courses. Enrollment for the term begins
on May 6 and is based on your appointment times."* The 2023 frame (Y) shows the same message area:
"...begin enrolling in classes on Tuesday, November 14." with a red italic "subject to change."

**Appointment popup** (D-p4): white modal, thin gray title strip, two columns — bold "First Pass" /
"Second Pass", each with "Start date/time: Saturday, 05/09/2015 2:00 p.m. PT" and "End date/time:
…" lines; gray `Close` button bottom-right.

Far right edge of content: two large dark-gray chevron glyphs (**^** and **v**) stacked — page
scroll shortcuts (D-p3).

## 6. Search panel

### Simple (D-p3, D-p5)
Bold label **"Search for Classes:"** with blue link **"Advanced Search"** directly beneath it.
Text input ~300px with gray placeholder `(e.g., BILD, BILD 3 or computer 3 )`, then gray `Search`
button. Typing pops an autocomplete dropdown (white, 1px gray border, scrollbar) of rows like
`LTCO / Literature/Comparative` — the matched substring underlined (D-p5).

### Advanced (D-p7, D-p8)
Link toggles to **"Hide advanced search"**. Two-column form:
- Left column, right-aligned bold labels: `Subject:` (multi-select tokens — chosen subjects render as gray chips with small × prefix, e.g. "× ANTH / Anthropology"), `Course:` ("Enter one or more"), `Department:` (chips too), `Instructor:` ("Last, First"), `Title:`, `Section ID:` ("Enter one or more"). Placeholders gray.
- Right column, bold header **"Show only"**: checkbox grid — `Lower: [1-99] [87,90] [99]`, `Upper: [100-198] [195] [199]`, `Graduate: [200-297] [298] [299]`, `[300+] [400+] [500+]`; row `Days: M Tu W Th F Sa Su` checkboxes; `Start: [none v] End: [none v]` selects; `Only show sections with seats available: [ ]`.
- Centered below: `Reset` `Search` gray buttons.

## 7. Search results (D-p6, D-p8, D-p14, Y)

- Toolbar line: `Show [10 v]` + pagination: dark-teal `#0A4A65` square buttons `First` `«` `1` `2` `»` `Last` (white text; current page distinguished), then bold **"N courses found"**. Right-aligned blue link **"Hide search result"** (toggles to "Show search result", D-p12).
- Panel headed by a gray bar labeled **"Search results and action"** with a round blue collapse toggle (– / +) at far right.
- **Collapsed drawer per course**: gray gradient bar: black ▶ triangle, bold `LTEN 21`, thin divider, `Intro/Lit/Brit Isles: pre-1660 (4 units)` (D-p6).
- **Expanded drawer** (▼) reveals an inner table (D-p8, D-p14, Y), columns exactly:
  `Section Number | Section | Meeting Type | Days | Time | Building | Room | Avail Seats | Total Seats | Waitlist Count | Book | Instructor | Action`
  - A right-aligned link row above the table: `Catalog ↗ | Resources ↗ | Evaluations ↗` (plus `Prerequisites ↗` when applicable, D-p14).
  - One **Section Number** (6-digit ID, e.g. 847885) groups its component rows: LE row (TuTh 8:00a-9:20a, HSS 1128A) + DI row (TBA); seats/waitlist and Instructor cells span the group; Action cell holds `[Plan] [Enroll]` — inapplicable button disabled (grayed). Full sections show `[Plan] [Waitlist]` (D-p14).
  - **Book** column: small red book icon + popout icon (link to textbook list).
  - Instructor: `Haviland, John B. ✉` (mail icon).
  - **FINAL row**: bold `FINAL` in first column, its Days/Time (e.g. `Sa 3:00p-5:59p`), Building/Room TBA, and the exam **date** (e.g. `09/05/2015`) right-aligned in the Action column (D-p14).
  - Summer terms show a session-dates strip inside the drawer: "Summer Session II 2015: August 03 2015 - September 05 2015" (D-p14).
  - Course-note rows appear as a full-width ℹ line inside the table when present (R-p7).

## 8. My Schedule area (D-p3, D-p12, D-p15)

Above the tab strip, right-aligned: bold `My schedule:` + dropdown (`Create new, copy, rename ...`)
+ gray `Add Event` button. (2023 frame Y capitalizes "My Schedule:".)

**Tab strip**: full-width dark-teal `#0A4A65` band. Left: three rounded-top tabs `List`
`Calendar` `Finals` — active tab white bg with **orange** label; inactive tabs pale gray-blue with
navy label. Right side of band, white bold text links: `Print Schedule | View Book List ↗`
(View Book List appears once schedule is non-empty).

### 8.1 List view (D-p12, D-p15, R-p10)
Column header row (gray gradient, black bold ~11px):
`Subject Course | Title | Section Code | Type | Instructor | Grade Option | Units | Days | Time | BLDG | Room | Status / (Position) | Action`

Row rendering by state:
- **Enrolled** — medium teal `#41788D` bg, **white** text; Status "Enrolled"; Action `[Drop] [Change]`.
- **Waitlisted** — pale cyan `#CEEBEE` bg, black text; Status `Waitlist (2)` (position in parens); Action `[Drop] [Change]`.
- **Planned** — white bg, gray text; Status "Planned"; Action `[Remove] [Enroll]` (Enroll disabled until appointment) or `[Remove] [Waitlist]` if full (D-p12, D-p15).
- Each course renders 2–3 physical rows sharing the color: main LE row (all columns), DI sub-row (only Section Code/Type/Days/Time/BLDG/Room filled), and a **"Final Exam"** sub-row (Title cell says "Final Exam", Type `FI`, Days like `F 09/04/2015`, Time `7:00p-9:59p`, BLDG/Room TBA).
- Type codes: LE, DI, LA, FI, SE, ST, TU. Grade Option shows `L` or `S/U` (older 1.5 spelled "Letter"). Units `4.00`.
- Multi-line titles allowed ("Folk Music - Music of Spain", D-p15).
- Below table: voter-registration footnote line with blue link "* (U.S. Citizens/California Residents Only) Register or re-register ↗ …" (D-p15).

### 8.2 Calendar view (D-p16, R-p9)
Weekly grid, columns **Monday → Sunday**, left gutter hour labels (`12pm`, `1pm`, …) every other
gridline (30-min rows, dotted intermediate lines). Header row dark teal with white day names.
Course blocks: `#41788D` teal, thin darker border, white ~10px text, stacked lines:
1. `1:00 - 1:50` + right-aligned status chip text `Enrolled` (dark strip at block top)
2. course `LTKO 2C`
3. `LE / WLH 2110` (type / building room)
4. instructor `Lee, Jeyseon`
5. tiny `[Drop] [Change]` gray buttons inside the block.
**Conflicts**: overlapping blocks each get a 2px **red border**; a persistent banner sits above the
schedule (see §10). Waitlisted/planned blocks render pale (cream/light) versions (R-p13 shows a
conflicting pale-yellow LISP 1AX block).

### 8.3 Finals view (D-p17)
Same grid but columns are **dated, Saturday-to-Saturday**: `Sat 6/6/2015 | Mon 6/8/2015 | Tue … |
Sat 6/13/2015` (white text on dark teal, two lines: day + date). Hour gutter (11am, 12pm, …).
Final blocks teal like calendar: time strip + `Enrolled`, italic date `06/08/2015`, course
`COMM 100C`, `Location - TBA`, instructor. Conflicting finals red-bordered; same conflict banner
persists.

## 9. Dialogs (all modal over dimmed-nothing — page just overlays; white box, thin gray title strip, drop shadow)

1. **Confirm add/plan** (D-p9): heading bold ~13px "Confirm class, and/or grading option or units
   to add this class to your plan" (or "…to enroll" / "…to waitlist"). Bordered table (1px gray),
   columns: `Subject/Course | Course Title | Grading | Units | Section Code | Meeting Type | Days | Time`.
   Grading is a select (`Letter` / `Pass/No Pass`); Units editable when variable (shows `4.00`).
   Component rows (A00 LE / A01 DI) as separate lines. Bottom-right: `Cancel` `Confirm`.
   - May contain a **yellow Alert box** at top: "⚠ Alert:" + bullets, e.g. corequisite warning (R-p8), or red-text conflict warning "Warning: You have scheduling conflicts!" with affected pairs (R-p13).
2. **Request result** (D-p10, D-p19, R-p12): green-bordered rounded box, green ✓ icon, bold
   "Request Successful", detail line "Planned ANTH 20 with Letter grade option for 4.00 units,
   Section 847885." / "Dropped COMM 100C Social Formations, Section 835789." Buttons bottom-right:
   `Close` and (for real transactions) `Send Me Email Confirmation`.
3. **Drop warning** (D-p18): red/pink rounded box: bold red "⚠ You are about to drop this class.",
   then "Warning: Academic regulations permit only one 'W' per-course…" paragraphs incl. blue link
   "Enrollment and Registration Calendar", bold "You will be dropped from all components of this
   class. / Are you sure you would like to drop this class?" Below: same component table (Grading
   as plain text "Letter"; Meeting Type spelled out "Lecture"/"Discussion"). Buttons: `Cancel` `Drop`.
4. **Appointment times** (D-p4): see §5.

## 10. Conflict banner (D-p16, D-p17)

Rounded pale-pink box, red border, above the My-Schedule area and persistent across tabs:
bold red "⚠ You have scheduling conflicts!", bulleted course pairs ("COMM 100C and LTKO 2C",
"COMM 101T Final and LTKO 2C Final"), then black text: "You are responsible for resolving time
conflicts, which may also include conflicts in the midterm or final exam schedules. Special
accommodations are not guaranteed. Review your Calendar and Final Tab now."

## 11. Buttons — unified style

Small (≈20px tall) light-gray gradient `#EFEFEF→#E2E2E2`, 1px `#AAAAAA` border, ~3px rounded
corners, black 11px label, subtle inner highlight. Disabled: same shape, text `#AAA`. Seen for:
Go, Search, Reset, Plan, Enroll, Waitlist, Remove, Drop, Change, Add Event, Close, Cancel,
Confirm, Send Me Email Confirmation. Pagination buttons are the exception (dark-teal squares,
white text).

## 12. Known gaps / conflicts / fallbacks

- **Header evolution**: all full-chrome shots are 2013–2015. Whether the very last (2020–2026)
  WebReg kept the shard-graphic banner is unverified (Y crops it). Fallback: keep the D-p3 chrome;
  it is the canonical "classic WebReg" look people remember. If a modern-navy variant is wanted,
  UCSD navy is `#182B49` with gold `#FFCD00` accents (brand palette — not sampled here).
- **Logout control**: not visible in any capture (see §3).
- **Exact px sizes/fonts**: inferred (11–12px Arial) — screenshots too low-res to measure.
- **Waitlist status cell**: R-p10 hints the `Waitlist (2)` cell may carry a highlight (greenish) on
  enrolled-row context; D-p15 shows plain. Use plain text.
- **Hover states, focus rings, scrollbar chevron behavior**: never captured; use sensible ExtJS-era
  defaults (darker button gradient on hover, underline links on hover).
- **WebReg 1.5** (T-p14–20): entirely different legacy skin — gold `#FFCC00` section-header bars
  with centered black text ("WebReg for Fall Quarter 2013", "Add a Class", "My Schedule"), cream
  `#FFFFCC` highlight rows, green "Enrolled" status text, buttons `Add a New Section` /
  `List Sections` / `Find a Section`, confirm row with Letter/Pass-No-Pass radio buttons and
  `Confirm Add` / `Cancel Request`. Only relevant if the clone targets the pre-2015 look.
