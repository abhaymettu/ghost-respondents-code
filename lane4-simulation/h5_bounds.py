"""H5 partial-identification bounds on rho_H (SPEC.md line 109), for the detector=none
sub-case of the 72-cell boundary map: gpt-4/EXT, n=1000, pi in 6 values x p in {0, 0.5, 1}.

The bound treats c as the unidentified nuisance parameter and pi as known, and uses the
E36/E17 closed forms already proven in derivations/lane1-partial-coupling.md, as
pass3-methods-review.md B3 names them: Att(pi, c) is affine and increasing in c at fixed pi
(E36), and this study's pools cannot realize c beyond c_pool = 0.379 (gpt-4/EXT,
LAYERB-GRID.md section 1.2) -- the paper's own Limitations section already says c > 0.379 is
unreachable here, so c_pool is the honest upper bound to use rather than the structural c=1.

rho_obs = rho_H * Att(pi, c) holds exactly only when there is no detection/selection step
(detector = none); detection adds a collider term (E30-E34) not part of this bound, so this
script does not cover calibrated/degraded/oracle cells -- see GAPS-CLOSURE-SPEC.md #2.

rho_obs_hat is read from the frozen results/layerb-grid/grid.jsonl record: naive's mean
point estimate at each cell (truth.rho_H + naive's rho_H bias), since fit_naive returns the
raw sample correlation, i.e. an unbiased estimate of rho_obs itself.

pi is used at its true (simulation) value, not an estimated pi_hat -- T3 shows pi_hat misses
by 5-6 points, so a bound conditioned on pi_hat would be wider and noisier than this one;
this script isolates what c-uncertainty alone contributes, stated explicitly as a limitation.

Run:  lane4-simulation/.venv/bin/python h5_bounds.py
"""
from __future__ import annotations

import json
from pathlib import Path

from population import att

ROOT = Path(__file__).resolve().parent
GRID = ROOT / "results" / "layerb-grid" / "grid.jsonl"
OUT_DIR = ROOT / "results" / "h5-bounds"

KAPPA = 0.798
DELTA = 0.534
C_POOL = 0.379
REL_H = 0.018255429162021216  # rel_H_true, gpt-4/EXT (setup.rel_H_true, every core cell)
WIDTH_THRESHOLD = 0.2  # SPEC.md line 109


def load_none_cells() -> list[dict]:
    rows = []
    with GRID.open() as f:
        for line in f:
            d = json.loads(line)
            c = d["cell"]
            if (
                c["pool"] == "personallm_gpt-4-0613"
                and c["trait"] == "EXT"
                and c["arm"] == "box"
                and c["n"] == 1000
                and c["detector"] == "none"
            ):
                rows.append(
                    {
                        "pi": c["pi"],
                        "p": c["p"],
                        "truth_rho_H": d["truth"]["rho_H"],
                        "rho_obs_hat": d["truth"]["rho_H"] + d["estimators"]["naive"]["rho_H"]["bias"],
                    }
                )
    return sorted(rows, key=lambda r: (r["pi"], r["p"]))


def bound(pi: float, rho_obs_hat: float) -> tuple[float, float]:
    att_lo = att(pi, 0.0, REL_H, KAPPA, DELTA)
    att_hi = att(pi, C_POOL, REL_H, KAPPA, DELTA)
    lo = rho_obs_hat / att_hi
    hi = rho_obs_hat / att_lo
    return lo, hi


def main() -> None:
    cells = load_none_cells()
    results = []
    for cell in cells:
        lo, hi = bound(cell["pi"], cell["rho_obs_hat"])
        width = hi - lo
        results.append(
            {
                **cell,
                "bound_lo": lo,
                "bound_hi": hi,
                "width": width,
                "passes_0.2": bool(width < WIDTH_THRESHOLD),
                "truth_in_bound": bool(lo <= cell["truth_rho_H"] <= hi),
            }
        )
    n_pass = sum(r["passes_0.2"] for r in results)
    n_covers_truth = sum(r["truth_in_bound"] for r in results)
    summary = {
        "kappa": KAPPA,
        "delta": DELTA,
        "c_pool": C_POOL,
        "rel_H": REL_H,
        "width_threshold": WIDTH_THRESHOLD,
        "n_cells": len(results),
        "n_width_under_threshold": n_pass,
        "n_truth_covered": n_covers_truth,
        "cells": results,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "bounds.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"{n_pass}/{len(results)} cells have bound width < {WIDTH_THRESHOLD}")
    print(f"{n_covers_truth}/{len(results)} bounds cover the true rho_H")
    for r in results:
        print(
            f"pi={r['pi']:.2f} p={r['p']:.1f} "
            f"bound=[{r['bound_lo']:.4f}, {r['bound_hi']:.4f}] width={r['width']:.4f} "
            f"truth={r['truth_rho_H']:.4f} covered={r['truth_in_bound']}"
        )


if __name__ == "__main__":
    main()
