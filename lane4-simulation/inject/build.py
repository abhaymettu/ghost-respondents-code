"""Build a Layer B sample: bootstrap the human base, inject the assigned machine texts.

The product is a `dgp.Sample` obeying lane4-simulation/CONVENTIONS.md, so every estimator
in estimators.py consumes a Layer B sample unchanged.

Two normalization facts that differ from Layer A and are stated once here (INJECT.md
repeats them):

  * Layer B defines theta := L, the binary persona label, standardized to mean 0 variance 1.
    The human loading on theta is NOT 1; it is r_H = Cor(x_H, theta), which plays the role
    Layer A's sqrt(rel_H) plays. Nothing assumes a loading of 1.
  * Scores are standardized by the HUMAN BASE's mean and sd, so mu_H = 0 and V_H = 1. Layer
    A instead fixes Var(theta) = 1 and derives V_H = 1 / rel_H. The two normalizations agree
    on every unit-free quantity (c, g, kappa, delta, Att, rho_H) and differ only in the
    units of the score itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from dgp import Cell, Sample

from .assign import (
    PoolCapacityError,
    RandomMode,
    assign_indices,
    assignment_moments,
    random_branch_weights,
)
from .pools import Pool


@dataclass
class InjectedSample:
    """A Layer B sample plus the provenance Layer A samples do not need."""

    sample: Sample
    x_full: np.ndarray  # (n,) whole-text trait score; the single indicator of every closed form
    text_ids: np.ndarray  # (n,) which text each respondent's score came from
    from_pool: np.ndarray  # (n,) pool index for machine respondents, -1 for humans
    provenance: dict[str, Any] = field(default_factory=dict)

    @property
    def n(self) -> int:
        return int(self.x_full.size)


def _standardizer(human_pool: Pool) -> tuple[float, float]:
    x = human_pool.scores
    sd = float(x.std(ddof=0))
    if sd <= 0:
        raise ValueError(f"human pool {human_pool.name!r} has zero score variance")
    return float(x.mean()), sd


def detector_flags(
    human_scores: np.ndarray, machine_scores: np.ndarray, sp: float
) -> tuple[float, float, float]:
    """Threshold the detector at the human specificity `sp`. Returns (threshold, sp, se).

    sp is SET by the threshold (it is a quantile of the human scores); se is MEASURED, not
    set -- on a same-genre pool it will be near the false-positive rate, which is the
    boundary result memo 2.3 predicts and Layer B is meant to produce.
    """
    if not 0.0 < sp <= 1.0:
        raise ValueError("sp must be in (0, 1]")
    h = np.asarray(human_scores, dtype=float)
    h = h[np.isfinite(h)]
    if h.size == 0:
        raise ValueError("no finite human detector scores")
    thr = float(np.quantile(h, sp)) if sp < 1.0 else float(np.max(h)) + np.finfo(float).eps
    m = np.asarray(machine_scores, dtype=float)
    m = m[np.isfinite(m)]
    se = float(np.mean(m > thr)) if m.size else float("nan")
    return thr, float(np.mean(h <= thr)), se


def bootstrap_base(human_pool: Pool, n: int, rng: np.random.Generator) -> np.ndarray:
    """Draw n respondents with replacement from the human base (the PK essays)."""
    if n < 2:
        raise ValueError("n must be >= 2")
    return rng.integers(0, len(human_pool), size=n)


def build_injected_sample(
    human_pool: Pool,
    machine_pool: Pool,
    n: int,
    pi: float,
    p: float,
    rng: np.random.Generator,
    rho_T: float = 0.5,
    k_chunks: int = 1,
    sp: float = 0.99,
    mode: RandomMode = "respondent_marginal",
    replace: bool = False,
) -> InjectedSample:
    """One Layer B replicate at a SPEC (n, pi) cell and coupling level p.

    The outcome w is CONSTRUCTED (w = rho_T * theta + u, Var(w) = 1): the texts and the
    trait scores are real, the outcome is not. Nothing in the corpora carries an outcome
    variable, and the memo's design says so (section 3.2, "w = b L_i + u_i").
    """
    if not 0.0 <= pi <= 1.0:
        raise ValueError("pi must be in [0, 1]")
    if human_pool.kind != "human":
        raise ValueError(f"human_pool {human_pool.name!r} has kind={human_pool.kind!r}")
    if human_pool.trait != machine_pool.trait:
        raise ValueError(
            f"trait mismatch: human {human_pool.trait!r} vs machine {machine_pool.trait!r}"
        )

    mu_h, sd_h = _standardizer(human_pool)
    hp = human_pool.standardized(mu_h, sd_h)
    mp = machine_pool.standardized(mu_h, sd_h)

    idx_h = bootstrap_base(hp, n, rng)
    labels = hp.labels[idx_h]
    q1 = float(np.mean(labels))
    if q1 in (0.0, 1.0):
        raise ValueError("bootstrap drew a single label; theta would be degenerate")
    theta = (labels - q1) / np.sqrt(q1 * (1 - q1))

    u = rng.normal(0.0, np.sqrt(max(1.0 - rho_T**2, 0.0)), size=n)
    w = rho_T * theta + u

    n_m = int(round(n * pi))
    A = np.zeros(n, dtype=np.uint8)
    # machine status independent of theta: A1 (ignorable). d_theta != 0 would break this
    # deliberately and is a Layer A arm, not a Layer B one.
    A[rng.permutation(n)[:n_m]] = 1
    m_pos = np.flatnonzero(A == 1)

    x_full = hp.scores[idx_h].astype(float)
    text_ids = np.array([hp.texts[i].text_id for i in idx_h], dtype=object)
    from_pool = np.full(n, -1, dtype=int)
    chunk_h = _chunks_or_none(hp, idx_h, k_chunks)
    chunk_m = None

    if m_pos.size:
        # q1 is the FULL sample's label marginal, the same one theta is standardized by, not
        # the machine subsample's own. Otherwise the assignment law and layer_b_moments refer
        # to two different q1 that agree only asymptotically.
        pool_idx = assign_indices(rng, labels[m_pos], mp, p, replace=replace, mode=mode, q1=q1)
        x_full[m_pos] = mp.scores[pool_idx]
        text_ids[m_pos] = [mp.texts[i].text_id for i in pool_idx]
        from_pool[m_pos] = pool_idx
        chunk_m = _chunks_or_none(mp, pool_idx, k_chunks)

    if k_chunks == 1:
        X = x_full[:, None]
    else:
        if chunk_h is None or (m_pos.size and chunk_m is None):
            raise ValueError(
                f"k_chunks={k_chunks} needs per-chunk scores on every text. Lane 3's step-1 "
                "brief does not include chunk-level scoring -- see INJECT.md 'Open dependency'."
            )
        X = np.empty((n, k_chunks), dtype=float)
        X[:] = chunk_h
        if m_pos.size:
            X[m_pos] = chunk_m

    det_h_all = hp.detector
    det_m_all = mp.detector
    F = np.full(n, np.nan, dtype=float)
    flag = np.zeros(n, dtype=bool)
    det_note = "no detector scores on the pools (lane 3 not landed); flag is all False"
    realized_sp = realized_se = float("nan")
    if np.isfinite(det_h_all).any() and (not m_pos.size or np.isfinite(det_m_all).any()):
        F = det_h_all[idx_h].astype(float)
        if m_pos.size:
            F[m_pos] = det_m_all[from_pool[m_pos]]
        thr, realized_sp, realized_se = detector_flags(
            det_h_all, det_m_all if m_pos.size else np.array([np.nan]), sp
        )
        flag = np.asarray(F > thr)
        det_note = f"threshold {thr:.4f} at target sp={sp}; realized sp={realized_sp:.4f}, se={realized_se:.4f}"

    nan = float("nan")
    # Every field that is a SET knob in Layer A but a MEASURED outcome in Layer B is NaN, so
    # nothing downstream can read a Layer A default off a Layer B cell and believe it. That
    # includes rel_H and delta, not just c and kappa: Layer B measures r_H and realizes delta.
    # detector="empirical" is deliberately NOT one of dgp.DETECTORS, so Cell.se_sp raises on a
    # Layer B cell rather than returning a set (se, sp) that Layer B never had. INJECT.md 10.
    cell = Cell(pi=pi, c=nan, n=n, detector="empirical", kappa=nan, rho_v=nan, rel_H=nan,
                delta=nan, rho_T=rho_T, k=X.shape[1], r_F=nan, arm="layerB")
    sample = Sample(theta=theta, w=w, X=X, A=A, F=F, flag=flag, cell=cell)
    return InjectedSample(
        sample=sample,
        x_full=x_full,
        text_ids=text_ids,
        from_pool=from_pool,
        provenance={
            "human_pool": human_pool.name,
            "machine_pool": machine_pool.name,
            "trait": human_pool.trait,
            "n": n, "pi": pi, "p": p, "n_machine": int(n_m),
            "rho_T": rho_T, "k_chunks": k_chunks, "mode": mode, "replace": replace,
            "q1_drawn": q1,
            "standardizer": {"mu_H": mu_h, "sd_H": sd_h},
            "detector": det_note,
            "realized_sp": realized_sp, "realized_se": realized_se,
            "w": "CONSTRUCTED: w = rho_T * theta + u, Var(w) = 1; no corpus carries an outcome",
        },
    )


def exact_mixture_law(
    human_pool: Pool,
    machine_pool: Pool,
    pi: float,
    p: float,
    rho_T: float = 0.5,
    q1: float | None = None,
    mode: RandomMode = "respondent_marginal",
) -> dict[str, float]:
    """rho_obs from the FULL joint law, enumerated text by text. No kappa, delta, g, or Att.

    This exists to make the (E7) check non-vacuous. Going through `layer_b_moments`,
    `rho_H * Att` and the mixture correlation are the SAME algebraic expression -- `Den` is
    identically `Var(x)` once the human base sets `V_H = 1` -- so their agreement is a
    tautology that a bug in `assignment_moments` would sail straight through.

    Here the joint distribution over (respondent class, respondent label, pool text) is built
    explicitly from the assignment RULE and every moment is a weighted sum over that grid.
    A coding error in `assignment_moments` shows up as a disagreement. This is still the same
    mathematics computed twice, not an empirical test -- `test_moments_match_simulation`,
    which draws from `assign_indices`, is the check against the sampler.
    """
    mu_h, sd_h = _standardizer(human_pool)
    hp = human_pool.standardized(mu_h, sd_h)
    mp = machine_pool.standardized(mu_h, sd_h)
    q1 = hp.balance if q1 is None else q1
    if not 0.0 < q1 < 1.0:
        raise ValueError("q1 must be in (0, 1)")
    sd_l = np.sqrt(q1 * (1 - q1))

    probs: list[np.ndarray] = []
    xs: list[np.ndarray] = []
    thetas: list[np.ndarray] = []

    # human respondents: the respondent IS the text, so (x, L) is a uniform draw from the base
    n_h = len(hp)
    probs.append(np.full(n_h, (1 - pi) / n_h))
    xs.append(hp.scores)
    thetas.append((hp.labels - q1) / sd_l)

    # machine respondents: label ~ Bernoulli(q1) independent of A, then the assignment rule
    if pi > 0:
        u = random_branch_weights(mp, q1, mode)
        by_label = mp.indices_by_label()
        x_m = mp.scores
        for l in (0, 1):
            q_l = q1 if l == 1 else 1 - q1
            matched = np.zeros(len(mp))
            idx = by_label[l]
            if idx.size == 0:
                raise PoolCapacityError(f"pool {mp.name!r} has no label-{l} texts")
            matched[idx] = 1.0 / idx.size
            probs.append(pi * q_l * (p * matched + (1 - p) * u))
            xs.append(x_m)
            thetas.append(np.full(len(mp), (l - q1) / sd_l))

    w_p = np.concatenate(probs)
    x = np.concatenate(xs)
    th = np.concatenate(thetas)
    total = float(w_p.sum())
    if abs(total - 1.0) > 1e-12:
        raise AssertionError(f"enumerated law does not sum to 1 (got {total!r})")

    e_x = float(w_p @ x)
    e_th = float(w_p @ th)
    var_x = float(w_p @ (x**2)) - e_x**2
    cov_x_th = float(w_p @ (x * th)) - e_x * e_th
    # w = rho_T * theta + u with Var(w) = 1 and u independent of everything
    cov_x_w = rho_T * cov_x_th
    return {
        "rho_obs": float(cov_x_w / np.sqrt(var_x)) if var_x > 0 else float("nan"),
        "E_x": e_x, "Var_x": var_x, "Cov_x_theta": cov_x_th, "grid": int(w_p.size),
    }


def _chunks_or_none(pool: Pool, idx: np.ndarray, k: int) -> np.ndarray | None:
    if k == 1:
        return None
    rows = []
    for i in idx:
        cs = pool.texts[int(i)].chunk_scores
        if len(cs) < k:
            return None
        rows.append(cs[:k])
    return np.array(rows, dtype=float)


# ------------------------------------------------------------- exact Layer B population
def layer_b_moments(
    human_pool: Pool,
    machine_pool: Pool,
    pi: float,
    p: float,
    rho_T: float = 0.5,
    q1: float | None = None,
    mode: RandomMode = "respondent_marginal",
) -> dict[str, float]:
    """Exact Layer B population moments and the (E7) prediction, no Monte Carlo.

    Every quantity is finite-population arithmetic over the two pools, so
    `rho_obs_direct` and `rho_obs_pred` agree to machine precision when (E7) holds. That
    agreement is a test of (E7) against the injection design, and it is what the Layer B
    pilot cell will score its Monte Carlo against.
    """
    mu_h, sd_h = _standardizer(human_pool)
    hp = human_pool.standardized(mu_h, sd_h)
    mp = machine_pool.standardized(mu_h, sd_h)

    q1 = hp.balance if q1 is None else q1
    if not 0.0 < q1 < 1.0:
        raise ValueError("q1 must be in (0, 1)")
    sd_l = np.sqrt(q1 * (1 - q1))

    xh = hp.scores
    lh = hp.labels
    theta_h = (lh - q1) / sd_l
    # human moments in human-standardized units: mu_H = 0, V_H = 1 by construction
    v_h = float(xh.var(ddof=0))
    r_H = float(np.mean((xh - xh.mean()) * theta_h) / np.sqrt(v_h)) if v_h > 0 else float("nan")

    mm = assignment_moments(mp, p, q1=q1, mode=mode)
    kappa = mm.var  # = s2_M / V_H, since V_H = 1 in these units
    delta = -mm.mean  # CONVENTIONS sign: delta = (mu_H - mu_M) / sqrt(V_H), mu_H = 0
    c = mm.c
    cov_m_theta = c * np.sqrt(kappa)
    cov_h_theta = r_H * np.sqrt(v_h)
    g = float(cov_m_theta / cov_h_theta) if cov_h_theta != 0 else float("nan")

    rho_H = float(rho_T * r_H)
    N = (1 - pi) + pi * g
    Den = (1 - pi) + pi * kappa + pi * (1 - pi) * delta**2
    Att = float(N / np.sqrt(Den))

    # direct mixture correlation, computed without going through Att
    cov_xw = rho_T * ((1 - pi) * cov_h_theta + pi * cov_m_theta)
    e_x = pi * mm.mean
    e_x2 = (1 - pi) * (v_h + 0.0) + pi * (mm.var + mm.mean**2)
    var_x = e_x2 - e_x**2
    rho_obs_direct = float(cov_xw / np.sqrt(var_x)) if var_x > 0 else float("nan")

    return {
        "pi": pi, "p": p, "rho_T": rho_T, "q1": q1,
        "r_H": r_H, "rho_H": rho_H, "V_H": v_h,
        "c": c, "kappa": kappa, "delta": delta, "g": g,
        "N": float(N), "Den": float(Den), "Att": Att,
        "rho_obs_pred": float(rho_H * Att),
        "rho_obs_direct": rho_obs_direct,
        "e7_abs_error": abs(float(rho_H * Att) - rho_obs_direct),
    }
