"""Self-check for estimators.py. Plain asserts, PASS/FAIL printed per check.

Run: .venv/bin/python test_estimators.py
"""

from __future__ import annotations

import inspect
import sys
import time

import numpy as np

from dgp import Cell, Sample, simulate
from estimators import (Fit, _distribution_match_pi, _pearson, fit_bounds_c, fit_delete,
                        fit_em, fit_labelfree, fit_naive, fit_robust_grm, fit_robust_t,
                        fit_simex)
from population import population_moments

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(cond), detail))
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}" + (f"  ({detail})" if detail else ""))


def mc_tol(n: int, mult: float = 6.0) -> float:
    """Rough Monte Carlo tolerance for a correlation estimate at sample size n."""
    return mult / np.sqrt(n)


def assert_fit_wellformed(fit: Fit, name: str) -> None:
    ok = (
        isinstance(fit, Fit)
        and fit.name == name
        and isinstance(fit.seconds, float)
        and isinstance(fit.converged, bool)
        and isinstance(fit.note, str)
        and (fit.pi_hat is None or isinstance(fit.pi_hat, float))
        and (fit.rel_hat is None or isinstance(fit.rel_hat, float))
        and isinstance(fit.rho_H_hat, float)
        and isinstance(fit.rho_T_hat, float)
        and (fit.ci_H is None or (isinstance(fit.ci_H, tuple) and len(fit.ci_H) == 2))
        and (fit.ci_T is None or (isinstance(fit.ci_T, tuple) and len(fit.ci_T) == 2))
        and (fit.loading_hat is None or isinstance(fit.loading_hat, float))
    )
    check(f"well-formed Fit: {name}", ok, repr(fit) if not ok else "")


# --------------------------------------------------------------------------------------
# 1. Clean cell (pi = 0): every estimator recovers rho_H within MC error at n = 20000.
# --------------------------------------------------------------------------------------

print("=== Clean cell (pi=0), n=20000 ===")
# kappa != 1 (and delta != 0) so the machine/human reference distributions are
# distinguishable; at kappa=1, delta=0 they coincide and pi is unidentified,
# which is a genuine identifiability fact, not a labelfree bug.
cell_clean = Cell(pi=0.0, c=0.0, n=20000, detector="oracle", kappa=0.5, delta=0.5)
rng = np.random.default_rng(1)
sample_clean = simulate(cell_clean, rng)
tol_clean = mc_tol(cell_clean.n)
print(f"truth rho_H = {cell_clean.rho_H:.4f}, tol = {tol_clean:.4f}")

f_naive = fit_naive(sample_clean)
check("naive recovers rho_H on clean cell", abs(f_naive.rho_H_hat - cell_clean.rho_H) < tol_clean,
      f"got {f_naive.rho_H_hat:.4f}")

f_delete = fit_delete(sample_clean)
check("delete recovers rho_H on clean cell", abs(f_delete.rho_H_hat - cell_clean.rho_H) < tol_clean,
      f"got {f_delete.rho_H_hat:.4f}")

se_c, sp_c = cell_clean.se_sp
f_simex = fit_simex(sample_clean, se=se_c, sp=sp_c, B=10, rng=np.random.default_rng(2))
check("simex recovers rho_H on clean cell", abs(f_simex.rho_H_hat - cell_clean.rho_H) < tol_clean,
      f"got {f_simex.rho_H_hat:.4f}")

machine_ref_clean = np.random.default_rng(3).standard_normal(20000) * np.sqrt(cell_clean.s2_M) + cell_clean.mu_M
human_ref_clean = np.random.default_rng(4).standard_normal(20000) * np.sqrt(cell_clean.V_H)
f_lf = fit_labelfree(sample_clean, machine_ref=machine_ref_clean, human_ref=human_ref_clean,
                      method="distribution_match", B=0)
check("labelfree recovers rho_H on clean cell", abs(f_lf.rho_H_hat - cell_clean.rho_H) < tol_clean,
      f"got {f_lf.rho_H_hat:.4f}, pi_hat={f_lf.pi_hat}")

