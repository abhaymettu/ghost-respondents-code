# Layer B sweep 2: corrections, a guard, k = 4, and the (pi, n) box

Follow-on to `LAYERB-SWEEP.md`. Three of that document's notes went stale between writing and
now; this one corrects them, then reports the three compute items that were blocked behind
them. All of it is local CPU, single-threaded under `nice -n 15`. The Layer A grid (PID 8258,
started Mon Sep 7 16:29:26, 5h21m elapsed at the time of the guard edit) ran untouched
throughout; neither `dgp.py` nor the grid was modified.

`LAYERB-SWEEP.md` is left exactly as shipped, still 333 lines ending `SWEEP-DONE`. The
corrections live here, not there, so the record of what was believed when it was written stays
readable.

---

## Part I. The three stale notes

### C1. The chunk dependency is resolved, and the loader needed no change

**Stale text** (`LAYERB-SWEEP.md` section 7): *"Chunk-level scores exist in lane 3's files for
the labeled pools (k = 4, loaded and tested), but not for pk_human, so the multi-item arms
remain blocked on lane 3."*

pk_human chunk scores exist. `inject/pools.py:610-690` (`lane3_pool`) already reads
`chunk_1..chunk_k` generically for every pool including pk_human, so **no loader change was
needed** — the blocker was a fact about lane 3's files, not about lane 4's code, and it
cleared without lane 4 doing anything.

The receipt that this is the right data and not a lookalike: the between-chunk correlation on
the **full** pk_human EXT pool (n = 2421) is **0.2083**, which reproduces lane 1's Q14
baseline (`POOL-MEASUREMENTS.md` ~line 232) to four decimals. Split halves of the same pool
give 0.1849-0.2816, so the split-half value is *not* the number to check against lane 1; only
the full pool reproduces it.

Section 7's other clause stands corrected too: **rho_T is now estimated**, at k = 4, in Part
III. It is estimated badly, which is the finding.

### C2. The `delta` sign is ruled, and the ruling required no code change

**Stale text** (sections 7 and 9): *"`delta` sign follows CONVENTIONS; lane 3's memo-sign
value is carried per cell in the JSON as `delta_lane3_memo_sign`. Still unresolved."* /
*"Get a ruling on the `delta` sign between CONVENTIONS and the memo."*

The two definitions are exact negations:

| source | definition |
|---|---|
| `CONVENTIONS.md:21` | `Delta = delta * sqrt(V_H)`, the unstandardized gap `mu_H - mu_M` |
| `POOL-MEASUREMENTS.md:22` | `delta = (mu_M - mu_H) / sqrt(V_H)` |

**Ruling: CONVENTIONS binds**, and it binds by consumption, not by preference. Three sites
consume `delta` *linearly*, where the sign changes the answer, and all three are written to
the CONVENTIONS sign:

- `dgp.py:57` — `Delta = delta * sqrt(V_H)`, with `mu_M = mu_H - Delta`. The DGP's machine
  mean is defined by it.
- `population.py:106` — (E21) nonignorable numerator, the `- pi(1-pi) delta d_theta / sqrt(rel_H)` term.
- `population.py:118` — (E23) `c_flip'`, the `delta d_theta / sqrt(rel_H) - 1/pi` bracket.

Every *other* use in the codebase is `delta**2` — `population.py:38` (Den), `:80` (c_star),
`:133` (r_obs), `inject/build.py:342` — and is sign-blind.

The memo sign is a display convention on lane 3's own files, and it is converted at the
boundary, in one direction, at four already-existing sites: `inject/build.py:334`
(`delta = -mm.mean`, comment already naming CONVENTIONS), `layerb_pilot.py:211`,
`sweep_layerb.py:150`, and the assertion at `inject/test_inject.py:538`, which checks lane 3's
filed value against the recomputation *with the negation applied* and passes.

