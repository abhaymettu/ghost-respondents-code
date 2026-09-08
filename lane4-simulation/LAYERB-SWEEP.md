# Layer B sweep: 4 pools x 5 traits

design-pivot-memo section 8.2 step 3, widened from the single cell in `LAYERB-PILOT.md` to
all 20 labeled pool x trait cells lane 3 measured. Script `sweep_layerb.py`, log
`results/layerb_sweep.log`, machine-readable `results/layerb_sweep.json`. **306s**, one core,
single-threaded, `nice -n 15`, no network, no API calls. The Layer A grid (PID 8258) and
`dgp.py` were not touched.

**9 of 12 checks pass.** Every exact identity and every Monte Carlo recovery check holds in
all 20 cells. The three failures are all in the estimators, all reported as findings:

1. The distribution-match prevalence estimator misses by more than 0.01 in **16 of 20 cells**,
   in **both directions** (-0.089 to +0.220). The pilot's single cell showed a downward bias;
   that direction does not generalize.
2. The EIV correction recovers rho_H within 25% in **59 of 60 cell-arms**; the one failure
   (+38%) is the cell with the smallest signal and a negative g.
3. The adjusted-count prevalence estimator misses by more than 0.01 in **13 of 20 cells**
   (-0.081 to +0.302). The route is **structurally undefined on one of the four pools**, and
   where it is defined its error scales as 1/(detector denominator): +-0.015 at AUC 0.95,
   +-0.08 at AUC 0.78.

## The design point

Identical to the pilot cell, held fixed across all 20 cells so the only thing that varies is
the pool and the trait:

| knob | value |
|---|---|
| n | 1000 |
| pi | 0.10 |
| p (coupling arms) | 0, 0.5, 1 |
| reps | 400 per arm |
| rho_T | 0.5 |
| k_chunks | 1 |
| detector target sp | 0.99 |
| seed | 20260907 + 1000 * cell index |

Each cell gets its **own** held-out 50/50 splits of both pools, so each has its own `r_H`,
`c_pool` and detector operating point. Nothing is pooled across cells. `big5-essays` is
`big5_personality_essays`, `gpt-4` is `personallm_gpt-4-0613`, `gpt-3.5` is
`personallm_gpt-3.5-turbo-0613`, `llama-2` is `personallm_llama-2`.

`big5_personality_essays` is a **human** corpus (the Pennebaker-King essays) standing in the
machine slot. It is kept in the sweep deliberately: it is the negative control for the
detector route, and section 5 is what it buys.

## 1. Realized moments and the attenuation range