# At pi = 0 there is no second component, so the 2-component mixture is unidentified and
# EM splits a single Gaussian arbitrarily. Splitting a Gaussian along any direction
# attenuates the within-component correlation (the same conditioning mechanism as
# Prop. 11), so EM is biased LOW here by construction. That is a documented property of
# the estimator, not a defect, and it is asserted as such rather than hidden behind a
# widened tolerance. Recovery is tested below on a cell where the model is correct.
f_em = fit_em(sample_clean, n_init=5, B_boot=0, rng=np.random.default_rng(5))
check("em returns a finite, attenuated fit at pi=0 (mixture unidentified, documented)",
      np.isfinite(f_em.rho_H_hat) and f_em.rho_H_hat < cell_clean.rho_H,
      f"got {f_em.rho_H_hat:.4f} vs truth {cell_clean.rho_H:.4f} (bias low, as expected)")

# Robust estimators are less efficient than Pearson (they discard/downweight information even
# on clean data), so their MC tolerance is wider -- same n, looser bound, per ROBUST-ARM-SPEC.md.
tol_robust_clean = mc_tol(cell_clean.n, mult=15.0)
f_robt = fit_robust_t(sample_clean)
check("robust_t recovers rho_H on clean cell", abs(f_robt.rho_H_hat - cell_clean.rho_H) < tol_robust_clean,
      f"got {f_robt.rho_H_hat:.4f}")
f_robg = fit_robust_grm(sample_clean)
check("robust_grm recovers rho_H on clean cell", abs(f_robg.rho_H_hat - cell_clean.rho_H) < tol_robust_clean,
      f"got {f_robg.rho_H_hat:.4f}")

# --------------------------------------------------------------------------------------
# 2. Contaminated cell: naive attenuated per (E7); labelfree with oracle pi recovers rho_H.
# --------------------------------------------------------------------------------------

print("\n=== Contaminated cell (pi=0.10, c=0, kappa=0.5, delta=0, oracle), n=20000 ===")
cell_c = Cell(pi=0.10, c=0.0, n=20000, detector="oracle", kappa=0.5, delta=0.0)
rng2 = np.random.default_rng(10)
sample_c = simulate(cell_c, rng2)
print(f"truth rho_H = {cell_c.rho_H:.4f}")

f_naive_c = fit_naive(sample_c)
check(
    "naive attenuated on contaminated cell (E7 direction)",
    f_naive_c.rho_H_hat < cell_c.rho_H - 0.01,
    f"naive rho_H_hat={f_naive_c.rho_H_hat:.4f} vs truth {cell_c.rho_H:.4f}",
)

# Oracle pi: large reference corpora drawn from the TRUE machine/human processes so
# distribution_match recovers pi almost exactly.
n_ref = 100000
machine_ref = np.random.default_rng(11).standard_normal(n_ref) * np.sqrt(cell_c.s2_M) + cell_c.mu_M
human_ref = np.random.default_rng(12).standard_normal(n_ref) * np.sqrt(cell_c.V_H)
f_lf_c = fit_labelfree(sample_c, machine_ref=machine_ref, human_ref=human_ref,
                        method="distribution_match", c_known=cell_c.c, B=0)
tol_c = mc_tol(cell_c.n, mult=10.0)
check(
    "labelfree (oracle pi) recovers rho_H on contaminated cell",
    abs(f_lf_c.rho_H_hat - cell_c.rho_H) < tol_c,
    f"got {f_lf_c.rho_H_hat:.4f}, pi_hat={f_lf_c.pi_hat:.4f} (truth pi={cell_c.pi})",
)
check("labelfree pi_hat close to truth", abs(f_lf_c.pi_hat - cell_c.pi) < 0.02,
      f"pi_hat={f_lf_c.pi_hat:.4f}")

# EM on a correctly-specified cell (pi > 0, so two components genuinely exist). This is a
# regression test for the sklearn early-stopping defect: with max_iter=100/tol=1e-3 EM quit
# after ~8 iterations and returned 0.3360 here while reporting converged_=True.
f_em_c = fit_em(sample_c, n_init=10, B_boot=0, rng=np.random.default_rng(13))
check(
    "em recovers rho_H on contaminated cell (mixture correctly specified)",
    abs(f_em_c.rho_H_hat - cell_c.rho_H) < mc_tol(cell_c.n),
    f"got {f_em_c.rho_H_hat:.4f} vs truth {cell_c.rho_H:.4f}, pi_hat={f_em_c.pi_hat:.3f}",
)
check(
    "em beats naive on contaminated cell",
    abs(f_em_c.rho_H_hat - cell_c.rho_H) < abs(f_naive_c.rho_H_hat - cell_c.rho_H),
    f"em err={abs(f_em_c.rho_H_hat - cell_c.rho_H):.4f} vs naive err={abs(f_naive_c.rho_H_hat - cell_c.rho_H):.4f}",
)

