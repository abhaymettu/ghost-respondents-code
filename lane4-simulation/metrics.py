"""Per-cell Monte Carlo summaries and pre-registered success thresholds (SPEC 4.4).

`summarize(cell, fits, truth)` turns `reps` replications' worth of `Fit` objects (from
estimators.py, ESTIMATORS mapping) into one self-contained dict per cell: per-estimator
bias/RMSE/coverage/CI-width for both rho_H and rho_T (N2 is unresolved, so both targets are
computed, never just one), plus pi_hat and loading_hat diagnostics, plus the empirical
between-item correlation against population.py's r_obs (E26, H2), plus the full
population_moments(cell) dict inlined under "population" so verification pass 2 (SPEC
section 7) can check every closed form against this one row.

`success_flags(summary)` evaluates SPEC 4.4's four pre-registered thresholds. A flag is
`None` (never `False`) in any cell/estimator/target where SPEC's applicability condition does
not hold -- e.g. corrected_bias_ok is only defined for pi <= 0.20 and c <= C_PARTIAL.

OPERATIONALIZATION NEEDING ABHAY'S SIGN-OFF: SPEC 4.3 names coupling levels
{0, partial, high} without numbers; lane 4 operationalizes partial = 0.4, high = 0.9
(see grid.py's C_PARTIAL/C_HIGH). This module's C_PARTIAL = 0.5 is a different quantity:
SPEC 4.4's applicability CUTOFF for "corrected_bias_ok" ("c <= partial"). It is deliberately
NOT equal to grid.py's C_PARTIAL = 0.4 grid level -- it sits strictly between the 0.4 and 0.9
grid points so c=0.4 is unambiguously inside the applicable region and c=0.9 unambiguously
outside. Both constants need Abhay's sign-off before the full grid ships, and if "partial"
moves off 0.4 then both must move together.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from population import population_moments

# SPEC 4.4: "corrected bias at most 20% of naive bias in every cell with pi <= 0.20 and
# c <= partial". SPEC 4.3 does not give partial a number. Lane 4's operationalization,
# pending Abhay's sign-off (see module docstring and grid.py's C_PARTIAL/C_HIGH):
C_PARTIAL = 0.5

TARGETS = ("rho_H", "rho_T")
CORRECTION_ESTIMATORS_EXCLUDE_FROM_BIAS_CHECK = ("naive",)


def _nan_or(value: float, default: float = float("nan")) -> float:
    return default if value is None else value


def _target_metrics(
    estimates: np.ndarray,
    converged: np.ndarray,
    cis: list[tuple[float, float] | None],
    truth_value: float,
) -> dict[str, Any]:
    """Bias/RMSE/coverage/CI-width for one estimator x one target, over `reps` replications."""
    n_reps = len(estimates)
    ok = converged & ~np.isnan(estimates)
    n_converged = int(ok.sum())
    out: dict[str, Any] = {
        "n_reps": n_reps,
        "n_converged": n_converged,
        "failure_rate": 1.0 - n_converged / n_reps if n_reps else float("nan"),
    }
    if n_converged == 0:
        out.update(
            bias=float("nan"), rel_bias=float("nan"), rmse=float("nan"), mcse=float("nan"),
            coverage=float("nan"), coverage_se=float("nan"), ci_width=float("nan"),
        )
        return out

    est_ok = estimates[ok]
    bias = float(np.mean(est_ok) - truth_value)
    rel_bias = bias / truth_value if truth_value != 0 else float("nan")
    rmse = float(np.sqrt(np.mean((est_ok - truth_value) ** 2)))
    sd = float(np.std(est_ok, ddof=1)) if n_converged > 1 else float("nan")
    mcse = sd / math.sqrt(n_converged) if n_converged > 1 else float("nan")

    widths = []
    hits = []
    for is_ok, ci in zip(ok, cis):
        if not is_ok or ci is None:
            continue
        lo, hi = ci
        if lo is None or hi is None or math.isnan(lo) or math.isnan(hi):
            continue
        widths.append(hi - lo)
        hits.append(lo <= truth_value <= hi)
    if hits:
        n_ci = len(hits)
        coverage = float(np.mean(hits))
        coverage_se = math.sqrt(coverage * (1.0 - coverage) / n_ci)
        ci_width = float(np.mean(widths))
    else:
        coverage = float("nan")
        coverage_se = float("nan")
        ci_width = float("nan")

    out.update(bias=bias, rel_bias=rel_bias, rmse=rmse, mcse=mcse,
                coverage=coverage, coverage_se=coverage_se, ci_width=ci_width)
    return out


def summarize(cell, fits: list[dict[str, Any]], truth: dict) -> dict:
    """Summarize `reps` replications of {estimator_name: Fit} into one self-contained dict.

    `truth` carries the per-cell quantities metrics are scored against and anything else
    computed outside the estimator loop that summarize needs but Fit does not carry:
      - rho_H, rho_T, pi, loading   (scalars; the truth every estimator is scored against)
      - r_obs_emp                   (list[float], one empirical mean between-item correlation
                                      per rep, computed by grid.py's run_cell from Sample.X;
                                      Fit does not carry raw-sample statistics, so this is the
                                      channel for H2's between-item metric, per E26)
    """
    n_reps = len(fits)
    estimator_names = sorted({name for rep_fits in fits for name in rep_fits})

    estimators_out: dict[str, Any] = {}
    for name in estimator_names:
        rep_fits = [rep.get(name) for rep in fits]
        converged = np.array([bool(f is not None and f.converged) for f in rep_fits])

        per_target: dict[str, Any] = {}
        for target in TARGETS:
            attr = f"{target}_hat"
            ci_attr = "ci_H" if target == "rho_H" else "ci_T"
            estimates = np.array(
                [float(getattr(f, attr)) if f is not None else float("nan") for f in rep_fits]
            )
            cis = [getattr(f, ci_attr) if f is not None else None for f in rep_fits]
            per_target[target] = _target_metrics(estimates, converged, cis, truth[target])

        pi_hats = [f.pi_hat for f in rep_fits if f is not None and f.converged and f.pi_hat is not None]
        if pi_hats:
            errs = np.abs(np.array(pi_hats) - truth["pi"])
            pi_abs_err = {
                "value": float(np.mean(errs)),
                "mcse": float(np.std(errs, ddof=1) / math.sqrt(len(errs))) if len(errs) > 1 else float("nan"),
                "n": len(errs),
            }
        else:
            pi_abs_err = None

        loading_hats = [
            f.loading_hat for f in rep_fits if f is not None and f.converged and f.loading_hat is not None
        ]
        loading_bias = float(np.mean(loading_hats) - truth["loading"]) if loading_hats else None

        estimators_out[name] = {
            **per_target,
            "pi_abs_err": pi_abs_err,
            "loading_bias": loading_bias,
            "n_converged": int(converged.sum()),
            "n_reps": n_reps,
            "failure_rate": 1.0 - float(converged.sum()) / n_reps if n_reps else float("nan"),
        }

    r_obs_emp_reps = truth.get("r_obs_emp") or []
    pop = population_moments(cell)
    if r_obs_emp_reps:
        arr = np.array(r_obs_emp_reps, dtype=float)
        arr = arr[~np.isnan(arr)]
        r_obs_summary = {
            "mean": float(np.mean(arr)) if len(arr) else float("nan"),
            "mcse": float(np.std(arr, ddof=1) / math.sqrt(len(arr))) if len(arr) > 1 else float("nan"),
            "population_r_obs": pop["r_obs"],
            "n": int(len(arr)),
        }
    else:
        r_obs_summary = {"mean": float("nan"), "mcse": float("nan"), "population_r_obs": pop["r_obs"], "n": 0}

    return {
        "cell_id": cell.cell_id,
        "cell": {
            "pi": cell.pi, "c": cell.c, "n": cell.n, "detector": cell.detector,
            "kappa": cell.kappa, "rho_v": cell.rho_v, "rel_H": cell.rel_H, "delta": cell.delta,
            "rho_T": cell.rho_T, "k": cell.k, "r_F": cell.r_F, "d_theta": cell.d_theta,
            "arm": cell.arm,
        },
        "n_reps": n_reps,
        "estimators": estimators_out,
        "r_obs_emp": r_obs_summary,
        "population": pop,
    }


def success_flags(summary: dict) -> dict[str, Any]:
    """SPEC 4.4's four pre-registered thresholds, evaluated per estimator (and per target
    where SPEC gives a target-specific quantity). A flag is None, never False, wherever
    SPEC's applicability condition does not hold for this cell/estimator.
    """
    cell = summary["cell"]
    ests = summary["estimators"]
    naive = ests.get("naive")
    delete = ests.get("delete")
    detector = cell["detector"]

    applicable_bias_cell = cell["pi"] <= 0.20 and cell["c"] <= C_PARTIAL

    flags: dict[str, Any] = {
        "corrected_bias_ok": {},
        "coverage_ok": {},
        "pi_err_ok": {},
        "beats_deletion": {},
    }

    for name, est in ests.items():
        if name == "naive":
            continue
        flags["corrected_bias_ok"][name] = {}
        for target in TARGETS:
            if not applicable_bias_cell or naive is None:
                flags["corrected_bias_ok"][name][target] = None
                continue
            corr_bias = est[target]["bias"]
            naive_bias = naive[target]["bias"]
            if math.isnan(corr_bias) or math.isnan(naive_bias) or naive_bias == 0:
                flags["corrected_bias_ok"][name][target] = None
            else:
                flags["corrected_bias_ok"][name][target] = abs(corr_bias) <= 0.20 * abs(naive_bias)

    for name, est in ests.items():
        flags["coverage_ok"][name] = {}
        for target in TARGETS:
            cov = est[target]["coverage"]
            flags["coverage_ok"][name][target] = None if math.isnan(cov) else (0.92 <= cov <= 0.98)

    for name, est in ests.items():
        pae = est.get("pi_abs_err")
        if cell["n"] != 1000 or pae is None:
            flags["pi_err_ok"][name] = None
        else:
            flags["pi_err_ok"][name] = pae["value"] <= 0.02

    for name, est in ests.items():
        if name in ("naive", "delete"):
            continue
        flags["beats_deletion"][name] = {}
        for target in TARGETS:
            if detector not in ("calibrated", "degraded") or delete is None:
                flags["beats_deletion"][name][target] = None
                continue
            rmse_corr = est[target]["rmse"]
            rmse_delete = delete[target]["rmse"]
            if math.isnan(rmse_corr) or math.isnan(rmse_delete):
                flags["beats_deletion"][name][target] = None
            else:
                flags["beats_deletion"][name][target] = rmse_corr < rmse_delete

    return flags
