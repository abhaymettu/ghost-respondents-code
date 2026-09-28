# H5 bound, detected cells: closing open item #4

Open item #4 says h5_bounds.py's E36 bound (detector=none, 18 cells) cannot be extended to
detected cells. This closes it in two parts: (A) the existing naive-based bound needs no
extension at all, because naive never sees the detector; (B) a new survivor-sample bound
(Prop. 18, derivations/lane1-detected-bound.md E77-E81, built on lane1-partial-coupling.md E47-E51) covers the 54 detected cells
(gpt-4/EXT/box/n=1000, detector x {calibrated, degraded, oracle}, pi x 6, p x 3) that h5's
bound does not.

Code: `h5_bounds_detected.py` (att_pass, --check), `r_f_estimation.py` (task 1),
`layerA_validate.py` (task 3), `layerB_apply.py` (task 4). Outputs: this file plus
the per-task JSON files `claimA_naive_invariance.json`, `r_f_estimation.json`,
`layerA_validation.json`, `layerB_application.json` (all under this directory).

## Sign convention (read before the numbers)

Two detector orientations coexist in this repo and are opposite:

- `population.py` / `CONVENTIONS.md` (E32/E33, used by every closed form here): fluency
  score `F`, HIGH = fluent = human-like, "pass" iff `F > tau`.
- `inject/pools.py`'s empirical `detector` column: HIGH = more machine-like (its own
  docstring), and `inject/build.py`'s `detector_flags` marks pass iff the pools score is
  `<= threshold` (the LOW tail).

These are a sign flip of each other, not a rescaling. So `r_F` in the population/E33
sense (what `att_pass`'s `r_F` parameter means) is

    r_F = Cor(F_population, theta) = Cor(-detector_pools, theta) = -Cor(detector_pools, theta)

and because Pearson correlation is invariant to a positive affine rescaling of either
argument, `Cor(detector_pools, theta) = Cor(detector_pools, label)` exactly (theta is an
affine rescaling of the 0/1 label). Every number below that is called "r_F_hat" or fed to
`att_pass` is already sign-corrected to the population convention; every number called
"raw" or "pools convention" is the literal correlation with the pools' own detector column.

## Claim A: the naive bound needs no extension

Naive reads `Cor(x, w)` on the full, undeleted sample -- detection never touches it -- so
h5_bounds.py's E36 bound (built entirely from naive's point estimate) should be valid
verbatim at every detector level, not just "none".

Checked on `results/layerb-grid/grid.jsonl`, gpt-4/EXT/box/n=1000, all 18 (pi, p) cells x
4 detector levels (72 cells): **max abs difference in naive's mean `rho_H` bias across
detector levels, at fixed (pi, p): 0.012367** (at pi=0.01, p=0.0).

This is not zero, but it is not a detector effect either: each detector level is a
*separate* grid cell (`LBCell.cell_id` hashes in `detector`), so it draws an *independent*
`rep_rng` stream -- four unrelated 100-rep Monte Carlo draws of the same population
quantity, not four measurements of the same draw. At n=1000/100 reps naive's MCSE is
~0.0031 (LAYERB-GRID.md 1.2), so the SE of a difference between two such independent means
is ~0.0044, and the observed max (a max over several pairwise comparisons across 4 groups,
which inflates the expected max) of 0.0124 is ~2.8x that pairwise SE -- consistent with
sampling noise, not a violation. **Claim A holds: h5_bounds.py's bound applies unmodified
at every detector level.**

## r_F and A3 estimation (task 1)

Loader: `inject.pools.lane3_pool`, `score_version="oof"` (same as `run_layerb_grid.py`),
full pools (not the frozen calibration split -- r_F and the A3 diagnostic are properties of
the detector and the corpus, not of one injected sample). Trait EXT. Bootstrap: 2000 draws,
percentile CI.

| quantity | pool | raw (pools convention, +=machine-like) | r_F fed to att_pass (population conv.) |
|---|---|---|---|
| Cor(detector, label) | pk_human (n=2467) | -0.0139, 95% CI (-0.0542, 0.0260) | **+0.0139, 95% CI (-0.0260, 0.0542)** |
| Cor(detector, trait score) | pk_human | +0.0208, 95% CI (-0.0174, 0.0583) | -0.0208 (informational; not used in att_pass, which takes r_F on the label/theta) |

`r_F_hat = 0.0139` and its CI straddles 0: on this pool the out-of-domain detector's score
carries essentially no linear signal about the EXT persona label. This is used as `r_F` in
the task-4 survivor bound; the near-zero value is also why r_F=0 vs r_F=r_F_hat barely move
anything downstream (see task 4).

A3 diagnostic (`a3_diag = Cor(detector, label)` in the MACHINE pool; near 0 supports A3 --
detector error on machine text does not depend on the trait):

| machine pool | a3_diag | 95% CI | CI covers 0 |
|---|---|---|---|
| personallm_gpt-4-0613 (n=320) | +0.0695 | (-0.0426, 0.1833) | **yes** |
| personallm_llama-2 (n=320) | -0.1761 | (-0.2687, -0.0739) | **no** |

