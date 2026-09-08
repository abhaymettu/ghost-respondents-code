"""Round 3 item 3: why the distribution-match slope is 0.31-0.48 in 5 cells and 0.935 in one.

The estimator minimises Hellinger distance between the observed histogram and a two-component
mixture of two REFERENCE histograms. Linearise it. Write D = p_M - p_H for the population
separation, e_m and e_h for the sampling error in the two reference histograms, and take the
inner product the Hellinger metric induces, <a,b> = sum_b a_b b_b / (4 q_b). The minimiser is
a weighted regression of (p_obs - p_h) on (p_m - p_h), so with S = <D,D>, N_m = E|e_m|^2 and
N_h = E|e_h|^2,

    E[pi_hat]  ~=  pi * S/(S + N_m + N_h)  +  N_h/(S + N_m + N_h)

which is the classical errors-in-variables attenuation, and it predicts BOTH observed
features at once: a slope below 1, and a POSITIVE intercept, because human-reference
sampling noise is absorbed into the machine component. The compression is therefore not a
property of the method but of the reference's bin-level noise relative to the separation.

That yields a falsifiable knob. N scales with the number of occupied bins; S saturates once
the bins resolve the separation. So the slope must RISE as n_bins falls -- until the bins are
too coarse to resolve D at all, at which point S collapses and the slope falls again. A cell
with a large separation (llama-2/OPE: delta -1.618, kappa 1.273) has S >> N already at the
default 60 bins and should show no compression. This runs that ladder.

Nothing here touches dgp.py or the Layer A grid. Single-threaded by construction.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from estimators import _distribution_match_pi
from inject.build import build_injected_sample
from inject.pools import lane3_pool, load_lane3
from round3_splits import POOLS, TRAITS, split_seeds, split_stats

PIS = (0.02, 0.05, 0.10, 0.20, 0.30)
BINS = (8, 15, 30, 60, 120)
N = 1000
RHO_T = 0.5
REPS = 60
SPLITS = 2                 # split 0 is sweep_layerb.py's own split
SP_TARGET = 0.99
SEED = 20260907 + 95000


def hell_terms(m, h, n_m: int, n_h: int, n_bins: int) -> dict:
    """<d,d>, N_m, N_h in the Hellinger-induced metric, over a common binning of m and h.

    The metric weight is 1/(4 q_b) with q_b the pooled bin mass, which keeps empty bins finite;
    the exact estimator re-derives its edges per replicate, so these edges are the pooled range.
    N_m/N_h are the multinomial variances of histograms built from n_m/n_h draws.
    """
    edges = np.linspace(float(min(m.min(), h.min())), float(max(m.max(), h.max())), n_bins + 1)
    pm = np.histogram(m, bins=edges)[0] / len(m)
    ph = np.histogram(h, bins=edges)[0] / len(h)
    q = (pm + ph) / 2.0
    w = np.where(q > 0, 1.0 / (4.0 * np.maximum(q, 1e-12)), 0.0)
    return {"dd": float(np.sum(w * (pm - ph) ** 2)),
            "N_m": float(np.sum(w * pm * (1 - pm)) / n_m),
            "N_h": float(np.sum(w * ph * (1 - ph)) / n_h),
            "occupied": int((q > 0).sum())}


def sn_ratio(m_ref, h_ref, m_pop, h_pop, n_bins: int) -> dict:
    """The oracle version: S is the separation of the FULL pools the reference halves came from."""
    t = hell_terms(m_pop, h_pop, len(m_ref), len(h_ref), n_bins)
    tot = t["dd"] + t["N_m"] + t["N_h"]
    return {"n_bins": n_bins, "S": t["dd"], "N_m": t["N_m"], "N_h": t["N_h"],
            "occupied": t["occupied"],
            "slope_pred": t["dd"] / tot if tot > 0 else float("nan"),
            "intercept_pred": t["N_h"] / tot if tot > 0 else float("nan")}


def run_split(H_all, M_all, sseed: int, seed: int) -> dict:
    S = split_stats(H_all, M_all, sseed)
    H_base, M_inj, MR, HR, _, _ = S["_pools"]
    mu_h, sd_h = float(H_base.scores.mean()), float(H_base.scores.std(ddof=0))
    m_pop = (M_all.scores - mu_h) / sd_h    # the population MR is a draw from
    h_pop = (H_all.scores - mu_h) / sd_h
    means = {b: {pi: [] for pi in PIS} for b in BINS}
    for pi in PIS:
        for r in range(REPS):
            rng = np.random.default_rng([seed, int(pi * 1000), r])
            inj = build_injected_sample(H_base, M_inj, N, pi, 0.0, rng, rho_T=RHO_T,
                                        k_chunks=1, sp=SP_TARGET, replace=True)
            x = inj.x_full
            for b in BINS:
                means[b][pi].append(_distribution_match_pi(x, MR, HR, n_bins=b))

    pis = np.array(PIS, float)
    out = {"seed": sseed, "kappa": S["kappa"], "delta": S["delta"], "g": S["g"],
            "r_H": S["r_H"], "c_pool": S["c_pool"],
            "n_Mref": int(len(MR)), "n_Href": int(len(HR)), "ladder": []}
    for b in BINS:
        mu = np.array([float(np.nanmean(means[b][pi])) for pi in PIS])
        sd = np.array([float(np.nanstd(means[b][pi], ddof=1) / np.sqrt(REPS)) for pi in PIS])
        slope, icept = np.polyfit(pis, mu, 1)
        th = sn_ratio(MR, HR, m_pop, h_pop, b)
        out["ladder"].append({**th, "slope": float(slope), "intercept": float(icept),
                              "pi_hat": mu.tolist(), "pi_hat_mcse": sd.tolist()})
    return out


def main() -> int:
    raw = load_lane3()
    cells = [(p, t) for p in POOLS for t in TRAITS]
    print(f"Round 3 item 3: dm-slope diagnosis, {len(cells)} cells x {SPLITS} splits")
    print(f"pi={PIS} n_bins ladder={BINS} n={N} p=0.0 reps={REPS}\n")
    rows, t0 = [], time.perf_counter()
    for ci, (pool, trait) in enumerate(cells):
        H_all = lane3_pool("pk_human", trait, raw)
        M_all = lane3_pool(pool, trait, raw)
        splits = [run_split(H_all, M_all, ss, SEED + 100000 * ci + si)
                  for si, ss in enumerate(split_seeds(ci)[:SPLITS])]
        rows.append({"pool": pool, "trait": trait, "splits": splits})
        d = {l["n_bins"]: l for l in splits[0]["ladder"]}
        print(f"  [{ci+1:2d}/{len(cells)}] {pool.split('_')[-1]:18s} {trait} "
              f"slope@60={d[60]['slope']:.3f} (pred {d[60]['slope_pred']:.3f})  "
              f"slope@8={d[8]['slope']:.3f} (pred {d[8]['slope_pred']:.3f})  "
              f"({time.perf_counter()-t0:.0f}s)", flush=True)
    out = {"pis": PIS, "bins": BINS, "n": N, "reps": REPS, "splits": SPLITS,
           "cells": rows, "seconds": time.perf_counter() - t0}
    Path("results").mkdir(exist_ok=True)
    Path("results/round3_dm.json").write_text(json.dumps(out, indent=2))
    print(f"\n-> results/round3_dm.json ({out['seconds']:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
