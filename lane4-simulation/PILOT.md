# Lane 4 pilot cell

Verification pass 2's first data point (SPEC section 7): one cell, run end to end, closed forms checked against Monte Carlo output, and measured per-fit runtime extrapolated to the full grid.

## (a) Cell definition and derived scale quantities

| field | value |
|---|---|
| pi | 0.1000 |
| c | 0.0000 |
| n | 1000 |
| detector | oracle |
| kappa | 0.5000 |
| rho_v | 0.0000 |
| rel_H | 0.7000 |
| delta | 0.0000 |
| rho_T | 0.5000 |
| k | 4 |
| r_F | 0.3000 |
| d_theta | 0.0000 |
| arm | pilot |
| V_H (derived) | 1.4286 |
| s2_H (derived) | 0.4286 |
| s2_M (derived) | 0.7143 |
| Delta (derived) | 0.0000 |
| mu_M (derived) | -0.0000 |
| b (derived) | 0.5000 |
| s2_u (derived) | 0.7500 |
| lam_M (derived) | 0.0000 |
| s2_v (derived) | 0.7143 |
| rho_H (derived) | 0.4183 |
| loading (derived) | 0.8367 |
| se, sp (detector=oracle) | 1.0, 1.0 |

## (b) Seed, reps, environment, reproduce command

| field | value |
|---|---|
| master_seed | 20260907 |
| reps | 500 |
| python | 3.12.13 |
| numpy | 2.5.3 |
| scipy | 1.18.1 |
| scikit-learn | 1.9.0 |
| platform | macOS-26.5.2-arm64-arm-64bit |
| cpu_count | 12 |
| command | `.venv/bin/python run_pilot.py --reps 500 --seed 20260907` |

## (c) Population moments vs. empirical Monte Carlo (closed-form check)

| quantity | population (closed form) | empirical MC | MCSE | pass/fail |
|---|---|---|---|---|
| r_obs (E26) | 0.6632 | 0.6622 | 0.0007 | PASS |
| naive rho_H vs population rho_obs | 0.3863 | 0.3854 | 0.0013 | PASS |
| naive rho_T vs population rho_obs / sqrt(r_obs) [E26] | 0.4743 | 0.4736 | 0.0015 | PASS |

**3/3 closed forms PASS at this pilot cell.**

Full `population_moments(cell)`:

```json
{
  "rho_H": 0.4183300132670378,
  "rho_T": 0.5,
  "att": 0.9233805168766387,
  "rho_obs": 0.38627778387552847,
  "r_obs": 0.6631578947368421,
  "pi_prime": 0.0,
  "rho_H_pass": 0.4183300132670378,
  "q": 1.0,
  "tau": -Infinity,
  "lam": 0.0,
  "psi": 0.0
}
```

## (d) Per-estimator results, rho_H and rho_T

| estimator | target | bias | MCSE(bias) | RMSE | coverage | mean CI width | failure rate |
|---|---|---|---|---|---|---|---|
| delete | rho_H | -0.0009 | 0.0012 | 0.0277 | 0.9440 | 0.1079 | 0.0000 |
| delete | rho_T | -0.0009 | 0.0014 | 0.0319 | 0.9580 | 0.1291 | 0.0000 |
| em | rho_H | -0.0339 | 0.0019 | 0.0543 | 0.7263 | 0.1227 | 0.0280 |
| em | rho_T | -0.0273 | 0.0022 | 0.0551 | 0.8251 | 0.1451 | 0.0280 |
| labelfree | rho_H | 0.0605 | 0.0023 | 0.0794 | 0.5040 | 0.1858 | 0.0000 |
| labelfree | rho_T | 0.0473 | 0.0022 | 0.0674 | 0.6440 | 0.1744 | 0.0000 |
| naive | rho_H | -0.0329 | 0.0013 | 0.0432 | 0.7620 | 0.1055 | 0.0000 |
| naive | rho_T | -0.0264 | 0.0015 | 0.0421 | 0.8760 | 0.1297 | 0.0000 |
| simex | rho_H | -0.0009 | 0.0012 | 0.0277 | n/a | n/a | 0.0000 |
| simex | rho_T | -0.0009 | 0.0014 | 0.0319 | n/a | n/a | 0.0000 |

## (e) Runtime per fit and extrapolated core-hours

| estimator | mean seconds/fit | of which resampling | resample share | total seconds (this pilot) | n fits |
|---|---|---|---|---|---|
| delete | 0.00011 | does not resample | n/a | 0.053 | 500 |
| em | 1.34162 | 0.89342 | 66.6% | 670.811 | 500 |
| labelfree | 0.29486 | does not resample | n/a | 147.431 | 500 |
| naive | 0.00012 | does not resample | n/a | 0.059 | 500 |
| simex | 0.00862 | 0.00862 | 99.9% | 4.312 | 500 |

Wall clock for this pilot cell (all estimators, 500 reps): 822.93s

**Reading the resample column.** `Fit.seconds_resample` is the time inside a fit spent on resampling rather than on the point estimate: EM's parametric bootstrap (`B_boot`) and SIMEX's remeasurement Monte Carlo (`B` draws per lambda). It is the part of the grid's cost that can be bought back by lowering B, so it is reported separately from total fit time. Two asymmetries to keep in mind:

- **EM** has a genuinely cheap point estimate; essentially all of its remaining cost is the interval. Cutting `B_boot` cuts EM's cost almost proportionally, at the price of the CI.
- **SIMEX** shows a ~100% share, but that is not the same claim. SIMEX's point estimate *is* a Monte Carlo (B remeasurement draws at each lambda, then an extrapolation); there is no cheaper non-resampling core to fall back to. Lowering its B degrades the point estimate, not just an interval.

