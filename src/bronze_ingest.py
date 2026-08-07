"""
============================================================================
 PROJECT 5 - MOJ Criminal Court Statistics (CCSQ)   |   BRONZE layer
============================================================================
Plain-English version of what this file does (so I can explain it to anyone):

The government gave us four Excel files. On screen they look like small summary
tables. But that's just the tip - the FULL raw data is hidden inside each file
in a part Excel calls the "pivot cache". Think of it as a locked filing cabinet
inside the spreadsheet holding millions of raw rows.

This script is an HONEST PHOTOCOPIER. It opens each file, reaches into that
hidden cabinet, copies out every single raw row, and saves it as a fast, clean
file called Parquet - WITHOUT changing any number, name or label. That faithful
copy is what we call the "Bronze" layer.

Rules I'm giving myself for Bronze:
  * Do NOT rename columns, do NOT fix messy labels, do NOT do any maths.
    (All of that happens later, in the Silver step.)
  * DO stamp every row with where it came from (file, release, fingerprint,
    timestamp) so we can always prove our numbers trace back to source.

Run it with:  python3 src/bronze_ingest.py
============================================================================
"""

import zipfile                      # an .xlsx is secretly a ZIP of XML files - this opens it
import hashlib                      # to fingerprint each source file (proves it wasn't tampered with)
import datetime as dt               # to timestamp when I ran the copy
import xml.etree.ElementTree as ET  # to read the XML inside the xlsx
from pathlib import Path

import pyarrow as pa                # the engine that writes Parquet files
import pyarrow.parquet as pq

# The XML inside an xlsx tags everything with this long namespace prefix.
# I'm saving it to a short variable NS so my code stays readable.
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

# ---------------------------------------------------------------------------
# 1. WHERE THINGS LIVE
#    BRONZE_DIR = the folder with the raw Excel files (my "in" tray)
#    OUT_DIR    = where the clean Parquet copies will go (my "out" tray)
#    RELEASE    = which quarter this data is from. I stamp every row with it so
#                 that when MOJ publishes next quarter I can tell the two apart.
# ---------------------------------------------------------------------------
BRONZE_DIR = Path(__file__).resolve().parents[1] / "data" / "bronze"
OUT_DIR    = BRONZE_DIR / "parquet"
RELEASE    = "2025Q4"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 2. FRIENDLY NAMES FOR EACH FILE'S HIDDEN CABINET(S)
#    Most files hold ONE cabinet (cache). cc_open_tool holds TWO - one with the
#    age-band detail, one with the average waiting durations - so I give each a
#    clear name instead of "cache1 / cache2".
# ---------------------------------------------------------------------------
FRIENDLY = {
    ("cc_rdos_tool.xlsx",                 1): "cc_rdos",             # receipts / disposals / open volumes
    ("cc_open_tool.xlsx",                 1): "cc_open_age",         # open caseload broken down by AGE band
    ("cc_open_tool.xlsx",                 2): "cc_open_averages",    # open caseload AVERAGE durations
    ("cc_waiting_hearing_tool.xlsx",      1): "cc_waiting_hearing",  # waiting + hearing times
    ("timeliness_tool_Crown_Court.xlsx",  1): "cc_timeliness",       # end-to-end offence-to-completion
}

FILES = [
    "cc_rdos_tool.xlsx",
    "cc_open_tool.xlsx",
    "cc_waiting_hearing_tool.xlsx",
    "timeliness_tool_Crown_Court.xlsx",
]

# How many rows I hold in memory before flushing to disk. Writing in batches is
# what stops the "Killed" out-of-memory crash we hit when we tried to load a
# whole 3-million-row cabinet at once.
BATCH_ROWS = 250_000


