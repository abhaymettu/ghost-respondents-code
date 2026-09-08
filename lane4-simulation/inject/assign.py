"""Assignment rules for the P1' coupling design (design-pivot-memo section 3.2, Prop. 16).

Replace a fraction pi of respondents with machine texts drawn from a labeled pool. Assign
respondent i a text by one of three rules -- random (c = 0), matched (text label == L_i,
c = c_pool), or matched with probability p -- and (E67) says

    c(p) = p c_pool,   kappa(p) = kappa_pool,   delta(p) = delta_pool.

The proof in the memo assumes a BALANCED pool and balanced respondent labels. This module
implements the general rule instead, because the balanced assumption is not on file for
either side (Q12) and the fix is one line of weighting:

    the random branch must draw from the same label marginal as the respondent labels,
    uniformly within a label cell.

With that, the marginal law of the injected score is exactly p-invariant for ANY pool
balance and ANY respondent balance, so (E67) holds exactly rather than approximately. See
INJECT.md 'The reweighting hook' for the two-line derivation and the test that shows the
naive uniform-over-texts random branch breaking invariance when the pool is unbalanced.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

from .pools import Pool

RandomMode = Literal["respondent_marginal", "balanced", "pool"]


class PoolCapacityError(RuntimeError):
    """Sampling without replacement would exhaust a label cell of the pool."""


def _q(resp_labels: np.ndarray) -> tuple[float, float]:
    """Respondent label marginal (q0, q1)."""
    lab = np.asarray(resp_labels)
    q1 = float(np.mean(lab == 1))
    return 1.0 - q1, q1


def random_branch_weights(pool: Pool, q1: float, mode: RandomMode) -> np.ndarray:
    """Per-text probabilities for the random (non-matched) branch. Sums to 1.

    respondent_marginal  u_t = q_{L_t} / N_{L_t}   -- exact E67 for any balance (default)
    balanced             u_t = 0.5   / N_{L_t}     -- memo Prop. 16 as written
    pool                 u_t = 1 / N              -- naive; breaks E67 unless the pool
                                                     balance equals the respondent balance
    """
    lab = pool.labels
    n = lab.size
    w = np.zeros(n, dtype=float)
    if mode == "pool":
        w[:] = 1.0 / n
        return w
    target = {0: 1.0 - q1, 1: q1} if mode == "respondent_marginal" else {0: 0.5, 1: 0.5}
    for l, idx in pool.indices_by_label().items():
        if idx.size == 0:
            if target[l] > 0:
                raise PoolCapacityError(
                    f"pool {pool.name!r} has no texts with label {l}, but the random branch "
                    f"needs to draw label {l} with probability {target[l]:.3f}"
                )
            continue
        w[idx] = target[l] / idx.size
    total = w.sum()
    if not np.isclose(total, 1.0):
        raise ValueError(f"random-branch weights sum to {total}, not 1")
    return w


# ------------------------------------------------------------------ exact population law
@dataclass(frozen=True)
class AssignmentMoments:
    """Exact population moments of the injected score under the rule, no Monte Carlo.

    The assignment law is a finite mixture over a finite pool, so every moment below is an
    arithmetic identity in the pool's scores -- which is why the E67 check in test_inject.py
    is exact to machine precision rather than within a Monte Carlo tolerance.
    """

    p: float
    mean: float
    var: float
    c: float  # Cor(x_M, theta) with theta the standardized respondent label
    cond_mean: tuple[float, float]  # E[x | L_i = 0], E[x | L_i = 1]
    q1: float
    mode: str


def assignment_moments(
    pool: Pool, p: float, q1: float = 0.5, mode: RandomMode = "respondent_marginal"
) -> AssignmentMoments:
    """Exact moments of the injected machine score under p-matching."""
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must be in [0, 1]")
    if not 0.0 < q1 < 1.0:
        raise ValueError("q1 must be in (0, 1): a degenerate respondent label has no coupling")
    x = pool.scores
    u = random_branch_weights(pool, q1, mode)
    mu_u = float(u @ x)
    m2_u = float(u @ (x**2))

    by_label = pool.indices_by_label()
    cond_mean = []
    cond_m2 = []
    for l in (0, 1):
        idx = by_label[l]
        if idx.size == 0:
            raise PoolCapacityError(
                f"pool {pool.name!r} has no texts with label {l}; matched assignment is "
                "undefined for respondents with that label"
            )
        cond_mean.append(p * float(np.mean(x[idx])) + (1 - p) * mu_u)
        cond_m2.append(p * float(np.mean(x[idx] ** 2)) + (1 - p) * m2_u)

    q = (1.0 - q1, q1)
    mean = sum(qi * mi for qi, mi in zip(q, cond_mean))
    m2 = sum(qi * mi for qi, mi in zip(q, cond_m2))
    var = m2 - mean**2
    sd_l = np.sqrt(q1 * (1 - q1))
    cov = sum(qi * mi * (l - q1) / sd_l for l, (qi, mi) in enumerate(zip(q, cond_mean)))
    c = cov / np.sqrt(var) if var > 0 else float("nan")
    return AssignmentMoments(p, mean, var, float(c), (cond_mean[0], cond_mean[1]), q1, mode)


def pool_coupling(pool: Pool, q1: float = 0.5, mode: RandomMode = "respondent_marginal") -> float:
    """c_pool as the design realizes it: the p = 1 endpoint of assignment_moments.

    NOTE this is the label-marginal-REWEIGHTED coupling, which differs from the raw
    Cor(x, L | pool) lane 3 reports when the pool is unbalanced. INJECT.md 'What c_pool
    means' says which number belongs in the paper.
    """
    return assignment_moments(pool, 1.0, q1, mode).c


def raw_pool_coupling(pool: Pool) -> float:
    """Cor(x, L | pool) on the pool as it sits: lane 3's c-hat, unreweighted."""
    lab = pool.labels.astype(float)
    x = pool.scores
    if lab.std() == 0 or x.std() == 0:
        return float("nan")
    return float(np.corrcoef(x, lab)[0, 1])