**Why the open note never produced a wrong number.** Layer B sets `d_theta = 0` by
construction — machine status is independent of theta, which is assumption A1
(`inject/build.py:133`). E21 and E23 are the only linear-in-`delta` estimator paths, and both
carry `d_theta` as a factor. So across the whole injected design `delta` enters *only* as
`delta**2`, and the conflict was unobservable. It becomes observable the moment Layer A's
`nonignorable` arm runs (`grid.py:141`, which pairs `d_theta != 0` with `delta = 0.3`) — which
is precisely the arm inside PID 8258 right now. The note was worth closing before those
results land, not after.

No code change. The conversion was already correct and already tested; the note was stale in
the sense that it described an open question that the code had already answered.

### C3. N2 is decided, and two files now say so

**Stale text**: N2 (the choice of headline estimand) was carried as undecided.

Decided 2026-09-07: the headline estimand is the **observed-score** `rho_H = Cor(x, w | H)`,
so "bias" means contamination bias and excludes classical attenuation. `rho_T` is retained as
the robustness estimand.

Two files edited, both this session:

- **`CONVENTIONS.md:30`** — the truth-value block now reads
  `rho_H = sqrt(rel_H) * rho_T   # PRIMARY estimand (N2 DECIDED 2026-09-07)`, with `rho_T`
  marked `SECONDARY, disattenuated`.
- **`README.md:37-42`** — N2 rewritten to the decided state, stating explicitly that **every
  metric is still computed for both**: the decision fixes which one is the headline, not what
  the code computes. No estimator was touched.

**`SPEC.md` is untouched.** SPEC 1.1/1.3 wording is Abhay's call (Q3) and both README and this
document say so rather than pre-empting it.

---

## Part II. The negative-denominator guard

`LAYERB-SWEEP.md` section 5 and item 1 of section 9: `_adjusted_count_pi` tested
`abs(denom) < 1e-8`, which refuses a denominator at zero but **accepts a negative one** and
returns a clipped, finite, monotonically-wrong prevalence. `estimators.py:347-354` now reads:

```python
def _adjusted_count_pi(flag_rate: float, se: float, sp: float) -> tuple[float, bool]:
    denom = se - (1.0 - sp)
    # <= not abs(): a detector at or below chance gives denom <= 0, and dividing through it
    # returns a finite, clipped, monotonically-WRONG pi. Refuse instead (lane 4 sweep s5).
    if denom <= 1e-8:
        return float("nan"), False
    pi_hat = (flag_rate - (1.0 - sp)) / denom
    return float(np.clip(pi_hat, 0.0, 1.0)), True
```

**Two things to flag, both against what was assumed when this edit was authorized.**

**1. There is no git repository here.** `git rev-parse` returns `fatal: not a git repository`
in `lane4-simulation/` and in its parent. The request was to note the guard's justification in
the commit message; there is no commit to carry it, so the justification lives in the source
comment above and in this section. If the tree is later initialized and committed, this is the
text that belongs in that message.

**2. The reason the edit is safe is the detector table, not process timing.** The argument
offered was that `estimators.py` was imported long ago, so editing the file cannot perturb the
running grid. That argument is incomplete: `run_grid_full.py:35,372` uses
`multiprocessing.Pool`, macOS defaults to the **spawn** start method, and `Pool` respawns a
worker if one dies. A respawned worker re-imports `estimators.py` **from disk**, picking up the
edit mid-run.

The argument that actually holds is that the new branch is **unreachable in every Layer A
cell**. `dgp.DETECTORS` (`dgp.py:16-21`) offers exactly four operating points:

| detector | se | sp | `denom = se - (1 - sp)` | old branch | new branch |
|---|---|---|---|---|---|
| `none` | 0.00 | 1.00 | **0.00** | refused | refused |
| `calibrated` | 0.95 | 0.99 | 0.94 | computed | computed |
| `degraded` | 0.85 | 0.85 | 0.70 | computed | computed |
| `oracle` | 1.00 | 1.00 | 1.00 | computed | computed |

**No Layer A denominator is negative**, and the one that is zero was already refused by
`abs(denom) < 1e-8` and is still refused by `denom <= 1e-8`. Old and new behaviour are
identical on all four rows, so a mid-run re-import is a no-op regardless of whether one
happens. Corroborating but strictly secondary: all 11 children of PID 8258 shared the parent's
16:29:26 start time, so in fact no worker had respawned in 5h21m.