# Contamination here is a mean/variance-shifted second Gaussian COMPONENT (c=0: no coupling
# to theta within either component), not a heavy tail on the human component -- exactly the
# case ROBUST-ARM-SPEC.md's arm 3 predicts robust methods should NOT fix, because there is no
# well-separated outlier subset for a bounded-influence rule to downweight. Asserted as a
# finite, well-formed fit only -- not required to beat or match naive, since the arm's whole
# point is to test that empirically on the real grid, not assume it in a unit test.
f_robt_c = fit_robust_t(sample_c)
check("robust_t returns a finite fit on contaminated cell", np.isfinite(f_robt_c.rho_H_hat),
      f"got {f_robt_c.rho_H_hat!r}")
f_robg_c = fit_robust_grm(sample_c)
check("robust_grm returns a finite fit on contaminated cell", np.isfinite(f_robg_c.rho_H_hat),
      f"got {f_robg_c.rho_H_hat!r}")

# --------------------------------------------------------------------------------------
# 3. Deletion-selection (lane 1 Prop. 11): r_F=0 -> no bias; r_F=0.5, sp=0.85 -> attenuated.
# --------------------------------------------------------------------------------------

print("\n=== Deletion-selection check ===")
cell_rf0 = Cell(pi=0.0, c=0.0, n=20000, detector="degraded", kappa=1.0, r_F=0.0)
sample_rf0 = simulate(cell_rf0, np.random.default_rng(20))
f_del_rf0 = fit_delete(sample_rf0)
check(
    "delete at r_F=0 recovers rho_H",
    abs(f_del_rf0.rho_H_hat - cell_rf0.rho_H) < mc_tol(cell_rf0.n),
    f"got {f_del_rf0.rho_H_hat:.4f} vs truth {cell_rf0.rho_H:.4f}",
)

cell_rf5 = Cell(pi=0.0, c=0.0, n=20000, detector="none", kappa=1.0, r_F=0.5)
# Build a custom detector operating point (r_F=0.5, sp=0.85) via a Cell using 'degraded'
# is se=sp=0.85; construct directly with detector field not matching table -> use degraded.
cell_rf5 = Cell(pi=0.0, c=0.0, n=20000, detector="degraded", kappa=1.0, r_F=0.5)
sample_rf5 = simulate(cell_rf5, np.random.default_rng(21))
f_del_rf5 = fit_delete(sample_rf5)
check(
    "delete at r_F=0.5, sp=0.85 is attenuated (Prop. 11)",
    f_del_rf5.rho_H_hat < cell_rf5.rho_H - 0.005,
    f"got {f_del_rf5.rho_H_hat:.4f} vs truth {cell_rf5.rho_H:.4f}",
)

# --------------------------------------------------------------------------------------
# 4. Degenerate input: n=30, all one class -- every estimator returns a well-formed Fit.
# --------------------------------------------------------------------------------------

print("\n=== Degenerate input (n=30, all human) ===")
cell_deg = Cell(pi=0.0, c=0.0, n=30, detector="oracle", kappa=1.0)
sample_deg = simulate(cell_deg, np.random.default_rng(30))

assert_fit_wellformed(fit_naive(sample_deg), "naive")
assert_fit_wellformed(fit_delete(sample_deg), "delete")
se_d, sp_d = cell_deg.se_sp
assert_fit_wellformed(fit_simex(sample_deg, se=se_d, sp=sp_d, B=5, rng=np.random.default_rng(31)), "simex")
mref_deg = np.random.default_rng(32).standard_normal(500)
href_deg = np.random.default_rng(33).standard_normal(500)
assert_fit_wellformed(
    fit_labelfree(sample_deg, machine_ref=mref_deg, human_ref=href_deg, method="distribution_match", B=0),
    "labelfree",
)
assert_fit_wellformed(fit_em(sample_deg, n_init=3, B_boot=0, rng=np.random.default_rng(34)), "em")
assert_fit_wellformed(fit_robust_t(sample_deg), "robust_t")
assert_fit_wellformed(fit_robust_grm(sample_deg), "robust_grm")

# All-machine degenerate cell too (pi effectively forced via a tiny all-machine sample).
X_allm = np.random.default_rng(35).standard_normal((30, 4))
w_allm = np.random.default_rng(36).standard_normal(30)
sample_allm = Sample(
    theta=np.random.default_rng(37).standard_normal(30),
    w=w_allm,
    X=X_allm,
    A=np.ones(30, dtype=np.uint8),
    F=np.random.default_rng(38).standard_normal(30),
    flag=np.zeros(30, dtype=bool),
    cell=cell_deg,
)
assert_fit_wellformed(fit_naive(sample_allm), "naive")
assert_fit_wellformed(fit_delete(sample_allm), "delete")
assert_fit_wellformed(fit_robust_t(sample_allm), "robust_t")
assert_fit_wellformed(fit_robust_grm(sample_allm), "robust_grm")

