"""Direct moment extraction for the P2-3 arms: the moments the grid does not record.

`grid.py` summarizes estimator output, so pass 2 could only reach the closed forms that an
estimator's plim happens to equal. Four of the equations P2-3 flags are not of that kind:

    (E2)  E[x] = mu_H - pi Delta
    (E3)  Var(x) = V_H Den(pi)
    (E4)  Cov(x, w) = b s2_T N,  and (E19) its between-mean form under A1'
    (E29) Sigma_obs = (1-pi) Sigma_H + pi Sigma_M + pi(1-pi) Delta Delta^T, and Prop. 10's
          asymmetry: that rank-one authorship factor is in every item covariance and in NO
          Cov(x_j, w)

This module re-simulates each arm cell from the same `rep_rng(master_seed, cell, rep)` streams
the grid run used and measures those moments directly. Same draws, so the correlation it
reports for a cell reproduces that cell's `fit_naive` output to floating point -- checked, and
printed as a control.

Sample means, variances and covariances are unbiased, so unlike the correlation checks of
pass 2 these carry no finite-sample correction term.

    .venv/bin/python arm_moments.py --out results/grid-nonignorable/moments.json
"""

from __future__ import annotations

import argparse
import json
import sys
from math import sqrt
from pathlib import Path

import numpy as np
from dataclasses import asdict

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dgp import Cell, rep_rng, simulate
from grid import full_grid
from run_grid_full import GRID_MASTER_SEED, REPS

ARMS = ("nonignorable", "delta", "flip")

# The D1 lever (pass-2 flag P2-4). The manufactured survivor mean gap of (E47),
# delta_pass = delta + r_F lam sqrt(rel_H), moves the survivor moment by only 0.20 MCSE
# anywhere on the frozen grid, because delta = 0 there leaves r_F lam sqrt(rel_H) as the whole
# of it. At delta = 3 it is a 4th of a SD, and at n = 5000 with 5000 reps the separation from
# the pre-D1 reading is ~17 MCSE: decidable. No estimator runs here, so the extra reps are free.
D1_CELL = Cell(pi=0.30, c=0.0, n=5000, detector="degraded", kappa=0.5, rho_v=0.0,
               delta=3.0, d_theta=0.0, arm="d1lever")
D1_REPS = 5000


def moments_closed_form(cell: Cell) -> dict:
    """Population moments in dgp.py's normalization (s2_T = 1, V_H = 1/rel_H, mu_H = 0).

    Written out here rather than imported so the arms are checked against the derivations'
    equations, not against population.py -- the same discipline as pass 2 section 1.1.
    """
    pi, c, kap, rel, dl, rt, rv, dt = (cell.pi, cell.c, cell.kappa, cell.rel_H, cell.delta,
                                       cell.rho_T, cell.rho_v, cell.d_theta)
    V_H, b, Delta = 1.0 / rel, rt, dl * sqrt(1.0 / rel)
    s2_M, g = kap * V_H, c * sqrt(kap / rel)
    r_M = c ** 2 + rv * (1.0 - c ** 2)                                          # (E24)
    Den = (1.0 - pi) + pi * kap + pi * (1.0 - pi) * dl ** 2                      # (E0b)
    N = (1.0 - pi) + pi * g                                                      # (E0a)
    between = pi * (1.0 - pi) * Delta ** 2                                       # rank-one term
    return {
        "E_x": -pi * Delta,                                                      # (E2)
        "Var_x": V_H * Den,                                                      # (E3), (E41)
        "Cov_xw": b * (N - pi * (1.0 - pi) * Delta * dt),                         # (E4), (E19)
        "Var_w": 1.0 + rt ** 2 * pi * (1.0 - pi) * dt ** 2,                       # (E20)
        "Sigma_offdiag": (1.0 - pi) * 1.0 + pi * s2_M * r_M + between,            # (E25), (E29)
        "Sigma_diag": V_H * Den,                                                  # (E3)
        "rank_one_term": between,                                                 # (E29)
        **{f"gap_{j}": Delta for j in range(cell.k)},   # (E29) uniform loadings Delta_j = Delta
    }


