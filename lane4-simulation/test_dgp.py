"""Monte Carlo checks that dgp.py generates what CONVENTIONS.md and lane 1
specify. Plain asserts, run as `.venv/bin/python test_dgp.py`. Tolerances are
3 standard deviations of the relevant Monte Carlo statistic (stated per line).
"""

from __future__ import annotations

import sys

import numpy as np

import population as pop
from dgp import Cell, simulate

N = 400_000
FAILURES: list[str] = []


def check(name: str, empirical: float, expected: float, tol: float) -> None:
    ok = abs(empirical - expected) <= tol
    status = "PASS" if ok else "FAIL"
    print(
        f"[{status}] {name}: empirical={empirical:.5f} population={expected:.5f} "
        f"tol={tol:.5f}"
    )
    if not ok:
        FAILURES.append(name)


def se_corr(r: float, n: int) -> float:
    """Approximate SE of a sample correlation (Fisher-normal approximation)."""
    n = max(n, 4)
    return max((1.0 - r**2), 0.05) / np.sqrt(n - 3)


def se_mean(sd: float, n: int) -> float:
    n = max(n, 1)
    return sd / np.sqrt(n)


def se_var(var: float, n: int) -> float:
    n = max(n, 2)
    return abs(var) * np.sqrt(2.0 / (n - 1))


def se_prop(p: float, n: int) -> float:
    n = max(n, 1)
    return np.sqrt(max(p * (1.0 - p), 1e-6) / n)


def run_cell(cell: Cell, rng: np.random.Generator) -> None:
    tag = (
        f"[c={cell.c},kappa={cell.kappa},delta={cell.delta},"
        f"rho_v={cell.rho_v},d_theta={cell.d_theta}]"
    )
    s = simulate(cell, rng)
    theta, w, X, A, flag = s.theta, s.w, s.X, s.A, s.flag
    x1 = X[:, 0]
    mask_M = A == 1
    mask_H = A == 0
    n_M = int(mask_M.sum())
    n_H = int(mask_H.sum())

    moments = pop.population_moments(cell)

    # Cor(x1, theta | M) == c
    r = np.corrcoef(x1[mask_M], theta[mask_M])[0, 1]
    check(f"{tag} Cor(x1,theta|M)", r, cell.c, 3 * se_corr(cell.c, n_M))

    # Var(x1 | M) == s2_M
    v = x1[mask_M].var(ddof=1)
    check(f"{tag} Var(x1|M)", v, cell.s2_M, 3 * se_var(cell.s2_M, n_M))

    # Var(x1 | H) == V_H
    v = x1[mask_H].var(ddof=1)
    check(f"{tag} Var(x1|H)", v, cell.V_H, 3 * se_var(cell.V_H, n_H))

    # E[x | M] == mu_M
    m = x1[mask_M].mean()
    sd_M = np.sqrt(cell.s2_M)
    check(f"{tag} E[x|M]", m, cell.mu_M, 3 * se_mean(sd_M, n_M))

    # E[x | H] == 0
    m = x1[mask_H].mean()
    sd_H = np.sqrt(cell.V_H)
    check(f"{tag} E[x|H]", m, 0.0, 3 * se_mean(sd_H, n_H))

    # Cor(x_j, x_l | M) == r_M(c, rho_v)   (E24)
    r_M_pop = pop.r_M(cell.c, cell.rho_v)
    r = np.corrcoef(X[mask_M, 1], X[mask_M, 2])[0, 1]
    check(f"{tag} Cor(xj,xl|M) E24", r, r_M_pop, 3 * se_corr(r_M_pop, n_M))

    # Cor(x_j, x_l | H) == rel_H
    r = np.corrcoef(X[mask_H, 1], X[mask_H, 2])[0, 1]
    check(f"{tag} Cor(xj,xl|H)", r, cell.rel_H, 3 * se_corr(cell.rel_H, n_H))

    # Cor(x1, w | H) == rho_H
    r = np.corrcoef(x1[mask_H], w[mask_H])[0, 1]
    check(f"{tag} Cor(x1,w|H)", r, cell.rho_H, 3 * se_corr(cell.rho_H, n_H))

    # pooled Cor(x1, w) == population rho_obs (E5 / E21)   -- key pass-2 check
    r = np.corrcoef(x1, w)[0, 1]
    check(f"{tag} pooled Cor(x1,w) E5/E21", r, moments["rho_obs"], 3 * se_corr(moments["rho_obs"], N))

    # pooled Cor(x_j, x_l) == population r_obs   (E26)
    r_obs_pop = pop.r_obs(cell.pi, cell.c, cell.rel_H, cell.kappa, cell.delta, cell.rho_v)
    r = np.corrcoef(X[:, 1], X[:, 2])[0, 1]
    check(f"{tag} pooled Cor(xj,xl) E26", r, r_obs_pop, 3 * se_corr(r_obs_pop, N))

    # Var(x1) == V_H * Den(pi)   (E3)
    var_pop = cell.V_H * pop.Den(cell.pi, cell.kappa, cell.delta)
    v = x1.var(ddof=1)
    check(f"{tag} Var(x1) E3", v, var_pop, 3 * se_var(var_pop, N))

    # E[x1] == -pi * Delta   (E2)
    mean_pop = -cell.pi * cell.Delta
    m = x1.mean()
    sd_pooled = np.sqrt(var_pop)
    check(f"{tag} E[x1] E2", m, mean_pop, 3 * se_mean(sd_pooled, N))

    # detector: P(flag | M) == se ; P(pass | H) == sp
    se_op, sp_op = cell.se_sp
    p_flag_M = flag[mask_M].mean()
    check(f"{tag} P(flag|M)==se", p_flag_M, se_op, 3 * se_prop(se_op, n_M))
    p_pass_H = (~flag[mask_H]).mean()
    check(f"{tag} P(pass|H)==sp", p_pass_H, sp_op, 3 * se_prop(sp_op, n_H))

    # deletion selection: among passed humans
    passed_H = mask_H & ~flag
    n_pass_H = int(passed_H.sum())
    lam = moments["lam"]
    q = moments["q"]
    mean_theta_pop = cell.r_F * lam
    var_theta_pop = q
    mean_theta = theta[passed_H].mean()
    var_theta = theta[passed_H].var(ddof=1)
    sd_theta_pass = np.sqrt(max(var_theta_pop, 1e-6))
    check(
        f"{tag} mean(theta|H,pass) E32",
        mean_theta,
        mean_theta_pop,
        3 * se_mean(sd_theta_pass, n_pass_H),
    )
    check(
        f"{tag} Var(theta|H,pass) E33",
        var_theta,
        var_theta_pop,
        3 * se_var(var_theta_pop, n_pass_H),
    )

    rho_H_pass_pop = moments["rho_H_pass"]
    r = np.corrcoef(x1[passed_H], w[passed_H])[0, 1]
    check(
        f"{tag} Cor(x1,w|H,pass) E34",
        r,
        rho_H_pass_pop,
        3 * se_corr(rho_H_pass_pop, n_pass_H),
    )


