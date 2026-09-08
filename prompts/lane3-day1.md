GHOST PROJECT - LANE 3 (TESTBED) - DAY 1 KICKOFF

Read SPEC.md section 2. You are lane 3, the testbed lane. Sonnet-led implementation lane; spawn subagents freely for loaders and plumbing. No generation of machine text today.

Tasks:
1. Pull HC3 (Hello-SimpleAI/HC3) from Hugging Face into lane3-testbed/data/hc3/. Verify actual record counts against the paper (about 24k questions with paired human-expert and ChatGPT answers across open QA, Reddit ELI5, medicine, finance; per-source breakdown) and record the exact license from the dataset card.
2. Locate the Pennebaker-King stream-of-consciousness essays dataset (2,479 essays with BFI trait scores, about 1.9M words). Try the IEEE DataPort mirror at https://doi.org/10.21227/dyfp-7f45 and the widely mirrored essays.csv. Verify what is actually downloadable from this machine without a login and save what you can into lane3-testbed/data/essays/.
3. Write loaders in lane3-testbed/loaders/ for both datasets, run them, and write lane3-testbed/TESTBED-REPORT.md with verified counts, schemas, license notes, and exact download URLs used.

If a source needs a browser login or blocks scripted access, stop at that source, document exactly what blocked it in TESTBED-REPORT.md, and continue with the rest. When the report exists, end your turn with DONE-LANE3-DAY1 and a one-paragraph summary.
