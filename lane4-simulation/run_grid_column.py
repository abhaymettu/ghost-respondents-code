"""Re-run ONE estimator column of the frozen Layer A grid (results/grid/grid.jsonl), reusing
the frozen cell set and the exact per-rep RNG streams grid.run_cell always builds first.

Generalizes run_labelfree_nbins8.py (M1) to any single-estimator column re-run, used for:
  - bounds_c: the H5 partial-identification bounds estimator did not exist when the grid ran
    (pass3-methods-review.md B3). Cheap (no resampling), so re-running it over all 372 cells
    costs about what naive costs.
  - simex with B_boot > 0: the grid ran with B_boot=0 (GRID-CONFIG.md), so simex's ci_H is
    null in every cell and its H4 coverage is structurally untestable (pass3-methods-review.md
    B2). Re-running with the module's estimator_opts lets B_boot be set without editing
    estimators.py's signature default.

Faithfulness note (same as run_labelfree_nbins8.py): this calls grid.run_cell itself with the
module-level ESTIMATORS map narrowed to one name; run_cell builds its per-rep default_opts --
including every estimator's RNG draw -- BEFORE the estimator loop and always in the same
source order, so narrowing the map changes which fits execute and not one draw of any other
estimator's RNG stream. estimators.py is not edited by this script; nothing here writes to
results/grid/.

Run:
  .venv/bin/python run_grid_column.py --estimator bounds_c --out results/grid-bounds-c
  .venv/bin/python run_grid_column.py --estimator simex --out results/grid-simex-boot \
      --estimator-opts '{"B_boot": 50}'
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from functools import partial
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import estimators
from run_grid_full import ARMS, GRID_MASTER_SEED, REPS

FROZEN = Path(__file__).resolve().parent / "results/grid/grid.jsonl"


def _run_one(cell, reps: int, cells_dir: str, estimator_name: str,
             extra_opts: dict) -> dict:
    estimators.ESTIMATORS = {estimator_name: getattr(estimators, f"fit_{estimator_name}")}
    from grid import run_cell
    t0 = time.time()
    try:
        result = run_cell(cell, reps, GRID_MASTER_SEED,
                           estimator_opts={estimator_name: extra_opts} if extra_opts else None)
        result["column_rerun"] = {"estimator": estimator_name, "extra_opts": extra_opts}
        result["wall_seconds"] = time.time() - t0
        Path(cells_dir, f"{cell.cell_id}.json").write_text(json.dumps(result, indent=1))
        return {"cell_id": cell.cell_id, "result": result, "seconds": time.time() - t0, "error": None}
    except Exception as e:
        return {"cell_id": cell.cell_id, "result": None, "seconds": time.time() - t0,
                "error": f"{type(e).__name__}: {e}"}


def main() -> None:
    ap = argparse.ArgumentParser(description="Re-run one estimator column of the frozen Layer A grid.")
    ap.add_argument("--estimator", required=True, help="name registered in estimators.ESTIMATORS")
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--reps", type=int, default=REPS)
    ap.add_argument("--estimator-opts", type=str, default="{}",
                     help="JSON dict merged into this estimator's per-rep opts")
    args = ap.parse_args()

    extra_opts = json.loads(args.estimator_opts)
    here = Path(__file__).resolve().parent
    out_dir = (here / args.out).resolve()
    assert out_dir.name not in ("grid", "grid-nonignorable", "layerb-grid"), "frozen or live"
    (out_dir / "cells").mkdir(parents=True, exist_ok=True)

    if not hasattr(estimators, f"fit_{args.estimator}"):
        sys.exit(f"REFUSING: no fit_{args.estimator} in estimators.py")

    from grid import full_grid
    by_id = {c.cell_id: c for c in full_grid(ARMS)}
    frozen_ids = [json.loads(l)["cell_id"] for l in FROZEN.read_text().splitlines() if l.strip()]
    missing = [i for i in frozen_ids if i not in by_id]
    if missing:
        sys.exit(f"REFUSING: {len(missing)} frozen cell_ids are not reproducible from full_grid(ARMS)")
    cells = [by_id[i] for i in sorted(frozen_ids)]

    jsonl_path = out_dir / "grid.jsonl"
    done: set[str] = set()
    if jsonl_path.exists():
        for line in jsonl_path.read_text().splitlines():
            if line.strip():
                done.add(json.loads(line)["cell_id"])
    todo = [c for c in cells if c.cell_id not in done]
    n_workers = args.workers or max(1, (os.cpu_count() or 4) - 2)
    print(f"column rerun ({args.estimator}, opts={extra_opts}): {len(cells)} frozen cells, "
          f"{len(done)} done, {len(todo)} to run, {n_workers} workers, reps={args.reps}, "
          f"seed={GRID_MASTER_SEED}", flush=True)
    if not todo:
        print("nothing to do")
        return

    t0, n_done, failures = time.time(), len(done), []
    with open(jsonl_path, "a") as out_f:
        with Pool(n_workers) as pool:
            worker = partial(_run_one, reps=args.reps, cells_dir=str(out_dir / "cells"),
                              estimator_name=args.estimator, extra_opts=extra_opts)
            for payload in pool.imap_unordered(worker, todo, chunksize=1):
                n_done += 1
                if payload.get("error"):
                    failures.append((payload["cell_id"], payload["error"]))
                    print(f"col: {n_done}/{len(cells)} FAILED {payload['cell_id']}: "
                          f"{payload['error'][:200]}", flush=True)
                    continue
                out_f.write(json.dumps(payload["result"]) + "\n")
                out_f.flush()
                if n_done % 10 == 0 or n_done == len(cells):
                    print(f"col: {n_done}/{len(cells)} ({time.time() - t0:.0f}s elapsed)", flush=True)

    print(f"col: COMPLETE {n_done - len(failures)}/{len(cells)} in {time.time() - t0:.0f}s"
          + (f", {len(failures)} FAILED (listed above)" if failures else ""))
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