def measure(cell: Cell, reps: int, master_seed: int) -> dict:
    """Per-rep sample moments over `reps` replications of this cell's own seed streams."""
    keys = ("E_x", "Var_x", "Cov_xw", "Var_w", "Sigma_offdiag", "Sigma_diag",
            "cor_xw", "cor_xw_pass", "r_between")
    acc: dict[str, list[float]] = {k: [] for k in keys}
    gaps: list[np.ndarray] = []
    for rep in range(reps):
        s = simulate(cell, rep_rng(master_seed, cell, rep))
        x, w, X = s.x, s.w, s.X
        k = X.shape[1]
        acc["E_x"].append(float(x.mean()))
        acc["Var_x"].append(float(np.var(x, ddof=1)))
        acc["Var_w"].append(float(np.var(w, ddof=1)))
        acc["Cov_xw"].append(float(np.cov(x, w, ddof=1)[0, 1]))
        S = np.cov(X, rowvar=False, ddof=1)
        iu = np.triu_indices(k, k=1)
        acc["Sigma_offdiag"].append(float(S[iu].mean()))
        acc["Sigma_diag"].append(float(np.diag(S).mean()))
        acc["cor_xw"].append(float(np.corrcoef(x, w)[0, 1]))
        p = s.passed
        acc["cor_xw_pass"].append(float(np.corrcoef(x[p], w[p])[0, 1]) if p.sum() > 2 else np.nan)
        C = np.corrcoef(X, rowvar=False)
        acc["r_between"].append(float(C[iu].mean()))
        # Prop. 10 / (E29): the between-class block is the rank-one pi(1-pi) Delta Delta^T, so
        # the authorship mean-gap VECTOR must be Delta in every coordinate. Measuring the gap
        # itself keeps the statistic linear and unbiased; the top singular value of the
        # stripped matrix does not (it is upward-biased by ~0.005 whatever the signal, which
        # swamps the z-score wherever pi(1-pi)Delta^2 is small).
        H, M = s.A == 0, s.A == 1
        if H.sum() > 1 and M.sum() > 1:
            gaps.append(X[H].mean(axis=0) - X[M].mean(axis=0))
    out = {}
    for k_, v in acc.items():
        a = np.asarray(v, float)
        a = a[~np.isnan(a)]
        out[k_] = {"mean": float(a.mean()), "mcse": float(a.std(ddof=1) / sqrt(len(a))),
                   "n": int(len(a))}
    if gaps:
        G = np.vstack(gaps)
        for j in range(G.shape[1]):
            out[f"gap_{j}"] = {"mean": float(G[:, j].mean()),
                               "mcse": float(G[:, j].std(ddof=1) / sqrt(len(G))), "n": int(len(G))}
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Measure the moments the grid does not record.")
    ap.add_argument("--out", default="results/grid-nonignorable/moments.json")
    args = ap.parse_args()
    here = Path(__file__).resolve().parent

    cells = sorted(full_grid(ARMS), key=lambda c: c.cell_id)
    payload = []
    for i, cell in enumerate(cells, 1):
        emp = measure(cell, REPS, GRID_MASTER_SEED)
        payload.append({"cell_id": cell.cell_id, "cell": asdict(cell),
                        "reps": REPS, "closed_form": moments_closed_form(cell), "empirical": emp})
        print(f"  [{i:2d}/{len(cells)}] {cell.arm:13s} pi={cell.pi} delta={cell.delta} "
              f"d_theta={cell.d_theta} c={cell.c} det={cell.detector}  "
              f"cor_xw={emp['cor_xw']['mean']:+.5f}", flush=True)

    print(f"D1 lever: {D1_CELL.arm} n={D1_CELL.n} delta={D1_CELL.delta} reps={D1_REPS}", flush=True)
    emp = measure(D1_CELL, D1_REPS, GRID_MASTER_SEED)
    payload.append({"cell_id": D1_CELL.cell_id, "cell": asdict(D1_CELL),
                    "reps": D1_REPS, "closed_form": moments_closed_form(D1_CELL), "empirical": emp})

    out_path = (here / args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=1))
    print(f"-> {out_path}")


if __name__ == "__main__":
    main()