def main() -> None:
    rng = np.random.default_rng(20260907)

    # Baseline plus one-at-a-time variations, covering every required value of
    # c, kappa, delta, rho_v, d_theta, plus a couple of interaction cells
    # (delta and d_theta together) needed to exercise E21's cross term.
    cells = [
        Cell(pi=0.10, c=0.0, n=N, detector="calibrated", kappa=1.0),
        Cell(pi=0.10, c=0.4, n=N, detector="calibrated", kappa=1.0),
        Cell(pi=0.10, c=0.9, n=N, detector="calibrated", kappa=1.0),
        Cell(pi=0.10, c=0.0, n=N, detector="calibrated", kappa=0.2),
        Cell(pi=0.10, c=0.4, n=N, detector="degraded", kappa=0.2, delta=0.8, rho_v=0.5),
        Cell(pi=0.10, c=0.9, n=N, detector="degraded", kappa=0.2, delta=0.8, rho_v=0.5),
        Cell(pi=0.10, c=0.0, n=N, detector="calibrated", kappa=1.0, delta=0.8),
        Cell(pi=0.10, c=0.4, n=N, detector="calibrated", kappa=1.0, rho_v=0.5),
        Cell(pi=0.10, c=0.0, n=N, detector="calibrated", kappa=1.0, d_theta=0.5),
        Cell(pi=0.10, c=0.4, n=N, detector="degraded", kappa=0.2, delta=0.8, d_theta=0.5),
        Cell(pi=0.10, c=0.9, n=N, detector="calibrated", kappa=1.0, delta=0.8, rho_v=0.5, d_theta=0.5),
    ]

    for cell in cells:
        run_cell(cell, rng)

    print()
    if FAILURES:
        print(f"{len(FAILURES)} check(s) FAILED: {FAILURES}")
        sys.exit(1)
    print("All checks PASSED.")


if __name__ == "__main__":
    main()
