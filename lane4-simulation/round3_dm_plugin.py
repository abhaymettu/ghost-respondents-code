"""Item 3, second half: is the dm slope DERIVABLE from things a deployment actually holds?

sn_ratio() in round3_dm.py used the full pools as the population, which no deployment has.
But the attenuation only needs S, N_m, N_h, and all three have unbiased plug-ins built from
the two reference histograms the estimator is already given:

    <d,d>_hat = sum_b w_b (p_m - p_h)^2        (computable: it IS the reference pair)
    N_m_hat   = sum_b w_b p_m(1-p_m)/n_M       (multinomial variance of that same histogram)
    N_h_hat   = sum_b w_b p_h(1-p_h)/n_H
    S_hat     = <d,d>_hat - N_m_hat - N_h_hat  (E<d,d> = S + N_m + N_h, so this is unbiased)

giving a slope estimate S_hat/<d,d>_hat and an intercept estimate N_h_hat/<d,d>_hat with no
oracle input at all. This checks the plug-in against the measured slope, and reports what a
plug-in-corrected prevalence would have cost.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inject.pools import lane3_pool, load_lane3
from round3_dm import BINS, hell_terms
from round3_splits import POOLS, TRAITS, split_seeds, split_stats


def plugin(m_ref: np.ndarray, h_ref: np.ndarray, n_bins: int) -> dict:
    t = hell_terms(m_ref, h_ref, len(m_ref), len(h_ref), n_bins)
    dd, sh = t["dd"], t["dd"] - t["N_m"] - t["N_h"]
    return {**t, "S_hat": sh,
            "slope_plug": sh / dd if dd > 0 else float("nan"),
            "intercept_plug": t["N_h"] / dd if dd > 0 else float("nan")}


def main() -> int:
    D = json.loads(Path("results/round3_dm.json").read_text())
    raw = load_lane3()
    cells = [(p, t) for p in POOLS for t in TRAITS]
    print("Plug-in attenuation, built only from the two reference histograms\n")
    print(f"  {'cell':26s} {'bins':>4s} {'slope_obs':>9s} {'plug':>6s} {'oracle':>7s}"
          f" | {'ic_obs':>7s} {'plug':>7s}")
    O, P, Q, IO, IP = [], [], [], [], []
    for ci, (pool, trait) in enumerate(cells):
        H_all, M_all = lane3_pool("pk_human", trait, raw), lane3_pool(pool, trait, raw)
        rec = D["cells"][ci]
        assert (rec["pool"], rec["trait"]) == (pool, trait)
        for si, sseed in enumerate(split_seeds(ci)[:D["splits"]]):
            S = split_stats(H_all, M_all, sseed)
            _, _, MR, HR, _, _ = S["_pools"]
            L = {l["n_bins"]: l for l in rec["splits"][si]["ladder"]}
            for b in BINS:
                pg, l = plugin(MR, HR, b), L[b]
                O.append(l["slope"]); P.append(pg["slope_plug"]); Q.append(l["slope_pred"])
                IO.append(l["intercept"]); IP.append(pg["intercept_plug"])
                if si == 0 and b in (8, 60):
                    print(f"  {pool.split('_')[-1]+'/'+trait:26s} {b:4d} {l['slope']:9.3f}"
                          f" {pg['slope_plug']:6.3f} {l['slope_pred']:7.3f} |"
                          f" {l['intercept']:+7.4f} {pg['intercept_plug']:+7.4f}")
    O, P, Q, IO, IP = map(lambda v: np.array(v, float), (O, P, Q, IO, IP))
    c = lambda a, b: float(np.corrcoef(a, b)[0, 1])
    print(f"\n  over {len(O)} (cell, split, n_bins) points:")
    print(f"    slope_obs vs plug-in  r={c(P,O):+.4f}  OLS {np.polyfit(P,O,1)[0]:.3f}"
          f"  mean(obs-plug)={np.mean(O-P):+.3f}  median|res|={np.median(abs(O-P)):.3f}")
    print(f"    slope_obs vs oracle   r={c(Q,O):+.4f}  OLS {np.polyfit(Q,O,1)[0]:.3f}"
          f"  mean(obs-oracle)={np.mean(O-Q):+.3f}")
    print(f"    plug-in vs oracle     r={c(P,Q):+.4f}  mean(plug-oracle)={np.mean(P-Q):+.3f}")
    print(f"    intercept_obs vs plug r={c(IP,IO):+.4f}  mean(obs-plug)={np.mean(IO-IP):+.4f}")

    neg = int((P < 0).sum())
    print(f"    S_hat < 0 (reference pair cannot resolve the two pools at all): {neg}/{len(P)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
