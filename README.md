# Crown Court Statistics — the backlog, its age, and its timeliness

A reproducible **Bronze → Silver → Gold** data pipeline on the Ministry of Justice's
*Criminal Court Statistics Quarterly*, focused on the **Crown Court of England and Wales**.
It turns the government's interactive Excel "tools" into clean, analysis-ready tables and
the story cuts behind a Medium series on the Crown Court backlog.

Built in Python (pandas) and Parquet. Every figure in the articles is computed by this
pipeline from published MOJ data — nothing is typed by hand.

## Headline findings (release: October–December 2025)

- The Crown Court outstanding caseload reached **80,203** at the end of December 2025 — the highest on record.
- It has **more than doubled** since 2019 (38,108 → 80,203).
- The court is disposing of **more** cases than before the pandemic, yet for **11 straight quarters** more cases arrived than were resolved.
- **21,002** open cases have been waiting a year or more (27.7% of the caseload, up from 6.5% in 2019).
- **52.8%** of the oldest cases are sexual offences or violence against the person.

## The data (and an important caveat)

- **Source:** [Criminal court statistics (GOV.UK)](https://www.gov.uk/government/collections/criminal-court-statistics), quarterly releases, under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
- The published files are interactive Excel dashboards; the real record-level data lives in each file's **pivot cache** — just under **9 million raw rows** across the four Crown Court tools used here.
- **One Crown:** MOJ paused this publication in 2024 after finding historical Crown Court figures were incorrect, then re-issued a **revised** series from December 2024 under the "One Crown" project. All figures here are on that restated basis, and the pipeline re-ingests the whole back-series from each release so revisions are handled cleanly. See [`docs/MOJ_CCSQ_raw_structure_notes.md`](docs/MOJ_CCSQ_raw_structure_notes.md).

## Architecture

| Layer | What it does |
|-------|--------------|
| **Bronze** | Streams every raw row out of each Excel pivot cache into Parquet, unchanged, with provenance (source file, release, SHA-256, ingest time). |
| **Silver** | Cleans and reshapes: friendly names, split compound labels, ordered age bands, `geo_level` tags to prevent double-counting, canonical offence labels, a real `quarter_end` date. |
| **Gold** | Small, purpose-built tables — one per question — behind each chart in the series. |

**Validation:** the pipeline reconstructs MOJ's own headline figure (80,203) from the
Bronze, Silver *and* Gold layers and asserts a match to the case. If any layer drifted by
one record, the build fails.

## Repository structure

```
├── notebooks/
│   ├── 01_bronze.ipynb        # Excel pivot-cache → Parquet (faithful copy)
│   ├── 02_silver.ipynb        # clean / reshape into tidy tables
│   ├── 03_gold.ipynb          # story-ready cuts (+ CSV)
│   └── 04_visuals.ipynb       # charts + cover/social cards
├── src/                       # scripted equivalents of the notebook logic
├── data/
│   ├── bronze/  (raw .xlsx — gitignored; download from GOV.UK)
│   ├── silver/  (Parquet — regenerated)
│   └── gold/    (Parquet + CSV — the outputs)
├── articles/                  # the Medium series + embedded visuals
├── docs/                      # raw-structure notes + data dictionary
├── requirements.txt
└── README.md
```

## Reproduce it

```bash
# 1. environment (conda or venv)
pip install -r requirements.txt

# 2. get the raw data
#    Download the four Crown Court tools from the latest CCSQ release on GOV.UK
#    (cc_rdos_tool, cc_open_tool, cc_waiting_hearing_tool, timeliness_tool_Crown_Court)
#    and place them in data/bronze/

# 3. run the notebooks in order
jupyter lab      # then run 01_bronze → 02_silver → 03_gold → 04_visuals
```

Each notebook is self-checking and stops if a validation fails.

## Gold outputs

`gold_backlog_trajectory`, `gold_caseload_age` (+ `_summary`), `gold_oldest_by_offence`,
`gold_timeliness_trend`, `gold_backlog_by_court`, `gold_remand_age` (+ `_summary`),
`gold_waiting_hearing`. Column definitions in [`docs/data_dictionary.md`](docs/data_dictionary.md).

## The article series

1. **The Crown Court Is Working Harder Than Ever. The Backlog Still Hit a Record.** — the backlog and the ageing caseload. *(live)*
2. Remand: custody vs bail — who is left to age. *(in progress)*
3. The geography of the backlog. *(planned)*
4. Why the numbers moved — the One Crown data story. *(planned)*

## Licence

Code released under the MIT Licence. Source data © Crown copyright, reused under the
Open Government Licence v3.0.

---

*Yusuf Ismail — Data Engineer · [medium.com/@yusufismail_91982](https://medium.com/@yusufismail_91982)*
