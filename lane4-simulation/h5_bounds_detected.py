"""Layer B H5 bound, DETECTED cells (open item #4): the survivor-sample extension.

h5_bounds.py's E36 bound covers detector="none" only, because rho_obs = rho_H * Att(pi, c)
(E7/E36) holds without a deletion step. Every detected cell (calibrated/degraded/oracle)
instead observes the SURVIVOR sample (D = pass), whose validity coefficient is
derivations/lane1-partial-coupling.md section 3, Prop. 14: (E47)-(E51),

    rho_obs,pass = rho_H * Att_pass(pi, c, rel_H, kappa, delta, rho_T, r_F, se, sp)   (E51)

under A3 (detector error on machine text is trait-blind: P(pass | M, theta) does not depend
on theta). Att_pass is affine and increasing in c at fixed pi, kappa, delta, rho_T, r_F, se,
sp -- exactly as Att(pi, c) is (E36) -- because c enters (E48)-(E51) ONLY through the
`pi' * g` term of N_pass, g = c sqrt(kappa/rel_H), and Den_pass, W_pass do not involve c at
all (E49, E50 -- delta_pass, q, lambda are functions of delta, r_F, se, sp, not c). So the
same Imbens-Manski construction h5_bounds.py / fit_bounds_c use for the undetected bound
applies here: propagate a Fisher-z sampling CI on rho_obs,pass through both Att_pass
endpoints (c_lo=0, c_hi=c_pool), giving

    rho_H in [ rho_pass_hat / Att_pass(pi, c_hi, ...),  rho_pass_hat / Att_pass(pi, c_lo, ...) ]

when Att_pass is increasing in c (it is, whenever g > 0, i.e. kappa, rel_H > 0), using
fit_delete's point estimate (Cor(x, w) on detector survivors) for rho_pass_hat.

r_F = -Cor(detector_pools, label); see H5-DETECTED.md section 1.

Run:
    lane4-simulation/.venv/bin/python h5_bounds_detected.py --check
"""

from __future__ import annotations

import sys

import numpy as np
from scipy.stats import norm

from population import att, pi_prime, rho_H_pass, selection_stats


def att_pass(
    pi: float,
    c: float,
    rel_H: float,
    kappa: float,
    delta: float,
    rho_T: float,
    r_F: float,
    se: float,
    sp: float,
) -> float:
    """(E51) Att_pass(pi, c) = N_pass / sqrt(Den_pass * W_pass), the survivor-sample
    attenuation factor under A1 + the Gaussian threshold detector + A3 (section 3.1-3.2).

    pi' (E30), lambda/psi/q (E33) come from population.pi_prime / population.selection_stats,
    unchanged. delta_pass (E47), N_pass (E48), Den_pass (E49), W_pass (E50) are new to this
    module. g = c sqrt(kappa / rel_H) is the same g population.N() computes internally; it is
    recomputed here (not imported) because N_pass's other two terms are not population.N()'s.
    """
    pi_p = pi_prime(pi, se, sp)

    stats = selection_stats(r_F, sp)
    lam, q = stats.lam, stats.q

    g = c * np.sqrt(kappa / rel_H)
    delta_pass = delta + r_F * lam * np.sqrt(rel_H)

    one_minus_pip = 1.0 - pi_p
    N_pass = (
        one_minus_pip * q
        + pi_p * g
        + pi_p * one_minus_pip * r_F * lam * (r_F * lam + delta / np.sqrt(rel_H))
    )
    Den_pass = (
        one_minus_pip * (1.0 - rel_H * (1.0 - q))
        + pi_p * kappa
        + pi_p * one_minus_pip * delta_pass**2
    )
    W_pass = (
        1.0
        - rho_T**2 * one_minus_pip * (1.0 - q)
        + pi_p * one_minus_pip * rho_T**2 * r_F**2 * lam**2
    )
    result = N_pass / np.sqrt(Den_pass * W_pass)
    return result if np.ndim(result) > 0 else float(result)


# --------------------------------------------------------------------------------------
# --check: unit checks (i)-(v)
# --------------------------------------------------------------------------------------


