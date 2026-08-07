# Project 5 — MOJ Criminal Court Statistics Quarterly (CCSQ)

## Raw structure & data-trap notes (pre-pipeline)

**Scope:** Crown Court backlog, case timeliness, age of the open caseload — England & Wales.
**Source collection:** https://www.gov.uk/government/collections/criminal-court-statistics
**Reference release used for this scoping:** Q4 2025 (October–December 2025), published 26 March 2026.
**Status:** documentation only — no pipeline code written yet. Items marked *(verify in file)* need confirmation by opening the actual workbook before Bronze ingestion.

---

## 1. Publication cadence & what "latest" means

- **Quarterly.** Each release covers a calendar quarter and is published ~3 months after quarter-end.
- Publication schedule seen in the collection: Q4 2025 → 26 Mar 2026; Q3 2025 → 18 Dec 2025; Q2 2025 → 30 Sep 2025; Q1 2025 → 26 Jun 2025; Q4 2024 → 27 Mar 2025; Q3 2024 → 12 Dec 2024. **Next release: 25 June 2026 (Q1 2026).**
- **Accreditation:** "Accredited official statistics" (formerly National Statistics).
- **The gap in the timeline is the story hook:** there is no "September 2024" or "Q3 2024 on the old basis" continuous with earlier data. Publication resumed 12 Dec 2024 (the Q3 2024 release) *on a revised basis*. Anything before that is not directly comparable to anything after — see §5.

---

## 2. The files in a release (Q4 2025 inventory)

Every quarterly release ships the same set. Formats: one summary ODS, a set of interactive Excel "tools" (these are the real granular data), and a transparency ZIP of flat files.

| # | File | Size | What it holds | Relevant to us? |
|---|------|------|---------------|-----------------|
| — | `ccsq_accessible_publication_tables_YYYYQn.ods` | ~0.3 MB | The numbered summary tables that back the bulletin (national-level headline series). | Headline cross-check / Gold sanity checks |
| 1 | `mags_rdos_tool.xlsx` | ~0.4 MB | Magistrates' receipts, disposals, open cases | Context only |
| 2 | `trials_tool.xlsx` | ~4 MB | Trial effectiveness (cracked/ineffective/vacated), both jurisdictions | Secondary (trial ineffectiveness angle) |
| 3 | **`cc_rdos_tool.xlsx`** | ~2 MB | **Crown Court receipts, disposals & open cases** | **CORE — the backlog** |
| 4 | **`cc_open_tool.xlsx`** | ~23 MB | **Crown Court open-case duration (age of the outstanding caseload)** | **CORE — age of caseload** |
| 5 | `cc_plea_tool.xlsx` | ~9 MB | Crown Court plea (guilty/not guilty, timing of plea) | Secondary |
| 6 | **`cc_waiting_hearing_tool.xlsx`** | ~37 MB | **Crown Court average waiting time & hearing time** | **CORE — timeliness (waiting)** |
| 7 | **`timeliness_tool_Crown_Court.xlsx`** | ~33 MB | **End-to-end timeliness (T4): offence → completion** | **CORE — timeliness (E2E)** |
| 8 | `time_mags_tool.xlsx` | ~105 MB | Magistrates' timeliness (T1–T3) | Context only |
| 9 | `interpreters_tool.xlsx` | ~0.3 MB | Language interpreter/translation services | Out of scope |
| — | `transparency_files.zip` | ~180 MB | Flat/record-level transparency extracts underpinning the tools | Candidate Bronze source — *verify contents* |

**Four files carry Project 5:** `cc_rdos_tool` (backlog volumes), `cc_open_tool` (age of open caseload), `cc_waiting_hearing_tool` + `timeliness_tool_Crown_Court` (timeliness). Total ~95 MB per quarter for the core four.

**Trap — these are "tools", not tidy data.** The `.xlsx` files are interactive dashboards (dropdowns, pivot caches, hidden helper sheets, formatted headers, merged cells, footnote rows). Bronze ingestion must target the underlying data sheets, not the front dashboard tab. *(Verify sheet names/layout in file before writing the reader.)*

