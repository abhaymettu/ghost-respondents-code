# FINALIZATION-REPORT (2026-09-10)

Draft-finalization consistency pass over `paper/GHOST-RESPONDENTS-DRAFT.md`. Scope: consistency
only, no new science, no new runs. Read first: `GHOST-GAPS-DONE.md` (7-item honest-gaps closure),
`lane4-simulation/ROBUST-ARM.md`, `lane4-simulation/WATERMARK.md`.

## What was verified

1. **Every number traces to a committed artifact.** Ran the repo's own
   `paper/scripts/check_numbers.py` (429/430 `numbers.json` keys render somewhere in the draft;
   the flagged "unmatched" tokens are false positives — commit hashes, dates, section numbers,
   DOIs, seeds, split IDs). Beyond the automated pass, hand-traced every major table:
   - Table 1 (detector operating points) byte-identical to `paper/tables/tab_detector_points.md`.
   - Table 3 (contamination map) and Table 7 (boundary map) byte-identical to
     `tab_contamination_bias.md` and `tab_boundary_map.md`.
   - Tables 2, 5, 6, 8, 9, 10, 11, A1 cross-checked against `tab_layerA_regimes.md`,
     `tab_t1_100rep.md`, `tab_t4_rmse.md`, `tab_rF_sensitivity.md`, `tab_thresholds_500rep.md`,
     `tab_layerA_thresholds.md`, `tab_t2_coverage.md`, `tab_t3_prevalence.md`,
     `tab_t1_by_pi.md` — all match.
   - T3's chunk-1 distribution numbers (-0.127/0.280/320, -0.015/0.342/2421) verified byte-exact
     against `paper/tables/t3_chunk1_dist.json`.
   - Watermark diagnostic numbers (0.00263/0.00080/0.00038, mcse ≈0.0019) verified against the
     raw `lane4-simulation/results/watermark/diagnostic.json` `accuracy_trajectory_pi030_p1`
     record, not just `WATERMARK.md`'s prose.
   - Robust-arm boundary-corner numbers (0.484/0.653, 0.363/0.501, medians 0.102/0.072) verified
     against `ROBUST-ARM.md` sections 2-3, which are themselves generated from
     `results/robust-arm/grid.jsonl`.
   - Internal-consistency checks (numbers derived from other quoted numbers) all reproduce:
     rho_H = 0.5 × 0.1351 = 0.0676; r_H² = 0.135² = 0.0183; 0.2096/0.0183 = 11.5×; MCSE
     0.0031/0.0676 = 4.6%; RMSE 0.0317/0.0676 = 47%; naive RMSE 0.0285/0.418 = 6.8%.
2. **SPEC section citations.** Every `SPEC` cross-reference in the draft (1.5, 2.2, 3.1-3.3,
   4.1-4.4) checked against `SPEC.md`'s actual headers — all correct.
3. **Figures.** All 8 figures (`fig1`-`fig8`) referenced in the draft exist in `paper/figures/`
   as both PNG and SVG; numbering matches text references one-to-one.
4. **Honest flags visible exactly as hedged.** Confirmed in the draft, not smoothed:
   - H5 bounds: "only 8 of 18 bounds actually contain the true rho_H," detector=none only
     (section 5.4, Limitations).
   - Document-pooled Layer B: stated as withdrawn future work (section 6, Limitations), not
     imminent.
   - Three references (Huang/AAPOR, Liang/Patterns, Zhang-Xu-Alvero/SMR) still marked
     `unverified` with the specific reason each couldn't be confirmed.
   - Author line reads "Abhay Mettu" with no affiliation — see Fixed/Flagged below.
5. **Terminology.** "boundary map," "coupling," "watermark cell/detector," "oracle floor" used
   consistently; no drift in what each term refers to across sections 2, 5.4, 5.6, 5.7.

## What was fixed

- **Duplicate section number 5.6.** Both "The anti-deletion headline, conditional on r_F" and
  "Two further regimes: robust estimation, and near-perfect (watermark) detection" were numbered
  5.6. Renumbered the second (added by the honest-gaps closure pass) to **5.7**. Checked every
  cross-reference to "section 5.6" in the draft (line 210, and the header itself) — the one
  prose cross-reference correctly means the anti-deletion section, which keeps its number, so no
  other text needed to change. `GHOST-GAPS-DONE.md`'s own description ("New section 5.6") is now
  a stale label for what is 5.7; left that file untouched since it's a historical record of what
  was done, not a claim about the current draft.

## What remains owner-blocked or otherwise open (not touched)

- **Author/affiliation tension.** The draft header states "Author: Abhay Mettu" with no
  affiliation, while the TODO list (item 7) and `GHOST-GAPS-DONE.md` mark author/affiliation as
  `BLOCKED-OWNER` — "needs Abhay's decision (name, affiliation, whether to credit anyone else) —
  not invented." The name is already filled in; the affiliation is not. This is a real
  inconsistency between the header and the TODO's stated status, but resolving it requires
  Abhay's decision (affiliation, and whether the name-as-given is final), so it was not touched.
- **TODO items 1-2** (verify the three motivation-source citations in 1.1; read the terminology
  and rectification-lineage papers before citing in 1.3) are open and are **not** owner-blocked —
  they were explicitly scoped out of the prior gaps-closure pass as requiring literature reading,
  and this finalization pass's brief was consistency-only, not new reading. Flagging this
  precisely because the task asked for "no dangling TODOs except owner-blocked ones": these two
  don't fit that bucket. They are pre-existing, deliberately deferred opens, not something this
  pass silently resolved or missed.
- Three references stay `unverified` (Huang/AAPOR, Liang/Patterns, Zhang-Xu-Alvero/SMR) — per
  task instruction, left marked, not re-attempted.
- Everything downstream of the draft (repro package, preprint submission) — per task scope, not
  started.

## Commits

- This pass: section renumbering fix (5.6 duplicate → 5.7) + this report.
