# UCSD WebReg (classic, act.ucsd.edu/webreg2) — Functional Inventory

Research date: 2026-07-21. Classic WebReg ("WebReg 2.0", live ~Feb 2015 through the
Triton Student System cutover in 2026) is being retired — the live tutorial pages have
already been scrubbed ("You will use Triton Student System (TSS) to book your courses
for Fall 2026 and beyond"), so this inventory was rebuilt from primary screenshots.

**Sources (in order of authority):**
1. **UCSD Registrar "WebReg 2.0 Campus enrollment interface system" demo deck (May 2015)** —
   `academicaffairs.ucsd.edu/_files/ug-ed/uaac/WebReg2point0_Demo_050515.pdf` — full
   annotated screenshots of every screen. All quoted UI text below marked [DEMO].
2. **Revelle College "New Transfer: How to Enroll in Classes" webinar deck (2018)** —
   `revelle.ucsd.edu/_files/academics/enroll-tran.pdf` — screenshots of live Fall 2018
   WebReg. Quotes marked [REV].
3. students.ucsd.edu enrollment/waitlist guides, summersession.ucsd.edu, advising.ucsd.edu,
   math/biology dept pages, acadcalendar.com guide, universityscoop.com guide,
   `github.com/UCSD-Historical-Enrollment-Data/webweg` (API wrapper — data model).
4. Own knowledge of WebReg. Anything not screenshot-verified is tagged *(approx.)*.

Quoted strings are verbatim from screenshots unless tagged *(approx.)*.

---

## 1. Access & Term Selection screen

- Reached from TritonLink: students.ucsd.edu → sign in to MyTritonLink → **"Classes &
  Enrollment"** tab → **WebReg** (URL `act.ucsd.edu/webreg2`). Login = PID + password/SSO
  with Duo two-factor.
- Chrome: dark-blue **"MY TRITONLINK"** banner, "UC San Diego" wordmark right; nav tabs:
  `Current Students | Advising & Grades | Classes & Enrollment | Financial Tools | Personal Tools | Student Forms | Help`. [DEMO]
- Page heading (orange, bold): **"Course Enrollment"** — this heading persists on every
  WebReg screen. [DEMO]
- Center of page: label **"Select a term to begin:"** + dropdown (e.g. `Fall Quarter 2018`)
  + **"Go"** button. [DEMO][REV]
- Below (2018): small link **"New to WebReg? View the tutorial"**. [REV]
- Term dropdown lists every open term, including summer variants, e.g.:
  `Summer Session II 2015 / Summer Session I 2015 / Special Summer Session 2015 /
  Summer Med School 2015 / Spring Quarter 2015 / Winter Quarter 2015`. [DEMO]
- Term naming format: `<Season> Quarter <YYYY>` (Fall/Winter/Spring), `Summer Session I|II <YYYY>`.
  Internal term codes are like `FA24`, `WI25`, `SP25`, `S125`, `S225` (webweg wrapper).
- Footer on all pages: `UC San Diego 9500 Gilman Dr. La Jolla, CA 92093 (858) 534-2230` /
  `Copyright ©2012 Regents of the University of California. All rights reserved.` /
  links `Terms & Conditions | Feedback`. [DEMO]
- After "Go" the app loads the single-page main screen for that term. A dropdown at top
  right lets you switch terms at any time without returning here ("One click switches you
  between terms" [DEMO]).

## 2. Main screen layout (single page, everything lives here)

Top-to-bottom on one page (it is effectively a one-page app):

1. **"Course Enrollment"** heading (left) — **`Appointment time | Enrollment Information ⧉ | [term ▼]`**
   links/dropdown (right). [DEMO]
2. **Term-status banner** (plain text under heading), e.g.:
   > "You can plan your courses. Enrollment for the term begins on May 6 and is based on your appointment times." [DEMO]
   This line changes with the enrollment calendar (planning open / enrollment open /
   add-drop deadlines). Term messages appear here.
3. **Conflict banner** (red rounded box) when applicable — see §10.
4. **"Search for Classes:"** input + **"Search"** button; **"Advanced Search"** link
   beneath the label (toggles to **"Hide advanced search"**). [DEMO]
5. Search results drawer (when a search ran) — collapsible via **"Hide search result"** /
   **"Show search result"** link. [DEMO]
6. **"My schedule:"** dropdown (`Create new, copy, rename ...`) + **"Add Event"** button. [DEMO]
7. **My Schedule** tab strip: **`List | Calendar | Finals`** with right-aligned links
   **"Print Schedule | View Book List ⧉"**. [DEMO]
8. Up/down chevron scroll-bar widgets on the right edge (jump between search area and
   schedule). [DEMO]
9. Occasional footer PSA line, e.g. `* (U.S. Citizens/California Residents Only) Register
   or re-register ⧉ with the California Secretary of State to vote in local, state and
   national elections.` [DEMO]

## 3. Appointment time & Enrollment Information

- **"Appointment time"** link opens a modal listing both passes: [DEMO]
  > **First Pass**
  > Start date/time: Saturday, 05/09/2015 2:00 p.m. PT
  > End date/time: Monday, 05/11/2015 11:59 p.m. PT
  >
  > **Second Pass**
  > Start date/time: Thursday, 05/21/2015 5:20 p.m. PT
  > End date/time: Thursday, 08/20/2015 11:59 p.m. PT
  with a **"Close"** button.
- **"Enrollment Information ⧉"** opens the Registrar's enrollment/registration calendar
  in a new window (external link icon).
- Business rules tied to appointments:
  - Before your appointment: **Enroll is greyed out; Plan is active** ("Student starts to
    build their schedule by planning. Once appointments are active they can enroll.
    Enroll button activated." [DEMO]).
  - First pass: can enroll up to ~11.5 units *(approx.)*; waitlisting **not** available.
  - Second pass: remaining units up to 19.5 total enrolled+waitlisted; waitlists open
    ("Wait-lists will only be available during second pass appointments" — students.ucsd.edu).
  - After quarter starts: cap rises to 22 units.

## 4. Search — simple

- Label **"Search for Classes:"**; placeholder text: **"(e.g., BILD, BILD 3 or computer 3 )"**. [DEMO]
  Accepts: subject code (`BILD`), subject+number (`BILD 3`), or keyword+number.
- **Typeahead autocomplete** on subject codes: typing `lit` drops down
  `LTCO / Literature/Comparative`, `LTCS / Literature/Cultural Studies`,
  `LTEA / Literatures/East Asian`, `LTEN / Literatures in English`, … [DEMO]
- **"Search"** button executes; results render in the drawer below.

## 5. Search — Advanced

Clicking **"Advanced Search"** expands a form (link becomes **"Hide advanced search"**). [DEMO]
Left column (fields with placeholder text):

| Field | Placeholder / format |
|---|---|
| **Subject:** | "Select one or more" — multi-select chips, shown as removable tags like `× ANTH / Anthropology`, `× BIEB / Biol/Ecology, Behavior, & Evol` |
| **Course:** | "Enter one or more" (course numbers) |
| **Department:** | "Select one or more" — multi-select chips (department ≠ subject; e.g. dept ANTH owns subjects ANTH, ANBI, ANAR, ANSC) |
| **Instructor:** | "Last, First" |
| **Title:** | free text |
| **Section ID:** | "Enter one or more" (6-digit IDs) |

Right column:

- **"Show only"** course-number-range checkboxes:
  - `Lower:  ☐ 1-99   ☐ 87,90   ☐ 99`
  - `Upper:  ☐ 100-198   ☐ 195   ☐ 199`
  - `Graduate:  ☐ 200-297   ☐ 298   ☐ 299`
  - `☐ 300+   ☐ 400+   ☐ 500+`
  (87/90 = freshman seminars, 99/199 = special studies, 195 = instruction apprenticeship,
  298/299 = grad independent study; 300+/400+/500+ = professional/teaching credit.)
- **Days:** `☐ M ☐ Tu ☐ W ☐ Th ☐ F ☐ Sa ☐ Su`
- **Start:** `[none ▼]`  **End:** `[none ▼]` (time-of-day range dropdowns)
- **"Only show sections with seats available:"** ☐  ← the "open sections only" filter
- Buttons: **"Reset"** and **"Search"**. [DEMO]

## 6. Search results drawer

- Pagination header: **`Show [10 ▼]  First « 1 2 » Last`** + count text **"18 courses found"**
  ("11 courses found", "7 courses found", "1 course found"). [DEMO][REV]
- Grey panel titled **"Search results and action"** with a collapse toggle (round ● icon,
  right side). [DEMO]
- **One collapsed row per course**: expand arrow `▶` + course code + title + units, e.g.
  `▶ ANTH 2   Human Origins (4 units)`, `▶ LTEN 87   Freshman Seminar (1 unit)`,
  `▼ LISP 1AX   Analysis of Spanish (2.5 units)`. Clicking flips `▶`→`▼` and expands all
  sections grouped under that course. [DEMO][REV]
- Expanded course shows a sub-table with header columns: [DEMO]
  `Section Number | Section | Meeting Type | Days | Time | Building | Room | Avail Seats | Total Seats | Waitlist Count | Book | Instructor | Action`
  (2018 capture labels the first column **"Section ID"** and calls the second **"Section"** [REV].)
- Above the section rows, a right-aligned link row per course:
  **`Catalog ⧉ | Resources ⧉ | Evaluations ⧉`** — with **`| Prerequisites ⧉`** inserted
  when the course has enforced prerequisites (e.g. `Catalog ⧉ | Prerequisites ⧉ | Resources ⧉ | Evaluations ⧉`). [DEMO]
  - Catalog → UCSD General Catalog course description; Resources → bookstore/course
    resources; Evaluations → CAPE course evaluations; Prerequisites → prereq list popup.
- **Row grouping**: one row per *enrollable unit* = the lecture plus its child section.
  A single Section Number (e.g. `847885`) spans two mini-rows: `A00 LE TuTh 8:00a-9:20a HSS 1128A`
  over `A01 DI TBA TBA TBA TBA`. Seat numbers (`Avail 25 | Total 25 | Waitlist 0`) apply
  to the enrollable (DI) section. Each distinct DI/LA under the same lecture is its own
  row with its own Section Number (847885 = A00+A01, 847886 = A00+A02). [DEMO]
- **FINAL row**: after a course's sections, a row labeled **"FINAL"** with the exam
  slot: `FINAL | Sa | 3:00p-5:59p | TBA | TBA` plus date at far right `09/05/2015`. [DEMO]
- **Summer terms**: a session-dates line appears above sections, e.g.
  **"Summer Session II 2015: August 03 2015 - September 05 2015"**. [DEMO]
- **Book column**: red book icon + external-link icon → textbook info for that section. [DEMO]
- **Instructor column**: `Haviland, John B. ✉` — name in `Last, First M.` format with a
  mailto envelope icon. Multiple instructors stack. `Staff` when unassigned. [DEMO]
- **Course Note row**: blue ⓘ note above sections when the course carries one, e.g.
  > "Course Note: Students can enroll in either section of 95G for 2 or 3 units. The
  > drop-down menu on WebReg will give you the unit option. Students enrolled in the
  > MUS 95G [performance] ensembles will be charged a $10 lab fee which will be assessed
  > with registration fees." [REV]

### Action buttons per result row (when each appears)

| State | Buttons shown |
|---|---|
| Seats available, appointment not yet active (or planning period) | **`Plan`** enabled, **`Enroll`** greyed [DEMO] |
| Seats available, appointment active | **`Plan`** + **`Enroll`** both enabled [REV] |
| `Avail Seats = 0` (full) | **`Plan`** + **`Waitlist`** (Waitlist replaces Enroll) [DEMO] |
| Full + waitlisting not open (first pass) | **`Plan`** enabled, **`Waitlist`** greyed [DEMO] |
| Already on your schedule | buttons reflect state (e.g. planned row offers Enroll from the schedule instead) |

## 7. Confirm dialog (Plan / Enroll / Waitlist share one design)

Modal title varies by action — exact wordings:
- **"Confirm class, and/or grading option or units to add this class to your plan"** [DEMO]
- **"Confirm class, and/or grading option or units to enroll"** [REV]
- **"Confirm class, and/or grading option or units to waitlist"** [REV]

Contents:
- Optional yellow **Alert** box at top (see §10 for texts).
- Table: `Subject/Course | Course Title | Grading | Units | Section Code | Meeting Type | Days | Time`
  — one row per component, e.g. `ANTH 20 | Profnl Talk:AnthApproach/Lang | [Letter ▼] | 4.00 | A00 | LE | TuTh | 8:00a-9:20a` and a second row `A01 | DI | TBA | TBA`. [DEMO]
- **Grading** is a dropdown: `Letter` / `Pass/No Pass` (displays as `L` and `P/NP` in the
  schedule; graduate S/U shows as `S/U`). Some courses are fixed to one option (dropdown
  locked). Default = Letter.
- **Units** is plain text for fixed-unit courses (`4.00`, `2.50`); for variable-unit
  courses it becomes a dropdown (e.g. MUS 95G "2 or 3 units", 199s 2.0/4.0).
- Buttons bottom-right: **"Cancel"** / **"Confirm"**. [DEMO][REV]

## 8. Result dialog ("Action results window")

After Confirm, a modal shows a green success box: [DEMO]
> ✔ **Request Successful**
> Planned ANTH 20 with Letter grade option for 4.00 units, Section 847885.

Other captured message formats:
- `Dropped COMM 100C Social Formations, Section 835789.` [DEMO]
- `Dropped wait-listed class LISP 1A Spanish Conversation, Section 906613.` [REV]
- *(approx.)* `Enrolled in <COURSE> ... Section <ID>.` / `Waitlisted <COURSE> ... Section <ID>.`
  follow the same template.

Buttons: **"Close"** and **"Send Me Email Confirmation"** (sends a transaction receipt to
the student's UCSD email; advisors tell students to click it after *every* add/drop/
waitlist/grading change [REV]). Failures render a red box in the same window with the
error text (see §10).

## 9. My Schedule

Header row: **"My schedule:"** dropdown + **"Add Event"** button; tab strip
**`List | Calendar | Finals`** (active tab highlighted orange); right-aligned
**"Print Schedule | View Book List ⧉"**. [DEMO]

### 9.1 Multiple named schedules (the planner)

- Dropdown placeholder: **"Create new, copy, rename ..."** [DEMO] — manages multiple named
  planning schedules per term (create / copy / rename / delete; webweg confirms
  "Create, remove, or rename your schedules").
- Your real schedule is the default ("My Schedule"); extra schedules hold **Planned**
  sections only. Enrolled/waitlisted classes appear on every schedule; planned sections
  live on whichever schedule you planned them to.
- **"Add Event"** — create a custom non-class event block (title, days, start/end time)
  to reserve time on the weekly calendar while planning (e.g. work shifts). Events show
  on Calendar view only.

### 9.2 List view

Columns (exact header labels): [DEMO]
`Subject Course | Title | Section Code | Type | Instructor | Grade Option | Units | Days | Time | BLDG | Room | Status /(Position) | Action`

- One block of rows per class: main section row (LE) carries Title/Instructor/Grade
  Option/Units; child rows (DI/LA) show only section code, type, days/time/room; then a
  row titled **"Final Exam"** with Type `FI` and its date/time, e.g.
  `Final Exam | FI | Tu 12/12/2017 | 7:00p-9:59p | TBA | TBA`. [REV]
- Example enrolled row: `BICD 100 | Genetics | A00 | LE | Day, Christopher D | L | 4.00 | TuTh | 6:30p-7:50p | YORK | 2722 | Enrolled | [Drop][Change]`. [REV]
- **Status / (Position)** values: **`Enrolled`**, **`Waitlist (2)`** (number = your
  position on that waitlist), **`Planned`**. [DEMO]
- **Row colors**: Enrolled = dark teal/blue rows (white text); Waitlisted = light blue
  rows; Planned = white/grey rows with greyed text. [DEMO]
- **Action buttons by status**:
  - Enrolled → **`Drop`** + **`Change`**
  - Waitlisted → **`Drop`** + **`Change`** (Drop removes you from the waitlist)
  - Planned → **`Remove`** + **`Enroll`** (Enroll greyed until appointment window) —
    or **`Remove`** + **`Waitlist`** if the section is now full. [DEMO]
- Grade Option column shows the short code: `L`, `P/NP`, `S/U`. Units shown as `4.00`, `2.50`.

### 9.3 Calendar view (weekly)

- Grid: day columns **Monday … Sunday**, hour rows (`8am … 10pm`, only the occupied span
  by default; rows labeled `12pm`, `1pm`, `2pm` …). [DEMO]
- Each meeting is a **colored block** positioned by day/time containing:
  `1:00 - 1:50` + status badge (`Enrolled` in the corner), course code (`LTKO 2C`),
  `LE / WLH 2110` (type / building room), instructor (`Lee, Jeyseon`), and mini
  **`Drop`** **`Change`** buttons inside the block. [DEMO]
- Color semantics: enrolled = solid teal; waitlisted = lighter/green *(approx. hue)*;
  planned = pale/grey; **conflicting blocks get a red outline** and overlap visually. [DEMO]
- Custom events from "Add Event" appear as plain blocks.

### 9.4 Finals view

- Tab **"Finals"**: a Saturday→Saturday finals-week grid; column headers show day + date
  (`Sat 6/6/2015 | Mon 6/8/2015 | Tue 6/9/2015 | Wed 6/10/2015 | Thu 6/11/2015 | Fri 6/12/2015 | Sat 6/13/2015`),
  hour rows (`11am`, `12pm`, `1pm` …). [DEMO]
- Final blocks: `11:30 - 2:20` + `Enrolled` badge, date line (`06/08/2015`), course code
  (`COMM 100C`), `Location - TBA`, instructor. Conflicting finals outlined red. [DEMO]

### 9.5 Print / Book List

- **"Print Schedule"** — printer-friendly rendering of the current view.
- **"View Book List ⧉"** — opens the UCSD Bookstore textbook list for your enrolled
  sections in a new window (external-link icon).
- Advisors also teach "email your schedule to yourself" via the email-confirmation
  button; there is no separate email-schedule button in the 2015+ UI *(approx.)*.

## 10. Warnings, errors & messages (catalog)

### Scheduling conflicts — red banner on main page (persistent, all tabs)

> ⚠ **You have scheduling conflicts!**
> • COMM 100C and LTKO 2C
> • COMM 101T and LTKO 2C
> • COMM 101T Final and LTKO 2C Final
>
> "You are responsible for resolving time conflicts, which may also include conflicts in
> the midterm or final exam schedules. Special accommodations are not guaranteed. Review
> your Calendar and Final Tab now." [DEMO]

Note pairs are listed for class-vs-class AND final-vs-final conflicts. WebReg **allows**
the conflicting add — warning inside the confirm dialog:

> ⚠ **Warning: You have scheduling conflict!**
> • LISP 1AX and BIPN 100
> • LISP 1AX Final and BIPN 100 Final
> "This section's time conflicts with another course on your schedule. Your add request
> has processed, but you must resolve this time conflict by dropping one of these
> courses. You are responsible for resolving time conflicts, which may also include
> conflicts in the midterm or final exam schedule." [REV]

### Corequisite alert — yellow box in confirm dialog

> ⚠ **Alert:**
> • **Warning**: This course requires a corequisite in which you must also enroll. Check
>   the course listing in the General Catalog or consult with the department offering the
>   course for more information.
>   ◦ LIFR 1A [REV]

### Drop warning dialog — red box

> ⚠ **You are about to drop this class.**
> **Warning**: Academic regulations permit only one 'W' per-course.
> If this is your second attempt, WebReg will prohibit the drop.
> If this is your first attempt to drop this course, it will result in a 'W' grade on
> your transcript. If you re-enroll in this course in a future quarter, you will not be
> permitted to drop this course again with another W grade on your transcript. See the
> **Enrollment and Registration Calendar** for official deadlines.
> **You will be dropped from all components of this class.**
> **Are you sure you would like to drop this class?** [DEMO]

(The one-'W' warning appears only after the W deadline period begins; earlier drops get a
simpler are-you-sure version with the same "dropped from all components" line *(approx.)*.)
Below the warning: the same component table as §7, buttons **"Cancel"** / **"Drop"**. [DEMO]

### Other messages (wording approximate unless quoted)

- **Holds**: a hold blocks enrollment actions; WebReg surfaces it as a red error naming
  the hold and telling you to contact the office that placed it (Registrar, Student
  Business Services/Billing, college advising) *(approx. — screenshots unavailable;
  behavior confirmed by students.ucsd.edu "contact the office that placed the hold")*.
- **Prerequisites not met**: enrollment attempt fails with a red error box telling the
  student they have not met the prerequisites and to contact the department / use the
  Enrollment Authorization System (EASy) *(approx.)*. Courses with enforced prereqs show
  the **"Prerequisites ⧉"** link in results [DEMO]. Waitlisted students who lack a prereq
  are dropped from the waitlist when it processes (biology.ucsd.edu).
- **Unit limit exceeded**: attempts beyond the pass cap (11.5 first pass *(approx.)* /
  19.5 second pass / 22 after start) are refused with an over-limit error.
- **"Record in Use"**: raised when a second WebReg session (or an advisor) holds your
  enrollment record open (acadcalendar).
- **Duplicate/section rules**: "You can only wait-list for one section of a course." and
  "You can't be simultaneously enrolled and wait-listed in different sections of a
  course." (students.ucsd.edu) — violating attempts get a refusal message.
- **Session timeout**: WebReg logs you out after ~10 minutes of inactivity; nightly
  maintenance window ~4:00–4:30 a.m. Pacific makes the app unavailable (webweg).

## 11. Add / Drop / Change flows

- **Add** = §6 search → `Enroll` (or `Plan`-then-`Enroll` from My Schedule) → confirm →
  result dialog. Adding auto-enrolls **all components** (LE+DI/LA travel together as one
  Section Number).
- **Drop** = `Drop` button (List row, Calendar block) → drop warning dialog (§10) →
  **"Drop"** → `✔ Request Successful / Dropped …` + email-confirmation option. Dropping
  removes all components. Waitlisted classes drop instantly with no W implications.
- **Change** = `Change` button → same confirm dialog pre-filled, used to switch **grading
  option** (Letter ↔ P/NP) or **units** on variable-unit courses. Section swaps are done
  by enrolling in the other section (WebReg offers "enroll in another section of the same
  class" when your section is full). Grading-option change deadline: Friday of Week 4
  (quoted by Revelle deck: "The deadline to change your grading option is Friday of
  Week 4"). You can see the current choice "under 'Grading Option' from your course
  list". [REV]
- **Key deadlines** (surface as banner text / disabled buttons):
  - Enroll/add deadline ~Friday of Week 2 (waitlists close "4:30 p.m. on Thursday of the
    2nd full week of classes"; "Planned and Waitlisted courses will be automatically
    removed from schedules after week 2." [DEMO]).
  - Drop without W: Friday of Week 4. Drop with W: Friday of Week 6. Lab courses often
    have an earlier no-W drop (after 2nd meeting). [REV]

## 12. Waitlist behavior

- Appears only when `Avail Seats = 0` and only during second pass onward.
- Confirm dialog title: "…or units to **waitlist**"; result row status **`Waitlist (n)`**
  where n = position, e.g. `Waitlist (2)`, `Waitlist (17)`. [DEMO][REV]
- Position is visible at all times in the **Status /(Position)** column; "You should also
  be able to see the number you are on the waitlist." [REV]
- Automated processing: nightly, first-come-first-served, auto-enrolls you when a seat
  opens (email notification: "you will receive an email notifying that you have been
  enrolled" [REV]); runs through Thursday of Week 2, then all waitlists purge.
- Waitlisted units count toward the 19.5/22 caps. One waitlist per course; can't be
  enrolled in one section and waitlisted in another of the same course.

## 13. Formats & conventions (for pixel-faithful cloning)

| Thing | Format | Examples |
|---|---|---|
| Course code | `SUBJ NNN[X]`, subject 2–4 caps + space + number + optional letter | `CSE 100`, `BILD 3`, `LISP 1A`, `LTEN 87`, `ANTH 196A`, `MUS 95G` |
| Section ID / Section Number | 6-digit number, unique per term | `847885`, `906613`, `835789`, `843065` |
| Section Code | letter + 2 digits; `A00`=lecture, `A01,A02…`=its sections, `B00`=2nd lecture | `A00`, `A01`, `A06`, `B00` |
| Meeting Type codes | 2-letter codes in Type column | `LE` lecture, `DI` discussion, `LA` lab, `SE` seminar, `ST` studio, `TU` tutorial, `PR` practicum, `IN` independent st., `FW` fieldwork, `FI` final exam, `MI` midterm, `RE` review, `PB` problem session |
| Meeting Type long names | spelled out in drop dialog table | `Lecture`, `Discussion` [DEMO] |
| Days string | concatenated caps, no separators | `MWF`, `TuTh`, `MTuWTh`, `W`, `F`, `Sa`, `Su` |
| Time range | `h:mma-h:mmp` lowercase a/p, no space, en dash-less hyphen | `9:30a-10:50a`, `6:30p-7:50p`, `12:30p-1:50p`, `3:00p-5:59p` |
| Final-exam datetime | day + `MM/DD/YYYY` + time range | `Tu 12/12/2017 7:00p-9:59p`, `F 12/15/2017 11:30a-2:29p` |
| Finals column header | `Ddd M/D/YYYY` | `Mon 6/8/2015` |
| Appointment datetime | `Dayname, MM/DD/YYYY h:mm a.m./p.m. PT` | `Saturday, 05/09/2015 2:00 p.m. PT` |
| Units | 2-decimal | `4.00`, `2.50`, `1.00` |
| Units in course title line | parenthesized | `Human Origins (4 units)`, `Freshman Seminar (1 unit)`, `(2.5 units)`, `(2-3 units)` |
| Grade option codes | `L`, `P/NP`, `S/U` | column "Grade Option" |
| Instructor | `Last, First Middle` + ✉ | `Day, Christopher D`, `Haviland, John B.`, `Staff` |
| Building codes | 3–5 caps | `YORK`, `WLH`, `HSS`, `CENTR`, `PETER`, `GH`, `MCC`, `OTRSN`, `TBA` |
| Room | number or alphanumeric | `2722`, `2113`, `1S113`, `TBA` |
| Placeholder | `TBA` everywhere a value is unknown | days/time/bldg/room |

## 14. Quirks worth replicating (or consciously skipping)

- **Everything is one page**: search, results, and schedule stack vertically; the chevron
  widgets exist purely to hop between the two halves. Search results push the schedule
  down, not to another route.
- **Planned/Waitlisted auto-purge**: "Planned and Waitlisted courses will be
  automatically removed from schedules after week 2." [DEMO]
- **Teaching-schedule quirk**: students who are also TAs/instructors see the sections
  they *teach* mixed into My Schedule for that term (status distinct from Enrolled; no
  grade option), and sections where they're the listed instructor can't be self-enrolled
  *(approx. — widely reported by grad students)*.
- **Co-scheduled/cross-listed courses** share a room/time under different subjects; each
  listing has its own Section ID and seat pool.
- **Seat counts are live**, but waitlist auto-enroll is a nightly batch — so `Avail Seats
  > 0` with `Waitlist Count > 0` is a real, common state (open seats are owed to the
  waitlist; Enroll still appears but the request may be refused *(approx.)*).
- **Pre-Authorization (EASy)** overrides prereq/department restrictions; WebReg honors
  authorizations when you retry the add.
- **Session fragility**: 10-minute idle logout; ~4:15 a.m. maintenance; "Record in Use"
  when two sessions collide.
- **Mobile**: a separate stripped mobile UI existed at `mobile.ucsd.edu` ("Select Term:
  Fall - 2013"). [DEMO]

---

# Planner adaptation

Our rebuild is a **class-planning app**: same UI, zero real registrar consequences.
"Enrolling" is a simulation state on a local schedule.

## Keep verbatim (pixel/behavior clone)

- Term-selection screen: "Select a term to begin:" + Go; term dropdown naming.
- Main-page layout & chrome: "Course Enrollment" heading, term switcher, status banner,
  chevrons, footer.
- Simple search w/ subject typeahead + placeholder "(e.g., BILD, BILD 3 or computer 3 )".
- Advanced Search: all fields incl. "Only show sections with seats available", Days,
  Start/End, number-range checkboxes, Reset/Search.
- Results drawer: pagination header, "N courses found", "Search results and action"
  panel, ▶/▼ course rows with "(4 units)" suffix, full column set, Catalog/Prerequisites/
  Resources/Evaluations links (point at catalog.ucsd.edu, CAPE/SET, bookstore), FINAL
  rows, Course Note rows, seat/waitlist counts (from scraped or snapshot data).
- Confirm dialog: exact titles, component table, Grading dropdown (Letter/P-NP),
  variable-unit dropdown, Cancel/Confirm.
- "✔ Request Successful" result dialog incl. message templates and Close button.
- My Schedule: named-schedule dropdown ("Create new, copy, rename ..."), Add Event,
  List/Calendar/Finals tabs, exact list columns incl. "Status /(Position)", colored
  calendar blocks with in-block Drop/Change, red-outlined conflicts, Sat→Sat finals
  grid, Print Schedule.
- Conflict system: allow-but-warn adds, red "You have scheduling conflicts!" banner with
  class and Final pairs, exact wording.
- All formats in §13 (TuTh 9:30a-10:50a, 6-digit section IDs, A00/A01, LE/DI/LA/FI…).

## Reinterpret for planning-only

| WebReg concept | Planner meaning |
|---|---|
| **Enroll** button + confirm | Adds section to the active schedule with status **`Enrolled`** (planned-enrolled). No appointment gating — always active; optionally simulate appointment times as a toggle for realism. |
| **Waitlist** button | Adds with status **`Waitlist (n)`**, n = real current waitlist count + 1 (or user-set) — a "planned waitlist" so students can see position math. Shown on full sections only, like the original. |
| **Plan** button | Unchanged concept: adds greyed `Planned` row to the selected named schedule — our "shortlist" tier below Enrolled. |
| Drop / Remove | Instant removal; keep the drop dialog styling but swap the W-grade warning for a soft one (or show the real W deadline as info — it's genuinely useful when planning). |
| Change | Edits grading option / units / swaps section locally. |
| Seat & waitlist counts | Read-only real data (snapshot or scraper); drive the Enroll↔Waitlist button swap exactly as WebReg does. |
| Appointment time link | Shows the user's real pass times (manually entered) so they can rehearse; purely informational. |
| Term banner | Repurpose to show real enrollment-calendar deadlines for the selected term (passes open, Week-2 add, Week-4/6 drops). |
| Send Me Email Confirmation | Optional: export/share the transaction or schedule (email/ICS) — or drop in v1. |
| Print Schedule / View Book List | Print = print stylesheet; Book List = link out to bookstore. |
| Multiple schedules | Core feature — this IS the planner; keep create/copy/rename/delete. |
| Conflict warnings | Keep fully — the most valuable planning signal (incl. finals conflicts). |
| Unit caps | Show running unit total; warn (don't block) past 19.5/22. |
| Prerequisite data | Show the Prerequisites link/popup as info; optional soft warning, never a block. |

## Drop entirely

- Real authentication/SSO, PID/Duo — replace with local profiles.
- Real registrar writes of any kind (no actual enrollment ever).
- Holds, billing/fees ($10 lab-fee notes stay as informational Course Notes text),
  registration-fee deadlines.
- EASy pre-authorization flow, "Record in Use" locking, 10-min idle logout,
  4 a.m. maintenance window.
- W-grade transcript enforcement ("only one 'W' per-course" logic).
- Nightly waitlist auto-enroll batch (we don't move anyone; position is static/simulated).
- Teaching-schedule TA quirk, mobile.ucsd.edu variant, voter-registration footer PSA.