# ===========================================================================
# HELPER A - fingerprint a file (so provenance is trustworthy)
# ===========================================================================
def sha256_of(path: Path) -> str:
    """Read the file in chunks and return its unique fingerprint (hash)."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ===========================================================================
# HELPER B - read the "recipe card" (pivotCacheDefinition)
#   It tells me: (1) the column names, and (2) for text columns, the full list
#   of allowed values. Text values in the data are stored as NUMBERS that point
#   at this list (e.g. "court #12"), so I need this card to translate them back.
# ===========================================================================
def read_definition(zf: zipfile.ZipFile, cache_no: int):
    xml = zf.read(f"xl/pivotCache/pivotCacheDefinition{cache_no}.xml")
    root = ET.fromstring(xml)

    field_names = []   # e.g. ["year", "quarter", "crown_court", "value", ...]
    shared      = []   # for each column, its lookup list (or [] if it's a number column)
    is_text     = []   # True = this column translates via the lookup list

    for cf in root.iter(f"{NS}cacheField"):
        field_names.append(cf.get("name"))
        si = cf.find(f"{NS}sharedItems")
        items = [e.get("v") for e in si] if si is not None else []
        shared.append(items)
        # A column is "text" if it has a lookup list. Otherwise it's a raw number
        # (like the actual case counts) that we keep exactly as-is.
        is_text.append(len(items) > 0)

    record_count = None
    # recordCount lives on the <pivotCacheDefinition> root element
    if root.get("recordCount"):
        record_count = int(root.get("recordCount"))
    return field_names, shared, is_text, record_count


# ===========================================================================
# HELPER C - translate ONE cell in a row into a real value
#   <x v="12"/>  -> text column, look up item #12 in the recipe card
#   <n v="8.0"/> -> a number, keep it
#   <s v="..."/> -> an inline text value, keep it
#   <m/>         -> blank / missing -> None
# ===========================================================================
def cell_to_value(cell, lookup):
    tag = cell.tag.rsplit("}", 1)[1]
    if tag == "x":                       # points at the lookup list
        return lookup[int(cell.get("v"))]
    if tag == "n":                       # a real number (a count / average)
        v = cell.get("v")
        return float(v) if v not in (None, "") else None
    if tag == "s":                       # inline text
        return cell.get("v")
    if tag == "b":                       # true/false
        return cell.get("v") in ("1", "true", "True")
    if tag in ("m", "e"):                # missing or error -> treat as blank
        return None
    return cell.get("v")                 # anything else: keep raw


# ===========================================================================
# HELPER D - build the Parquet "shape" (schema)
#   Text columns -> stored as text. Number columns -> stored as decimals.
#   Plus my five provenance columns, all prefixed with "_" so they're easy to
#   spot and never clash with a real MOJ column name.
# ===========================================================================
def build_schema(field_names, is_text):
    cols = []
    for name, txt in zip(field_names, is_text):
        cols.append((name, pa.string() if txt else pa.float64()))
    cols += [
        ("_source_file",   pa.string()),   # which Excel file this row came from
        ("_release",       pa.string()),   # which quarter (e.g. 2025Q4)
        ("_cache",         pa.string()),   # friendly cabinet name
        ("_source_sha256", pa.string()),   # the file's fingerprint
        ("_ingested_at",   pa.string()),   # when I ran this copy
    ]
    return pa.schema(cols)


# ===========================================================================
# THE MAIN JOB - photocopy one cabinet (cache) into one Parquet file
# ===========================================================================
def ingest_cache(xlsx_name, cache_no, file_hash, ingested_at):
    friendly = FRIENDLY[(xlsx_name, cache_no)]
    xlsx_path = BRONZE_DIR / xlsx_name
    out_path  = OUT_DIR / f"{friendly}.parquet"

    zf = zipfile.ZipFile(xlsx_path)
    field_names, shared, is_text, record_count = read_definition(zf, cache_no)
    schema = build_schema(field_names, is_text)

    # The provenance values are the same for every row in this cabinet, so I
    # build them once here.
    prov = {
        "_source_file":   xlsx_name,
        "_release":       RELEASE,
        "_cache":         friendly,
        "_source_sha256": file_hash,
        "_ingested_at":   ingested_at,
    }

    writer = pq.ParquetWriter(out_path, schema, compression="snappy")
    batch, written = [], 0

    def flush():
        """Turn the rows I'm holding into a table and append them to the file."""
        nonlocal batch
        if not batch:
            return
        # Re-shape my list-of-rows into column lists (what pyarrow wants).
        columns = {name: [] for name in schema.names}
        for row in batch:
            for name in schema.names:
                columns[name].append(row.get(name))
        writer.write_table(pa.table(columns, schema=schema))
        batch = []

    # STREAM the rows one at a time. iterparse reads a row, hands it to me, and
    # I call .clear() to throw it away immediately -> memory stays flat.
    with zf.open(f"xl/pivotCache/pivotCacheRecords{cache_no}.xml") as fh:
        for _event, el in ET.iterparse(fh, events=("end",)):
            if not el.tag.endswith("}r"):     # "r" = one record / one row
                continue
            cells = list(el)
            row = dict(prov)                  # start with provenance...
            for i, name in enumerate(field_names):   # ...then fill each real column
                v = cell_to_value(cells[i], shared[i])
                # Safety net for NUMBER columns: MOJ sometimes writes missing
                # values as the text "NA" (or ":") instead of leaving them blank.
                # A number column must hold numbers, so I turn anything that
                # isn't a real number into a blank (None). Bronze stays faithful -
                # a non-number was never a real count in the first place.
                if not is_text[i]:
                    try:
                        v = float(v) if v not in (None, "") else None
                    except (TypeError, ValueError):
                        v = None
                row[name] = v
            batch.append(row)
            written += 1
            if len(batch) >= BATCH_ROWS:
                flush()
            el.clear()

    flush()
    writer.close()
    zf.close()
    return {
        "cache": friendly,
        "source_file": xlsx_name,
        "rows_written": written,
        "rows_expected": record_count,
        "columns": len(field_names),
        "output": out_path.name,
        "sha256": file_hash,
    }


# ===========================================================================
# RUN EVERYTHING and write a manifest (a receipt listing what I produced)
# ===========================================================================
def main():
    ingested_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    manifest_rows = []

    for xlsx_name in FILES:
        file_hash = sha256_of(BRONZE_DIR / xlsx_name)
        # find how many cabinets this file has (1, except cc_open which has 2)
        cache_nos = [c for (f, c) in FRIENDLY if f == xlsx_name]
        for cache_no in sorted(cache_nos):
            print(f"-> photocopying {xlsx_name} (cabinet {cache_no})...", flush=True)
            info = ingest_cache(xlsx_name, cache_no, file_hash, ingested_at)
            got, exp = info["rows_written"], info["rows_expected"]
            tick = "OK" if exp is None or got == exp else "MISMATCH"
            print(f"   {info['cache']:<20} {got:>10,} rows  [{tick}] -> {info['output']}")
            manifest_rows.append(info)

    # Write the manifest as a small CSV receipt next to the Parquet files.
    man_path = OUT_DIR / "_bronze_manifest.csv"
    cols = ["cache", "source_file", "output", "rows_written", "rows_expected",
            "columns", "sha256"]
    with open(man_path, "w") as fh:
        fh.write(",".join(cols) + "\n")
        for r in manifest_rows:
            fh.write(",".join(str(r[c]) for c in cols) + "\n")
    print(f"\nManifest written -> {man_path}")
    total = sum(r["rows_written"] for r in manifest_rows)
    print(f"Bronze complete: {len(manifest_rows)} Parquet files, {total:,} total rows.")


if __name__ == "__main__":
    main()
