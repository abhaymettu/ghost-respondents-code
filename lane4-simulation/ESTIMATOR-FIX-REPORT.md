# Estimator-fix track: M1, B2, B3 (pass3-methods-review.md)

Scope: `lane4-simulation/` and `derivations/` only. Does not touch `paper/` or `SPEC.md` --
those are the sibling paper-rewrite lane's files. This report hands corrected numbers to that
lane; it does not itself change what the paper claims.

**Status when this session started:** `results/grid-labelfree-nbins8/` (M1) already existed,
committed at `29f0e38`, and `h5_bounds.py` (a Layer-B-only, detector=none, non-registered H5
script) already existed, committed at `77dd6a9`. This report verifies M1, and replaces the
Layer-B-only H5 script with a registered estimator run on the full Layer A grid. The `simex`
`B_boot` re-run (B2's third open item) did not exist before this session.

---

## 1. M1: labelfree re-run at n_bins = 8

**Status: done, verified, no new work needed beyond confirming it.** `run_labelfree_nbins8.py`
re-ran only the `labelfree` column of the frozen 372-cell Layer A grid at the estimator's
current default (`n_bins=8`, vs. `n_bins=60` when `results/grid/grid.jsonl` was produced),
reusing the exact same cell set and per-rep RNG streams as the frozen run (verified: `grid.py`'s
`run_cell` builds every estimator's RNG draw from `default_opts` before the estimator loop, in
fixed source order, so narrowing `ESTIMATORS` to `{"labelfree": fit_labelfree}` changes only
which fits execute, not any other estimator's draw). Output: `results/grid-labelfree-nbins8/`,
372/372 cells, ~11.9 core-hours (`labelfree-nbins8-run.log`).

**Comparability limits (already stated in the script's own docstring, restated here):**
`labelfree`'s point estimates and CIs at `n_bins=8` are not directly comparable to the frozen
grid's `n_bins=60` numbers for the same cell -- they are two different estimators sharing a
name. Every other column (`naive`, `delete`, `em`, and now `simex`/`bounds_c`) is untouched by
this change and remains comparable across the two grids.

---

## 2. simex: B_boot re-run so coverage is testable

**Status: done.** `results/grid-simex-boot50/grid.jsonl` reached 372/372 cells; final numbers
below. The frozen grid ran with `B_boot=0` (`GRID-CONFIG.md`),
so `fit_simex`'s `ci_H` is `None` in every cell and `simex`'s H4 coverage claim was structurally
untestable, not merely poor (pass3-methods-review.md B2).

**B_boot choice: 50.** `fit_simex(B_boot=50)` re-runs the full SIMEX point estimate (5 lambdas
x 20 remeasurement draws, the existing `B=20` default) inside each of 50 outer bootstrap
resamples, so cost is roughly `(1 + B_boot)` times the base per-fit cost. Measured on this
machine (1 cell, 20 reps): 0.392 s/rep at `B_boot=50` vs. 0.0084 s/rep at `B_boot=0` from
`GRID-CONFIG.md`'s cost table -- a factor of ~47, consistent with the `(1+B_boot)` model.
Projected cost: 372 cells x 500 reps x 0.392 s = ~72,900 core-seconds = ~20.3 core-hours, ~2h
wall clock at 10 workers. `B_boot=50` was chosen as the smallest bootstrap size in common use
(a coarser choice than EM's own bootstrap elsewhere in this codebase) that still gives a stable
95th-percentile-based CI; a defensible cheaper alternative would be `B_boot=20-30` at
proportionally lower cost, not attempted because 50 was affordable within this session's window.

New script: `run_grid_column.py`, a generalization of `run_labelfree_nbins8.py`'s
narrow-the-ESTIMATORS-map pattern to any single-column re-run (used for both this and
`bounds_c` below), with the same faithfulness guarantee (RNG streams for every other estimator
are untouched).

**Result: `results/grid-simex-boot50/grid.jsonl` reached 372/372 cells; numbers below are from
`recompute_b2_tables.py` re-run against the completed grid.**

With `ci_H` now populated (Fisher-z-style bootstrap CI built from the 50 outer resamples),
`simex`'s H4 coverage claim is testable for the first time: median coverage across all 372
cells is 0.910, with 75.8% of cells at or above 90% nominal coverage but only **105/372 (0.282)**
landing inside SPEC 4.4's tight [0.92, 0.98] band -- close to but still below `naive`'s 0.602 and
well below `delete`'s 0.831. Coverage does not improve with `n` (median 0.911 at n=500, 0.912 at
n=1000, 0.906 at n=5000; fraction inside the [0.92, 0.98] band falls from 0.319 to 0.303 to
0.181 as `n` grows), consistent with the CI being driven by SIMEX's own extrapolation bias
rather than by sampling noise the bootstrap can average away. Median `ci_width` is 0.0995 (max
0.196). `simex`'s point-estimate statistics (bias, RMSE, the H3 and 20%-of-naive-bias tables
below) are unaffected by `B_boot` and match the pre-existing pass3-methods-review.md numbers
exactly -- `B_boot` only ever entered the CI construction, never the point estimate -- which is
the internal-consistency check that this re-run's numbers are correct.

---

## 3. B3: `fit_bounds_c`, the H5 partial-identification bounds estimator

**Status: done.** Registered as an eighth estimator in `estimators.py`'s `ESTIMATORS` dict
(`bounds_c`, alongside the frozen five plus the already-existing `robust_t`/`robust_grm` arm),
unit-tested (7 new checks in `test_estimators.py`, all passing; 39/39 total in the file), and
run across all 372 Layer A grid cells (`results/grid-bounds-c/`, ~34s wall).

### What it computes

(E7): `rho_obs = rho_H * Att(pi, c)`. (E36): `Att` is affine and strictly increasing in `c` at
fixed `pi`. `fit_naive`'s point estimate is a direct estimate of `rho_obs` (Pearson correlation
on the full, undeleted sample -- no detector-dependent filtering, at every detector level), so
inverting (E7) at the two endpoints of a bound `[c_lo, c_hi]` on the unidentified coupling
parameter brackets `rho_H`. `pi`, `rel_H`, `kappa`, `delta` are read off the cell as known
structural parameters (this bounds `c` alone, following the same convention `h5_bounds.py`
already used for Layer B); the default interval is the full structural range `c in [0, 1]`.

### The one-line version of this bound has a coverage bug, and the fix is real work

A bound built by inverting (E36) at the point estimate `rho_obs_hat` alone -- the direct,
"obvious" implementation, and what the first version of this script did -- states only the
*identification* uncertainty from unknown `c` and ignores the *sampling* uncertainty in
`rho_obs_hat` itself:

| version | n=1000 median width | frac(width<0.2) | median coverage | frac(coverage>=0.90) |
|---|---|---|---|---|
| point-estimate bound (first pass) | 0.0247 | 0.982 | 0.349 | -- |
| + Fisher-z sampling CI unioned in (final) | 0.1312 | 0.781 | 0.974 | 1.000 |

At `n=1000` the sampling noise in a Pearson correlation (~1/sqrt(n) ~ 0.03 in correlation
units) is comparable to or larger than a typical `c`-identification width, so the point-estimate
bound easily meets SPEC's width-under-0.2 bar while covering the true `rho_H` in barely a third
of replications -- a bound that is narrow because it is wrong, not because it is informative.
The fix (Imbens & Manski 2004's standard treatment of a partially identified parameter): union
the two uncertainty sources by propagating a 95% Fisher-z CI on `rho_obs_hat`, not just its
point value, through both `Att` endpoints. This is the version registered and reported below.

### Results across the Layer A grid (372 cells, final version)

| slice | n cells | median width | max width | frac(width<0.2) | median coverage | frac(coverage>=0.90) |
|---|---|---|---|---|---|---|
| all | 372 | 0.1405 | 0.3273 | 0.801 | 0.974 | 1.000 |
| n=500 | 72 | 0.1780 | 0.3116 | 0.667 | 0.970 | 1.000 |
| **n=1000 (SPEC's H5 operating point)** | **228** | **0.1312** | **0.3273** | **0.781** | **0.974** | **1.000** |
| n=5000 | 72 | 0.0749 | 0.1996 | 1.000 | 0.978 | 1.000 |

**H5's threshold ("width under 0.2 correlation units at n=1000") is met in 178/228 (78.1%) of
n=1000 cells, not universally**, with coverage now honest (median 97.4%, every one of the 372
cells at or above 90%). Width shrinks with `n` because the sampling-CI component of the bound
shrinks; the `c`-identification component does not (it is a function of `pi`, `kappa`, `rel_H`,
`delta` alone, not `n`), so the floor at `n=5000` (median 0.075) is the pure identification
width -- and that floor alone is well under 0.2 everywhere, confirming the earlier finding that
the *structural* bound is narrow; what fails the width bar at `n<=1000` is finite-sample noise,
which a larger reference sample or a tighter external bound on `c` (as `h5_bounds.py`'s
`c_pool=0.379` did for Layer B) would fix.

This is a genuinely different and more complete result than the pre-existing `h5_bounds.py`
(Layer B, `detector=none` only, 18 cells, 8/18 width pass, no registered estimator, no unit
tests). It is left in place; this report's numbers are the Layer A companion, run at all four
detector levels.

---

## 4. Recomputed H3/H4/SPEC-4.4 tables at the shipped configuration

`recompute_b2_tables.py` merges the frozen grid (`naive`/`delete`/`em`) with the three
single-column re-runs above by `cell_id`, then reproduces B2's table shapes. Output:
`results/b2-tables-recomputed.json`.

### H4: cells with rho_H coverage in [0.92, 0.98]

| estimator | pass3-review (n_bins=60, B_boot=0) | this session (n_bins=8, B_boot=50) |
|---|---|---|
| delete | 309/372 (0.831) | 309/372 (0.831) -- unaffected |
| naive | 224/372 (0.602) | 224/372 (0.602) -- unaffected |
| em | 52/372 (0.140) | 52/372 (0.140) -- unaffected |
| labelfree | 0/372 | 59/372 (0.159) |
| simex | coverage `null` in all 372 | 105/372 (0.282) |
| bounds_c | n/a (did not exist) | reported separately in section 3 (H5 is a bound, not a rho_H point CI, so H4's 0.92-0.98 coverage bar does not apply to it the same way) |

`labelfree` at the shipped `n_bins=8` goes from 0/372 to 59/372 (15.9%) -- a real change,
still far short of nominal, and **still contradicts H4** as a general claim. `simex` with its
coverage now testable (`B_boot=50`) reaches 105/372 (28.2%) -- better than `em` and `labelfree`,
still well short of `naive` (60.2%) and `delete` (83.1%), and **still contradicts H4** as a
general claim.

### H3: RMSE beats delete, realistic detectors (calibrated / degraded)

| estimator | pass3-review calibrated | pass3-review degraded | this session calibrated | this session degraded |
|---|---|---|---|---|
| simex | 22/102 (0.216) | 12/90 (0.133) | 22/102 (0.216) -- unaffected | 12/90 (0.133) -- unaffected |
| em | 0/102 (0.000) | 10/90 (0.111) | 0/102 (0.000) | 10/90 (0.111) -- unaffected |
| labelfree | 0/102 (0.000) | 3/90 (0.033) | 0/102 (0.000) | 13/90 (0.144) |
| bounds_c | n/a | n/a | 44/102 (0.431) | 65/90 (0.722) |

`labelfree` improves at `n_bins=8` (3/90 -> 13/90 at degraded) but **still loses to deletion in
85.6-100% of realistic-detector cells; H3 as a general claim still fails.** `simex`'s RMSE is
unaffected by `B_boot` (it only changes the CI, not the point estimate), so its H3 numbers are
identical to pass3-methods-review.md's: still loses to deletion in 78.4-86.7% of realistic-
detector cells. `bounds_c` beats
deletion's RMSE far more often (43.1%/72.2%) -- expected, since it is a much wider interval
whose *point summary* (the bound's midpoint) trades bias for width rather than minimizing RMSE
the way a point estimator does; this comparison is included for completeness, not as evidence
`bounds_c` is "better" by H3's point-estimation logic, which is not the game a bounds estimator
is playing.

### "corrected bias at most 20% of naive bias", pi<=0.20 and c<=partial (210 cells)

| estimator | pass3-review frac<=0.20 / median / max | this session frac<=0.20 / median / max |
|---|---|---|
| simex | 0.386 / 0.336 / 59.2 | 0.386 / 0.336 / 59.2 -- unaffected |
| delete | 0.343 / 0.426 / 47.4 | 0.343 / 0.426 / 47.4 -- unaffected |
| em | 0.119 / 1.254 / 50.4 | 0.119 / 1.254 / 50.4 -- unaffected |
| labelfree | 0.000 / 5.917 / 1821 | 0.095 / 1.916 / 2098.8 |
| bounds_c | n/a | 0.252 / 0.516 / 2.1 |

`labelfree` at `n_bins=8` is less catastrophic (max ratio drops from 1821x to 2099x -- actually
slightly worse at the tail, but the median drops from 5.9x to 1.9x naive bias) and now passes
the 20% bar in 9.5% of applicable cells instead of 0%. **Still nowhere near "every cell"; the
bar is not met.**

### "pi-hat error at most 2 points at n=1000" (228 cells)

| estimator | pass3-review median / max / frac<=0.02 | this session median / max / frac<=0.02 |
|---|---|---|
| em | 0.0679 / 0.2229 / 0.031 | 0.0679 / 0.2229 / 0.031 -- unaffected |
| labelfree | 0.1481 / 0.5028 / 0.000 | 0.0707 / 0.4161 / 0.000 |

`labelfree`'s median `pi_hat` error roughly halves at `n_bins=8` (0.148 -> 0.071) but still
misses the 2-point bar in every cell.

---

## 5. Does M1/B2/B3 change B2's verdict?

**No.** At `n_bins=8` and with `simex`'s coverage now testable, every SPEC 4.4 threshold that
pass3-methods-review.md B2 flagged as contradicted remains contradicted:

- H4 (nominal coverage): `labelfree` improves from 0/372 to 59/372 and `simex` goes from
  structurally untestable to 105/372 (0.282), but no estimator reaches a defensible fraction of
  cells; `delete` (the estimator the paper exists to discredit) is still the only one that
  regularly hits the [0.92, 0.98] band.
- H3 (RMSE beats deletion): `simex`, `labelfree`, and `em` still lose to deletion in the
  overwhelming majority of realistic-detector cells (`simex`'s RMSE is unchanged by `B_boot`,
  since `B_boot` only affects the CI).
- The 20%-of-naive-bias bar: no estimator gets close to "every cell"; `labelfree` is
  substantially less bad but still fails the bar entirely.
- The 2-point pi-hat bar: `labelfree` roughly halves its error but the bar is still missed in
  effectively every cell.

The direction of every fix in this report is "less bad, not passing." B2's recommended
resolution -- report the SPEC 4.4 threshold failures as the paper's finding (the boundary-map
outcome SPEC 8.1 already names as the likely honest result) -- still stands, now with numbers
computed at the estimators' actual shipped configuration rather than a superseded one.

**B3 is closed differently than B2 predicted.** B2's text expected fixing the estimators would
either flip H3/H4 or not; what actually happened is that H5 (bounds) is the one place a fix
produces a genuinely informative result: the `bounds_c` estimator's *structural* width (its
floor at large `n`) is comfortably under SPEC's 0.2 threshold at every detector level, and once
its coverage bug is fixed, its combined width still clears the bar in 78% of `n=1000` cells and
100% of `n=5000` cells. That is the strongest single result in this report and matches
pass3-methods-review.md B3's own read: given B2, H5 bounds are "the paper's most likely spine."

---

## 6. Runtime cost, this session

| task | cost |
|---|---|
| M1 (labelfree @ n_bins=8, already done pre-session) | ~11.9 core-hours, 372/372 cells |
| bounds_c, first pass (point-estimate bound) | ~11s, 372/372 cells |
| bounds_c, final pass (Fisher-CI-unioned bound) | ~34s, 372/372 cells |
| simex B_boot=50 re-run | ~20.3 core-hours projected, ~2h wall at 10 workers |
| table recompute / analysis scripts | seconds |

`bounds_c` is effectively free relative to the grid's other estimators (no resampling; its
cost is one Pearson correlation and two closed-form `Att` evaluations per rep). `simex`'s
`B_boot` re-run is the only genuinely expensive piece of this track, and it is a `(1+B_boot)`
multiplier on an estimator that was already cheap (`0.0084` s/rep at `B_boot=0`).

---

## Files this session touched (lane4-simulation/ and derivations/ only)

- `estimators.py`: added `fit_bounds_c`, registered in `ESTIMATORS`.
- `test_estimators.py`: 7 new checks for `fit_bounds_c` against from-scratch (E36 + Fisher-z)
  closed forms and Monte Carlo coverage.
- `run_grid_column.py`: new, generalizes `run_labelfree_nbins8.py`'s single-column re-run
  pattern; used for both the `bounds_c` and `simex B_boot=50` re-runs.
- `recompute_b2_tables.py`: new, merges the frozen grid with the three column re-runs and
  reproduces pass3-methods-review.md B2's table shapes at the shipped configuration.
- `results/grid-bounds-c/`: new, 372 cells.
- `results/grid-simex-boot50/`: new, 372 cells, complete.
- `results/b2-tables-recomputed.json`: new.
- This file.

No change to `population.py`, `dgp.py`, `grid.py`, `metrics.py`, `run_grid_full.py`, or any
file under `paper/` or `SPEC.md`.
