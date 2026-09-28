"""Task 4 of the H5-detected close-out: apply both bounds to the 54 real detected cells.

54 cells = gpt-4/EXT/box/n=1000, detector in {calibrated, degraded, oracle} x pi (6 levels)
x p (3 levels). Reuses run_layerb_grid.py's exact cell construction (LBCell, rep_rng,
setup, MASTER_SEED, SP_TARGET) so the built samples are BIT-IDENTICAL to the frozen
results/layerb-grid/grid.jsonl run at the same (cell, rep) -- same master seed, same
cell_id hash, same frozen calibration split. Only fit_naive/fit_delete-equivalent Pearson
correlations are computed per rep (not the full 8-estimator suite), which is why this reruns
in seconds rather than the original grid's ~11000 core-seconds.

Two bounds per cell, both using the Imbens-Manski union of sampling + identification
uncertainty (95% Fisher-z CI on the point estimate, propagated through both Att endpoints):

  naive bound      (existing, h5_bounds.py / fit_bounds_c): rho_obs_hat = Cor(x, w) on the
                    FULL (undeleted) sample; Att(pi, c) from (E7); c in [0, c_pool=0.379].
  survivor bound    (new, Prop. 18 / h5_bounds_detected.att_pass): rho_pass_hat = Cor(x, w)
                    on detector survivors; Att_pass(pi, c, ...) from (E51); same c range.
                    Reported for r_F = r_F_hat (task 1's estimate) and r_F = 0.

se, sp fed to att_pass are this cell's REALIZED values (computed once from the fixed H_b/M_i
detector columns via inject.build.detector_flags at the cell's target specificity -- constant
across reps since H_b/M_i do not change rep to rep), not the target/nominal operating point,
so the survivor bound uses the same detector performance the sample was actually built with.

Run:  lane4-simulation/.venv/bin/python layerB_apply.py [--reps 100]
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from estimators import _fisher_ci, _pearson
from h5_bounds_detected import att_pass
from inject.build import build_injected_sample, detector_flags
from population import att
from run_layerb_grid import FRONTIER, K_CHUNKS, RHO_T, SP_TARGET, LBCell, rep_rng, setup

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "h5-bounds-detected" / "layerB_application.json"

KAPPA = 0.798
DELTA = 0.534
REL_H = 0.018255429162021216
RHO_H_TRUE = 0.06755632679849685
C_LO, C_HI = 0.0, 0.379
PI_LEVELS = (0.01, 0.02, 0.05, 0.10, 0.20, 0.30)
P_LEVELS = (0.0, 0.5, 1.0)
DETECTOR_LEVELS = ("calibrated", "degraded", "oracle")
N = 1000


def invert(r: float, n: int, att_lo: float, att_hi: float) -> tuple[float, float]:
    ci = _fisher_ci(r, n) or (r, r)
    ep = (ci[0] / att_hi, ci[1] / att_lo)
    return min(ep), max(ep)


def run_cell(cell: LBCell, S: dict, reps: int, r_F_hat: float) -> dict:
    detector = cell.detector
    if detector == "oracle":
        se_real, sp_real = 1.0, 1.0
    else:
        _, sp_real, se_real = detector_flags(S["H_b"].detector, S["M_i"].detector,
                                              SP_TARGET[detector])

    pi = cell.pi
    bounds = {
        "naive": {
            "r_F_used": None,
            "att_lo": att(pi, C_LO, REL_H, KAPPA, DELTA),
            "att_hi": att(pi, C_HI, REL_H, KAPPA, DELTA),
            "widths": [], "covers": [],
        },
        "survivor_rF_hat": {
            "r_F_used": r_F_hat,
            "att_lo": att_pass(pi, C_LO, REL_H, KAPPA, DELTA, RHO_T, r_F_hat, se_real, sp_real),
            "att_hi": att_pass(pi, C_HI, REL_H, KAPPA, DELTA, RHO_T, r_F_hat, se_real, sp_real),
            "widths": [], "covers": [],
        },
        "survivor_rF_0": {
            "r_F_used": 0.0,
            "att_lo": att_pass(pi, C_LO, REL_H, KAPPA, DELTA, RHO_T, 0.0, se_real, sp_real),
            "att_hi": att_pass(pi, C_HI, REL_H, KAPPA, DELTA, RHO_T, 0.0, se_real, sp_real),
            "widths": [], "covers": [],
        },
    }

    n_pass_list, rho_obs_list, rho_pass_list = [], [], []

    for rep in range(reps):
        rng = rep_rng(cell, rep)
        inj = build_injected_sample(S["H_b"], S["M_i"], cell.n, cell.pi, cell.p, rng,
                                     rho_T=RHO_T, k_chunks=K_CHUNKS,
                                     sp=SP_TARGET[detector], replace=True)
        s = inj.sample
        if detector == "oracle":
            s.flag = s.A == 1
        passed = s.passed
        n_pass = int(passed.sum())
        n_pass_list.append(n_pass)

        rho_obs_hat = _pearson(s.x, s.w)
        rho_pass_hat = _pearson(s.x[passed], s.w[passed])
        rho_obs_list.append(rho_obs_hat)
        rho_pass_list.append(rho_pass_hat)

        lo_n, hi_n = invert(rho_obs_hat, s.x.size, bounds["naive"]["att_lo"], bounds["naive"]["att_hi"])
        bounds["naive"]["widths"].append(hi_n - lo_n)
        bounds["naive"]["covers"].append(bool(lo_n <= RHO_H_TRUE <= hi_n))

        for key in ("survivor_rF_hat", "survivor_rF_0"):
            lo, hi = invert(rho_pass_hat, n_pass, bounds[key]["att_lo"], bounds[key]["att_hi"])
            bounds[key]["widths"].append(hi - lo)
            bounds[key]["covers"].append(bool(lo <= RHO_H_TRUE <= hi))

    naive_widths = np.array(bounds["naive"]["widths"])
    surv_widths_hat = np.array(bounds["survivor_rF_hat"]["widths"])
    n_narrower = int(np.sum(surv_widths_hat < naive_widths))

    out = {
        "pi": cell.pi, "p": cell.p, "detector": detector,
        "se_realized": se_real, "sp_realized": sp_real,
        "mean_n_pass": float(np.mean(n_pass_list)),
        "mean_rho_obs_hat": float(np.nanmean(rho_obs_list)),
        "mean_rho_pass_hat": float(np.nanmean(rho_pass_list)),
    }
    field_names = {
        "naive": "naive_bound",
        "survivor_rF_hat": "survivor_bound_rF_hat",
        "survivor_rF_0": "survivor_bound_rF_0",
    }
    for key, field in field_names.items():
        b = bounds[key]
        entry: dict = {}
        if b["r_F_used"] is not None:
            entry["r_F_used"] = b["r_F_used"]
        entry["median_width"] = float(np.median(b["widths"]))
        entry["coverage"] = float(np.mean(b["covers"]))
        out[field] = entry
    out["share_survivor_narrower_than_naive_rF_hat"] = n_narrower / reps
    out["reps"] = reps
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=100)
    args = ap.parse_args()

    r_f_path = ROOT / "results" / "h5-bounds-detected" / "r_f_estimation.json"
    r_F_hat = json.loads(r_f_path.read_text())["human_pool_diagnostics"][
        "r_F_hat_population_convention"]["point"]
    print(f"Using r_F_hat = {r_F_hat:.4f} (population convention) from {r_f_path}")

    t0 = time.time()
    S = setup(FRONTIER, "EXT")
    cells = [LBCell(pi=pi, n=N, p=p, detector=d)
             for d in DETECTOR_LEVELS for pi in PI_LEVELS for p in P_LEVELS]
    assert len(cells) == 54, len(cells)

    results = []
    for cell in cells:
        results.append(run_cell(cell, S, args.reps, r_F_hat))
    elapsed = time.time() - t0
    print(f"{len(cells)} cells x {args.reps} reps in {elapsed:.1f}s")

    by_detector: dict[str, list[dict]] = {d: [] for d in DETECTOR_LEVELS}
    for r in results:
        by_detector[r["detector"]].append(r)

    summary_by_detector = {}
    for d, rows in by_detector.items():
        naive_med_widths = [r["naive_bound"]["median_width"] for r in rows]
        naive_covs = [r["naive_bound"]["coverage"] for r in rows]
        surv_med_widths = [r["survivor_bound_rF_hat"]["median_width"] for r in rows]
        surv_covs = [r["survivor_bound_rF_hat"]["coverage"] for r in rows]
        surv0_med_widths = [r["survivor_bound_rF_0"]["median_width"] for r in rows]
        surv0_covs = [r["survivor_bound_rF_0"]["coverage"] for r in rows]
        shares_narrower = [r["share_survivor_narrower_than_naive_rF_hat"] for r in rows]
        summary_by_detector[d] = {
            "n_cells": len(rows),
            "naive": {"median_of_median_widths": float(np.median(naive_med_widths)),
                      "mean_coverage": float(np.mean(naive_covs)),
                      "n_cells_coverage_ge_95pct": sum(1 for c in naive_covs if c >= 0.95)},
            "survivor_rF_hat": {"median_of_median_widths": float(np.median(surv_med_widths)),
                                 "mean_coverage": float(np.mean(surv_covs)),
                                 "n_cells_coverage_ge_95pct": sum(1 for c in surv_covs if c >= 0.95)},
            "survivor_rF_0": {"median_of_median_widths": float(np.median(surv0_med_widths)),
                              "mean_coverage": float(np.mean(surv0_covs)),
                              "n_cells_coverage_ge_95pct": sum(1 for c in surv0_covs if c >= 0.95)},
            "mean_share_cells_survivor_narrower": float(np.mean(shares_narrower)),
        }
        print(f"\n=== detector={d} ({len(rows)} cells) ===")
        print(f"  naive:        median width={summary_by_detector[d]['naive']['median_of_median_widths']:.4f}  "
              f"mean coverage={summary_by_detector[d]['naive']['mean_coverage']:.3f}")
        print(f"  survivor(rF_hat): median width={summary_by_detector[d]['survivor_rF_hat']['median_of_median_widths']:.4f}  "
              f"mean coverage={summary_by_detector[d]['survivor_rF_hat']['mean_coverage']:.3f}")
        print(f"  survivor(rF=0):   median width={summary_by_detector[d]['survivor_rF_0']['median_of_median_widths']:.4f}  "
              f"mean coverage={summary_by_detector[d]['survivor_rF_0']['mean_coverage']:.3f}")
        print(f"  mean share of cells where survivor(rF_hat) narrower than naive: "
              f"{summary_by_detector[d]['mean_share_cells_survivor_narrower']:.3f}")

    out = {
        "kappa": KAPPA, "delta": DELTA, "rel_H": REL_H, "rho_H_true": RHO_H_TRUE,
        "c_bound": [C_LO, C_HI], "rho_T": RHO_T, "r_F_hat_used": r_F_hat,
        "n": N, "reps": args.reps, "elapsed_seconds": elapsed,
        "cells": results,
        "summary_by_detector": summary_by_detector,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\nWritten to {OUT}")


if __name__ == "__main__":
    main()