**The guard fires on real data immediately.** In Part IV's (pi, n) run,
`big5_personality_essays/EXT` returns `nan` for adjusted-count prevalence at every pi, because
that pool's detector has se ~ 0.00 at sp = 0.99 — `denom ~ -0.01`, negative, which the old
`abs()` test waved through. Every adjusted-count number previously reported for that cell was
a division by a negative number.

**Regression, both run after the edit:** `test_estimators.py` **20/20**,
`python -m inject.test_inject` **61/61**.

---

## Part III. k_chunks = 4: the multi-item arms

`sweep_k4.py`, 6 cells, 50s. Full output in `results/layerb_k4.json` and `.log`.

### The six cells, and why these six

EXT on all four machine pools, because EXT is the only trait with an **external** between-chunk
number to check against (lane 1's 0.2083), plus `gpt-3.5-turbo/AGR` (largest g in the whole
20-cell sweep, +2.882, and the largest Att swing, 0.902 -> 1.191) and `llama-2/OPE` (largest
`c_pool`, 0.5048, and largest kappa, 1.273). Together they bracket g from +0.497 to +2.882,
the sweep's entire positive range. Part IV uses the same six, so the two rounds are directly
comparable.

### What `rel_H`'s truth value is at k = 4

Layer A defines `rel_H` through `x = sqrt(rel_H) theta + noise`, i.e.
`rho_H = sqrt(rel_H) rho_T` (CONVENTIONS). In the injected design `theta` is the standardized
**label** (`inject/build.py:124`) and `rho_H_true = rho_T * r_H`. Therefore
**`sqrt(rel_H_true) = r_H`, and `rel_H_true = r_H^2`.** That is the number a between-chunk
correlation has to match for the weak-H2 route to identify `rho_T`, and it is the scoring basis
for every weak-H2 check below.

### Three headline readings, because `Sample.x` changes meaning at k > 1

`dgp.py:112-114` sets `Sample.x = X[:, 0]`, so at k = 4 the headline score becomes **chunk 1**,
while `inj.x_full` stays the whole-text score. That is not a bug, but it means "the" answer is
three answers, and the script reports all three: whole-text / sqrt(rbar) (what
`_naive_style_fit` at `estimators.py:119-142` actually does), whole-text /
sqrt(Spearman-Brown composite), and chunk-1 / sqrt(rbar) — the last being the fair
parallel-item reading, since `rbar` is chunk 1's own reliability.

### Results

| cell | r_H (whole) | r_H (chunk 1) | ratio | rbar | SB | rel_true = r_H^2 | rbar / rel_true |
|---|---|---|---|---|---|---|---|
| big5/EXT | +0.1451 | +0.3155 | 2.17x | 0.2098 | 0.5151 | 0.0211 | **10.0x** |
| gpt-4/EXT | +0.1721 | +0.3509 | 2.04x | 0.1849 | 0.4757 | 0.0296 | **6.2x** |
| gpt-3.5/EXT | +0.1636 | +0.3449 | 2.11x | 0.2032 | 0.5050 | 0.0268 | **7.6x** |
| llama-2/EXT | +0.1392 | +0.3141 | 2.26x | 0.2034 | 0.5053 | 0.0194 | **10.5x** |
| gpt-3.5/AGR | +0.1182 | +0.3273 | 2.77x | 0.1652 | 0.4419 | 0.0140 | **11.8x** |
| llama-2/OPE | +0.1873 | +0.3712 | 1.98x | 0.2816 | 0.6106 | 0.0351 | **8.0x** |

rho_T recovery, all against a truth of 0.5, on a **clean (pi = 0) sample**, plus the coupling
arms at pi = 0.10:

