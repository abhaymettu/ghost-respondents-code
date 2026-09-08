"""Grid construction and the parallel Layer A runner (SPEC 4.3, 6; CONVENTIONS.md).

OPERATIONALIZATION NEEDING ABHAY'S SIGN-OFF: SPEC 4.3 names coupling levels
{0, partial, high} without numbers. Lane 4 operationalizes:
    C_ZERO = 0.0, C_PARTIAL = 0.4, C_HIGH = 0.9
metrics.py's C_PARTIAL (the applicability cutoff for corrected_bias_ok, "c <= partial") is
set to 0.5, deliberately not identical to this module's C_PARTIAL = 0.4 grid level -- SPEC 4.4
says "c <= partial" as an applicability *region*, and 0.5 was chosen there as a cutoff strictly
above the c = 0.4 grid point so that grid point is always inside the applicable region even
under Monte Carlo float jitter, while c = 0.9 stays outside it. Both numbers need Abhay's
sign-off before the full grid ships; if he sets partial != 0.4, update both this file and
metrics.py's C_PARTIAL together.

`kappa_arm()`, `rho_v_arm()`, `nonignorable_arm()` are reduced slices (documented on each
function) so the full arm set stays affordable (SPEC 6's ~108k-fit / ~60-core-hour budget is
for the base grid alone). Cells that numerically coincide with the base grid's reference
values (kappa = 0.5, rho_v = 0.0) are tagged arm = "base" rather than the arm that generated
them, so `full_grid`'s dedup-by-cell_id (cell_id hashes every Cell field, arm included --
CONVENTIONS.md) actually collapses them instead of silently re-running the same cell twice
under two different arm labels.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from dataclasses import asdict
from functools import partial
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from dgp import Cell, rep_rng, simulate
from metrics import success_flags, summarize

# SPEC 4.3 coupling levels {0, partial, high}; see module docstring for the sign-off note.
C_ZERO = 0.0
C_PARTIAL = 0.4
C_HIGH = 0.9

PI_LEVELS = (0.01, 0.02, 0.05, 0.10, 0.20, 0.30)
C_LEVELS = (C_ZERO, C_PARTIAL, C_HIGH)
N_LEVELS = (500, 1000, 5000)
DETECTOR_LEVELS = ("none", "calibrated", "degraded", "oracle")
KAPPA_REFERENCE = 0.5

# Measured at the pilot cell (pi=0.10, c=0, n=1000, kappa=0.5, detector="oracle", seed
# 20260907, 2026-09-07; see PILOT.md section (e)), superseding SPEC 6's "~2s average per
# fit" placeholder. Used by --dry-run / --cells-only; run_pilot.py's own per-run timings
# supersede these again for any cost table it writes.
#
# CAVEAT: measured at n=1000 only. EM and labelfree cost grows with n, and the grid runs
# n up to its largest level, so cost estimates for larger-n cells are optimistic. The
# extrapolation assumes per-fit cost is independent of cell parameters, which is untested.
DEFAULT_SECONDS_PER_FIT = {
    "naive": 0.0001,
    "delete": 0.0001,
    "simex": 0.0084,
    "labelfree": 0.2841,
    "em": 1.3461,
}


def base_grid() -> list[Cell]:
    """SPEC 4.3's cross at the reference kappa = 0.5, rho_v = 0. 6*3*3*4 = 216 cells."""
    cells = []
    for pi in PI_LEVELS:
        for c in C_LEVELS:
            for n in N_LEVELS:
                for detector in DETECTOR_LEVELS:
                    cells.append(
                        Cell(pi=pi, c=c, n=n, detector=detector, kappa=KAPPA_REFERENCE,
                             rho_v=0.0, arm="base")
                    )
    return cells


def kappa_arm() -> list[Cell]:
    """N3's extension: kappa in {0.2, 0.5, 1.0}, reduced to n = 1000 (all pi, c, detector).

    kappa = 0.5 cells duplicate the n=1000 slice of base_grid() exactly, so they are tagged
    arm="base" (see module docstring) and full_grid() dedups them away. 3*6*3*4 = 216 cells
    total, 72 of which collapse into base at kappa=0.5, leaving 144 new cells.
    """
    cells = []
    for kappa in (0.2, 0.5, 1.0):
        arm = "base" if kappa == KAPPA_REFERENCE else "kappa"
        for pi in PI_LEVELS:
            for c in C_LEVELS:
                for detector in DETECTOR_LEVELS:
                    cells.append(
                        Cell(pi=pi, c=c, n=1000, detector=detector, kappa=kappa,
                             rho_v=0.0, arm=arm)
                    )
    return cells


