# Open item #4: the H5 bound on detected cells

2026-09-27, overnight agentSEM lane. Conventions as in the day-1 and day-2 files. Equations continue
from (E77), propositions from Prop. 18. Numbers in section 5 come from
`lane4-simulation/h5_bounds_detected.py` and `lane4-simulation/H5-DETECTED.md`. None are hand-typed here
before that script has run.

## 1. What the open item says, and what it gets wrong

`paper/GAPS-CLOSURE-SPEC.md` item 2 and `paper/FINAL-PASS-REPORT.md` section 3 both say that the H5 bound
covers only the 18 detector = none cells, because "detection adds a selection term (E30 to E34, r_F) that is
not part of E36". That is true of an estimator that conditions on the detector. It is **not** true of the
bound as built. `h5_bounds.py` and `fit_bounds_c` both invert naive's `rho_obs_hat`, which is `Cor(x, w)` on
the full, undeleted sample. `fit_bounds_c`'s docstring says so ("no detector-dependent filtering").
Detection never touches that sample. So:

**(E77)** For every detector level, `rho_H in [rho_obs / Att(pi, c_hi), rho_obs / Att(pi, c_lo)]`, with
`Att` from (E36).

This needs no new derivation. It follows from the fact that the naive sample is the same at every detector
level. The script checks that fact on the frozen grid (test A). So the bound already covers all 72
boundary-map cells, conditional on a known `pi`, as before.

What does need a derivation is the bound that *uses* the detector: the survivor sample after
detect-and-delete. The question is whether throwing away flagged rows buys a narrower c-interval than the
naive bound, and what it costs in assumptions.

## 2. Lemma D1: affinity in c survives deletion, distribution-free

Assume:

- (i) **A3.** `P(pass | M, theta, x, w) = 1 - se`. Detector error on machine text is blind to the trait
  and to the scores.
- (ii) **Option A** (day-2 section 2). In class M, the mean `mu_M`, the variance `s2_M` and the joint law
  of `(theta, w)` do not depend on c. Only `Cov(x, theta | M) = c sqrt(s2_M s2_T)` moves with c.
- (iii) `w = b theta + u`, with `u` independent of `(theta, x, F, class)`.
- (iv) Nothing on the human side depends on c.

On the survivor population, write `pi'` for the machine share (E30). Under (i), it does not depend on c.
Then

    Var_pass(x) = (1 - pi') Var(x | H, pass) + pi' s2_M + pi' (1 - pi') (E[x | H, pass] - mu_M)^2
    Var_pass(w) = (1 - pi') Var(w | H, pass) + pi' Var(w | M) + pi' (1 - pi') (E[w | H, pass] - E[w | M])^2
    Cov_pass(x, w) = (1 - pi') Cov(x, w | H, pass) + pi' Cov(x, w | M)
                     + pi' (1 - pi') (E[x | H, pass] - mu_M) (E[w | H, pass] - E[w | M])                  (E78)

By (i), the class-M moments among survivors equal the class-M moments, because the survivors are a random
thinning of M. By (ii) and (iv), every term except `Cov(x, w | M)` is free of c. By (ii) and (iii),
`Cov(x, w | M) = b Cov(x, theta | M) = b c sqrt(s2_M s2_T)`. Hence

    rho_obs,pass(c) = rho_obs,pass(0) + c * pi' b sqrt(s2_M s2_T) / sqrt(Var_pass(x) Var_pass(w))           (E79)

This is affine in c, strictly increasing when `b > 0` and `pi' > 0`. No normality was used.

Dividing by `rho_H` gives `Att_pass(c) = Att_pass(0) + c * s_pass`. The Gaussian closed form is
(E48) to (E51). There c enters only through the `pi' g` term of `N_pass`, and `Den_pass` and `W_pass` are
free of c, so

    s_pass = pi' sqrt(kappa / rel_H) / sqrt(Den_pass W_pass)                                                 (E80)

Check: at `se = 0, sp = 1`, `pi' = pi`, `q = 1`, `W_pass = 1` and `Den_pass = Den`, so (E80) is the E36
slope. QED.

## 3. Prop. 18: the survivor bound

Under Lemma D1, with `c in [c_lo, c_hi]`, `Att_pass(c_lo) > 0`, and `(pi, se, sp, r_F, kappa, delta,
rel_H, rho_T)` known:

    rho_H in [ rho_pass / Att_pass(c_hi),  rho_pass / Att_pass(c_lo) ]      (rho_pass >= 0; swap if negative)  (E81)

