import sqlite3

con = sqlite3.connect("data/cohort.db")


def q(label, sql):
    print(f"\n--- {label} ---")
    for row in con.execute(sql):
        print(" ", row)


q("samples with zero mutations: their TMB and clinical info", """
    SELECT s.patient_id, s.tmb_nonsynonymous, p.sex, p.age_at_diagnosis, p.stage
    FROM samples s
    JOIN patients p ON p.patient_id = s.patient_id
    LEFT JOIN mutations m ON m.sample_id = s.sample_id
    WHERE m.mutation_id IS NULL""")

q("patients missing sex, age, AND stage", """
    SELECT COUNT(*) FROM patients
    WHERE sex IS NULL AND age_at_diagnosis IS NULL AND stage IS NULL""")

q("patients missing at least one of sex, age, stage", """
    SELECT COUNT(*) FROM patients
    WHERE sex IS NULL OR age_at_diagnosis IS NULL OR stage IS NULL""")