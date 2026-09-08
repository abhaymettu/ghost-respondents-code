# Layer B pilot cell

design-pivot-memo section 8.2 step 3. One cell of the P1' assignment-coupling design, run
on lane 3's real measurements. Script `layerb_pilot.py`, log `results/layerb_pilot.log`,
machine-readable `results/layerb_pilot.json`. 15.6s, single-threaded, `nice -n 15`, no
network. The Layer A grid (PID 8258) and `dgp.py` were not touched.

**12 of 14 checks pass. The two failures are real and are reported as findings, not
smoothed over: SPEC 3.2's two prevalence routes are biased in opposite directions on this
cell. Distribution-match reads pi = 0.070 against a true 0.10 (-0.0295, 15.2 MCSE);
adjusted-count reads 0.133 (+0.0329, ~35 MCSE). Section 5 attributes 96% of the second to
detector-calibration transfer gaps of 0.008 (FPR) and 0.013 (sensitivity) between the
reference halves and the halves the survey draws from, and shows the number does not
replicate across calibration splits.**

*Revised 2026-09-07: section 5 previously recorded the adjusted-count branch as unscorable.
Lane 3's FIXES-DONE landed `detector_p_machine` on `pk_human.json`, so it is now scored. The
`g` correction from the same fix is folded into section 1.*

## The cell

| | |
|---|---|
| trait | EXT |
| machine pool | `personallm_gpt-4-0613` (PersonaLLM, n = 320) |
| human base | PK essays, cross-fitted ridge scores (n = 2467) |
| n | 1000 |
| pi | 0.10 (exactly 100 machine respondents per replicate, by permutation, not Bernoulli) |
| p | 0, 0.5, 1 |
| rho_T | 0.5 |
| k_chunks | 1 |
| replicates | 400 per arm |
| seed | 20260907 |

Both pools are split 50/50 into an injection half and a **disjoint held-out reference**
(`split_reference`). The reference is what the SPEC 3.2 estimator reads; if it overlapped
the injected texts or the respondent base, the estimator would be reading its own input
back. Disjointness is asserted in-run, not assumed: machine 160/160, human 1234/1233.

The split means **the pilot's `r_H` and `c_pool` are not lane 3's whole-pool numbers**:

| | whole pool | pilot's injection half |
|---|---|---|
| r_H (PK, EXT) | 0.159629 | **0.182842** |
| c_pool (reweighted) | 0.442002 | **0.475973** |
| predicted p=1 vs p=0 contrast | 0.020012 | **0.021984** |

A random half of 2467 essays moves r_H by 0.023, which is about 0.8 of its own standard
error (1/sqrt(1234) = 0.028). Nothing is wrong; it is the reason every number below is
keyed to the half the pilot actually ran on, and the whole-pool prediction is printed
alongside so the drift is visible.

## 1. The closed form at the realized (g, kappa, delta)

Exact finite-population arithmetic over the two pools, no Monte Carlo:

| p | c | kappa | delta | g | Den | Att | rho_obs predicted |
|---|---|---|---|---|---|---|---|
| 0.00 | -0.00000 | 0.86375 | 0.53616 | -0.00000 | 1.01225 | 0.89454 | 0.081780 |
| 0.50 | 0.23799 | 0.86375 | 0.53616 | 1.20968 | 1.01225 | 1.01477 | 0.092771 |
| 1.00 | 0.47597 | 0.86375 | 0.53616 | 2.41936 | 1.01225 | 1.13501 | 0.103763 |

- **PASS — (E7) closed form equals the direct mixture correlation at every arm.** Max
  |rho_pred - rho_direct| = 1.4e-17. This is the non-vacuous check built in the review round
  (`exact_mixture_law`), which rebuilds the joint law over respondent class x respondent
  label x pool text from the assignment rule and never touches kappa, delta, g or Att.
- **PASS — (E67) `c(p) = p * c_pool` exactly.** Max deviation 1.1e-16 across the three arms.
- **PASS — (E67) kappa and delta are invariant in p.** Identical to 1e-12: 0.863748 and
  0.536157 at every arm. This is the reweighting hook of INJECT.md section 2 doing its job;
  it is exact here rather than approximate because the random branch draws label l with the
  respondent marginal q1 = 0.5170, not with the pool's 0.5000.
- **PASS — capacity holds without replacement.** Worst cell 51.7 expected draws of 80
  available, at p = 1.

`delta` is reported in the CONVENTIONS sign, `(mu_H - mu_M)/sqrt(V_H)`, hence positive.
Lane 3's file uses the memo sign and reports -0.4922 for the same quantity. `Att` depends on
`delta` squared, so no number moves; the sign conflict between CONVENTIONS and the memo is
still unresolved and still needs a ruling (INJECT.md 7b).

