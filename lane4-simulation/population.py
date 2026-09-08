"""Population (n = infinity) closed forms from derivations/lane1-zero-coupling.md.

Every function here is a pure function of plain floats (or numpy arrays of floats,
which broadcast through the same arithmetic) matching lane 1's standardized
parameters pi, c, rel_H, kappa, delta, rho_T, rho_v, d_theta, r_F, se, sp. This
module exists so verification pass 2 (SPEC section 7) can compare Layer A's
Monte Carlo output against these closed forms mechanically. See CONVENTIONS.md
for the scale normalization and the Cell dataclass these wrap.

Docstrings quote the equation number verbatim from lane1-zero-coupling.md.
"""

from __future__ import annotations

from typing import NamedTuple

import numpy as np
from scipy.stats import norm


class SelectionStats(NamedTuple):
    """Section 6.3 intermediates for the Gaussian threshold detector."""

    tau: float
    lam: float
    psi: float
    q: float


def N(pi: float, c: float, rel_H: float, kappa: float) -> float:
    """(E0a) Covariance multiplier N(pi, c) := (1 - pi) + pi * g, g = c sqrt(kappa/rel_H)."""
    g = c * np.sqrt(kappa / rel_H)
    return (1.0 - pi) + pi * g


def Den(pi: float, kappa: float, delta: float) -> float:
    """(E0b) Variance multiplier Den(pi) := (1-pi) + pi*kappa + pi*(1-pi)*delta^2."""
    return (1.0 - pi) + pi * kappa + pi * (1.0 - pi) * delta**2


def att(pi: float, c: float, rel_H: float, kappa: float, delta: float) -> float:
    """(E7) Att(pi, c) = N(pi, c) / sqrt(Den(pi)), the general-c attenuation factor."""
    return N(pi, c, rel_H, kappa) / np.sqrt(Den(pi, kappa, delta))


def rho_obs(pi: float, c: float, rel_H: float, kappa: float, delta: float, rho_T: float) -> float:
    """(E5) rho_obs := Cor(x, w) = rho_H * Att(pi, c), rho_H = sqrt(rel_H) * rho_T."""
    rho_H = np.sqrt(rel_H) * rho_T
    return rho_H * att(pi, c, rel_H, kappa, delta)


def bias_rho_obs(pi: float, c: float, rel_H: float, kappa: float, delta: float, rho_T: float) -> float:
    """(E6) bias(rho_obs) := rho_obs - rho_H = rho_H * [Att(pi, c) - 1]."""
    rho_H = np.sqrt(rel_H) * rho_T
    return rho_H * (att(pi, c, rel_H, kappa, delta) - 1.0)


def att_0(pi: float, kappa: float, delta: float) -> float:
    """(E8) Att_0(pi) := Att(pi, 0) = (1-pi) / sqrt[(1-pi) + pi*kappa + pi*(1-pi)*delta^2]."""
    return (1.0 - pi) / np.sqrt(Den(pi, kappa, delta))


def c1(kappa: float, rel_H: float) -> float:
    """(E16) c_1 := 2 sqrt(kappa * rel_H) / (1 + kappa), the lower slope threshold."""
    return 2.0 * np.sqrt(kappa * rel_H) / (1.0 + kappa)


def c2(kappa: float, rel_H: float) -> float:
    """(E16) c_2 := (1 + kappa) sqrt(rel_H) / (2 sqrt(kappa)), the upper slope threshold."""
    return (1.0 + kappa) * np.sqrt(rel_H) / (2.0 * np.sqrt(kappa))


def c_star(pi: float, rel_H: float, kappa: float, delta: float) -> float:
    """(E17) Inflation boundary c*(pi) = sqrt(rel_H/kappa) * [sqrt(Den(pi)) - (1-pi)] / pi.

    At pi = 0 uses the limit from E17's proof: sqrt(rel_H/kappa) * (1 + kappa + delta^2) / 2.
    """
    pi_arr = np.asarray(pi, dtype=float)
    safe_pi = np.where(pi_arr == 0.0, 1.0, pi_arr)
    generic = np.sqrt(rel_H / kappa) * (np.sqrt(Den(pi_arr, kappa, delta)) - (1.0 - pi_arr)) / safe_pi
    limit0 = np.sqrt(rel_H / kappa) * (1.0 + kappa + delta**2) / 2.0
    result = np.where(pi_arr == 0.0, limit0, generic)
    return result if result.ndim > 0 else float(result)


