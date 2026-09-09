"""Run the between-mean arms that close pass-2 flag P2-3, into their own results directory.

    .venv/bin/python run_arms.py --out results/grid-nonignorable

The completed 372-cell grid (results/grid/) is a frozen record and this script never opens
it. It deliberately does NOT reuse run_grid_full.py's main(): that one writes GRID-CONFIG.md
and GRID-PROGRESS.md, which belong to the frozen run. Everything that decides a number --
the cells, `run_cell`, `_run_one`, REPS, GRID_MASTER_SEED -- is imported from the same
modules the frozen grid used, so these cells are drawn from the same DGP with the same seed
scheme and are directly comparable to it.
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

from grid import full_grid
from run_grid_full import GRID_MASTER_SEED, REPS, _run_one, config_fingerprint

ARMS = ("nonignorable", "delta", "flip")


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the P2-3 between-mean arms.")
    ap.add_argument("--out", default="results/grid-nonignorable")
    ap.add_argument("--workers", type=int, default=None)
    args = ap.parse_args()

    here = Path(__file__).resolve().parent
    out_dir = (here / args.out).resolve()
    assert out_dir.name != "grid", "results/grid is the frozen pass-2 record"
    (out_dir / "cells").mkdir(parents=True, exist_ok=True)
    jsonl_path = out_dir / "grid.jsonl"

    cells = sorted(full_grid(ARMS), key=lambda c: c.cell_id)
    # Identifies this cell set (the cell_ids are in the hash) and is stamped into every cell
    # manifest. Its "arms" field is run_grid_full's own frozen tuple, not the tuple above, so
    # read it as a cell-set id, not as a description of which arms ran.
    fp = config_fingerprint(cells)
    n_workers = args.workers or max(1, (os.cpu_count() or 4) - 2)

    done: set[str] = set()
    if jsonl_path.exists():
        for line in jsonl_path.read_text().splitlines():
            if line.strip():
                done.add(json.loads(line)["cell_id"])
    todo = [c for c in cells if c.cell_id not in done]
    print(f"arms {ARMS}: {len(cells)} cells, {len(done)} done, {len(todo)} to run, "
          f"{n_workers} workers, reps={REPS}, master_seed={GRID_MASTER_SEED}, cell-set id {fp}",
          flush=True)
    for c in cells:
        print(f"  {c.arm:13s} pi={c.pi} delta={c.delta} d_theta={c.d_theta} c={c.c} "
              f"rho_v={c.rho_v} det={c.detector} n={c.n} {c.cell_id}", flush=True)
    if not todo:
        print("nothing to do")
        return

    t0, n_done, failures = time.time(), len(done), []
    with open(jsonl_path, "a") as out_f:
        with Pool(n_workers) as pool:
            worker = partial(_run_one, reps=REPS, master_seed=GRID_MASTER_SEED,
                             fingerprint=fp, cells_dir=str(out_dir / "cells"))
            for payload in pool.imap_unordered(worker, todo, chunksize=1):
                n_done += 1
                if payload.get("error"):
                    failures.append((payload["cell_id"], payload["error"]))
                    print(f"arms: {n_done}/{len(cells)} FAILED {payload['cell_id']}: "
                          f"{payload['error'][:200]}", flush=True)
                    continue
                out_f.write(json.dumps(payload["result"]) + "\n")
                out_f.flush()
                print(f"arms: {n_done}/{len(cells)} cell_id={payload['cell_id']} "
                      f"({payload['seconds']:.1f}s, {time.time() - t0:.0f}s elapsed)", flush=True)

    print(f"arms: COMPLETE {n_done - len(failures)}/{len(cells)} in {time.time() - t0:.0f}s"
          + (f", {len(failures)} FAILED (listed above)" if failures else ""))
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
