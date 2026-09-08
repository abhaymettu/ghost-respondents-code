"""Round 3 items 1 and 2: the reference split as the shared random effect.

Item 1 (EIV failure isolation) and item 2 (calibration-split spread) turned out to be one
question. A first probe re-ran gpt-4/EXT -- one of the two cells LAYERB-SWEEP2.md flagged
as an EIV failure at +31% -- under a different reference split and got +1.4%. If the
split, not the cell, carries the failure, then no ranking of (g, c_pool, kappa, delta)
over one split per cell can isolate anything, because every such ranking is confounded
with a single draw of a nuisance variable.

So both items are answered by holding the cell fixed and varying the split:

  TIER 1  closed form, no Monte Carlo, many splits. Everything that is finite-population
          arithmetic over the two halves -- r_H, kappa, delta, c_pool, g, the detector's
          se/sp on each side, the two-term adjusted-count offset of LAYERB-SWEEP.md s5 --
          is recomputed per split. This gives the split-to-split spread at high precision.

  TIER 2  Monte Carlo on a subset of splits, to check the closed form and to run the 2x2
          EIV counterfactual (true pi handed in, oracle reference handed in, crossed).

Nothing here touches dgp.py or the Layer A grid. Single-threaded by construction.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from estimators import _adjusted_count_pi, _distribution_match_pi, _pearson
from inject.build import build_injected_sample, layer_b_moments
from inject.pools import lane3_pool, load_lane3, reference_detector, split_reference
from layerb_pilot import eiv_correct, mcse

POOLS = ("big5_personality_essays", "personallm_gpt-4-0613",
         "personallm_gpt-3.5-turbo-0613", "personallm_llama-2")
TRAITS = ("EXT", "NEU", "AGR", "CON", "OPE")
PIS = (0.10, 0.30)
N = 1000
ARMS = (0.0, 1.0)          # 0 and 1 bracket the coupling; p=0.5 is interior and monotone
RHO_T = 0.5
SPLITS_CF = 400            # tier 1: closed form only
SPLITS_MC = 12             # tier 2: the first SPLITS_MC of the same splits, with Monte Carlo
REPS = 40
SP_TARGET = 0.99
SEED = 20260907 + 94000
SWEEP_SEED = 20260907      # sweep_layerb.py cell seeds are SWEEP_SEED + 1000 * cell_index


def amplification(pi: float, kappa: float, delta: float, gp: float, h: float = 1e-4) -> float:
    """d(eiv_err)/d(pi_hat) at pi_hat = pi, from the closed-form moment chain.

    With V_H = 1 in the human-standardized units, the estimator's attenuation is
        Att_hat * sqrt(var_x) = (1 - pi_hat) * sqrt(V_H_hat) + pi_hat * g_p
    and eiv_err = Att / Att_hat - 1, so sqrt(var_x) cancels and the slope depends only on
    (pi, kappa, delta, g_p). This is the factor that turns a prevalence error into an EIV
    error, and it is what differs between cells that share a g.
    """
    var_x = (1 - pi) + pi * kappa + pi * (1 - pi) * delta ** 2

    def att_hat(pih: float) -> float:
        D = delta * (1 - pi) / (1 - pih)
        V = (var_x - pih * kappa - pih * (1 - pih) * D ** 2) / (1 - pih)
        return float("nan") if V <= 0 else ((1 - pih) * np.sqrt(V) + pih * gp) / np.sqrt(var_x)

    att = ((1 - pi) + pi * gp) / np.sqrt(var_x)
    return float(((att / att_hat(pi + h)) - (att / att_hat(pi - h))) / (2 * h))


def split_seeds(ci: int) -> list[int]:
    """Split 0 IS the split sweep_layerb.py shipped, so every cell's published (g, c_pool,
    kappa, delta) is recoverable as draw 0 of this distribution rather than compared to it."""
    return [SWEEP_SEED + 1000 * ci] + [SEED + 100000 * ci + si for si in range(1, SPLITS_CF)]


def split_stats(H_all, M_all, seed: int) -> dict | None:
    """Everything one reference split determines, with no Monte Carlo at all."""
    rng = np.random.default_rng(seed)
    M_inj, M_ref = split_reference(M_all, rng, frac=0.5)
    H_base, H_ref = split_reference(H_all, rng, frac=0.5)

    mu_h, sd_h = float(H_base.scores.mean()), float(H_base.scores.std(ddof=0))
    if not np.isfinite(sd_h) or sd_h <= 0:
        return None
    q1 = H_base.balance
    xh = (H_base.scores - mu_h) / sd_h
    th = (H_base.labels - q1) / np.sqrt(q1 * (1 - q1))
    r_H = float(np.mean((xh - xh.mean()) * th))

    det_Href = reference_detector(H_all, H_ref)
    det_Mref = reference_detector(M_all, M_ref)
    thr = float(np.quantile(det_Href, SP_TARGET))
    sp_cal = float(np.mean(det_Href <= thr))
    se_cal = float(np.mean(det_Mref > thr))
    sp_base = float(np.mean(H_base.detector <= thr))
    se_inj = float(np.mean(M_inj.detector > thr))

    mom = layer_b_moments(H_base, M_inj, 0.10, 1.0, RHO_T, q1=q1)
    return {
        "seed": seed, "r_H": r_H, "q1": q1,
        "kappa": mom["kappa"], "delta": mom["delta"], "c_pool": mom["c"], "g": mom["g"],
        "thr": thr, "sp_cal": sp_cal, "se_cal": se_cal, "sp_base": sp_base, "se_inj": se_inj,
        "mu_Mref": float(np.mean((M_ref.scores - mu_h) / sd_h)),
        "s2_Mref": float(np.var((M_ref.scores - mu_h) / sd_h, ddof=1)),
        "mu_Minj": float(np.mean((M_inj.scores - mu_h) / sd_h)),
        "s2_Minj": float(np.var((M_inj.scores - mu_h) / sd_h, ddof=1)),
        "_pools": (H_base, M_inj, (M_ref.scores - mu_h) / sd_h, (H_ref.scores - mu_h) / sd_h,
                   xh, (M_inj.scores - mu_h) / sd_h),
    }


def ac_offset_pred(S: dict, pi: float) -> float:
    """LAYERB-SWEEP.md s5 two-term transfer law, as a function of this split's se/sp."""
    denom = S["se_cal"] - (1.0 - S["sp_cal"])
    if denom <= 1e-8:
        return float("nan")
    return (pi * (S["se_inj"] - S["se_cal"])
            + (1 - pi) * ((1 - S["sp_base"]) - (1 - S["sp_cal"]))) / denom