### `g`: lane 3's number is a ratio of correlations and should be corrected

Lane 3 reports **g = 2.7725** for this pool and trait. `lane3-testbed/pool_measurement.py:245`
computes it as `chat_r / r_H`. (E66) defines `g = Cov(x_M, theta) / Cov(x_H, theta)`, and
`Cov(x_M, theta) = c * sd_M`, so the covariance form is `c * sqrt(kappa) / r_H`. On the
whole pool that is **2.5163**, not 2.7725; lane 3's is high by exactly `1/sqrt(kappa) = 1.10`.

The tie-break is the most literal reading of (E66), the ratio of label-mean differences
`(m1 - m0)/(h1 - h0)`, which needs no definition at all. On the whole pool that is
**2.5108**; on the pilot's injection half it is **2.41936**, agreeing with the covariance
form to 6 digits (**PASS**, and the check is in the script). The pilot uses the covariance
form throughout.

**Resolved.** Lane 3 recomputed the column on 2026-09-07 (FIXES-DONE): every `g` in
`pool_measurements.json` is now `chat_r * sqrt(kappa) / r_H`, with the old value preserved
per-trait as `g_old_ratio_form` and the method recorded in `meta.g_formula`.
`inject/test_inject.py::test_lane3_moments_match` recomputes `g` in the covariance form from
the per-text files and matches lane 3's post-fix value on **all 20 cells to 8.9e-16**. The
2.7725 above is now `g_old_ratio_form`; the live number for this cell is 2.5163.

## 2. Monte Carlo recovery, 400 replicates per arm

| p | quantity | predicted | MC mean | MCSE | z |
|---|---|---|---|---|---|
| 0.00 | c | -0.000000 | -0.000951 | 0.004984 | -0.19 |
| 0.00 | kappa | 0.863748 | 0.871015 | 0.003548 | 2.05 |
| 0.00 | delta | 0.536157 | 0.536683 | 0.003377 | 0.16 |
| 0.00 | rho_obs | 0.081780 | 0.079335 | 0.001604 | -1.52 |
| 0.00 | Att | 0.894539 | 0.867803 | 0.017543 | -1.52 |
| 0.50 | c | 0.237986 | 0.232471 | 0.004487 | -1.23 |
| 0.50 | kappa | 0.863748 | 0.865439 | 0.003302 | 0.51 |
| 0.50 | delta | 0.536157 | 0.535509 | 0.003406 | -0.19 |
| 0.50 | rho_obs | 0.092771 | 0.089750 | 0.001563 | -1.93 |
| 0.50 | Att | 1.014773 | 0.981722 | 0.017099 | -1.93 |
| 1.00 | c | 0.475973 | 0.475075 | 0.002226 | -0.40 |
| 1.00 | kappa | 0.863748 | 0.869886 | 0.003289 | 1.87 |
| 1.00 | delta | 0.536157 | 0.535818 | 0.003314 | -0.10 |
| 1.00 | rho_obs | 0.103763 | 0.104058 | 0.001467 | 0.20 |
| 1.00 | Att | 1.135007 | 1.138229 | 0.016045 | 0.20 |

**PASS — every realized moment within 4 MCSE of its closed form** (worst 2.05).

`Att` crossing 1 between p = 0 and p = 1 is the substantive result: at p = 0 the machine
texts attenuate the correlation (0.895), at p = 1 the same texts, differently assigned,
**amplify** it (1.135). Same pool, same kappa, same delta; only the assignment changes.

An earlier 100-replicate run had the p = 0.5 arm 3.0 MCSE low on rho_obs, with a matching
deficit in realized c. It did not replicate: an independent 400-replicate run at a different
seed stream put every arm within 1.1 MCSE, and running the same arms with `replace=True`
gave the same picture, so without-replacement depletion of the 160-text pool is not the
cause. It was seed noise across 15 z-scores. Recorded because it was checked, not assumed.

## 3. The random-vs-matched contrast, and what n = 1000 can actually resolve

| | |
|---|---|
| predicted (E7) contrast | 0.021984 |
| observed | 0.024723 +/- 0.002176 (MCSE) |
| agreement with (E7) | 1.26 MCSE (**PASS**) |
| SD of the contrast in ONE replicate | 0.04353 |
| **z from a single replicate** | **0.51** |
| z over 400 replicates | 11.36 |
| replicates for z >= 2.8 at n = 1000 | **31** |

