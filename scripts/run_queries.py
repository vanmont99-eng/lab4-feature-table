import sqlite3
from pathlib import Path

con = sqlite3.connect("data/cohort.db")


def run(path):
    sql = Path(path).read_text()
    return con.execute(sql).fetchall()


# ---------- Query 1 ----------
q1 = run("sql/q1_gene_counts.sql")
print("=== Query 1: protein-altering mutation counts per patient per gene ===")
print("expected rows: 566 patients x 5 genes = 2830")
print("actual rows:  ", len(q1))
print("distinct patients:", len({r[0] for r in q1}))
print("rows with count > 0:", sum(1 for r in q1 if r[2] > 0))
print("first 10 rows:")
for r in q1[:10]:
    print("  ", r)

# cross-check: total from the query should equal a direct count from mutations
direct = con.execute("""
    SELECT COUNT(*) FROM mutations
    WHERE gene_symbol IN ('TP53','KRAS','EGFR','STK11','KEAP1')
      AND variant_classification <> 'Silent'
""").fetchone()[0]
print("sum of counts in query 1:", sum(r[2] for r in q1))
print("direct count from mutations table:", direct)

# ---------- Query 2 ----------
q2 = run("sql/q2_site_stage.sql")
print("\n=== Query 2: patients per tissue source site per stage ===")
print("expected rows: between 34 and 340, counts summing to 566")
print("actual rows:  ", len(q2))
print("sum of n_patients:", sum(r[2] for r in q2))
print("patients in missing-stage groups:", sum(r[2] for r in q2 if r[1] is None))
print("first 10 rows:")
for r in q2[:10]:
    print("  ", r)