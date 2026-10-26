"""Build a one-row-per-patient feature table from data/cohort.db.

Run from the repo root:
    python scripts/build_feature_table.py

Writes output/feature_table.tsv
"""
import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = "data/cohort.db"
OUT_PATH = Path("output/feature_table.tsv")
GENES = ["TP53", "KRAS", "EGFR", "STK11", "KEAP1"]

con = sqlite3.connect(DB_PATH)

n_patients = con.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
print(f"patients in the patients table: {n_patients}")

# Step 1: clinical + sample features, one row per patient (SQL does the join)
features = pd.read_sql_query(Path("sql/q3_patient_features.sql").read_text(), con)
print(f"after joining samples: {len(features)} rows, "
      f"{features['patient_id'].nunique()} distinct patients")
assert len(features) == n_patients
assert features["patient_id"].is_unique

# Step 2: gene counts in long format, one row per patient per gene (Query 1)
gene_long = pd.read_sql_query(Path("sql/q1_gene_counts.sql").read_text(), con)
print(f"gene counts (long): {len(gene_long)} rows "
      f"(expected {n_patients} x {len(GENES)} = {n_patients * len(GENES)})")
assert len(gene_long) == n_patients * len(GENES)

# Step 3: reshape to wide, one column per gene.
# pivot() raises an error if any patient/gene pair shows up twice,
# so this also checks the grain is one row per patient per gene.
gene_wide = gene_long.pivot(
    index="patient_id", columns="gene_symbol", values="n_protein_altering"
)
gene_wide = gene_wide[GENES].add_suffix("_count").reset_index()
gene_wide.columns.name = None
print(f"gene counts (wide): {len(gene_wide)} rows")
assert len(gene_wide) == n_patients

# Step 4: combine. validate= makes pandas error out if the merge isn't one-to-one.
table = features.merge(gene_wide, on="patient_id", how="left", validate="one_to_one")
table = table.rename(columns={"tmb_nonsynonymous": "tmb"})
print(f"final table: {len(table)} rows, {table['patient_id'].nunique()} distinct patients")
assert len(table) == n_patients
assert table["patient_id"].is_unique

# Gene counts should never be missing: no mutation means 0, not NA
count_cols = [f"{g}_count" for g in GENES]
assert table[count_cols].notna().all().all()

print("\nmissing values per column:")
print(table.isna().sum().to_string())

OUT_PATH.parent.mkdir(exist_ok=True)
table.to_csv(OUT_PATH, sep="\t", index=False, na_rep="NA")
print(f"\nwrote {OUT_PATH}")