A3 is not rejected for the gpt-4 pool used in task 4's application. It **is** rejected
(95% CI excludes 0) for llama-2/EXT: the detector's error there is not trait-blind. This is
reported plainly and not corrected for -- llama-2 is not part of task 4's 54-cell
application, and no claim in this file rests on A3 holding for llama-2.

## att_pass and its --check (task 2)

`h5_bounds_detected.py` implements (E47)-(E51) as `att_pass(pi, c, rel_H, kappa, delta,
rho_T, r_F, se, sp)`, reusing `population.selection_stats` (tau, lambda, psi, q, E33)
unchanged. `python h5_bounds_detected.py --check`: **ALL CHECKS PASSED**, specifically:

- (i) r_F=0 -> equals `population.att(pi', c, rel_H, kappa, delta)`, 3 parameter points, diff=0 (machine precision).
- (ii) se=0, sp=1 -> equals `population.att(pi, c, ...)`, 3 points, diff=0.
- (iii) pi=0 -> equals the (E34) ratio `rho_H_pass / rho_H`, 3 points, diff <= 1.1e-16.
- (iv) affinity: second difference in c over {0, 0.379, 0.758} is exactly 0 (<=7.7e-16) at 5 random parameter draws -- Att_pass is affine in c, as (E48)-(E51) predict (c enters only through `pi' * g` in N_pass).
- (table 3.4, covered by the full-table check) table 3.4 row tau=-1.036: got 0.93976, want 0.940, diff 2.4e-4 (tol 5e-4).
- (table 3.5, covered by the full-table check) table 3.5 row (kappa=0.2, c=0, r_F=0.3, degraded): got 0.97132, want 0.971, diff 3.2e-4.
- (v-c)/(vi) bonus, not required by the brief: the full table 3.4 ROC family (4 rows) and the full table 3.5 (4 rows x 5 columns, including "calibrated" at (se,sp)=(0.99,0.99) per the table header) all reproduce within 5e-4 (oracle column exact to 1e-9).

## Layer A (Gaussian DGP) validation (task 3)

`dgp.py` already implements the E32/E33 detector exactly (Gaussian threshold on
`F = r_F*theta + sqrt(1-r_F^2)*eta`, pass iff `F > tau`, machine flag ~ Bernoulli(se)
independent of theta -- A3 by construction), so no separate simulator was written, per the
brief's fallback clause. rel_H=0.7, kappa=0.2, delta=0, rho_T=0.5 (lane1's hand-computed
values, same as tables 3.4/3.5), n=1000, 500 reps, detector="degraded" (se=sp=0.85), pi in
{0.1, 0.3}, c in {0, 0.4, 0.9}, r_F in {0, 0.3} (12 cells).

**Mean-matches-prediction check.** 10/12 cells have `mean(survivor Cor(x,w))` within 2 MCSE
of `rho_H * att_pass(...)`. The two that don't: pi=0.3, c=0, r_F=0.3 (-2.97 MCSE) and
pi=0.3, c=0.4, r_F=0.3 (-2.19 MCSE) -- both small, both in the direction of the MC mean
running slightly low, and with 12 cells tested at a 2-sigma bar, 1-2 misses is within the
expected false-flag rate; reported as-is rather than rounded away.

**Imbens-Manski survivor-bound coverage**, c_bound = [0, 0.9] (this validation's own c grid,
span used deliberately so every tested true c in {0, 0.4, 0.9} sits inside it):

| | min coverage | mean coverage | cells >= 95% |
|---|---|---|---|
| r_F known (used correctly) | 0.938 | 0.960 | 10/12 |
| r_F misspecified as 0 (true r_F=0.3) | 0.932 | 0.951 | 3/6 |

r_F known: 10/12 cells clear the 95% bar, the other two (0.938, 0.944) are close.
Misspecifying r_F as 0 when it is really 0.3 costs little at these c and pi levels (mean
coverage drops from ~0.96 to ~0.95, still only slightly under nominal) -- consistent with
r_F entering (E48)-(E50) only through second-order `pi' * lambda` terms that are small at
pi <= 0.3.

## Layer B application, 54 detected cells (task 4)