**Trap — filenames are stable but the media URLs are not.** Each quarter the download links sit under `assets.publishing.service.gov.uk/media/<hash>/<filename>.xlsx` where `<hash>` changes every release. The pipeline should resolve links by scraping the release page for the known filename stems (`cc_rdos_tool`, `cc_open_tool`, `cc_waiting_hearing_tool`, `timeliness_tool_Crown_Court`), not hardcode URLs.

---

## 3. Measure coding scheme (how MOJ labels series)

The bulletin/tables use a letter+number scheme. Knowing it makes the ODS tables and tool tabs legible:

- **M1–M2** — Magistrates' caseload (receipts/disposals/open). Source: Libra + Common Platform.
- **C1–C11** — Crown Court measures (receipts, disposals, open caseload, waiting/hearing times, pleas, etc.). Source: XHIBIT (legacy) + Common Platform.
- **O1–O3** — Crown Court **open caseload / open-case duration** measures. Source: XHIBIT + Common Platform.
- **T1–T3** — Magistrates' timeliness (charge/first-listing/completion stage durations). Source: Libra/Common Platform.
- **T4** — **End-to-end timeliness** (offence → final decision), the matched magistrates'+Crown measure. This is the only published offence-to-completion measure.

*(The exact C-number ↔ table mapping should be confirmed against the ODS table index when we open it.)*

---

## 4. Granularity & comparable time period

