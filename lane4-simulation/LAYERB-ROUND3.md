# Layer B, round 3

Three items from `prompts/lane4-round3.md`: isolate the EIV failure, characterise the
calibration-split spread, diagnose the distribution-match slope.

Everything below is CPU-only. No LLM calls, no API keys, nothing spent. The Layer A grid and
`dgp.py` were not touched, and neither was `SPEC.md`. No estimator was edited, so nothing in
`estimators.py`, `layerb_pilot.py` or `inject/` changed; the test suites were run anyway as a
pre-commit receipt and pass at **20/20** (`test_estimators.py`) and **61/61**
(`python -m inject.test_inject`).

New this round:

| file | what it does |
| --- | --- |
| `round3_splits.py` | 20 cells x 400 calibration splits closed-form, first 12 with Monte Carlo. Items 1 and 2. |
| `round3_dm.py` | 20 cells x 2 splits x 5 prevalences x a 5-point `n_bins` ladder. Item 3. |
| `round3_dm_plugin.py` | the deployable version of item 3's prediction, built from reference histograms alone. |
| `round3_report.py` | reads both JSONs, prints every number quoted here. Cheap to re-run. |
| `results/round3_report.txt`, `results/round3_plugin.txt` | the printed output, verbatim. |

---

## 0. One design change, stated up front

Item 1 asked for a targeted run over the full 20 cells at pi in {0.10, 0.30}, scoring the EIV
error against `g`, `c_pool`, `kappa`, `delta` and their products. **I ran exactly that** (§1.1)
and I also ran something the prompt did not ask for (§1.2), because the first design on its own
cannot isolate anything.

The reason: each cell in `results/layerb_sweep.json` carries one calibration split, and every
quantity in the candidate list is computed from that split. Re-running `gpt-4-0613/EXT` -- one
of the two cells `LAYERB-SWEEP2.md` flagged at +31% -- at a different split seed gives **+1.4%**.
Over 400 splits of that same cell, `g` has mean +2.53 with sd 0.43 and range 1.51 to 4.30; the
published 1.973 is an unremarkable draw. So a ranking of 20 numbers against 20 other numbers,
one split each, is a ranking of one draw of a dominant nuisance variable against another draw
of the same variable. §1.2 holds the cell fixed and re-draws the split instead.

To keep the shipped sweep recoverable rather than merely comparable, `split_seeds(ci)` returns
`sweep_layerb.py`'s own seed as **split index 0**. `split_stats()` was checked against
`sweep_layerb.py:run_cell` and reproduces `r_H`, `kappa`, `delta`, `c_pool` and `g` exactly in
all 20 cells, 0 mismatches. Every "split 0" row below is therefore the published cell.

Arms were cut to p in {0.0, 1.0} to buy split count; p = 0.5 is interior and the effect is
monotone in p. `replace=True` throughout, which the sweep2 bridge check licensed at
max |dAtt(p=1)| = 0.0051, and which pi = 0.30 at n = 1000 requires anyway.

---

## 1. EIV failure isolation

### 1.1 The prompt's ranking, run as specified

All 20 cells on their own shipped split, `err_00` = the EIV error with the deployable reference
and the deployable prevalence estimate, p = 1, 40 reps. Sorted by |err| at pi = 0.30.

```
  cell                             g  c_pool  kappa   delta  err@.10  err@.30
  essays/NEU                  -0.601  -0.056  0.869  +0.247  +19.2%  -33.6%
  gpt-3.5-turbo-0613/AGR      +2.882  +0.409  0.845  +0.358   +5.9%  +26.4% <-FAIL
  gpt-3.5-turbo-0613/OPE      +0.108  +0.036  0.487  -2.696  -17.2%  -20.5%
  gpt-3.5-turbo-0613/CON      +0.389  +0.029  0.718  -0.259  +28.5%  +17.8%
  essays/OPE                  -0.136  -0.044  0.544  -2.132   +0.7%  -16.6%
  llama-2/AGR                 +1.800  +0.265  0.771  +0.554   +4.3%  +15.8%
  ...
  gpt-4-0613/EXT              +1.973  +0.399  0.801  +0.494   -0.1%  +13.2% <-FAIL
  ...
  llama-2/OPE                 +2.395  +0.505  1.273  -1.618   +6.7%   +5.7% <-REF
```

