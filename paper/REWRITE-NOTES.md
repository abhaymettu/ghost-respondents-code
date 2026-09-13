# Rewrite notes: from the kill-claim paper to the boundary-map paper

This documents Track 1 of the recovery (rewrite track; a sibling lane owns estimator fixes in
`lane4-simulation/`). Brief: `derivations/pass3-methods-review.md`, the pass-3 BLOCK. The
paper and tables/figures in `paper/` already reflect the rewrite (commits `21337ac` through
`35d0088`); this note is the record of what changed and why, plus the SPEC.md amendments made
in this pass. Nothing in `lane4-simulation/` was touched.

## What forced the rewrite

Three blocking findings in the pass-3 review, all claim-vs-evidence rather than math errors:

- **B1.** SPEC 1.5's "kills detect-and-delete" needs r_F ~ 0.5; lane 3 measured r_F ~ 0.053.
- **B2.** SPEC 4.4's pre-registered thresholds and H3/H4 are contradicted by the completed
  372-cell Layer A grid: deletion beats every correction on RMSE in 82-98% of realistic
  cells; the primary (`labelfree`) estimator reaches nominal coverage in 0 of 372 cells.
- **B3.** H5's bounds estimator did not exist.

## Section-by-section: what changed

**Title and abstract.** "Ghost respondents" (an anti-deletion methods paper) became "a
boundary map for covert AI authorship" (a paper whose deliverable is the map of where
correction helps, where deletion helps, and where nothing helps). The abstract's headline
moved from "deletion is biased, here is the fix" to "the corrections do not [work]: three of
four thresholds fail outright and the fourth fails at both realistic detector operating
points" plus the conditional r_F claim.

**Section 1 (Introduction).** Unchanged in problem setup (the mixture framing, coupling c,
homogenization). What changed is section 1.2 ("What the paper finds"): it now states the
threshold results in the first sentence.

