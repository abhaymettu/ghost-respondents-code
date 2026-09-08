GHOST PROJECT - LANE 3 - P1' STEP 1: POOL MEASUREMENT ROUND (user GO 7:19pm)

The user approved P1' (assignment-coupling design, zero generation). The frozen 14,874 batch stays shelved; P3' is appendix-only, no gate. You are step 1 of derivations/design-pivot-memo.md section 8.2 - read that memo first, especially sections 2.1, 2.4, 2.5, 3.2, 8.2.

TASK: score every pool with the audit3 trait models and the roberta detector, extending existing scripts to SAVE PER-TEXT SCORES (the injection module needs them later). Human scores must be CROSS-FITTED (K-fold ridge on PK) - in-sample human scores would manufacture kappa < 1 and c-hat/r_H < 1 (memo 3.2 implementation rule).

Pools: PersonaLLM gpt-4-0613, gpt-3.5-turbo-0613, llama-2 (lane3-testbed/data/personallm), Big5PersonalityEssays (399), and the three unlabeled pools from audit 2 (student_llm_essays, ghostbuster gpt_writing, ArguGPT - subsample as in audit 2).

Report per trait x per labeled pool: r_H (PK cross-fitted), c-hat, kappa = s2_M/V_H, delta = (mu_M - mu_H)/sqrt(V_H), detector AUC vs PK-human. Per unlabeled pool: kappa, delta, detector AUC only (no labels).

Also: (a) A3 check - detector score against pool label inside each labeled pool (SPEC assumption 3, now testable); (b) Spearman-Brown check (memo 2.4/4): rerun PK trait recoverability truncated at 100 and 190 words to test the (E72) premise; (c) Q12 - Big5 pool label balance per trait (Prop 16 assumes balanced); (d) confirm personallm/human_stories is the PK essays by hashing against essays.csv.

DELIVERABLE: lane3-testbed/POOL-MEASUREMENTS.md with the per-pool tables + a machine-readable pool_measurements.json (per-pool per-trait g, kappa, delta, AUC, and paths to saved per-text score files). End with MEASURE-DONE. No generation, no API keys, local compute only. This table is the paper's first empirical content - realized (g, kappa, delta) of persona-conditioned text across four generators.
