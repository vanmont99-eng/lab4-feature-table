import sqlite3

con = sqlite3.connect("data/cohort.db")

tables = [r[0] for r in con.execute(
    "SELECT name FROM sqlite_master WHERE type='table'")]

for t in tables:
    n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"\n=== {t} ({n} rows) ===")
    for col in con.execute(f"PRAGMA table_info({t})"):
        print(f"  {col[1]:<25} {col[2]:<10} {'PK' if col[5] else ''}")
    for fk in con.execute(f"PRAGMA foreign_key_list({t})"):
        print(f"  FK: {fk[3]} -> {fk[2]}.{fk[4]}")
