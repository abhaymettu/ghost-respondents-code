"""M1 (pass-3 methods): re-execute ONLY the labelfree column of the Layer A grid at n_bins = 8.

    .venv/bin/python run_labelfree_nbins8.py --out results/grid-labelfree-nbins8

The 372-cell Layer A grid in results/grid/ was run before 2026-09-09, when
`_distribution_match_pi`'s shipped default was n_bins = 60. SPEC-FIXES-ROUND3.md fix 2 changed
it to 8 after the grid completed, so the frozen grid's `labelfree` column is the only part of
it that describes a superseded estimator. This re-runs that column, and nothing else, at the
current default.

Faithfulness. The point is a paired comparison, so every rep must see the same data and the
same reference draws as the original. This calls `grid.run_cell` itself with the module-level
ESTIMATORS map narrowed to labelfree; `run_cell` builds its per-rep `default_opts` -- including
labelfree's `machine_ref` / `human_ref` normal draws and each estimator's seed integer -- BEFORE
the estimator loop and always in the same source order, so narrowing the map changes which fits
execute and not one draw of the RNG stream. `estimators.py` is not edited; nothing here writes
to results/grid/.
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
from estimators import _distribution_match_pi, fit_labelfree
from run_grid_full import ARMS, GRID_MASTER_SEED, REPS

FROZEN = Path(__file__).resolve().parent / "results/grid/grid.jsonl"


def _run_one(cell, reps: int, cells_dir: str) -> dict:
    # Narrow the map in the worker, before grid.run_cell's deferred import reads it.
    estimators.ESTIMATORS = {"labelfree": fit_labelfree}
    from grid import run_cell
    t0 = time.time()
    try:
        result = run_cell(cell, reps, GRID_MASTER_SEED)
        result["n_bins_default"] = _distribution_match_pi.__defaults__[0]
        result["wall_seconds"] = time.time() - t0
        Path(cells_dir, f"{cell.cell_id}.json").write_text(json.dumps(result, indent=1))
        return {"cell_id": cell.cell_id, "result": result, "seconds": time.time() - t0, "error": None}
    except Exception as e:
        return {"cell_id": cell.cell_id, "result": None, "seconds": time.time() - t0,
                "error": f"{type(e).__name__}: {e}"}


def main() -> None:
    ap = argparse.ArgumentParser(description="Re-run the Layer A labelfree column at n_bins=8.")
    ap.add_argument("--out", default="results/grid-labelfree-nbins8")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--reps", type=int, default=REPS)
    args = ap.parse_args()

    here = Path(__file__).resolve().parent
    out_dir = (here / args.out).resolve()
    assert out_dir.name not in ("grid", "grid-nonignorable", "layerb-grid"), "frozen or live"
    (out_dir / "cells").mkdir(parents=True, exist_ok=True)

    n_bins = _distribution_match_pi.__defaults__[0]
    if n_bins != 8:
        sys.exit(f"REFUSING: estimators.py ships n_bins={n_bins}, expected 8. "
                 "M1 is defined as the re-run at the CURRENT default; do not edit estimators.py.")

    # The cell set comes from the frozen grid's own rows, so this reruns exactly what ran --
    # not what a rebuilt grid definition would produce today.
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
    print(f"M1 labelfree re-run: {len(cells)} frozen cells, {len(done)} done, {len(todo)} to run, "
          f"{n_workers} workers, reps={args.reps}, n_bins={n_bins}, seed={GRID_MASTER_SEED}",
          flush=True)
    if not todo:
        print("nothing to do")
        return

    t0, n_done, failures = time.time(), len(done), []
    with open(jsonl_path, "a") as out_f:
        with Pool(n_workers) as pool:
            worker = partial(_run_one, reps=args.reps, cells_dir=str(out_dir / "cells"))
            for payload in pool.imap_unordered(worker, todo, chunksize=1):
                n_done += 1
                if payload.get("error"):
                    failures.append((payload["cell_id"], payload["error"]))
                    print(f"m1: {n_done}/{len(cells)} FAILED {payload['cell_id']}: "
                          f"{payload['error'][:200]}", flush=True)
                    continue
                out_f.write(json.dumps(payload["result"]) + "\n")
                out_f.flush()
                if n_done % 10 == 0 or n_done == len(cells):
                    print(f"m1: {n_done}/{len(cells)} ({time.time() - t0:.0f}s elapsed)", flush=True)

    print(f"m1: COMPLETE {n_done - len(failures)}/{len(cells)} in {time.time() - t0:.0f}s"
          + (f", {len(failures)} FAILED (listed above)" if failures else ""))
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