def rho_v_arm() -> list[Cell]:
    """Q7's extension: rho_v in {0.0, 0.5}. rho_v only enters the between-item metrics (E24,
    E26), so it is reduced further than kappa_arm: n = 1000, c in {C_ZERO, C_PARTIAL} only
    (at c = C_HIGH, r_M = c^2 + rho_v(1-c^2) is already close to 1 regardless of rho_v, so the
    high-c cell is not informative about rho_v), detector = "calibrated" only (a single
    representative operating point; rho_v does not interact with the detector mechanism).
    rho_v = 0.0 cells duplicate base_grid() at those (pi, c, detector) points and are tagged
    arm="base". 2 rho_v * 6 pi * 2 c = 24 cells, 12 of which collapse into base, leaving 12 new.
    """
    cells = []
    for rho_v in (0.0, 0.5):
        arm = "base" if rho_v == 0.0 else "rho_v"
        for pi in PI_LEVELS:
            for c in (C_ZERO, C_PARTIAL):
                cells.append(
                    Cell(pi=pi, c=c, n=1000, detector="calibrated", kappa=KAPPA_REFERENCE,
                         rho_v=rho_v, arm=arm)
                )
    return cells


def nonignorable_arm() -> list[Cell]:
    """OPTIONAL, pending Abhay's Q5 call (derivations/lane1-open-questions.md).

    d_theta in {0.0, 0.5, 1.0} (A1' trait-mean shift of machine users). Per Q5, a sign flip
    on the SPEC grid needs the between-mean term active, which needs delta != 0 (att_nonignorable,
    E21, multiplies delta * d_theta); this arm therefore overrides delta = 0.3 (a modest mean
    gap) rather than the Cell default delta = 0.0, so it never numerically coincides with the
    base grid and every cell is tagged arm="nonignorable". Reduced slice, per Q5's own finding
    that the effect needs high pi: n = 1000, pi in {0.10, 0.20, 0.30}, c = C_ZERO,
    detector = "none" (deletion-selection is a separate mechanism, held off here).
    3 pi * 3 d_theta = 9 cells. Do NOT include in full_grid()'s default arms without Abhay's
    sign-off on whether this arm ships at all.
    """
    cells = []
    for pi in (0.10, 0.20, 0.30):
        for d_theta in (0.0, 0.5, 1.0):
            cells.append(
                Cell(pi=pi, c=C_ZERO, n=1000, detector="none", kappa=KAPPA_REFERENCE,
                     rho_v=0.0, delta=0.3, d_theta=d_theta, arm="nonignorable")
            )
    return cells


ARM_BUILDERS = {
    "base": base_grid,
    "kappa": kappa_arm,
    "rho_v": rho_v_arm,
    "nonignorable": nonignorable_arm,
}


def full_grid(arms: tuple[str, ...] = ("base",)) -> list[Cell]:
    """Assemble and deduplicate cells across `arms` by cell.cell_id (first-arm-wins order)."""
    seen: dict[str, Cell] = {}
    for name in arms:
        if name not in ARM_BUILDERS:
            raise ValueError(f"unknown arm {name!r}; known arms: {sorted(ARM_BUILDERS)}")
        for cell in ARM_BUILDERS[name]():
            seen.setdefault(cell.cell_id, cell)
    return list(seen.values())


def _to_jsonable(obj):
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(v) for v in obj]
    if isinstance(obj, (np.floating,)):
        v = float(obj)
        return None if math.isnan(v) else v
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, float) and math.isnan(obj):
        return None
    return obj