| cell | oracle err (z) | naive rbar | Spearman-Brown | chunk-1 | p = 0 | p = 1 | shift |
|---|---|---|---|---|---|---|---|
| big5/EXT | +3.7% (1.71) | -67.2% | -79.0% | -30.3% | -72.2% | -68.6% | +3.5% |
| gpt-4/EXT | +0.2% (0.12) | -59.9% | -75.0% | -18.3% | -66.0% | -59.0% | +6.9% |
| gpt-3.5/EXT | -0.6% (-0.30) | -63.8% | -77.1% | -23.1% | -70.2% | -66.5% | +3.7% |
| llama-2/EXT | -0.4% (-0.17) | -69.3% | -80.5% | -29.7% | -73.1% | -68.8% | +4.3% |
| gpt-3.5/AGR | +2.7% (1.01) | -70.1% | -81.7% | -17.4% | -78.1% | -68.9% | +9.2% |
| llama-2/OPE | +0.2% (0.13) | -64.6% | -76.0% | -30.3% | -76.7% | -71.5% | +5.1% |

**5 of 10 checks pass.** The five failures are findings, not scoring bugs, and the oracle
column is what proves that: dividing `rho_H` by the *true* `sqrt(rel_H) = |r_H|` on a clean
sample returns `rho_T = 0.5` within **1.71 MCSE** in the worst cell, under the project's
existing 4-MCSE discipline. The correction machinery is sound. What fails is the estimate of
`rel_H` fed into it.

### PASS

1. **pk_human EXT between-chunk r reproduces lane 1's 0.2083 exactly** on the full pool
   (n = 2421); split halves give 0.1849-0.2816.
2. **Every cell built at k = 4 with no unchunkable text in any draw.**
3. **rbar is stable across coupling arms** (max |rbar(p=1) - rbar(p=0)| = 0.0022), as it must
   be: chunk agreement is a property of the text, not of who was assigned to whom.
4. **The oracle control passes** — max |z| = 1.71 over 6 cells, max |err| 3.7%, finite-sample.
5. **Coupling still moves the multi-item error** (+3.5% to +9.2% from p = 0 to p = 1), so
   k = 4 does **not** immunize an estimate against contamination.

### FAIL 1 (and the cause of the rest): lane 3's chunk scores are not cross-fitted

`r(chunk 1, label) / r(whole text, label)` runs **1.98x to 2.77x**. A quarter of a text cannot
be twice as valid against the label as the whole text. The cause is in lane 3's own memo:
`POOL-MEASUREMENTS.md` ~line 225 records that the five RidgeClassifiers behind the chunk scores
were **"a refit, not a reload"** — refit on all texts, then applied to chunks *of their own
training texts*. The whole-text scores are 5-fold cross-fitted; the chunk scores are in-sample.
Corroborating, on the full pk_human pool (n = 2421, `results/layerb_k4_chunkdiag.json`):
the mean of the four chunk scores correlates with the whole-text score at only **0.5908** (EXT),
0.5620 (AGR), 0.6766 (OPE) — far below what two views of the same construct should give. The
same file carries the raw pair behind the ratio: `r(chunk 1, label) = 0.3380` against
`r(whole, label) = 0.1646` for EXT, and the pattern repeats at 3.01x (AGR) and 1.79x (OPE).

Lane 3's prose contradicts itself here — ~line 241 describes the chunk baseline as sitting on
"a cross-fitted trait score", which line 225 rules out.

This inflates every chunk-based number **in the optimistic direction**. Weak-H2 fails anyway.
That direction matters: the failures below are a floor.

### FAIL 2: between-chunk r is 6x to 12x the true rel_H

`rbar` runs 6.2x to 11.8x `r_H^2`. Against the chunk-1 indicator, where `rbar` is at least the
right reliability for the right score, it is still 1.5x to 2.1x. Chunks of one text share
topic, length, register and author idiom, none of which is the trait. Between-chunk agreement
measures stylistic self-similarity, and only partly measures trait reliability.

### FAIL 3 and 4: disattenuation therefore fails, and Spearman-Brown makes it worse