def c_flip(pi: float, rel_H: float, kappa: float) -> float:
    """(E18) c_flip(pi) := -(1-pi)/pi * sqrt(rel_H/kappa), the A1 sign-flip threshold.

    At pi = 0 there is no contamination to flip the sign against; the limit is -inf.
    """
    pi_arr = np.asarray(pi, dtype=float)
    safe_pi = np.where(pi_arr == 0.0, 1.0, pi_arr)
    generic = -(1.0 - pi_arr) / safe_pi * np.sqrt(rel_H / kappa)
    result = np.where(pi_arr == 0.0, -np.inf, generic)
    return result if result.ndim > 0 else float(result)


def att_nonignorable(
    pi: float, c: float, rel_H: float, kappa: float, delta: float, d_theta: float, rho_T: float
) -> float:
    """(E21) Att'(pi, c) under A1' (non-ignorable authorship, section 4b).

    Att'(pi, c) = [N(pi, c) - pi(1-pi) delta d_theta / sqrt(rel_H)]
                  / sqrt[Den(pi) (1 + pi(1-pi) rho_T^2 d_theta^2)]
    """
    numerator = N(pi, c, rel_H, kappa) - pi * (1.0 - pi) * delta * d_theta / np.sqrt(rel_H)
    denominator = np.sqrt(Den(pi, kappa, delta) * (1.0 + pi * (1.0 - pi) * rho_T**2 * d_theta**2))
    return numerator / denominator


def c_flip_prime(pi: float, rel_H: float, kappa: float, delta: float, d_theta: float) -> float:
    """(E23) c_flip'(pi) = (1-pi) sqrt(rel_H/kappa) [delta d_theta / sqrt(rel_H) - 1/pi].

    At pi = 0 the bracket's -1/pi term dominates and drives the limit to -inf.
    """
    pi_arr = np.asarray(pi, dtype=float)
    safe_pi = np.where(pi_arr == 0.0, 1.0, pi_arr)
    generic = (1.0 - pi_arr) * np.sqrt(rel_H / kappa) * (delta * d_theta / np.sqrt(rel_H) - 1.0 / safe_pi)
    result = np.where(pi_arr == 0.0, -np.inf, generic)
    return result if result.ndim > 0 else float(result)


def r_M(c: float, rho_v: float) -> float:
    """(E24) r_M := Cor(x_j, x_l | M) = c^2 + rho_v (1 - c^2), within-machine between-item corr."""
    return c**2 + rho_v * (1.0 - c**2)


def r_obs(pi: float, c: float, rel_H: float, kappa: float, delta: float, rho_v: float) -> float:
    """(E26) r_obs := Cor(x_j, x_l), the pooled between-item correlation.

    r_obs = [(1-pi) rel_H + pi kappa r_M + pi(1-pi) delta^2] / Den(pi)
    """
    numerator = (1.0 - pi) * rel_H + pi * kappa * r_M(c, rho_v) + pi * (1.0 - pi) * delta**2
    return numerator / Den(pi, kappa, delta)


def pi_prime(pi: float, se: float, sp: float) -> float:
    """(E30) pi' := P(M | pass) = (1-se) pi / [(1-se) pi + sp (1-pi)]."""
    pi_arr = np.asarray(pi, dtype=float)
    numerator = (1.0 - se) * pi_arr
    denominator = numerator + sp * (1.0 - pi_arr)
    safe_denom = np.where(denominator == 0.0, 1.0, denominator)
    result = np.where(denominator == 0.0, np.nan, numerator / safe_denom)
    return result if result.ndim > 0 else float(result)