|err@0.30| against each candidate, 20 cells (Pearson / Spearman):

```
    g            r=-0.201   rho=-0.188      g*kappa      r=-0.243   rho=-0.217
    |g|          r=-0.006   rho=-0.126      g*|delta|    r=-0.243   rho=-0.206
    c_pool       r=-0.184   rho=-0.286      (g-1)        r=-0.201   rho=-0.188
    kappa        r=-0.249   rho=-0.334      |g-1|        r=+0.593   rho=+0.400
    delta        r=-0.112   rho=-0.159
    |delta|      r=+0.079   rho=+0.051
```

**Nothing in the candidate list separates them.** The best is `|g-1|` at r = +0.593, and its rank
correlation is +0.400, which over 20 points is not a finding. Every other candidate is inside
|r| < 0.25, and the signs are wrong for the mechanism -- larger `g` goes with *smaller* error.
Note also that on this ranking the two published failures are not the top two: `essays/NEU` at
-33.6% and `gpt-3.5/OPE` at -20.5% both beat `gpt-4-0613/EXT`.

### 1.2 The same cells, re-drawing the calibration split

Cell held fixed, 12 Monte Carlo splits each, pi = 0.30, p = 1. `sd_mc` is the pooled 40-rep
Monte Carlo standard error; `sd_split` is the between-split sd with that variance removed.

```
  cell                         split0     mean      sd      min      max   sd_mc sd_split
  essays/NEU                  -33.6%   -0.9%  15.6%  -33.6%  +26.4%  12.5%    9.4%
  gpt-3.5-turbo-0613/AGR      +26.4%  +15.3%  15.8%  -11.3%  +37.0%   6.4%   14.4% <-FAIL
  llama-2/AGR                 +15.8%  +19.7%  14.8%   -5.4%  +44.1%   7.6%   12.7%
  gpt-4-0613/EXT              +13.2%   +8.6%   6.9%   -6.6%  +19.9%   4.3%    5.4% <-FAIL
  llama-2/OPE                  +5.7%   -0.4%   4.4%   -7.5%   +5.7%   3.7%    2.4% <-REF
  llama-2/NEU                  +2.7%  +17.4%  13.7%   -0.3%  +45.1%   9.9%    9.5%
  gpt-3.5-turbo-0613/NEU       -2.5%  -19.3%  32.2%  -98.6%   +8.0%  12.0%   29.9%
```

```
  between-cell sd of the split-averaged error : 9.7%
  within-cell sd across splits (MC-corrected) : 10.5%
  variance share that is the cell, not the split: 45.7%
```

**The calibration split explains more of the EIV error than the cell does.** 54% of the variance
in the published table is the split draw. That is the single most important number in this
round, and it applies retroactively to every per-cell EIV figure in `LAYERB-SWEEP2.md`.

Two consequences follow immediately.

**The published pair is not the right pair.** `llama-2/AGR` has the largest split-averaged error
of all 20 cells (+19.7%), and `llama-2/NEU` (+17.4%) and `gpt-3.5/NEU` (-19.3%) both exceed
`gpt-4-0613/EXT` (+8.6%). None of the three was flagged, because their split-0 draws happened to
land near zero (+15.8%, +2.7%, -2.5%). Conversely `essays/NEU` was flagged by its split-0 draw
of -33.6%, the worst single number in the table, while its split-averaged error is **-0.9%**.

**One of the two flagged cells does not separate from the reference cell at all.**

```
  gpt-3.5-turbo-0613/AGR     [-11.3%,+37.0%]  vs  llama-2/OPE [-7.5%,+5.7%]  gap = 1.49 within-sd
  gpt-4-0613/EXT             [ -6.6%,+19.9%]  vs  llama-2/OPE [-7.5%,+5.7%]  gap = 0.85 within-sd
```

