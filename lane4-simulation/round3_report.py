"""Round 3 analysis: reads results/round3_splits.json and results/round3_dm.json, prints the
numbers LAYERB-ROUND3.md quotes. No simulation here, so it is cheap to re-run."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def load(p):
    f = Path(p)
    return json.loads(f.read_text()) if f.exists() else None


def corr(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 3:
        return float("nan")
    return float(np.corrcoef(a[ok], b[ok])[0, 1])


def _rank(v):
    v = np.asarray(v, float)
    order = np.argsort(np.argsort(v))
    return order.astype(float)


name = lambda c: f"{c['pool'].split('_')[-1]}/{c['trait']}"


def sec(t):
    print(f"\n{'='*86}\n{t}\n{'='*86}")


# ------------------------------------------------------------------ item 1
def item1(D):
    cells = D["cells"]
    FAIL = {"gpt-4-0613/EXT", "gpt-3.5-turbo-0613/AGR"}
    REF = "llama-2/OPE"

    sec("ITEM 1a  the published ranking, reproduced on the sweep's own split (split 0)")
    print("Every cell at its shipped calibration split, err_00 = EIV error with the deployable")
    print("reference and the deployable prevalence estimate. pi=0.10 and 0.30, p=1.\n")
    print(f"  {'cell':26s} {'g':>7s} {'c_pool':>7s} {'kappa':>6s} {'delta':>7s}"
          f" {'err@.10':>8s} {'err@.30':>8s}")
    rows = []
    for c in cells:
        s0 = c["splits"][0]
        mc = {r["pi"]: r for r in c["mc"] if r["split"] == 0}
        if not mc:
            continue
        e10, e30 = mc[0.10]["err_00"]["1.0"], mc[0.30]["err_00"]["1.0"]
        rows.append({"name": name(c), "g": s0["g"], "c": s0["c_pool"], "k": s0["kappa"],
                     "d": s0["delta"], "e10": e10, "e30": e30})
    for r in sorted(rows, key=lambda r: -abs(r["e30"])):
        mark = " <-FAIL" if r["name"] in FAIL else (" <-REF" if r["name"] == REF else "")
        print(f"  {r['name']:26s} {r['g']:+7.3f} {r['c']:+7.3f} {r['k']:6.3f} {r['d']:+7.3f}"
              f" {r['e10']:+7.1%} {r['e30']:+7.1%}{mark}")

    print("\n  |err@0.30| against each candidate, over all 20 cells (Pearson / Spearman):")
    y = [abs(r["e30"]) for r in rows]
    for lab, x in [("g", [r["g"] for r in rows]), ("|g|", [abs(r["g"]) for r in rows]),
                   ("c_pool", [r["c"] for r in rows]), ("kappa", [r["k"] for r in rows]),
                   ("delta", [r["d"] for r in rows]), ("|delta|", [abs(r["d"]) for r in rows]),
                   ("g*kappa", [r["g"] * r["k"] for r in rows]),
                   ("g*|delta|", [r["g"] * abs(r["d"]) for r in rows]),
                   ("(g-1)", [r["g"] - 1 for r in rows]),
                   ("|g-1|", [abs(r["g"] - 1) for r in rows])]:
        print(f"    {lab:12s} r={corr(x, y):+.3f}   rho={corr(_rank(x), _rank(y)):+.3f}")

    sec("ITEM 1b  the same cells, holding the cell fixed and re-drawing the split")
    print("The ranking above is one draw of the calibration split per cell. Re-draw it.\n")
    print(f"  {'cell':26s} {'split0':>8s} {'mean':>8s} {'sd':>7s} {'min':>8s} {'max':>8s}"
          f" {'sd_mc':>7s} {'sd_split':>8s}")
    spread = []
    for c in cells:
        e = [(r["split"], r["err_00"]["1.0"], r["err_00_mcse"]["1.0"])
             for r in c["mc"] if r["pi"] == 0.30]
        if not e:
            continue
        v = np.array([x[1] for x in e], float)
        mcse = float(np.sqrt(np.mean(np.array([x[2] for x in e], float) ** 2)))
        s0 = [x[1] for x in e if x[0] == 0][0]
        tot = float(np.std(v, ddof=1))
        pure = float(np.sqrt(max(tot ** 2 - mcse ** 2, 0.0)))
        spread.append({"name": name(c), "s0": s0, "mu": float(v.mean()), "sd": tot,
                       "lo": float(v.min()), "hi": float(v.max()), "mcse": mcse, "pure": pure})
    for r in sorted(spread, key=lambda r: -abs(r["s0"])):
        mark = " <-FAIL" if r["name"] in FAIL else (" <-REF" if r["name"] == REF else "")
        print(f"  {r['name']:26s} {r['s0']:+7.1%} {r['mu']:+7.1%} {r['sd']:6.1%}"
              f" {r['lo']:+7.1%} {r['hi']:+7.1%} {r['mcse']:6.1%} {r['pure']:7.1%}{mark}")

    b = float(np.std([r["mu"] for r in spread], ddof=1))
    w = float(np.sqrt(np.mean([r["pure"] ** 2 for r in spread])))
    print(f"\n  between-cell sd of the split-averaged error : {b:.1%}")
    print(f"  within-cell sd across splits (MC-corrected) : {w:.1%}")
    print(f"  variance share that is the cell, not the split: {b**2/(b**2+w**2):.1%}")

    print("\n  overlap of the two flagged cells with llama-2/OPE, over the split distribution:")
    byname = {r["name"]: r for r in spread}
    for f in sorted(FAIL):
        if f in byname and REF in byname:
            a, o = byname[f], byname[REF]
            print(f"    {f:26s} [{a['lo']:+.1%},{a['hi']:+.1%}]  vs  "
                  f"{REF} [{o['lo']:+.1%},{o['hi']:+.1%}]  "
                  f"gap in means = {a['mu']-o['mu']:+.1%} = {abs(a['mu']-o['mu'])/max(w,1e-9):.2f} within-sd")

    sec("ITEM 1d  the prompt's ranking, done against split-AVERAGED quantities")
    print("Same four candidates, but both sides averaged over the 12 MC splits, so neither the")
    print("error nor the moment is one draw of the nuisance variable.\n")
    R = []
    for c in cells:
        rs = [r for r in c["mc"] if r["pi"] == 0.30]
        if not rs:
            continue
        S = c["splits"][:len(set(r["split"] for r in c["mc"]))]
        R.append({"name": name(c),
                  "e": float(np.mean([abs(r["err_00"]["1.0"]) for r in rs])),
                  "amp": float(np.mean([abs(r["amp"]["1.0"]) for r in rs])),
                  "dmb": float(np.mean([abs(r["pi_dm_bias"]) for r in rs])),
                  "g": float(np.mean([x["g"] for x in S])),
                  "c": float(np.mean([x["c_pool"] for x in S])),
                  "k": float(np.mean([x["kappa"] for x in S])),
                  "d": float(np.mean([x["delta"] for x in S])),
                  "rH": float(np.mean([x["r_H"] for x in S]))})
    y = [r["e"] for r in R]
    for lab, x in [("g", [r["g"] for r in R]), ("|g-1|", [abs(r["g"]-1) for r in R]),
                   ("c_pool", [r["c"] for r in R]), ("kappa", [r["k"] for r in R]),
                   ("|delta|", [abs(r["d"]) for r in R]), ("r_H", [r["rH"] for r in R]),
                   ("1/r_H", [1/r["rH"] for r in R]),
                   ("amplification |d err/d pi|", [r["amp"] for r in R]),
                   ("|dm prevalence bias|", [r["dmb"] for r in R]),
                   ("amp * |dm bias|", [r["amp"]*r["dmb"] for r in R])]:
        print(f"    {lab:28s} r={corr(x, y):+.3f}   rho={corr(_rank(x), _rank(y)):+.3f}")

    sec("ITEM 1c  the 2x2: which of the estimator's two unknowns actually carries the error")
    print("PI = hand it the true prevalence.  REF = hand it the injected texts as reference.")
    print("Mean |error| at p=1, averaged over splits, per cell, at pi=0.30.\n")
    print(f"  {'cell':26s} {'err_00':>8s} {'err_pi':>8s} {'err_ref':>8s} {'err_both':>9s}")
    agg = {k: [] for k in ("err_00", "err_pi", "err_ref", "err_both")}
    for c in cells:
        rs = [r for r in c["mc"] if r["pi"] == 0.30]
        if not rs:
            continue
        m = {k: float(np.mean([abs(r[k]["1.0"]) for r in rs])) for k in agg}
        for k in agg:
            agg[k].append(m[k])
        mark = " <-FAIL" if name(c) in FAIL else (" <-REF" if name(c) == REF else "")
        print(f"  {name(c):26s} {m['err_00']:7.1%} {m['err_pi']:7.1%} {m['err_ref']:7.1%}"
              f" {m['err_both']:8.1%}{mark}")
    K = ("err_00", "err_pi", "err_ref", "err_both")
    print(f"\n  {'MEAN over cells':26s} " + " ".join(f"{np.mean(agg[k]):7.1%}" for k in K))
    print(f"  {'MEDIAN over cells':26s} " + " ".join(f"{np.median(agg[k]):7.1%}" for k in K))
    print("  (the mean is carried by one cell: gpt-4-0613/CON, whose deployable error is fine")
    print("   but whose oracle-reference error blows up -- its EIV denominator is near zero, so")
    print("   the RELATIVE error is undefined-ish there, not the correction itself.)")
    b0, bp, br, bb = (np.median(agg[k]) for k in K)
    print(f"\n  on the median cell: knowing pi alone removes    {1-bp/b0:5.1%} of the error")
    print(f"                      a matched reference alone     {1-br/b0:5.1%}")
    print(f"                      both together                 {1-bb/b0:5.1%}")
    print("\n  per-cell share of the error that knowing pi removes (1 - err_pi/err_00):")
    for c in cells:
        rs = [r for r in c["mc"] if r["pi"] == 0.30]
        if not rs:
            continue
        e0 = float(np.mean([abs(r["err_00"]["1.0"]) for r in rs]))
        ep = float(np.mean([abs(r["err_pi"]["1.0"]) for r in rs]))
        mark = " <-FAIL" if name(c) in FAIL else (" <-REF" if name(c) == REF else "")
        print(f"    {name(c):26s} {1-ep/e0:+7.1%}{mark}")


# ------------------------------------------------------------------ item 2
def item2(D):
    cells = D["cells"]
    pis = [float(p) for p in D["pis"]]

    sec("ITEM 2  the adjusted-count offset over %d calibration splits per cell" % D["splits_cf"])
    print("ac_pred is the two-term transfer law evaluated at each split's own (se_cal, sp_cal).\n")
    print(f"  {'cell':26s} {'pi':>5s} {'split0':>8s} {'mean':>8s} {'sd':>7s} {'p05':>8s} {'p95':>8s} {'def':>5s}")
    tab = {}
    for c in cells:
        for pi in (0.10, 0.30):
            v = np.array([s["ac_pred"][str(pi)] for s in c["splits"]], float)
            ok = np.isfinite(v)
            if ok.sum() < 10:
                print(f"  {name(c):26s} {pi:5.2f} {'--':>8s} (undefined in "
                      f"{(~ok).sum()}/{len(v)} splits: detector at or below chance)")
                continue
            vv = v[ok]
            tab[(name(c), pi)] = vv
            print(f"  {name(c):26s} {pi:5.2f} {v[0]:+8.4f} {vv.mean():+8.4f} {vv.std(ddof=1):7.4f}"
                  f" {np.percentile(vv,5):+8.4f} {np.percentile(vv,95):+8.4f} {ok.sum():5d}")

    sec("ITEM 2b  does a between-wave change detector survive that spread?")
    print("Per split, fit offset(pi) = b0 + b1*pi over pi in %s." % (pis,))
    print("Two waves at pi1, pi2 estimated by adjusted count:")
    print("  same calibration split  -> b0 cancels; the change is scaled by (1+b1).")
    print("  re-drawn split          -> the change also picks up b(2)(pi2)-b(1)(pi1).\n")
    print("Same split: the change is multiplied by (1+b1), so the error is RELATIVE, 2*sd(b1).")
    print("Re-drawn:   the change gains an ADDITIVE noise, sd = sqrt(sd(b@pi1)^2 + sd(b@pi2)^2);")
    print("            MDC is 2x that, an absolute floor on any detectable change in pi.\n")
    print(f"  {'cell':26s} {'b0 mean':>9s} {'sd(b0)':>8s} {'b1 mean':>9s} {'sd(b1)':>8s}"
          f" {'rel err same':>12s} {'MDC redraw':>11s}  {'d=0.20 is':>10s}")
    for c in cells:
        B0, B1 = [], []
        for s in c["splits"]:
            v = np.array([s["ac_pred"][str(p)] for p in pis], float)
            if not np.all(np.isfinite(v)):
                continue
            b1, b0 = np.polyfit(np.array(pis), v, 1)
            B0.append(b0); B1.append(b1)
        if len(B0) < 10:
            print(f"  {name(c):26s} (undefined)")
            continue
        B0, B1 = np.array(B0), np.array(B1)
        # 2-sd detectable change: same split, only the b1 uncertainty scales the change;
        # re-drawn split, an additive sqrt(2)*sd(b0) noise floor must be cleared.
        rel = 2 * B1.std(ddof=1)
        s1, s2 = tab.get((name(c), 0.10)), tab.get((name(c), 0.30))
        noise = float(np.sqrt(s1.std(ddof=1) ** 2 + s2.std(ddof=1) ** 2))
        mdc_re = 2 * noise
        print(f"  {name(c):26s} {B0.mean():+9.4f} {B0.std(ddof=1):8.4f} {B1.mean():+9.4f}"
              f" {B1.std(ddof=1):8.4f} {rel:11.1%} {mdc_re:11.4f}  {0.20/noise:8.1f} sd")

    sec("ITEM 2c  the law's per-split prediction against the realized Monte Carlo offset")
    P, R = [], []
    for c in cells:
        for r in c["mc"]:
            s = c["splits"][r["split"]]
            p, a = s["ac_pred"][str(r["pi"])], r["pi_ac_bias"]
            if np.isfinite(p) and np.isfinite(a):
                P.append(p); R.append(a)
    P, R = np.array(P), np.array(R)
    if len(P):
        res = R - P
        sl, ic = np.polyfit(P, R, 1)
        print(f"  {len(P)} (cell, split, pi) points   corr={corr(P,R):+.4f}  "
              f"OLS slope={sl:.3f} intercept={ic:+.4f}")
        print(f"  residual: median |r| = {np.median(abs(res)):.4f}, max = {abs(res).max():.4f}")


# ------------------------------------------------------------------ item 3
def item3(D):
    cells = D["cells"]
    bins = D["bins"]

    sec("ITEM 3  the distribution-match slope, and the ladder that explains it")
    print("dm linearises to a weighted regression of (p_obs-p_h) on (p_m-p_h). Reference")
    print("sampling noise sits in the DENOMINATOR, so the slope attenuates by S/(S+Nm+Nh) and")
    print("the intercept picks up Nh/(S+Nm+Nh). Both are predictions, not fits.\n")
    hdr = "  " + f"{'cell':26s} {'|delta|':>7s} {'S@60':>6s} " + " ".join(f"sl@{b:<4d}" for b in bins)
    print(hdr)
    obs, pred, S60, dl = [], [], [], []
    for c in cells:
        s = c["splits"][0]
        L = {l["n_bins"]: l for l in s["ladder"]}
        print(f"  {name(c):26s} {abs(s['delta']):7.3f} {L[60]['S']:6.3f} "
              + " ".join(f"{L[b]['slope']:6.3f}" for b in bins))
        obs.append(L[60]["slope"]); pred.append(L[60]["slope_pred"])
        S60.append(L[60]["S"]); dl.append(abs(s["delta"]))
    print(f"\n  slope@60 vs predicted S/(S+Nm+Nh) : r={corr(pred,obs):+.4f}  "
          f"rho={corr(_rank(pred),_rank(obs)):+.4f}  mean(obs-pred)={np.mean(np.array(obs)-np.array(pred)):+.3f}")
    print(f"  slope@60 vs |delta|               : r={corr(dl,obs):+.4f}")
    print(f"  slope@60 vs S                     : r={corr(S60,obs):+.4f}")

    print("\n  the ladder, averaged over cells and splits (the causal test):")
    for b in bins:
        L = [l for c in cells for s in c["splits"] for l in s["ladder"] if l["n_bins"] == b]
        avg = lambda k: np.mean([l[k] for l in L])
        print(f"    n_bins={b:4d}  occupied={avg('occupied'):5.1f}  slope={avg('slope'):.3f}"
              f" (pred {avg('slope_pred'):.3f})  intercept={avg('intercept'):+.4f}")

    print("\n  per-cell best n_bins on the ladder (|slope-1| minimised):")
    for c in cells:
        s = c["splits"][0]
        L = sorted(s["ladder"], key=lambda l: abs(l["slope"] - 1))
        d60 = {l["n_bins"]: l for l in s["ladder"]}[60]
        print(f"    {name(c):26s} best={L[0]['n_bins']:4d} (slope {L[0]['slope']:.3f})"
              f"   default 60 -> {d60['slope']:.3f}")

    print("\n  split-to-split stability of the slope (does item 2's split effect move it?):")
    for c in cells:
        d = [{l["n_bins"]: l for l in s["ladder"]}[60] for s in c["splits"]]
        v, i = [x["slope"] for x in d], [x["intercept"] for x in d]
        print(f"    {name(c):26s} slope@60 {min(v):.3f}..{max(v):.3f}   "
              f"intercept@60 {min(i):+.4f}..{max(i):+.4f}")


def main():
    A, B = load("results/round3_splits.json"), load("results/round3_dm.json")
    if A:
        item1(A)
        item2(A)
    else:
        print("results/round3_splits.json not present yet")
    if B:
        item3(B)
    else:
        print("\nresults/round3_dm.json not present yet")


if __name__ == "__main__":
    main()
