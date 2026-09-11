"""Robust-estimator arm (ROBUST-ARM-SPEC.md): naive + robust_t + robust_grm on the exact
72-cell Layer B boundary map (LAYERB-GRID.md section 5: n=1000, core box, all pi x detector x p).

    .venv/bin/python run_robust_arm.py --out results/robust-arm

Reuses run_layerb_grid.py's `setup`, `rep_rng`, `box()` and `build_injected_sample` call
unchanged, so the cell_ids, truth values, detector calibration and per-(cell,rep) draws are
IDENTICAL to the frozen `results/layerb-grid/` record -- `naive` recomputed here must
reproduce that record's naive numbers exactly (ROBUST-ARM-SPEC.md section 2's check).
`delete`/`simex`/`labelfree`/`em` are not recomputed; their numbers are already committed
there and quoted directly in the addendum.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
from dataclasses import asdict
from functools import partial
from multiprocessing import Pool as ProcPool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from estimators import fit_naive, fit_robust_grm, fit_robust_t
from inject.build import build_injected_sample
from metrics import _target_metrics
from run_layerb_grid import FRONTIER, K_CHUNKS, RHO_T, SP_TARGET, box, rep_rng, setup

REPS = 100
ARM_ESTIMATORS = {"naive": fit_naive, "robust_t": fit_robust_t, "robust_grm": fit_robust_grm}
CORES_LEFT_FREE = 2


def boundary_map_cells():
    """The exact 72 cells of LAYERB-GRID.md section 5: n=1000, arm='box' (core box only)."""
    return sorted(
        (c for c in box() if c.n == 1000 and c.arm == "box"),
        key=lambda c: c.cell_id,
    )


def run_cell(cell, reps: int = REPS) -> dict:
    S = setup(cell.pool, cell.trait)
    fits_per_rep: list[dict] = []
    for rep in range(reps):
        rng = rep_rng(cell, rep)
        inj = build_injected_sample(S["H_b"], S["M_i"], cell.n, cell.pi, cell.p, rng,
                                    rho_T=RHO_T, k_chunks=K_CHUNKS,
                                    sp=SP_TARGET[cell.detector], replace=True)
        s = inj.sample
        fits_per_rep.append({name: fn(s) for name, fn in ARM_ESTIMATORS.items()})

    truth = {"rho_H": S["rho_H_true"], "rho_T": S["rho_T_true"], "pi": cell.pi,
              "loading": S["loading_true"]}
    estimators_out = {}
    for name in sorted(ARM_ESTIMATORS):
        rf = [r[name] for r in fits_per_rep]
        conv = np.array([bool(f is not None and f.converged) for f in rf])
        out = {}
        for target, attr, ci_attr in (("rho_H", "rho_H_hat", "ci_H"), ("rho_T", "rho_T_hat", "ci_T")):
            est = np.array([float(getattr(f, attr)) for f in rf])
            out[target] = _target_metrics(est, conv, [getattr(f, ci_attr) for f in rf], truth[target])
        out["n_converged"] = int(conv.sum())
        estimators_out[name] = out

    return {
        "cell_id": cell.cell_id, "cell": asdict(cell), "reps": reps, "truth": truth,
        "estimators": estimators_out,
    }


def _run_one(cell, reps: int, cells_dir: str) -> dict:
    t0 = time.time()
    try:
        result = run_cell(cell, reps)
        result["wall_seconds"] = time.time() - t0
        result["host"] = platform.node()
        Path(cells_dir, f"{cell.cell_id}.json").write_text(json.dumps(result, indent=1))
        return {"cell_id": cell.cell_id, "result": result, "seconds": time.time() - t0, "error": None}
    except Exception as e:
        return {"cell_id": cell.cell_id, "result": None, "seconds": time.time() - t0,
                "error": f"{type(e).__name__}: {e}"}


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the robust-estimator arm (boundary-map cells).")
    ap.add_argument("--out", default="results/robust-arm")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--reps", type=int, default=REPS)
    ap.add_argument("--cells-only", action="store_true")
    args = ap.parse_args()

    here = Path(__file__).resolve().parent
    out_dir = (here / args.out).resolve()
    cells = boundary_map_cells()
    print(f"robust arm: {len(cells)} cells (n=1000, core box), reps={args.reps}", flush=True)
    if args.cells_only:
        for c in cells:
            print(f"  pi={c.pi:<5} p={c.p:<4} det={c.detector:11s} {c.cell_id}")
        return

    (out_dir / "cells").mkdir(parents=True, exist_ok=True)
    jsonl_path = out_dir / "grid.jsonl"
    done: set[str] = set()
    if jsonl_path.exists():
        for line in jsonl_path.read_text().splitlines():
            if line.strip():
                done.add(json.loads(line)["cell_id"])
    todo = [c for c in cells if c.cell_id not in done]
    n_workers = args.workers or max(1, (os.cpu_count() or 4) - CORES_LEFT_FREE)
    print(f"  {len(done)} already done, {len(todo)} to run, {n_workers} workers", flush=True)
    if not todo:
        print("nothing to do")
        return

    S = setup(FRONTIER, "EXT")
    print(f"  split_id={S['split_id']} truth rho_H={S['rho_H_true']:.4f}", flush=True)

    t0, n_done, failures = time.time(), len(done), []
    with open(jsonl_path, "a") as out_f:
        with ProcPool(n_workers) as pool:
            worker = partial(_run_one, reps=args.reps, cells_dir=str(out_dir / "cells"))
            for payload in pool.imap_unordered(worker, todo, chunksize=1):
                n_done += 1
                if payload.get("error"):
                    failures.append((payload["cell_id"], payload["error"]))
                    print(f"robustarm: {n_done}/{len(cells)} FAILED {payload['cell_id']}: "
                          f"{payload['error'][:200]}", flush=True)
                    continue
                out_f.write(json.dumps(payload["result"]) + "\n")
                out_f.flush()
                c = payload["result"]["cell"]
                print(f"robustarm: {n_done}/{len(cells)} pi={c['pi']:<5} p={c['p']:<4} "
                      f"det={c['detector']:11s} ({payload['seconds']:.1f}s, "
                      f"{time.time() - t0:.0f}s elapsed)", flush=True)

    print(f"robustarm: COMPLETE {n_done - len(failures)}/{len(cells)} in {time.time() - t0:.0f}s"
          + (f", {len(failures)} FAILED" if failures else ""))
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