def _check() -> bool:
    ok = True
    rng = np.random.default_rng(2026)

    def report(name: str, got: float, want: float, tol: float) -> bool:
        nonlocal ok
        diff = abs(got - want)
        passed = diff <= tol
        ok = ok and passed
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}: got={got!r} want={want!r} "
              f"diff={diff:.3e} tol={tol:.1e}")
        return passed

    print("(i) r_F=0 -> att_pass equals population.att(pi', c, rel_H, kappa, delta)")
    for pi, se, sp, c, rel_H, kappa, delta, rho_T in [
        (0.10, 0.85, 0.85, 0.0, 0.7, 0.2, 0.0, 0.5),
        (0.30, 0.95, 0.99, 0.4, 0.7, 0.5, 0.3, 0.5),
        (0.05, 0.5, 0.6, 0.9, 0.5, 1.0, -0.2, 0.4),
    ]:
        num = (1 - se) * pi
        pi_p = num / (num + sp * (1 - pi))
        got = att_pass(pi, c, rel_H, kappa, delta, rho_T, 0.0, se, sp)
        want = att(pi_p, c, rel_H, kappa, delta)
        report(f"pi={pi},se={se},sp={sp},c={c}", got, want, 1e-10)

    print("(ii) se=0 & sp=1 -> att_pass equals population.att(pi, c, ...) (no deletion)")
    for pi, c, rel_H, kappa, delta, rho_T, r_F in [
        (0.10, 0.0, 0.7, 0.2, 0.0, 0.5, 0.3),
        (0.30, 0.4, 0.7, 0.5, 0.3, 0.5, 0.5),
        (0.20, 0.9, 0.5, 1.0, -0.2, 0.4, 0.7),
    ]:
        got = att_pass(pi, c, rel_H, kappa, delta, rho_T, r_F, 0.0, 1.0)
        want = att(pi, c, rel_H, kappa, delta)
        report(f"pi={pi},c={c},r_F={r_F}", got, want, 1e-10)

    print("(iii) pi=0 -> att_pass equals the (E34) ratio rho_H_pass / rho_H")
    for rel_H, kappa, delta, rho_T, r_F, se, sp in [
        (0.7, 0.2, 0.0, 0.5, 0.3, 0.85, 0.85),
        (0.5, 1.0, 0.3, 0.4, 0.5, 0.95, 0.99),
        (0.018255429162021216, 0.798, 0.534, 0.5, 0.3, 0.85, 0.85),
    ]:
        c_dummy = 0.37  # (iii) must hold for ANY c, since pi'=0 kills the g term
        got = att_pass(0.0, c_dummy, rel_H, kappa, delta, rho_T, r_F, se, sp)
        rho_H = np.sqrt(rel_H) * rho_T
        want = rho_H_pass(rel_H, rho_T, r_F, sp) / rho_H
        report(f"rel_H={rel_H},rho_T={rho_T},r_F={r_F},sp={sp}", got, want, 1e-10)

    print("(iv) affinity: second difference in c ~ 0 at 5 random parameter points")
    for _ in range(5):
        pi = float(rng.uniform(0.01, 0.30))
        rel_H = float(rng.uniform(0.02, 0.7))
        kappa = float(rng.uniform(0.2, 1.5))
        delta = float(rng.uniform(-0.5, 0.5))
        rho_T = float(rng.uniform(0.3, 0.6))
        r_F = float(rng.uniform(-0.5, 0.5))
        se = float(rng.uniform(0.1, 0.99))
        sp = float(rng.uniform(0.5, 0.999))
        c0, c1, c2 = 0.0, 0.379, 0.758
        h = c1 - c0
        y0 = att_pass(pi, c0, rel_H, kappa, delta, rho_T, r_F, se, sp)
        y1 = att_pass(pi, c1, rel_H, kappa, delta, rho_T, r_F, se, sp)
        y2 = att_pass(pi, c2, rel_H, kappa, delta, rho_T, r_F, se, sp)
        second_diff = (y2 - 2 * y1 + y0) / h**2
        report(
            f"pi={pi:.3f},rel_H={rel_H:.3f},kappa={kappa:.3f},delta={delta:.3f},r_F={r_F:.3f}",
            second_diff, 0.0, 1e-12,
        )

    print("(v) bonus: full table 3.4 ROC family (tau, sp_bar, Att_pass)")
    d_prime = 2.073
    table_34 = [
        (-np.inf, 1.00, 0.938),
        (-2.326, 0.99, 0.953),
        (-1.036, 0.85, 0.940),
        (0.0, 0.50, 0.908),
    ]
    for tau, sp_bar, att_want in table_34:
        se_row = float(norm.cdf(tau + d_prime)) if np.isfinite(tau) else 0.0
        pi_p_got = pi_prime(0.10, se_row, sp_bar)
        stats = selection_stats(0.5, sp_bar)
        got = att_pass(pi=0.10, c=0.0, rel_H=0.7, kappa=0.2, delta=0.0, rho_T=0.5, r_F=0.5,
                       se=se_row, sp=sp_bar)
        report(f"tau={tau} se={se_row:.4f} pi'={pi_p_got:.4f} q={stats.q:.4f}",
               got, att_want, 5e-4)

    print("(vi) bonus: full table 3.5 (four rows)")
    table_35 = [
        (0.2, 0.0, 0.3, 0.938, 0.971, 0.996, 0.983, 1.0),
        (0.2, 0.0, 0.5, 0.938, 0.940, 0.991, 0.951, 1.0),
        (0.2, 0.9, 0.5, 0.988, 0.949, 0.992, 0.951, 1.0),
        (1.0, 0.0, 0.5, 0.900, 0.932, 0.991, 0.951, 1.0),
    ]
    for kappa, c, r_F, none_want, degraded_want, calibrated_want, se1sp85_want, oracle_want in table_35:
        none_got = att(0.10, c, 0.7, kappa, 0.0)
        degraded_got = att_pass(0.10, c, 0.7, kappa, 0.0, 0.5, r_F, 0.85, 0.85)
        calibrated_got = att_pass(0.10, c, 0.7, kappa, 0.0, 0.5, r_F, 0.99, 0.99)
        se1sp85_got = att_pass(0.10, c, 0.7, kappa, 0.0, 0.5, r_F, 1.0, 0.85)
        oracle_got = att_pass(0.10, c, 0.7, kappa, 0.0, 0.5, r_F, 1.0, 1.0)
        prefix = f"kappa={kappa},c={c},r_F={r_F}"
        report(prefix + " none", none_got, none_want, 5e-4)
        report(prefix + " degraded", degraded_got, degraded_want, 5e-4)
        report(prefix + " calibrated", calibrated_got, calibrated_want, 5e-4)
        report(prefix + " se=1,sp=.85", se1sp85_got, se1sp85_want, 5e-4)
        report(prefix + " oracle", oracle_got, oracle_want, 1e-9)

    return ok


if __name__ == "__main__":
    if "--check" in sys.argv:
        ok = _check()
        print()
        print("ALL CHECKS PASSED" if ok else "SOME CHECKS FAILED")
        sys.exit(0 if ok else 1)
    else:
        print(__doc__)
        print("Pass --check to run the unit checks.")
