"""Lane 4 correction estimators (SPEC section 3), scored against dgp.py's Sample.

Five estimators, each `fit_<name>(sample: Sample, **opts) -> Fit`:
  fit_naive      - Pearson Cor(x_1, w) on the full contaminated sample.
  fit_delete     - same, on detector survivors (detect-and-delete).
  fit_simex      - MC-SIMEX (Kuechenhoff, Mun & Carroll 2006) on known misclassification.
  fit_labelfree  - SPEC 3.2 label-free prevalence + errors-in-variables (inverts E2/E3/E26).
  fit_em         - SPEC 3.3 two-component full-covariance Gaussian mixture (EM, multi-start).

All formulas trace to derivations/lane1-zero-coupling.md (E2-E9, E24-E30, E34); see
CONVENTIONS.md for the Fit contract and scale normalization these estimators invert.
No estimator raises: every failure is caught and returned as NaNs with converged=False.
"""

from __future__ import annotations

import time
import warnings
from dataclasses import dataclass

import numpy as np
from sklearn.mixture import GaussianMixture

from dgp import Sample
from population import r_M as _r_M_formula

# --------------------------------------------------------------------------------------
# Contract (CONVENTIONS.md "Estimator return contract")
# --------------------------------------------------------------------------------------


@dataclass
class Fit:
    name: str
    rho_H_hat: float
    rho_T_hat: float
    pi_hat: float | None
    rel_hat: float | None
    ci_H: tuple[float, float] | None
    ci_T: tuple[float, float] | None
    loading_hat: float | None
    seconds: float
    converged: bool = True
    note: str = ""
    # Share of `seconds` spent in resampling (bootstrap/SIMEX Monte Carlo) rather than the
    # point estimate. None where the estimator does no resampling. Reported separately
    # because it is the part the grid can cut by lowering B/B_boot.
    seconds_resample: float | None = None


def _nan_fit(name: str, seconds: float, note: str) -> Fit:
    return Fit(
        name=name,
        rho_H_hat=float("nan"),
        rho_T_hat=float("nan"),
        pi_hat=None,
        rel_hat=float("nan"),
        ci_H=None,
        ci_T=None,
        loading_hat=float("nan"),
        seconds=seconds,
        converged=False,
        note=note,
    )


# --------------------------------------------------------------------------------------
# Shared helpers
# --------------------------------------------------------------------------------------


def _pearson(x: np.ndarray, y: np.ndarray) -> float:
    if x.size < 3 or np.std(x) == 0 or np.std(y) == 0:
        return float("nan")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        r = np.corrcoef(x, y)[0, 1]
    return float(r)


def _between_item_corr(X: np.ndarray) -> float:
    """Mean pairwise correlation among the k columns of X (parallel-item reliability)."""
    k = X.shape[1]
    if k < 2 or X.shape[0] < 3:
        return float("nan")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        C = np.corrcoef(X, rowvar=False)
    iu = np.triu_indices(k, k=1)
    vals = C[iu]
    vals = vals[np.isfinite(vals)]
    if vals.size == 0:
        return float("nan")
    return float(np.mean(vals))


def _fisher_ci(r: float, n: int) -> tuple[float, float] | None:
    if not np.isfinite(r) or n < 4 or abs(r) >= 1.0:
        return None
    z = np.arctanh(np.clip(r, -0.999999, 0.999999))
    se = 1.0 / np.sqrt(n - 3)
    lo, hi = z - 1.96 * se, z + 1.96 * se
    return float(np.tanh(lo)), float(np.tanh(hi))


def _rho_T_from_H(rho_H_hat: float, rel_hat: float) -> float:
    if not np.isfinite(rho_H_hat) or not np.isfinite(rel_hat) or rel_hat <= 0:
        return float("nan")
    return float(rho_H_hat / np.sqrt(rel_hat))


def _ci_T_from_H(ci_H: tuple[float, float] | None, rel_hat: float) -> tuple[float, float] | None:
    if ci_H is None or not np.isfinite(rel_hat) or rel_hat <= 0:
        return None
    factor = 1.0 / np.sqrt(rel_hat)
    return float(ci_H[0] * factor), float(ci_H[1] * factor)