`rho_T_hat = rho_H / sqrt(rel_hat)`. Overstating `rel_hat` shrinks the estimate. Naive `rbar`
gives **-59.9% to -70.1%** on a clean sample; **Spearman-Brown makes it worse, -75.0% to
-81.7%**, exactly as the algebra requires — the composite reliability (0.44-0.61) is larger
than `rbar` (0.17-0.28), so it divides by more. The textbook correction moves in the wrong
direction here because the reliability it corrects with is the wrong quantity, not because the
formula is misapplied.

### FAIL 5: even the fair reading fails

Applying the correction to the indicator `rbar` is actually valid for — chunk 1 — still lands
at **-17.4% to -30.3%**, outside the 25% band in 4 of 6 cells. Halving the discrepancy is not
closing it.

### What Part III licenses

Licensed: (a) pk_human chunk scores load, and reproduce lane 1's external baseline exactly;
(b) the disattenuation machinery is arithmetically sound, proven by the oracle control at
1.71 MCSE; (c) contamination is not neutralized by going multi-item.

**Not licensed, and the paper must not claim it: between-chunk consistency does not identify
`rel_H` on this corpus.** Weak-H2 is not usable as specified. It fails by 6-12x on the
reliability itself and 60-82% on `rho_T`, on chunk scores that are biased optimistically, and
it fails in the direction that would make a contaminated survey look *better* corrected than it
is.

---

## Part IV. The (pi, n) box

`sweep_pin.py`, the same six cells x pi in {0.02, 0.05, 0.10, 0.20, 0.30} x n in {500, 1000,
2500} x three coupling arms, 400 reps each: **90 design points, 270 arm-points, 1839s**. Full
output in `results/layerb_pin.json` and `.log`. `LAYERB-SWEEP.md` varies the pool and the trait
at one design point; this varies the design point at six fixed cells, which is the
complementary cut its section 9 item 5 asked for.

### Machine texts are drawn with replacement, and the bridge check earns it

Without replacement, pi = 0.30 at n = 2500 needs 750 machine respondents out of a ~160-text
injection half. Impossible. With replacement is also the honest model of a ghost-respondent
farm, which resubmits generated text. To make sure the change of sampling scheme is not itself
doing work, the design point (pi = 0.10, n = 1000) is run **both ways** in every cell:
**max |dAtt(p=1)| = 0.0051**. The two schemes agree, so Part IV's numbers are comparable to
`LAYERB-SWEEP.md`'s.

### Two of my own checks were mis-specified, and are rescored

`sweep_pin.py`'s report scored monotonicity of Att in pi against a hard `1e-3` and n-invariance
against a hard `0.05`. Both tolerances sit *below this run's own Monte Carlo standard error*
(MCSE(Att) is 0.03-0.04 at n = 500), so they tested the noise rather than the claim. Rescored
in `rescore_pin.py` against MCSE, the discipline the rest of the project uses — reading the
same JSON, re-running nothing:

- **Att(p=1) is monotone increasing in pi**: PASS. The largest decrease anywhere is
  **2.00 MCSE** (llama-2/EXT, n = 500, pi 0.02->0.05, dAtt = -0.083), and every other violation
  is under 0.74 MCSE.
- **Att is n-invariant**: PASS. The largest across-n spread is **2.97 MCSE** (llama-2/EXT,
  pi = 0.02, spread 0.093). Bias is a population property and behaves like one.

The `sweep_pin.py` log's raw 4/10 therefore understates the result; the corrected scoring is
**6/10**. The four surviving failures are in the estimators, and all four are findings.

### PASS

1. **(E7) holds across the whole box** — predicted `rho_obs` within **2.88 MCSE** of the
   realized mean over all 270 arm-points. The identity does not care about pi or n.
2. **The matched-vs-random contrast agrees with (E7)** everywhere, within 2.01 MCSE.
3. **MCSE(rho_obs) scales as 1/sqrt(n)** — the n = 500 / n = 2500 ratio is 2.03-2.49 over 30
   (cell, pi) pairs, against sqrt(5) = 2.24.
4. **Att is monotone in pi and invariant in n** (rescored above).
5. **With-replacement sampling reproduces without-replacement** (max |dAtt| 0.0051).

### The amplification threshold: every cell crosses Att = 1 by pi = 0.30