def mc_point(S: dict, pi: float, seed: int) -> dict:
    """Monte Carlo at one (split, pi): the 2x2 EIV counterfactual and the realized offsets."""
    H_base, M_inj, MR, HR, HO, MO = S["_pools"]
    r_H = S["r_H"]
    rho_H_true = RHO_T * r_H
    pred = {p: layer_b_moments(H_base, M_inj, pi, p, RHO_T, q1=S["q1"]) for p in ARMS}

    keys = ("pi_dm", "pi_ac", "rho_obs", "err_00", "err_pi", "err_ref", "err_both")
    res = {p: {k: [] for k in keys} for p in ARMS}
    for r in range(REPS):
        for p in ARMS:
            rng = np.random.default_rng([seed, r, int(p * 100)])
            inj = build_injected_sample(H_base, M_inj, N, pi, p, rng, rho_T=RHO_T,
                                        k_chunks=1, sp=SP_TARGET, replace=True)
            x, w = inj.x_full, inj.sample.w
            ck = p * pred[1.0]["c"]
            d = res[p]
            d["rho_obs"].append(_pearson(x, w))
            d["pi_dm"].append(_distribution_match_pi(x, MR, HR))
            fr = float(np.mean(np.asarray(inj.sample.F) > S["thr"]))
            d["pi_ac"].append(_adjusted_count_pi(fr, S["se_cal"], S["sp_cal"])[0])
            for k, (mr, hr, pf) in {
                "err_00":   (MR, HR, None), "err_pi":   (MR, HR, pi),
                "err_ref":  (MO, HO, None), "err_both": (MO, HO, pi),
            }.items():
                e = eiv_correct(x, w, mr, hr, r_H, c_known=ck, pi_fixed=pf)
                d[k].append(e["rho_H_hat"] / rho_H_true - 1.0)

    A = {p: {k: np.array(v, float) for k, v in d.items()} for p, d in res.items()}
    m = lambda p, k: float(np.nanmean(A[p][k]))
    out = {"pi": pi,
           "Att_real": {str(p): m(p, "rho_obs") / rho_H_true for p in ARMS},
           "Att_pred": {str(p): pred[p]["Att"] for p in ARMS},
           "pi_dm_bias": m(0.0, "pi_dm") - pi,
           "pi_ac_bias": m(0.0, "pi_ac") - pi,
           "pi_ac_mcse": mcse(A[0.0]["pi_ac"]),
           "pi_dm_mcse": mcse(A[0.0]["pi_dm"])}
    for k in ("err_00", "err_pi", "err_ref", "err_both"):
        out[k] = {str(p): m(p, k) for p in ARMS}
        out[k + "_mcse"] = {str(p): mcse(A[p][k]) for p in ARMS}
    out["amp"] = {str(p): amplification(pi, S["kappa"], S["delta"], p * S["g"]) for p in ARMS}
    return out