def _naive_style_fit(name: str, x: np.ndarray, w: np.ndarray, X: np.ndarray, note: str) -> Fit:
    t0 = time.perf_counter()
    try:
        n = x.size
        rho_H_hat = _pearson(x, w)
        rel_hat = _between_item_corr(X)
        loading_hat = float(np.sqrt(max(rel_hat, 0.0))) if np.isfinite(rel_hat) else float("nan")
        rho_T_hat = _rho_T_from_H(rho_H_hat, rel_hat)
        ci_H = _fisher_ci(rho_H_hat, n)
        ci_T = _ci_T_from_H(ci_H, rel_hat)
        converged = bool(np.isfinite(rho_H_hat) and np.isfinite(rel_hat))
        return Fit(
            name=name,
            rho_H_hat=rho_H_hat,
            rho_T_hat=rho_T_hat,
            pi_hat=None,
            rel_hat=rel_hat,
            ci_H=ci_H,
            ci_T=ci_T,
            loading_hat=loading_hat,
            seconds=time.perf_counter() - t0,
            converged=converged,
            note=note if converged else (note + " | non-finite result (degenerate input)").strip(" |"),
        )
    except Exception as e:  # never raise
        return _nan_fit(name, time.perf_counter() - t0, f"{name} failed: {e!r}")


# --------------------------------------------------------------------------------------
# 1. Naive
# --------------------------------------------------------------------------------------


def fit_naive(sample: Sample, **opts) -> Fit:
    return _naive_style_fit("naive", sample.x, sample.w, sample.X, note="")


# --------------------------------------------------------------------------------------
# 2. Detect-and-delete
# --------------------------------------------------------------------------------------


def fit_delete(sample: Sample, **opts) -> Fit:
    passed = sample.passed
    n_eff = int(passed.sum())
    note = f"n_eff={n_eff} (detector={sample.cell.detector})"
    return _naive_style_fit("delete", sample.x[passed], sample.w[passed], sample.X[passed], note=note)


# --------------------------------------------------------------------------------------
# 3. MC-SIMEX
# --------------------------------------------------------------------------------------


def _matrix_power_2x2(M: np.ndarray, p: float) -> tuple[np.ndarray, bool]:
    """M^p via eigendecomposition. Returns (power, ok). ok=False on complex/near-singular."""
    try:
        vals, vecs = np.linalg.eig(M)
        if np.any(np.abs(vals.imag) > 1e-8):
            return M, False
        vals = vals.real
        vecs_r = vecs.real
        if abs(np.linalg.det(vecs_r)) < 1e-10:
            return M, False
        Mp = vecs_r @ np.diag(vals**p) @ np.linalg.inv(vecs_r)
        if not np.all(np.isfinite(Mp)):
            return M, False
        return Mp.real, True
    except Exception:
        return M, False


def _extrapolate(lam_vals: np.ndarray, y_vals: np.ndarray) -> tuple[float, str]:
    """Fit quadratic in lam, extrapolate to lam=-1; fall back to linear if ill-posed."""
    used = "quadratic"
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            coeffs = np.polyfit(lam_vals, y_vals, 2)
        val = np.polyval(coeffs, -1.0)
        if not np.isfinite(val) or not (-1.0 <= val <= 1.0):
            raise ValueError("quadratic extrapolant out of [-1, 1]")
    except Exception:
        used = "linear"
        coeffs = np.polyfit(lam_vals, y_vals, 1)
        val = np.polyval(coeffs, -1.0)
        val = float(np.clip(val, -1.0, 1.0)) if np.isfinite(val) else float("nan")
    return float(val), used


