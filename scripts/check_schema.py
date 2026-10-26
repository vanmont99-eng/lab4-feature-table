import sqlite3

con = sqlite3.connect("data/cohort.db")

def q(label, sql):
    print(f"\n--- {label} ---")
    for row in con.execute(sql):
        print(" ", row)

# patients <-> samples: is it really one-to-one?
q("distinct patients in samples", "SELECT COUNT(DISTINCT patient_id) FROM samples")
q("max samples per patient", """
    SELECT MAX(n) FROM (SELECT COUNT(*) AS n FROM samples GROUP BY patient_id)""")
q("patients with no sample", """
    SELECT COUNT(*) FROM patients p
    LEFT JOIN samples s ON s.patient_id = p.patient_id
    WHERE s.sample_id IS NULL""")

# samples <-> mutations: one-to-many, and who has zero?
q("samples with zero mutations", """
    SELECT COUNT(*) FROM samples s
    LEFT JOIN mutations m ON m.sample_id = s.sample_id
    WHERE m.mutation_id IS NULL""")
q("min / max mutations per sample (among samples that have any)", """
    SELECT MIN(n), MAX(n) FROM (SELECT COUNT(*) AS n FROM mutations GROUP BY sample_id)""")

# mutations -> genes: any orphan gene symbols?
q("mutation gene_symbols not in genes table", """
    SELECT COUNT(*) FROM mutations m
    LEFT JOIN genes g ON g.gene_symbol = m.gene_symbol
    WHERE g.gene_symbol IS NULL""")

# missing data in patients
q("missing sex / age / stage", """
    SELECT SUM(sex IS NULL), SUM(age_at_diagnosis IS NULL), SUM(stage IS NULL)
    FROM patients""")
q("sex values", "SELECT sex, COUNT(*) FROM patients GROUP BY sex")
q("stage values", "SELECT stage, COUNT(*) FROM patients GROUP BY stage ORDER BY stage")
q("missing TMB / tissue site", """
    SELECT SUM(tmb_nonsynonymous IS NULL), SUM(tissue_source_site IS NULL) FROM samples""")
q("number of distinct tissue source sites", "SELECT COUNT(DISTINCT tissue_source_site) FROM samples")

# what mutation types exist (need this to define 'protein-altering')
q("variant_classification values", """
    SELECT variant_classification, COUNT(*) FROM mutations
    GROUP BY variant_classification ORDER BY 2 DESC""")