def run_cell(cell: Cell, reps: int, master_seed: int, estimator_opts: dict | None = None) -> dict:
    """Simulate `reps` replications of `cell`, fit every estimator, summarize, return one
    JSON-serializable dict. Records wall-clock per estimator per rep (mean, total) -- the
    core-hour extrapolation (estimate_cost, run_pilot.py) depends on these numbers, not on
    whatever Fit.seconds an estimator self-reports.
    """
    from estimators import ESTIMATORS  # deferred: --dry-run / --cells-only need no estimators

    estimator_opts = estimator_opts or {}
    fits_per_rep: list[dict] = []
    seconds_by_estimator: dict[str, list[float]] = {name: [] for name in ESTIMATORS}
    # Fit.seconds_resample: the share of a fit spent in resampling (EM's parametric
    # bootstrap, SIMEX's remeasurement Monte Carlo) rather than the point estimate. Kept
    # separate because it is the part the grid can buy back by lowering B/B_boot.
    resample_by_estimator: dict[str, list[float]] = {name: [] for name in ESTIMATORS}
    r_obs_emp_reps: list[float] = []

    se, sp = cell.se_sp
    # fit_simex and fit_labelfree take required args (se/sp; labelfree's machine_ref) that
    # are cell/rng-derived, not fixed config -- estimator_opts (caller-supplied) can override
    # any of these per name, but these are the defaults every rep gets. machine_ref stands in
    # for "a reference corpus of known-machine text" (SPEC 3.2): its mean/variance are all
    # fit_labelfree uses, and the true marginal machine-item distribution N(mu_M, s2_M) is
    # exactly that reference in Layer A's parametric world.
    MACHINE_REF_N = 2000

    for rep in range(reps):
        rng = rep_rng(master_seed, cell, rep)
        sample = simulate(cell, rng)

        k = sample.X.shape[1]
        if k > 1:
            corr = np.corrcoef(sample.X, rowvar=False)
            iu = np.triu_indices(k, k=1)
            r_obs_emp_reps.append(float(np.mean(corr[iu])))
        else:
            r_obs_emp_reps.append(float("nan"))

        default_opts = {
            "naive": {},
            "delete": {},
            "simex": {"se": se, "sp": sp, "rng": np.random.default_rng(rng.integers(0, 2**31 - 1))},
            "labelfree": {
                "se": se, "sp": sp,
                "machine_ref": rng.normal(cell.mu_M, np.sqrt(max(cell.s2_M, 1e-12)), size=MACHINE_REF_N),
                # A known-HUMAN reference corpus (pre-LLM archival survey data) is exactly as
                # available as a known-machine one, and SPEC 3.2's distribution matching needs
                # both. Without it fit_labelfree falls back to a GMM surrogate for human_ref,
                # which is degenerate at delta=0 (both classes zero-mean) -- the cause of the
                # ~0.6 labelfree bias seen in the first pilot smoke run.
                "human_ref": rng.normal(0.0, np.sqrt(max(cell.V_H, 1e-12)), size=MACHINE_REF_N),
                # The researcher does not know c; 0 is the working assumption. Misspecification
                # at c > 0 is a result to measure, not a bug -- stated explicitly, not defaulted.
                "c_known": 0.0,
                "rng": np.random.default_rng(rng.integers(0, 2**31 - 1)),
            },
            "em": {"rng": np.random.default_rng(rng.integers(0, 2**31 - 1))},
        }

        rep_fits: dict = {}
        for name, fit_fn in ESTIMATORS.items():
            opts = {**default_opts.get(name, {}), **estimator_opts.get(name, {})}
            t0 = time.perf_counter()
            fit = fit_fn(sample, **opts)
            elapsed = time.perf_counter() - t0
            seconds_by_estimator[name].append(elapsed)
            if getattr(fit, "seconds_resample", None) is not None:
                resample_by_estimator[name].append(float(fit.seconds_resample))
            rep_fits[name] = fit
        fits_per_rep.append(rep_fits)

    truth = {
        "rho_H": cell.rho_H, "rho_T": cell.rho_T, "pi": cell.pi, "loading": cell.loading,
        "r_obs_emp": r_obs_emp_reps,
    }
    summary = summarize(cell, fits_per_rep, truth)
    flags = success_flags(summary)

    timing = {}
    for name, secs in seconds_by_estimator.items():
        res = resample_by_estimator[name]
        mean_total = float(np.mean(secs)) if secs else float("nan")
        mean_res = float(np.mean(res)) if res else None
        timing[name] = {
            "mean_seconds": mean_total,
            "total_seconds": float(np.sum(secs)) if secs else 0.0,
            "n": len(secs),
            # None (not 0.0) for estimators that do no resampling, so "does not resample"
            # is distinguishable from "resamples, but immeasurably fast".
            "mean_seconds_resample": mean_res,
            "resample_share": (mean_res / mean_total) if (mean_res and mean_total) else None,
        }

    result = {
        "cell_id": cell.cell_id,
        "cell": asdict(cell),
        "reps": reps,
        "master_seed": master_seed,
        "summary": summary,
        "success_flags": flags,
        "timing": timing,
    }
    return _to_jsonable(result)


def _parse_shard(shard: str | None, n_cells: int) -> tuple[int, int] | None:
    if shard is None:
        return None
    i_str, n_str = shard.split("/")
    i, n = int(i_str), int(n_str)
    if not (0 <= i < n):
        raise ValueError(f"shard index {i} out of range for n={n}")
    return i, n