def fit_simex(
    sample: Sample,
    se: float,
    sp: float,
    lambdas: tuple[float, ...] = (0.0, 0.5, 1.0, 1.5, 2.0),
    B: int = 20,
    rng: np.random.Generator | None = None,
    B_boot: int = 0,
    **opts,
) -> Fit:
    t0 = time.perf_counter()
    try:
        if rng is None:
            rng = np.random.default_rng()

        def _simex_point(x: np.ndarray, w: np.ndarray, X: np.ndarray, flag: np.ndarray,
                          se_: float, sp_: float, rng_: np.random.Generator) -> tuple[float, float, str, str]:
            Pi = np.array([[sp_, 1.0 - se_], [1.0 - sp_, se_]])  # rows: obs(pass,flag), cols: true(H,M)
            o = flag.astype(int)  # 0 = pass, 1 = flag
            rho_pts = np.empty(len(lambdas))
            rel_pts = np.empty(len(lambdas))
            note_bits = []
            for li, lam in enumerate(lambdas):
                if lam == 0.0:
                    T = np.eye(2)
                    ok = True
                else:
                    T, ok = _matrix_power_2x2(Pi, lam)
                if not ok:
                    note_bits.append(f"lam={lam}:matrix-power-fallback")
                rho_draws = np.empty(B)
                rel_draws = np.empty(B)
                for b in range(B):
                    u = rng_.random(o.size)
                    p_new0 = T[0, o]  # P(new label = pass | current label = o)
                    new_label = (u >= p_new0).astype(int)  # 0 = pass, 1 = flag
                    keep = new_label == 0
                    if keep.sum() < 3:
                        rho_draws[b] = np.nan
                        rel_draws[b] = np.nan
                        continue
                    rho_draws[b] = _pearson(x[keep], w[keep])
                    rel_draws[b] = _between_item_corr(X[keep])
                rho_pts[li] = np.nanmean(rho_draws)
                rel_pts[li] = np.nanmean(rel_draws)
            lam_arr = np.asarray(lambdas, dtype=float)
            good_rho = np.isfinite(rho_pts)
            good_rel = np.isfinite(rel_pts)
            if good_rho.sum() < 3 or good_rel.sum() < 3:
                return float("nan"), float("nan"), "insufficient valid lambda points", ""
            rho_ext, used_rho = _extrapolate(lam_arr[good_rho], rho_pts[good_rho])
            rel_ext, used_rel = _extrapolate(lam_arr[good_rel], rel_pts[good_rel])
            note = f"extrap(rho)={used_rho}, extrap(rel)={used_rel}"
            if note_bits:
                note += " | " + "; ".join(note_bits)
            return rho_ext, rel_ext, note, ""

        # The whole SIMEX point estimate IS resampling (B remeasurement draws per lambda),
        # so unlike fit_em there is no cheap point estimate to separate out; the resample
        # share below therefore covers the point estimate's own Monte Carlo plus any
        # outer bootstrap.
        t_res = time.perf_counter()
        rho_H_hat, rel_hat, extra_note, _ = _simex_point(
            sample.x, sample.w, sample.X, sample.flag, se, sp, rng
        )
        seconds_resample = time.perf_counter() - t_res
        rho_T_hat = _rho_T_from_H(rho_H_hat, rel_hat)
        loading_hat = float(np.sqrt(max(rel_hat, 0.0))) if np.isfinite(rel_hat) else float("nan")

        ci_H = ci_T = None
        boot_note = ""
        if B_boot and B_boot > 0:
            t_boot = time.perf_counter()
            n = sample.x.size
            boots_H = np.empty(B_boot)
            boots_T = np.empty(B_boot)
            for bi in range(B_boot):
                idx = rng.integers(0, n, size=n)
                rho_b, rel_b, _, _ = _simex_point(
                    sample.x[idx], sample.w[idx], sample.X[idx], sample.flag[idx], se, sp, rng
                )
                boots_H[bi] = rho_b
                boots_T[bi] = _rho_T_from_H(rho_b, rel_b)
            boots_H = boots_H[np.isfinite(boots_H)]
            boots_T = boots_T[np.isfinite(boots_T)]
            if boots_H.size > 10:
                ci_H = (float(np.percentile(boots_H, 2.5)), float(np.percentile(boots_H, 97.5)))
            if boots_T.size > 10:
                ci_T = (float(np.percentile(boots_T, 2.5)), float(np.percentile(boots_T, 97.5)))
            seconds_resample += time.perf_counter() - t_boot
            boot_note = f" | B_boot={B_boot}"

        converged = bool(np.isfinite(rho_H_hat) and np.isfinite(rel_hat))
        return Fit(
            name="simex",
            rho_H_hat=rho_H_hat,
            rho_T_hat=rho_T_hat,
            pi_hat=None,
            rel_hat=rel_hat,
            ci_H=ci_H,
            ci_T=ci_T,
            loading_hat=loading_hat,
            seconds=time.perf_counter() - t0,
            seconds_resample=seconds_resample,
            converged=converged,
            note=(extra_note + boot_note).strip(" |"),
        )
    except Exception as e:
        return _nan_fit("simex", time.perf_counter() - t0, f"simex failed: {e!r}")