**PASS at this (n, replicates) — and the honest reading is narrower than the pass.** The
contrast is 0.022 against a per-replicate SD of 0.044. **A single survey of n = 1000 cannot
see it: z = 0.51.** The effect is resolvable only as a design-level claim averaged over
replicates, and 31 replicates is the threshold at n = 1000.

The single-survey route is n, not replicates. The per-replicate SD scales as 1/sqrt(n), so
resolving the contrast at z = 2.8 within one survey needs

    n >= 1000 * (2.8 * 0.04353 / 0.021984)^2 = **30,700**.

That is the number the paper should quote if it ever claims a single study could detect the
matched-vs-random difference at this pool, this trait, and this pi. At pi = 0.10 and
r_H = 0.18 it is out of reach for one survey; the claim the design supports is about the
estimator's behaviour across replications, not about detecting coupling in a given dataset.

Everything above uses r_H = 0.1828 (the injection half). At lane 3's whole-pool
r_H = 0.1596 the predicted contrast falls to 0.020012, and the single-survey n rises to
roughly 37,000.

## 4. Estimator recovery

Target rho_H = rho_T * r_H = **0.091421**. `rho_T` itself is **not** recovered: that step
needs rel_H, which at k_chunks = 1 is not identified, and lane 3 did not produce chunk-level
scores (INJECT.md section 9). The pilot stops at rho_H and says so.

The prevalence step is `estimators._distribution_match_pi`, the SPEC 3.2 code itself, not a
re-implementation. The EIV chain is `estimators.fit_labelfree` lines 402-425 with one
substitution: **Layer B's r_H plays the role Layer A's sqrt(rel_H) plays in N**, so
`N = (1 - pi) + pi * c * sqrt(kappa) / r_H`. `fit_labelfree` itself cannot be called here
because it estimates rel_H from an item matrix that a k_chunks = 1 sample does not have.

| p | estimator | target | mean | bias |
|---|---|---|---|---|
| 0.00 | pi (dist-match) | 0.100000 | 0.070945 | -0.029055 |
| 0.00 | pi (adj. count) | 0.100000 | 0.131504 | +0.031504 |
| 0.00 | rho_H (c known) | 0.091421 | 0.085278 | -0.006143 |
| 0.00 | rho_H (pi oracle) | 0.091421 | 0.087919 | -0.003502 |
| 0.00 | rho_H (c = 0 assumed) | 0.091421 | 0.085278 | -0.006143 |
| 0.50 | pi (dist-match) | 0.100000 | 0.069470 | -0.030530 |
| 0.50 | pi (adj. count) | 0.100000 | 0.133942 | +0.033942 |
| 0.50 | rho_H (c known) | 0.091421 | 0.088613 | -0.002807 |
| 0.50 | rho_H (pi oracle) | 0.091421 | 0.088165 | -0.003255 |
| 0.50 | rho_H (c = 0 assumed) | 0.091421 | 0.096435 | +0.005014 |
| 1.00 | pi (dist-match) | 0.100000 | 0.070980 | -0.029020 |
| 1.00 | pi (adj. count) | 0.100000 | 0.133370 | +0.033370 |
| 1.00 | rho_H (c known) | 0.091421 | 0.095167 | +0.003746 |
| 1.00 | rho_H (pi oracle) | 0.091421 | 0.091789 | +0.000368 |
| 1.00 | rho_H (c = 0 assumed) | 0.091421 | 0.112001 | +0.020580 |

- **PASS — the EIV correction recovers rho_H within 25% at every arm** (worst 6.7%, at
  p = 0). With pi supplied as an oracle the worst arm is 3.8% and p = 1 lands at 0.4%, which
  locates most of the residual error in the prevalence step rather than the correction.
- **PASS — (E67) the prevalence estimate is invariant in p.** Spread across arms 0.0015
  against an MCSE of 0.0020. `pi_hat` reads only x, whose marginal law (E67) says is p-free,
  and the Monte Carlo confirms it to within noise. This is an independent confirmation of
  the reweighting hook from a direction the exact arithmetic in section 1 does not touch.
- **FAIL — the prevalence estimator is biased low.** Mean `pi_hat` = 0.0709, 0.0695, 0.0710
  against pi = 0.10; **bias -0.0295, or 15.2 MCSE**. Not seed noise, not p-dependent, and
  unchanged by `replace=True`. The mechanism is overlap: the machine and human score
  distributions have kappa = 0.86 and delta = 0.54, so they sit almost on top of each other,
  and the Hellinger-minimising mixture weight under heavy overlap pulls toward 0. **A
  30% relative under-count of machine prevalence is a headline number for the paper**, and
  it is a property of the estimator on realistic pools, not of the injection design.