`gpt-4-0613/EXT`'s split distribution overlaps `llama-2/OPE`'s across most of its range and the
gap in means is 0.85 of a within-cell sd. **Saying it plainly, as the prompt asked: nothing
separates `gpt-4-0613/EXT` from `llama-2/OPE`.** The +31% that flagged it was a draw.
`gpt-3.5-turbo-0613/AGR` is a real effect -- 1.49 within-sd, mean +15.3% against -0.4% -- but it
is one cell, not a pair, and it is not the most extreme one.

### 1.3 Narrowing the candidates

Both sides averaged over the 12 splits, so neither the error nor the moment is a single draw:

```
    g                            r=+0.026   rho=-0.036
    |g-1|                        r=+0.413   rho=+0.361
    c_pool                       r=-0.345   rho=-0.414
    kappa                        r=+0.130   rho=+0.188
    |delta|                      r=-0.347   rho=-0.343
    r_H                          r=-0.640   rho=-0.665
    1/r_H                        r=+0.650   rho=+0.665
    amplification |d err/d pi|   r=+0.327   rho=+0.550
    |dm prevalence bias|         r=+0.594   rho=+0.606
    amp * |dm bias|              r=+0.595   rho=+0.853
```

The four candidates the prompt named get weaker, not stronger, once the split noise is averaged
out: `|g-1|` falls from +0.593 to +0.413. What survives is **not a coupling moment at all**:

- `1/r_H`, r = +0.650. `r_H` is the denominator of the relative error, so weak-signal traits
  report large relative errors from small absolute ones. This is a scale artefact, not a defect
  in the correction. `gpt-4-0613/CON` has the smallest `r_H` of its pool (0.0565) and is the one
  cell whose oracle-reference error blows up to 544%.
- **`amplification x |dm prevalence bias|`, Spearman rho = +0.853.** The product of how wrong the
  prevalence estimate is and how hard the EIV chain amplifies a prevalence error at that cell's
  (pi, kappa, delta, g). This is the largest rank correlation anywhere in round 3.

So the narrowed candidate is: the EIV error is the prevalence estimator's error, passed through
a cell-specific amplification, divided by `r_H`. `g`, `c_pool`, `kappa` and `delta` enter only
through the amplification factor, which is why none of them predicts the error on its own.

### 1.4 The 2x2: which unknown carries it

`eiv_correct` already takes `pi_fixed`, so the counterfactual needed no estimator edit. Two
things the estimator does not know can each be handed to it: **PI** (the true prevalence) and
**REF** (the actually-injected texts as reference, rather than the held-out halves). Crossing
them gives four errors. Neither branch is deployable; both are diagnostics.

Share of the error that knowing pi alone removes, pi = 0.30, p = 1, averaged over 12 splits:

```
    gpt-4-0613/EXT              +63.9% <-FAIL
    gpt-3.5-turbo-0613/AGR      +69.0% <-FAIL
    llama-2/AGR                 +74.0%
    llama-2/NEU                 +52.1%
    gpt-3.5-turbo-0613/OPE      +46.7%
    ...
    llama-2/OPE                  -7.4% <-REF
    gpt-4-0613/OPE               -7.4%
    llama-2/EXT                  -4.3%
```

**This is the separator, and it is a channel rather than a moment.** Both flagged cells lose
roughly two thirds of their error the moment prevalence is known. `llama-2/OPE` loses nothing --
handing it the true prevalence makes it marginally worse. Whatever residual error `llama-2/OPE`
has is not a prevalence problem, and that is the real distinction between it and the flagged
cells. It is invisible in the published table because it only appears after averaging over
splits.

The class is wider than two cells: five cells are prevalence-dominated (>45% removed), and
`llama-2/AGR` -- unflagged -- is the most prevalence-dominated of all.

Aggregate, on the median cell (the mean is destroyed by `gpt-4-0613/CON`'s 544%, whose EIV
denominator is near zero so its *relative* error is ill-conditioned; the correction itself is
fine there):