Proof: monotone inversion of (E79). For the sampling version, union the Imbens-Manski interval with a
Fisher-z CI on `rho_pass`, computed at `n_pass = n [ (1 - pi) sp + pi (1 - se) ]`, as `fit_bounds_c` does.
QED.

**Identification width.** The c-part of the width is

    rho_H * (c_hi - c_lo) * s * Att(c) / (Att(c_lo) Att(c_hi))

with `s` the slope and `Att(c)` the attenuation at the true c, for either bound. To first order in pi,
`s_pass / s_naive = (pi' / pi) sqrt(Den / (Den_pass W_pass))`, and `pi' < pi` iff `se + sp > 1`. So a
detector better than chance narrows the c-part of the interval, roughly by the share of machine text it
removes. This is the only thing deletion can buy for H5.

**What it costs.**

1. **r_F must be known.** Range restriction on the humans (q) and the manufactured mean term shift
   `Att_pass(0)`. If r_F is misspecified, the interval moves; it does not widen. That is a bias, not a
   coverage-preserving uncertainty. The fix is to bracket r_F as well. Att_pass is not monotone in r_F in
   general, because (E48) has a term linear in r_F with the sign of delta. [Corrected per section 7: the
   earlier citation of Prop. 14 (ii) was wrong, since that result concerns tau. The bracket is closed-form (L12 in
   the cross-check); no grid union is needed.]
2. **A3 must hold.** Under assignment-coupled injection, machine texts are assigned by theta. If the
   detector score of a machine text tracks its persona label, pass depends on theta within M. Then (i)
   fails, the survivor class-M moments differ from the class-M moments, and the survivor c is not the pool
   c. The diagnostic is `Cor(F, label | machine pool)`.
3. **Fewer rows.** `n_pass < n` widens the sampling part by about `sqrt(n / n_pass)`.

**Oracle.** At `se = sp = 1`, `pi' = 0` and `s_pass = 0`, so the c-part vanishes. Every human survives
(sp = 1 means `psi = 0`, `q = 1`), and `Att_pass = 1`. The bound is the sampling CI alone, which is the
one case where deletion is exactly right. This matches Prop. 14 (i): only `sp -> 1` removes the deletion
bias.

## 4. Consequence for the draft

- The H5 Limitations bullet and FINAL-PASS-REPORT section 3 overstate the gap. The naive bound (E77) holds
  on all 72 cells. The draft should say so, and cite test A.
- The survivor bound (E81) is new. It is narrower exactly when the detector removes machine text faster
  than humans (`se + sp > 1`). It is valid only under A3 with r_F known or bracketed. On Layer B, both
  conditions are checked from the pools, not assumed.
- What stays open is the bound when `pi` is itself unknown. The union over a `pi` sweep is still not
  computed (section 5.3 of the draft).

## 5. Numbers

