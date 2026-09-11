# Honest-gaps closure spec (paper/GHOST-RESPONDENTS-DRAFT.md TODO list, 7 items)

Written before any code or draft edit, per the spec-first rule. Scope: close or honestly
withdraw the 7 items the write-up pass flagged, plus reconcile ROBUST-ARM.md and
WATERMARK.md into the draft. No new simulation grids. Foreground only.

## Closure order and per-item plan

**1. T3 SDs (chunk-1 component means/SDs, section 5.3).**
Source: `lane3-testbed/data/scores/personallm_gpt-4-0613.json` and `pk_human.json`,
`chunk_1_oof` field (matches the grid's documented `score_version: oof` convention), trait
`cEXT` (the core box's trait, LAYERB-GRID.md line 37). The numbers currently quoted
(-0.536/-0.242, SDs 0.92/1.03) do not reproduce from any pool/trait/field combination found
by search across all 8 score files and both `chunk_1`/`chunk_1_oof` fields — they cannot be
sourced and must be replaced, not patched.
Closed as: a small script (`paper/scripts/t3_chunk1_dist.py`) computes machine vs. human
chunk-1-OOF mean/SD on the core pool/trait, writes `paper/tables/t3_chunk1_dist.json`, and
the draft quotes those numbers with the script cited. CLOSED if the script runs and the
draft's TODO sentence is replaced with the sourced numbers; WITHDRAWN-honestly (drop the
specific numbers, keep the qualitative overlap claim only) if the script's numbers turn out
not to support "overlap heavily."

**2. H5 partial-identification bounds (section 5.4).**
Ingredients already proven, per pass3-methods-review.md B3: `Att(pi, c)` is affine and
increasing in c at fixed pi (E36, `population.py::att`), and the realized coupling in this
study is bounded at `c_pool = 0.379` (gpt-4/EXT; LAYERB-GRID.md section 1.2) — the paper's
own Limitations section already says c > 0.379 is not reachable here, so it is the honest
upper bound to use, not the structural c=1.
Construction: for the detector = none cells (18 of the 72-cell boundary map: `pi` in 6
values x `p` in {0, 0.5, 1}, n=1000, gpt-4/EXT), `rho_obs_hat` = naive's point estimate
(closed form, `rho_obs = rho_H * Att(pi,c)` exactly when there is no detection/selection
step). Given `pi` and `rho_obs_hat`, but c unknown, the bound is
`[rho_obs_hat / Att(pi, c_pool), rho_obs_hat / Att(pi, 0)]` since Att increases in c.
Scope limit, stated honestly rather than smoothed: this construction only applies where
`rho_obs = rho_H * Att(pi,c)` holds exactly, i.e. detector = none. For calibrated/degraded/
oracle cells, detection adds a selection term (E30-E34, r_F) that is not part of E36/E17's
harmlessness curve, so extending the bound there needs a second derivation not in scope here.
Closed as: script `lane4-simulation/h5_bounds.py` computes the 18-cell bound table, checked
against the SPEC 109 threshold (width < 0.2 correlation units at n=1000), written to
`lane4-simulation/results/h5-bounds/bounds.json`. The draft's TODO is replaced with the
result — CLOSED if the bound is delivered and its width evaluated against the threshold,
for the reachable detector=none sub-case, with the scope limit stated in the same paragraph.
This is not the same claim as "the boundary map's bounds are supplied everywhere" — that
remains unimplemented for detected cells and is stated as still open in Limitations.

**3. Document-pooled Layer B run (section 6).**
Checked: no document-pooled-scorer grid run exists in `lane4-simulation/results/` (only
chunk-level runs). Running the actual document-pooled Layer B grid is a new simulation and
out of the "no new code changes without a spec, no new grids" scope of a gaps-closure pass —
building it properly (a document-pooled scorer swapped into the OOF pipeline, then a fresh
72+ cell grid) is a multi-hour lane-3+lane-4 undertaking, not a doc fix.
Closed as: WITHDRAWN-honestly. The draft's TODO sentence is rewritten from "the obvious next
experiment, not run" (implying imminence) to an explicit statement that it is out of scope
for this paper and named as future work in Limitations, with the existing whole-text
comparator numbers (`PASS3-FIXES.md` T3) kept as the only evidence, clearly labeled as
suggestive rather than confirmatory.

**4. Verified reference list (References section).**
Full verification of every citation against a primary source (checking author names, years,
venues, DOIs) for ~15-20 references is a literature-checking task, not a code or derivation
task, and several sources are dated 2026-08/2607/2506 (post-cutoff or unusual identifiers)
that cannot be checked against my training knowledge and would need a live source check.
Closed as: audit what's checkable now (internal consistency: does the DOI/arXiv ID resolve
in format, is the same source cited consistently across RADAR-DAY6/7/8.md, SPEC.md, and the
draft) and flag every entry that still needs a live look-up, rather than claiming full
verification without one. Reported as CLOSED for the audit-and-flag step; WITHDRAWN-honestly
on the specific "verified against a real source" claim — that requires network/library
access not exercised here, and the TODO is rewritten to say precisely what was and was not
checked.