**Section 2 (mixture model, section 2.3 detect-and-delete).** The derivation is untouched —
pass 3 could not break any of it. What changed is the framing sentence at the end of 2.3
("Every term of the selection channel enters through q, so the whole effect is O(r_F^2).
Section 5.6 shows what that costs the argument") — added to point forward to the conditional
result instead of asserting the kill claim inline.

**Section 3 (estimators).** No claim changes; unchanged.

**Section 4 (simulation design).** Added Table 1 (realized detector operating points on real
text — 27% sensitivity for frontier-model text at 99% specificity) and the out-of-fold
scoring correction (chunk-1 validity corrected from an inflated in-sample 1.79x-4.33x to the
true 0.135, flat across chunks rather than decaying). This number is load-bearing: it sets
rho_H = 0.068, which is what makes the box variance-dominated.

**Section 5 (results) — the core of the rewrite.**
- 5.1 (Layer A): added the threshold failures at the parametric layer itself (T1 8.6-10.4%,
  coverage only `delete` regular at 83%, `labelfree` 0/372).
- 5.2-5.3: new. The real-text contamination map (Table 3) and the four SPEC 4.4 thresholds
  scored against real text (Table 4), all FAIL or PARTIAL.
- 5.4: the boundary map itself (Table 7), promoted from a contemplated fallback (SPEC 4.4's
  last paragraph) to the paper's spine.
- 5.5: added after the initial 100-rep run raised the objection that most cells were
  unresolved noise, not zero bias. A 500-rep re-run of the pi<=0.20 slice sharpens rather than
  dissolves the failure (best corrector meets the bias bar in 28.5% of resolvable cells, not
  100%; EM gets worse, not better, with more resolution).
- 5.6: the r_F-conditional rewrite of the deletion-selection headline (Table 11), replacing
  the unconditional kill claim with the sensitivity table.
- 5.7: two follow-on arms (robust estimation, watermark-style near-perfect detection) probing
  the boundary map's worst corner from outside the original five-estimator design. Both are
  additional evidence, not corrections to 5.1-5.5.

**Section 6 (discussion).** Rewritten from "here is the correction to use" to six practice
recommendations that start from "report the naive coefficient with the contamination map, not
a corrected coefficient" — the corrected version of the paper's practical advice given the
grid.

**Section 7 (limitations).** Expanded substantially: coupling capped at c=0.379 (below SPEC's
intended high-c corner), synthetic outcome, rho_T not recoverable from chunk pseudo-items
(11.5x reliability overstatement), simex has no interval, H5 bound covers only detector=none
and has weak empirical coverage (8/18) at these replication counts.

## Numbers that moved

- **`labelfree` n_bins**: the shipped default changed from 60 to 8 after the Layer A grid
  completed (staged deliberately so no in-flight worker could pick it up mid-run). The paper
  reports both readings rather than silently using the newer one on old results (section 5.1,
  M1 in the pass-3 review).
- **Chunk-1 validity**: in-sample scoring gave 1.79x-4.33x inflation; the out-of-fold refit
  corrected EXT chunk-1 validity to r_H = 0.135 (flat across chunks: 0.135, 0.131, 0.134,
  0.094), which is what makes rho_H = 0.068 rather than something larger. The 336-cell grid
  was re-run entirely on out-of-fold scores.
- **T3 (prevalence) component means/SDs**: an earlier draft's quoted machine/human component
  means and SDs (-0.536/-0.242, SDs 0.92/1.03) did not reproduce from any pool, trait, or
  score field on disk and were replaced with the sourced numbers (machine mean -0.127 SD
  0.280 n=320; human mean -0.015 SD 0.342 n=2421), generated fresh by
  `paper/scripts/t3_chunk1_dist.py`.
- **Naive-lowest-RMSE cell count**: corrected from an earlier miscount to 274/336 (documented
  in commit `ea19a83`, "correct naive cellwise RMSE counts... delete==naive ties counted in
  none column").
- **r_F**: measured at 0.053 (composite fluency proxy, essays testbed), an order of magnitude
  below the ~0.5 the original unconditional claim required.

## SPEC.md amendments made in this pass

SPEC.md is a pre-registration document and was frozen at commit `db7c171` for the paper's
Reproducibility appendix. Per this track's brief ("do not silently delete pre-registered
text; supersede it visibly"), three dated amendment blocks were added in this pass, each
directly under the text it supersedes rather than replacing it:

1. **Section 1.5**, after the unconditional "kills detect-and-delete" sentence: the
   conditional form (deletion-selection scales with r_F^2; measured r_F ~ 0.053 is an order
   of magnitude below what the unconditional claim needs; deletion nets a five-point
   improvement at the measured r_F, not a loss).
2. **Section 4.4**, after the four pre-registered thresholds: contradicted-by-grid, with the
   headline numbers (82-98% RMSE losses, 0/372 coverage, ~29% bias-bar pass rate at 500 reps),
   and the note that the boundary report SPEC 4.4 already named as a possible deliverable is
   now the paper's spine.
3. **Section 5**, after H1-H5: H3/H4 marked contradicted-by-grid; H5 marked as built for the
   detector=none subcase only, with its coverage caveat; H1 marked as surviving with the c=0.9
   caveat; H2 split three ways per the pass-3 review's M5 finding.

No pre-registered text was deleted. The original hypotheses and thresholds remain readable in
place, with the amendment stating what the grid found and pointing to where the paper reports
it.

## Open seams (not closed by this pass)

- The high-c corner SPEC's failure-mode-1 anticipates (identifiability collapse, correction
  reverts to bounds) is not reachable with the current PersonaLLM pools (c capped at 0.379);
  the boundary map's real-text evidence is confined to the coupling range these pools produce.
- H5's bound does not extend past detector=none; extending it needs a second derivation
  combining the c-affine bound with the detection selection term (E30-E34).
- The rewrite depends on lane 3's r_F measurement being a genuine lower bound, not a
  measurement artifact; a validated continuous-score fluency instrument (behind the IEEE
  DataPort BFI login) could move it, in an unknown direction, by an unknown amount.
- Author line, affiliation, and acknowledgements remain BLOCKED-OWNER (needs Abhay's
  decision), per the draft's own TODO list, item 7.

---

## Career framing: which version serves which audience

One-page comparison. The document being compared is the same paper
(there is only one version, the boundary-map version); the question is how the pass-3 rewrite
changed its legibility to two different readers.

**For quant psych PhD applications, this version is stronger than the kill-claim version
would have been.** A methods-focused admissions committee is reading for exactly the things
this rewrite adds: a three-pass verification discipline (independent re-derivation, numerical
certification against simulation, adversarial review) that revised the headline claim before
submission; a pre-registered analysis plan with the threshold results stated at their
magnitude (82-98% miss); and a negative result with a mechanism (the box is
variance-dominated at this validity level). That is closer to what a strong
methods dissertation chapter looks like than a paper with one clean positive finding would
have been. The genuine cost: there is no splashy result to lead with in a research statement,
and the paper is not yet peer-reviewed or even submitted, so it is evidence of process rather
than evidence of a finished, cited contribution. A committee that skims for "what did you
discover" rather than reading the methods will get less out of it.

**For industry research roles, the calculus is more mixed.** The boundary map itself is a
genuinely useful industry artifact — section 6's six recommendations are exactly the kind of
decision rule ("report the naive coefficient with the contamination map," "prefer the
higher-sensitivity detector operating point and report what was deleted") a research scientist
would want to hand to a product team, and the label-free prevalence and EM mixture
results are the kind of finding that saves someone else from shipping a broken correction. But an interview panel or a resume screen optimizes differently from a
dissertation committee: a one-line pitch of "we tested four corrections against detect-and-
delete and none of them beat it" reads, out of context, as a null result, and industry
research roles more often want a portfolio piece that ends in a working, deployed capability.
The mitigation is framing, not content — leading with the boundary map as a decision tool
rather than with the correction estimators as the headline — but that framing has to happen in
the pitch, not the paper; the paper itself is written for the methods audience, correctly, and
should not be softened for the industry read.

**Net:** ship this version for the PhD track as written. For an industry-facing summary (a
one-pager, a talk, a portfolio entry), pull section 6 and the boundary map forward and drop the
pre-registration/threshold-failure framing to a footnote — same evidence, different lead.