# ---------------------------------------------------------------------------- sampling
def capacity_report(resp_labels: np.ndarray, pool: Pool, p: float,
                    mode: RandomMode = "respondent_marginal",
                    q1: float | None = None) -> dict[int, tuple[float, int]]:
    """Expected demand vs. availability per label cell, for without-replacement assignment."""
    lab = np.asarray(resp_labels)
    n_m = lab.size
    q1 = _q(lab)[1] if q1 is None else q1
    u = random_branch_weights(pool, q1, mode)
    by_label = pool.indices_by_label()
    out: dict[int, tuple[float, int]] = {}
    for l in (0, 1):
        n_matched = float(np.sum(lab == l))
        p_random_l = float(u[by_label[l]].sum())
        demand = p * n_matched + (1 - p) * n_m * p_random_l
        out[l] = (demand, int(by_label[l].size))
    return out


def assign_indices(
    rng: np.random.Generator,
    resp_labels: np.ndarray,
    pool: Pool,
    p: float,
    replace: bool = False,
    mode: RandomMode = "respondent_marginal",
    q1: float | None = None,
) -> np.ndarray:
    """Pool-text index assigned to each respondent in `resp_labels`.

    p = 0 is the random rule, p = 1 the matched rule, in between the p-matched rule.
    Without replacement, exhausting a label cell raises rather than silently falling back
    to the other cell: a fallback would quietly change the label marginal and with it the
    realized c, which is the one quantity this design exists to control.
    """
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must be in [0, 1]")
    lab = np.asarray(resp_labels).astype(int)
    n_m = lab.size
    if n_m == 0:
        return np.empty(0, dtype=int)
    # q1 is the respondent label marginal the random branch is reweighted to. It defaults to
    # this subsample's own marginal, but the caller should pass the marginal of the FULL
    # respondent sample -- the one theta is standardized by -- so that the assignment law and
    # the population moments in build.layer_b_moments refer to the same q1. They agree only
    # asymptotically otherwise, and the gap is widest exactly where pilot cells live (small pi).
    q1 = _q(lab)[1] if q1 is None else q1
    if not 0.0 < q1 < 1.0:
        raise ValueError("q1 must be in (0, 1)")
    u = random_branch_weights(pool, q1, mode)
    by_label = pool.indices_by_label()
    p_label = {l: float(u[by_label[l]].sum()) for l in (0, 1)}

    if not replace:
        for l, (demand, avail) in capacity_report(lab, pool, p, mode, q1).items():
            if demand > avail:
                raise PoolCapacityError(
                    f"pool {pool.name!r} label cell {l}: expected demand {demand:.1f} exceeds "
                    f"{avail} available texts at p={p}, n_machine={n_m}. Pool a second "
                    "generator, lower pi, or pass replace=True (memo 3.2 'Coverage')."
                )

    matched = rng.random(n_m) < p
    draw_label = np.where(
        matched, lab, (rng.random(n_m) < p_label[1]).astype(int)
    )

    out = np.empty(n_m, dtype=int)
    if replace:
        for l in (0, 1):
            sel = np.flatnonzero(draw_label == l)
            if sel.size:
                out[sel] = rng.choice(by_label[l], size=sel.size, replace=True)
        return out

    remaining = {l: list(rng.permutation(by_label[l])) for l in (0, 1)}
    for i in range(n_m):
        l = int(draw_label[i])
        if not remaining[l]:
            raise PoolCapacityError(
                f"pool {pool.name!r} label cell {l} exhausted after {i} of {n_m} assignments "
                f"at p={p} (had {by_label[l].size} texts). Realized demand exceeded the "
                "expectation; raise the pool size or pass replace=True."
            )
        out[i] = remaining[l].pop()
    return out


def realized_coupling(scores: np.ndarray, resp_labels: np.ndarray) -> float:
    """Cor(x, theta) in one realized assignment, theta the standardized respondent label."""
    x = np.asarray(scores, dtype=float)
    lab = np.asarray(resp_labels, dtype=float)
    if x.size < 2 or x.std() == 0 or lab.std() == 0:
        return float("nan")
    return float(np.corrcoef(x, lab)[0, 1])
