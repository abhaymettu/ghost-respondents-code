"""Checks that population.py reproduces lane 1's hand-computed numbers and named
propositions. Plain asserts, run as `.venv/bin/python test_population.py`.
"""

from __future__ import annotations

import sys

import numpy as np

import population as pop

FAILURES: list[str] = []


def check(name: str, cond: bool, detail: str) -> None:
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}: {detail}")
    if not cond:
        FAILURES.append(name)


def close(a, b, tol) -> bool:
    return abs(a - b) <= tol


def main() -> None:
    # -----------------------------------------------------------------
    # (a) section 6.3 table: three hand-computed rows
    # -----------------------------------------------------------------
    rel_H, rho_T = 0.7, 0.5
    rho_H = np.sqrt(rel_H) * rho_T

    rows = [
        # sp_bar, r_F, tau, lam, psi, q, ratio
        (0.85, 0.3, -1.036, 0.274, 0.360, 0.968, 0.983),
        (0.85, 0.5, -1.036, 0.274, 0.360, 0.910, 0.951),
        (0.99, 0.5, -2.326, 0.027, 0.063, 0.984, 0.992),
    ]

    for sp_bar, r_F, tau_c, lam_c, psi_c, q_c, ratio_c in rows:
        stats = pop.selection_stats(r_F, sp_bar)
        check(
            f"tau(sp_bar={sp_bar})",
            close(stats.tau, tau_c, 1e-3),
            f"computed={stats.tau:.3f} claimed={tau_c}",
        )
        check(
            f"lam(sp_bar={sp_bar})",
            close(stats.lam, lam_c, 1e-3),
            f"computed={stats.lam:.3f} claimed={lam_c}",
        )
        check(
            f"psi(sp_bar={sp_bar})",
            close(stats.psi, psi_c, 1e-3),
            f"computed={stats.psi:.3f} claimed={psi_c}",
        )
        check(
            f"q(sp_bar={sp_bar}, r_F={r_F})",
            close(stats.q, q_c, 1e-3),
            f"computed={stats.q:.3f} claimed={q_c}",
        )
        rho_pass = pop.rho_H_pass(rel_H, rho_T, r_F, sp_bar)
        ratio = rho_pass / rho_H
        check(
            f"ratio(sp_bar={sp_bar}, r_F={r_F})",
            close(ratio, ratio_c, 1e-3),
            f"computed={ratio:.3f} claimed={ratio_c}",
        )

    # -----------------------------------------------------------------
    # (b) section 5.2 worked scale: E28a threshold gap
    # -----------------------------------------------------------------
    for kappa, claimed_threshold in [(1.0, 1.61), (0.2, 0.72)]:
        threshold = np.sqrt(kappa * 0.7 / 0.27)
        check(
            f"E28a threshold(kappa={kappa})",
            close(threshold, claimed_threshold, 5e-3),
            f"computed={threshold:.3f} claimed={claimed_threshold}",
        )

    # -----------------------------------------------------------------
    # (c) section 3.1 boundary checks
    # -----------------------------------------------------------------
    a = pop.att(0.0, 0.4, 0.7, 0.5, 0.3)
    check("att(pi=0) == 1", close(a, 1.0, 1e-12), f"att={a}")

    for c in [0.0, 0.4, 0.9]:
        a = pop.att(1.0, c, 0.7, 0.5, 0.3)
        expected = c / np.sqrt(0.7)
        check(
            f"att(pi=1, c={c}) == c/sqrt(rel_H)",
            close(a, expected, 1e-9),
            f"att={a} expected={expected}",
        )

    for pi in [0.0, 0.1, 0.3, 0.5, 0.9]:
        a = pop.att(pi, 0.0, 0.7, 1.0, 0.0)
        check(
            f"att(kappa=1, delta=0, c=0, pi={pi}) == 1-pi",
            close(a, 1.0 - pi, 1e-9),
            f"att={a} expected={1.0 - pi}",
        )

    for pi in [0.0, 0.1, 0.3, 0.5, 0.9]:
        rel_H_local = 0.7
        c_val = np.sqrt(rel_H_local)  # c^2 = rel_H
        a = pop.att(pi, c_val, rel_H_local, 1.0, 0.0)
        check(
            f"att(kappa=1, c^2=rel_H, delta=0, pi={pi}) == 1",
            close(a, 1.0, 1e-9),
            f"att={a}",
        )

    # -----------------------------------------------------------------
    # (d) Prop. 1: att_0 <= sqrt(1-pi) over a dense grid
    # -----------------------------------------------------------------
    pis = np.linspace(0.0, 0.999, 50)
    kappas = np.linspace(0.0, 2.0, 20)
    deltas = np.linspace(0.0, 2.0, 20)
    worst = -np.inf
    for pi in pis:
        for kappa in kappas:
            for delta in deltas:
                a0 = pop.att_0(pi, kappa, delta)
                bound = np.sqrt(1.0 - pi)
                worst = max(worst, a0 - bound)
    check(
        "Prop.1: att_0 <= sqrt(1-pi) over dense grid",
        worst <= 1e-9,
        f"max(att_0 - sqrt(1-pi))={worst:.3e}",
    )

    # -----------------------------------------------------------------
    # (e) Prop. 3: att_0 strictly decreasing in pi over a dense grid
    # -----------------------------------------------------------------
    pi_grid = np.linspace(0.0, 0.999, 200)
    worst_increase = -np.inf
    for kappa in np.linspace(0.0, 2.0, 10):
        for delta in np.linspace(0.0, 2.0, 10):
            vals = pop.att_0(pi_grid, kappa, delta)
            diffs = np.diff(vals)
            worst_increase = max(worst_increase, diffs.max())
    check(
        "Prop.3: att_0 strictly decreasing in pi over dense grid",
        worst_increase < 0.0,
        f"max diff (should be <0)={worst_increase:.3e}",
    )

    # -----------------------------------------------------------------
    # (f) Prop. 4 thresholds: c1 <= c2, and at kappa=1, c1==c2==sqrt(rel_H)
    # -----------------------------------------------------------------
    worst_gap = -np.inf
    for kappa in np.linspace(0.01, 5.0, 100):
        for rel_H_val in np.linspace(0.01, 1.0, 20):
            v1 = pop.c1(kappa, rel_H_val)
            v2 = pop.c2(kappa, rel_H_val)
            worst_gap = max(worst_gap, v1 - v2)
    check("Prop.4: c1 <= c2 always", worst_gap <= 1e-9, f"max(c1-c2)={worst_gap:.3e}")

    for rel_H_val in [0.3, 0.5, 0.7, 0.9]:
        v1 = pop.c1(1.0, rel_H_val)
        v2 = pop.c2(1.0, rel_H_val)
        expected = np.sqrt(rel_H_val)
        check(
            f"Prop.4: kappa=1 -> c1=c2=sqrt(rel_H) (rel_H={rel_H_val})",
            close(v1, expected, 1e-9) and close(v2, expected, 1e-9),
            f"c1={v1:.4f} c2={v2:.4f} expected={expected:.4f}",
        )

    # -----------------------------------------------------------------
    # (g) att(pi, c) crosses 1 exactly at c = c_star(pi)
    # -----------------------------------------------------------------
    for pi in [0.05, 0.1, 0.2, 0.3, 0.5, 0.8]:
        for kappa in [0.2, 0.5, 1.0, 1.5]:
            for delta in [0.0, 0.3, 0.8]:
                cs = pop.c_star(pi, rel_H, kappa, delta)
                a = pop.att(pi, cs, rel_H, kappa, delta)
                check(
                    f"att(c_star) == 1 (pi={pi}, kappa={kappa}, delta={delta})",
                    close(a, 1.0, 1e-9),
                    f"att={a:.6f}",
                )

    print()
    if FAILURES:
        print(f"{len(FAILURES)} check(s) FAILED: {FAILURES}")
        sys.exit(1)
    print("All checks PASSED.")


if __name__ == "__main__":
    main()