**The c = 0 row is the point of the whole design.** SPEC 3.2 assumes no coupling. At p = 0
that assumption is true and costs nothing (the `c = 0` and `c known` rows are identical).
At p = 1 assuming c = 0 **over-corrects rho_H by +22.5%** (0.1120 against 0.0914) while the
same chain given the true c lands within 4.1%. Coupled machine respondents break the
label-free correction in the direction of overstating the human correlation, and the size of
the break at realistic (kappa, delta, g) is about 22% at pi = 0.10.

## 5. The adjusted-count prevalence branch, now that lane 3 has landed the scores

**Status change.** This section previously read FAIL-unscorable: `pk_human.json` carried
`ids`, `labels` and `cross_fitted_scores` and no `detector_p_machine`, so
`build_injected_sample` fell through to `flag = all False` and `se = sp = NaN`. Lane 3 shipped
the column on 2026-09-07 (`POOL-MEASUREMENTS.md` section *Pilot fixes*, FIXES-DONE):
2467/2467 scores written by `pk_human_detector_scores.py`, aligned 1:1 to the existing `ids`.
The branch is now scored, and it fails for a different and more interesting reason.

### How the operating point is calibrated

`fit_labelfree(method="adjusted_count")` inverts `pi_hat = (flag_rate - (1-sp)) / (se - (1-sp))`.
Everything on the right must come from outside the survey, or the estimator reads its own
input back. So all three inputs are taken from the **held-out halves**:

| quantity | source | value |
|---|---|---|
| threshold | 0.99 quantile of the human REFERENCE half's detector scores | 0.999222 |
| `sp` | realized specificity on that same human reference half | 0.98946 |
| `se` | realized sensitivity on the machine REFERENCE half | 0.28125 |
| denominator `se - (1-sp)` | | 0.27071 |

This is deliberately **not** `build_injected_sample`'s internal threshold, which is computed
on the respondent base itself (it reports sp = 0.9895, se = 0.2375) and would be in-sample.
The per-replicate flag rate is recomputed as `mean(s.F > thr)` against the held-out threshold
and inverted through SPEC 3.2's own `_adjusted_count_pi`.

### Result

| p | target | mean pi_hat_ac | MCSE | bias |
|---|---|---|---|---|
| 0.00 | 0.100000 | 0.131504 | 0.0009 | +0.031504 |
| 0.50 | 0.100000 | 0.133942 | 0.0010 | +0.033942 |
| 1.00 | 0.100000 | 0.133370 | 0.0009 | +0.033370 |

- **PASS — the branch is scored.** Both `se` and `sp` are finite, the flag rate is non-zero,
  and the estimate is defined at every arm.
- **FAIL — it over-counts by +0.033, about 33% relative,** at every arm and roughly 35 MCSE.

### Why: the calibration does not transfer to the survey's own halves

The failure is not in the injection design and not in the inversion. It is that neither `se`
nor `sp`, measured on the reference halves, holds on the halves the survey actually draws
from. Write the realized flag rate as `pi * se_inj + (1 - pi) * (1 - sp_base)` and invert it
with the reference half's `(se_cal, sp_cal)`; the bias is exactly

```
bias = [ pi * (se_inj - se_cal) + (1 - pi) * ((1 - sp_base) - (1 - sp_cal)) ] / (se_cal - (1 - sp_cal))
```

a sensitivity term and a false-positive-rate term, both divided by the denominator.

| term | gap | contribution |
|---|---|---|
| sensitivity: injected texts 0.29375 vs reference half 0.28125 | +0.0125 | +0.0046 |
| false-positive rate: survey base 0.01864 vs reference half 0.01054 | +0.0081 | +0.0269 |
| **predicted** | | **+0.0315** |
| **observed** | | **+0.0329** |

**The two transfer gaps account for 96% of the bias**, and the FPR term is 85% of what they
account for. `LAYERB-SWEEP.md` confirms the same decomposition across 15 machine cells: it
explains **99.6% of the variance in the adjusted-count bias**, with a maximum residual of
0.0049.

The mechanism is arithmetic. At pi = 0.10 the true signal in the flag rate is
`pi * se = 0.028`; the false-positive floor is `(1 - sp) = 0.019`. The floor is two thirds
the size of the signal, so a 0.008 error in the floor is a 30% error in pi. **A detector with
se = 0.28 at sp = 0.99 has no headroom at pi = 0.10**, and its adjusted count is dominated by
how precisely its own operating point is known, not by how well it separates.