| pool | trait | r_H | c_pool | kappa | delta | g | Att(p=0) | Att(p=.5) | Att(p=1) | contrast |
|---|---|---|---|---|---|---|---|---|---|---|
| big5-essays | EXT | +0.1441 | +0.1381 | 0.717 | +0.452 | +0.811 | 0.905 | 0.945 | 0.986 | +0.0059 |
| big5-essays | NEU | +0.0871 | -0.0562 | 0.869 | +0.247 | -0.601 | 0.903 | 0.873 | 0.843 | -0.0026 |
| big5-essays | AGR | +0.0725 | +0.0840 | 0.886 | +0.839 | +1.091 | 0.877 | 0.931 | 0.984 | +0.0039 |
| big5-essays | CON | +0.0893 | +0.1097 | 0.909 | -0.256 | +1.172 | 0.901 | 0.960 | 1.019 | +0.0052 |
| big5-essays | OPE | +0.2368 | -0.0438 | 0.544 | -2.132 | -0.136 | 0.771 | 0.765 | 0.759 | -0.0014 |
| gpt-4 | EXT | +0.1811 | +0.3992 | 0.801 | +0.494 | +1.973 | 0.899 | 0.998 | 1.096 | +0.0178 |
| gpt-4 | NEU | +0.0893 | +0.1171 | 0.909 | +0.392 | +1.250 | 0.898 | 0.960 | 1.023 | +0.0056 |
| gpt-4 | AGR | +0.1214 | +0.2375 | 1.130 | +0.529 | +2.080 | 0.883 | 0.985 | 1.087 | +0.0124 |
| gpt-4 | CON | +0.0565 | +0.0570 | 0.861 | -0.327 | +0.938 | 0.902 | 0.949 | 0.996 | +0.0027 |
| gpt-4 | OPE | +0.2196 | +0.3248 | 0.752 | -2.168 | +1.283 | 0.761 | 0.815 | 0.870 | +0.0119 |
| gpt-3.5 | EXT | +0.1442 | +0.2907 | 0.812 | +0.570 | +1.817 | 0.895 | 0.986 | 1.076 | +0.0130 |
| gpt-3.5 | NEU | +0.1628 | +0.0942 | 0.927 | +0.421 | +0.557 | 0.896 | 0.924 | 0.952 | +0.0045 |
| gpt-3.5 | AGR | +0.1303 | +0.4086 | 0.845 | +0.358 | +2.882 | 0.902 | 1.046 | 1.191 | +0.0188 |
| gpt-3.5 | CON | +0.0631 | +0.0289 | 0.718 | -0.259 | +0.389 | 0.910 | 0.930 | 0.949 | +0.0012 |
| gpt-3.5 | OPE | +0.2337 | +0.0360 | 0.487 | -2.696 | +0.108 | 0.711 | 0.715 | 0.719 | +0.0010 |
| llama-2 | EXT | +0.1707 | +0.1111 | 0.583 | +0.239 | +0.497 | 0.917 | 0.942 | 0.968 | +0.0043 |
| llama-2 | NEU | +0.0823 | +0.0652 | 0.794 | +0.312 | +0.706 | 0.905 | 0.941 | 0.976 | +0.0029 |
| llama-2 | AGR | +0.1294 | +0.2653 | 0.771 | +0.554 | +1.800 | 0.898 | 0.988 | 1.078 | +0.0116 |
| llama-2 | CON | +0.0769 | +0.1476 | 0.644 | +0.516 | +1.540 | 0.905 | 0.983 | 1.060 | +0.0060 |
| llama-2 | OPE | +0.2377 | +0.5048 | 1.273 | -1.618 | +2.395 | 0.801 | 0.907 | 1.014 | +0.0253 |

- **kappa spans 0.487 to 1.273** and **delta spans -2.696 to +0.839**. The pilot cell
  (kappa 0.86, delta 0.54) is not extreme in either direction; the OPE cells are, in all
  four pools, at delta -1.6 to -2.7.
- **g spans -0.601 to +2.882**, and **two cells have g < 0** (big5 NEU and OPE). A negative g
  means the machine texts' label signal runs *against* the human one, so matching machine
  personas to respondent labels makes attenuation **worse**: these are the only two cells
  where Att(1) < Att(0), and the only two with a negative predicted contrast.
- **Att(0) is below 1 in every one of the 20 cells** (0.711 to 0.917). Uncoupled machine
  respondents attenuate, always, at this pi. **Att(1) crosses above 1 in 9 of 20 cells**
  (up to 1.191). Assignment alone, holding the pool and pi fixed, moves a real correlation
  from attenuation to amplification in **45% of the pool-trait combinations lane 3 measured**.
  This is the paper's mechanism claim, and it now rests on 20 cells rather than 1.
- The largest single swing is gpt-3.5/AGR: Att 0.902 -> 1.191, a 32% move in the observed
  correlation from assignment alone.

### The identities

| check | result |
|---|---|
| (E7) closed form == direct mixture correlation, every cell and arm | PASS, max 2.78e-17 |
| (E67) c(p) = p * c_pool exactly, every cell | PASS, max dev 5.76e-16 |
| (E67) kappa, delta invariant in p, every cell | PASS, max dev 2.66e-15 / 4.44e-16 |
| g by (E66) covariance ratio == g by label-mean-difference ratio | PASS, worst cell 0.0% |
| held-out references disjoint from injection pools, every cell | PASS, 20 cells |
| without-replacement capacity holds, every cell and arm | PASS, worst demand 53.1 of 80 |
| every realized moment within 4 MCSE of its closed form | PASS, max abs z = 3.17 over 300 z-scores |
| observed matched-vs-random contrast agrees with (E7), every cell | PASS, max 2.19 MCSE |

The 300 z-scores are 20 cells x 3 arms x 5 quantities (c, kappa, delta, rho_obs, Att), 400
replicates each. One value at 3.17 out of 300 is what a correct implementation looks like.

