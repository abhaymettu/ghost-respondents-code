# Robust-estimator arm: spec (QUEUE item 3)

Written before any estimator code, per the standing spec-first rule. Judgment-sized: this is
a new feature (two new estimator columns) on an existing grid design, not a new simulation
layer, so the spec is brief rather than a full spec-kit flow.

## 1. What's being added

Two estimator columns, alongside the existing five (`naive`, `delete`, `simex`, `labelfree`,
`em`), registered in `estimators.py`'s `ESTIMATORS` dict:

- **`robust_t`** -- operationalizes "multivariate-t SEM under contamination" (Zhang et al.
  2017, doi:10.3389/fpsyg.2017.01286). Their approach fits an elliptical (multivariate-t)
  model and downweights observations by their robust Mahalanobis distance from the fitted
  center. The direct available equivalent without a new dependency is **Minimum Covariance
  Determinant** (`sklearn.covariance.MinCovDet`, already in the environment via
  `sklearn.mixture.GaussianMixture`'s package): it fits a robust location/scatter estimate by
  finding the subset of observations with smallest generalized variance, which is the same
  bounded-influence, distance-based downweighting logic as a robust elliptical fit, without
  requiring a new SEM package. `rho_H_hat` is read off the robust 2x2 covariance of `(x, w)`;
  `rel_hat` is the mean off-diagonal robust correlation among the `k` items' robust covariance
  matrix, mirroring `_naive_style_fit`'s definition of `rel_hat` (between-item correlation) so
  the two are comparable at the `rho_H_hat` / `rel_hat` / `rho_T_hat` level.

- **`robust_grm`** -- operationalizes "robust latent-trait GRM" (doi:10.3758/s13428-024-02574-2),
  whose core mechanism is a bounded-influence M-estimator that downweights response patterns
  inconsistent with the fitted trait model. The available equivalent without a new dependency
  (the environment has no `statsmodels`) is **Tukey's biweight midcorrelation**, a standard
  bounded-influence robust correlation (Wilcox's robust-statistics literature; implemented in
  `astropy.stats.biweight_midcorrelation` elsewhere) computed here directly in numpy. It gives
  zero weight to points beyond 9 MADs from the median and smoothly downweights the rest --
  the same "ignore or discount atypical responses" logic as a robust GRM fit, without
  reimplementing ordinal IRT machinery that the estimand (`x`, `w` are continuous, not ordinal
  item responses) does not need.

**Named reduction, stated plainly.** Neither estimator reimplements the cited paper's full
model (a fitted multivariate-t SEM / a fitted robust GRM). Both substitute the paper's
downweighting *mechanism* -- distance-based (robust_t) or bounded-influence M-estimation
(robust_grm) -- for its full parametric machinery, applied to the same `(x, w, X)` this grid's
other five estimators already consume. This is enough to test the QUEUE's actual question
(do outlier-robust methods, of either flavor, recover `rho_H` where the boundary map shows
naive/delete/simex/labelfree/em all failing) without a new dependency or a new simulation
layer.

Both estimators run on the **full sample**, like `naive`/`simex`/`labelfree`/`em` -- they do
not consume `sample.flag`. That is the point of the arm: robust estimation is being tested as
an *alternative to* detection, not a refinement of it.

## 2. Grid cells: the Layer B boundary map, exactly

LAYERB-GRID.md section 5's boundary map is the paper's "where nothing works" deliverable: 72
cells, `n = 1000`, core box (frontier generator `personallm_gpt-4-0613`, trait EXT),
`pi in {0.01, 0.02, 0.05, 0.10, 0.20, 0.30}` x `detector in {none, calibrated, degraded,
oracle}` x `p in {0.0, 0.5, 1.0}`. Reusing this exact cell set (same `LBCell`, same
`rep_rng(cell, rep)` seeding, same `setup(FRONTIER, "EXT")`, `REPS = 100`) makes the new
columns directly comparable to the existing best-of-five numbers in that table -- no new
truth values, no new split, no new detector calibration.

`naive` is recomputed alongside the two robust columns (not read from the frozen
`results/layerb-grid/` record) as a same-run, same-seed check: because `rep_rng` and
`build_injected_sample` are unchanged, the recomputed `naive` numbers must reproduce the
frozen record's `naive` numbers for these 72 cells exactly (same verification pattern as
LAYERB-GRID.md section 7's D7 check). If they don't, the run is not trustworthy and gets
reported as a wall, not smoothed over.

`delete`, `simex`, `labelfree`, `em` are **not** recomputed -- their numbers for these 72
cells are already committed in `results/layerb-grid/grid.jsonl` and quoted directly from
there (best-of-five column of the boundary map table).

## 3. What "robust loses" looks like operationally

The paper's expected result: robust methods dampen outliers, but ghost respondents are a
second mixture *component*, not a heavy tail on the human distribution, so a bounded-influence
or distance-based downweighting rule should not reliably separate them the way a correction
built on the mixture structure would (or the way plain deletion does when `se` is high). Two
concrete, falsifiable readings of "robust loses":

1. **Boundary-corner test.** At the boundary map's hardest cells (`detector = none`, `p = 1`,
   `pi in {0.20, 0.30}`, best-of-five relative bias 33.5%-39.8%), robust_t and robust_grm do
   not bring relative bias below the existing best-of-five estimator's value.
2. **Overall test.** Across all 72 cells, robust_t and robust_grm's median relative bias is
   not smaller than naive's, and neither wins (is the single best of the seven columns) in a
   majority of cells -- the same "no cell uniformly won" pattern section 5 already reports for
   the original five.

If either estimator *does* win narrowly or broadly, that is reported as found (per the
honest-science rule): it would complicate, not falsify, the QUEUE's framing, and the addendum
says so rather than re-reading the result to fit the expectation.

## 4. Artifacts

- New estimator functions + `ESTIMATORS` registration: `estimators.py`.
- Unit tests (clean-cell recovery, contamination sanity, `Fit` contract): `test_estimators.py`.
- Runner reusing `run_layerb_grid.py`'s `setup`/`rep_rng`/`build_injected_sample`, restricted
  to the 72 boundary-map cells and the `{naive, robust_t, robust_grm}` estimator subset:
  `run_robust_arm.py` -> `results/robust-arm/grid.jsonl`, `results/robust-arm/cells/`.
- Results addendum alongside `LAYERB-GRID.md`: `ROBUST-ARM.md`, a boundary-map-shaped table
  (robust_t, robust_grm columns added next to the existing best-of-five) plus the headline
  verdict stated plainly, win/loss counts, and the naive-reproduction check from section 2.