Att(p = 1) at n = 2500, the smallest pi at which fully-matched assignment stops attenuating and
starts inflating:

| cell | pi=0.02 | 0.05 | 0.10 | 0.20 | 0.30 | crosses at |
|---|---|---|---|---|---|---|
| big5/EXT | 0.994 | 0.995 | 0.999 | 1.007 | 1.014 | pi >= 0.20 |
| gpt-3.5/EXT | 0.998 | 1.018 | 1.043 | 1.087 | 1.164 | pi >= 0.05 |
| llama-2/EXT | 0.980 | 1.014 | 1.013 | 1.027 | 1.062 | pi >= 0.05 |
| llama-2/OPE | 1.009 | 1.010 | 1.031 | 1.102 | 1.199 | pi >= 0.02 |
| gpt-4/EXT | 1.047 | 1.073 | 1.137 | 1.299 | 1.425 | pi >= 0.02 |
| gpt-3.5/AGR | 1.070 | 1.128 | 1.253 | 1.468 | **1.706** | pi >= 0.02 |

**6 of 6 cells cross inside pi <= 0.30**, three of them by pi = 0.02. `LAYERB-SWEEP.md` found
inflation in 9 of 20 cells at the single design point pi = 0.10; raising pi turns that into a
near-universal effect, and at pi = 0.30 in the worst cell a matched ghost population inflates
the observed correlation by about **71%** (Att = 1.706 at n = 2500; the three n values at that
point read 1.682 / 1.729 / 1.706, agreeing within MCSE, and the n = 2500 estimate is the most
precise of them).

### FAIL 1 and 2: the two prevalence estimators fail in *different* ways, and this matters

This is the sharpest result in Part IV. Regressing the estimate on the truth across the five pi
values (n = 2500, p = 0):

| cell | dm slope | dm intercept | adj-count slope | adj-count intercept |
|---|---|---|---|---|
| big5/EXT | 0.478 | +0.034 | **undefined** | **undefined** |
| gpt-3.5/AGR | 0.309 | -0.008 | 0.540 | -0.016 |
| gpt-3.5/EXT | 0.378 | +0.135 | 0.987 | +0.052 |
| gpt-4/EXT | 0.335 | +0.209 | 1.083 | +0.000 |
| llama-2/EXT | 0.314 | +0.181 | 1.204 | -0.008 |
| llama-2/OPE | 0.935 | -0.009 | 0.794 | +0.007 |

**The distribution-match estimator fails on slope.** In 5 of 6 cells it recovers only
**0.31-0.48** of a change in true prevalence. It is not merely biased; it is *unresponsive to
the quantity it estimates*. Tripling the ghost share from 0.10 to 0.30 moves the estimate by
about a third of that. 83 of 90 points miss by more than 0.01, |bias| spanning 0.0037-0.2280,
and the sign flips within a single cell as pi rises (big5/EXT runs +0.023 at pi = 0.02 to
-0.123 at pi = 0.30), so there is no direction to correct in.

**The adjusted-count estimator fails on level.** Where the detector is usable its slope is
**0.79-1.20** — it *tracks* pi correctly — and the damage is an additive offset of -0.016 to
+0.052. 55 of 75 defined points still miss 0.01 (|bias| 0.0016-0.1565), so it is not a usable
absolute estimate either. But the failure mode is qualitatively different, and the practical
consequence differs with it: **an adjusted-count estimate is usable for detecting *change*
between two waves calibrated the same way; a distribution-match estimate is not usable even for
that.** Neither is a usable point estimate of pi.

`big5_personality_essays/EXT` is `undefined` at every pi, not merely wrong — this is the new
guard from Part II firing. That pool's detector has se ~ 0.00 at sp = 0.99, so
`denom = se - (1 - sp) ~ -0.01`, negative. Every adjusted-count number ever reported for that
cell was a division by a negative number, silently clipped into range.

### FAIL 3: the transfer law holds, but the residual concentrates at small pi

The two-term calibration-transfer law from `LAYERB-SWEEP.md` section 5 predicts the
adjusted-count bias with **corr(observed, predicted) = 0.9963** across all 75 defined points.
The check fails only because one point exceeds the 0.02 absolute tolerance:

