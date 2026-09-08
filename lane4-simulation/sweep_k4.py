"""Layer B multi-item arms at k_chunks=4, unblocked by lane 3's CHUNKS-DONE pass.

LAYERB-SWEEP.md section 7 said the multi-item arms were blocked on lane 3. They are not:
lane3-testbed/data/scores/pk_human.json carries chunk_1..chunk_4 (2421 of 2467 non-null)
plus chunk_meta, and inject/pools.lane3_pool already reads them generically. This script
runs the arms that dependency was blocking.

The question is weak-H2 (memo 3.4): with k parallel pseudo-items, rel_H is identified, so
rho_T = rho_H / sqrt(rel_H) should be recoverable. This scores that claim against the two
things it could mean and reports both.

Nothing here touches dgp.py or the Layer A grid. Single-threaded by construction.
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import replace
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from estimators import _between_item_corr, _pearson  # SPEC 3.2 code, not a re-write
from inject.build import build_injected_sample, layer_b_moments
from inject.pools import Pool, lane3_pool, load_lane3, split_reference
from layerb_pilot import mcse

N = 1000
PI = 0.10
RHO_T = 0.5
K = 4
REPS = 400
ARMS = (0.0, 0.5, 1.0)
SEED = 20260907 + 77000
HUMAN_BASELINE_EXT = 0.2083  # lane 1's PK EXT between-chunk r, the number this must reproduce

# Six cells, not twenty. EXT on all four pools because EXT is the only trait with an
# external between-chunk number to check against (lane 1's 0.2083); plus the two extremes
# LAYERB-SWEEP.md section 1 identified -- gpt-3.5/AGR (largest g, 2.882; largest Att swing,
# 0.902 -> 1.191) and llama-2/OPE (largest c_pool, 0.5048; largest kappa, 1.273). Together
# they bracket g from +0.497 to +2.882, which is the full sweep's positive range.
CELLS = [
    ("big5_personality_essays", "EXT"),
    ("personallm_gpt-4-0613", "EXT"),
    ("personallm_gpt-3.5-turbo-0613", "EXT"),
    ("personallm_llama-2", "EXT"),
    ("personallm_gpt-3.5-turbo-0613", "AGR"),
    ("personallm_llama-2", "OPE"),
]

_FAILURES: list[str] = []
_CHECKS = 0


def check(name: str, ok: bool, detail: str = "") -> bool:
    global _CHECKS
    _CHECKS += 1
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else ""))
    if not ok:
        _FAILURES.append(name)
    return ok


def chunkable(pool: Pool, k: int) -> tuple[Pool, int]:
    """Restrict to texts lane 3 could split into k chunks.

    build._chunks_or_none refuses an index set containing ANY unchunkable text, so a draw
    that touches one degrades the whole matrix to None and build raises. Filtering up front
    is the only way to run k>1 on a pool lane 3 could not chunk completely. The dropped
    fraction is reported per cell and is a disclosure, not a free move.
    """
    keep = [t for t in pool.texts if len(t.chunk_scores) == k]
    return replace(pool, texts=keep), len(pool.texts) - len(keep)


def r_point_biserial(scores: np.ndarray, labels: np.ndarray) -> float:
    """Cor(score, standardized label) -- the same r_H the k=1 sweep reports."""
    q1 = float(labels.mean())
    th = (labels - q1) / np.sqrt(q1 * (1 - q1))
    s = (scores - scores.mean()) / scores.std(ddof=0)
    return float(np.mean(s * th))


def run_cell(pool_name: str, trait: str, raw: dict, cell_seed: int) -> dict:
    t0 = time.perf_counter()
    H_all, drop_h = chunkable(lane3_pool("pk_human", trait, raw), K)
    M_all, drop_m = chunkable(lane3_pool(pool_name, trait, raw), K)

    rng0 = np.random.default_rng(cell_seed)
    M_inj, _M_ref = split_reference(M_all, rng0, frac=0.5)
    H_base, _H_ref = split_reference(H_all, rng0, frac=0.5)

    mu_h, sd_h = float(H_base.scores.mean()), float(H_base.scores.std(ddof=0))
    q1 = H_base.balance

    # --- the two candidate headline indicators, on the same human base -------------------
    r_H_whole = r_point_biserial(H_base.scores, H_base.labels)
    CH = np.array([t.chunk_scores for t in H_base.texts], dtype=float)   # (n_H, 4)
    r_H_chunk = r_point_biserial(CH[:, 0], H_base.labels)
    rbar_H = _between_item_corr(CH)                                       # weak-H2's rel_hat
    rel_sb = K * rbar_H / (1.0 + (K - 1) * rbar_H)                        # Spearman-Brown
    # Layer A's rel_H is defined by x = sqrt(rel_H) theta + noise, so on this design the
    # TRUE rel_H of an indicator is its squared label validity. That is the number the
    # between-chunk correlation has to match for weak-H2 to identify rho_T.
    rel_true_whole = r_H_whole ** 2
    rel_true_chunk = r_H_chunk ** 2

    rho_H_true_whole = RHO_T * r_H_whole
    rho_H_true_chunk = RHO_T * r_H_chunk
    pred = {p: layer_b_moments(H_base, M_inj, PI, p, RHO_T, q1=q1) for p in ARMS}

    keys = ("rho_whole", "rho_chunk1", "rbar", "rel_sb_rep",
            "rho_T_naive", "rho_T_sb", "rho_T_oracle", "rho_T_chunk_naive")
    # pi=0 clean control. The oracle correction has to return rho_T on an UNCONTAMINATED
    # sample; scoring it at p=0 conflates the reliability question with Att(0) < 1, which
    # is contamination and is what the rest of the sweep already measures.
    clean = {k: [] for k in keys}
    for r in range(REPS):
        rng = np.random.default_rng([cell_seed, r, 999])
        s0 = build_injected_sample(H_base, M_inj, N, 0.0, 0.0, rng,
                                   rho_T=RHO_T, k_chunks=K)
        w0, X0 = s0.sample.w, s0.sample.X
        rb0 = _between_item_corr(X0)
        sb0 = K * rb0 / (1.0 + (K - 1) * rb0)
        rw0 = _pearson(s0.x_full, w0)
        r10 = _pearson(X0[:, 0], w0)
        clean["rho_whole"].append(rw0); clean["rho_chunk1"].append(r10)
        clean["rbar"].append(rb0); clean["rel_sb_rep"].append(sb0)
        clean["rho_T_naive"].append(rw0 / np.sqrt(rb0))
        clean["rho_T_sb"].append(rw0 / np.sqrt(sb0))
        clean["rho_T_chunk_naive"].append(r10 / np.sqrt(rb0))
        clean["rho_T_oracle"].append(rw0 / abs(r_H_whole))
    C = {k: np.array(v, float) for k, v in clean.items()}
    cmean = lambda k: float(np.nanmean(C[k]))

    res = {p: {k: [] for k in keys} for p in ARMS}
    for r in range(REPS):
        for p in ARMS:
            rng = np.random.default_rng([cell_seed, r, int(p * 100)])
            inj = build_injected_sample(H_base, M_inj, N, PI, p, rng,
                                        rho_T=RHO_T, k_chunks=K)
            s = inj.sample
            w, X = s.w, s.X
            d = res[p]
            rho_w = _pearson(inj.x_full, w)      # whole-text headline, comparable to k=1
            rho_1 = _pearson(X[:, 0], w)         # Sample.x: chunk 1 as a parallel item
            rb = _between_item_corr(X)
            sb = K * rb / (1.0 + (K - 1) * rb) if np.isfinite(rb) and rb > -1 / (K - 1) else np.nan
            d["rho_whole"].append(rho_w)
            d["rho_chunk1"].append(rho_1)
            d["rbar"].append(rb)
            d["rel_sb_rep"].append(sb)
            # weak-H2 as estimators._naive_style_fit does it: divide by sqrt(mean inter-item r)
            d["rho_T_naive"].append(rho_w / np.sqrt(rb) if rb > 0 else np.nan)
            d["rho_T_sb"].append(rho_w / np.sqrt(sb) if sb > 0 else np.nan)
            # the same correction applied to the indicator it is actually valid for
            d["rho_T_chunk_naive"].append(rho_1 / np.sqrt(rb) if rb > 0 else np.nan)
            # what the correction would give with the TRUE rel_H (r_H^2): must return rho_T
            d["rho_T_oracle"].append(rho_w / abs(r_H_whole))

    A = {p: {k: np.array(v, float) for k, v in d.items()} for p, d in res.items()}
    mean = lambda p, k: float(np.nanmean(A[p][k]))

    return {
        "pool": pool_name, "trait": trait, "seed": cell_seed,
        "n_human": len(H_all.texts), "n_machine": len(M_all.texts),
        "dropped_unchunkable_human": drop_h, "dropped_unchunkable_machine": drop_m,
        "r_H_whole": r_H_whole, "r_H_chunk1": r_H_chunk,
        "rbar_H_pool": rbar_H, "rel_sb_pool": rel_sb,
        "rel_true_whole": rel_true_whole, "rel_true_chunk": rel_true_chunk,
        "ratio_rbar_over_rel_true_whole": rbar_H / rel_true_whole,
        "ratio_rbar_over_rel_true_chunk": rbar_H / rel_true_chunk,
        "rho_H_true_whole": rho_H_true_whole, "rho_H_true_chunk": rho_H_true_chunk,
        "clean": {
            "rho_whole": cmean("rho_whole"), "rho_chunk1": cmean("rho_chunk1"),
            "rbar": cmean("rbar"), "rel_sb": cmean("rel_sb_rep"),
            "rho_T_oracle": cmean("rho_T_oracle"),
            "err_oracle": cmean("rho_T_oracle") / RHO_T - 1.0,
            "z_oracle": (cmean("rho_T_oracle") - RHO_T) / mcse(C["rho_T_oracle"]),
            "rho_T_naive": cmean("rho_T_naive"),
            "err_naive": cmean("rho_T_naive") / RHO_T - 1.0,
            "rho_T_sb": cmean("rho_T_sb"),
            "err_sb": cmean("rho_T_sb") / RHO_T - 1.0,
            "rho_T_chunk_naive": cmean("rho_T_chunk_naive"),
            "err_chunk_naive": cmean("rho_T_chunk_naive") / RHO_T - 1.0,
        },
        "arms": {
            str(p): {
                "rho_whole": mean(p, "rho_whole"),
                "rho_whole_mcse": mcse(A[p]["rho_whole"]),
                "rho_whole_pred": pred[p]["rho_obs_pred"],
                "rho_chunk1": mean(p, "rho_chunk1"),
                "rbar": mean(p, "rbar"), "rbar_mcse": mcse(A[p]["rbar"]),
                "rel_sb": mean(p, "rel_sb_rep"),
                "rho_T_naive": mean(p, "rho_T_naive"),
                "rho_T_sb": mean(p, "rho_T_sb"),
                "rho_T_chunk_naive": mean(p, "rho_T_chunk_naive"),
                "rho_T_oracle": mean(p, "rho_T_oracle"),
                "err_naive": mean(p, "rho_T_naive") / RHO_T - 1.0,
                "err_sb": mean(p, "rho_T_sb") / RHO_T - 1.0,
                "err_chunk_naive": mean(p, "rho_T_chunk_naive") / (RHO_T) - 1.0,
                "err_oracle": mean(p, "rho_T_oracle") / RHO_T - 1.0,
            } for p in ARMS
        },
        "seconds": time.perf_counter() - t0,
    }


def main() -> int:
    raw = load_lane3()
    print(f"Layer B multi-item arms: k_chunks={K}, {len(CELLS)} cells")
    print(f"cell: n={N} pi={PI} p in {ARMS} reps={REPS} rho_T={RHO_T} k={K}\n")
    rows, t0 = [], time.perf_counter()
    for i, (pool, trait) in enumerate(CELLS):
        row = run_cell(pool, trait, raw, SEED + 1000 * i)
        rows.append(row)
        a1 = row["arms"]["1.0"]
        print(f"  [{i+1}/{len(CELLS)}] {pool:30s} {trait} "
              f"r_H={row['r_H_whole']:+.4f} r_H(ch1)={row['r_H_chunk1']:+.4f} "
              f"rbar={row['rbar_H_pool']:.4f} rel_true={row['rel_true_whole']:.4f} "
              f"ratio={row['ratio_rbar_over_rel_true_whole']:.1f}x "
              f"rho_T_naive(p=1)={a1['rho_T_naive']:.4f} "
              f"({row['seconds']:.0f}s, {time.perf_counter()-t0:.0f}s total)", flush=True)
    out = {"k": K, "n": N, "pi": PI, "reps": REPS, "rho_T": RHO_T,
           "human_baseline_ext": HUMAN_BASELINE_EXT,
           "cells": rows, "seconds": time.perf_counter() - t0}
    Path("results").mkdir(exist_ok=True)
    Path("results/layerb_k4.json").write_text(json.dumps(out, indent=2))
    print(f"\n-> results/layerb_k4.json ({out['seconds']:.0f}s)\n")
    report(rows, raw)
    return 0 if not _FAILURES else 1


def _full_pool_rbar(raw: dict) -> float:
    """Lane 1's Q14 number, recomputed here: mean pairwise r of the 4 cEXT chunk scores
    over every pk_human text that could be split into 4 chunks."""
    H, _ = chunkable(lane3_pool("pk_human", "EXT", raw), K)
    return _between_item_corr(np.array([t.chunk_scores for t in H.texts], dtype=float))


def report(rows: list[dict], raw_for_report: dict) -> None:
    col = lambda k: [r[k] for r in rows]
    ext = [r for r in rows if r["trait"] == "EXT"]

    print("\n=== the dependency is real: chunks load and reproduce lane 1 ===")
    # Scored on the FULL pk_human pool, which is what lane 1's 0.2083 was computed on.
    # The per-cell rbar_H_pool values are split halves (n ~ 1210) and carry their own noise;
    # they are reported for context, not scored against a full-pool number.
    full = _full_pool_rbar(raw_for_report)
    check("pk_human EXT between-chunk r reproduces lane 1's 0.2083 exactly",
          abs(full - HUMAN_BASELINE_EXT) < 5e-4,
          f"full pool n=2421: {full:.4f} vs lane 1 {HUMAN_BASELINE_EXT}; "
          f"the six split halves give {min(r['rbar_H_pool'] for r in ext):.4f}-"
          f"{max(r['rbar_H_pool'] for r in rows):.4f}")
    check("every cell built at k=4 with no unchunkable text in any draw",
          all(np.isfinite(r["arms"]["1.0"]["rbar"]) for r in rows),
          f"dropped {max(col('dropped_unchunkable_human'))} human / "
          f"{max(col('dropped_unchunkable_machine'))} machine texts up front")
    check("rbar is stable across coupling arms (chunks are a property of the text, not p)",
          all(abs(r["arms"]["1.0"]["rbar"] - r["arms"]["0.0"]["rbar"]) < 0.05 for r in rows),
          f"max |rbar(1) - rbar(0)| = "
          f"{max(abs(r['arms']['1.0']['rbar'] - r['arms']['0.0']['rbar']) for r in rows):.4f}")

    print("\n=== the oracle control: the correction itself is not broken ===")
    worst_or = max(abs(r["clean"]["err_oracle"]) for r in rows)
    zor = max(abs(r["clean"]["z_oracle"]) for r in rows)
    # same 4-MCSE discipline the k=1 sweep scores every realized moment against
    check("on a CLEAN sample (pi=0), dividing rho_H by the true sqrt(rel_H) = |r_H| "
          "returns rho_T within 4 MCSE", zor < 4.0,
          f"max |z| = {zor:.2f} over {len(rows)} cells (max |err| = {worst_or:.1%}, "
          "bootstrap finite-sample)")

    print("\n=== lane 3 defect: chunk scores are not cross-fitted ===")
    worst_ratio = max(r["r_H_chunk1"] / r["r_H_whole"] for r in rows)
    check("a quarter-text chunk is no MORE valid against the label than the whole text",
          worst_ratio <= 1.0,
          f"r(chunk1, label) / r(whole, label) spans "
          f"{min(r['r_H_chunk1'] / r['r_H_whole'] for r in rows):.2f}x to {worst_ratio:.2f}x; "
          "whole-text scores are 5-fold cross-fitted, chunk scores come from ridge models "
          "REFIT on all texts (POOL-MEASUREMENTS.md 'a refit, not a reload') and applied to "
          "chunks of their own training texts -- in-sample")

    print("\n=== weak-H2: does between-chunk consistency identify rel_H? ===")
    rat_w = col("ratio_rbar_over_rel_true_whole")
    rat_c = col("ratio_rbar_over_rel_true_chunk")
    check("between-chunk r equals the true rel_H (r_H^2) within a factor of 2",
          all(0.5 <= x <= 2.0 for x in rat_w),
          f"ratio rbar / r_H^2 spans {min(rat_w):.1f}x to {max(rat_w):.1f}x "
          f"(chunk-1 indicator: {min(rat_c):.1f}x to {max(rat_c):.1f}x)")
    e_naive = [r["clean"]["err_naive"] for r in rows]
    e_sb = [r["clean"]["err_sb"] for r in rows]
    e_ch = [r["clean"]["err_chunk_naive"] for r in rows]
    check("chunk-disattenuated rho_T recovers rho_T=0.5 within 25% on a clean sample (naive rbar)",
          all(abs(x) <= 0.25 for x in e_naive),
          f"err spans {min(e_naive):+.1%} to {max(e_naive):+.1%}")
    check("chunk-disattenuated rho_T recovers rho_T=0.5 within 25% on a clean sample (Spearman-Brown)",
          all(abs(x) <= 0.25 for x in e_sb),
          f"err spans {min(e_sb):+.1%} to {max(e_sb):+.1%}")
    check("the same correction on the indicator it is valid for (chunk 1) recovers rho_T",
          all(abs(x) <= 0.25 for x in e_ch),
          f"err spans {min(e_ch):+.1%} to {max(e_ch):+.1%}")

    print("\n=== contamination on top of the multi-item route ===")
    for r in rows:
        d = r["arms"]["1.0"]["err_naive"] - r["arms"]["0.0"]["err_naive"]
        r["_coupling_shift"] = d
    sh = [r["_coupling_shift"] for r in rows]
    check("coupling moves the multi-item rho_T error, so k=4 does not immunize against pi",
          max(abs(x) for x in sh) > 0.01,
          f"p=0 -> p=1 shift spans {min(sh):+.1%} to {max(sh):+.1%}")

    print(f"\n{_CHECKS - len(_FAILURES)}/{_CHECKS} checks passed")
    if _FAILURES:
        print("FAILED: " + ", ".join(_FAILURES))


if __name__ == "__main__":
    raise SystemExit(main())