# --------------------------------------------------------------------------------------
# 4. Label-free prevalence + errors-in-variables
# --------------------------------------------------------------------------------------


def _hellinger(p: np.ndarray, q: np.ndarray) -> float:
    return float(np.sqrt(np.sum((np.sqrt(p) - np.sqrt(q)) ** 2)) / np.sqrt(2.0))


def _distribution_match_pi(obs: np.ndarray, machine_ref: np.ndarray, human_ref: np.ndarray,
                            n_bins: int = 60, n_grid: int = 501) -> float:
    lo = min(obs.min(), machine_ref.min(), human_ref.min())
    hi = max(obs.max(), machine_ref.max(), human_ref.max())
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        return float("nan")
    edges = np.linspace(lo, hi, n_bins + 1)
    h_obs, _ = np.histogram(obs, bins=edges, density=False)
    h_m, _ = np.histogram(machine_ref, bins=edges, density=False)
    h_h, _ = np.histogram(human_ref, bins=edges, density=False)
    p_obs = h_obs / max(h_obs.sum(), 1)
    p_m = h_m / max(h_m.sum(), 1)
    p_h = h_h / max(h_h.sum(), 1)
    grid = np.linspace(0.0, 1.0, n_grid)
    dists = np.array([_hellinger(p_obs, pi_ * p_m + (1.0 - pi_) * p_h) for pi_ in grid])
    return float(grid[np.argmin(dists)])


def _adjusted_count_pi(flag_rate: float, se: float, sp: float) -> tuple[float, bool]:
    denom = se - (1.0 - sp)
    # <= not abs(): a detector at or below chance gives denom <= 0, and dividing through it
    # returns a finite, clipped, monotonically-WRONG pi. Refuse instead (lane 4 sweep s5).
    if denom <= 1e-8:
        return float("nan"), False
    pi_hat = (flag_rate - (1.0 - sp)) / denom
    return float(np.clip(pi_hat, 0.0, 1.0)), True