| pi | max residual | mean residual |
|---|---|---|
| 0.02 | **0.0233** | 0.0046 |
| 0.05 | 0.0154 | 0.0028 |
| 0.10 | 0.0071 | 0.0020 |
| 0.20 | 0.0058 | 0.0023 |
| 0.30 | 0.0091 | 0.0027 |

The residual grows monotonically as pi falls, which is what the law's structure implies: at
small pi the bias is dominated by the `(1 - pi)` specificity-transfer term and the estimator
divides a shrinking signal. The law is sound; **its accuracy degrades exactly where
ghost-respondent prevalence is lowest**, which is the regime a real survey most likely sits in.

### FAIL 4: the EIV correction breaks in two specific cells, and not because of n

11 of 270 arm-points exceed 25% error, worst **42.0%**. My first guess — finite-sample noise at
small n — is wrong, and the data says so plainly:

| n | max abs err | median | > 25% |
|---|---|---|---|
| 500 | 33.2% | 5.9% | 3/90 |
| 1000 | 39.8% | 3.6% | 5/90 |
| 2500 | **42.0%** | 3.7% | 3/90 |

The failures do not shrink with n; the worst point is at the *largest* n. They are
population-level, and they are concentrated in exactly two cells:

| cell | g | max abs err | median | > 25% |
|---|---|---|---|---|
| gpt-4/EXT | +1.973 | 33.2% | **12.0%** | 6/45 |
| gpt-3.5/AGR | +2.882 | **42.0%** | **8.4%** | 5/45 |
| llama-2/OPE | +2.395 | 16.0% | 3.3% | 0/45 |
| gpt-3.5/EXT | +1.817 | 15.3% | 4.5% | 0/45 |
| llama-2/EXT | +0.497 | 22.3% | 4.1% | 0/45 |
| big5/EXT | +0.811 | 20.9% | 1.8% | 0/45 |

The two bad cells have median errors 2-7x every other cell, so this is systematic, not
outliers. **It is not a clean function of g**: llama-2/OPE at g = +2.395 sits between the two
failures in g and is fine. Six cells cannot separate g from `c`, kappa and delta, so the
mechanism is not identified here and this document does not guess at one. The fact stands: the
EIV correction has a cell-dependent failure mode that more data does not fix.

### What one survey can resolve, as a function of pi

Single-replicate z on the matched-vs-random contrast at n = 1000, and the n needed for
z = 2.8:

| cell | z @ pi=0.02 | 0.05 | 0.10 | 0.20 | 0.30 | n needed @ pi=0.10 | @ pi=0.30 |
|---|---|---|---|---|---|---|---|
| llama-2/EXT | 0.034 | 0.087 | 0.174 | 0.347 | 0.521 | 259,511 | 28,855 |
| big5/EXT | 0.041 | 0.097 | 0.200 | 0.366 | 0.562 | 195,859 | 24,819 |
| gpt-3.5/EXT | 0.042 | 0.100 | 0.210 | 0.406 | 0.650 | 177,670 | 18,582 |
| gpt-4/EXT | 0.077 | 0.172 | 0.344 | 0.696 | 1.112 | 66,083 | 6,344 |
| gpt-3.5/AGR | 0.077 | 0.192 | 0.382 | 0.780 | 1.159 | 53,596 | 5,840 |
| llama-2/OPE | 0.142 | 0.347 | 0.617 | 1.169 | 1.651 | 20,571 | **2,875** |

z scales as roughly `pi^0.9`, so the required n falls as roughly `pi^-1.8`. This **materially
refines** `LAYERB-SWEEP.md`'s "not licensed" item 3, which read *"a single n = 1000 survey
cannot resolve the matched-vs-random contrast in any cell (best single-replicate z = 0.58,
requiring n >= 23,128)"*. That is correct at pi = 0.10 and stays correct. But at pi = 0.30 the
most favourable cell needs only **n ~ 2,875**, and the best single-replicate z actually observed
anywhere in the box is **2.531** (llama-2/OPE, pi = 0.30, n = 2500) — within reach of a single
ordinary survey. **Resolvability is not a fixed property of the design; it is governed by pi,
and it becomes feasible somewhere between pi = 0.10 and pi = 0.30.**

