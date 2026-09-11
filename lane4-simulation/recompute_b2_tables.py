"""Recompute pass3-methods-review.md B2's H3/H4/SPEC-4.4 tables at the shipped configuration:
labelfree at n_bins=8 (M1), simex with B_boot>0 so its coverage is testable (B2), and adds
bounds_c (H5, B3) alongside. naive/delete/em/robust_t/robust_grm are unaffected by n_bins/B_boot
and are read from the frozen results/grid/grid.jsonl.

Merges four grid outputs by cell_id -- the frozen grid plus the three single-column re-runs
this session produced -- into one row per cell, then reproduces B2's four table shapes.

Run:  .venv/bin/python recompute_b2_tables.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
FROZEN = HERE / "results/grid/grid.jsonl"
LABELFREE8 = HERE / "results/grid-labelfree-nbins8/grid.jsonl"
SIMEX_BOOT = HERE / "results/grid-simex-boot50/grid.jsonl"
BOUNDS_C = HERE / "results/grid-bounds-c/grid.jsonl"

C_PARTIAL_APPLICABILITY = 0.5  # metrics.py's C_PARTIAL, SPEC 4.4's "c <= partial" cutoff


def _isnan(x) -> bool:
    """NaN floats survive JSON round-trip as None (grid.py's _clean); treat both as missing."""
    return x is None or (isinstance(x, float) and math.isnan(x))


def load(path: Path) -> dict[str, dict]:
    return {json.loads(l)["cell_id"]: json.loads(l) for l in path.read_text().splitlines() if l.strip()}


def merged_rows() -> list[dict]:
    frozen = load(FROZEN)
    labelfree8 = load(LABELFREE8)
    simex_boot = load(SIMEX_BOOT) if SIMEX_BOOT.exists() else {}
    bounds_c = load(BOUNDS_C)

    rows = []
    n_simex_boot, n_labelfree8, n_bounds_c = 0, 0, 0
    for cell_id, base in frozen.items():
        est = dict(base["summary"]["estimators"])  # naive, delete, em, labelfree(stale), simex(B_boot=0)
        if cell_id in labelfree8:
            est["labelfree"] = labelfree8[cell_id]["summary"]["estimators"]["labelfree"]
            n_labelfree8 += 1
        if cell_id in simex_boot:
            est["simex"] = simex_boot[cell_id]["summary"]["estimators"]["simex"]
            n_simex_boot += 1
        if cell_id in bounds_c:
            est["bounds_c"] = bounds_c[cell_id]["summary"]["estimators"]["bounds_c"]
            n_bounds_c += 1
        rows.append({"cell_id": cell_id, "cell": base["cell"], "estimators": est})
    counts = {"labelfree8": n_labelfree8, "simex_boot": n_simex_boot, "bounds_c": n_bounds_c}
    return rows, counts


def table_h4_coverage(rows: list[dict]) -> dict[str, tuple[int, int]]:
    """H4: cells with rho_H coverage in [0.92, 0.98]."""
    out: dict[str, tuple[int, int]] = {}
    for name in ("delete", "naive", "em", "labelfree", "simex"):
        n_pass, n_total = 0, 0
        for r in rows:
            e = r["estimators"].get(name)
            if e is None:
                continue
            cov = e["rho_H"]["coverage"]
            n_total += 1
            if not _isnan(cov) and 0.92 <= cov <= 0.98:
                n_pass += 1
        out[name] = (n_pass, n_total)
    return out


def table_h3_rmse_beats_delete(rows: list[dict]) -> dict[str, dict[str, tuple[int, int]]]:
    """H3: fraction of realistic-detector cells (detector != none) where estimator RMSE < delete RMSE."""
    out: dict[str, dict[str, tuple[int, int]]] = {}
    for name in ("simex", "em", "labelfree", "bounds_c"):
        calibrated = [0, 0]
        degraded = [0, 0]
        for r in rows:
            e = r["estimators"].get(name)
            d = r["estimators"].get("delete")
            if e is None or d is None or r["cell"]["detector"] not in ("calibrated", "degraded"):
                continue
            bucket = calibrated if r["cell"]["detector"] == "calibrated" else degraded
            bucket[1] += 1
            e_rmse, d_rmse = e["rho_H"]["rmse"], d["rho_H"]["rmse"]
            if _isnan(e_rmse) or _isnan(d_rmse):
                continue
            if e_rmse < d_rmse:
                bucket[0] += 1
        out[name] = {"calibrated": tuple(calibrated), "degraded": tuple(degraded)}
    return out


def table_corrected_bias(rows: list[dict]) -> dict[str, dict[str, float]]:
    """'corrected bias at most 20% of naive bias', pi<=0.20 and c<=partial (metrics.C_PARTIAL)."""
    out: dict[str, dict[str, float]] = {}
    for name in ("simex", "delete", "em", "labelfree", "bounds_c"):
        ratios = []
        for r in rows:
            if r["cell"]["pi"] > 0.20 or r["cell"]["c"] > C_PARTIAL_APPLICABILITY:
                continue
            e = r["estimators"].get(name)
            n_ = r["estimators"].get("naive")
            if e is None or n_ is None:
                continue
            naive_bias = n_["rho_H"]["bias"]
            corr_bias = e["rho_H"]["bias"]
            if _isnan(naive_bias) or _isnan(corr_bias) or naive_bias == 0:
                continue
            ratios.append(abs(corr_bias) / abs(naive_bias))
        if ratios:
            arr = np.array(ratios)
            out[name] = {
                "n_cells": len(arr),
                "frac_le_020": float(np.mean(arr <= 0.20)),
                "median_ratio": float(np.median(arr)),
                "max_ratio": float(np.max(arr)),
            }
    return out


def table_pi_hat_err(rows: list[dict]) -> dict[str, dict[str, float]]:
    """'pi-hat error at most 2 points at n=1000'."""
    out: dict[str, dict[str, float]] = {}
    for name in ("em", "labelfree"):
        errs = []
        for r in rows:
            if r["cell"]["n"] != 1000:
                continue
            e = r["estimators"].get(name)
            if e is None or e.get("pi_abs_err") is None:
                continue
            errs.append(e["pi_abs_err"]["value"])
        if errs:
            arr = np.array(errs)
            out[name] = {
                "n_cells": len(arr),
                "median": float(np.median(arr)),
                "max": float(np.max(arr)),
                "frac_le_002": float(np.mean(arr <= 0.02)),
            }
    return out


def table_h5_bound_width(rows: list[dict]) -> dict[str, dict]:
    """H5: bound width < 0.2 correlation units, all cells and at n=1000."""
    out: dict[str, dict] = {}
    for label, pred in (("all", lambda c: True), ("n=1000", lambda c: c["n"] == 1000)):
        widths, covs = [], []
        for r in rows:
            if not pred(r["cell"]):
                continue
            e = r["estimators"].get("bounds_c")
            if e is None:
                continue
            widths.append(e["rho_H"]["ci_width"])
            covs.append(e["rho_H"]["coverage"])
        if widths:
            w = np.array(widths)
            cov = np.array(covs)
            out[label] = {
                "n_cells": len(w),
                "median_width": float(np.median(w)),
                "max_width": float(np.max(w)),
                "frac_width_lt_0.2": float(np.mean(w < 0.2)),
                "median_coverage": float(np.median(cov)),
                "frac_coverage_ge_0.90": float(np.mean(cov >= 0.90)),
            }
    return out


def main() -> None:
    rows, counts = merged_rows()
    print(f"merged {len(rows)} cells "
          f"(labelfree@n_bins=8: {counts['labelfree8']}/{len(rows)}, "
          f"simex B_boot>0: {counts['simex_boot']}/{len(rows)}, "
          f"bounds_c: {counts['bounds_c']}/{len(rows)})")
    if counts["simex_boot"] < len(rows):
        print(f"NOTE: simex B_boot rerun incomplete -- {len(rows) - counts['simex_boot']} cells still "
              "use the frozen grid's B_boot=0 simex column (null coverage). Re-run this script once "
              "results/grid-simex-boot50/grid.jsonl reaches 372 lines for final numbers.")

    print("\n=== H4 coverage in [0.92, 0.98] ===")
    for name, (n_pass, n_total) in table_h4_coverage(rows).items():
        print(f"  {name}: {n_pass}/{n_total} ({n_pass/n_total:.3f})" if n_total else f"  {name}: n/a")

    print("\n=== H3: RMSE beats delete (realistic detectors) ===")
    for name, d in table_h3_rmse_beats_delete(rows).items():
        for det, (n_pass, n_total) in d.items():
            print(f"  {name} {det}: {n_pass}/{n_total} ({n_pass/n_total:.3f})" if n_total else f"  {name} {det}: n/a")

    print("\n=== corrected bias <= 20% naive bias (pi<=0.20, c<=partial) ===")
    for name, d in table_corrected_bias(rows).items():
        print(f"  {name}: n={d['n_cells']} frac<=0.20={d['frac_le_020']:.3f} "
              f"median={d['median_ratio']:.3f} max={d['max_ratio']:.1f}")

    print("\n=== pi-hat error <= 2 points at n=1000 ===")
    for name, d in table_pi_hat_err(rows).items():
        print(f"  {name}: n={d['n_cells']} median={d['median']:.4f} max={d['max']:.4f} "
              f"frac<=0.02={d['frac_le_002']:.3f}")

    print("\n=== H5 bound width < 0.2 / coverage (bounds_c) ===")
    for label, d in table_h5_bound_width(rows).items():
        print(f"  {label}: n={d['n_cells']} median_width={d['median_width']:.4f} "
              f"max_width={d['max_width']:.4f} frac_width<0.2={d['frac_width_lt_0.2']:.3f} "
              f"median_coverage={d['median_coverage']:.3f} frac_cov>=0.90={d['frac_coverage_ge_0.90']:.3f}")

    out = {
        "h4_coverage": {k: {"n_pass": v[0], "n_total": v[1]} for k, v in table_h4_coverage(rows).items()},
        "h3_rmse_beats_delete": table_h3_rmse_beats_delete(rows),
        "corrected_bias": table_corrected_bias(rows),
        "pi_hat_err": table_pi_hat_err(rows),
        "h5_bound_width": table_h5_bound_width(rows),
        "simex_b_boot_available": SIMEX_BOOT.exists(),
    }
    out_path = HERE / "results/b2-tables-recomputed.json"
    out_path.write_text(json.dumps(out, indent=1))
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
