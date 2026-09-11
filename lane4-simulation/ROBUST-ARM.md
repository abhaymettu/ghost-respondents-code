# Robust-estimator arm: results (QUEUE item 3)

Run 2026-09-10, 72 cells (the exact Layer B boundary map, LAYERB-GRID.md section 5: `n =
1000`, core box, all `pi x detector x p`), 100 reps each, 326 s on 10 workers, zero failed
cells. Spec: `ROBUST-ARM-SPEC.md`. Estimators: `estimators.py::fit_robust_t` (Minimum
Covariance Determinant, a distance-based reduction of Zhang et al. 2017's multivariate-t
robust SEM) and `fit_robust_grm` (Tukey biweight midcorrelation, a bounded-influence
reduction of robust-GRM estimation). Output in `results/robust-arm/` (`grid.jsonl`,
`cells/`), runner `run_robust_arm.py`.

**Reproduction check (ROBUST-ARM-SPEC.md section 2).** `naive` was recomputed in this run
under the identical cell_ids, `rep_rng` and `build_injected_sample` calls as the frozen
`results/layerb-grid/` record. Reconstructed naive point estimates (`truth.rho_H + bias`)
match the frozen record exactly across all 72 cells (`max |diff| = 0.0`). This run's draws
are the same draws as the boundary map's, so every comparison below is apples-to-apples.

**Bottom line: robust_t underperforms the existing five-estimator field on most of the box
and specifically at the hardest cells; robust_grm is roughly a wash on average but also loses
at the hardest cells. Neither rescues the boundary map's worst corner -- both make it worse.
This is the QUEUE's predicted result, and it held.**

## 1. The boundary map, with robust columns added

Best (smallest) absolute relative bias over the original five estimators (`naive`, `delete`,
`simex`, `labelfree`, `em`; identical to LAYERB-GRID.md section 5, quoted from the frozen
`results/layerb-grid/` record, not recomputed) next to `robust_t` (`rt`) and `robust_grm`
(`rg`), both recomputed here.

| detector | p | pi=0.01 | 0.02 | 0.05 | 0.10 | 0.20 | 0.30 |
|---|---|---|---|---|---|---|---|
| none | 0.0 | 0.082(lf)\|rt .150\|rg .117 | 0.006(nv)\|rt .014\|rg .026 | 0.046(lf)\|rt .133\|rg .122 | 0.036(lf)\|rt .204\|rg .140 | 0.099(lf)\|rt .581\|rg .295 | 0.046(lf)\|rt .444\|rg .318 |
| none | 0.5 | 0.025(nv)\|rt .047\|rg **.011** | 0.002(sx)\|rt .088\|rg .010 | 0.042(nv)\|rt .072\|rg **.025** | 0.010(nv)\|rt .073\|rg **.010** | 0.123(em)\|rt **.112**\|rg .139 | 0.153(nv)\|rt **.092**\|rg .140 |
| none | 1.0 | 0.010(nv)\|rt .067\|rg .021 | 0.074(nv)\|rt .082\|rg **.074** | 0.076(em)\|rt **.045**\|rg .070 | 0.159(nv)\|rt .190\|rg .163 | **0.335(em)**\|rt .484\|rg .363 | **0.398(em)**\|rt .653\|rg .501 |
| calibrated | 0.0 | 0.015(sx)\|rt .155\|rg .086 | 0.005(sx)\|rt .074\|rg .065 | 0.016(nv)\|rt .081\|rg .032 | 0.006(em)\|rt .206\|rg .048 | 0.013(sx)\|rt .188\|rg .136 | 0.010(sx)\|rt .353\|rg .209 |
| calibrated | 0.5 | 0.006(sx)\|rt .089\|rg .050 | 0.051(em)\|rt **.010**\|rg .036 | 0.115(nv)\|rt **.075**\|rg .107 | 0.004(dl)\|rt .038\|rg .000 | 0.004(dl)\|rt .008\|rg .004 | 0.101(sx)\|rt .148\|rg .138 |
| calibrated | 1.0 | 0.068(nv)\|rt **.009**\|rg .059 | 0.042(em)\|rt .065\|rg .031 | 0.138(nv)\|rt .177\|rg .136 | 0.113(sx)\|rt .192\|rg .204 | 0.080(sx)\|rt .375\|rg .319 | **0.316(sx)**\|rt .606\|rg .589 |
| degraded | 0.0 | 0.006(sx)\|rt .154\|rg .070 | 0.004(lf)\|rt .151\|rg .051 | 0.028(nv)\|rt .130\|rg .045 | 0.037(lf)\|rt .173\|rg .145 | 0.016(dl)\|rt .157\|rg .139 | 0.003(lf)\|rt .484\|rg .319 |
| degraded | 0.5 | 0.005(nv)\|rt .093\|rg .041 | 0.003(dl)\|rt .070\|rg .003 | 0.002(nv)\|rt .049\|rg .016 | 0.002(nv)\|rt .059\|rg .015 | 0.024(dl)\|rt .072\|rg .066 | 0.022(em)\|rt .031\|rg .059 |
| degraded | 1.0 | 0.028(sx)\|rt **.027**\|rg .045 | 0.004(dl)\|rt .011\|rg .049 | 0.029(sx)\|rt .050\|rg .086 | 0.051(sx)\|rt .184\|rg .227 | 0.054(sx)\|rt .395\|rg .370 | 0.053(sx)\|rt .590\|rg .536 |
| oracle | 0.0 | 0.006(em)\|rt .035\|rg .057 | 0.003(dl)\|rt .135\|rg .056 | 0.085(lf)\|rt .163\|rg .143 | 0.007(sx)\|rt .155\|rg .119 | 0.058(dl)\|rt .383\|rg .274 | 0.025(dl)\|rt .413\|rg .268 |
| oracle | 0.5 | 0.001(dl)\|rt .071\|rg .037 | 0.035(lf)\|rt **.019**\|rg .086 | 0.055(dl)\|rt **.011**\|rg .047 | 0.009(dl)\|rt .076\|rg .029 | 0.025(dl)\|rt .085\|rg .095 | 0.059(dl)\|rt .114\|rg **.041** |
| oracle | 1.0 | 0.052(dl)\|rt **.038**\|rg .064 | 0.011(em)\|rt .036\|rg **.004** | 0.048(nv)\|rt .051\|rg .028 | 0.053(em)\|rt .166\|rg .081 | 0.101(dl)\|rt .330\|rg .391 | 0.001(dl)\|rt .569\|rg .528 |