def fit_labelfree(
    sample: Sample,
    machine_ref: np.ndarray,
    human_ref: np.ndarray | None = None,
    c_known: float = 0.0,
    method: str = "distribution_match",
    se: float | None = None,
    sp: float | None = None,
    rho_v: float = 0.0,
    B: int = 200,
    rng: np.random.Generator | None = None,
    **opts,
) -> Fit:
    t0 = time.perf_counter()
    try:
        if rng is None:
            rng = np.random.default_rng()
        machine_ref = np.asarray(machine_ref, dtype=float)

        def _run(x, w, X, flag):
            mu_M_hat = float(np.mean(machine_ref))
            s2_M_hat = float(np.var(machine_ref, ddof=1))
            notes = []
            if method == "adjusted_count":
                if se is None or sp is None:
                    raise ValueError("adjusted_count requires se and sp")
                flag_rate = float(np.mean(flag))
                pi_hat, ok = _adjusted_count_pi(flag_rate, se, sp)
                if not ok:
                    raise ValueError("adjusted_count undefined: se + sp = 1")
            elif method == "distribution_match":
                if human_ref is None:
                    notes.append("human_ref=None: used GMM surrogate for human_ref (assumption)")
                    gm = GaussianMixture(n_components=2, n_init=5, random_state=0,
                                         max_iter=500, tol=1e-6).fit(x.reshape(-1, 1))
                    means = gm.means_.ravel()
                    m_idx = int(np.argmin(np.abs(means - mu_M_hat)))
                    h_idx = 1 - m_idx
                    mu_h_s = float(means[h_idx])
                    var_h_s = float(gm.covariances_.ravel()[h_idx])
                    human_ref_eff = mu_h_s + np.sqrt(max(var_h_s, 1e-8)) * rng.standard_normal(5000)
                else:
                    human_ref_eff = np.asarray(human_ref, dtype=float)
                pi_hat = _distribution_match_pi(x, machine_ref, human_ref_eff)
            else:
                raise ValueError(f"unknown method {method!r}")

            if not np.isfinite(pi_hat):
                raise ValueError("pi_hat non-finite")
            pi_hat = float(np.clip(pi_hat, 1e-6, 1.0 - 1e-6))

            mean_x = float(np.mean(x))
            var_x = float(np.var(x, ddof=1))
            mu_H_hat = (mean_x - pi_hat * mu_M_hat) / (1.0 - pi_hat)
            Delta_hat = mu_H_hat - mu_M_hat
            V_H_hat = (var_x - pi_hat * s2_M_hat - pi_hat * (1.0 - pi_hat) * Delta_hat**2) / (1.0 - pi_hat)
            if not np.isfinite(V_H_hat) or V_H_hat <= 0:
                raise ValueError("V_H_hat non-positive")
            kappa_hat = s2_M_hat / V_H_hat
            delta_hat = Delta_hat / np.sqrt(V_H_hat)
            Den_hat = var_x / V_H_hat

            r_M_hat = _r_M_formula(c_known, rho_v)
            r_obs_hat = _between_item_corr(X)
            rel_H_hat = (r_obs_hat * Den_hat - pi_hat * kappa_hat * r_M_hat
                         - pi_hat * (1.0 - pi_hat) * delta_hat**2) / (1.0 - pi_hat)
            rel_H_hat = float(np.clip(rel_H_hat, 1e-6, 1.0))

            N_hat = (1.0 - pi_hat) + pi_hat * c_known * np.sqrt(kappa_hat / rel_H_hat)
            Att_hat = N_hat / np.sqrt(Den_hat)
            if not np.isfinite(Att_hat) or Att_hat == 0:
                raise ValueError("Att_hat non-finite/zero")

            rho_obs_hat = _pearson(x, w)
            rho_H_hat = rho_obs_hat / Att_hat
            rho_T_hat = _rho_T_from_H(rho_H_hat, rel_H_hat)

            notes.append(f"c_known={c_known} (assumption, default 0)")
            notes.append(f"rho_v={rho_v} (assumption, default 0)")
            return rho_H_hat, rho_T_hat, pi_hat, rel_H_hat, "; ".join(notes)

        rho_H_hat, rho_T_hat, pi_hat, rel_H_hat, note = _run(sample.x, sample.w, sample.X, sample.flag)
        loading_hat = float(np.sqrt(max(rel_H_hat, 0.0))) if np.isfinite(rel_H_hat) else float("nan")

        ci_H = ci_T = None
        if B and B > 0:
            n = sample.x.size
            boots_H = np.empty(B)
            boots_T = np.empty(B)
            for bi in range(B):
                idx = rng.integers(0, n, size=n)
                try:
                    rh, rt, _, _, _ = _run(sample.x[idx], sample.w[idx], sample.X[idx], sample.flag[idx])
                except Exception:
                    rh, rt = float("nan"), float("nan")
                boots_H[bi] = rh
                boots_T[bi] = rt
            boots_H = boots_H[np.isfinite(boots_H)]
            boots_T = boots_T[np.isfinite(boots_T)]
            if boots_H.size > 10:
                ci_H = (float(np.percentile(boots_H, 2.5)), float(np.percentile(boots_H, 97.5)))
            if boots_T.size > 10:
                ci_T = (float(np.percentile(boots_T, 2.5)), float(np.percentile(boots_T, 97.5)))

        converged = bool(np.isfinite(rho_H_hat) and np.isfinite(rel_H_hat))
        return Fit(
            name="labelfree",
            rho_H_hat=rho_H_hat,
            rho_T_hat=rho_T_hat,
            pi_hat=pi_hat,
            rel_hat=rel_H_hat,
            ci_H=ci_H,
            ci_T=ci_T,
            loading_hat=loading_hat,
            seconds=time.perf_counter() - t0,
            converged=converged,
            note=note,
        )
    except Exception as e:
        return _nan_fit("labelfree", time.perf_counter() - t0, f"labelfree failed: {e!r}")