---

## Part V. What sweep 2 licenses

Licensed, on top of `LAYERB-SWEEP.md` section 8:

1. **(E7) holds across pi in [0.02, 0.30] and n in [500, 2500]**, 270 arm-points, max 2.88 MCSE.
   Combined with sweep 1's 20 cells, the identity is now checked over both cuts of the design.
2. **Att is monotone in pi, invariant in n, and crosses 1 in 6 of 6 cells by pi = 0.30** — three
   of them by pi = 0.02. Matched ghost respondents inflate the observed correlation by about
   71% in the worst cell measured (gpt-3.5/AGR at pi = 0.30).
3. **pk_human chunk scores exist and reproduce lane 1's 0.2083 exactly** on the full pool.
4. **The disattenuation machinery is arithmetically correct**, proven by the k = 4 oracle
   control at 1.71 MCSE on a clean sample.
5. **Contamination is not neutralized by going multi-item** (+3.5% to +9.2% from p = 0 to p = 1
   at k = 4).
6. **The adjusted-count prevalence estimator tracks pi with slope 0.79-1.20** where the detector
   is usable, and its error is a calibration-transfer offset the two-term law explains at
   corr 0.9963.
7. **Required n for the matched-vs-random contrast falls as roughly `pi^-1.8`**, reaching
   n ~ 2,875 at pi = 0.30 in the most favourable cell.

Not licensed, and the paper must not claim it:

1. **Between-chunk consistency does not identify `rel_H` on this corpus.** Weak-H2 fails by
   6-12x on the reliability and 60-82% on `rho_T`, on chunk scores that are biased
   *optimistically* because they are in-sample. The failures are a floor.
2. **The distribution-match prevalence estimator is not usable, for level or for change.** Its
   slope on true pi is 0.31-0.48 in 5 of 6 cells.
3. **The adjusted-count estimator is not a usable absolute prevalence**, only potentially a
   change detector between identically-calibrated waves, and it is **undefined** wherever the
   detector is at or below chance — a case that is now refused rather than silently returned.
4. **The EIV correction has an unexplained cell-dependent failure mode** (2 of 6 cells, median
   error 8-12%, max 42%) that does not shrink with n and is not a clean function of g.
5. Nothing about `rho_v > 0`, real survey outcomes, or any k other than 1 and 4.
6. Nothing about pi > 0.30 or n > 2500.

## Part VI. What runs next

1. **Ask lane 3 to re-derive the chunk scores out-of-fold.** This is now the single highest-value
   dependency: every weak-H2 number in Part III is measured on in-sample chunk scores and is
   therefore optimistic, and weak-H2 fails anyway. Whether it fails by *this much* is unknown
   until the chunk scores are cross-fitted the way the whole-text scores already are. Lane 3's
   own memo contradicts itself on this point (`POOL-MEASUREMENTS.md` ~225 vs ~241) and should be
   reconciled.
2. **Isolate the EIV failure mode.** Six cells cannot separate g from `c`, kappa and delta. A
   targeted run over the full 20 cells at pi in {0.10, 0.30}, scoring EIV error against all four,
   would identify it; at Part IV's measured rate that is roughly 20 minutes.
3. **Characterise the adjusted-count offset across many random calibration splits**, still open
   from `LAYERB-SWEEP.md` section 9 item 2. Part IV shows the offset is stable *in pi*, which
   makes the split-to-split spread the only thing between it and a usable change detector.
4. **Re-examine the distribution-match estimator's slope.** A slope of 0.31-0.48 is specific
   enough to be diagnosable, and llama-2/OPE's 0.935 shows it is not intrinsic to the method.
5. **Initialize a git repository.** There is none, so none of this session's edits —
   `estimators.py`, `CONVENTIONS.md`, `README.md` — is under version control.

SWEEP2-DONE
