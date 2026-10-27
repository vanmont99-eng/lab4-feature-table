import sqlite3
from pathlib import Path

con = sqlite3.connect("data/cohort.db")

q1 = con.execute(Path("sql/q1_gene_counts.sql").read_text()).fetchall()


def compare(patient, gene):
    """Print Query 1's count next to the raw mutation rows for one patient and gene."""
    count = next(r[2] for r in q1 if r[0] == patient and r[1] == gene)
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


# A patient with 2+ mutations in one gene: should still be one row with the full count
patient, gene, _ = next(r for r in q1 if r[2] >= 2)
compare(patient, gene)

# A patient with a Silent mutation in a target gene: checks the Silent filter works
patient2, gene2 = con.execute("""
    SELECT s.patient_id, m.gene_symbol
    FROM mutations m
    JOIN samples s ON s.sample_id = m.sample_id
    WHERE m.gene_symbol IN ('TP53','KRAS','EGFR','STK11','KEAP1')
      AND m.variant_classification = 'Silent'
    LIMIT 1
""").fetchone()
print()
compare(patient2, gene2)
