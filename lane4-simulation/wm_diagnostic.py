"""Paired diagnostic for the watermark cell (WATERMARK.md): same injection draws, only the
detector flag (se, sp) varies, isolating the true accuracy effect from the across-cell seed
noise that the as-run grid (run_watermark_grid.py) inherits from LAYERB-GRID.md's convention
of hashing `detector` into the cell seed. `fit_delete` only; naive does not consume `flag`.

    .venv/bin/python wm_diagnostic.py > results/watermark/diagnostic.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from estimators import fit_delete
from inject.build import build_injected_sample
from run_layerb_grid import FRONTIER, K_CHUNKS, RHO_T, setup

N = 1000
NREP = 400
SEED = 20260910


def sweep(pi: float, p: float, fixed_axis: str, fixed_val: float, sweep_vals, S) -> list[dict]:
    """fixed_axis='joint' sweeps se=sp=x together; else holds `fixed_axis` at `fixed_val` and
    sweeps the other axis through `sweep_vals`."""
    rows = []
    for x in sweep_vals:
        if fixed_axis == "joint":
            se, sp = x, x
        else:
            se, sp = (x, fixed_val) if fixed_axis == "sp" else (fixed_val, x)
        biases = []
        for rep in range(NREP):
            rng = np.random.default_rng(np.random.SeedSequence([SEED, rep]))
            inj = build_injected_sample(S["H_b"], S["M_i"], N, pi, p, rng,
                                        rho_T=RHO_T, k_chunks=K_CHUNKS, sp=1.0, replace=True)
            s = inj.sample
            u = rng.random(N)
            s.flag = np.where(s.A == 1, u < se, u < (1.0 - sp))
            f = fit_delete(s)
            biases.append(f.rho_H_hat - S["rho_H_true"])
        biases = np.array(biases)
        rows.append({"pi": pi, "p": p, "se": se, "sp": sp,
                     "mean_bias": float(biases.mean()),
                     "mcse": float(biases.std(ddof=1) / np.sqrt(len(biases))), "n_rep": NREP})
    return rows


def main() -> None:
    S = setup(FRONTIER, "EXT")
    out = {
        "truth_rho_H": S["rho_H_true"], "n_rep": NREP, "n": N, "seed": SEED,
        "estimator": "delete",
        "accuracy_trajectory_pi030_p1": sweep(0.30, 1.0, "joint", None,
                                              [0.95, 0.99, 1.0], S),
        "prop14_test_pi030_p1_sp_fixed_085": sweep(0.30, 1.0, "sp", 0.85,
                                                    [0.85, 0.90, 0.95, 0.99, 1.0], S),
        "prop14_test_pi030_p1_se_fixed_085": sweep(0.30, 1.0, "se", 0.85,
                                                    [0.85, 0.90, 0.95, 0.99, 1.0], S),
        "prop14_test_pi005_p1_sp_fixed_085": sweep(0.05, 1.0, "sp", 0.85, [0.85, 1.0], S),
        "prop14_test_pi005_p1_se_fixed_085": sweep(0.05, 1.0, "se", 0.85, [0.85, 1.0], S),
    }
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