def main() -> int:
    raw = load_lane3()
    cells = [(p, t) for p in POOLS for t in TRAITS]
    print(f"Round 3 items 1+2: {len(cells)} cells x {SPLITS_CF} splits (closed form), "
          f"first {SPLITS_MC} with Monte Carlo")
    print(f"pi={PIS} n={N} p in {ARMS} reps={REPS} rho_T={RHO_T} k=1 replace=True\n")

    out_cells, t0 = [], time.perf_counter()
    for ci, (pool, trait) in enumerate(cells):
        H_all = lane3_pool("pk_human", trait, raw)
        M_all = lane3_pool(pool, trait, raw)
        cf, mc = [], []
        for si, sseed in enumerate(split_seeds(ci)):
            S = split_stats(H_all, M_all, sseed)
            if S is None:
                continue
            rec = {k: v for k, v in S.items() if k != "_pools"}
            rec["ac_pred"] = {str(pi): ac_offset_pred(S, pi) for pi in PIS}
            cf.append(rec)
            if si < SPLITS_MC:
                for pi in PIS:
                    mc.append({"split": si, "is_sweep_split": si == 0,
                               **mc_point(S, pi, SEED + 100000 * ci + 7 * si)})
        out_cells.append({"pool": pool, "trait": trait, "n_human": len(H_all),
                          "n_machine": len(M_all), "splits": cf, "mc": mc})
        gs = [c["g"] for c in cf]
        e1 = [r["err_00"]["1.0"] for r in mc if r["pi"] == 0.10]
        print(f"  [{ci+1:2d}/{len(cells)}] {pool.split('_')[-1]:18s} {trait} "
              f"g={np.mean(gs):+.3f}+-{np.std(gs):.3f}  "
              f"err_00(pi=.10,p=1) {min(e1):+.1%}..{max(e1):+.1%}  "
              f"({time.perf_counter()-t0:.0f}s)", flush=True)

    out = {"pis": PIS, "n": N, "arms": ARMS, "reps": REPS, "splits_cf": SPLITS_CF,
           "splits_mc": SPLITS_MC, "cells": out_cells, "seconds": time.perf_counter() - t0}
    Path("results").mkdir(exist_ok=True)
    Path("results/round3_splits.json").write_text(json.dumps(out, indent=2))
    print(f"\n-> results/round3_splits.json ({out['seconds']:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
