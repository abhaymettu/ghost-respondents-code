"""Self-check for estimators.py. Plain asserts, PASS/FAIL printed per check.

Run: .venv/bin/python test_estimators.py
"""

from __future__ import annotations

import sys
import time

import numpy as np

from dgp import Cell, Sample, simulate
from estimators import Fit, fit_delete, fit_em, fit_labelfree, fit_naive, fit_simex

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

n_fail = sum(1 for _, ok, _ in RESULTS if not ok)
print(f"\n{len(RESULTS) - n_fail}/{len(RESULTS)} checks passed")
if n_fail:
    sys.exit(1)