gpt-4/EXT/box/n=1000, detector in {calibrated, degraded, oracle} x pi (6) x p (3), rebuilt
with `run_layerb_grid.py`'s own `LBCell`/`rep_rng`/`setup`/`MASTER_SEED` (bit-identical
samples to the frozen grid: cross-checked one cell's mean naive point estimate against
`grid.jsonl` and it matches to the printed precision, e.g. pi=0.10/p=0.5/calibrated:
0.0686080 both ways). Only `fit_naive`/`fit_delete`-equivalent Pearson correlations were
computed per rep (not the full 8-estimator suite) -- **100 reps, 54 cells, 22.0 s total**,
no need to drop to 50 reps. kappa=0.798, delta=0.534, rel_H=0.018255429162021216,
rho_H_true=0.06755632679849685, c in [0, 0.379]. se/sp fed to `att_pass` are each cell's
REALIZED rates on the fixed injection pools (constant across reps): calibrated
(se=0.263, sp=0.989), degraded (se=0.688, sp=0.849), oracle exactly (1.0, 1.0) by
construction (perfect detection is forced, matching `run_layerb_grid.py`'s override).

| detector | naive median width | naive mean coverage | naive cells >=95% | survivor(r_F_hat) median width | survivor(r_F_hat) mean coverage | survivor(r_F_hat) cells >=95% | survivor(r_F=0) median width | survivor(r_F=0) mean coverage | survivor(r_F=0) cells >=95% | share cells survivor narrower |
|---|---|---|---|---|---|---|---|---|---|---|
| calibrated | 0.1348 | 0.962 | 14/18 | 0.1339 | 0.961 | 14/18 | 0.1339 | 0.961 | 14/18 | 0.600 |
| degraded | 0.1346 | 0.972 | 17/18 | 0.1412 | 0.969 | 15/18 | 0.1413 | 0.969 | 15/18 | 0.278 |
| oracle | 0.1350 | 0.966 | 14/18 | 0.1284 | 0.955 | 13/18 | 0.1284 | 0.955 | 13/18 | 0.881 |

(mean coverage and the ">=95%" cell counts are both per detector group, from
`layerB_application.json`'s `summary_by_detector`; a handful of individual cells sit below
95% in every group, most often at low pi where n_pass is small and the Fisher CI is wide
relative to the true effect.)

r_F_hat (0.0139) and r_F=0 give **essentially indistinguishable** widths and coverage at
every detector level (differences in the 4th decimal), because r_F_hat is itself
indistinguishable from 0 on this corpus (task 1's CI straddles 0). This is a real result,
not a shortcut taken to save work: with this detector and this pool, the survivor bound's
sensitivity to r_F misspecification is moot in practice, because r_F is measured to be
negligible.

**Oracle collapses to the E34 ratio, as expected.** At se=sp=1 exactly, `pi_prime(pi,1,1) =
0` for every pi < 1, so `att_pass` loses all dependence on c (the only c-term is `pi' * g`)
and the survivor bound's width comes ENTIRELY from the Fisher-z sampling CI on the survivor
correlation, none from c-identification uncertainty. This is why oracle has both the
narrowest survivor bound (0.1284, vs 0.1339-0.1412 at calibrated/degraded) and the highest
share of cells where survivor beats naive (0.881): oracle detection removes essentially all
machine contamination from the sample it leaves behind, so the only bound-widening term
left is ordinary sampling noise on ~(1-pi) x n humans.

**Degraded is the one place survivor loses to naive most often** (narrower only 28% of
cells): at se=0.688 the detector still misses about a third of the machine text, so
deleting on this detector removes signal without removing much bias, while shrinking n_pass
(sampling loss) and leaving Att_pass's own uncertainty band similar in width to Att's --
net, the survivor bound is often not worth it at this operating point, which matches the
qualitative story in section 3.5 of lane1-partial-coupling.md ("a better detector, in the
sense of a higher threshold, is not always less bias").

## What passed, what failed, stated plainly

- Claim A (naive needs no extension): **holds**, confirmed on all 72 relevant grid cells; the one non-zero number (0.0124 max diff) is explained as MC noise, not rounded to zero.
- att_pass (E47-E51) implementation: **all --check items pass**, including two exact table reproductions from the derivation and 8 bonus reproductions (full tables 3.4, 3.5).
- Layer A Monte Carlo validation of E51: mean-matches-prediction holds in 10/12 cells within 2 MCSE (2 cells run slightly hot, largest -2.97 MCSE); coverage with r_F known clears 95% in 10/12 cells (min 0.938); coverage with r_F misspecified as 0 clears 95% in only 3/6 cells (min 0.932, mean 0.951) -- a real but small undercoverage, not "passes at nominal."
- Layer B application: both bounds hit their nominal coverage closely (0.955-0.972) across all three real detector levels on gpt-4/EXT; the survivor bound is narrower than naive on a majority of cells only at calibrated (60%) and oracle (88%), and on a MINORITY at degraded (28%) -- so the new bound is not a strict improvement everywhere, and this file says so rather than reporting only the favorable cells.

## Commands run

```
lane4-simulation/.venv/bin/python r_f_estimation.py           # ~1.0 s
lane4-simulation/.venv/bin/python h5_bounds_detected.py --check   # ~2.4 s (wall, incl. import)
lane4-simulation/.venv/bin/python layerA_validate.py           # ~2.9 s
lane4-simulation/.venv/bin/python layerB_apply.py --reps 100   # ~23.3 s (22.0 s of that inside the loop)
```

Total wall time for this close-out, all four scripts: well under a minute; no need to drop
Layer B to 50 reps.
