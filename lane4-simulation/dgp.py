"""Layer A data-generating process (SPEC 4.1, lane 1 notation N1/N3/Q7).

Scale normalization is fixed: s2_T = Var(theta) = 1, V_w = Var(w) = 1, mu_H = 0.
See CONVENTIONS.md; every symbol matches derivations/lane1-zero-coupling.md section 0.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field

import numpy as np
from scipy.stats import norm

# se = P(flag | M), sp = P(pass | H).  SPEC 2.4 / 4.3 operating points.
DETECTORS: dict[str, tuple[float, float]] = {
    "none": (0.00, 1.00),
    "calibrated": (0.95, 0.99),
    "degraded": (0.85, 0.85),
    "oracle": (1.00, 1.00),
}


@dataclass(frozen=True)
class Cell:
    """One grid cell. Field order is the canonical order for cell ids."""

    pi: float
    c: float
    n: int
    detector: str
    kappa: float
    rho_v: float = 0.0
    rel_H: float = 0.7
    delta: float = 0.0
    rho_T: float = 0.5
    k: int = 4
    r_F: float = 0.3
    d_theta: float = 0.0
    arm: str = "base"

    # --- derived scale quantities (all from CONVENTIONS.md) ---
    @property
    def V_H(self) -> float:
        return 1.0 / self.rel_H

    @property
    def s2_H(self) -> float:
        return self.V_H - 1.0

    @property
    def s2_M(self) -> float:
        return self.kappa * self.V_H

    @property
    def Delta(self) -> float:
        return self.delta * np.sqrt(self.V_H)

    @property
    def mu_M(self) -> float:
        return -self.Delta

    @property
    def b(self) -> float:
        return self.rho_T

    @property
    def s2_u(self) -> float:
        return 1.0 - self.rho_T**2

    @property
    def lam_M(self) -> float:
        """Machine slope on theta; lane 1's g = c sqrt(s2_M / s2_T) (N1)."""
        return self.c * np.sqrt(self.s2_M)

    @property
    def s2_v(self) -> float:
        return (1.0 - self.c**2) * self.s2_M

    @property
    def se_sp(self) -> tuple[float, float]:
        return DETECTORS[self.detector]

    # --- truth values the metrics score against ---
    @property
    def rho_H(self) -> float:
        """Cor(x, w | H) = sqrt(rel_H) rho_T. Primary estimand (N2)."""
        return np.sqrt(self.rel_H) * self.rho_T

    @property
    def loading(self) -> float:
        """True standardized parallel-item loading."""
        return np.sqrt(self.rel_H)

    @property
    def cell_id(self) -> str:
        payload = "|".join(f"{k}={v}" for k, v in sorted(asdict(self).items()))
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


@dataclass
class Sample:
    theta: np.ndarray  # (n,)
    w: np.ndarray  # (n,)
    X: np.ndarray  # (n, k); X[:, 0] is the headline single indicator
    A: np.ndarray  # (n,) uint8, 1 = machine
    F: np.ndarray  # (n,) fluency
    flag: np.ndarray  # (n,) bool, detector flagged as machine
    cell: Cell = field(repr=False)

    @property
    def x(self) -> np.ndarray:
        """Headline single indicator (every lane-1 closed form is single-indicator)."""
        return self.X[:, 0]

    @property
    def passed(self) -> np.ndarray:
        return ~self.flag


def simulate(cell: Cell, rng: np.random.Generator) -> Sample:
    n, k = cell.n, cell.k

    A = (rng.random(n) < cell.pi).astype(np.uint8)
    # A1' (lane 1 section 4b): theta | M ~ N(d_theta, 1). d_theta = 0 recovers A1.
    theta = rng.standard_normal(n) + cell.d_theta * A
    w = cell.b * theta + np.sqrt(cell.s2_u) * rng.standard_normal(n)

    # Human: x_ij = mu_H + theta_i + e_ij, mu_H = 0.
    e = np.sqrt(cell.s2_H) * rng.standard_normal((n, k))
    X_H = theta[:, None] + e

    # Machine: x_ij = mu_M + lam_M (theta_i - d_theta) + v_ij, v equicorrelated rho_v.
    # Equicorrelated draw: v_j = sqrt(rho_v) z_shared + sqrt(1 - rho_v) z_j, scaled by sd_v.
    sd_v = np.sqrt(cell.s2_v)
    z_shared = rng.standard_normal((n, 1))
    z_ind = rng.standard_normal((n, k))
    v = sd_v * (np.sqrt(cell.rho_v) * z_shared + np.sqrt(1.0 - cell.rho_v) * z_ind)
    X_M = cell.mu_M + cell.lam_M * (theta - cell.d_theta)[:, None] + v

    X = np.where(A[:, None] == 1, X_M, X_H)

    # Fluency and detector (lane 1 section 6.3): F = r_F theta + sqrt(1 - r_F^2) eta.
    F = cell.r_F * theta + np.sqrt(1.0 - cell.r_F**2) * rng.standard_normal(n)
    se, sp = cell.se_sp
    tau = -np.inf if sp >= 1.0 else norm.ppf(1.0 - sp)
    flag_H = F <= tau  # humans fail the threshold
    flag_M = rng.random(n) < se  # machine flagged independently of theta
    flag = np.where(A == 1, flag_M, flag_H)

    return Sample(theta=theta, w=w, X=X, A=A, F=F, flag=flag, cell=cell)


def rep_rng(master_seed: int, cell: Cell, rep: int) -> np.random.Generator:
    """Reproducible per-(cell, rep) stream; independent of shard boundaries."""
    key = int(hashlib.sha256(f"{cell.cell_id}:{rep}".encode()).hexdigest()[:16], 16)
    return np.random.default_rng(np.random.SeedSequence([master_seed, key]))