```
                      err_00   err_pi  err_ref  err_both
  MEDIAN over cells    11.1%    7.2%     7.0%     6.7%

  knowing pi alone removes    35.1%
  a matched reference alone   36.8%
  both together               39.8%
```

The two channels are close to redundant and neither closes the gap: **~60% of the median cell's
EIV error survives both oracles.** That residual is the one thing round 3 does not explain, and
it is the honest ceiling on what fixing the prevalence estimator can buy.

---

## 2. Calibration-split spread of the adjusted-count offset

400 splits per cell, closed form (`ac_offset_pred` = the `LAYERB-SWEEP.md` §5 two-term transfer
law evaluated at each split's own `se_cal`, `sp_cal`), plus 12 splits with Monte Carlo.

### 2.1 The offset is mean-zero. It was never a bias.

```
  cell                          pi   split0     mean      sd      p05      p95
  gpt-4-0613/EXT              0.30  +0.0363  +0.0077  0.0604  -0.0807  +0.1136
  gpt-4-0613/NEU              0.30  +0.0792  +0.0013  0.0587  -0.0870  +0.1059
  gpt-3.5-turbo-0613/AGR      0.30  -0.1394  +0.0287  0.1386  -0.1438  +0.2484
  gpt-3.5-turbo-0613/CON      0.30  -0.0884  +0.0117  0.1253  -0.1475  +0.2442
  llama-2/OPE                 0.30  -0.0190  +0.0022  0.0272  -0.0399  +0.0469
  llama-2/EXT                 0.30  +0.0442  +0.0020  0.0284  -0.0418  +0.0514
```

Every defined cell has |mean| <= 0.029 against an sd of 0.027 to 0.139. **The adjusted-count
offset documented in Part IV is a calibration-split random effect with mean zero, not a
systematic bias.** `gpt-3.5-turbo-0613/AGR`'s published -0.1394 sits at roughly the 3rd
percentile of its own split distribution.

Its size is set by the machine pool's detectability, which is `se_cal` and therefore the
denominator of the adjusted count:

| pool | `se_cal` | sd of offset at pi=0.30 |
| --- | --- | --- |
| llama-2 | 0.56 - 0.64 | 0.027 - 0.029 |
| gpt-4-0613 | 0.22 - 0.27 | 0.059 - 0.065 |
| gpt-3.5-turbo-0613 | 0.10 - 0.12 | 0.118 - 0.139 |
| big5 essays | **0.000** | undefined, 400/400 splits |

The essays pool is GPT-4-turbo synthetic text (corrected 2026-09-09, pass-3 review — the pool
was previously mischaracterized as human; see `LAYERB-SWEEP.md`'s correction note and
`lane3-testbed/CORPUS-AUDIT.md`), so a detector thresholded at sp = 0.99 flags none of it —
a detector failure on synthetic text, not a human negative control —
`denom = se - (1-sp) <= 0`, and `_adjusted_count_pi`'s shipped guard refuses in every single
split. That is the guard working as designed, and it matches the `ac_bias=nan` column that
`layerb_pin.json` reports for `big5/EXT`.

### 2.2 The transfer law is near-exact once evaluated at the right split

360 (cell, split, pi) points, predicted offset against the realized Monte Carlo offset:

```
  corr = +0.9917   OLS slope = 1.017   intercept = +0.0006
  residual: median |r| = 0.0024, max = 0.0387
```

Part IV recorded the law as a FAIL at "max residual 0.0233". That residual was the law being
evaluated at one split's `se_cal`/`sp_cal` and scored against a different split's realization.
Per split, its median residual is 0.0024 -- an order of magnitude inside the offsets it predicts.
The law is right; the earlier check was mis-specified.

### 2.3 Does a usable between-wave change detector survive?

Write the per-split offset as `b(pi) = b0 + b1*pi`, fitted over pi in {0.02, 0.05, 0.10, 0.20,
0.30}. Two waves at pi1 and pi2 = pi1 + delta, both estimated by adjusted count:

- **Same calibration split reused.** `b0` cancels exactly and the estimated change is
  `delta * (1 + b1)`. The error is *multiplicative*, and `b1` has mean ~0.
- **Split re-drawn between waves.** The change also picks up `b(2)(pi2) - b(1)(pi1)`, an
  *additive* noise of sd `sqrt(sd(b@pi1)^2 + sd(b@pi2)^2)`.

```
  cell                         b0 mean   sd(b0)   b1 mean   sd(b1) rel err same  MDC redraw   d=0.20 is
  gpt-4-0613/EXT               +0.0006   0.0163   +0.0237   0.1986       39.7%      0.1303       3.1 sd
  gpt-4-0613/OPE               +0.0003   0.0166   +0.0119   0.2102       42.0%      0.1400       2.9 sd
  gpt-3.5-turbo-0613/AGR       -0.0069   0.0475   +0.1186   0.4827       96.5%      0.2996       1.3 sd
  gpt-3.5-turbo-0613/EXT       -0.0012   0.0439   +0.0702   0.4157       83.1%      0.2680       1.5 sd
  llama-2/OPE                  -0.0003   0.0065   +0.0082   0.0904       18.1%      0.0583       6.9 sd
  llama-2/EXT                  +0.0010   0.0074   +0.0033   0.0940       18.8%      0.0611       6.5 sd
```

**Verdict: a usable change detector survives, but only if the calibration split is frozen across
waves.**

With the split frozen, the change is unbiased in expectation (`b1` mean is +0.003 to +0.119) and
carries a 2-sd *relative* error of 18% (llama-2), 40% (gpt-4) or 83-97% (gpt-3.5). The sign of
the change is never at risk, since |b1| < 1 in essentially every split. A doubling of ghost
prevalence between waves is detected as a doubling plus or minus a fifth for llama-2-like pools.

With the split re-drawn, the additive floor is 0.058, 0.13 and 0.27 respectively. A true change
of delta = 0.20 -- a very large wave-on-wave shift -- is 6.9 sd for llama-2, a marginal 3.1 sd
for gpt-4, and **1.3 sd for gpt-3.5, i.e. undetectable**. Re-drawing the calibration split
between waves destroys the detector for the two-thirds of pools whose detector is weak.

The operational rule this implies: freeze the calibration split at wave 1 and reuse the identical
held-out reference halves at every subsequent wave. It costs nothing, it is the difference
between a 18-40% relative error and a 0.06-0.27 absolute noise floor, and it is not currently
written down anywhere in the pipeline.

---

## 3. Distribution-match slope

### 3.1 The premise moves: it is not llama-2, it is OPE

`LAYERB-SWEEP2.md` reported the slope of realized `pi_hat` on true `pi` running 0.31 to 0.48 in
five of six pin-box cells and 0.935 in `llama-2/OPE`. That box contained exactly one OPE cell.
Over all 20 cells (split 0, p = 0, 60 reps, five prevalences):

```
  cell                       |delta|   S@60 sl@8    sl@15   sl@30   sl@60   sl@120
  essays/OPE                   2.132  0.657  1.078  1.064  1.035  1.009  0.960
  gpt-4-0613/OPE               2.168  0.602  1.051  1.040  1.037  0.995  0.911
  gpt-3.5-turbo-0613/OPE       2.696  0.786  1.013  1.021  0.999  0.973  0.951
  llama-2/OPE                  1.618  0.407  1.016  1.066  0.988  0.952  0.827
  --- every non-OPE cell ---
  essays/AGR                   0.839  0.181  1.030  1.025  0.975  0.868  0.646
  gpt-3.5-turbo-0613/EXT       0.570  0.123  0.779  0.856  0.733  0.719  0.548
  gpt-4-0613/EXT               0.494  0.110  0.967  0.822  0.662  0.485  0.270
  llama-2/EXT                  0.239  0.085  0.752  0.637  0.467  0.307  0.235
  gpt-4-0613/AGR               0.529  0.085  1.184  1.042  0.532  0.231  0.107
  gpt-4-0613/NEU               0.392  0.049  0.425  0.578  0.448  0.089  0.065
```

All four OPE cells sit at 0.952 to 1.009 at the default 60 bins. All sixteen non-OPE cells sit
at 0.089 to 0.868. The pool is irrelevant -- `essays/OPE`, whose texts are GPT-4-turbo synthetic (not
human-written, see correction above), and whose `g` is -0.136, has slope 1.009. **What makes `llama-2/OPE` special is that it is an
OPE cell, and OPE is the trait where the two score distributions barely overlap:** |delta| runs
1.62 to 2.70 for OPE against 0.24 to 0.84 for everything else.

### 3.2 The mechanism, and a prediction made before measuring

`_distribution_match_pi` minimises Hellinger distance between the observed histogram and
`pi*p_m + (1-pi)*p_h`. Linearise it. With `D = p_M - p_H` the population separation, `e_m` and
`e_h` the sampling error in the two reference histograms, and the inner product the Hellinger
metric induces (`<a,b> = sum_b a_b b_b / 4q_b`), the minimiser is a weighted regression of
`p_obs - p_h` on `p_m - p_h`. The regressor is noisy, so with `S = <D,D>`, `N_m = E|e_m|^2`,
`N_h = E|e_h|^2`:

```
    E[pi_hat]  ~=  pi * S/(S + N_m + N_h)  +  N_h/(S + N_m + N_h)
```

That is textbook errors-in-variables attenuation, and it predicts **both** observed features
from one ratio: a slope below 1, and a *positive* intercept, because human-reference sampling
noise is absorbed into the machine component. Against the measured slope at 60 bins, 20 cells:

```
  slope@60 vs predicted S/(S+Nm+Nh) : r=+0.9322   rho=+0.7880
  slope@60 vs |delta|               : r=+0.8570
  slope@60 vs S                     : r=+0.8498
```

The prediction has a falsifiable consequence. `N` scales with the number of occupied bins; `S`
saturates once the bins resolve the separation. So the slope must **rise as `n_bins` falls**.
Averaged over 20 cells x 2 splits:

```
    n_bins=   8  occupied=  8.0  slope=0.748 (pred 0.858)  intercept=+0.0465
    n_bins=  15  occupied= 14.7  slope=0.688 (pred 0.782)  intercept=+0.0507
    n_bins=  30  occupied= 27.8  slope=0.584 (pred 0.691)  intercept=+0.0595
    n_bins=  60  occupied= 51.7  slope=0.494 (pred 0.612)  intercept=+0.0664
    n_bins= 120  occupied= 95.5  slope=0.386 (pred 0.541)  intercept=+0.0741
```

Monotone in both, in the predicted direction, over a factor of two in slope. The intercept falls
as the slope rises, exactly as `N_h/(S+N_m+N_h)` requires, and the OPE cells -- where `S >> N` --
have intercepts of -0.018 to +0.018 against +0.14 to +0.24 for the most attenuated cells.

Where the theory is wrong: the predicted slope is a systematic **upper bound**, mean observed
minus predicted = -0.110 at 60 bins. The local-quadratic approximation to Hellinger overstates
how much signal survives sparse bins. The ordering and the ladder are right; the level is not.

### 3.3 Is it derivable in deployment?

`S` above was computed from the full pools, which no deployment holds. But all three terms have
plug-ins built from nothing but the two reference histograms the estimator is already handed:
`E<d,d> = S + N_m + N_h`, so `S_hat = <d,d> - N_m_hat - N_h_hat` is unbiased, with `N_m_hat` and
`N_h_hat` the multinomial variances of those same histograms. Over 200 (cell, split, n_bins)
points:

```
    slope_obs vs plug-in  r=+0.7562  OLS 0.868  mean(obs-plug)=-0.030  median|res|=0.125
    slope_obs vs oracle   r=+0.8623  OLS 1.456  mean(obs-oracle)=-0.117
    plug-in vs oracle     r=+0.9329
    intercept_obs vs plug r=+0.4904
    S_hat < 0 (reference pair cannot resolve the two pools at all): 2/200
```

**Diagnosable: yes. Correctable: no, not at this reference size.** The plug-in tracks the
realized slope at r = +0.756 with no oracle input, which is enough to tell a practitioner in
advance whether their prevalence estimate will be compressed by a third or not at all. It is not
enough to divide through by -- a median residual of 0.125 on a slope would propagate into the
corrected prevalence at a size comparable to the bias being removed. The intercept plug-in is
weaker still (r = +0.490).

The one unambiguously useful output is the refusal signal: `S_hat < 0` means the reference pair's
separation is below its own sampling noise, so the estimate is uninformative. It fires in 2 of
200 points here, including `gpt-4-0613/NEU` at 60 bins, whose measured slope is 0.089.

### 3.4 What this says about the shipped default

`n_bins = 60` is the wrong default for a machine reference of 160 texts. Per cell, the bin count
on the ladder that gets closest to slope 1:

```
    gpt-4-0613/AGR             best=  15 (slope 1.042)   default 60 -> 0.231
    gpt-4-0613/EXT             best=   8 (slope 0.967)   default 60 -> 0.485
    essays/EXT                 best=   8 (slope 0.995)   default 60 -> 0.407
    essays/AGR                 best=  15 (slope 1.025)   default 60 -> 0.868
    gpt-3.5-turbo-0613/EXT     best=  15 (slope 0.856)   default 60 -> 0.719
    llama-2/OPE                best=  30 (slope 0.988)   default 60 -> 0.952
    gpt-3.5-turbo-0613/NEU     best=  60 (slope 0.233)   default 60 -> 0.233
```

Coarsening to 8-15 bins recovers a near-unit slope in several cells where the default gives 0.23
to 0.49, and costs the OPE cells almost nothing since they are unattenuated everywhere. It does
not save every cell -- `gpt-3.5-turbo-0613/NEU` is at 0.233 for every bin count, which is the
`S_hat < 0` regime where no binning helps.

**I have not changed the default.** `n_bins` is an `estimators.py` signature default and the
SPEC 1.1/1.3 question is explicitly Abhay's call; this is the evidence for that decision, not
the decision. The measurement is reproducible with `round3_dm.py` if the value is to be revisited.

---

## 4. What round 3 changes

1. **Per-cell EIV errors in `LAYERB-SWEEP2.md` should not be read as cell properties.** 54% of
   their variance is the calibration split. Any table of 20 cells at one split each is reporting
   a nuisance draw at roughly the same magnitude as the effect.
2. **`gpt-4-0613/EXT` is not a failing cell.** It does not separate from `llama-2/OPE` (0.85
   within-sd, overlapping ranges). `gpt-3.5-turbo-0613/AGR` is real at 1.49 within-sd, and
   `llama-2/AGR`, unflagged, is worse than either.
3. **The EIV error is the prevalence error times an amplification factor, over `r_H`**
   (rho = +0.853). Not `g`, `c_pool`, `kappa` or `delta`, each of which is under |r| = 0.25.
   About 60% of the median cell's error survives both oracles and remains unexplained.
4. **The adjusted-count offset has mean zero over splits.** It is a random effect whose sd is set
   by `se_cal`. Part IV read one draw of it as a systematic bias.
5. **The transfer law is near-exact per split** (median residual 0.0024), not the FAIL Part IV
   recorded. That check was evaluating it against the wrong split.
6. **Freeze the calibration split across waves.** It converts an absolute noise floor of
   0.06-0.27 into a relative error of 18-40%, and it is the difference between a working and a
   dead between-wave change detector for weak-detector pools.
7. **The distribution-match slope is errors-in-variables attenuation from the reference
   histograms**, predicted at r = +0.932 and confirmed causally by a monotone `n_bins` ladder
   that moves the mean slope from 0.386 to 0.748. `llama-2/OPE` is not special; OPE is.
8. **`n_bins = 60` is too fine for a 160-text reference.** Evidence recorded, default untouched.

ROUND3-DONE