**5. Author/affiliation (References/front matter).**
Needs Abhay's name, affiliation, and whether to credit anyone else — facts only he has.
BLOCKED-OWNER, no action, left in the TODO list with that exact status.

**6. SPEC.md freeze-commit.**
`git log -1 -- SPEC.md` = `db7c17102355d7ef8b7799d206753b77a5c13801`, and `git status` shows
no uncommitted changes to SPEC.md — it is already frozen at that commit. Closed as: CLOSED,
by adding the commit hash to the Reproducibility appendix's artifact table so "confirm it is
frozen at the commit the paper cites" resolves to a written, checkable hash instead of an
open question.

**7. Reconcile ROBUST-ARM.md and WATERMARK.md into the draft.**
Both addenda are already `*-DONE` and contain findings not in the current draft:
- ROBUST-ARM.md: second independent line of evidence for the structural-mixture claim
  (robust_t/robust_grm underperform naive at the boundary map's hardest corner, robust_t
  worse than naive on 74% of the 72-cell box) — belongs in section 5.4/5.5 (it extends the
  boundary-map story) and in Limitations (robust estimation does not rescue the corner).
- WATERMARK.md: the unplanned finding is that Prop. 14's se/sp asymmetry does NOT transfer to
  a watermark-style detector, because the watermark's flag is independent of theta by
  construction (r_F = 0), so bias is governed by plain post-deletion residual-contamination
  algebra (se-dominant at this box's prevalence) rather than the classifier's collider-driven
  sp-dominant asymmetry. This must be represented as a scope boundary of Prop. 14, not a
  refutation — belongs in a Threats-to-Validity/related-work-style subsection near section
  5.4 (detector reality) and in Limitations ("one detector, two generators" bullet gets a
  sibling bullet on the watermark regime).
Closed as: CLOSED if both are added as a new "5.6 Two further estimator/detector regimes"
subsection (or equivalent) with the findings stated as accurately as the source addenda
state them (no strengthening: robust_grm is a "wash," not "also fails"; watermark's se/sp
result is a scope statement about Prop. 14, not a contradiction of it), plus one Limitations
bullet each.

## What "closed" means, restated

- CLOSED: a sourced artifact or a verified fact backs the sentence, and the draft's TODO
  text is replaced.
- WITHDRAWN-honestly: the claim is removed or downgraded to what the evidence actually
  supports, with the reason stated in place of the removed claim.
- BLOCKED-OWNER: needs a fact only Abhay has; left untouched, flagged.

## Non-goals

No new Monte Carlo grid. No claim that the full boundary map (all 72 cells) gets H5 bounds —
only the detector=none sub-case, stated as such. No literature verification requiring a live
network fetch. No draft finalization (chained separately per the task).
