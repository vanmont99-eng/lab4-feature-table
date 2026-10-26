import sqlite3
from pathlib import Path

con = sqlite3.connect("data/cohort.db")

q1 = con.execute(Path("sql/q1_gene_counts.sql").read_text()).fetchall()
patient, gene, count = next(r for r in q1 if r[2] >= 2)
print(f"Query 1 says {patient} has {count} protein-altering {gene} mutations\n")

rows = con.execute("""
    SELECT m.variant_classification, m.protein_change
    FROM mutations m
    JOIN samples s ON s.sample_id = m.sample_id
    WHERE s.patient_id = ? AND m.gene_symbol = ?
""", (patient, gene)).fetchall()

print(f"All {gene} mutations for {patient} in the raw table (including Silent):")
for r in rows:
    print("  ", r)
patient2, gene2 = con.execute("""
    SELECT s.patient_id, m.gene_symbol
    FROM mutations m
    JOIN samples s ON s.sample_id = m.sample_id
    WHERE m.gene_symbol IN ('TP53','KRAS','EGFR','STK11','KEAP1')
      AND m.variant_classification = 'Silent'
    LIMIT 1
""").fetchone()
count2 = next(r[2] for r in q1 if r[0] == patient2 and r[1] == gene2)
print(f"\nQuery 1 says {patient2} has {count2} protein-altering {gene2} mutations\n")

rows2 = con.execute("""
    SELECT m.variant_classification, m.protein_change
    FROM mutations m
    JOIN samples s ON s.sample_id = m.sample_id
    WHERE s.patient_id = ? AND m.gene_symbol = ?
""", (patient2, gene2)).fetchall()

print(f"All {gene2} mutations for {patient2} in the raw table (including Silent):")
for r in rows2:
    print("  ", r)