# --------------------------------------------------------------------------------------
# 5. Full joint mixture (EM)
# --------------------------------------------------------------------------------------


def _fit_gmm2(data: np.ndarray, n_init: int, k: int, random_state) -> GaussianMixture:
    gm = GaussianMixture(
        n_components=2,
        covariance_type="full",
        n_init=n_init,
        init_params="k-means++",
        reg_covar=1e-6,
        random_state=random_state,
        # sklearn's defaults (max_iter=100, tol=1e-3) stop EM after ~8 iterations on the
        # weakly-separated mixtures this grid is full of (delta=0: the components differ
        # only in scale), and sklearn still reports converged_=True because the loose tol
        # criterion is met. Measured at pi=0.30, n=1000: 0.2407 vs truth 0.4183 at the
        # defaults, 0.4377 here. The likelihood surface is flat, not multimodal -- every
        # init strategy agrees once EM is allowed to run.
        max_iter=500,
        tol=1e-6,
    )
    gm.fit(data)
    return gm


def _sample_gmm2(gm: GaussianMixture, n: int, rng: np.random.Generator) -> np.ndarray:
    """Draw n points from the fitted 2-component mixture using OUR rng.

    Not `gm.sample(n)`: sklearn's sample() calls check_random_state(self.random_state)
    on every invocation, so with the integer random_state _fit_gmm2 sets it returns the
    IDENTICAL dataset each call. A parametric bootstrap built on gm.sample() therefore
    resamples nothing -- every replicate sees the same data, and the resulting interval
    measures multi-start optimizer noise rather than sampling variability.
    """
    labels = rng.choice(len(gm.weights_), size=n, p=gm.weights_)
    out = np.empty((n, gm.means_.shape[1]))
    for j in range(len(gm.weights_)):
        m = labels == j
        if m.any():
            out[m] = rng.multivariate_normal(gm.means_[j], gm.covariances_[j], size=int(m.sum()))
    return out


def _refit_gmm2_warm(data: np.ndarray, gm: GaussianMixture) -> GaussianMixture:
    """Refit a 2-component GMM warm-started from `gm`'s own parameters.

    Used only for the parametric bootstrap, where `data` was generated FROM `gm`, so
    `gm`'s parameters are the ideal starting point: a single warm start converges in a
    few iterations where multi-start k-means++ re-searches the whole surface. Measured
    at the pilot cell this cuts fit_em from 16.8s to well under a second with no change
    to the point estimate. It also isolates sampling variability from optimization
    variability, which is what a parametric bootstrap interval is meant to capture.
    """
    gm_b = GaussianMixture(
        n_components=2,
        covariance_type="full",
        n_init=1,
        reg_covar=1e-6,
        max_iter=500,
        tol=1e-6,
        weights_init=gm.weights_,
        means_init=gm.means_,
        precisions_init=np.linalg.inv(gm.covariances_),
    )
    gm_b.fit(data)
    return gm_b


def _em_identify_human(gm: GaussianMixture, k: int) -> tuple[int, str]:
    weights = gm.weights_
    note = ""
    if abs(weights[0] - weights[1]) < 0.02:
        item_var = [np.mean(np.diag(gm.covariances_[j])[:k]) for j in range(2)]
        human_idx = int(np.argmax(item_var))
        note = "weights within 0.02: identified human by larger mean item variance"
    else:
        human_idx = int(np.argmax(weights))
    return human_idx, note