**Geography / court level.** Headline series are national (E&W). The bulletin also publishes breakdowns "by court or Local Justice Area" (per the collection page and the Open Justice site). The large "tool" workbooks (23–37 MB) are large precisely because they hold **court-centre-level** (Crown Court) and **LJA-level** (magistrates') breakdowns across the full time series. Expected granularity dimensions for the Crown Court core files:

- **Court centre** (individual Crown Court locations) *(verify exact field + coverage in file)*
- **Region** *(verify)*
- **Offence group** (principal offence — see §5 caveat)
- **Case type** (trial / sentence / appeal; triable-either-way vs indictable)
- **Age band of open case** (e.g. <3m, 3–6m, 6–12m, 12m+ — the "year or more" cut) *(verify exact bands in `cc_open_tool`)*
- **Receipt/plea/remand status** depending on the tool
- **Quarter** (time axis)

**Time coverage.** VERIFIED: all four core tools carry a quarterly back-series **2016–2025** (see §7). Subject to the comparability break below.

**Comparable period — the key ruling for this project:**
- Data published **from the 12 Dec 2024 release onward** is on the revised / One Crown basis for the Crown Court.
- **Crown Court headline series (open caseload, receipts, disposals) are reconstructed back through the series on the One Crown basis within the current release**, so *within a single recent release* the Crown Court back-series is internally consistent. Do **not** splice figures taken from a pre-Dec-2024 release with figures from a post-Dec-2024 release.
- **Practical rule:** treat each quarterly release as an authoritative *restatement of the whole back-series*. Prefer to always re-ingest the full series from the **latest** release rather than appending one quarter at a time. Keep older releases only as an audit trail of revisions, not as live data.

---

## 5. Data traps (the part that is the story, not the inconvenience)

**5.1 The 2024 pause and the magistrates' overstatement.**
HMCTS found the magistrates' open caseload was significantly overstated in the legacy Libra MIS warehouse. Bulk clean-up cut the **December 2024** published magistrates' open caseload by **~80,000 cases**, with a **further ~17,000** reduction in **March 2025**. This is a magistrates' revision, but it is why publication paused/reset and why pre- vs post-Dec-2024 magistrates' figures cannot be compared.

**5.2 The missing-offence-type revision (June 2025).**
A cohort of magistrates' cases with no recorded offence type had been excluded from criminal counts. After reference-data fixes they were reclassified into criminal, **increasing criminal receipts/disposals by ~8,500 cases per month and the open caseload by ~31,000 as at March 2025**. Overall civil+criminal volume unchanged; the split changed. Another reason magistrates' series shift between releases.

**5.3 One Crown (Crown Court definitional overhaul).**
The One Crown project reviewed *all* published Crown Court measures and re-based the caseload estimates, aligning MOJ and HMCTS to a single agreed definition sourced from a new "One Crown pipeline." Backed by an external Crown Court Data Assurance Report and two public user consultations (Dec 2024, Mar 2025). Consequence: **all Crown Court headline metrics changed basis**; trends before the restatement are only valid as restated in current releases. Expect **ongoing revisions** — MOJ explicitly warns "some series may be disrupted, with an increased likelihood of revisions to data in future."

**5.4 Removed annual measures (still "in development").**
Some annually-released series were **removed and not yet reinstated**: grounds for sending, representation status, and further detail on grounds for conviction. Do not design Gold cuts that depend on these for recent quarters.

**5.5 Legacy vs reform system split (methodological seams).**
Every measure blends **XHIBIT (legacy)** and **Common Platform (reform)**. Common Platform rolled out Sep 2020 → all criminal courts by Sep 2023, but some cases still enter legacy systems (e.g. Crown Court appeals), and some cases are "ejected" from Common Platform back to legacy (de-duplicated out of CP counts). "Combined" measures carry small, known methodological differences between the two systems. Watch for step-changes around 2020–2023 that are system-migration artefacts, not real-world change.

**5.6 Principal-offence is defined DIFFERENTLY across files — do not join naively.**
- **Crown Court receipts/disposals/open (C/O series):** principal offence = **most serious** offence (largest maximum sentence; indictable-only prioritised).
- **Timeliness (T series):** principal offence = offence with the **longest charge-to-completion duration**.
- ⇒ The same case can appear under different offence groups in the backlog file vs the timeliness file. Any Gold model that puts backlog and timeliness side-by-side by offence must state this explicitly and must not treat the offence key as identical.

**5.7 Open-caseload counting subtleties (for the "age" story).**
- Open case = a **point-in-time snapshot** (e.g. as at 31 Dec), **not** receipts-minus-disposals. Don't derive it arithmetically.
- Cases with a **live bench warrant are excluded** from the open caseload, then re-included once the warrant is executed → a case's "age" clock and its presence in the snapshot can be non-monotonic.
- **Transfers between Crown Court centres** stay one case; for timeliness the **original receipt date to any Crown Court** starts the clock (matters for court-centre-level age analysis).
- Remand status on an **open** case = latest status; on a **disposed** case = most serious ever recorded. Different definitions — don't compare open vs disposed remand directly.

**5.8 Timeliness is completed-cases only.**
T1–T4 are based on **defendants in completed cases**, looking back from completion. You **cannot** measure timeliness of the currently-open backlog from these — the age-of-open-caseload story must come from `cc_open_tool` (O-series), and the timeliness story from the T-series; they answer different questions and must not be conflated.

**5.9 Counting unit varies.**
Caseload/receipts/disposals count **cases** (unique case number, may hold multiple defendants/offences). Timeliness counts **defendants**. Trials count **trials** (at initial listing). Keep the unit explicit in every Gold table's column names.

---

## 6. Implications for the medallion design (for discussion, not yet built)

- **Bronze:** land each of the four core workbooks per quarter verbatim (plus the transparency ZIP if it proves to hold cleaner record-level data). Resolve download URLs by scraping the release page for filename stems. Capture release date + a hash so revisions are auditable.
- **Silver:** one tidy long table per measure family — `cc_open` (with age bands), `cc_rdos` (receipts/disposals/open), `cc_waiting_hearing`, `cc_timeliness_e2e`. Standardise dimensions (quarter, court centre, region, offence group, case type, age band) but **keep two distinct offence keys** (most-serious vs longest-duration) rather than forcing one.
- **Gold — candidate story cuts (matches the Project-4 "one pipeline, several articles" approach):**
  1. The 80,200 peak — national backlog trajectory and how demand outstripped disposals.
  2. Age of the open caseload — the >22,000 cases open 12m+, and the sexual-offence / violence-against-the-person share within the oldest band.
  3. Timeliness — charge-to-completion drift back to early-2024 levels; waiting time vs hearing time.
  4. Geography — court-centre-level variation in backlog and age (the map/Streamlit angle).
  5. The data-quality story itself — the pause, One Crown, and why the numbers moved (a methods piece; strong differentiator vs NHS work).
- **Revision handling:** always rebuild from the latest release's full restated series; retain prior releases as a revisions ledger, and surface "this figure was revised by X between release A and B" as a first-class feature, not a footnote.

---

## 7. VERIFIED FILE STRUCTURE (profiled from Q4 2025 workbooks)

All four "tools" have the same shape: three visible sheets — **`Contents`** (dashboard/landing), **`Pivot…`** (the interactive pivot the user drives), **`Notes`** (footnotes/definitions) — and the **real record-level data lives in the file's pivot cache** (`xl/pivotCache/pivotCacheDefinition*.xml` + `pivotCacheRecords*.xml`), not in any worksheet. That cache is where the 23–38 MB comes from, and it is the correct Bronze ingestion target. The visible pivot sheets are small (49–1,333 rows); the caches are millions of rows.

**Record counts (raw rows in the pivot cache) — this project's "raw records" figure:**

| File | Cache | Raw records | Cache fields |
|---|---|---:|---|
| `cc_rdos_tool` | 1 | **345,590** | 9 |
| `cc_open_tool` | 1 (age detail) | **3,129,789** | 7 |
| `cc_open_tool` | 2 (averages) | **395,534** | 9 |
| `cc_waiting_hearing_tool` | 1 | **4,346,919** | 11 |
| `timeliness_tool_Crown_Court` | 1 | **754,795** | 30 |
| **Total** | | **≈ 8.97M** | |

**Time coverage (all four): 2016–2025, quarterly** (year ∈ 2016…2025; quarter ∈ Q1–Q4). Corrects the earlier "~2014" guess. This is the One-Crown-restated span in the current release.

### 7.1 Exact fields per file

**`cc_rdos_tool` (backlog volumes)** — fields: `year, quarter, receipt_type, region, lcjb_area, crown_court, rdos, offence_group, value`
- `rdos` = `{1. Receipts, 2. Disposals, 3. Open}` — one file covers all three headline volume measures.
- `receipt_type` (5): Triable-either-way trials / Indictable only trials / Committed for sentence / Appeals / Unknown.
- **Geography is 3-level: `region` (8) → `lcjb_area` (45 LJAs) → `crown_court` (70 court centres).** This is the ONLY core file with individual court-centre granularity.

**`cc_open_tool` (age of open caseload)** — TWO caches:
- Cache 1 (age detail): `year, quarter, receipt_type, offence_group, geographic_area, age_open_grouped, value`
- Cache 2 (averages): same dims + `Total cases, Valid cases, Open duration (median), Open duration (mean)`
- `age_open_grouped` (9 real bands + 2 totals): `Under 4 weeks · 4–8 · 8–12 · 12–16 · 16–20 · 20–26 weeks · 6 months to under 1 year · 1 to 2 years · 2 years or more · [Total cases] · [Valid cases]`. **No single "12-month+" band — "1 year or more" = `1 to 2 years` + `2 years or more`.**
- `receipt_type` (16): includes remand splits (remanded in custody / on bail / unknown) for trials.
- `geographic_area` (54): `England and Wales, England, Wales, 8 regions, 45 LJAs, Unknown`. **LJA is the finest level — NO court-centre breakdown here.**

**`cc_waiting_hearing_tool` (waiting & hearing times)** — fields: `annual_quarterly, year, quarter, receipt_type, offence_group, region, waiting_hearing_times, measure, value, remand_status, plea`
- `waiting_hearing_times` = `{1. Waiting times, 2. Hearing times}`.
- **`measure` mixes units** — weeks (waiting), hours (hearing), counts, and mean-number-of-hearings all live in one field: `Total cases/defendants, Valid cases/defendants, Median (weeks), Mean (weeks), Median (hours), Mean (hours), Mean number of hearings`. Filter on unit deliberately.
- Extra breakdowns: `remand_status` (4), `plea` (5).
- **Geography is `region` only (10, incl. England / England and Wales) — no LJA or court centre.**
- Has `annual_quarterly` toggle (Annual vs Quarterly) and `quarter` includes an `All` member — **filter to avoid double-counting annual+quarterly.**

**`timeliness_tool_Crown_Court` (end-to-end T4)** — 30 fields. Dims: `Annual or quarterly, Year, Quarter, Geographic area, Receipt type, Offence group`; the remaining 24 are **paired Mean/Median measures** for each journey stage: Offence→charge, Charge→first listing, First listing→completion in mags, Sending→main hearing, Main hearing→completion, **Offence→completion (the E2E headline)**, Pre-court, At court, Charge→sending, Receipt at CC→completion, Charge→completion at CC.
- Counts are **defendants**, completed cases only (`Number of defendants whose cases have completed`, `…valid defendants…`).
- `Receipt type` (27): full plea × remand cross-breakdown.
- `Geographic area` (55): E&W / regions / LJAs. **LJA finest — no court centre.** Also `Annual or quarterly` toggle + `All` quarter → same double-count caveat.

### 7.2 Geography granularity — resolved (critical for the "geography" story)

| Level | cc_rdos | cc_open | cc_waiting_hearing | timeliness |
|---|:--:|:--:|:--:|:--:|
| Court centre (70) | ✅ | ❌ | ❌ | ❌ |
| LJA / LCJB (~45) | ✅ | ✅ | ❌ | ✅ |
| Region (8–10) | ✅ | ✅ | ✅ | ✅ |

⇒ **Court-centre-level analysis is only possible for receipts/disposals/open volumes.** Age-of-caseload and timeliness bottom out at LJA; waiting/hearing times at region. A court-centre map can show backlog volume, but *not* court-level age or timeliness.

### 7.3 Offence-group vocabulary — resolved (and a confirmed join trap)

17–18 groups (`00: All offences` + numbered groups). Sexual offences carry sub-splits (`Adult Rape`, `Child Rape`, `All Rape`). **Labels are NOT identical across files** — e.g. `13: Not known` (rdos/open/waiting) vs `13: Unknown` (timeliness); `Adult Rape` (title case) vs `adult rape` (lower); `cc_rdos` lacks the `All Rape` roll-up. Silver must normalise these to a canonical offence key; do not join on the raw label.

### 7.4 Headline figures reproduced from the raw cache (validation)

Q4 2025 · England & Wales · `01. All open cases` · `00: All offences`, summed from `cc_open` cache 1:

- **Total cases = 80,203** → matches the published "~80,200 highest ever" **exactly.** ✅
- Valid cases (sum of the 9 age bands) = 75,799.
- Open **1 year or more** = 14,839 (1–2yr) + 6,163 (2yr+) = **21,002 valid cases = 27.7% of valid**; grossed to total cases ≈ **22,200** → this is the source of the published "over 22,000." ⚠️ **Report whether a 1yr+ figure is on a valid-case or total-case basis — the two differ by ~1,200.**

### 7.5 Remaining item (optional)

- `transparency_files.zip` (180 MB) not yet inspected — may hold flatter CSVs, but the pivot caches are already clean, well-typed and fully sufficient, so the ZIP is likely unnecessary for Bronze.

---

## 8. Confirmed implications for Bronze ingestion

- **Ingestion target = the pivot cache, not a worksheet.** Read `pivotCacheDefinition*.xml` for field names + shared-item vocabularies, then stream `pivotCacheRecords*.xml`. **Stream with `iterparse` and `.clear()`** — loading a full cache (3.1M / 4.3M rows) into a DOM will OOM. `cc_open` has two caches (age detail + averages); ingest both.
- **Filter toggles at read time:** drop `annual_quarterly = Annual` and `quarter = All` in the waiting/hearing and timeliness files unless the annual view is explicitly wanted, to prevent double counting.
- **Preserve Total vs Valid** as distinct columns everywhere (open caseload and timeliness both distinguish them).
- **Two offence keys, normalised labels:** keep most-serious (C/O) vs longest-duration (T) offence semantics separate, and canonicalise the label spellings above.
- **Provenance columns:** stamp each Bronze row with source filename, release quarter, and a file hash so the restatement/revision history is auditable.

---

*Sources: GOV.UK Criminal court statistics collection; CCSQ Oct–Dec 2025 release page and bundled "A Guide to Criminal Court Statistics"; MOJ Crown Court Data Assurance Report; One Crown consultations (Dec 2024, Mar 2025); direct profiling of the four Q4 2025 Crown Court workbooks (pivot cache definitions + records).*
