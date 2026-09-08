"""Launch the full Layer A grid: frozen config, sharded by cell across cores, resumable.

Writes GRID-CONFIG.md BEFORE the first cell starts and refuses to run if an existing
config disagrees with the one this script would write -- a post-start config change means
a logged rerun, not a silent continuation (see GRID-CONFIG.md "Rerun policy").

Outputs under results/grid/:
  grid.jsonl            one appended line per completed cell (resume index)
  cells/<cell_id>.json  per-cell manifest: result + provenance + wall clock
and GRID-PROGRESS.md at the package root, refreshed every ~30 min.

CPU only. No network, no API calls.
"""

from __future__ import annotations

# Must precede numpy/sklearn import: with N_WORKERS processes, a multithreaded BLAS
# oversubscribes the machine badly (10 workers x 8 BLAS threads on 12 cores). One thread
# per worker keeps the "leave 2 cores free" promise honest.
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import hashlib
import json
import platform
import sys
import time
from dataclasses import asdict
from datetime import datetime, timedelta
from functools import partial
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import scipy
import sklearn

from dgp import Cell
from grid import full_grid, run_cell

# ---------------------------------------------------------------- frozen configuration
GRID_MASTER_SEED = 20260907
REPS = 500
ARMS = ("base", "kappa", "rho_v")
CORES_LEFT_FREE = 2
NICE_LEVEL = 10
PROGRESS_INTERVAL_S = 30 * 60
DIVERGENCE_THRESHOLD = 0.25

# Measured 2026-09-07 on this machine, 2 reps per n at (pi=0.10, c=0.4, detector=calibrated,
# kappa=0.5). Seconds per REP (all five estimators). The pilot (PILOT.md section (e)) measured
# n=1000 only; these are what the ETA and the divergence check are scored against.
PILOT_SECONDS_PER_REP_BY_N = {500: 1.051, 1000: 1.323, 5000: 6.360}


def expected_seconds(cell: Cell) -> float:
    """Predicted wall seconds for one cell (REPS reps), from the measured n-scaling."""
    per_rep = PILOT_SECONDS_PER_REP_BY_N.get(cell.n)
    if per_rep is None:  # n level not measured: interpolate off the n=1000 anchor
        per_rep = PILOT_SECONDS_PER_REP_BY_N[1000] * (cell.n / 1000.0)
    return per_rep * REPS


