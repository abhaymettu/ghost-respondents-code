# GHOST-GAPS-DONE (2026-09-10)

Closure pass on the write-up's self-flagged honest-gaps list (`paper/GHOST-RESPONDENTS-DRAFT.md`
TODO list, 7 items). Spec first: `paper/GAPS-CLOSURE-SPEC.md` (commit `35d72c5`). Execution:
commit `77dd6a9`.

## Per-item status

1. **T3 SDs (chunk-1 means/SDs).** CLOSED. The quoted numbers (-0.536/-0.242, SDs 0.92/1.03)
   did not reproduce from any pool/trait/field in `lane3-testbed/data/scores/` — searched all
   8 score files, both `chunk_1` and `chunk_1_oof`. Replaced with sourced numbers: gpt-4/EXT
   `chunk_1_oof`, machine mean -0.127 (SD 0.280, n=320) vs. human mean -0.015 (SD 0.342,
   n=2421). Script: `paper/scripts/t3_chunk1_dist.py`, artifact:
   `paper/tables/t3_chunk1_dist.json`.

2. **H5 partial-identification bounds.** CLOSED for the detector=none sub-case (18 of the
   72-cell boundary map). Built from E36 (Att affine/increasing in c) and the study's own
   reachable-coupling bound (`c_pool = 0.379`, gpt-4/EXT), no new simulation. Script:
   `lane4-simulation/h5_bounds.py`, artifact: `lane4-simulation/results/h5-bounds/bounds.json`.
   All 18 cells pass the SPEC width criterion (< 0.2), but only 8/18 bounds actually contain
   the true rho_H — reported as found, not smoothed, because the bound treats a 100-rep MC
   point estimate as exact. Calibrated/degraded/oracle cells are NOT bounded (would need a
   second derivation combining E36 with the detection selection term, E30-E34) — stated as a
   remaining limitation, not implied closed.

3. **Document-pooled Layer B run.** WITHDRAWN-honestly. Confirmed no such run exists on disk.
   Building it is a new scorer plus a new grid, out of scope for a gaps-closure pass. Draft's
   "obvious next experiment, not run" (implying imminence) rewritten to state it explicitly as
   future work; added to Limitations.

4. **Verified reference list.** CLOSED as an audit-and-flag pass, not full live verification
   of every entry. Checked live: Argyle et al. 2023 (full author list + volume/pages
   corrected), Wu/Ma/Chen 2026 Psychometrika (author names recovered — were entirely missing),
   PersonaLLM (full citation added), Park/Jeong/Kim "Style as a confound" (full citation
   added), Meta Muse press release (confirmed live), roberta-base-openai-detector (confirmed
   live). Could not confirm live (JS-rendered page or 403): Liang et al. Patterns (DOI
   resolves correctly, author list not re-confirmed), Huang et al. AAPOR (only the PDF
   filename's first-author name is confirmed), Zhang/Xu/Alvero SMR preprint (OSF page
   returned no bibliographic content). All three marked `unverified` in the References
   section with the specific reason, rather than presented as checked.

5. **Author/affiliation.** BLOCKED-OWNER. Needs Abhay's decision (name, affiliation, whether
   to credit anyone else) — not invented, left untouched in the TODO list with this status.

6. **SPEC.md freeze-commit.** CLOSED. `git log`/`git status` confirm SPEC.md has no
   uncommitted changes and is frozen at commit `db7c17102355d7ef8b7799d206753b77a5c13801`.
   Hash added to the Reproducibility appendix's artifact table.

7. **Reconcile ROBUST-ARM.md and WATERMARK.md into the draft.** CLOSED. New section 5.6
   ("Two further regimes: robust estimation, and near-perfect (watermark) detection") added,
   plus three new Limitations bullets. Robust-estimator finding stated at the same strength
   as ROBUST-ARM.md (robust_t worse than naive on 74% of cells; robust_grm "close to a wash,"
   not "also fails"). Watermark's unplanned finding — Prop. 14's se/sp asymmetry does not
   transfer to a decoupled (r_F = 0) detector, because the collider mechanism the asymmetry
   runs on is absent, leaving a residual-contamination formula that favors se over sp at this
   box's prevalence — is stated as a scope boundary of Prop. 14, not a contradiction of it,
   matching WATERMARK.md section 3's own framing.

## What is still open (not part of this pass, not silently closed)

- TODO items 1-2 from the draft's original list (verify motivation-source wording, section
  1.1; read terminology/rectification-lineage papers, section 1.3) — out of scope for this
  pass, left as-is.
- Draft finalization — chained separately per the task, not started here.

## Commits

- `35d72c5` — spec, before any code/draft change.
- `77dd6a9` — execution: draft edits, `h5_bounds.py`, `t3_chunk1_dist.py`, artifacts.
