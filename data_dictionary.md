# Data dictionary: `output/feature_table.tsv`

One row per patient (566 rows), tab separated. Missing values are written as `NA`. Built by `scripts/build_feature_table.py` from `data/cohort.db` (TCGA Lung Adenocarcinoma PanCancer Atlas, from cBioPortal).

| Column | Meaning | Type / units | Source table (column) | Missing values |
|---|---|---|---|---|
| `patient_id` | TCGA patient barcode. One row per patient. | text | `patients` (`patient_id`) | none (0) |
| `sex` | Patient sex, `female` or `male` | text | `patients` (`sex`) | `NA` for 52 patients with no clinical data |
| `age_at_diagnosis` | Age when the cancer was diagnosed | years | `patients` (`age_at_diagnosis`) | `NA` for 71 patients |
| `stage` | AJCC pathologic tumor stage: `I`, `IA`, `IB`, `II`, `IIA`, `IIB`, `IIIA`, `IIIB`, `IV`. `I` and `II` (6 patients) are kept as recorded, with no substage guessed. | text | `patients` (`stage`) | `NA` for 54 patients |
| `tissue_source_site` | Institution that submitted the tumor sample (34 sites) | text | `samples` (`tissue_source_site`) | none (0) |
| `tmb` | Tumor mutation burden: nonsynonymous mutations per megabase, across all genes. Renamed from `tmb_nonsynonymous`. | mutations per megabase | `samples` (`tmb_nonsynonymous`) | none (0) |
| `TP53_count` | Number of protein-altering mutations in TP53 | count of mutations | `mutations` (joined through `samples`) | never `NA`. `0` = no protein-altering mutation found |
| `KRAS_count` | Number of protein-altering mutations in KRAS | count of mutations | `mutations` (joined through `samples`) | never `NA`. `0` = no protein-altering mutation found |
| `EGFR_count` | Number of protein-altering mutations in EGFR | count of mutations | `mutations` (joined through `samples`) | never `NA`. `0` = no protein-altering mutation found |
| `STK11_count` | Number of protein-altering mutations in STK11 | count of mutations | `mutations` (joined through `samples`) | never `NA`. `0` = no protein-altering mutation found |
| `KEAP1_count` | Number of protein-altering mutations in KEAP1 | count of mutations | `mutations` (joined through `samples`) | never `NA`. `0` = no protein-altering mutation found |

## What the gene count columns count

**Counted** (`variant_classification` in `mutations`): `Missense_Mutation`, `Nonsense_Mutation`, `Splice_Site`, `Frame_Shift_Del`, `Frame_Shift_Ins`, `In_Frame_Del`, `In_Frame_Ins`, `Translation_Start_Site`, `Nonstop_Mutation`

**Excluded:** `Silent` (changes the DNA but not the protein)

The course's `cohort.db` was already filtered to mutations in coding sequence or at splice sites, so UTR, intron, flank, RNA, and splice-region mutations were never in the database to begin with (see the course repo's `SOURCE.md`).

If a patient has two protein-altering mutations in the same gene, the count is 2. The 4 patients with no mutation rows at all have 0 in every gene column, because their TMB is recorded as 0.0 (see Task 4 in `README.md`).