def selection_stats(r_F: float, sp_bar: float) -> SelectionStats:
    """(E33) Section 6.3 intermediates: tau, lam, psi, q for the Gaussian threshold detector.

    tau = Phi^-1(1 - sp_bar), lam = phi(tau)/sp_bar, psi = lam(lam - tau), q = 1 - r_F^2 psi.
    Guards sp_bar = 1 (tau = -inf): lam = 0, psi = 0, q = 1.
    """
    sp_arr = np.asarray(sp_bar, dtype=float)
    is_full = sp_arr >= 1.0
    safe_sp = np.where(is_full, 0.5, sp_arr)
    tau_generic = norm.ppf(1.0 - safe_sp)
    tau = np.where(is_full, -np.inf, tau_generic)
    lam_generic = norm.pdf(tau_generic) / safe_sp
    lam = np.where(is_full, 0.0, lam_generic)
    psi_generic = lam_generic * (lam_generic - tau_generic)
    psi = np.where(is_full, 0.0, psi_generic)
    q = 1.0 - r_F**2 * psi
    if tau.ndim == 0:
        return SelectionStats(tau=float(tau), lam=float(lam), psi=float(psi), q=float(q))
    return SelectionStats(tau=tau, lam=lam, psi=psi, q=q)


def q_selection(r_F: float, sp_bar: float) -> float:
    """(E33) q := 1 - r_F^2 psi, the residual human trait-variance fraction after selection."""
    return selection_stats(r_F, sp_bar).q


def rho_H_pass(rel_H: float, rho_T: float, r_F: float, sp_bar: float) -> float:
    """(E34) rho_H,pass := Cor(x, w | H, pass), deletion-selection bias at pi' = 0.

    rho_H,pass = rho_H * q / sqrt[(1 - rel_H(1-q))(1 - rho_T^2(1-q))]
    When sp_bar = 1 (q = 1), rho_H,pass = rho_H exactly.
    """
    rho_H = np.sqrt(rel_H) * rho_T
    q = q_selection(r_F, sp_bar)
    denominator = np.sqrt((1.0 - rel_H * (1.0 - q)) * (1.0 - rho_T**2 * (1.0 - q)))
    return rho_H * q / denominator


def population_moments(cell) -> dict:
    """Cell convenience wrapper: population moments Layer A checks its Monte Carlo output against.

    Keys: rho_H, rho_T, att, rho_obs, r_obs, pi_prime, rho_H_pass, q, tau, lam, psi.
    Uses att_nonignorable (E21) instead of att (E7) when cell.d_theta != 0, since that is
    the process dgp.py actually simulates (CONVENTIONS.md A1' block). rho_H_pass uses the
    cell's detector operating point sp; at sp = 1 it equals rho_H.
    """
    rho_H = cell.rho_H
    rho_T = cell.rho_T
    if cell.d_theta == 0.0:
        att_val = att(cell.pi, cell.c, cell.rel_H, cell.kappa, cell.delta)
    else:
        att_val = att_nonignorable(
            cell.pi, cell.c, cell.rel_H, cell.kappa, cell.delta, cell.d_theta, cell.rho_T
        )
    rho_obs_val = rho_H * att_val
    r_obs_val = r_obs(cell.pi, cell.c, cell.rel_H, cell.kappa, cell.delta, cell.rho_v)
    se, sp = cell.se_sp
    pi_prime_val = pi_prime(cell.pi, se, sp)
    stats = selection_stats(cell.r_F, sp)
    rho_H_pass_val = rho_H_pass(cell.rel_H, cell.rho_T, cell.r_F, sp)
    return dict(
        rho_H=rho_H,
        rho_T=rho_T,
        att=att_val,
        rho_obs=rho_obs_val,
        r_obs=r_obs_val,
        pi_prime=pi_prime_val,
        rho_H_pass=rho_H_pass_val,
        q=stats.q,
        tau=stats.tau,
        lam=stats.lam,
        psi=stats.psi,
    )
