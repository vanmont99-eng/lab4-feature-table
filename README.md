# Lab 4: Database-Driven Feature Table

Builds a one-row-per-patient feature table from `cohort.db` (TCGA Lung Adenocarcinoma PanCancer Atlas from cBioPortal, 566 patients).

## How to run

From the repo root:

```bash
conda env create -f environment.yml
conda activate lab4
python scripts/get_data.py
python scripts/build_feature_table.py
```

- **Expects:** `data/cohort.db`. `get_data.py` downloads it from the course repo if it isn't there. The `data/` folder is in `.gitignore`, so the database isn't committed.
- **Outputs:** `output/feature_table.tsv`. One row per patient (566 rows), tab separated, missing values written as `NA`. Columns are described in `data_dictionary.md`.

The other scripts are the checks I ran along the way. Run them from the repo root too:

| Command | What it does |
|---|---|
| `python scripts/inspect_schema.py` | Prints every table with its columns, keys, and row count |
| `python scripts/check_schema.py` | Checks how the tables connect and counts missing values |
| `python scripts/run_queries.py` | Runs the two Task 2 queries and prints expected vs actual row counts |
| `python scripts/hand_check.py` | Compares Query 1's counts to the raw mutation rows for two patients |
| `python scripts/check_missing.py` | Looks at the patients with no mutations and how the missing values overlap |

## Repo layout

- `scripts/` : Python scripts (listed above, plus `get_data.py` and `build_feature_table.py`)
- `sql/q1_gene_counts.sql` : Task 2, Query 1 (also used to build the feature table)
- `sql/q2_site_stage.sql` : Task 2, Query 2
- `sql/q3_patient_features.sql` : clinical and sample columns for the feature table
- `output/feature_table.tsv` : the final feature table
- `data_dictionary.md` : what each column in the feature table means (Task 5)
- `environment.yml` : conda environment (Python 3.11, pandas)
- `AI_USAGE.md` : how I used AI on this lab

## Schema (Task 1)

I looked at the structure with `scripts/inspect_schema.py` and checked how the tables connect with `scripts/check_schema.py`.

### Tables

| Table | Rows | Primary key | Foreign keys | One row is... |
|---|---|---|---|---|
| `patients` | 566 | `patient_id` | none | one patient |
| `samples` | 566 | `sample_id` | `patient_id` → `patients.patient_id` | one tumor sample |
| `mutations` | 200,789 | `mutation_id` | `sample_id` → `samples.sample_id`, `gene_symbol` → `genes.gene_symbol` | one somatic mutation in one sample |
| `genes` | 17,756 | `gene_symbol` | none | one gene |

### Columns

- **patients:** `patient_id`, `sex`, `age_at_diagnosis`, `stage`, `vital_status`, `followup_months`
- **samples:** `sample_id`, `patient_id`, `tissue_source_site`, `tmb_nonsynonymous`, `aneuploidy_score`, `msi_mantis_score`
- **mutations:** `mutation_id`, `sample_id`, `gene_symbol`, `variant_classification`, `variant_type`, `protein_change`, `chromosome`, `start_pos`, `end_pos`, `t_ref_count`, `t_alt_count`
- **genes:** `gene_symbol`, `entrez_gene_id`, `chromosome`

### How the tables connect

`patients` (1) → `samples` (1) → `mutations` (0 or more) → `genes` (1)

