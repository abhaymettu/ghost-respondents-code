# Layer B full grid: SPEC 4.3's box on real text, against SPEC 4.4's pre-registered thresholds

Run 2026-09-09, 336 cells, 100 replications each, 10844 s on 10 workers at `nice -n 15`,
zero failed cells. Outputs in `results/layerb-grid/` (`grid.jsonl`, `cells/`), log
`layerb-grid-run.log`, runner `run_layerb_grid.py`.

**`score_version = "oof"`.** Every chunk score is read from lane 3's out-of-fold columns
(`inject/pools.py::SCORE_VERSIONS`). An earlier 336-cell run on the in-sample columns was
halted at 176/336 by orchestrator decision D1 (lane 3 pass-3 review finding B3) and is
preserved, unused, in `results/layerb-grid-insample-partial/`. **No number in this file comes
from that run**, and none should be quoted from it.

**Bottom line: three of SPEC 4.4's four thresholds FAIL on real text, and the fourth fails in
the direction SPEC anticipated only for the oracle cell.** This is a finding, not a defect:
the reason is visible, measured, and the same in every table below. On out-of-fold scores the
trait signal in a text chunk is weak (`rho_H = 0.068`), so at SPEC's Layer B sample sizes the
sampling noise in a validity coefficient is ~47% of the coefficient itself. Contamination bias
at `pi <= 0.30` is smaller than that noise in most cells, and every correction that removes
some of the bias adds more variance than it removes. **The naive estimator has the lowest
median rho_H RMSE in every detector group, and the lowest cellwise RMSE (ties included) in 274
of the 336 cells.** Layer A's corrections were validated in a regime
(`rho_H = 0.418`, 500 reps) that the real text does not reach.

---

## 1. The box

336 cells. All at `k = 4` chunk items, `rho_T = 0.5`, machine draws with replacement,
`n_bins = 8`. Each (pool, trait) pair has its own frozen calibration split, so the saved
record carries six split IDs: `729645da4c64c3a1` for the 216 core cells (gpt-4, EXT),
`f0b3f09fe0a4fe9b` for the 72 llama-2 generator cells, and `b345358eedf337b1` (NEU),
`f5f4db1949e3911c` (AGR), `fa4de8eb4b9f4dc2` (CON), `96726cec98c66706` (OPE) for the 12 cells
of each trait arm.

| arm | cells | design |
|---|---|---|
| core | 216 | pi(6) x detector(4) x n(3) x p(3), frontier generator (`personallm_gpt-4-0613`), EXT |
| generator | 72 | open model (`personallm_llama-2`), n = 1000, full pi x detector x p |
| trait | 48 | NEU, AGR, CON, OPE at n = 1000, p = 0.5, the two real detector points |

- `pi` in {0.01, 0.02, 0.05, 0.10, 0.20, 0.30} and `detector` in {none, calibrated, degraded,
  oracle} are SPEC 4.3 verbatim. `n` in {500, 1000, 2400} is SPEC 6's Layer B cap (n = 5000
  exists only in Layer A, because the essays base cannot support it).