# --------------------------------------------------------------------------------------
# 5. CI machinery: on a clean cell, naive CI covers rho_H.
# --------------------------------------------------------------------------------------

print("\n=== CI coverage (naive, clean cell) ===")
cell_ci = Cell(pi=0.0, c=0.0, n=2000, detector="oracle", kappa=1.0)
n_reps = 100
covered = 0
for rep in range(n_reps):
    s = simulate(cell_ci, np.random.default_rng(1000 + rep))
    f = fit_naive(s)
    if f.ci_H is not None and f.ci_H[0] <= cell_ci.rho_H <= f.ci_H[1]:
        covered += 1
coverage = covered / n_reps
check(
    "naive Fisher-z CI covers rho_H at approx nominal rate",
    0.85 <= coverage <= 1.0,
    f"empirical coverage {coverage:.2f} over {n_reps} reps",
)

# --------------------------------------------------------------------------------------
# 6. distribution_match bin count: the prevalence response is attenuated by fine binning.
#    LAYERB-ROUND3.md 3.4 measured this on the 20 lane-3 cells and put the usable range at
#    8-15; SPEC-FIXES-ROUND3.md picks 8. The checks below pass n_bins explicitly, so they
#    hold both before and after staged/estimators-n_bins.patch changes the shipped default.
# --------------------------------------------------------------------------------------

print("\n=== distribution_match bin count ===")
_ref_rng = np.random.default_rng(7)
_H_ref = _ref_rng.normal(0.0, 1.0, 160)          # ~160 held-out texts a side, as in lane 3
_M_ref = _ref_rng.normal(0.8, 1.05, 160)
_PIS = (0.02, 0.05, 0.10, 0.20, 0.30)
_LADDER = (8, 15, 30, 60, 120)


def dm_slope(n_bins: int, reps: int = 30, n: int = 1000) -> tuple[float, float]:
    """OLS slope/intercept of mean pi_hat on true pi. Slope 1 = a change of pi is seen in full."""
    means = []
    for pi in _PIS:
        k = int(round(n * pi))
        draws = []
        for rep in range(reps):
            g = np.random.default_rng([99, rep])
            x = np.concatenate([g.normal(0.0, 1.0, n - k), g.normal(0.8, 1.05, k)])
            draws.append(_distribution_match_pi(x, _M_ref, _H_ref, n_bins=n_bins))
        means.append(float(np.mean(draws)))
    A = np.vstack([np.array(_PIS), np.ones(len(_PIS))]).T
    slope, intercept = np.linalg.lstsq(A, np.array(means), rcond=None)[0]
    return float(slope), float(intercept)


_slopes = {b: dm_slope(b) for b in _LADDER}
check(
    "n_bins=8 tracks a change in prevalence better than the shipped n_bins=60",
    _slopes[8][0] > _slopes[60][0] and abs(_slopes[8][0] - 1) < abs(_slopes[60][0] - 1),
    f"slope {_slopes[8][0]:+.3f} at 8 vs {_slopes[60][0]:+.3f} at 60",
)
check(
    "attenuation is monotone in the bin count over the 3.4 ladder",
    all(_slopes[a][0] > _slopes[b][0] for a, b in zip(_LADDER, _LADDER[1:])),
    " > ".join(f"{b}:{_slopes[b][0]:+.3f}" for b in _LADDER),
)
_shipped = inspect.signature(_distribution_match_pi).parameters["n_bins"].default
check(
    "the shipped n_bins default is a value SPEC-FIXES-ROUND3.md accounts for",
    _shipped in (60, 8),
    "60 = pre-patch (staged, grid was live); 8 = patch applied" if _shipped in (60, 8)
    else f"unrecognized default {_shipped}",
)

# --------------------------------------------------------------------------------------
# 7. bounds_c (H5 / pass3-methods-review.md B3): partial-identification bounds on rho_H
#    from a bound on c, via (E7)/(E36)'s c-affine structure. att_manual below re-derives
#    (E36) independently of population.att so this is not "test calls the function it
#    checks" -- both Att_0 (E8) and Den (from E36's denominator) are re-typed from the
#    module docstring's formulas, not imported.
# --------------------------------------------------------------------------------------

