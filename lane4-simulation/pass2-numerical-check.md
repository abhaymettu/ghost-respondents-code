# Pass 2: derived moments vs the completed Layer A grid

SPEC section 7, verification pass 2. Every closed-form moment in `derivations/lane1-zero-coupling.md`
(day 1) and `derivations/lane1-partial-coupling.md` (day 2) checked against
`lane4-simulation/results/grid/grid.jsonl`.

**Bottom line: PASS.** 1116 per-cell Monte Carlo comparisons, zero failures at the Bonferroni
threshold; 142 of 142 hand-computed numbers in the two documents reproduced; 11 population
moments per cell agree with the derivations to 4.4e-16. Nothing here blocks the preprint. Five
items are logged below as flags rather than failures, of which the one that matters is a
**coverage gap, not a discrepancy**: the grid holds `delta = 0` and `d_theta = 0` in all 372
cells, so every between-mean-term result is unverified by simulation and SPEC 1.4's "Layer A
must reproduce every derived moment" is satisfied for the moments the grid contains, not for
all of them.

| input | value |
|---|---|
| grid | 372 / 372 cells, 500 reps each, zero failed cells, finished 2026-09-09 01:39 local |
| config fingerprint | `080e38c51239da1a` |
| documents | `lane1-zero-coupling.md` (E1-E34, Props. 1-11), `lane1-partial-coupling.md` (E35-E63, E75-E76, Props. 12-17) |
| grid files touched | read-only (`grid.jsonl`, `grid_run.log`, `GRID-PROGRESS.md`) |
| n_bins | no check below touches `_distribution_match_pi`, so the 60 -> 8 change of 2026-09-09 is irrelevant to every number in this report; the `labelfree` columns of the grid (the only consumer) were not used |

---

## 1. Method

### 1.1 Three independent things are being compared

1. **The derivations.** Every closed form was re-typed from the equation numbers into a fresh
   module rather than imported from `population.py`, so that agreement between the two is a
   result rather than an assumption. The transcription uses the derivations' own normalization
   (day-2 6.1: `V_H = V_w = 1`, `s2_T = rel_H`); `dgp.py` uses `s2_T = 1`, `V_H = 1/rel_H`.
   Correlations are scale-free, and the exact agreement in section 2 is the proof that the two
   normalizations describe the same population.
2. **`population.py`.** Its `population_moments(cell)` dict is inlined in every grid row.
3. **The grid's Monte Carlo output**, 500 replications per cell.

Section 2 is (1) vs (2), exact. Section 3 is (1) vs (3), Monte Carlo. Sections 4 and 5 are (1)
against itself: the printed numbers and the propositions.

### 1.2 Which empirical quantities carry a closed form

Layer A records only three quantities that a lane-1 population moment predicts directly. Every
other recorded number (RMSE, coverage, CI width, `pi_abs_err`, per-estimator timings) is an
estimator-performance result, not a derived moment, and is out of scope for pass 2.

| grid field | population limit | equations |
|---|---|---|
| `estimators.naive.rho_H.bias` + `rho_H` | `rho_obs = rho_H Att(pi, c)` | (E5), (E7); (E21) if `d_theta != 0` |
| `estimators.delete.rho_H.bias` + `rho_H` | `rho_obs,pass = rho_H Att_pass` | (E47)-(E51), through (E30), (E32), (E33) |
| `r_obs_emp.mean` | `r_obs` | (E24), (E26) |

`fit_naive` is Pearson's r on `(x, w)`; `fit_delete` is the same on the `pass` subsample
(`estimators.py:152-165`), so their population limits are exactly `rho_obs` and `rho_obs,pass`.
`r_obs_emp` is the mean of the six pairwise item correlations of `X` (`grid.py:213-216`), whose
limit is `r_obs`.

### 1.3 Monte Carlo tolerance

For each comparison, with `R` converged replications, `m` the mean of the per-rep estimates and
`s` the recorded `mcse = sd/sqrt(R)`:

    z = (m - target) / s,     target = closed form + finite-sample term

Under the null that the closed form is right, `z` is asymptotically standard normal. With
`M = 1116` per-cell comparisons, a two-sided family-wise error rate of 0.05 by Bonferroni gives

    z* = Phi^-1(1 - 0.025 / 1116) = 4.081

A comparison FAILS iff `|z| > 4.081`. At `R = 500` this is a tolerance of `4.081 * mcse`. The
mean `mcse` is 1.16e-3 for `naive`, 1.23e-3 for `delete` and 5.81e-4 for `r_obs_emp`, so the
mean tolerance in correlation units is 4.7e-3, 5.0e-3 and 2.4e-3 respectively.

**Finite-sample term.** The closed forms are `n = infinity` statements; the grid estimates them
with a Pearson correlation at `n` in {500, 1000, 5000}, whose bias is
`E[r] - rho = -rho(1 - rho^2)/(2n) + O(n^-2)`. That term is small per cell (median 0.15 and at
most 0.50 `mcse`)
but it is systematic across 372 cells, so it must be in the target or the aggregate diagnostic
misreads it as a discrepancy. It is added to every target; both corrected and uncorrected `z`
are reported. For `delete` the effective sample size is
`n_eff = n[(1 - pi) sp + pi (1 - se)]`. The formula is the bivariate-normal one and the
contaminated `x` is a mixture, so the correction is itself approximate; section 3.3 shows the
residual it leaves.

---

## 2. The derivations against `population_moments()` (exact)

