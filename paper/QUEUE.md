# Queue: next grid work items (Day-8 radar items 3-4)

Not run. Queued for the next grid-design pass; owner decides scheduling.

## 3. Robust-estimator arm for the MC grid

Add a robust-estimator arm to the Monte Carlo grid (Layer A and/or Layer B) alongside the
existing five estimators (naive, delete, simex, labelfree, em):

- Multivariate-t SEM under contamination: Zhang, Y., et al. (2017). Robust structural equation
  modeling with the multivariate t distribution under contamination. Frontiers in Psychology.
  doi:10.3389/fpsyg.2017.01286.
- Robust latent-trait GRM: doi:10.3758/s13428-024-02574-2 (robust graded-response-model
  estimation).

**Why this arm, and what the expected result argues.** The paper's current argument is that
machine-authored responses form a structured subpopulation (a second mixture component with
its own mean, variance, and coupling to the trait), not unstructured noise, so ordinary
outlier-robust methods should not be expected to fix contamination bias the way a correction
tuned to the mixture structure would. The expected result — robust estimators dampen outliers
but do not recover rho_H at the levels the SPEC 4.4 thresholds require, because ghost
respondents are not outliers in the classical (heavy-tail) sense — IS the argument: it would be
a second, independent line of evidence for the paper's central claim (naive beats correction in
most of the box) using a completely different estimator family, strengthening the case that the
failure mode is structural (a mixture, not a tail) rather than a defect specific to the four
estimators already tested.

**Scope note.** This is an additional estimator column on the existing grid design (Section 4),
not a new simulation layer; it reuses Layer A/B cells if slotted into `estimators.py`.

## 4. Near-perfect-detection (watermark) regime cell

Add a coupling x accuracy grid cell (or small sub-grid) at near-perfect detector accuracy,
modeling a watermark-based detection regime rather than a classifier-based one:

- arxiv.org/html/2607.10103
- arxiv.org/abs/2506.05594

**Why this cell.** The current grid's `oracle` detector (se = sp = 1) is the closest existing
analog but is treated as a concession/upper bound, not explored as its own regime. A watermark
detector is a distinct, currently-real technology path toward se -> 1, sp -> 1 that differs from
"a better classifier" in kind (it depends on generator cooperation, not text statistics), so it
deserves its own cell rather than being folded into the oracle column. This turns "what happens
if detection becomes near-perfect" from a hypothetical boundary condition into a named regime
tied to a specific, citable detection mechanism — and Section 2.3 / Prop. 14 already establishes
that the deletion-selection bias does NOT vanish as se -> 1 (only sp -> 1 removes it), so this
cell would test whether a watermark regime (which can plausibly push both se and sp toward 1
simultaneously, unlike a classifier operating on a ROC curve) is the one regime where that
result changes character.

**Scope note.** Likely requires only a new detector spec (se, sp) pair plus documentation of why
it's modeled as reachable unlike the classifier-based operating points; no new estimator or
simulation layer.