From `lane4-simulation/results/h5-bounds-detected/H5-DETECTED.md` and the per-task JSON files
(2026-09-27, 22.0 s Layer B run, rebuilt bit-for-bit from the grid's own seeding).

**Test A (E77).** Across the four detector levels at fixed (pi, p), naive's mean `rho_H` bias differs by
at most 0.0124 (18 (pi, p) pairs x 4 levels). The levels are separate cells with independent rep streams;
the SE of a pairwise difference is about 0.0044, so this is Monte Carlo noise. The structural argument
(naive never reads the flag) is what carries the claim, and the number does not contradict it.

**r_F and A3 on the real pools** (2000-draw bootstrap, OOF scores, sign mapped to the E33 convention):
`r_F_hat = +0.014 [-0.026, 0.054]` on the human pool (n = 2467), indistinguishable from 0. The A3
diagnostic `Cor(F, label | M)` is `+0.070 [-0.043, 0.183]` for gpt-4, where A3 is not rejected, and
`-0.176 [-0.269, -0.074]` for llama-2, where **A3 is rejected**. [Superseded by section 7: on the gpt-4
*injection half* that the grid actually uses, the diagnostic is +0.183 (n = 160, SE about 0.079). **A3 fails on
both pools** as used in Layer B. The r_F figures are also ill-posed on real text; see section 7.]

**Layer A validation** (Gaussian DGP, where truth is exact: 12 cells, 500 reps, n = 1000, degraded
detector). The mean survivor correlation matches `rho_H Att_pass` within 2 MCSE in 10 of 12 cells
(worst -2.97 MCSE). Imbens-Manski coverage with r_F known: mean 0.960, min 0.938, 10 of 12 at or above
0.95. With r_F = 0 assumed against a true value of 0.3: mean 0.951, min 0.932, 3 of 6 at or above 0.95.
This is the section 3 prediction: misspecified r_F shifts the interval rather than widening it.

**Layer B, 54 detected cells** (gpt-4/EXT, n = 1000, 100 reps, `c in [0, 0.379]`):

| detector | naive: median width / coverage | survivor (r_F_hat): median width / coverage | survivor narrower |
|---|---|---|---|
| calibrated | 0.1348 / 0.962 | 0.1339 / 0.961 | 60% of cells |
| degraded | 0.1346 / 0.972 | 0.1412 / 0.969 | 28% |
| oracle | 0.1350 / 0.966 | 0.1284 / 0.955 | 88% |

Reading. At n = 1000 the Fisher part of the interval is about 0.124 wide. So on this box about 0.01 of
the naive width comes from the unknown c, and that 0.01 is the most deletion can remove. The calibrated
detector removes a little of it (se 0.28). The degraded detector gives back more than it removes,
because deleting 15 percent of humans costs sampling width. The oracle removes all of it (`pi' = 0`, the
section 3 collapse). **Pooled coverage is at or above 0.955 for every bound at every detector level** (pooled over cells; per-cell coverage is in `layerB_application.json`). The substantive
result for the draft: on Layer B, the H5 interval is sampling-limited, not identification-limited.
Even a perfect detector narrows the median interval by only 4.9 percent (0.1350 to 0.1284).

## 6. Verification status

The algebra was self-checked once. A numeric check is delegated to `h5_bounds_detected.py --check`: the
reductions at `r_F = 0`, at `se = 0, sp = 1` and at `pi = 0`; affinity; and reproduction of the table 3.4
and 3.5 rows. Layer A Monte Carlo coverage is checked against the known truth. Passes 1 to 3 have not
been run on this file.

## 7. Cross-check adopted (2026-09-27 ~20:40)

An independent Opus cross-check by session bridge-jobs-6d is in
`~/lanes/bridge-jobs/agentsem-overnight-20260927/layerB-bound-derivation.md`, section 0, with numbers from
`layerB_check.py`. It confirms (E77) (to 2.8e-17 in 30 detected cells), (E78), (E79), (E80) and the oracle
paragraph. It corrects four points, all adopted here:

1. **Prop. 18 conditions on `rho_T` together with `rel_H`, and those two fix the estimand.** The effect is
   second order, through `W_pass` only (about 0.989 at r_F = 0.5, sp = 0.85). The cross-check's (L7)
   removes `rho_T` in closed form. The Layer A validation above plugged in the true `rho_T`, so it had an
   oracle input.
2. **Width.** "Narrower when se + sp > 1" holds for the identification part only. On Layer B, total
   survivor width is 0.87 to 1.09 of the undeleted width, median 1.00 (their section 9.3). This agrees with
   section 5's reading: the interval is sampling-limited.
3. **r_F has no real-text counterpart.** The Gaussian implication `r_xD = r_H r_thD` fails on the essays
   (+0.0042 against -0.0007). So `r_F_hat` in section 5 is a descriptive correlation, not an (E80) input.
   The human-side terms need the cross-check's Pearson-Lawley route (its section 4).
4. **A3 fails on Layer B, gpt-4 included,** once it is measured on the injection half the grid uses
   (+0.183), not on the full pool (+0.070). Under assignment coupling, Att_pass is then no longer affine in
   c, though it is still invertible in closed form (L11, L12). The coupling to bracket is the survivor
   coupling, not `c_pool`. Taking Lemma D1 (i) literally costs 2.7 to 5.9 percent relative error in the
   predicted survivor correlation on gpt-4, and 2.0 to 8.3 percent on llama-2.

**What stands:** (E77), so the paper's scope limit is wrong for the bound as built. The Gaussian Lemma D1
and Prop. 18 also stand, as Layer A results. **What changes:** the Layer B survivor bound is the
cross-check's closed-form version (L7, L11, L12), not (E81) with plug-in r_F. Section 5's Layer B table is
kept as a record of the plug-in run. Its coverage numbers hold, but for a bound whose assumptions A3 and
r_F are not met on this text.