Pass-1 flag **BW1** ("use population moments rather than averaged sample correlations when
checking the closed forms") is honoured: every grid row carries the full `population_moments`
dict, and it is checked against the derivation equations independently of any sample.

372 cells, 11 moments each, 4092 comparisons, tolerance 1e-12:

| moment | equation | max abs difference | verdict |
|---|---|---|---|
| `rho_H` | section 0, (E75) | 0.000e+00 | PASS |
| `rho_T` | section 0 | 0.000e+00 | PASS |
| `att` | (E7) | 0.000e+00 | PASS |
| `rho_obs` | (E5) | 0.000e+00 | PASS |
| `r_obs` | (E26), via (E24) | 0.000e+00 | PASS |
| `pi_prime` | (E30) | 0.000e+00 | PASS |
| `rho_H_pass` | (E34) | 0.000e+00 | PASS |
| `q` | (E33) | 0.000e+00 | PASS |
| `tau` | section 6.3 | 4.441e-16 | PASS |
| `lam` | section 6.3 | 3.816e-17 | PASS |
| `psi` | section 6.3 | 8.327e-17 | PASS |

The three non-zero entries are the normal quantile only: the transcription uses a rational
approximation plus two Halley steps where `population.py` uses `scipy.stats.norm.ppf`. They
agree to 4.4e-16, four orders inside the 1e-12 bar.

This also settles the normalization question: the two modules compute the same numbers from
`s2_T = rel_H, V_H = 1` and from `s2_T = 1, V_H = 1/rel_H` respectively, to zero.

---

## 3. The derivations against the grid's Monte Carlo output

### 3.1 Per-moment results

| moment | closed form | cells | mean MC tol (4.081 mcse) | mean z (uncorr.) | mean z (corr.) | max abs z | FAIL | verdict |
|---|---|---|---|---|---|---|---|---|
| `rho_obs` | (E5), (E7) | 372 | 4.7e-03 | -0.180 | -0.044 | 3.10 | 0 | **PASS** |
| `rho_obs,pass` | (E48)-(E51) | 372 | 5.0e-03 | -0.194 | -0.044 | 3.10 | 0 | **PASS** |
| `r_obs` | (E24), (E26) | 372 | 2.4e-03 | -0.407 | -0.106 | 2.87 | 0 | **PASS** |

Worst and median cell for each (empirical vs closed form, correlation units):

| moment | cell | closed form | empirical | mcse | z |
|---|---|---|---|---|---|
| `rho_obs` worst | pi=0.30, c=0.4, n=5000, kappa=0.5, none | 0.363638 | 0.361923 | 5.43e-4 | -3.10 |
| `rho_obs` median | pi=0.20, c=0.0, n=1000, kappa=1.0, degraded | 0.334664 | 0.335324 | 1.29e-3 | +0.63 |
| `rho_obs,pass` worst | pi=0.30, c=0.4, n=5000, kappa=0.5, none | 0.363638 | 0.361923 | 5.43e-4 | -3.10 |
| `rho_obs,pass` median | pi=0.20, c=0.9, n=1000, kappa=0.2, calibrated | 0.416467 | 0.415373 | 1.36e-3 | -0.64 |
| `r_obs` worst | pi=0.02, c=0.9, n=1000, kappa=1.0, calibrated | 0.702200 | 0.700547 | 5.13e-4 | -2.87 |
| `r_obs` median | pi=0.05, c=0.4, n=1000, kappa=0.5, oracle | 0.686154 | 0.685654 | 5.41e-4 | -0.59 |

Largest absolute residual, in correlation units: 3.8e-3 (`rho_obs`), 4.7e-3 (`rho_obs,pass`),
2.2e-3 (`r_obs`), against tolerances of 4.7e-3, 5.0e-3 and 2.4e-3. Mean residual across all
1116 comparisons: between -7.4e-6 and -6.7e-5.

### 3.2 Are the checks vacuous?

A check only means something if the closed form predicts a departure the Monte Carlo can see.
Predicted departure from the null "contamination does nothing", in `mcse` units:

| moment | null | median | max | cells where the predicted departure is under 1 mcse |
|---|---|---|---|---|
| `rho_obs` | `rho_H` | 6.7 | 174.5 | 64 / 372 |
| `rho_obs,pass` | `rho_H` | 2.3 | 171.1 | 122 / 372 |
| `r_obs` | `rel_H` | 22.2 | 350.4 | 14 / 372 |

The low-power cells are the small-`pi` and `oracle`/`none` ones, where the closed form itself
says the departure is nearly zero. The `rho_obs,pass` figure is dominated by the 180 cells where
the survivor formula is degenerate by construction (see 3.4).

Two sharper discriminations the grid does make:

- **The range-restriction factor `q` (E33), and with it Prop. 11 and the day-2 survivor
  result.** Re-targeting `delete` at the same formula with `q` forced to 1 -- "deletion
  preserves the human joint law", i.e. the day-1 6.1 reading in which only residual
  contamination `pi'` matters -- moves the target by a median 5.31 `mcse` at the degraded
  operating point, and **72 of 90 degraded cells reject `q = 1` at `z*`** (max 13.45). At the
  calibrated point the separation is a median 1.02 `mcse` and no cell rejects, which is the
  derivation's own reading of table 3.5 ("at the calibrated point deletion works"). The grid
  therefore does not merely fail to contradict the deletion result; it confirms the mechanism
  where the derivation says the mechanism bites.
- **The shared machine residual `rho_v` (E24).** The 12 `rho_v = 0.5` cells sit a median 33.2
  and a max 142.6 `mcse` away from their `rho_v = 0` counterparts, and all 12 pass (mean
  corrected `z` -0.272, max abs 1.67).

### 3.3 The systematic offset, and why it is not a discrepancy

The uncorrected `z` have mean -0.26, i.e. the empirical means sit slightly below the closed
forms everywhere. Aggregated over 372 cells that is a `z` of -3.5 to -7.9 per moment, which on
its own would read as a real discrepancy. It is the finite-sample bias of the Pearson
correlation, and adding the `-rho(1-rho^2)/(2n)` term removes it:

| subgroup | `rho_obs` mean z uncorr. -> corr. | `r_obs` | `rho_obs,pass` |
|---|---|---|---|
| n = 500 | -0.171 -> +0.028 | -0.637 -> -0.200 | -0.116 -> +0.104 |
| n = 1000 | -0.151 -> -0.011 | -0.346 -> -0.037 | -0.181 -> -0.026 |
| n = 5000 | -0.283 -> -0.220 | -0.368 -> -0.229 | -0.316 -> -0.246 |

The correction is largest at `n = 500`, where the offset is largest, and it flattens the
subgroup structure in `pi` and in detector as well. Across all 1116 comparisons the corrected
`z` have mean -0.0645, sd 0.9946, and KS distance 0.039 from N(0,1) (p = 0.068). The residual
-0.065 is roughly 4e-5 in correlation units: it is the `O(n^-2)` remainder plus the part of the
`O(1/n)` term that the bivariate-normal formula misses because contaminated `x` is a mixture. It
is three orders of magnitude below any claim either document makes, the `z` are not independent
across the three moments within a cell, and no subgroup deviates by more than 0.25. Recorded,
not a discrepancy.

### 3.4 Two structural notes on the `rho_obs,pass` column

- **`detector = none` (90 cells): `delete` is `naive`.** Everyone passes, so the two estimators
  see the same numbers on the same draws (verified: max difference 0.0) and the closed forms
  coincide (`pi' = pi`, `q = 1`, `lam = 0`, so (E51) reduces to (E7), which is the derivation's
  own `tau -> -inf` check). These 90 comparisons are not independent evidence for the survivor
  formula.
- **`detector = oracle` (90 cells): the target is exactly `rho_H`.** `se = 1` gives `pi' = 0`
  and `sp = 1` gives `q = 1`, so `Att_pass = 1` identically (verified: max deviation 0.0). These
  cells check that deletion at oracle quality is exactly unbiased, which is a real claim, but
  not one that exercises (E48)-(E50).

That leaves the 102 calibrated and 90 degraded cells as the genuine test of the day-2 survivor
coefficient, and it is those cells that carry the `q` discrimination above.

---

## 4. Hand-computed numbers in the two documents

Day-2 section 6.3 lists five sets of numbers "lane 4 reproduces before any of them appears in
prose". All five, plus every other number printed in either document, were recomputed from the
transcribed closed forms. **142 checks, 142 PASS**, each to the precision the document prints
(tolerance 5e-4 on a 3-decimal figure, and so on).

| block | equations | count | verdict |
|---|---|---|---|
| day-1 6.3 table: `tau`, `lam`, `psi`, `q`, `rho_H,pass/rho_H` at 3 operating points | (E32)-(E34) | 15 | PASS |
| day-2 table 1.6: 24 values of `Att(pi, c)` at `rel_H = 0.7`, `delta = 0` | (E7) | 24 | PASS |
| day-2 1.6 thresholds `c_1`, `c_2` at `kappa` in {0.2, 0.5, 1.0} | (E15), (E16) | 6 | PASS |
| day-2 1.4 numeric cross-check of (E37) against (E13) | (E13), (E37) | 5 | PASS |
| day-2 (E38) `pi_min = 0.352` and `Att` at pi = 0.30/0.35/0.40 | (E38) | 6 | PASS |
| day-1 line 169 (the D3 edit): `Att` at c = 1, kappa = 0.2 across pi, and the crossing | (E7) | 6 | PASS |
| pass-1 D2 / (E54): the `c = 1, kappa = rel_H` cell, 1.015 and 1.048, and `c*(0.1) = 0.849` | (E7), (E17), (E54) | 7 | PASS |
| day-2 (E76), (E55) window, 8.2 latent-reading numbers | (E55), (E76) | 15 | PASS |
| day-1 5.2 worked scale (H2 threshold coefficients 1.61, 0.72) | (E28a) | 3 | PASS |
| day-2 3.3/3.4: the ROC family at `d' = 2.073`, 4 rows x (se, pi', q, Att_pass), plus (E52) | (E30), (E33), (E48)-(E52) | 22 | PASS |
| day-2 3.5: 16 `Att_pass` values by operating point, plus the oracle column | (E48)-(E51) | 20 | PASS |
| day-2 3.4(iii) / (E53): the -79 SD and -15.8 SD requirements | (E53) | 8 | PASS |
| day-2 5.3: `Att_2` = 1.014, 1.19, 0.594 and the `N_2` values; 5.2's 5.44 and 0.184 | (E56)-(E60) | 8 | PASS |

Two of these deserve a note.

- **(E53) is not just reproduced, it is evaluated on the grid.** Over all 192 cells with
  `pi' > 0` and `r_F lam > 0`, the survivor flip boundary `c_flip,pass` has a maximum of
  **-10.71**. A sign flip needs `c` below that, and the grid's `c` is in {0, 0.4, 0.9}. Prop.
  14(iii) -- "the flip region is empty on the SPEC grid" -- holds on every cell actually run,
  not only at the two hand-checked points.
- **Day-1 line 169's "Att crosses 1 at pi = 0.60"** is right to the two decimals printed: the
  exact root is 0.6044, and `Att(0.60) = 0.99945`. Flagged in section 7 only so the writeup does
  not quote 0.60 as an exact crossing.

---

## 5. Propositions as properties

The propositions are statements about the closed forms rather than moments the grid records, so
they were checked by dense scan over `pi` in (0, 1) x `kappa` in {0, 0.2, 0.5, 1, 2} x `delta`
in {0, 0.5, 1, 2} x `c` in {0, 0.4, 0.9, 1} (27200 evaluation points):

| claim | statement | verdict |
|---|---|---|
| Prop. 1 (E10) | `0 < Att_0 <= sqrt(1-pi)` | PASS |
| Prop. 2 (E11) | `Att_0 > 1-pi` iff `kappa + (1-pi)delta^2 < 1` | PASS |
| Prop. 3 | `Att_0` strictly decreasing in `pi` | PASS |
| Props. 4, 12 | three regimes in `c`; (E38) locates the interior minimum | PASS |
| Prop. 5 (E17) | `Att(pi, c*(pi)) = 1` identically | PASS |
| Prop. 6 | `sign(rho_obs) = sign(rho_H)` for `c` in [0, 1] | PASS |
| Prop. 11 | `rho_H,pass < rho_H` strictly whenever `r_F != 0`, `sp_bar < 1` | PASS |
| Prop. 14(i) | `Att_pass` at `se = 1` equals the (E34) floor, independent of `pi` and `c` | PASS |
| Prop. 17 (8.2) | `sqrt(rel_H) Att < 1` everywhere on `c <= 1` | PASS |
| (E36) | `Att` affine in `c` at fixed `pi` | PASS |

---

## 6. UNVERIFIABLE: what the grid cannot check

Not failures. Each is a moment or claim that is correct as arithmetic (section 4) but has no
support in the 372 cells, because the grid does not vary the parameter it depends on. All 372
cells hold `delta = 0`, `d_theta = 0`, `rel_H = 0.7`, `rho_T = 0.5`, `r_F = 0.3`, `k = 4`.

| equations | claim | why unverifiable |
|---|---|---|
| (E2) | `E[x] = mu_H - pi Delta` | not recorded by the grid, and degenerate at `delta = 0` |
| (E3), (E4) | `Var(x) = V_H Den`, `Cov(x, w) = b s2_T N` | not recorded separately; verified only as the ratio (E5) |
| (E18) | sign flip needs `c < 0` | grid `c` in {0, 0.4, 0.9}; the region is off the grid by construction |
| (E19)-(E23), Prop. 7 | the A1' between-mean term and its flip region | `d_theta = 0` in every cell (the `nonignorable` arm exists in `grid.py:123-143` but is not in the run's 372) |
| (E28a), (E28b) | H2's homogenization-inflation threshold | needs `delta != 0`; at `delta = 0` the condition reduces to `r_M > rel_H`, and only the sign of that is exercised |
| (E29), Prop. 10 | general loadings, the rank-one authorship factor | `k = 4` parallel items only, and the rank-one term is `pi(1-pi) Delta Delta^T = 0` at `delta = 0` |
| (E34) alone | pure deletion bias at `pi' = 0`, `sp < 1` | no operating point has `se = 1` with `sp < 1`; it is verified as the `pi' -> 0` limit inside (E48)-(E51), and its `q` channel is confirmed at degraded (3.2) |
| (E40)-(E45), Prop. 13 | the general unequal-variance mixture | only the survivor special case (`q_M = 1`, `a_H != 0`) is realized; `q_M != 1` never occurs |
| (E46) | option B conversion (Q10) | `dgp.py` codes option A and `q_M = 1`, where the two coincide; nothing to convert |
| (E47) delta term | the manufactured survivor mean gap | see flag P2-4: real but 0.20 `mcse` at most |
| (E54), (E55), (E76) | exact harmlessness, the `kappa` window, the amanuensis cell | all live at `c = 1`; grid `c` maxes at 0.9 |
| (E56)-(E60), Prop. 15 | both endpoints machine-written | Layer A's `w = b theta + u` is clean by construction, so `rho_vw = 0` identically -- this is pass-1 flag **BW3**, and it is satisfied structurally rather than by choice of arm |
| day-2 8.1 pilot table | the Layer B realization on real text | Layer B, not this grid; its arithmetic reproduces (checked), its Monte Carlo is `LAYERB-PILOT.md`'s business |

---

## 7. Flags and discrepancies, with severity

No item below is an unresolved numerical discrepancy. Per the brief's gate, none of them blocks
the preprint; three are wording or scope items the writeup must respect.

**P2-1. `calibrated` means (0.95, 0.99) in the code and (0.99, 0.99) in day 2. Severity: low
(definitional), action: writeup wording.**
`dgp.py:16-21` sets `DETECTORS["calibrated"] = (se, sp) = (0.95, 0.99)`. Day-2 section 0 reads
SPEC 4.3's "calibrated" as `se = sp = 0.99`. SPEC itself (line 59) names no numbers, only
"roughly 99% in-domain down to mid-80s out of domain", so neither reading contradicts SPEC.
Consequence: **table 3.5's calibrated column does not describe the grid's calibrated cells.**
Both are correct for their own operating point (both reproduce, section 4), but a sentence of
the form "table 3.5 is what the grid ran" would be false. `degraded` and `oracle` match exactly.

**P2-2. Day-1 line 169's crossing is 0.6044, printed as 0.60. Severity: low (rounding),
action: none unless quoted as exact.** See section 4.

**P2-3. The grid holds `delta = 0` and `d_theta = 0`, so the whole between-mean-term half of the
theory is unsimulated. Severity: medium (scope), action: writeup wording, or a follow-up arm.**
This is the one item that constrains what the paper may claim. SPEC 1.4 sets "Layer A simulation
must reproduce every derived moment" as the first verification target; what pass 2 establishes
is that Layer A reproduces every derived moment **it instantiates**. The between-mean term is
not a minor corner: it is the mechanism behind H2's reliability paradox (E27, E28), the
Simpson's-structure sign flip (Prop. 7), and the rank-one authorship factor the label-free
estimator is supposed to exploit (Prop. 10). Its closed forms are verified as arithmetic and
against `population.py`, and never against a simulation. `grid.py:123-143` already contains a
`nonignorable` arm (`delta = 0.3`, `d_theta` in {0, 0.5, 1.0}, 9 cells) that is excluded from
`full_grid()` pending Abhay's Q5 call; running it would close most of this gap cheaply, and a
small `delta != 0` arm would close the rest.

**P2-4. The D1 fix touches a checkable moment, and the grid cannot resolve it. Severity: low
(informational), action: record.**
The D1 wording fix (`lane1-open-questions.md:53`) corrects day-1 6.4 on two points, and the
first is a moment: the survivor mean gap is `delta_pass = delta + r_F lam sqrt(rel_H)` (E47),
not `delta`, because the observed human mean among survivors moves even though `mu_H` and `e` do
not. That term is live in the grid's own `delete` cells -- at `delta = 0` it is not zero, it is
`r_F lam sqrt(rel_H)`, which is 0.0068 SD at calibrated and 0.0689 SD at degraded. But its
effect on the target is at most **0.20 `mcse`** (degraded; exactly 0.00 at calibrated, oracle
and none), far below `z* = 4.081`. So the corrected and uncorrected survivor formulas are
numerically indistinguishable on this grid: D1's first point is verified as arithmetic and is
UNVERIFIABLE by simulation here. D1's second point -- claim (iii), "the same mechanism, but the
flip region is empty on the grid" -- is verified, and strongly: `c_flip,pass <= -10.71` on all
192 relevant cells (section 4).

**P2-5. A systematic -0.26 mean `z` before the finite-sample correction. Severity: none
(explained), action: record.** Section 3.3.

---

## 8. Carried pass-1 flags

| flag | source | status |
|---|---|---|
| **BW1** | `pass1-diff-report.md` section 8: "use population moments rather than averaged sample correlations when checking the closed forms" | **Honoured.** Section 2 checks the derivations against the inlined `population_moments` dict, exactly, before any sample enters. The Monte Carlo comparison in section 3 is against those population moments, not against another average. |
| **BW3** | same: "the regime story assumes `rho_vw = 0`" | **Satisfied structurally.** Layer A's outcome is `w = b theta + u` with no machine branch (`dgp.py:127`), so `rho_vw = 0` identically and the (E56)-(E60) extension has no Layer A instance. The grid's `rho_v` arm is the *between-item* residual correlation (E24, 12 cells at `rho_v = 0.5`, all PASS), a different parameter. |

The three pass-1 edits that section 8 made conditions of the gate are on disk: D2 at
`lane1-zero-coupling.md:62`, D3 at `:169`, D17 at `:350` and `:352`, and D4 at `SPEC.md` 1.5, each
as a dated inline correction. The D1/N2 estimand decree is closed in `lane1-partial-coupling.md`
section 8. All four are consistent with the numbers above: section 4 reproduces the corrected D2
value (1.015 at `pi = 0.1`) and the corrected D3 series, and every check in this report is stated
against the N2 headline `rho_H = Cor(x, w | H)`.

---

## 9. Verdict

**PASS.** All moments are within Monte Carlo error.

- 4092 exactness comparisons (derivations vs `population.py`): max difference 4.4e-16, bar 1e-12.
- 1116 per-cell Monte Carlo comparisons: **0 failures** at `z* = 4.081`; max abs `z` = 3.10;
  corrected `z` distributed as N(0, 1) to KS distance 0.039.
- 142 hand-computed numbers in the two documents: **142 reproduced**.
- 10 propositions verified as properties over 27200 evaluation points.
- The grid actively confirms the day-2 range-restriction result: 72 of 90 degraded cells reject
  `q = 1` at the same threshold, so the deletion bias is not merely consistent with the data, it
  is required by it.

Nothing is blocked. The one item to carry into the writeup is P2-3: the grid holds `delta = 0`
and `d_theta = 0`, so pass 2 certifies the moments the grid instantiates, and the between-mean
term -- H2's inflation condition, Prop. 7's sign flip, Prop. 10's authorship factor -- is
certified as algebra only. Any sentence claiming the simulation reproduced *every* derived moment
should be narrowed, or the 9-cell `nonignorable` arm and a `delta != 0` arm should be run.

Method note: the checking scripts were written in the session scratchpad and are not committed,
per this pass's "no repo modifications outside the deliverable" constraint. Everything needed to
reproduce them is in sections 1.2, 1.3 and the equation numbers above; the closed forms were
transcribed from the derivations rather than imported from `population.py`, and section 2 is the
receipt that the two agree.

PASS2-DONE
---

## 10. Addendum, 2026-09-09: flag P2-3 closed by the between-mean arms

Pass 2 above returned PASS with one substantive flag, **P2-3**: all 372 cells of the frozen
grid hold `delta = 0` and `d_theta = 0`, so the between-mean half of the theory was certified
as algebra and never simulated. Q5 was decided on 2026-09-09 (run the arms). This section
reports the arms and re-runs the pass-2 checks on them. **The original verdict above is
unchanged and was not rewritten**: `results/grid/` was not reopened, and nothing in sections 1
to 9 depends on anything below.

**Result: P2-3 closes, and P2-4 closes with it.** Every closed form that P2-3 listed as
unsimulated now has a live instance and passes at the same bar. Two of them are not merely
consistent with the data but required by it: the H2 inflation threshold and Prop. 7's sign
flip both change side exactly where the closed form says they should.

### 10.1 What was run

| | |
|---|---|
| runner | `run_arms.py` (new), 10 workers, `nice -n 10`, log `nonignorable-run.log` |
| output | `results/grid-nonignorable/` (`grid.jsonl`, `cells/`, `moments.json`) |
| conventions | `reps = 500`, `master_seed = 20260907`, same `run_cell`, same `dgp.py` as the frozen grid |
| frozen grid | untouched; its fingerprint `080e38c51239da1a` is unchanged by the new arm builders, and no arm cell shares a `cell_id` with it |
| n_bins era | **post-patch (`n_bins = 8`)**. No check below touches `_distribution_match_pi`, but the arm rows' `labelfree` columns are therefore NOT comparable with the frozen grid's, which were produced at 60. |

Three arms, 20 cells, all at `n = 1000`, `kappa = 0.5`, `rel_H = 0.7`, `rho_T = 0.5`,
`r_F = 0.3`, `k = 4`:

| arm | cells | design |
|---|---|---|
| `nonignorable` (`grid.py:123-143`, as already coded) | 9 | `delta = 0.3`, `d_theta` in {0, 0.5, 1.0} x `pi` in {0.10, 0.20, 0.30}, `c = 0`, detector `none` |
| `delta` (new) | 8 | `d_theta = 0`, `delta` in {1.0, 1.5} at `pi` in {0.10, 0.30}, plus one variation each on `c = 0.9`, `rho_v = 0.5`, and detector `degraded` |
| `flip` (new) | 3 | `d_theta = 1.0`, `pi = 0.30`, `delta` in {2.5, 3.0} at `c = 0`, and `delta = 3.0` at `c = 0.4` |

The `delta` arm is built to straddle boundaries rather than to sample a region: a coverage
patch is only worth its core-hours if a wrong closed form would show. At `kappa = 0.5`,
`c = 0`, `rho_v = 0`, (E28a)'s inflation threshold is
`delta* = sqrt(kappa rel_H / ((1-pi)(1-rel_H)))` = 1.139 at `pi = 0.10` and 1.291 at
`pi = 0.30`, so `delta` in {1.0, 1.5} puts one cell on each side at each prevalence. The
`flip` arm straddles (E22)'s condition `delta d_theta > sqrt(rel_H)/pi = 2.789`, and its third
cell straddles (E23)'s `c_flip' = 0.209`. A 3-SD mean gap is a verification setting, not a
claim about any real survey: it is the cheapest place to put Prop. 7 at risk.

### 10.2 Method

Unchanged from sections 1.2 and 1.3: same transcribed closed forms, same
`z = (empirical - target)/mcse`, same finite-sample Pearson term, and the **same bar
`z* = 4.081`**, kept verbatim rather than recomputed for the smaller family so the arms are
held to the bar the frozen grid was held to (recomputing it for the new comparisons alone
would only loosen it).

One instrument is added. The grid summarizes estimator output, so pass 2 could only reach
closed forms that some estimator's plim equals; four of the equations P2-3 lists are not of
that kind. `arm_moments.py` re-simulates every arm cell from the same
`rep_rng(master_seed, cell, rep)` streams and measures the raw moments directly:
`E[x]`, `Var(x)`, `Cov(x, w)`, `Var(w)`, the item covariance matrix and the authorship mean-gap
vector. Sample means, variances and covariances are unbiased, so these carry no finite-sample
correction. Control: the correlation this pass computes reproduces the grid run's `fit_naive`
mean for the same cell to 0.0 -- the same draws, twice.

One statistic was replaced mid-analysis and the replacement is worth recording. (E29)'s
rank-one structure was first tested through the top singular value of
`Sigma_obs - (1-pi) Sigma_H - pi Sigma_M`, which flagged 2 of 21 cells. That was the
instrument, not the theory: the excess was a constant +0.005 whatever the signal
(Spearman(signal, z) = -0.75, and the two flagged cells were the two smallest signals), which
is what an upward-biased nonlinear statistic does and not what a wrong closed form does -- a
wrong closed form's excess would scale with the signal. It was replaced by the authorship
mean-gap vector `x_bar_H - x_bar_M`, which tests the same claim (loadings `Delta_j` uniform
across items, at the predicted magnitude) with a linear, unbiased statistic.

### 10.3 The three pass-2 moments on the arms

Same three moments as section 3, same bar. 20 cells x 3 = 60 comparisons:

| moment | closed form | cells | mean tol (4.081 mcse) | mean z (uncorr.) | mean z (corr.) | max abs z | FAIL | verdict |
|---|---|---|---|---|---|---|---|---|
| `rho_obs` | (E5), (E7), **(E21) where `d_theta != 0`** | 20 | 5.3e-03 | +0.115 | +0.211 | 2.18 | 0 | **PASS** |
| `rho_obs,pass` | (E48)-(E51); (E21) at detector `none` | 20 | 5.4e-03 | +0.078 | +0.180 | 2.18 | 0 | **PASS** |
| `r_obs` | (E24), (E26) | 20 | 2.1e-03 | -0.022 | +0.329 | 3.59 | 0 | **PASS** |

Largest absolute residual anywhere: 2.8e-03 in correlation units against a 5.3e-03 tolerance.

**One method note, against the arms' own evidence.** On the frozen grid the bivariate-normal
`O(1/n)` Pearson term removed a clear systematic offset (section 3.3). On these arms it does
not: the mean z moves from +0.057 uncorrected to +0.240 corrected, i.e. slightly away from
zero. That is the expected behaviour, not a new problem. The correction is the
bivariate-normal expansion, and `x` in these cells is a two-component mixture with class means
up to 3 SD apart -- strongly bimodal, where the normal-theory `O(1/n)` term is simply the wrong
expansion. Both readings are reported, and **no per-cell verdict depends on which is used**:
0 failures either way, max abs z 3.88 uncorrected and 3.59 corrected, both inside 4.081.

### 10.4 The moments the grid does not record

`arm_moments.py`, 21 cells (the 20 arm cells plus the D1 lever of 10.6), 10 moments each,
210 comparisons, no finite-sample correction needed:

| moment | equation | cells | mean z | max abs z | FAIL |
|---|---|---|---|---|---|
| `E[x]` | (E2) | 21 | +0.131 | 2.25 | 0 |
| `Var(x)` | (E3) | 21 | +0.195 | 2.16 | 0 |
| `Cov(x, w)` | (E4), (E19) | 21 | +0.156 | 2.24 | 0 |
| `Var(w)` | (E20) | 21 | -0.035 | 3.02 | 0 |
| item covariance | (E25), (E29) | 21 | +0.165 | 3.64 | 0 |
| item variance | (E3) | 21 | +0.106 | 3.33 | 0 |
| authorship mean gap, item 1 | (E29) | 21 | +0.328 | 2.28 | 0 |
| authorship mean gap, item 2 | (E29) | 21 | -0.010 | 2.00 | 0 |
| authorship mean gap, item 3 | (E29) | 21 | +0.265 | 2.49 | 0 |
| authorship mean gap, item 4 | (E29) | 21 | -0.201 | 1.72 | 0 |

**Prop. 10's asymmetry, shown directly.** The claim is that the rank-one authorship factor
`pi(1-pi) Delta Delta^T` enters every item covariance and no `Cov(x_j, w)`. Across the 12
`d_theta = 0`, `delta > 0` cells, `Cov(x, w)` matches the closed form that carries **no delta
term at all** (`b N`), with z from -0.47 to +1.71, while the rank-one term those same cells put
into Sigma runs from 0.012 to 2.70. The mean-gap rows above are the other half: the factor's
loadings are `Delta_j = Delta` in all four coordinates, on every cell.

### 10.5 The four predictions the arms were built to put at risk

Each was computed from the closed forms and written down before the cells finished.

**B1. H2's inflation condition (E28a), and the reliability paradox.** `r_obs - rel_H` must
change sign at `delta* = sqrt(kappa rel_H / ((1-pi)(1-rel_H)))` while `Att` keeps falling:

| pi | delta | vs `delta*` | `r_obs - rel_H` closed form | empirical | distance from `rel_H` | `Att` |
|---|---|---|---|---|---|---|
| 0.10 | 1.0 | below (1.139) | -0.00769 | **-0.00758** +- 0.00054 | -14.1 mcse | 0.8825 |
| 0.10 | 1.5 | ABOVE | +0.02234 | **+0.02271** +- 0.00047 | +48.7 mcse | 0.8383 |
| 0.30 | 1.0 | below (1.291) | -0.03962 | **-0.03974** +- 0.00056 | -70.7 mcse | 0.6799 |
| 0.30 | 1.5 | ABOVE | +0.02779 | **+0.02728** +- 0.00042 | +64.3 mcse | 0.6087 |

The sign turns over between `delta = 1.0` and `delta = 1.5` at both prevalences, on the side
the threshold names, tens of MCSE clear of `rel_H` in both directions. In the two ABOVE cells
the between-item correlation is above human reliability while the validity coefficient is 16%
and 39% attenuated: **the reliability paradox of day-1 section 5.2's Corollary, simulated.** A
contaminated scale reads more reliable and less valid in the same sample.

**B2. Prop. 7's sign flip (E22).** The condition is `delta d_theta > sqrt(rel_H)/pi = 2.789`
at `pi = 0.30`:

| delta | `delta * d_theta` | `rho_obs` closed form | empirical | sign | z |
|---|---|---|---|---|---|
| 2.5 | 2.50 (below) | +0.02010 | **+0.02097** +- 0.00144 | positive, as predicted | +0.60 |
| 3.0 | 3.00 (ABOVE) | -0.01305 | **-0.01257** +- 0.00144 | NEGATIVE, as predicted | +0.34 |

The pooled correlation is negative while both within-class correlations are positive. That is
the Simpson's structure of day-1 section 4b, produced on demand, on the side of the boundary
the closed form names and not on the other.

**B3. Coupling protects (E23).** At `delta = 3.0`, `d_theta = 1.0`, `pi = 0.30` the flip
threshold is `c_flip' = 0.209`, so `c = 0` must flip and `c = 0.4` must not:

| c | `rho_obs` closed form | empirical | sign | z |
|---|---|---|---|---|
| 0.0 | -0.01305 | **-0.01257** +- 0.00144 | NEGATIVE | +0.34 |
| 0.4 | +0.01193 | **+0.01190** +- 0.00142 | positive | -0.02 |

**B4. The between-mean term's magnitude (E19)-(E21).** All nine `nonignorable` cells, `rho_obs`
against (E21):

| pi | `d_theta = 0` | `d_theta = 0.5` | `d_theta = 1.0` |
|---|---|---|---|
| 0.10 | 0.38464 / **0.38574** (z +0.87) | 0.37669 / **0.37543** (z -1.05) | 0.36675 / **0.36505** (z -1.36) |
| 0.20 | 0.34998 / **0.34941** (z -0.44) | 0.33575 / **0.33549** (z -0.21) | 0.31857 / **0.31758** (z -0.77) |
| 0.30 | 0.31415 / **0.31441** (z +0.21) | 0.29532 / **0.29382** (z -1.10) | 0.27327 / **0.27600** (z +2.08) |

**These checks are not vacuous.** The A1' targets sit 6.7 to 134 MCSE away from the A1
(`d_theta = 0`) value the frozen grid would have predicted for the same cell, and the
delta-carrying `r_obs` targets sit 54 to 1445 MCSE away from their `delta = 0` counterparts. A
closed form that had the between-mean term wrong could not have hidden inside these tolerances.

### 10.6 Flag P2-4 also closes: the D1 fix is now decided by simulation

P2-4 recorded that the D1 wording fix touches a checkable moment -- the survivor mean gap is
`delta_pass = delta + r_F lam sqrt(rel_H)` (E47), not `delta` -- but that the frozen grid moves
by at most 0.20 MCSE between the corrected and uncorrected readings, because `delta = 0` there
leaves the manufactured term as the whole of it.

At `delta = 3.0` the manufactured term has a lever. One extra cell (pi = 0.30, `n = 5000`,
detector `degraded`, `c = 0`, 5000 reps, no estimators, so the reps are nearly free):

| reading | `rho_obs,pass` | z |
|---|---|---|
| **D1-corrected (E47)** | 0.309120 | **-0.35 PASS** |
| pre-D1 wording (survivor gap = `delta`) | 0.305170 | **+15.98 REJECTED** |

Empirical `Cor(x, w | pass) = 0.308990 +- 0.000242`; the two readings are 16.3 MCSE apart. The
D1 fix is confirmed by simulation and its pre-fix wording is rejected at the pass-2 bar.

### 10.7 What is still unverifiable, and why

P2-3's list is now empty. Four items from section 6 remain, none of them a between-mean item:

| equations | why still unverifiable |
|---|---|
| (E18) | the A1 sign flip needs `c < 0`; no arm carries a negative coupling, and a negative correlation between machine output and the respondent's trait is not a cell anyone has argued for |
| (E40)-(E45) with `q_M != 1` | **structurally unreachable in the current DGP**: `dgp.py:126` draws `theta = standard_normal(n) + d_theta * A`, so `Var(theta | M) = Var(theta | H) = 1` by construction and `q_M = 1` always. Reaching it needs a DGP change, not a new cell. (E46)'s option-A/option-B distinction is moot for the same reason, as day-2 section 3.1 already notes |
| (E54), (E55), (E76) | live at `c = 1`; the grid and the arms top out at `c = 0.9`. Not a P2-3 item -- logged in section 6 and unchanged |
| (E56)-(E60), Prop. 15 | Layer A's outcome `w = b theta + u` is clean by construction, so `rho_vw = 0` identically (flag BW3). Unchanged |

### 10.8 Updated flag status

| flag | section 7 status | now |
|---|---|---|
| P2-1 (`calibrated` = (0.95, 0.99) vs (0.99, 0.99)) | open, low | **unchanged** -- a definitional item for the writeup, untouched by the arms |
| P2-2 (crossing printed as 0.60, exact 0.6044) | open, low | **unchanged** |
| **P2-3 (delta = 0, d_theta = 0 everywhere)** | open, medium | **CLOSED.** 20 cells, 60 moment comparisons and 210 direct-moment comparisons, 0 failures at `z* = 4.081`; H2's threshold, Prop. 7's flip, (E23)'s protection and (E29)'s rank-one factor each verified on both sides of their own boundary |
| **P2-4 (D1 unresolvable on the grid)** | open, low | **CLOSED.** D1-corrected reading passes at z = -0.35, pre-D1 rejected at z = +15.98 (10.6) |
| P2-5 (systematic offset before correction) | explained | **refined**: on strongly bimodal cells the normal-theory `O(1/n)` term is the wrong expansion and slightly over-corrects; no verdict depends on it (10.3) |

### 10.9 Verdict on the arms

**PASS.** 60 per-cell Monte Carlo comparisons and 210 direct-moment comparisons, **0 failures**
at the pass-2 bar `z* = 4.081`, max abs z = 3.64. Nothing is BLOCKED.

The sentence pass 2 asked the writeup to narrow can now be widened back: with these arms, Layer
A reproduces every derived moment the DGP can instantiate, the between-mean half included.
SPEC 1.4's first verification target is met for all of it except the four structural gaps in
10.7, of which only `q_M != 1` would need a DGP change to close.

Reproduction: `run_arms.py --out results/grid-nonignorable` then
`arm_moments.py --out results/grid-nonignorable/moments.json`. As in pass 2, the checking
scripts are session scratchpad and not committed; the closed forms they test against are
transcribed from the derivations rather than imported from `population.py`, and `arm_moments.py`
carries its own transcription in `moments_closed_form` for the same reason.

ARM-DONE (2026-09-09)