def config_fingerprint(cells: list[Cell]) -> str:
    """Hash of everything that would change the numbers. Any drift here means a rerun."""
    payload = json.dumps(
        {
            "master_seed": GRID_MASTER_SEED,
            "reps": REPS,
            "arms": list(ARMS),
            "cell_ids": sorted(c.cell_id for c in cells),
            "estimators": ["naive", "delete", "simex", "labelfree", "em"],
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


# ------------------------------------------------------------------------- config file
def write_config(cells: list[Cell], n_workers: int, path: Path) -> str:
    fp = config_fingerprint(cells)
    by_arm: dict[str, int] = {}
    by_n: dict[int, int] = {}
    for c in cells:
        by_arm[c.arm] = by_arm.get(c.arm, 0) + 1
        by_n[c.n] = by_n.get(c.n, 0) + 1

    total_core_s = sum(expected_seconds(c) for c in cells)
    core_h = total_core_s / 3600.0
    wall_h = core_h / n_workers

    L = []
    L.append("# Layer A full grid - frozen run configuration\n")
    L.append(f"**Config fingerprint: `{fp}`**. Written before the first cell started. ")
    L.append(
        "This file is the authority for the run; `run_grid_full.py` recomputes the "
        "fingerprint at every launch and refuses to start if it disagrees with the value "
        "recorded here.\n"
    )

    L.append("## Reading of the launch brief\n")
    L.append(
        "SPEC 4.3's cross, extended by lane 1's N3 (kappa in {0.2, 0.5, 1.0}) and Q7. Q7 is "
        "read as fixing rho_v = 0 (independent calls) as the DEFAULT level, and the run "
        "additionally carries the 12-cell rho_v = 0.5 sensitivity slice so Q7 is answered "
        "empirically rather than assumed. Those 12 cells cost ~2.2 core-hours out of ~116; "
        "omitting them and later wanting them would force a full logged rerun, which is the "
        "more expensive mistake.\n"
    )
    L.append(
        "The `nonignorable` arm (d_theta, A1' trait-mean shift) is EXCLUDED: it is gated on "
        "Abhay's Q5 call and was not named in the launch brief.\n"
    )

    L.append("## Carried flags from the pass-1 diff report\n")
    L.append(
        "- **(BW1)** The pass-2 numerical check compares closed forms against **population "
        "moments**, not against averaged sample correlations. `population.py` computes each "
        "moment as a pure function of the cell, and `metrics.summarize` inlines the full "
        "`population_moments(cell)` dict into every cell's row, so the check reads the "
        "population value directly rather than reconstructing it from replicate means. Where "
        "an empirical Monte Carlo mean is used, it is used only as the thing being TESTED, "
        "never as the reference.\n"
        "- **(BW3)** The regime story assumes rho_vw = 0 (the machine-noise term is "
        "uncorrelated with the outcome w). Layer A's DGP imposes this: nothing in `dgp.py` "
        "induces a v-w covariance. The rho_v arm varies the between-ITEM correlation of the "
        "machine noise, which is a different parameter and does not relax rho_vw = 0. So "
        "every regime claim from this grid inherits the assumption; it is not tested here.\n"
    )

    L.append("## Frozen parameters\n")
    L.append("| field | value |")
    L.append("|---|---|")
    L.append(f"| master_seed | {GRID_MASTER_SEED} |")
    L.append(f"| reps per cell | {REPS} (SPEC 4.3) |")
    L.append(f"| arms | {', '.join(ARMS)} |")
    L.append(f"| cells (deduplicated) | {len(cells)} |")
    L.append(f"| cells by arm | {', '.join(f'{k}={v}' for k, v in sorted(by_arm.items()))} |")
    L.append(f"| cells by n | {', '.join(f'{k}={v}' for k, v in sorted(by_n.items()))} |")
    L.append("| pi levels | 0.01, 0.02, 0.05, 0.10, 0.20, 0.30 |")
    L.append("| c levels | 0.0, 0.4, 0.9 |")
    L.append("| n levels | 500, 1000, 5000 |")
    L.append("| detector levels | none, calibrated, degraded, oracle |")
    L.append("| kappa levels | 0.2, 0.5, 1.0 (N3; reference 0.5) |")
    L.append("| rho_v levels | 0.0 default (Q7, independent calls), 0.5 sensitivity slice |")
    L.append("| estimators | naive, delete, simex, labelfree, em |")
    L.append(f"| total estimator-fits | {len(cells) * REPS * 5:,} |")
    L.append("")

    L.append("## Seeding\n")
    L.append(
        "Per-(cell, rep) streams via `dgp.rep_rng(master_seed, cell, rep)`, which hashes "
        "`f\"{cell.cell_id}:{rep}\"` with SHA-256. `cell_id` is a hash of the full `Cell` "
        "dataclass including `arm`, so no two grid cells share a stream, and re-running any "
        "single cell reproduces it exactly. Estimator-internal RNGs (SIMEX's remeasurement "
        "draws, EM's bootstrap and multi-start) are spawned from that per-rep stream inside "
        "`grid.run_cell`, so they are frozen by the same seed.\n"
    )

    L.append("## Execution\n")
    L.append("| field | value |")
    L.append("|---|---|")
    L.append(f"| workers | {n_workers} (cpu_count {os.cpu_count()} minus {CORES_LEFT_FREE} left free) |")
    L.append(f"| nice level | {NICE_LEVEL} |")
    L.append("| BLAS threads per worker | 1 (OMP/OPENBLAS/MKL/NUMEXPR/VECLIB pinned) |")
    L.append("| shard unit | one cell (SPEC 6: fits are embarrassingly parallel) |")
    L.append("| resumable | yes, by cell_id present in results/grid/grid.jsonl |")
    L.append(f"| python | {sys.version.split()[0]} |")
    L.append(f"| numpy / scipy / scikit-learn | {np.__version__} / {scipy.__version__} / {sklearn.__version__} |")
    L.append(f"| platform | {platform.platform()} |")
    L.append(f"| started (local) | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |")
    L.append("")

    L.append("## Cost projection\n")
    L.append(
        "Per-rep cost measured on this machine at 2 reps per n, (pi=0.10, c=0.4, "
        "detector=calibrated, kappa=0.5):\n"
    )
    L.append("| n | measured s/rep | cells at this n | projected core-hours |")
    L.append("|---|---|---|---|")
    for n_val in sorted(by_n):
        per_rep = PILOT_SECONDS_PER_REP_BY_N.get(n_val, float("nan"))
        L.append(
            f"| {n_val} | {per_rep:.3f} | {by_n[n_val]} | "
            f"{by_n[n_val] * REPS * per_rep / 3600.0:.1f} |"
        )
    L.append(f"| **total** | | **{len(cells)}** | **{core_h:.1f}** |")
    L.append(f"\nProjected wall clock at {n_workers} workers: **{wall_h:.1f} h**.\n")
    L.append(
        f"**This exceeds SPEC 6's ~60 core-hour budget (~{core_h:.0f} vs ~60), and that is "
        "known at launch rather than discovered mid-run.** The pilot extrapolation in "
        "PILOT.md section (e) measured n=1000 only and projected 87 core-hours for the full "
        "arm set; the n=5000 cells cost 6.36 s/rep against that 1.32 s/rep anchor, which is "
        "where the extra ~29 core-hours come from. EM is the driver (~66% of its own cost is "
        "the parametric bootstrap, and EM is ~95% of grid cost). The run proceeds as "
        "briefed; the lever if it needs to come down later is EM's `B_boot`, which would be "
        "a config change and therefore a logged rerun.\n"
    )

    L.append("## Rerun policy\n")
    L.append(
        "No config change after the first cell starts. If any frozen parameter above changes "
        "-- seed, reps, arms, cell set, estimator list -- the fingerprint changes, this "
        "script refuses to launch against the old results directory, and the run must be "
        "restarted into a fresh directory with the change logged here. Resuming an "
        "interrupted run with an UNCHANGED fingerprint is not a config change and is "
        "expected: completed cells are skipped by cell_id.\n"
    )
    path.write_text("\n".join(L))
    return fp


# ---------------------------------------------------------------------------- progress
def write_progress(path: Path, state: dict) -> None:
    done = state["done"]
    total = state["total"]
    elapsed = time.time() - state["t_start"]
    frac_cost_done = (state["cost_done"] / state["cost_total"]) if state["cost_total"] else 0.0

    L = []
    L.append("# Layer A full grid - progress\n")
    L.append(f"_Updated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (local)._\n")
    status = "COMPLETE" if done >= total else "RUNNING"
    L.append(f"**Status: {status} - {done} / {total} cells done "
             f"({100.0 * done / total:.1f}%).**\n")
    L.append("| field | value |")
    L.append("|---|---|")
    L.append(f"| config fingerprint | `{state['fingerprint']}` |")
    L.append(f"| cells done / total | {done} / {total} |")
    L.append(f"| cells resumed (already done at launch) | {state['resumed']} |")
    L.append(f"| workers | {state['n_workers']} (nice {NICE_LEVEL}) |")
    L.append(f"| elapsed | {timedelta(seconds=int(elapsed))} |")
    if done > state["resumed"] and frac_cost_done > 0:
        remaining_s = elapsed * (1.0 - frac_cost_done) / frac_cost_done
        eta = datetime.now() + timedelta(seconds=int(remaining_s))
        L.append(f"| remaining (cost-weighted) | {timedelta(seconds=int(remaining_s))} |")
        L.append(f"| **ETA** | **{eta.strftime('%Y-%m-%d %H:%M:%S')}** |")
    else:
        L.append("| ETA | not yet estimable (no cell finished since launch) |")
    L.append(f"| core-seconds consumed | {state['core_seconds']:,.0f} |")
    L.append("")
    L.append(
        "ETA is cost-weighted, not cell-count-weighted: n=5000 cells cost ~6x an n=500 cell, "
        "so a raw cells-done percentage would badly misreport the remaining time.\n"
    )

    L.append("## Measured vs. projected per-rep cost\n")
    L.append("| n | projected s/rep | measured s/rep | cells measured | divergence |")
    L.append("|---|---|---|---|---|")
    for n_val in sorted(state["obs_by_n"]):
        obs = state["obs_by_n"][n_val]
        meas = obs["seconds"] / obs["reps"] if obs["reps"] else float("nan")
        proj = PILOT_SECONDS_PER_REP_BY_N.get(n_val, float("nan"))
        div = (meas - proj) / proj if proj else float("nan")
        L.append(f"| {n_val} | {proj:.3f} | {meas:.3f} | {obs['cells']} | {div:+.1%} |")
    L.append("")
    if state["divergences"]:
        L.append(
            f"**Per-fit runtime diverged more than {DIVERGENCE_THRESHOLD:.0%} from the pilot "
            "extrapolation.** Per the launch brief this is recorded and the run continues; "
            "it changes no config and invalidates no result. It affects the ETA and the "
            "core-hour accounting only.\n"
        )
        for d in state["divergences"]:
            L.append(f"- {d}")
        L.append("")
    else:
        L.append(
            f"No per-n divergence beyond {DIVERGENCE_THRESHOLD:.0%} of the pilot "
            "extrapolation so far.\n"
        )

    L.append("## Failures\n")
    if state["failures"]:
        L.append("| cell_id | error |")
        L.append("|---|---|")
        for cid, err in state["failures"]:
            L.append(f"| `{cid}` | {err} |")
        L.append("")
    else:
        L.append("No cell raised. (Per-estimator non-convergence within a cell is a RESULT, "
                 "recorded in each cell's `failure_rate`, not a failure here.)\n")

    L.append("## Outputs\n")
    L.append("- `results/grid/grid.jsonl` - one line per completed cell (resume index)")
    L.append("- `results/grid/cells/<cell_id>.json` - per-cell manifest")
    L.append("- `GRID-CONFIG.md` - frozen configuration\n")
    if done >= total:
        L.append(
            "\n**Grid complete.** Pass 2 (numerical check of every closed-form moment "
            "against this output) may now run; it must not be started on a partial grid.\n"
        )
    path.write_text("\n".join(L))


# -------------------------------------------------------------------------------- main
def main() -> None:
    ap = argparse.ArgumentParser(description="Launch the full Layer A grid.")
    ap.add_argument("--out", default="results/grid")
    ap.add_argument("--workers", type=int, default=None)
    args = ap.parse_args()

    here = Path(__file__).resolve().parent
    out_dir = (here / args.out).resolve()
    cells_dir = out_dir / "cells"
    cells_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = out_dir / "grid.jsonl"
    config_path = here / "GRID-CONFIG.md"
    progress_path = here / "GRID-PROGRESS.md"

    n_workers = args.workers or max(1, (os.cpu_count() or 4) - CORES_LEFT_FREE)
    cells = sorted(full_grid(ARMS), key=lambda c: c.cell_id)
    fp = config_fingerprint(cells)

    # Frozen-config gate: an existing config with a different fingerprint means the run
    # definition changed after the fact. Refuse rather than silently mixing two definitions.
    if config_path.exists():
        prior = config_path.read_text()
        if f"`{fp}`" not in prior:
            sys.exit(
                f"REFUSING TO LAUNCH: {config_path.name} exists with a different config "
                f"fingerprint than this run would use ({fp}). A post-start config change "
                "requires a logged rerun into a fresh results directory. Move or delete the "
                "old config and results deliberately if that is what you intend."
            )
        print(f"config fingerprint {fp} matches existing {config_path.name}; resuming")
    else:
        write_config(cells, n_workers, config_path)
        print(f"wrote {config_path} (fingerprint {fp})")

    done_ids: set[str] = set()
    if jsonl_path.exists():
        for line in jsonl_path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                done_ids.add(json.loads(line)["cell_id"])
            except (json.JSONDecodeError, KeyError):
                continue

    todo = [c for c in cells if c.cell_id not in done_ids]
    state = {
        "fingerprint": fp,
        "total": len(cells),
        "done": len(done_ids),
        "resumed": len(done_ids),
        "n_workers": n_workers,
        "t_start": time.time(),
        "cost_total": sum(expected_seconds(c) for c in cells),
        "cost_done": sum(expected_seconds(c) for c in cells if c.cell_id in done_ids),
        "core_seconds": 0.0,
        "obs_by_n": {},
        "divergences": [],
        "failures": [],
    }
    write_progress(progress_path, state)
    print(f"grid: {len(cells)} cells, {len(done_ids)} already done, {len(todo)} to run, "
          f"{n_workers} workers")
    if not todo:
        print("grid: nothing to do")
        return

    worker = partial(_run_one, reps=REPS, master_seed=GRID_MASTER_SEED, fingerprint=fp,
                     cells_dir=str(cells_dir))
    last_progress = time.time()
    with open(jsonl_path, "a") as out_f:
        with Pool(n_workers) as pool:
            for payload in pool.imap_unordered(worker, todo, chunksize=1):
                cid = payload["cell_id"]
                if payload.get("error"):
                    state["failures"].append((cid, payload["error"][:200]))
                else:
                    out_f.write(json.dumps(payload["result"]) + "\n")
                    out_f.flush()
                    n_val = payload["n"]
                    obs = state["obs_by_n"].setdefault(n_val, {"seconds": 0.0, "reps": 0, "cells": 0})
                    obs["seconds"] += payload["seconds"]
                    obs["reps"] += REPS
                    obs["cells"] += 1
                    state["core_seconds"] += payload["seconds"]
                    _check_divergence(state, n_val)
                state["done"] += 1
                state["cost_done"] += payload["expected_seconds"]

                if time.time() - last_progress >= PROGRESS_INTERVAL_S:
                    write_progress(progress_path, state)
                    last_progress = time.time()
                print(f"grid: {state['done']}/{state['total']} cell_id={cid} "
                      f"({payload['seconds']:.1f}s)", flush=True)

    write_progress(progress_path, state)
    print(f"grid: COMPLETE {state['done']}/{state['total']}")


def _check_divergence(state: dict, n_val: int) -> None:
    """Record a >25% per-rep divergence from the pilot extrapolation, once per n level."""
    obs = state["obs_by_n"][n_val]
    if obs["cells"] < 3:  # need a few cells before calling it
        return
    proj = PILOT_SECONDS_PER_REP_BY_N.get(n_val)
    if not proj:
        return
    meas = obs["seconds"] / obs["reps"]
    div = (meas - proj) / proj
    if abs(div) > DIVERGENCE_THRESHOLD and not any(f"n={n_val}" in d for d in state["divergences"]):
        state["divergences"].append(
            f"n={n_val}: measured {meas:.3f} s/rep vs projected {proj:.3f} s/rep "
            f"({div:+.1%}) over {obs['cells']} cells. Run continues per the launch brief."
        )


def _run_one(cell: Cell, reps: int, master_seed: int, fingerprint: str, cells_dir: str) -> dict:
    """Run one cell and write its manifest. Never raises: a failed cell is reported, not fatal."""
    t0 = time.time()
    started = datetime.now().isoformat(timespec="seconds")
    try:
        result = run_cell(cell, reps, master_seed)
        seconds = time.time() - t0
        manifest = {
            "cell_id": cell.cell_id,
            "cell": asdict(cell),
            "reps": reps,
            "master_seed": master_seed,
            "config_fingerprint": fingerprint,
            "started": started,
            "finished": datetime.now().isoformat(timespec="seconds"),
            "wall_seconds": seconds,
            "seconds_per_rep": seconds / reps if reps else None,
            "host": platform.node(),
            "result": result,
        }
        Path(cells_dir, f"{cell.cell_id}.json").write_text(json.dumps(manifest, indent=1))
        return {"cell_id": cell.cell_id, "result": result, "seconds": seconds,
                "n": cell.n, "expected_seconds": expected_seconds(cell), "error": None}
    except Exception as e:  # a bad cell must not take the grid down
        return {"cell_id": cell.cell_id, "result": None, "seconds": time.time() - t0,
                "n": cell.n, "expected_seconds": expected_seconds(cell),
                "error": f"{type(e).__name__}: {e}"}


if __name__ == "__main__":
    main()