### Extrapolated core-hours at 12 workers

Base grid (216 cells x 500 reps):

| estimator | core-hours |
|---|---|
| naive | 0.00 |
| delete | 0.00 |
| simex | 0.26 |
| labelfree | 8.85 |
| em | 40.25 |
| **total** | **49.36** (wall-clock 4.11h at 12 workers) |

Full arm set (381 cells x 500 reps):

| estimator | core-hours |
|---|---|
| naive | 0.01 |
| delete | 0.01 |
| simex | 0.46 |
| labelfree | 15.60 |
| em | 70.99 |
| **total** | **87.07** (wall-clock 7.26h at 12 workers) |

## (f) Pre-registered success flags (SPEC 4.4)

`None` means SPEC's applicability condition does not hold at this cell, never "failed". `beats_deletion` is None for every estimator because it is only defined at the calibrated/degraded detectors and this cell is oracle.

| flag | estimator | rho_H | rho_T |
|---|---|---|---|
| corrected_bias_ok | delete | True | True |
| corrected_bias_ok | em | False | False |
| corrected_bias_ok | labelfree | False | False |
| corrected_bias_ok | simex | True | True |
| coverage_ok | delete | True | True |
| coverage_ok | em | False | False |
| coverage_ok | labelfree | False | False |
| coverage_ok | naive | False | False |
| coverage_ok | simex | n/a | n/a |
| beats_deletion | em | n/a | n/a |
| beats_deletion | labelfree | n/a | n/a |
| beats_deletion | simex | n/a | n/a |
| pi_err_ok | delete | n/a | (not target-specific) |
| pi_err_ok | em | False | (not target-specific) |
| pi_err_ok | labelfree | False | (not target-specific) |
| pi_err_ok | naive | n/a | (not target-specific) |
| pi_err_ok | simex | n/a | (not target-specific) |

**Read this cell as a null result for the corrections, not as evidence against them.** The detector is oracle, so `delete` simply removes every machine row and is essentially unbiased (-0.0009); no correction can beat that, and none is supposed to. `em` (-0.0339) and `naive` (-0.0329) are biased low by almost exactly the same amount, and `labelfree` is biased the other way (+0.0605) and worse than naive. The regime where the corrections are meant to earn their keep is precisely the one this cell excludes: an imperfect detector, where deletion is not available as a clean fallback. Nothing here supports a claim that any correction works, and nothing here refutes one.

## (g) What this pilot does NOT establish

- **SIMEX is exactly `delete` at this cell, so its row above says nothing about SIMEX.** The pilot detector is `oracle` (se=sp=1), so the misclassification matrix Pi is the identity and Pi^lambda = I for every lambda; every lambda point is the same complete-case estimate and the extrapolation is flat. Measured difference between the simex and delete rho_H point estimates at this cell: 5.0e-16 (max over the first 5 reps of the frozen seed). This is correct behavior -- with no misclassification there is nothing to extrapolate away -- but it means SIMEX is untested here and contributes only runtime. SIMEX's behavior is only informative at the calibrated/degraded detectors.
- **rho_T intervals omit a variance term, but that is NOT what drives coverage here.** `_ci_T_from_H` forms the rho_T interval by scaling the rho_H endpoints by 1/sqrt(rel_hat), treating `rel_hat` as a known constant; it does not propagate `rel_hat`'s own sampling error, so every rho_T interval is narrower than a correctly-propagated one. The prediction that this would show up as rho_T undercoverage is NOT borne out at this cell: measured rho_T coverage is *higher* than rho_H coverage for every estimator (delete .958 vs .944, naive .876 vs .762, em .825 vs .726, labelfree .644 vs .504). Two effects run the other way and dominate -- the 1/sqrt(rel_hat) scaling with rel_hat < 1 widens the interval in absolute terms, and coverage at this cell is driven by bias rather than by width. The missing variance term is real and should be fixed before the paper reports rho_T intervals, but it is not the binding term in these numbers.
- **SIMEX reports no interval at all** (`coverage` and `mean CI width` are n/a): `fit_simex` defaults to `B_boot=0`, so it returns a point estimate only. Its `coverage_ok` flag is therefore None, not a pass.
- **EM's bootstrap is warm-started from the fitted model** (single start, initialized at the fitted parameters rather than re-searching with multi-start k-means++). This is legitimate for a parametric bootstrap -- the bootstrap data is drawn from that very model -- and it is what makes EM affordable (19.8s -> 1.35s per fit). It also means the interval reflects sampling variability only, not the variability a real multi-start fit contributes when optimization fails.
- **`_extrapolate`'s linear fallback clips to [-1, 1]** and can therefore report a correlation of exactly +/-1 rather than flagging the extrapolation as out of range. Untriggered at this cell (the extrapolation is flat here), but live for the grid's non-oracle detectors.
- **SIMEX's validity check admits `rel` in [-1, 1]** where a reliability belongs in [0, 1]. A negative `rel_hat` would pass the check and then propagate into `rho_T_hat = rho_H_hat / sqrt(rel_hat)` as a NaN. Not triggered at this cell.
- One cell only: pi=0.10, c=0, n=1000, kappa=0.5, rho_v=0, delta=0, d_theta=0.
- One detector: oracle (se=1, sp=1). The calibrated/degraded operating points that SPEC 4.4's beats_deletion threshold actually needs are untested here.
- c=0 only: every coupling-dependent closed form (att, r_obs's c^2 term, the sign-flip thresholds) is untested at c > 0.
- Runtime is measured on one machine, one process, with reps possibly far below 500 (see --reps); extrapolation assumes per-fit cost does not depend on cell parameters, which is untested.
- No estimator convergence-failure behavior observed if this pilot's stub/real estimators never fail at this easy (oracle, c=0) cell.