def run_grid(
    cells: list[Cell],
    reps: int,
    master_seed: int,
    n_workers: int,
    out_dir: str,
    shard: str | None = None,
    estimator_opts: dict | None = None,
) -> str:
    """multiprocessing.Pool over cells (SPEC 6: fits are embarrassingly parallel, shard by
    cell). Writes one JSONL line per cell to `out_dir/grid.jsonl`, appending. Resumable: a
    cell whose cell_id already has a line in that file is skipped. shard="i/n" selects the
    cells whose position (in cell_id-sorted order, for determinism independent of caller
    ordering) mod n == i.
    """
    cells = sorted(cells, key=lambda c: c.cell_id)

    parsed = _parse_shard(shard, len(cells))
    if parsed is not None:
        i, n = parsed
        cells = [c for idx, c in enumerate(cells) if idx % n == i]

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    jsonl_path = out_path / "grid.jsonl"

    seen: set[str] = set()
    if jsonl_path.exists():
        with open(jsonl_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    seen.add(json.loads(line)["cell_id"])
                except (json.JSONDecodeError, KeyError):
                    continue

    todo = [c for c in cells if c.cell_id not in seen]
    already_done = len(cells) - len(todo)
    print(f"run_grid: {len(cells)} cells selected, {already_done} already done, {len(todo)} to run")

    if not todo:
        return str(jsonl_path)

    worker = partial(run_cell, reps=reps, master_seed=master_seed, estimator_opts=estimator_opts)
    with open(jsonl_path, "a") as out_f:
        with Pool(n_workers) as pool:
            for i, result in enumerate(pool.imap_unordered(worker, todo)):
                out_f.write(json.dumps(result) + "\n")
                out_f.flush()
                print(f"run_grid: {i + 1}/{len(todo)} cells done (cell_id={result['cell_id']})")

    return str(jsonl_path)


def estimate_cost(
    cells: list[Cell],
    reps: int,
    seconds_per_fit_by_estimator: dict[str, float],
    n_workers: int | None = None,
) -> dict:
    """Dry-run core-hour estimate: no simulation runs. SPEC 6 budgets ~108k fits at ~2s
    average for the base grid alone (~60 core-hours); this reproduces the real number for
    whatever `cells` it is handed.
    """
    n_workers = n_workers or (os.cpu_count() or 1)
    n_cells = len(cells)
    n_estimators = len(seconds_per_fit_by_estimator)
    total_fits = n_cells * reps * n_estimators

    core_hours_by_estimator = {
        name: n_cells * reps * seconds / 3600.0
        for name, seconds in seconds_per_fit_by_estimator.items()
    }
    total_core_hours = sum(core_hours_by_estimator.values())

    return {
        "n_cells": n_cells,
        "n_reps": reps,
        "n_estimators": n_estimators,
        "total_fits": total_fits,
        "core_hours_by_estimator": core_hours_by_estimator,
        "total_core_hours": total_core_hours,
        "n_workers": n_workers,
        "wall_clock_hours": total_core_hours / n_workers,
    }


def _print_cost_table(cost: dict) -> None:
    print(f"cells               : {cost['n_cells']}")
    print(f"reps                : {cost['n_reps']}")
    print(f"estimators          : {cost['n_estimators']}")
    print(f"total fits          : {cost['total_fits']}")
    for name, hours in cost["core_hours_by_estimator"].items():
        print(f"  core-hours[{name:10s}] = {hours:.2f}")
    print(f"total core-hours    : {cost['total_core_hours']:.2f}")
    print(f"n_workers           : {cost['n_workers']}")
    print(f"wall-clock hours    : {cost['wall_clock_hours']:.2f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Lane 4 grid construction and runner.")
    parser.add_argument("--arms", default="base", help="comma-separated arm names")
    parser.add_argument("--reps", type=int, default=500, help="SPEC 4.1 default")
    parser.add_argument("--seed", type=int, default=20260907, help="master seed")
    parser.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    parser.add_argument("--out", default="results")
    parser.add_argument("--shard", default=None, help='e.g. "0/4"')
    parser.add_argument("--dry-run", action="store_true", help="print cost table and cell count only")
    parser.add_argument("--cells-only", action="store_true", help="print the cell list only")
    args = parser.parse_args()

    arms = tuple(a.strip() for a in args.arms.split(",") if a.strip())
    cells = full_grid(arms)

    if args.cells_only:
        for c in sorted(cells, key=lambda c: c.cell_id):
            print(json.dumps(_to_jsonable(asdict(c)) | {"cell_id": c.cell_id}))
        print(f"# {len(cells)} cells total across arms {arms}")
        return

    if args.dry_run:
        cost = estimate_cost(cells, args.reps, DEFAULT_SECONDS_PER_FIT, n_workers=args.workers)
        print(f"arms: {arms}")
        _print_cost_table(cost)
        print("(seconds-per-fit measured at the pilot cell, n=1000 only; larger-n cells cost")
        print(" more, so these totals are optimistic. See PILOT.md section (e).)")
        return

    run_grid(cells, args.reps, args.seed, args.workers, args.out, shard=args.shard)


if __name__ == "__main__":
    main()
