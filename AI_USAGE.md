# AI Usage
I used the Claude Model (opus 5.5)

## Task 1 :
"walk me through step by step how to complete lab 4 one step at a time from the beggining" with the link to the course repo to get a good start where I should begin because there was a lot of information thrown at me at once 
What it gave me: a bash block to make the folders, download cohort.db with curl, and create .gitignore, environment.yml, and placeholder files. Also wrote scripts/inspect_schema.py and scripts/check_schema.py.

Error: the setup block failed in my terminal with:

zsh: command not found: #
zsh: unknown file attribute: h
zsh: not enough directory stack entries.

I read through the commands before asking and figured it was a Mac zsh problem with the # comment lines, since zsh doesn't treat # as a comment when you paste into the terminal by default. I pasted the error to Claude to double check. It agreed and gave a version without comments plus setopt interactivecomments. The curl download had already worked (the output showed 15.0M). I made inspect_schema.py in the VS Code editor instead of through the terminal.

I checked the script and found that it used /usr/bin/python3 isntead of my conda Python as well. I checked it copmapring the row counts with the output and they all matched. The four samples with no mutations and the missing counts were all correct.

## Task 2 

**What it gave me:** Claude wrote both queries (`sql/q1_gene_counts.sql`, `sql/q2_site_stage.sql`), a runner script that prints expected vs actual row counts (`scripts/run_queries.py`), and `scripts/hand_check.py`. I didn't change the code. I went through each query to make sure it did what the lab asked before running it.
 
**Error:** the first time I ran `python scripts/run_queries.py` both queries came back with 0 rows, but the direct count from the `mutations` table worked (746):
 
- `actual rows:   0`
- `sum of counts in query 1: 0`
I didn't realize what was wrong. Claude pointed out that 0 rows with no error meant the `.sql` files were empty, because I had made them in VS Code but never saved them. I saved them, checked with `wc -c sql/*.sql`, and turned on Auto Save. Second run gave 2,830 rows for Query 1 and 142 for Query 2.
 
**ON vs WHERE:** I had Claude explain again why the gene and `Silent` filters go in the `ON` clause of the LEFT JOIN. In `WHERE`, patients with no matching mutation have NULLs in the mutation columns, fail the filter, and get dropped, so they'd vanish instead of showing up with a count of 0.
 
**How I checked it:**
- Query 1 had 2,830 rows (566 x 5) and 566 distinct patients. The counts added up to 746, same as counting those mutations directly from `mutations`.
- Query 2 added up to 566 patients, and the 54 in the missing-stage groups matched the 54 patients with no stage.
- Hand checked two patients with `scripts/hand_check.py`. TCGA-05-4382 has 2 Missense EGFR mutations and Query 1 says 2. TCGA-17-Z023 has one Nonsense and one Silent TP53 mutation and Query 1 says 1.
- **Off-target:** my first hand check (TCGA-05-4382) had no Silent mutations, so it didn't actually test the `Silent` filter. Claude pointed that out and I added the second patient to cover it.


## Task 3: Feature table
 
**Environment error:** before starting Task 3 I checked for pandas with `python -c "import pandas; print(pandas.__version__)"` and got:
 
- `ModuleNotFoundError: No module named 'pandas'` 

I already figured stuff would be missing from my `base` conda environment because I had cleared out a lot of storage on my laptop. Instead of installing pandas into `base`, Claude suggested building the environment from my `environment.yml` (`conda env create -f environment.yml`, then `conda activate lab4`) so I'd be testing the same setup a grader would use. I also switched VS Code's interpreter to `lab4` instead of the `base` 
 
**What it gave me:** Claude wrote `sql/q3_patient_features.sql` and `scripts/build_feature_table.py`, and tested the script on its own copy of the database before giving it to me. I went through the script and asked Claude questions about what I did not understand, and used my knowledge to check to see if it was actually doing what I wanted it to do. I understood the main choices: using `pivot()` instead of `pivot_table()` so duplicates cause an error instead of getting added together, and `validate="one_to_one"` on the merge. I didn't use the git commands Claude gave me. I did my own commits and pushes with my own commit messages.
 
**How I checked it:** the script prints the row count at every step and uses `assert` so it stops if anything is off. Every step had 566 rows and 566 distinct patients, the long gene counts had 2,830 rows, and the missing counts in the final table (52 sex, 71 age, 54 stage) matched what `check_schema.py` found in Task 1. Opened `output/feature_table.tsv` and checked it had 567 lines (566 patients plus the header).

## Task 4: Missing data
 
**What it gave me:** Claude wrote `scripts/check_missing.py` to look at the 4 patients with no mutations and how the missing sex, age, and stage overlap. I looked at this script the same way I did in task 3, asking any questions where I had confusion what the commands did. 
 
**The 0 vs NA decision:** Claude flagged that the 4 patients with no mutation rows could mean either "sequenced, nothing found" (0) or "sequencing failed" (NA), and suggested checking their TMB. All 4 had a recorded TMB of 0.0, not NULL, so I decided with using 0 for their gene counts instead of using NA.
 
**How I checked it:** the overlap numbers add up. 52 patients are missing all three fields, which is every patient missing sex. 71 - 52 = 19 more missing only age, 54 - 52 = 2 more missing only stage, and 52 + 19 + 2 = 73, which matches the count of patients missing at least one.

## Task 5: Data dictionary
 
**What it gave me:** Claude wrote `data_dictionary.md`. It took the stage definition (AJCC pathologic stage) and the note that the database only has coding and splice-site mutations from the course repo's `generate_data.py` and `SOURCE.md`. I didn't change anything, but I did review it and made sure I understood what was being written and why I needed this data dictionary.
 
**How I checked it:** compared the 11 rows in the dictionary against the header of the TSV (`head -1 output/feature_table.tsv`). Same 11 columns, none missing, no extras.

## Other:
**AI USAGE** given the extensive discussion on AI Usage in class, I wanted to make sure I wasn't missing anything so I figured AI would know the most about what exactly it id for me so after writing this I just ran it through to identify anything not disclosed, and it pointed out a lot of things that I simply was me asking AI to explain things to me like specific commands that I did not know what they did.
 