**This cell's specific number does not replicate across calibration splits, and that is the
finding.** `LAYERB-SWEEP.md` re-runs gpt-4/EXT at a different seed, so a different random
half calibrates the detector, and gets **+0.0070** where this run gets +0.0329. Same pool,
same trait, same pi, same reps -- the adjusted count moved by 0.026 on nothing but which
160 essays landed in the calibration half. The reported bias is a draw from that
distribution, not a property of the cell.

This is a stronger result than the unscored FAIL it replaces: the two prevalence routes fail
in **opposite directions** on the same cell. Distribution-match under-counts by 30% relative
(overlap: kappa = 0.86, delta = 0.54); adjusted-count over-counts by 33% relative (an
FPR floor that is 67% of the signal). Neither is usable as a point estimate of pi here, and
they do not bracket the truth by any argument this pilot can make.

## 6. Disclosures this pilot carries

- **The outcome w is synthetic.** `w = rho_T * theta + u`, Var(w) = 1. The texts and the
  trait scores are real; no corpus in this project carries an outcome variable. What Layer B
  demonstrates is that **real machine text attenuates or amplifies a correlation exactly as
  (E7) predicts at its realized (g, kappa, delta)**. It does not demonstrate that any real
  survey outcome behaves this way.
- **theta := L**, the binary persona label, standardized by the respondent marginal
  q1 = 0.5170. Layer B normalizes on the human base, so mu_H = 0 and V_H = 1 and Layer A's
  `V_H = 1/rel_H` chain does not apply. `r_H = 0.1828` plays the role `sqrt(rel_H)` plays in
  Layer A.
- **Every Layer A knob that is a Layer B outcome is NaN on the Cell** (`c, kappa, rel_H,
  delta, rho_v, r_F`), and `detector="empirical"` is deliberately not in `dgp.DETECTORS` so
  `Cell.se_sp` raises rather than returning an operating point Layer B never had.
- **k_chunks = 1**, so rel_H is unidentified and rho_T is not recovered. Chunk-level scores
  remain an open dependency on lane 3.
- **`delta` sign** follows CONVENTIONS here and the memo in lane 3's file. Unresolved.
- **The adjusted-count operating point is a held-out split, not an independent calibration
  set.** Both halves are PK essays. A real deployment would calibrate on a different corpus
  and should expect a *larger* specificity transfer gap than the 0.008 measured here, so the
  +33% over-count is a floor on that route's error, not a worst case.

## 7. What this pilot licenses, and what it does not

Licensed by this run:

1. (E7) and (E67) hold on the injected design at real measured (g, kappa, delta), to machine
   precision in the exact arithmetic and within 2.1 MCSE in 400 replicates.
2. Assignment alone, holding the pool fixed, moves Att from 0.895 to 1.135 — attenuation to
   amplification. This is the paper's mechanism claim and it now has real text behind it.
3. The EIV correction recovers rho_H to within 7% when c is known, and most of that residual
   is the prevalence step.
4. Assuming c = 0 when c = c_pool over-corrects rho_H by 22.5% at pi = 0.10.

Not licensed, and the paper must not claim it:

1. **A single n = 1000 survey cannot resolve the matched-vs-random contrast** (z = 0.51).
   Roughly n = 30,700 would, at this pool and pi.
2. **The distribution-match prevalence estimator is not usable as an unbiased pi estimate on
   pools like this one** — it under-counts by 30% relative.
3. **The detector-based prevalence route over-counts by 33% relative** on this cell, 96% of
   it explained by detector-calibration transfer gaps amplified by a denominator of 0.27.
   The two SPEC 3.2 prevalence routes are biased in opposite directions here; nothing in
   this pilot licenses averaging them or treating them as bounds. The *sign and size* of the
   adjusted-count bias is a property of the calibration split, not of the cell -- the same
   cell at another seed reads +0.0070 (`LAYERB-SWEEP.md`).
4. Nothing about rho_T, reliability, or multi-item structure, at k_chunks = 1.
5. Nothing about real survey outcomes: w is synthetic.

## 8. What runs next

1. ~~Ask lane 3 for `detector_p_machine` on `pk_human.json` and for the `g` correction.~~
   **Done, 2026-09-07** (lane 3 FIXES-DONE). Section 5 is rescored above; section 1's `g`
   now matches lane 3's post-fix covariance-form value on all 20 cells to 8.9e-16.
2. Ask lane 3 for chunk-level scores (unblocks rel_H, rho_T, and the multi-item arms).
3. Get a ruling on the `delta` sign between CONVENTIONS and the memo.
4. ~~Extend to the other three pools and the other four traits.~~ **Done** -- see
   `LAYERB-SWEEP.md`, 20 cells at this same design point.

PILOTB-DONE
