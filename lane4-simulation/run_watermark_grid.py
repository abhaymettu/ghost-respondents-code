"""Watermark near-perfect-detection cell (WATERMARK-SPEC.md, QUEUE item 4).

    .venv/bin/python run_watermark_grid.py --out results/watermark

Grid A ("jointA"): pi(6) x p(3) x {wm95, wm99}, 36 cells, full five-estimator suite --
boundary-map-shaped, composes with LAYERB-GRID.md section 5's table (`degraded` -> wm95 ->
wm99 -> `oracle` is the accuracy trajectory; `oracle` itself is not recomputed here, it is
already committed at se=sp=1.0 exactly).

Grid B ("asymB"): the hardest boundary-map cell (p=1, pi=0.30) and one low-difficulty
control (p=0, pi=0.05), crossed with se-only and sp-only pushes at {0.90, 0.95, 0.99},
naive + delete only -- the direct test of Prop. 14's se/sp asymmetry.

Both grids reuse run_layerb_grid.py's `setup`, `rep_rng`, and `build_injected_sample`
unchanged. The only new mechanism is the detector flag itself: `se`/`sp` are independent SET
knobs (`flag_M = u < se`, `flag_H = u < 1-sp`), the same logic dgp.py's Layer A `simulate`
already uses, ported to Layer B in place of `detector_flags`' real-score threshold -- because
a watermark's catch rate and false-positive rate are set by the scheme, not read off a
classifier's ROC curve (WATERMARK-SPEC.md section 2).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
from dataclasses import asdict, dataclass
from functools import partial
from multiprocessing import Pool as ProcPool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from estimators import ESTIMATORS
from inject.build import build_injected_sample
from metrics import _target_metrics
from run_layerb_grid import FRONTIER, K_CHUNKS, PI_LEVELS, RHO_T, rep_rng, setup

REPS = 100
CORES_LEFT_FREE = 2
WM_JOINT = {"wm95": (0.95, 0.95), "wm99": (0.99, 0.99)}
WM_ASYM = {
    "wm_se90": (0.90, 1.0), "wm_se95": (0.95, 1.0), "wm_se99": (0.99, 1.0),
    "wm_sp90": (1.0, 0.90), "wm_sp95": (1.0, 0.95), "wm_sp99": (1.0, 0.99),
}
ARM_ESTIMATOR_NAMES = {
    "jointA": ("naive", "delete", "simex", "labelfree", "em"),
    "asymB": ("naive", "delete"),
}


@dataclass(frozen=True)
class WMCell:
    pi: float
    p: float
    detector: str  # wm95/wm99/wm_se90/... key into WM_JOINT or WM_ASYM
    se: float
    sp: float
    arm: str  # "jointA" or "asymB"
    n: int = 1000
    pool: str = FRONTIER
    trait: str = "EXT"

    @property
    def cell_id(self) -> str:
        payload = "|".join(f"{k}={v}" for k, v in sorted(asdict(self).items()) if k != "arm")
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


def grid_a_cells() -> list[WMCell]:
    return sorted(
        (WMCell(pi=pi, p=p, detector=d, se=se, sp=sp, arm="jointA")
         for pi in PI_LEVELS for p in (0.0, 0.5, 1.0) for d, (se, sp) in WM_JOINT.items()),
        key=lambda c: c.cell_id,
    )


def grid_b_cells() -> list[WMCell]:
    base = ((1.0, 0.30), (0.0, 0.05))  # (p, pi): hardest boundary-map cell, one control
    return sorted(
        (WMCell(pi=pi, p=p, detector=d, se=se, sp=sp, arm="asymB")
         for p, pi in base for d, (se, sp) in WM_ASYM.items()),
        key=lambda c: c.cell_id,
    )


def run_cell(cell: WMCell, reps: int = REPS) -> dict:
    S = setup(cell.pool, cell.trait)
    est_names = ARM_ESTIMATOR_NAMES[cell.arm]
    fits_per_rep: list[dict] = []
    realized = {"sp": [], "se": [], "flag_rate": []}
    for rep in range(reps):
        rng = rep_rng(cell, rep)
        inj = build_injected_sample(S["H_b"], S["M_i"], cell.n, cell.pi, cell.p, rng,
                                    rho_T=RHO_T, k_chunks=K_CHUNKS, sp=1.0, replace=True)
        s = inj.sample
        u = rng.random(cell.n)
        s.flag = np.where(s.A == 1, u < cell.se, u < (1.0 - cell.sp))
        H, M = s.A == 0, s.A == 1
        realized["sp"].append(float(np.mean(~s.flag[H])) if H.any() else float("nan"))
        realized["se"].append(float(np.mean(s.flag[M])) if M.any() else float("nan"))
        realized["flag_rate"].append(float(s.flag.mean()))

        # Watermark parameters are the scheme's published/measured knobs, not calibrated off
        # held-out text -- unlike the classifier detectors, the researcher's belief IS (se, sp).
        opts = {
            "naive": {}, "delete": {},
            "simex": {"se": cell.se, "sp": cell.sp,
                      "rng": np.random.default_rng(rng.integers(0, 2**31 - 1))},
            "labelfree": {"se": cell.se, "sp": cell.sp,
                          "machine_ref": S["Mref_c1"], "human_ref": S["Href_c1"],
                          "c_known": 0.0,
                          "rng": np.random.default_rng(rng.integers(0, 2**31 - 1))},
            "em": {"rng": np.random.default_rng(rng.integers(0, 2**31 - 1))},
        }
        fits_per_rep.append({name: ESTIMATORS[name](s, **opts.get(name, {})) for name in est_names})

    truth = {"rho_H": S["rho_H_true"], "rho_T": S["rho_T_true"], "pi": cell.pi,
              "loading": S["loading_true"]}
    estimators_out = {}
    for name in sorted(est_names):
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
        "detector": {"se_set": cell.se, "sp_set": cell.sp,
                     "realized_sp": float(np.nanmean(realized["sp"])),
                     "realized_se": float(np.nanmean(realized["se"])),
                     "flag_rate": float(np.nanmean(realized["flag_rate"]))},
        "estimators": estimators_out,
    }


def _run_one(cell: WMCell, reps: int, cells_dir: str) -> dict:
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
    ap = argparse.ArgumentParser(description="Run the watermark near-perfect-detection cell.")
    ap.add_argument("--out", default="results/watermark")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--reps", type=int, default=REPS)
    ap.add_argument("--cells-only", action="store_true")
    args = ap.parse_args()

    here = Path(__file__).resolve().parent
    out_dir = (here / args.out).resolve()
    cells = grid_a_cells() + grid_b_cells()
    n_jointA = sum(1 for c in cells if c.arm == "jointA")
    print(f"watermark: {len(cells)} cells ({n_jointA} jointA, "
          f"{len(cells) - n_jointA} asymB), reps={args.reps}", flush=True)
    if args.cells_only:
        for c in cells:
            print(f"  arm={c.arm:6s} pi={c.pi:<5} p={c.p:<4} det={c.detector:9s} "
                  f"se={c.se} sp={c.sp} {c.cell_id}")
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
                    print(f"watermark: {n_done}/{len(cells)} FAILED {payload['cell_id']}: "
                          f"{payload['error'][:200]}", flush=True)
                    continue
                out_f.write(json.dumps(payload["result"]) + "\n")
                out_f.flush()
                c = payload["result"]["cell"]
                print(f"watermark: {n_done}/{len(cells)} arm={c['arm']:6s} pi={c['pi']:<5} "
                      f"p={c['p']:<4} det={c['detector']:9s} ({payload['seconds']:.1f}s, "
                      f"{time.time() - t0:.0f}s elapsed)", flush=True)

    print(f"watermark: COMPLETE {n_done - len(failures)}/{len(cells)} in {time.time() - t0:.0f}s"
          + (f", {len(failures)} FAILED" if failures else ""))
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
