"""Task 1 of the H5-detected close-out: estimate r_F and check A3 from the real pools.

Uses the SAME loader run_layerb_grid.py's `setup()` uses (inject.pools.lane3_pool,
score_version="oof", human pool "pk_human", machine pools "personallm_gpt-4-0613" and
"personallm_llama-2", trait "EXT"). Runs on the FULL pool (not the frozen calibration
split/injection half) because r_F and the A3 diagnostic are properties of the detector and
the pool, not of a particular injected sample -- and using the full pool gives narrower CIs
without touching anything the grid's frozen split_id depends on.

r_F = -Cor(detector_pools, label); see H5-DETECTED.md section 1.

Run:  lane4-simulation/.venv/bin/python r_f_estimation.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from inject.pools import lane3_pool, load_lane3

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "h5-bounds-detected" / "r_f_estimation.json"
TRAIT = "EXT"
HUMAN_POOL = "pk_human"
MACHINE_POOLS = ("personallm_gpt-4-0613", "personallm_llama-2")
SCORE_VERSION = "oof"
N_BOOT = 2000
BOOT_SEED = 20260927


def boot_corr(a: np.ndarray, b: np.ndarray, n_boot: int, seed: int) -> dict:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    mask = np.isfinite(a) & np.isfinite(b)
    a, b = a[mask], b[mask]
    n = a.size
    point = float(np.corrcoef(a, b)[0, 1])
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    boots = np.empty(n_boot)
    for i in range(n_boot):
        ai, bi = a[idx[i]], b[idx[i]]
        if ai.std() == 0 or bi.std() == 0:
            boots[i] = np.nan
            continue
        boots[i] = np.corrcoef(ai, bi)[0, 1]
    lo, hi = np.nanpercentile(boots, [2.5, 97.5])
    n_nan = int(np.sum(~np.isfinite(boots)))
    return {"point": point, "ci95": [float(lo), float(hi)], "n": int(n),
            "n_boot": n_boot, "n_boot_degenerate": n_nan}


def main() -> None:
    raw = load_lane3()
    H = lane3_pool(HUMAN_POOL, TRAIT, raw, score_version=SCORE_VERSION)
    results: dict = {
        "trait": TRAIT, "human_pool": HUMAN_POOL, "score_version": SCORE_VERSION,
        "n_boot": N_BOOT, "boot_seed": BOOT_SEED,
        "sign_convention": (
            "inject/pools.py detector: high=machine-like. population.py/E33: F high="
            "fluent/human-like, pass iff F>tau. r_F_population_convention = "
            "-Cor(detector_pools, label)."
        ),
        "human_pool_diagnostics": {},
        "machine_pool_diagnostics": {},
    }

    det_H, label_H, score_H = H.detector, H.labels.astype(float), H.scores
    r_label = boot_corr(det_H, label_H, N_BOOT, BOOT_SEED + 1)
    r_score = boot_corr(det_H, score_H, N_BOOT, BOOT_SEED + 2)
    r_F_formula = {
        "point": -r_label["point"],
        "ci95": [-r_label["ci95"][1], -r_label["ci95"][0]],
        "n": r_label["n"],
    }
    results["human_pool_diagnostics"] = {
        "n_texts": len(H),
        "cor_detector_label_raw_pools_convention": r_label,
        "cor_detector_trait_score_raw_pools_convention": r_score,
        "r_F_hat_population_convention": r_F_formula,
        "note": (
            "r_F_hat_population_convention is what h5_bounds_detected.att_pass's r_F "
            "parameter expects (sign-flipped from the raw pools-convention correlation)."
        ),
    }

    for pool_name in MACHINE_POOLS:
        M = lane3_pool(pool_name, TRAIT, raw, score_version=SCORE_VERSION)
        det_M, label_M, score_M = M.detector, M.labels.astype(float), M.scores
        a3_label = boot_corr(det_M, label_M, N_BOOT, BOOT_SEED + 3)
        a3_score = boot_corr(det_M, score_M, N_BOOT, BOOT_SEED + 4)
        supports_a3 = a3_label["ci95"][0] <= 0.0 <= a3_label["ci95"][1]
        results["machine_pool_diagnostics"][pool_name] = {
            "n_texts": len(M),
            "a3_diag_cor_detector_label": a3_label,
            "cor_detector_trait_score": a3_score,
            "a3_ci_covers_zero": bool(supports_a3),
        }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2) + "\n")

    print("=== Task 1: r_F and A3 diagnostics ===")
    print(f"Human pool ({HUMAN_POOL}, {TRAIT}, n={len(H)}):")
    print(f"  Cor(detector, label) [pools convention, +=machine-like]: "
          f"{r_label['point']:.4f}  95% CI ({r_label['ci95'][0]:.4f}, {r_label['ci95'][1]:.4f})")
    print(f"  Cor(detector, trait score) [pools convention]: "
          f"{r_score['point']:.4f}  95% CI ({r_score['ci95'][0]:.4f}, {r_score['ci95'][1]:.4f})")
    print(f"  => r_F_hat (population/E33 convention, fed to att_pass): "
          f"{r_F_formula['point']:.4f}  95% CI "
          f"({r_F_formula['ci95'][0]:.4f}, {r_F_formula['ci95'][1]:.4f})")
    for pool_name, d in results["machine_pool_diagnostics"].items():
        a3 = d["a3_diag_cor_detector_label"]
        sc = d["cor_detector_trait_score"]
        print(f"Machine pool {pool_name} (n={d['n_texts']}):")
        print(f"  a3_diag = Cor(detector, label): {a3['point']:.4f}  95% CI "
              f"({a3['ci95'][0]:.4f}, {a3['ci95'][1]:.4f})  "
              f"CI covers 0: {d['a3_ci_covers_zero']}")
        print(f"  Cor(detector, trait score): {sc['point']:.4f}  95% CI "
              f"({sc['ci95'][0]:.4f}, {sc['ci95'][1]:.4f})")
    print(f"\nWritten to {OUT}")


if __name__ == "__main__":
    main()
