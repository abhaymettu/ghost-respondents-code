"""Task 3 of the H5-detected close-out: Layer A (Gaussian DGP) validation of att_pass.

dgp.py already implements exactly the process (E47)-(E51) assume -- Cell.r_F, the Gaussian
threshold detector on human fluency F = r_F*theta + sqrt(1-r_F^2)*eta with pass iff F > tau,
tau = Phi^-1(1-sp), and machine detection flag ~ Bernoulli(se) INDEPENDENT of theta (A3 by
construction) -- so no separate simulator is needed (per the task brief's fallback clause;
dgp.py/CONVENTIONS.md's "Detector" section is exactly the E32/E33 setup).

For pi in {0.1, 0.3}, c in {0, 0.4, 0.9}, detector="degraded" (se=sp=0.85, DETECTORS dict),
r_F in {0, 0.3}, at rel_H=0.7, kappa=0.2, delta=0.0, rho_T=0.5 (lane1's hand-computed
values, table 3.4/3.5), n=1000, 500 reps:

1. Check the mean survivor correlation (Cor(x, w) on detector survivors) matches
   rho_H * att_pass(...) within Monte Carlo error.
2. Check the Imbens-Manski survivor bound (Fisher-z CI on the survivor correlation at
   n_pass, propagated through att_pass's endpoints at c in [c_bound_lo, c_bound_hi] =
   [0, 0.9], the span of this validation's own c grid) covers the true rho_H at >= 95%,
   when r_F is known (used correctly in att_pass).
3. Report the same coverage when r_F is misspecified as 0 while the true r_F is 0.3.

Run:  lane4-simulation/.venv/bin/python layerA_validate.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from dgp import Cell, rep_rng, simulate
from estimators import _fisher_ci, _pearson
from h5_bounds_detected import att_pass

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "h5-bounds-detected" / "layerA_validation.json"

REL_H, KAPPA, DELTA, RHO_T = 0.7, 0.2, 0.0, 0.5
RHO_H_TRUE = float(np.sqrt(REL_H) * RHO_T)
N, REPS, MASTER_SEED = 1000, 500, 20260927001
SE_DEGRADED, SP_DEGRADED = 0.85, 0.85
C_BOUND_LO, C_BOUND_HI = 0.0, 0.9
PI_LEVELS = (0.1, 0.3)
C_LEVELS = (0.0, 0.4, 0.9)
R_F_LEVELS = (0.0, 0.3)


def covers(ci: tuple[float, float] | None, att_lo: float, att_hi: float, rho_true: float) -> bool:
    if ci is None:
        return False
    ci_lo, ci_hi = ci
    ep = (ci_lo / att_hi, ci_hi / att_lo)
    lo, hi = min(ep), max(ep)
    return bool(lo <= rho_true <= hi)


def run_cell(pi: float, c: float, r_F: float) -> dict:
    cell = Cell(pi=pi, c=c, n=N, detector="degraded", kappa=KAPPA, rel_H=REL_H,
                delta=DELTA, rho_T=RHO_T, r_F=r_F, k=1)
    att_pass_true = att_pass(pi, c, REL_H, KAPPA, DELTA, RHO_T, r_F, SE_DEGRADED, SP_DEGRADED)
    rho_pass_pred = RHO_H_TRUE * att_pass_true

    att_hi_known = att_pass(pi, C_BOUND_HI, REL_H, KAPPA, DELTA, RHO_T, r_F,
                             SE_DEGRADED, SP_DEGRADED)
    att_lo_known = att_pass(pi, C_BOUND_LO, REL_H, KAPPA, DELTA, RHO_T, r_F,
                             SE_DEGRADED, SP_DEGRADED)
    att_hi_mis = att_pass(pi, C_BOUND_HI, REL_H, KAPPA, DELTA, RHO_T, 0.0,
                           SE_DEGRADED, SP_DEGRADED)
    att_lo_mis = att_pass(pi, C_BOUND_LO, REL_H, KAPPA, DELTA, RHO_T, 0.0,
                           SE_DEGRADED, SP_DEGRADED)

    survivor_corrs = []
    n_pass_list = []
    covered_known = []
    covered_misspec = []  # only meaningful when r_F == 0.3 (misspecify as 0)
    for rep in range(REPS):
        rng = rep_rng(MASTER_SEED, cell, rep)
        s = simulate(cell, rng)
        passed = s.passed
        n_pass = int(passed.sum())
        n_pass_list.append(n_pass)
        r_hat = _pearson(s.x[passed], s.w[passed])
        survivor_corrs.append(r_hat)

        ci = _fisher_ci(r_hat, n_pass)
        covered_known.append(covers(ci, att_lo_known, att_hi_known, RHO_H_TRUE))
        covered_misspec.append(covers(ci, att_lo_mis, att_hi_mis, RHO_H_TRUE))

    survivor_corrs = np.array(survivor_corrs)
    mean_corr = float(np.nanmean(survivor_corrs))
    mcse = float(np.nanstd(survivor_corrs, ddof=1) / np.sqrt(np.sum(np.isfinite(survivor_corrs))))
    diff = mean_corr - rho_pass_pred
    return {
        "pi": pi, "c": c, "r_F": r_F,
        "att_pass_true": att_pass_true,
        "rho_pass_predicted": rho_pass_pred,
        "rho_pass_mc_mean": mean_corr,
        "rho_pass_mcse": mcse,
        "diff_mc_minus_predicted": diff,
        "diff_in_mcse_units": diff / mcse if mcse > 0 else float("nan"),
        "mean_n_pass": float(np.mean(n_pass_list)),
        "coverage_r_F_known": float(np.mean(covered_known)),
        "coverage_r_F_misspecified_as_0": float(np.mean(covered_misspec)) if r_F != 0.0 else None,
        "n_reps": REPS,
    }


def main() -> None:
    results = []
    for pi in PI_LEVELS:
        for c in C_LEVELS:
            for r_F in R_F_LEVELS:
                res = run_cell(pi, c, r_F)
                results.append(res)
                print(f"pi={pi} c={c} r_F={r_F}: predicted={res['rho_pass_predicted']:.4f} "
                      f"MC_mean={res['rho_pass_mc_mean']:.4f} "
                      f"diff={res['diff_mc_minus_predicted']:+.4f} "
                      f"({res['diff_in_mcse_units']:+.2f} MCSE)  "
                      f"cover(known)={res['coverage_r_F_known']:.3f}  "
                      f"cover(misspec r_F=0)="
                      f"{res['coverage_r_F_misspecified_as_0']}")

    n_ok_2mcse = sum(1 for r in results if abs(r["diff_in_mcse_units"]) < 2.0)
    known_covs = [r["coverage_r_F_known"] for r in results]
    misspec_covs = [r["coverage_r_F_misspecified_as_0"] for r in results
                    if r["coverage_r_F_misspecified_as_0"] is not None]
    summary = {
        "rel_H": REL_H, "kappa": KAPPA, "delta": DELTA, "rho_T": RHO_T, "rho_H_true": RHO_H_TRUE,
        "n": N, "reps": REPS, "detector": "degraded", "se": SE_DEGRADED, "sp": SP_DEGRADED,
        "c_bound": [C_BOUND_LO, C_BOUND_HI],
        "cells": results,
        "n_cells_matching_within_2mcse": n_ok_2mcse,
        "n_cells": len(results),
        "coverage_known_r_F": {"min": min(known_covs), "mean": float(np.mean(known_covs)),
                                "n_cells_ge_95pct": sum(1 for x in known_covs if x >= 0.95)},
        "coverage_misspecified_r_F": {
            "min": min(misspec_covs), "mean": float(np.mean(misspec_covs)),
            "n_cells_ge_95pct": sum(1 for x in misspec_covs if x >= 0.95),
            "n_cells": len(misspec_covs),
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2) + "\n")
    print()
    print(f"{n_ok_2mcse}/{len(results)} cells: MC mean survivor corr within 2 MCSE of "
          f"rho_H * att_pass")
    print(f"coverage (r_F known): min={min(known_covs):.3f} mean={np.mean(known_covs):.3f} "
          f">=95%: {summary['coverage_known_r_F']['n_cells_ge_95pct']}/{len(known_covs)}")
    print(f"coverage (r_F misspecified as 0, true r_F=0.3): min={min(misspec_covs):.3f} "
          f"mean={np.mean(misspec_covs):.3f} >=95%: "
          f"{summary['coverage_misspecified_r_F']['n_cells_ge_95pct']}/{len(misspec_covs)}")
    print(f"\nWritten to {OUT}")


if __name__ == "__main__":
    main()