`g` matching lane 3's post-fix column to 8.9e-16 on all 20 cells is checked separately, in
`inject/test_inject.py::test_lane3_moments_match` (61/61).

## 2. Estimator recovery, per cell

Errors are relative to each cell's own `rho_H_true = rho_T * r_H`. The last column is the n a
**single** survey would need for the matched-vs-random contrast to reach z = 2.8.

| pool | trait | pi-hat dm | bias | pi-hat ac | bias | rho_H err p=0 | p=0.5 | p=1 | c=0 err at p=1 | n for z=2.8 |
|---|---|---|---|---|---|---|---|---|---|---|
| big5-essays | EXT | 0.1343 | +0.0343 | 0.0354 | -0.0646 | +6.2% | +5.1% | +0.2% | +13.7% | 416964 |
| big5-essays | NEU | 0.2422 | +0.1422 | 0.1731 | +0.0731 | +17.3% | +21.6% | +38.2% | +9.0% | n/a |
| big5-essays | AGR | 0.1367 | +0.0367 | 0.1396 | +0.0396 | +6.8% | +2.9% | -0.6% | +15.5% | 1021064 |
| big5-essays | CON | 0.0925 | -0.0075 | 0.4022 | +0.3022 | +5.5% | +1.1% | -5.6% | +6.7% | 544360 |
| big5-essays | OPE | 0.1092 | +0.0092 | 0.0573 | -0.0427 | +1.5% | +1.4% | +1.6% | -0.2% | n/a |
| gpt-4 | EXT | 0.0927 | -0.0073 | 0.1070 | +0.0070 | +1.8% | -2.5% | +0.8% | +21.5% | 47719 |
| gpt-4 | NEU | 0.2364 | +0.1364 | 0.1166 | +0.0166 | +11.9% | +8.1% | -0.5% | +34.9% | 477332 |
| gpt-4 | AGR | 0.1487 | +0.0487 | 0.0759 | -0.0241 | +7.7% | -2.7% | -0.2% | +37.1% | 93521 |
| gpt-4 | CON | 0.1766 | +0.0766 | 0.0716 | -0.0284 | +3.1% | -4.5% | -15.4% | +2.2% | 2258548 |
| gpt-4 | OPE | 0.1010 | +0.0010 | 0.1006 | +0.0006 | -0.3% | -0.9% | -4.8% | +10.8% | 109455 |
| gpt-3.5 | EXT | 0.0704 | -0.0296 | 0.1070 | +0.0070 | -2.2% | -2.7% | +5.4% | +19.2% | 97273 |
| gpt-3.5 | NEU | 0.0271 | -0.0729 | 0.0754 | -0.0246 | -11.1% | -5.0% | -2.7% | -1.4% | 623938 |
| gpt-3.5 | AGR | 0.1115 | +0.0115 | 0.0189 | -0.0811 | +0.1% | -0.5% | -0.3% | +32.3% | 44135 |
| gpt-3.5 | CON | 0.2141 | +0.1141 | 0.0421 | -0.0579 | +6.7% | +8.5% | +7.9% | +20.3% | 10057981 |
| gpt-3.5 | OPE | 0.0794 | -0.0206 | 0.1088 | +0.0088 | -7.9% | -8.4% | -11.7% | -10.9% | 15224778 |
| llama-2 | EXT | 0.3195 | +0.2195 | 0.1151 | +0.0151 | +21.2% | +15.8% | +6.5% | +29.6% | 842528 |
| llama-2 | NEU | 0.0589 | -0.0411 | 0.0959 | -0.0041 | -7.4% | -1.4% | -1.4% | +4.8% | 1843606 |
| llama-2 | AGR | 0.0292 | -0.0708 | 0.0931 | -0.0069 | -7.1% | -2.9% | +5.0% | +9.9% | 124108 |
| llama-2 | CON | 0.0109 | -0.0891 | 0.0881 | -0.0119 | -5.6% | -3.8% | +10.4% | +12.9% | 461937 |
| llama-2 | OPE | 0.1210 | +0.0210 | 0.0925 | -0.0075 | +2.6% | +1.5% | -0.7% | +29.9% | 23128 |

`n/a` marks the two negative-contrast cells, where matching decreases the observed
correlation and the one-survey power question does not have a positive answer.

## 3. The distribution-match prevalence estimator fails in both directions