- `p` in {0, 0.5, 1} is the assignment coupling, SPEC 4.3's `c` axis realized as `c = p c_pool`
  (design-pivot memo section 8.2, P1'). **Why the box is crossed with coupling rather than
  holding it fixed:** SPEC 4.4's headline threshold is conditioned on `c`, so the cells the
  success claim is made in have to be present at every (pi, n, detector).
- The generator arm is reduced on `n` only, because `n` moves sampling variance and not the
  population moments -- checked on the Layer A grid and in LAYERB-SWEEP.md's (pi, n) box.
  This reduction, and the realization of SPEC 4.3's `c` axis through the assignment coupling
  `p` above, are design adaptations of SPEC 4.3; the grid is not the exact pre-registered cell
  set, and section 3 says so.
- Trait is not a SPEC 4.3 axis; the arm exists because the rest of the box sits at EXT and the
  headline should not hinge on one trait.

### 1.1 What the design cannot reach, stated up front

**Realized coupling tops out below SPEC's "partial".** `c = p c_pool` and the measured pool
couplings are `c_pool = 0.379` (gpt-4/EXT, `kappa = 0.798`, `delta = +0.534`, `g = 1.862`) and
`c_pool = 0.194` (llama-2/EXT, `kappa = 0.537`, `delta = +0.264`, `g = 0.780`). So the strongest
cell in the box, p = 1, sits at `c = 0.379`, below Layer A's operationalization of partial
(0.4) and far below high (0.9).

Two consequences, both load-bearing:

1. SPEC 4.4's applicability condition `c <= partial` is satisfied by **every cell in the box**,
   so the bias threshold is evaluated at all three p levels, not only p <= 0.5.
2. The high-c corner SPEC 4.4 anticipates for the boundary map ("high pi with high c") **is
   unreachable with these pools**. Assignment-coupled injection is bounded by the pool's own
   realized coupling; the memo says so (`continuous on [0, g_pool]`). The boundary map in
   section 5 is therefore a map of the reachable region, and its high-c edge is 0.379.

### 1.2 Three things Layer B measures that Layer A sets

**The detector sets specificity; sensitivity is a result.** `detector_flags` thresholds at a
quantile of the human detector scores, so `sp` is chosen and `se` is measured. Layer A's
(se, sp) pairs do not exist here. SPEC 4.3's "calibrated" and "degraded" are read as the
specificity targets 0.99 and 0.85:

| pool | detector | sp target | realized sp | **realized se** |
|---|---|---|---|---|
| gpt-4 | calibrated | 0.99 | 0.989 | **0.276** |
| gpt-4 | degraded | 0.85 | 0.849 | **0.683** |
| llama-2 | calibrated | 0.99 | 0.989 | **0.624** |
| llama-2 | degraded | 0.85 | 0.849 | **0.946** |

At the in-domain operating point the detector catches 28% of frontier-model text. That single
number does more to explain this grid than any estimator property.

**The estimand is small.** `x` is chunk 1 of the essay and the truth is
`rho_H = rho_T * Cor(chunk_1, theta) = 0.5 * 0.1351 = 0.0676` (EXT). At n = 1000 with 100 reps
the naive MCSE is about 0.0031, i.e. about **+-0.046 relative** to the truth. That is one
MCSE, not a 95% interval; the corresponding 95% half-width is about +-0.09 relative. SPEC 4.3's
100 reps were set
before the OOF refit; they are used verbatim here, and the resulting power is a fact about the
design that every threshold below inherits.

**The chunks are near-parallel, and the between-chunk correlation is not reliability.** On OOF
scores the four chunk-trait correlations are 0.135, 0.131, 0.134, 0.094 -- flat. (The
0.350/0.218/0.175/0.124 decay visible on the in-sample columns was leakage concentrated in
chunk 1; it is the reason this grid was re-run.) What survives is the weak-H2 failure:
`rel_H_true = r_H^2 = 0.0183` against a between-chunk correlation of 0.2096, an
**overstatement of 11.5x**, inside WEAK-H2-DIAGNOSIS.md's 5.4x-41.7x range.

---

## 2. SPEC 4.4, verbatim, with numbers

### T1. "corrected bias at most 20% of naive bias in every cell with pi <= 0.20 and c <= partial"

**FAIL.** Applicable: all 280 cells with `pi <= 0.20` (c <= 0.379 < partial everywhere, 1.1).

| estimator | meets the 20% bar | reduces the bias at all |
|---|---|---|
| delete | 24/280 (8.6%) | 141/280 (50.4%) |
| simex | 29/280 (10.4%) | 146/280 (52.1%) |
| labelfree | 20/280 (7.1%) | 90/280 (32.1%) |
| em | 14/280 (5.0%) | 117/280 (41.8%) |

**The bar is degenerate in two thirds of those cells, and saying so is part of the finding.**
The threshold is a ratio against the naive bias, and at 100 reps the naive bias is not
resolvable in most of this box: median `|naive bias| / MCSE = 1.05`, and only **95 of 280
cells (34%)** have `|naive bias| > 2 MCSE`. Where there is no bias to remove, "20% of it" is a
bar set by Monte Carlo noise. The other 185 of 280 cells (66.1%) are unresolved, which
means the naive bias sits inside 2 MCSE of zero, not that it is zero. Restricted to the 95
cells where the naive bias is resolvable:

| estimator | meets the 20% bar | reduces the bias at all |
|---|---|---|
| delete | 14/95 (14.7%) | 67/95 (70.5%) |
| simex | **19/95 (20.0%)** | **71/95 (74.7%)** |
| labelfree | 12/95 (12.6%) | 44/95 (46.3%) |
| em | 5/95 (5.3%) | 54/95 (56.8%) |

The threshold still fails, by a factor of four to five. But the structure is informative: the
pass rate rises monotonically with prevalence, because prevalence is what creates a bias large
enough to be worth removing. Best-of-three corrector, resolvable subset, by pi:

| pi | 0.01 | 0.02 | 0.05 | 0.10 | 0.20 |
|---|---|---|---|---|---|
| cells passing | 0/6 | 0/6 | 2/13 | 8/29 | **20/41** |

### T2. "CI coverage back inside [92, 98]"

**FAIL on rho_T (0/336 for naive, delete and em; 1/336 for labelfree; simex not evaluable).
PARTIAL on rho_H.**

SPEC 4.4's coverage threshold is assessed on rho_H; the rho_T rows are an additional
diagnosis, not the SPEC test. Naive coverage near nominal on rho_H reflects a bias that is
small relative to the interval width in most cells, and is not evidence that any correction
succeeded.

| estimator | rho_H in band | median | rho_T in band | median |
|---|---|---|---|---|
| naive | 261/336 (77.7%) | 0.950 | 0/336 | 0.000 |
| delete | 281/336 (83.6%) | 0.950 | 0/336 | 0.000 |
| labelfree | 222/336 (66.1%) | 0.930 | 1/336 | 0.010 |
| em | 141/336 (42.0%) | 0.910 | 0/336 | 0.020 |
| simex | not evaluable | -- | not evaluable | -- |

`fit_simex` returns no interval unless its bootstrap is opted into with `B_boot`; the Layer A
grid records `coverage: None` for it too. It is not evaluable on this threshold in either
layer, which is a gap in the estimator, not a Layer B result.

On rho_H the median cell is at nominal coverage and the failures are concentrated where bias
dominates variance: for naive, the worst cells are (p = 1, pi = 0.30) and (p = 1, pi = 0.20),
61 of 75 failures being under-coverage.

**The rho_T failure is near-total (one labelfree cell, pi = 0.30 / OPE, lands in band), and
its mechanism is measured end-to-end.** Every estimator reaches rho_T by dividing rho_H_hat by
`sqrt(rel_hat)`, and `rel_hat` is the between-chunk correlation, which overstates `rel_H_true`
by 11.5x on the core cells. Predicted from the population moments,
`rho_T_hat = 0.0676 / sqrt(0.2096) = 0.1476`; the observed mean naive `rho_T_hat` is **0.1447**
over the 216 core cells (0.1446 over the 54 undetected core cells). The two agree to about 2%,
not to three decimals. The gap has a stated source: the per-replication estimate is a ratio of
two noisy quantities, and the contaminated sample's `rel_hat` is not the human
`rel_between_chunk`. The recorded loading bias shows the second point directly. Naive
`loading_hat` (= `sqrt(rel_hat)`) averages 0.487 over the core cells (bias +0.352 on a truth
of 0.135), not `sqrt(0.2096) = 0.458`, and it rises with prevalence from 0.460 at pi = 0.01 to
0.531 at pi = 0.30 because the machine component adds between-chunk agreement. An earlier
draft of this section quoted a loading bias of +0.329 and treated 0.135 + 0.329 = 0.464 as
equal to 0.458; the figure does not reproduce from any single aggregation of the saved table,
and the identity does not hold. **Within the tested scoring and correction setup, the rho_T
scale is not recovered from chunk pseudo-items on this text.** That is the conclusion of
LAYERB-SWEEP2.md Part III and the narrowed claim in lane 3's PASS3-FIXES.md, now measured
through the estimator chain rather than on the score files alone. It does not establish that
rho_T is unrecoverable by any method or at any n.

### T3. "pi-hat error at most 2 points at n = 1000"

**FAIL.**

| estimator | cells passing | median abs error | worst |
|---|---|---|---|
| labelfree | 5/192 (2.6%) | 0.0546 | 0.2836 (pi = 0.01, degraded, CON) |
| em | 0/192 (0.0%) | 0.0637 | 0.2471 (pi = 0.30, calibrated, NEU) |

`delete` and `simex` return no `pi_hat` and are not evaluable. Prevalence estimation on real
text misses by roughly 5 to 6 points against a 2-point bar. Note the sign structure: labelfree
over-estimates at low prevalence (+0.283 at pi = 0.01) and em under-estimates at high
prevalence (-0.246 at pi = 0.30) -- both are pulled toward the middle of the range, which is
what a weakly separated mixture does to any prevalence estimator. The frontier machine and
human chunk-1 distributions overlap heavily (means -0.536 and -0.242, SDs 0.92 and 1.03).

These numbers are at the **post-fix `n_bins = 8`** default. The pre-fix default of 60 was worse
(see `SPEC-FIXES-ROUND3.md` fix 2, and the M1 re-run for the Layer A quantification).

### T4. "correction beats detect-and-delete on RMSE at calibrated and degraded; concede oracle"

**FAIL at both operating points. The oracle concession holds, and is the least of the problem.**

Cells where a correction beats deletion on rho_H RMSE:

| detector | simex | labelfree | em | best of three |
|---|---|---|---|---|
| calibrated | 5/96 | 3/96 | 2/96 | 10/96 (10.4%) |
| degraded | 0/96 | 35/96 | 12/96 | 41/96 (42.7%) |
| oracle | 18/72 | 5/72 | 0/72 | -- (conceded) |

Median RMSE tells the story more directly than the win counts:

| detector | naive | delete | best corrector |
|---|---|---|---|
| none | 0.0317 | 0.0317 | 0.0317 |
| calibrated | 0.0317 | 0.0321 | 0.0342 |
| degraded | 0.0317 | 0.0355 | 0.0359 |
| oracle | 0.0315 | 0.0323 | 0.0323 |

**Naive has the lowest median RMSE in every detector column**, and the lowest cellwise RMSE
(ties included) in 274/336 cells: none 71/72, calibrated 69/96, degraded 87/96, oracle 47/72.
That is a statement about medians and a cell count, not a uniform per-cell ordering. Against
`rho_H = 0.0676`, an RMSE of
0.0317 is 47% of the estimand: this box is variance-dominated, deletion throws away sample and
adds variance, and the corrections add more. The oracle column is the SPEC-anticipated
concession: deletion beats labelfree in 67/72 cells and em in 72/72, and against simex the
comparison is 32 wins, 18 losses and **22 exact ties** -- with a perfect detector there is no
misclassification left for simex to extrapolate away and it returns the deleted-sample estimate
(bias identical to `delete` in 30 of 72 oracle cells, and identical to `naive` in 31 of 72
`none` cells). But the honest statement is stronger and less flattering than the concession:
at this signal level, *doing nothing* beats both.

---

## 3. The four thresholds, at a glance

| # | SPEC 4.4 threshold | verdict | headline number |
|---|---|---|---|
| T1 | corrected bias <= 20% of naive, pi <= 0.20, c <= partial | **FAIL** | best estimator 29/280 (10.4%) verbatim; 19/95 (20.0%) where the naive bias is resolvable |
| T2 | CI coverage inside [92, 98] | **FAIL (rho_T), PARTIAL (rho_H)** | rho_T 0/336 naive, delete, em; 1/336 labelfree; simex not evaluable. rho_H median 0.950 naive, 261/336 in band |
| T3 | pi-hat error <= 2 points at n = 1000 | **FAIL** | median 0.055 (labelfree), 0.064 (em) |
| T4 | correction beats deletion on RMSE, calibrated + degraded | **FAIL** | 10.4% and 42.7% of cells; naive has the lowest median RMSE in all four detector columns |

Nothing was tuned to pass. The thresholds are evaluated as pre-registered, on a cell set that
adapts SPEC 4.3 in two stated ways (section 1): the generator arm is reduced to n = 1000, and
SPEC's coupling axis `c` is realized through the assignment coupling `p` as `c = p c_pool`,
which caps the reachable coupling at 0.379. This is not the exact pre-registered cell set.
The one applicability reading is stated in 1.1 (c <= partial holds everywhere, so T1 is
evaluated on more cells than a p <= 0.5 reading would have used, not fewer).

---

## 4. Headline numbers for the paper tables

**Contamination bias on real text** (naive rho_H, core box, n = 1000, detector = none, EXT,
truth 0.0676, +- is MCSE over 100 reps):

| p (coupling) | pi = 0.01 | 0.02 | 0.05 | 0.10 | 0.20 | 0.30 |
|---|---|---|---|---|---|---|
| 0.0 (c = 0) | -0.0077 | -0.0004 | -0.0067 | -0.0082 | -0.0180 | -0.0194 |
| 0.5 (c = 0.19) | +0.0017 | -0.0002 | +0.0029 | +0.0007 | +0.0098 | +0.0103 |
| 1.0 (c = 0.38) | -0.0007 | +0.0050 | +0.0058 | +0.0108 | +0.0238 | +0.0319 |

MCSE is +-0.0030 in every cell. As relative bias: -11% to -29% at c = 0 (dilution), +15% at
c = 0.19, and **+47% at c = 0.38, pi = 0.30** (inflation). The sign structure is lane 1's three
regimes on real text: attenuation at zero coupling, near-cancellation at the middle, inflation
at the pool's full coupling, with `g = 1.862` above the inflation threshold as (E39) requires.

**Detector reality** (section 1.2 table): 28% sensitivity on frontier text at 99% specificity;
62% on the open model. Detectability is a generator property, not a constant.

**The weak-H2 number**: between-chunk correlation 0.2096 against `rel_H_true` 0.0183, 11.5x,
driving `rho_T_hat` to 0.145 against a truth of 0.5.

**The regime statement**: `rho_H = 0.068`, RMSE 0.032 at n = 1000. Everything else follows.

---

## 5. Boundary map

SPEC 4.4 asks for the cells where nothing works, as a deliverable. Best (smallest) absolute
relative bias over all five estimators, n = 1000, core box; the estimator achieving it in
parentheses.

| detector | p | pi=0.01 | 0.02 | 0.05 | 0.10 | 0.20 | 0.30 |
|---|---|---|---|---|---|---|---|
| none | 0.0 | 0.082 (lf) | 0.006 (nv) | 0.046 (lf) | 0.036 (lf) | 0.099 (lf) | 0.046 (lf) |
| none | 0.5 | 0.025 (nv) | 0.002 (sx) | 0.042 (nv) | 0.010 (nv) | 0.123 (em) | 0.153 (nv) |
| none | 1.0 | 0.010 (nv) | 0.074 (nv) | 0.076 (em) | 0.159 (nv) | 0.335 (em) | **0.398 (em)** |
| calibrated | 0.0 | 0.015 (sx) | 0.005 (sx) | 0.016 (nv) | 0.006 (em) | 0.013 (sx) | 0.010 (sx) |
| calibrated | 0.5 | 0.006 (sx) | 0.051 (em) | 0.115 (nv) | 0.004 (dl) | 0.004 (dl) | 0.101 (sx) |
| calibrated | 1.0 | 0.068 (nv) | 0.042 (em) | 0.138 (nv) | 0.113 (sx) | 0.080 (sx) | **0.316 (sx)** |
| degraded | 0.0 | 0.006 (sx) | 0.004 (lf) | 0.028 (nv) | 0.037 (lf) | 0.016 (dl) | 0.003 (lf) |
| degraded | 0.5 | 0.005 (nv) | 0.003 (dl) | 0.002 (nv) | 0.002 (nv) | 0.024 (dl) | 0.022 (em) |
| degraded | 1.0 | 0.028 (sx) | 0.004 (dl) | 0.029 (sx) | 0.051 (sx) | 0.054 (sx) | 0.053 (sx) |
| oracle | 0.0 | 0.006 (em) | 0.003 (dl) | 0.085 (lf) | 0.007 (sx) | 0.058 (dl) | 0.025 (dl) |
| oracle | 0.5 | 0.001 (dl) | 0.035 (lf) | 0.055 (dl) | 0.009 (dl) | 0.025 (dl) | 0.059 (dl) |
| oracle | 1.0 | 0.052 (dl) | 0.011 (em) | 0.048 (nv) | 0.053 (em) | 0.101 (dl) | 0.001 (dl) |

Reading it:

- **The method's limit in this box is the top-right corner of the undetected rows**: p = 1,
  pi >= 0.20 with detector none, where the best available estimator still carries 34% to 40%
  relative bias (0.335, 0.398), plus p = 1, pi = 0.30 with the calibrated detector (0.316). At
  p = 1, pi = 0.20 the calibrated detector's best relative bias is **8.0%** (simex), so that
  cell is not part of the boundary. That is the reachable boundary; the true high-c corner
  SPEC imagines is past `c_pool` and cannot be built from these pools (1.1).
- **The degraded detector is the best-behaved column**, which is counter-intuitive until the se
  column is read: at sp = 0.85 the detector catches 68% of frontier machine text, so deletion
  actually removes most of the contamination, whereas at sp = 0.99 it catches 28% and leaves
  most of it in. What it does delete is still mostly machine: at pi = 0.20 the realized rates
  (se 0.27, sp 0.99) put about 86% of the deleted observations in the machine component. The
  cost of the calibrated detector is the contamination it misses and the sample it discards,
  not a flood of removed humans. A detector tuned for a low false-positive rate is the one that
  fails.
- **No cell is uniformly won by a correction.** The winning estimator is naive or delete in 34
  of the 72 cells above (naive 17, delete 17, simex 17, em 11, labelfree 10), and no estimator
  wins a majority anywhere.
- **The partial-identification bounds SPEC asks for are not supplied.** SPEC's boundary
  deliverable pairs this map with bounds on rho_H from the partial-identification analysis
  (SPEC "bound estimand" and H5). No bounds were computed in this run; the map above is a
  point-estimate map only, and that part of the deliverable is incomplete.

---

## 6. What this does and does not license

Supported by this grid:

- The contamination-bias sign map of lane 1 holds on real text, including the inflation regime
  at the pool's own coupling (section 4).
- Detect-and-delete at a realistic in-domain operating point removes 28% of machine text and
  costs more RMSE than it saves (T4, section 5).
- Prevalence estimation from a weakly separated text score misses by 5-6 points (T3).
- Within the tested scoring and correction setup, the rho_T scale is not recovered from chunk
  pseudo-items on this corpus (T2). Whether another setup could recover it is not tested here.

Not supported, and not to be claimed:

- No success claim under SPEC 4.4. Three thresholds fail outright and the fourth fails at both
  real operating points.
- Nothing about `c > 0.379`, which these pools cannot produce.
- Nothing from `results/layerb-grid-insample-partial/`.
- No conclusion at 100 reps about any cell whose naive bias is under ~0.006 in absolute value;
  185 of the 280 `pi <= 0.20` cells (66.1%) are in that state, and section 2's T1 says which.
  An unresolved naive bias is a bias that 100 replications cannot separate from zero, not
  evidence that there is none.

The obvious follow-up, not run here: SPEC 4.3's 100 reps were fixed before the OOF refit shrank
the estimand by 2.6x. Re-running the `pi <= 0.20` slice at 500 reps would move the resolvable
fraction from 34% toward Layer A's, and would make T1 a test of the corrections rather than
partly a test of Monte Carlo noise. That is a design decision, not something to fix by
re-scoring.

LAYERB-GRID-DONE

---

## 7. Addendum, 2026-09-10: the pi <= 0.20 slice at 500 replications (decision D7)

Section 2's T1 verdict came with a caveat that was doing a lot of work: at SPEC 4.3's 100
Layer B replications the naive bias was resolvable in only 34% of the applicable cells, so
"20% of the naive bias" was partly a bar set by Monte Carlo noise. D7 re-ran the `pi <= 0.20`
slice at 500 replications to settle whether T1 was testing the corrections or testing the
noise.

**Run.** 280 cells (180 box, 60 generator, 40 trait), 500 reps, the same six frozen splits as
section 1 (`729645da4c64c3a1` on the 180 core cells), same `score_version = "oof"`, same
estimators, `nice -n 15`, 44629 s on 10 workers, zero failed cell jobs. Output in
`results/layerb-grid-500rep/`; the 336-cell record in `results/layerb-grid/` is untouched.

**The two runs are nested, not independent.** `rep_rng` is keyed on `(cell_id, rep)`, so reps
0-99 of this run are the same draws as the 100-rep run and reps 100-499 are new. Verified
rather than assumed: recomputing one cell at 100 reps reproduces all 50 recorded rho_H and
rho_T fields of its 100-rep row exactly. Every comparison below is therefore within-cell.

### 7.1 The resolvability shift is real but partial

| | 100 reps | 500 reps |
|---|---|---|
| median naive MCSE | 0.00309 | 0.00140 (x2.21, theory x2.24) |
| median `\|naive bias\| / MCSE` | 1.26 | 1.79 |
| cells with a resolvable naive bias (> 2 MCSE) | 95/280 (34%) | **130/280 (46%)** |

Five times the replications buys 12 percentage points of resolvability, not a majority. That
is itself an answer: **in the remaining 150 cells (53.6%) the naive bias is still inside 2 MCSE
of zero at 500 reps, i.e. below about 0.003 in absolute value.** That bounds the bias; it does
not show it is zero. At `pi <= 0.05` with `c <= 0.19` the naive
validity coefficient on real text is unbiased to within a thousandth, and no correction can
improve on it.

### 7.2 T1 at 500 replications

| estimator | verbatim (280 cells) | resolvable subset (130 cells) | reduces the bias at all |
|---|---|---|---|
| delete | 24 -> **48** /280 (8.6% -> 17.1%) | 14/95 -> **29/130** (14.7% -> 22.3%) | 141 -> 146 /280 |
| simex | 29 -> **48** /280 (10.4% -> 17.1%) | 19/95 -> **37/130** (20.0% -> **28.5%**) | 146 -> 141 /280 |
| labelfree | 20 -> **39** /280 (7.1% -> 13.9%) | 12/95 -> **31/130** (12.6% -> 23.8%) | 90 -> 73 /280 |
| em | 14 -> **9** /280 (5.0% -> 3.2%) | 5/95 -> **1/130** (5.3% -> **0.8%**) | 117 -> 123 /280 |

Per-cell verdict flips confirm the direction is not an artifact of the changing denominator:
fail->pass outnumbers pass->fail for delete (38 vs 14), simex (33 vs 14) and labelfree (30 vs
11), and reverses for em (7 vs 12).

**T1 still FAILS, and the failure is now a statement about the estimators rather than about
the replication count.** The best corrector, simex, meets the 20% bar in 28.5% of the cells
where there is a bias to meet it on; SPEC 4.4 requires *every* cell with `pi <= 0.20` and
`c <= partial`. The prevalence structure of section 2 survives and sharpens:

| pi | 0.01 | 0.02 | 0.05 | 0.10 | 0.20 |
|---|---|---|---|---|---|
| best-of-three, resolvable cells | 1/5 | 3/10 | 11/25 | 19/41 | **24/49** |

### 7.3 What the extra replications exposed: em

`em` is the one estimator that gets *worse* under better resolution, and it is worth saying
plainly. On the resolvable subset it falls from 5/95 to **1/130**. This is not a convergence
artifact: its median failure rate over the 280 cells is 0.006 and its maximum is 0.024, so
essentially every replication contributed. Its median bias is -0.00090 against naive's
-0.00019, and **`|em bias|` exceeds `|naive bias|` in 157 of 280 cells (56%)**. At 100 reps em
looked like a weak corrector; at 500 it is visibly a slightly harmful one on this text. The
mechanism is not mysterious -- em fits a two-component Gaussian mixture and the chunk-score
mixture on real essays is not one -- but the grid did not have the resolution to say so before.

### 7.4 The other three thresholds, on the same 280 cells

| threshold | 100 reps | 500 reps | verdict |
|---|---|---|---|
| T2 rho_H coverage in band | naive 232/280, delete 244/280 | naive 259/280, delete 269/280 | improves (the coverage estimate is itself better resolved); rho_T still 0/280 |
| T3 labelfree `\|pi_hat - pi\|` at n = 1000 | median 0.0542, 3/160 pass | median 0.0528, 3/160 pass | **unchanged: prevalence error is bias, not noise** |
| T4 best corrector beats deletion on RMSE | 47/160 | **38/160** | **worse** |

T3 and T4 are the informative ones. Prevalence error does not move with replication count
because it was never a variance problem. And T4 moves *against* the corrections: with sharper
estimates, deletion wins more of the calibrated and degraded cells than it did at 100 reps, not
fewer.

### 7.5 What D7 settles

- T1's failure in section 2 was **not** an artifact of 100 replications. Five times the
  replications moves the best corrector from 20.0% to 28.5% of resolvable cells against a
  threshold that demands 100%.
- 150 of the 280 cells (54%) in the `pi <= 0.20` box have a naive bias that 500 replications
  cannot separate from zero; more replications shrank that set from 185 to 150 rather than
  dissolving it.
- Section 2's headline stands unchanged: on real text at the OOF estimand, the naive estimator
  is hard to beat, and `em` is now positively contraindicated.
- Section 6's boundary map and every number in sections 1-6 are from the 336-cell 100-rep
  record and are not superseded; this section adds resolution on `pi <= 0.20` only.

D7-DONE (2026-09-10)