print("\n=== bounds_c ===")


def att_manual(pi: float, c: float, rel_H: float, kappa: float, delta: float) -> float:
    den = (1 - pi) + pi * kappa + pi * (1 - pi) * delta**2
    att_0 = (1 - pi) / np.sqrt(den)
    return att_0 + c * pi * np.sqrt(kappa / rel_H) / np.sqrt(den)


cell_bc = Cell(pi=0.10, c=0.4, n=20000, detector="oracle", kappa=0.5, rel_H=0.7, delta=0.0)
rng_bc = np.random.default_rng(2026091001)
sample_bc = simulate(cell_bc, rng_bc)
rho_obs_hat_bc = _pearson(sample_bc.x, sample_bc.w)

fit_bc = fit_bounds_c(sample_bc, c_lo=0.0, c_hi=1.0)
assert_fit_wellformed(fit_bc, "bounds_c")
check("bounds_c: ci_H is set", fit_bc.ci_H is not None)
check("bounds_c: converged", fit_bc.converged)

att_lo_manual = att_manual(cell_bc.pi, 0.0, cell_bc.rel_H, cell_bc.kappa, cell_bc.delta)
att_hi_manual = att_manual(cell_bc.pi, 1.0, cell_bc.rel_H, cell_bc.kappa, cell_bc.delta)
expected_lo = rho_obs_hat_bc / att_hi_manual
expected_hi = rho_obs_hat_bc / att_lo_manual
check(
    "bounds_c matches a from-scratch (E36) re-derivation, not just population.att",
    abs(fit_bc.ci_H[0] - expected_lo) < 1e-9 and abs(fit_bc.ci_H[1] - expected_hi) < 1e-9,
    f"got [{fit_bc.ci_H[0]:.6f}, {fit_bc.ci_H[1]:.6f}], expected [{expected_lo:.6f}, {expected_hi:.6f}]",
)

fit_bc_point = fit_bounds_c(sample_bc, c_lo=cell_bc.c, c_hi=cell_bc.c)
check(
    "bounds_c collapses to the point estimate when c_lo == c_hi == true c",
    abs(fit_bc_point.ci_H[1] - fit_bc_point.ci_H[0]) < 1e-9,
    f"width={fit_bc_point.ci_H[1] - fit_bc_point.ci_H[0]:.2e}",
)
check(
    "bounds_c's point-c estimate matches naive's rho_obs_hat divided by the true Att(pi,c)",
    abs(fit_bc_point.rho_H_hat - rho_obs_hat_bc / att_manual(cell_bc.pi, cell_bc.c, cell_bc.rel_H, cell_bc.kappa, cell_bc.delta)) < 1e-9,
)

fit_bc_narrow = fit_bounds_c(sample_bc, c_lo=0.3, c_hi=0.5)
w_wide = fit_bc.ci_H[1] - fit_bc.ci_H[0]
w_narrow = fit_bc_narrow.ci_H[1] - fit_bc_narrow.ci_H[0]
check(
    "bounds_c width shrinks as the c interval narrows",
    w_narrow < w_wide,
    f"width(c in [0,1])={w_wide:.4f} vs width(c in [0.3,0.5])={w_narrow:.4f}",
)

# Coverage of the true (population) rho_H by the c in [0,1] bound, over independent reps,
# at a realistic n. The bound covers the truth whenever noise in rho_obs_hat does not push
# past the endpoint set by the true c -- not a guarantee at any n, so this checks a high
# rate, not 100%.
truth_bc = population_moments(cell_bc)
n_cov_reps = 200
n_covered = 0
for rep in range(n_cov_reps):
    s = simulate(cell_bc, np.random.default_rng([2026091002, rep]))
    f = fit_bounds_c(s, c_lo=0.0, c_hi=1.0)
    if f.ci_H is not None and f.ci_H[0] <= truth_bc["rho_H"] <= f.ci_H[1]:
        n_covered += 1
check(
    "bounds_c's c in [0,1] bound covers the true rho_H in most replications at n=20000",
    n_covered / n_cov_reps > 0.85,
    f"{n_covered}/{n_cov_reps} covered, true rho_H={truth_bc['rho_H']:.4f}",
)

n_fail = sum(1 for _, ok, _ in RESULTS if not ok)
print(f"\n{len(RESULTS) - n_fail}/{len(RESULTS)} checks passed")
if n_fail:
    sys.exit(1)