def _em_moments(gm: GaussianMixture, k: int) -> tuple[int, float, float, float, str]:
    human_idx, note = _em_identify_human(gm, k)
    machine_idx = 1 - human_idx
    pi_hat = float(gm.weights_[machine_idx])
    Sigma = gm.covariances_[human_idx]
    rho_H_hat = Sigma[0, k] / np.sqrt(Sigma[0, 0] * Sigma[k, k])
    iu = np.triu_indices(k, k=1)
    item_cov = Sigma[:k, :k]
    diag = np.sqrt(np.diag(item_cov))
    corr = item_cov / np.outer(diag, diag)
    rel_hat = float(np.mean(corr[iu]))
    return human_idx, pi_hat, float(rho_H_hat), rel_hat, note


def fit_em(
    sample: Sample,
    n_init: int = 10,
    B_boot: int = 100,
    rng: np.random.Generator | None = None,
    **opts,
) -> Fit:
    t0 = time.perf_counter()
    try:
        if rng is None:
            rng = np.random.default_rng()
        k = sample.X.shape[1]
        data = np.column_stack([sample.X, sample.w])
        seed0 = int(rng.integers(0, 2**31 - 1))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            gm = _fit_gmm2(data, n_init, k, seed0)
        human_idx, pi_hat, rho_H_hat, rel_hat, id_note = _em_moments(gm, k)
        loading_hat = float(np.sqrt(max(rel_hat, 0.0))) if np.isfinite(rel_hat) else float("nan")
        rho_T_hat = _rho_T_from_H(rho_H_hat, rel_hat)

        ci_H = ci_T = None
        boot_note = ""
        seconds_resample = 0.0
        if B_boot and B_boot > 0:
            t_boot = time.perf_counter()
            n = data.shape[0]
            boots_H = np.empty(B_boot)
            boots_T = np.empty(B_boot)
            n_failed = 0
            for bi in range(B_boot):
                sim_data = _sample_gmm2(gm, n, rng)
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        gm_b = _refit_gmm2_warm(sim_data, gm)
                    if not gm_b.converged_:
                        n_failed += 1
                    _, _, rh, rl, _ = _em_moments(gm_b, k)
                    boots_H[bi] = rh
                    boots_T[bi] = _rho_T_from_H(rh, rl)
                except Exception:
                    n_failed += 1
                    boots_H[bi] = np.nan
                    boots_T[bi] = np.nan
            boots_H_f = boots_H[np.isfinite(boots_H)]
            boots_T_f = boots_T[np.isfinite(boots_T)]
            if boots_H_f.size > 10:
                ci_H = (float(np.percentile(boots_H_f, 2.5)), float(np.percentile(boots_H_f, 97.5)))
            if boots_T_f.size > 10:
                ci_T = (float(np.percentile(boots_T_f, 2.5)), float(np.percentile(boots_T_f, 97.5)))
            seconds_resample = time.perf_counter() - t_boot
            boot_note = (
                f" | parametric bootstrap B={B_boot}, non-convergence fraction="
                f"{n_failed / B_boot:.2f}, warm-started from the fitted model"
                " (single start; isolates sampling variability from multi-start"
                " optimization variability, so the interval does not reflect"
                " variability contributed by multi-start failure in real fits)"
            )

        converged = bool(gm.converged_ and np.isfinite(rho_H_hat) and np.isfinite(rel_hat))
        note = f"human=larger-weight-component; {id_note}".strip("; ") + boot_note
        return Fit(
            name="em",
            rho_H_hat=rho_H_hat,
            rho_T_hat=rho_T_hat,
            pi_hat=pi_hat,
            rel_hat=rel_hat,
            ci_H=ci_H,
            ci_T=ci_T,
            loading_hat=loading_hat,
            seconds=time.perf_counter() - t0,
            seconds_resample=seconds_resample,
            converged=converged,
            note=note,
        )
    except Exception as e:
        return _nan_fit("em", time.perf_counter() - t0, f"em failed: {e!r}")


# --------------------------------------------------------------------------------------

ESTIMATORS = {
    "naive": fit_naive,
    "delete": fit_delete,
    "simex": fit_simex,
    "labelfree": fit_labelfree,
    "em": fit_em,
}