**FAIL, 16 of 20 cells** outside a 0.01 tolerance (and beyond 2.8 MCSE; per-cell MCSE runs
0.0003 to 0.0042). Bias range **-0.0891 to +0.2195**, median absolute bias **0.0389** against
a true pi of 0.10.

The pilot reported this estimator as **biased low** (-0.0295) and attributed it to
distribution overlap. **The sweep does not support the direction.** Only 4 of 20 cells land
within 0.01 (big5/CON, big5/OPE, gpt-4/EXT, gpt-4/OPE), and the errors are signed both ways
with no relationship to the overlap statistics: correlation with kappa is 0.011, with
|delta| it is -0.243. llama-2/EXT reads pi = 0.32 against a truth of 0.10; llama-2/CON reads
0.011.

What survives from the pilot is the weaker and more useful claim: **the Hellinger
grid-search prevalence estimator is not usable as a point estimate of pi on real score
distributions**, with errors of the same order as pi itself. The pilot's specific mechanism
story (overlap pulls the mixture weight toward 0) is a description of one cell, not a law,
and should not go in the paper as one.

## 4. The EIV correction holds, and assuming c = 0 does not

**59 of 60 cell-arms recover rho_H within 25%**, median absolute error **4.7%**. The single
failure is **big5/NEU at p = 1, +38.2%** -- the cell with the second-smallest `r_H` (0.0725
is smaller, but big5/NEU's 0.0871 pairs with a negative g of -0.601), so the target rho_H is
0.0436 and a small absolute error is a large relative one. It is the same cell the prevalence
estimator misses by +0.142, and the EIV chain inherits that.

**Assuming c = 0 when c = c_pool is worse than knowing c in 15 of 20 cells at p = 1**, by up
to **+37.1%** (gpt-4/AGR). The size of the penalty tracks `g`: correlation between g and the
c = 0 error is **0.614**, and every cell with g > 1.5 pays between +9.9% and +37.1%. SPEC 3.2
assumes c = 0. On coupled machine respondents that assumption **overstates the human
correlation**, and the sweep bounds how much: roughly +10% to +37% at pi = 0.10 wherever the
pool has a real label signal.

## 5. The detector route, and a pool where it is undefined

**FAIL, 13 of 20 cells** outside a 0.01 tolerance, bias range **-0.0811 to +0.3022**.

| pool | detector AUC vs PK | se at sp=0.99 | denominator se-(1-sp) | mean abs adj-count bias | route |
|---|---|---|---|---|---|
| llama-2 | 0.939-0.966 | 0.562-0.637 | +0.552-+0.627 | 0.0091 | usable to +-0.015 |
| gpt-4 | 0.836-0.858 | 0.219-0.269 | +0.208-+0.258 | 0.0153 | degraded |
| gpt-3.5 | 0.775-0.796 | 0.100-0.119 | +0.089-+0.108 | 0.0359 | unusable (+-0.08) |
| big5-essays | 0.444-0.493 | 0.000-0.000 | -0.011--0.011 | 0.1044 | undefined (negative denominator) |

Detector quality separates cleanly by pool, and the adjusted count's usable range follows it:

- **llama-2** (AUC 0.94-0.97, se 0.56-0.64 at sp = 0.99): every cell within +-0.015 of pi.
- **gpt-4** (AUC 0.84-0.86, se 0.22-0.27): within +-0.028.
- **gpt-3.5** (AUC 0.78-0.80, se 0.10-0.12): up to **-0.081**, i.e. the estimate reads
  pi = 0.019 where the truth is 0.10.
- **big5-essays** (AUC 0.44-0.48, se = **0.000**): the route has no meaning at all.

The mechanism is the denominator `se - (1 - sp)`. It is 0.55-0.63 for llama-2, 0.21-0.26 for
gpt-4, and 0.089-0.108 for gpt-3.5, and every calibration error is divided by it. Across the
15 machine cells, correlation between 1/denominator and absolute bias is **0.534**, and the
per-pool mean absolute bias ranks exactly with it: 0.0091, 0.0153, 0.0359.

### The defect: a negative denominator returns a number instead of raising

big5-essays is human text. The detector reads it at chance (lane 3's own
`detector_auc_vs_pk` = 0.4724, matching the 0.444-0.479 measured here on the reference
halves), so at a 0.99-specificity threshold **se = 0.000 exactly in all five traits** and the
denominator is `0.000 - 0.0105 = -0.0105`, **negative**.

`estimators._adjusted_count_pi` guards `abs(denom) < 1e-8` and returns `(nan, False)` there,
but a negative denominator passes that guard. The division then runs, the result is clipped
to `[0, 1]`, and the caller gets a finite, plausible-looking number that is **monotonically
decreasing in the flag rate**: big5/CON returns **pi = 0.4022** and big5/EXT returns
**0.0354**, both from the same true pi = 0.10 and the same broken operating point.

This is why the sweep's "adjusted-count branch scored" check **passes on all 20 cells and the
pass is partly vacuous**. The check is reported honestly here rather than tightened after the
fact. **The recommendation for SPEC 3.2 is to guard `denom <= tol`, not `abs(denom) < tol`,
and to return `(nan, False)` when the detector does not separate.** No change was made to
`estimators.py` in this run; the sweep was not scoped to edit the estimator.

### What drives the error where the route is defined

Writing the realized flag rate as `pi * se_inj + (1 - pi) * (1 - sp_base)` and inverting it
with the reference halves' `(se_cal, sp_cal)` gives the bias in closed form:

```
bias = [ pi * (se_inj - se_cal) + (1 - pi) * ((1 - sp_base) - (1 - sp_cal)) ] / (se_cal - (1 - sp_cal))
```

| pool | trait | se term | fpr term | predicted bias | observed bias |
|---|---|---|---|---|---|
| gpt-4 | EXT | +0.0138 | -0.0065 | +0.0073 | +0.0070 |
| gpt-4 | NEU | +0.0300 | -0.0140 | +0.0160 | +0.0166 |
| gpt-4 | AGR | -0.0099 | -0.0145 | -0.0244 | -0.0241 |
| gpt-4 | CON | -0.0145 | -0.0141 | -0.0286 | -0.0284 |
| gpt-4 | OPE | +0.0000 | -0.0000 | -0.0000 | +0.0006 |
| gpt-3.5 | EXT | -0.0116 | +0.0201 | +0.0086 | +0.0070 |
| gpt-3.5 | NEU | +0.0070 | -0.0325 | -0.0256 | -0.0246 |
| gpt-3.5 | AGR | -0.0326 | -0.0533 | -0.0860 | -0.0811 |
| gpt-3.5 | CON | -0.0196 | -0.0380 | -0.0576 | -0.0579 |
| gpt-3.5 | OPE | +0.0210 | -0.0082 | +0.0127 | +0.0088 |
| llama-2 | EXT | +0.0144 | +0.0013 | +0.0157 | +0.0151 |
| llama-2 | NEU | +0.0079 | -0.0119 | -0.0040 | -0.0041 |
| llama-2 | AGR | -0.0080 | +0.0000 | -0.0080 | -0.0069 |
| llama-2 | CON | -0.0071 | -0.0047 | -0.0119 | -0.0119 |
| llama-2 | OPE | -0.0060 | -0.0012 | -0.0072 | -0.0075 |

**This explains 99.6% of the variance in the adjusted-count bias across the 15 machine
cells** (correlation 0.9989, maximum residual 0.0049, mean 0.0010). The route's entire error
at pi = 0.10 is calibration transfer -- how well the held-out halves' operating point
describes the halves the survey actually draws from -- divided by the denominator. It is not
an injection artifact and not Monte Carlo noise.

The consequence for the pilot is direct: `LAYERB-PILOT.md` reports **+0.0329** for gpt-4/EXT
and this sweep reports **+0.0070** for the same cell at a different seed. Same pool, same
trait, same pi, same 400 reps; only the random calibration half differs. **The adjusted-count
bias is a draw from a distribution over calibration splits, not a property of a cell**, and a
single number for it should not be quoted without that spread.

## 6. What one survey can resolve

The matched-vs-random contrast is a design-level effect at every cell, not a per-survey one.
At n = 1000 the z-score of the contrast in a **single** replicate runs **0.023 to 0.582**
across the 18 cells with a positive contrast. The n a single survey would need for z = 2.8:

- best case **23,128** (llama-2/OPE, contrast +0.0253)
- median **469,634**
- worst case **15,224,778** (gpt-3.5/CON, contrast +0.0012)

The pilot's cell needed ~30,700. **It is near the optimistic end of the range, not typical.**
Over 400 replicates the contrast is resolved cleanly in every cell (the (E7) agreement check
passes at max 2.19 MCSE), which is what makes it a claim about the design rather than about
any one fielded survey.

## 7. Disclosures this sweep carries

Everything in `LAYERB-PILOT.md` section 6 applies unchanged to all 20 cells. Additionally:

- **`big5_personality_essays` is human text in the machine slot.** Its coupling, kappa, delta
  and g are real measurements and its rows in sections 1-4 are valid; its rows in section 5
  are a negative control, not a detector result.
- **Each cell has its own held-out split**, so `r_H` here (0.0565-0.2377) is the split-half
  value, not lane 3's whole-pool value (0.0694-0.2267). Both are in the JSON per cell
  (`r_H` and `r_H_lane3_fullpool`).
- **The detector operating point is a held-out split of the same corpus**, not an independent
  calibration set, in every cell. A real deployment calibrates on a different corpus and
  should expect larger transfer gaps than the ones measured here, so section 5's error bars
  are a floor.
- **k_chunks = 1**, so rel_H is unidentified and **rho_T is not recovered in any cell**. The
  sweep stops at rho_H, exactly as the pilot does. Chunk-level scores exist in lane 3's files
  for the labeled pools (k = 4, loaded and tested), but not for pk_human, so the multi-item
  arms remain blocked on lane 3.
- **`delta` sign** follows CONVENTIONS; lane 3's memo-sign value is carried per cell in the
  JSON as `delta_lane3_memo_sign`. Still unresolved.
- **w is synthetic** in every cell.

## 8. What this sweep licenses

Licensed:

1. (E7) and (E67) hold on the injected design at 20 independently measured (g, kappa, delta)
   triples, to machine precision exactly and within 3.17 MCSE over 300 Monte Carlo z-scores.
2. **Uncoupled machine respondents attenuate in 20 of 20 cells** (Att(0) 0.711-0.917), and
   **assignment alone pushes Att above 1 in 9 of 20** (up to 1.191).
3. **A negative g reverses the sign of the assignment effect** (big5 NEU, OPE): matching
   deepens attenuation instead of relieving it. The design predicts this and the Monte Carlo
   confirms it.
4. The EIV correction recovers rho_H within 25% in 59 of 60 cell-arms, median error 4.7%.
5. **Assuming c = 0 overstates rho_H by +10% to +37% wherever g > 1.5**, at pi = 0.10.
6. The adjusted-count prevalence error is 99.6%-explained by detector-calibration transfer
   divided by `se - (1 - sp)`, and its usable range is set by detector AUC.

Not licensed, and the paper must not claim it:

1. **The distribution-match prevalence estimator is not a usable point estimate of pi**, and
   its error has no reliable sign: 16 of 20 cells miss by more than 0.01, from -0.089 to
   +0.220.
2. **No single adjusted-count bias number.** It moves by 0.026 on the calibration split alone
   for one fixed cell.
3. **A single n = 1000 survey cannot resolve the matched-vs-random contrast in any cell**
   (best single-replicate z = 0.58, requiring n >= 23,128).
4. Nothing about rho_T, reliability, or multi-item structure, at k_chunks = 1.
5. Nothing about real survey outcomes.
6. Nothing about pi other than 0.10, or n other than 1000. The sweep varies the pool and the
   trait; it holds the design point fixed by construction.

## 9. What runs next

1. **Guard the negative denominator in `estimators._adjusted_count_pi`** (section 5). One
   comparison; it currently returns a clipped number where it should return `(nan, False)`.
2. **Repeat the adjusted-count calibration over many random splits** of one cell to
   characterise the spread in section 5, rather than quoting a single split's number.
3. Ask lane 3 for **chunk-level scores on pk_human**, the last dependency blocking rel_H,
   rho_T, and every multi-item arm.
4. Get a ruling on the **`delta` sign** between CONVENTIONS and the memo.
5. Sweep **pi and n**, now that the pool x trait dimension is characterised at one design
   point. The 306s runtime for 20 cells means a (pi, n) grid over these same cells is a
   minutes-scale job, not a grid submission.

SWEEP-DONE
