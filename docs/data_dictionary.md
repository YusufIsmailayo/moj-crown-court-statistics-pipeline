# Data dictionary — Gold layer

All Gold tables are national (England & Wales) unless a geography column is present, cover
2016–2025 quarterly on the One Crown restated basis, and are written as both Parquet and
CSV in `data/gold/`. For raw structure and data-quality detail see
[`MOJ_CCSQ_raw_structure_notes.md`](MOJ_CCSQ_raw_structure_notes.md).

Shared columns: `quarter_end` (quarter-end date, e.g. 2025-12-31), `year` (int), `quarter` (Q1–Q4).

### gold_backlog_trajectory
One row per quarter. `receipts`, `disposals`, `open` (all national, all offences, all case
types), and `net_flow` = `receipts − disposals` (positive means the backlog grew).

### gold_caseload_age
One row per quarter × age band. `age_band` (ordered: Under 4 weeks … 2 years or more),
`age_order` (1–9), `count`.

### gold_caseload_age_summary
One row per quarter. `total_cases` (all open cases), `valid_cases` (cases with a computable
age = sum of the nine bands), `open_1yr_plus` (1–2 years + 2 years or more), `share_1yr_plus`
(of valid cases).

### gold_oldest_by_offence
One row per quarter × offence, cases open a year or more. `offence` (canonical, component
groups only — `All offences` and rape sub-splits excluded), `open_1yr_plus`, `share_of_quarter`.

### gold_timeliness_trend
One row per quarter (national, all cases closed, all offences). End-to-end timeliness in
days: `offence_to_completion_mean` / `_median`, `charge_to_completion_at_the_crown_court_mean` / `_median`.
Counts are **defendants** in completed cases (timeliness is not measurable for open cases).

### gold_backlog_by_court
One row per Crown Court centre (the only file with court-level detail). `region`, `court`,
`open_latest`, `open_year_ago`, `change`, `pct_change` (latest quarter vs the same quarter a year earlier).

### gold_remand_age (+ _summary)
Open trial cases by remand status. `remand_status` (Custody / Bail / Unknown), by `age_band`;
summary adds `open_valid`, `open_1yr_plus`, `share_1yr_plus`. Note: bail cases age more than
custody cases (custody time limits push those up the list).

### gold_waiting_hearing
One row per quarter. `waiting_mean_weeks`, `waiting_median_weeks`, `hearing_mean_hours`,
`hearing_median_hours`. **Units differ by design** — waiting time is in weeks, hearing time in hours.

---

## Silver layer — key conventions

- **`geo_level`** tags each row `national` / `country` / `region` / `lja` / `unknown`. Filter to ONE level; never sum across (national = regions + an `Unknown` bucket).
- **Two offence keys, canonicalised.** Backlog/caseload files pick the *most serious* offence; timeliness picks the offence with the *longest duration*. Labels are normalised (`Not known` vs `Unknown`, rape sub-split casing) but the two semantics are kept distinct — do not join them as identical.
- **Total vs Valid** open cases are preserved separately (80,203 total vs 75,799 valid at Dec 2025).
- **Annual / `All` aggregate rows are dropped** from the waiting/hearing and timeliness tables to prevent double-counting.
- **Counting units vary:** caseload counts *cases*; timeliness counts *defendants*.
