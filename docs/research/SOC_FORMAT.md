# UCSD Legacy Schedule of Classes — Scraping Format Reference

Researched 2026-07-21. Sources: live probing of `act.ucsd.edu` (partially successful — server
returning transient HTTP 500 "Max Sessions Exceeded" / connection hangs all afternoon), the saved
form page, and three GitHub scrapers cross-checked against a captured real results page:

- [PatrickTangwen/coursetable-ucsd](https://github.com/PatrickTangwen/coursetable-ucsd) — `tools/catalog-snapshot/scheduleOfClasses.ts` (actively maintained, 2026; most authoritative)
- [ucsdscheduleplanner/scraper](https://github.com/ucsdscheduleplanner/scraper) — Python/selenium scraper + bs4 parser
- [rantaoca/ucsd-api](https://github.com/rantaoca/ucsd-api) — contains a captured real results page (`test/course-schedule/schedules-results.html`, CSE SP15) used to verify HTML structure
- [davidk003/UCSD-scheduleofclasses-scraper-api](https://github.com/davidk003/UCSD-scheduleofclasses-scraper-api) — confirms `subject-list.json` / `department-list.json` endpoints and their JSON shape

Verification status of each claim is marked **[verified live]**, **[verified against captured page]**
(the SP15 sample, structure unchanged for a decade), or **[from reference, unverified]**.

---

## 1. Endpoints

Base: `https://act.ucsd.edu/scheduleOfClasses`

| Endpoint | Method | Purpose |
|---|---|---|
| `/scheduleOfClassesStudent.htm` | GET | Search form. Term `<select id="selectedTerm">` is inline HTML; subject `<select id="selectedSubjects">` is EMPTY in raw HTML — populated by JS from `subject-list.json`. **[verified live]** |
| `/subject-list.json?selectedTerm=XX99` | GET | JSON array of subjects for a term: `[{"code":"CSE ","value":"CSE  - Computer Sci & Engineering"}, ...]`. Codes are space-padded to 4 chars. **[verified live for shape — but see §5 SP26 gotcha]** |
| `/department-list.json?selectedTerm=XX99` | GET | Same shape, department codes (used by the "by department" tab). **[from reference, unverified]** |
| `/scheduleOfClassesStudentResult.htm` | POST | Runs the search, returns page 1 of results, binds the query to the session. |
| `/scheduleOfClassesStudentResult.htm?page=N` | GET | Page N of the *session's last search* (query is server-side session state — cookies required, no other params needed). **[verified against captured page + both scrapers]** |
| `/scheduleOfClassesFacultyResult.htm` | POST | Faculty variant, same results HTML; accepts the full form in one shot without a session (east-winds/ucsd-class-schedule-quickview uses it). **[from reference, unverified]** |

## 2. Request recipe

### 2.1 Mandatory transport details

- **User-Agent is required.** Default curl UA → connection hangs forever. Use a Chrome UA:
  `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36` **[verified live]**
- **Cookie jar across the whole flow.** GET the form page with `-c jar`, then reuse `-b jar -c jar`
  on every subsequent request. Observed cookies: `TS01111c3f` (F5/BIG-IP), `itscookie`,
  `jlinksessionidx`, `jlinkauthserver`; `JSESSIONID` is set by the results POST (not always by the
  form GET). Pagination GETs are meaningless without the cookies from the POST response. **[verified live: form GET yielded 4 cookies, no JSESSIONID]**
- **Capacity errors are the norm right now (Jul 2026).** The server frequently answers
  HTTP 500 (Tomcat 8.0.33 error page, message "Max Sessions Exceeded") or times out entirely
  (no response in 45 s). These are transient: retry with 20–60 s sleeps; `--max-time 45` per
  attempt. Roughly 1 in 5–10 attempts got through during testing. **[verified live]**

### 2.2 Search POST (page 1)

```
POST https://act.ucsd.edu/scheduleOfClassesStudentResult.htm
Content-Type: application/x-www-form-urlencoded
Cookie: (jar from form-page GET)
```

Body used by the working 2026 coursetable-ucsd scraper (subject-search tab):

```
selectedTerm=FA25
xsoc_term=
loggedIn=false
tabNum=tabs-sub
_selectedSubjects=1
selectedSubjects=CSE            <- code from subject-list.json; safest to send the padded 4-char code
_schDay=on
_hideFullSec=on
_showPopup=on
schedOption1=true   _schedOption1=on      <- 1-99
schedOption2=true   _schedOption2=on      <- 100-198
schedOption3=true   _schedOption3=on
schedOption4=true   _schedOption4=on      <- 195s
schedOption5=true   _schedOption5=on      <- 199s
schedOption7=true   _schedOption7=on
schedOption8=true   _schedOption8=on
schedOption9=true   _schedOption9=on
schedOption10=true  _schedOption10=on
schedOption11=true  _schedOption11=on     <- 87 & 90s
schedOption12=true  _schedOption12=on     <- 99s
schedOption13=true  _schedOption13=on
```

(`schedOptionN` are the course-number-range checkboxes; `_x=on` are Spring-MVC hidden companions
that must be present. Include ALL of them to get every course level.) **[from reference — coursetable-ucsd, actively working in 2026]**

Alternative tab params seen in the form (course-code tab): `tabNum=tabs-crs` with
`courseNo=101`, `sectionTypes=all`, `instructorType=begin`, `instructor=`, `titleType=contain`,
`title=`. **[verified live in form HTML; result POST unverified]**

**Failure mode observed live:** a POST that the server judges invalid (e.g. a term whose subject
list is empty — see §5) returns HTTP 200 with the *search form page* again (~45 KB, contains
`id="socFacSearch"`), not an error status. Detect success by presence of `sectxt`/`crsheader`
in the body, never by status code. **[verified live]**

### 2.3 Pagination

- Page count marker in page HTML: `Page  (1&nbsp;of&nbsp;2)` — regex
  `/page\s*\(\s*\d+\s+of\s+(\d+)\s*\)/i` after entity-decoding. Appears top and bottom of the
  results table. **[verified against captured page]**
- Also derivable from pager links containing `?page=N`.
- Fetch page 2..N with plain `GET scheduleOfClassesStudentResult.htm?page=N` sending the cookies
  returned by the POST. The search itself is stored in the server session. **[verified against captured page + 2 scrapers]**
- ucsdscheduleplanner stops paging when the returned page title contains `Apache` (error) or body
  contains `No Result Found`.

### 2.4 Working curl sequence

```sh
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
B=https://act.ucsd.edu/scheduleOfClasses
curl -A "$UA" -c jar --max-time 45 "$B/scheduleOfClassesStudent.htm" -o form.html
curl -A "$UA" -b jar -c jar --max-time 45 "$B/subject-list.json?selectedTerm=FA25" -o subjects.json
curl -A "$UA" -b jar -c jar --max-time 60 -H 'Content-Type: application/x-www-form-urlencoded' \
     --data "$BODY_FROM_2_2" "$B/scheduleOfClassesStudentResult.htm" -o p1.html
curl -A "$UA" -b jar --max-time 60 "$B/scheduleOfClassesStudentResult.htm?page=2" -o p2.html
# wrap every call in: retry on (status!=200 || body lacks expected marker), sleep 20-60s between
```

## 3. Results-page HTML structure

Everything below is **[verified against captured page]** (rantaoca/ucsd-api sample, CSE SP15) and
matches what both parsers consume. All data rows live inside `<form id="socDisplayCVO">` →
`<table class="tbrdr">`; rows are `<tr>`, parse them in document order keeping "current course"
state (section rows do not repeat the course number).

### 3.0 Page furniture

- `<h2><span class="centeralign">Computer Science &amp; Engineering (CSE  )</span></h2>` — subject
  header (one per subject; a variant without the parenthesized code also appears).
- `<span class="centeralign"><span class="bold_text">As of: 03/21/2015, 00:32:00</span></span>` —
  data snapshot timestamp.
- Column header rows use `td.ubrdr`. Logical column order (13 columns after colspan expansion):

  | idx | column |
  |---|---|
  | 0 | Restriction codes ("R") |
  | 1 | Course Number |
  | 2 | Section ID (6-digit enrollment number) |
  | 3 | Meeting Type (LE/DI/LA/FI/...) |
  | 4 | Section (code A00/B01... — or a DATE for exam rows) |
  | 5 | Days |
  | 6 | Time |
  | 7 | Building |
  | 8 | Room |
  | 9 | Instructor |
  | 10 | Seats Available |
  | 11 | Seats Limit |
  | 12 | action column (bookstore link / blank) |

  `Building & Room` renders as one header cell with `colspan=2`; expand every `colspan=N` cell
  into N logical cells before indexing (both reference parsers do this).

### 3.1 Course header rows (`td.crsheader`)

Two variants, both `<tr>` (no class on the tr; identified by `td class="crsheader"`):

**(a) Simple/department-listing variant** — 3 cells:
```html
<tr>
  <td class="crsheader"></td>                       <!-- restriction codes -->
  <td class="crsheader">101</td>                    <!-- course number -->
  <td colspan="11" class="crsheader">Design &amp; Analysis of Algorithm</td>
</tr>
```

**(b) Full variant** (repeated before each lecture family) — 4 cells:
```html
<tr>
  <td class="crsheader"></td>
  <td class="crsheader">101</td>
  <td class="crsheader" colspan="5">
    <a href="javascript:openNewWindow('http://www.ucsd.edu/catalog/courses/CSE.html#cse101')">
      <span class="boldtxt">Design &amp; Analysis of Algorithm</span></a>
    ( 4 Units)                                      <!-- units inside same cell, "( N Units)" -->
  </td>
  <td class="crsheader" colspan="6" align="right">Prerequisites | Resources | Evaluations spans</td>
</tr>
```

Parsing notes:
- cell[1] = course number (e.g. `101`, `8A`, `199`); cell[2] = title text; units via regex
  `\(\s*([\d.\s–-]+)\s*Units\)` on cell[2] text (ucsdscheduleplanner uses `(.*)\((.+)Units\)`).
- The same course header REPEATS for every lecture family (A00, B00, ...) of the same course —
  dedupe by (subject, course number).
- ucsdscheduleplanner treats `len(cells)==4` as the start-of-course marker.

### 3.2 Section rows (`tr.sectxt`)

```html
<tr class="sectxt">
  <td class="brdr"></td>                            <!-- 0 restriction -->
  <td class="brdr"></td>                            <!-- 1 course number (blank; carry from header) -->
  <td class="brdr">839503</td>                      <!-- 2 section ID; BLANK for non-enrollable rows -->
  <td class="brdr"><span id="insTyp" title="Lecture">LE</span></td>  <!-- 3 meeting type -->
  <td class="brdr">A00</td>                         <!-- 4 section code -->
  <td class="brdr">MW     </td>                     <!-- 5 days, concatenated tokens M Tu W Th F S Su, right-padded -->
  <td class="brdr">5:00p-6:20p</td>                 <!-- 6 time h:mma-h:mmp -->
  <td class="brdr">CENTR</td>                       <!-- 7 building code -->
  <td class="brdr">115  </td>                       <!-- 8 room -->
  <td class="brdr">Glick, John Edward</td>          <!-- 9 instructor ("Last, First"; may be <a> link, "Staff", or blank) -->
  <td class="brdr">24</td>                          <!-- 10 seats available (see below) -->
  <td class="brdr">146</td>                         <!-- 11 seat limit -->
  <td class="brdr">bookstore icon</td>              <!-- 12 -->
</tr>
```

- **Meeting type** is always `<span id="insTyp" title="Lecture">LE</span>` — the `title` attr gives
  the long name. Codes seen: LE lecture, DI discussion, LA lab, SE seminar, ST studio, TU tutorial,
  IN independent study, FI final, MI midterm, RE review, PB problem session. The `insTyp` span in
  logical cell 3 is the most reliable "this is a schedule row" test (coursetable-ucsd skips any
  sectxt/nonenrtxt row without it).
- **Full section:** seats-available cell contains
  `<span class="ertext">FULL<br>Waitlist(21)</span>` instead of a number; limit cell still numeric.
  With `_hideFullSec=on` NOT checked you still receive full sections.
- **Non-enrollable meeting rows** (e.g. the DI attached to a lecture, or extra meetings of the same
  section): `tr.sectxt` with cell 2 (section ID) EMPTY, and seat cells are `&nbsp;` in
  `span.ertext`. Attach them to the enclosing lecture family (family = leading letter of section
  code, A01 → A).
- **Cancelled section:** the meeting columns are replaced by one merged cell:
  `<td class="brdr" colspan="8" align="center"><span class="ertext">Cancelled</span></td>`.
  Detect via text `Cancelled` after colspan expansion.
- **TBA values:** days/time/building/room may be `TBA` (also `TBD`/`Arranged` variants per
  coursetable-ucsd's matcher `^(tba|tbd|arr|arranged|arrange)$`).
- Day tokens: `M Tu W Th F S Su` concatenated without separators (`MWF`, `TuTh`); time format
  `H:MMa-H:MMp`.

### 3.3 Exam rows (`tr.nonenrtxt` with insTyp)

Final exams / midterms are `tr.nonenrtxt` rows shaped like section rows but with a DATE in the
section-code column:

```html
<tr class="nonenrtxt">
  <td class="brdr" colspan="2"></td>                <!-- 0-1 merged -->
  <td class="brdr"></td>                            <!-- 2 no section ID -->
  <td class="brdr"><span id="insTyp" title="Final">FI</span></td>
  <td class="brdr">06/06/2015</td>                  <!-- 4 date MM/DD/YYYY -->
  <td class="brdr">S      </td>                     <!-- 5 day -->
  <td class="brdr">8:00a-10:59a</td>
  <td class="brdr">TBA</td>  <td class="brdr">TBA</td>
  <td class="brdr"></td>                            <!-- 9 instructor (blank) -->
  <td class="brdr" colspan="3">&nbsp;</td>          <!-- 10-12 merged -->
</tr>
```

Attach to the current course/family like other no-section-ID rows.

### 3.4 Course-note rows (`tr` or `td.nonenrtxt` WITHOUT insTyp)

Right under a course header there may be a free-text note row:

```html
<tr>
  <td class="nonenrtxt" colspan="2" align="right"></td>
  <td class="nonenrtxt" colspan="11">
    <span class="ertext"> CSE 101 is equivalent to MATH 188. Students are required to attend ... </span>
  </td>
</tr>
```

No `insTyp` span → not a schedule row; skip or store as course note.

### 3.5 Restriction column (cell 0)

One-letter codes (D, R, etc.) linking to
`registrar.ucsd.edu/StudentLink/rstr_codes.html`; usually empty. Other lookup pages referenced by
the header: `id_crse_codes.html` (section ID), `instr_codes.html` (meeting types),
`bldg_codes.html` (buildings), `avail_limit.html` (seats).

## 4. Terms and subjects

- **Terms** (`data/terms.json`, extracted from the live form page 2026-07-21): 20 terms from
  `SA26` (Summer Sessions (All) 2026) back to `S224`. Codes: `FA`/`WI`/`SP` + 2-digit year,
  summers `S1`/`S2`/`S3`/`SA`/`SU` + year. **No FA26** — Fall 2026 exists only in the new TSS
  system. **[verified live]**
- **Subjects** (`data/subjects.json`): 179 subjects. The live `subject-list.json` could not be
  captured for a non-empty term during the outage window (see §5), so the file is built from the
  fixture in davidk003/UCSD-scheduleofclasses-scraper-api (`tests/data/subjects.json`), which is a
  saved capture of exactly this endpoint. Shape normalized to `{code, name}` with the 4-char
  padding stripped. **[from reference capture — re-fetch live per term before scraping; the set
  varies slightly by term]**

## 5. Live-probing log & gotchas (2026-07-21, ~12:00-12:30 PT)

- Form page GET: succeeded intermittently (HTTP 200, 44.7 KB) with Chrome UA + patience.
- `subject-list.json?selectedTerm=SP26` → HTTP 200 but literally `[]` (empty array). **SP26 appears
  retired from search** (quarter ended in June); expect current+future terms (S126/S226/S326/SA26,
  and FA25 as the most recent complete quarter) to be the useful ones. An empty subject list also
  means a subject-tab POST for that term bounces back to the form.
- Results POSTs during the window: every attempt returned either HTTP 500 "Max Sessions
  Exceeded" (Tomcat error page, ~1.7 KB), a hang (>45-60 s), or HTTP 200 echoing the search form.
  See `data/samples/` — if `CSE_*_p1.html` files are present there, a later retry got through.
- Practical scraper settings: 1 request at a time, 20-60 s between retries, several-minute backoff
  after consecutive 500s; run off-peak (late night PT). The endpoint has worked for other projects
  as recently as mid-July 2026 (coursetable-ucsd's snapshot tooling), so this is capacity, not a
  block.