Bold marks a cell where a robust column beats the original five-estimator best. `rel_bias` is
signed relative bias against the truth (`rho_H` scale); the table reports its absolute value,
same convention as LAYERB-GRID.md section 5.

## 2. The boundary map's hardest corner, specifically

Section 5's reading of the original map named the top-right corner as the method's limit:
`detector = none`, `p = 1.0`, `pi >= 0.20`, where the best of the original five still carries
33.5%-39.8% relative bias. That is exactly where robust estimation was expected to lose (its
mechanism is a bounded-influence or distance-based downweighting rule, and ghost respondents
at `p = 1.0` are a mixture **component** fully coupled to the trait, not a detached tail
outlier a robust rule would isolate). It does:

| cell | best-of-5 | robust_t | robust_grm |
|---|---|---|---|
| none, p=1.0, pi=0.20 | 0.335 (em) | 0.484 | 0.363 |
| none, p=1.0, pi=0.30 | 0.398 (em) | 0.653 | 0.501 |

Both robust columns make the method's stated limit worse, not better: robust_t by 44% and
64% relative to the best-of-5 figure at these two cells, robust_grm by 8% and 26%.

## 3. Overall pattern across the 72 cells

| | naive | robust_t | robust_grm |
|---|---|---|---|
| median \|rel_bias\| | 0.071 | 0.102 | 0.072 |
| mean \|rel_bias\| | 0.126 | 0.168 | 0.131 |
| worse than naive (count / 72) | -- | 53 (74%) | 38 (53%) |
| wins outright (single best of all 7 columns) | 8 | 10 | 10 |

**robust_t is worse than naive on the large majority of cells (74%) and worse on average**
(median 0.102 vs 0.071, mean 0.168 vs 0.126). MinCovDet's robust-subset search is doing
exactly what it is built to do -- find the smallest-variance majority subset -- but on a
mixture where the contaminating component is often *not* the minority-variance subset (the
machine component's variance depends on `kappa`, and at `p > 0` it is trait-coupled, not
merely off-center), so the subset it selects does not track the human component.

**robust_grm is roughly a wash against naive on average** (median 0.072 vs 0.071, essentially
tied) but still loses at the boundary corner (section 2) and is worse than naive in 53% of
cells -- a coin flip, not an improvement. Biweight midcorrelation's bounded-influence rule
downweights points by univariate distance from the median on each variable separately; it can
happen to track pi at low contamination (many of its outright wins above are at `pi <= 0.05`,
where the naive estimator itself is already near-unbiased and the comparison is between small
numbers) but has no mechanism for the coupled, high-`pi` regime where the map's real
difficulty lives.

**Win counts do not tell a different story.** robust_t and robust_grm each win 10/72 cells
outright -- comparable to naive (8) and labelfree (9), fewer than delete (13) or simex (16).
This is the same "no cell is uniformly won" pattern LAYERB-GRID.md section 5 already reports
for the original five: adding two more non-dominant columns does not change that reading, and
most robust wins cluster at low `pi` where every column's bias is already small (section 1's
bolded cells are concentrated at `pi <= 0.10`, with only three exceptions, all softer than the
top-right corner).

## 4. What this settles

- **Second, independent line of evidence for the paper's structural-mixture claim.** Two
  estimator families built on a completely different assumption (elliptical / bounded-
  influence downweighting of outliers) than the original five (detection, mixture-model
  fitting, errors-in-variables) fail in the same place -- the high-`pi`, high-coupling,
  undetected corner -- and fail *worse* there than the field they're compared against. That
  is consistent with the QUEUE's framing: ghost respondents are a structured subpopulation
  fully coupled to the trait, not a heavy tail, so a rule built to find and discount tails
  does not find them.
- **Not a clean sweep, and this file says so.** robust_grm is a genuine near-tie with naive
  in the bulk of the box (pi <= 0.20, away from the hardest corner) -- it is not "always
  worse," only worse specifically where the paper's headline difficulty lives. Reporting it
  as uniformly worse would overstate the finding; the honest read is corner-specific failure,
  general-case wash.
- **robust_t's failure is not corner-specific -- it is general.** Worse than naive in 3 of
  every 4 cells is a broader and more legible finding than the boundary-corner-only story,
  and it is reported as such rather than folded into the (weaker) robust_grm framing.

ROBUST-ARM-DONE (2026-09-10)