- **patients to samples is one-to-one.** I checked this instead of assuming it from both tables having 566 rows. All 566 patients show up in `samples`, nobody has more than one sample, and nobody is missing one.
- **samples to mutations is one-to-many.** Samples that have mutations have anywhere from 1 to 2,602. 4 samples have no mutations at all, so it can also be zero.
- **mutations to genes is many-to-one.** Every `gene_symbol` in `mutations` exists in `genes` (0 that don't match). Lots of genes in `genes` never show up in `mutations` for a given sample.

### Stuff I noticed

- `variant_classification` has 10 types. `Silent` is the only one that doesn't change the protein, so it's the only one I leave out of the gene counts.
- 5 patients have stage `I` and 1 has stage `II` with no A or B. I'm leaving those as they are.
- Missing values: 52 patients have no `sex`, 71 have no `age_at_diagnosis`, and 54 have no `stage`. `tissue_source_site` and `tmb_nonsynonymous` aren't missing for anyone.

## SQL queries (Task 2)

Both queries are in `sql/`. `scripts/run_queries.py` runs them and prints the row counts and checks below.

```bash
python scripts/run_queries.py
```

### Query 1: protein-altering mutations per patient per gene (`sql/q1_gene_counts.sql`)

Counts mutations in TP53, KRAS, EGFR, STK11, and KEAP1 for every patient, leaving out `Silent`. I built a grid of every patient times every gene and LEFT JOINed `mutations` onto it, so patients with no mutation in a gene get a 0 instead of disappearing. The gene and `Silent` filters are in the `ON` clause, not `WHERE`. If they were in `WHERE`, the rows with no matching mutation would have NULLs and get filtered out. I used `COUNT(m.mutation_id)` instead of `COUNT(*)` so an empty match counts as 0, not 1.

- **Expected rows:** 566 patients x 5 genes = 2,830
- **Actual rows:** 2,830, with 566 distinct patients
- **Extra check:** the counts add up to 746, which matches counting the same mutations straight from the `mutations` table (746)

700 of the rows have a count above 0, but the total is 746. So some patients have more than one mutation in the same gene. The query groups by patient and gene, so those still end up as one row each.

### Query 2: patients per tissue source site per stage (`sql/q2_site_stage.sql`)

Groups patients by `tissue_source_site` and `stage` and counts distinct patients. Patients with no stage stay in the result as their own NULL group.

- **Expected rows:** I couldn't know the exact number ahead of time. At least 34 (one per site) and at most 340 (34 sites x 10 stage values counting NULL). The counts should add up to 566.
- **Actual rows:** 142. The counts add up to 566, and 54 patients are in the missing-stage groups, which matches the 54 patients with no stage.

It's way under 340 because most sites only sent patients from a few stages.

### Hand check

```bash
python scripts/hand_check.py
```

This picks two patients and prints their raw mutation rows next to what Query 1 says.

- **TCGA-05-4382, EGFR:** Query 1 says 2. The raw table has 2 Missense mutations (p.R222L, p.E545Q) and no Silent ones. Matches. This also shows a patient with 2 mutations in one gene still ends up as one row with a count of 2.
- **TCGA-17-Z023, TP53:** Query 1 says 1. The raw table has 2 mutations, one Nonsense (p.E198*) and one Silent (p.V197=). The Silent one got left out, so 1 is right.

I picked the second patient on purpose because the first one didn't have any Silent mutations, so it couldn't show that the `Silent` filter actually works.

## Feature table (Task 3)

SQL does the joining and Python does the reshaping.

1. `sql/q3_patient_features.sql` LEFT JOINs `samples` onto `patients` to get sex, age, stage, tissue source site, and TMB. One row per patient.
2. `sql/q1_gene_counts.sql` (same as Query 1 from Task 2) gets the gene counts in long format, one row per patient per gene.
3. pandas `pivot()` turns the gene counts wide, one column per gene. I used `pivot()` instead of `pivot_table()` because `pivot()` errors out if a patient/gene pair shows up twice, while `pivot_table()` would quietly add them together. So it doubles as a check that the grain is right before reshaping.
4. pandas merges the two on `patient_id` with `validate="one_to_one"`, which errors if either side has a duplicate patient.

The script uses `assert` at each step so it stops instead of writing a bad table. What it prints:

| Step | Rows | Distinct patients |
|---|---|---|
| `patients` table | 566 | 566 |
| after joining `samples` | 566 | 566 |
| gene counts, long | 2,830 (566 x 5) | 566 |
| gene counts, wide | 566 | 566 |
| final table | 566 | 566 |

## Missing data (Task 4)

I checked the missing values with `scripts/check_missing.py`.

### Patient count through the joins

No patient was dropped. Every step has 566 rows and 566 distinct patients (see the table in Task 3), and the script stops with an `assert` if that ever changes. I used LEFT JOINs from `patients` so a patient with no sample or no mutations would still be kept with NULLs instead of disappearing.

### How I handled each kind of gap

| Gap | How many | What I did | Coded as |
|---|---|---|---|
| Missing `sex` | 52 | Kept the patient, left it missing | `NA` |
| Missing `age_at_diagnosis` | 71 | Kept the patient, left it missing | `NA` |
| Missing `stage` | 54 | Kept the patient, left it missing | `NA` |
| Stage with no substage (`I`, `II`) | 6 | Left as recorded, didn't guess A or B | `I` / `II` |
| No mutation in a gene | most patients, for each gene | Counted as zero | `0` |
| No mutations at all | 4 | Counted as zero for every gene | `0` |

I didn't fill in (impute) any missing values. That's a choice for whoever uses the table, not something to hide in the build step.

**The missing clinical data isn't random.** All 52 patients missing `sex` are also missing `age_at_diagnosis` and `stage`, so they basically have no clinical data at all. 73 patients are missing at least one of the three. The other 21 have sex recorded but are missing age (19) or stage (2). Anyone using this table should know that dropping rows with any NA would remove 73 patients, not just a few scattered ones.

### Zero vs. missing for the gene counts

A 0 and an NA mean different things here.

- **0** means the tumor was sequenced and no protein-altering mutation was found in that gene.
- **NA** means the value wasn't recorded, so we don't know.

I used **0** for the gene count columns. Every patient has a sequenced sample, and a mutation that isn't in the `mutations` table means none was found, not that we don't know.

The 4 patients with no mutation rows at all (TCGA-64-1678, TCGA-69-8453, TCGA-78-7143, TCGA-86-A4D0) were the case I wasn't sure about, since no rows could also mean the sequencing failed. All 4 have a recorded TMB of 0.0 (not NULL), so their samples were analyzed and nothing was found. That fits 0 better than NA. I can't fully rule out that 0.0 is a default value from the pipeline, but nothing in the data points to that.

For sex, age, and stage I used **NA**, because a missing value there really does mean nobody recorded it.

## Data dictionary (Task 5)

See `data_dictionary.md`.