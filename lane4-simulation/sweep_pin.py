"""Layer B (pi, n) expansion on the six cells the pool x trait sweep singled out.

LAYERB-SWEEP.md section 9 item 5: the pool x trait dimension is characterised at ONE design
point (n=1000, pi=0.10). This varies the design point and holds the cells fixed, which is the
complementary cut. pi in {0.02, 0.05, 0.10, 0.20, 0.30} x n in {500, 1000, 2500}.

Machine texts are drawn WITH replacement here. Without replacement, pi=0.30 at n=2500 needs
750 machine respondents from a ~160-text injection half and is impossible; with replacement
is also the honest model of a ghost-respondent farm, which resubmits generated text. The
design point (pi=0.10, n=1000) is run both ways as a bridge to the k=1 sweep's numbers.

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
from sweep_k4 import CELLS  # the same six cells, so the two rounds are directly comparable

PIS = (0.02, 0.05, 0.10, 0.20, 0.30)
NS = (500, 1000, 2500)
ARMS = (0.0, 0.5, 1.0)
RHO_T = 0.5
REPS = 400
SP_TARGET = 0.99
SEED = 20260907 + 88000

_FAILURES: list[str] = []
_CHECKS = 0


def check(name: str, ok: bool, detail: str = "") -> bool:
    global _CHECKS
    _CHECKS += 1
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else ""))
    if not ok:
        _FAILURES.append(name)
    return ok


def cell_setup(pool_name: str, trait: str, raw: dict, cell_seed: int) -> dict:
    """Everything that depends on the (pool, trait) but not on (pi, n): one split, reused."""
    H_all = lane3_pool("pk_human", trait, raw)
    M_all = lane3_pool(pool_name, trait, raw)
    rng0 = np.random.default_rng(cell_seed)
    M_inj, M_ref = split_reference(M_all, rng0, frac=0.5)
    H_base, H_ref = split_reference(H_all, rng0, frac=0.5)

    mu_h, sd_h = float(H_base.scores.mean()), float(H_base.scores.std(ddof=0))
    q1 = H_base.balance
    xh = (H_base.scores - mu_h) / sd_h
    th = (H_base.labels - q1) / np.sqrt(q1 * (1 - q1))
    r_H = float(np.mean((xh - xh.mean()) * th))

    det_Href = reference_detector(H_all, H_ref)
    det_Mref = reference_detector(M_all, M_ref)
    thr = float(np.quantile(det_Href, SP_TARGET))
    return {
        "H_base": H_base, "M_inj": M_inj, "q1": q1, "r_H": r_H,
        "Mref_std": (M_ref.scores - mu_h) / sd_h,
        "Href_std": (H_ref.scores - mu_h) / sd_h,
        "thr": thr,
        "sp_cal": float(np.mean(det_Href <= thr)),
        "se_cal": float(np.mean(det_Mref > thr)),
        "sp_base": float(np.mean(H_base.detector <= thr)),
        "se_inj": float(np.mean(M_inj.detector > thr)),
    }


def run_point(S: dict, pi: float, n: int, seed: int, replace: bool = True) -> dict:
    H_base, M_inj, q1, r_H = S["H_base"], S["M_inj"], S["q1"], S["r_H"]
    rho_H_true = RHO_T * r_H
    pred = {p: layer_b_moments(H_base, M_inj, pi, p, RHO_T, q1=q1) for p in ARMS}

    keys = ("rho_obs", "Att_real", "pi_dm", "pi_ac", "rho_H_hat", "rho_H_hat_c0")
    res = {p: {k: [] for k in keys} for p in ARMS}
    for r in range(REPS):
        for p in ARMS:
            rng = np.random.default_rng([seed, r, int(p * 100)])
            inj = build_injected_sample(H_base, M_inj, n, pi, p, rng, rho_T=RHO_T,
                                        k_chunks=1, sp=SP_TARGET, replace=replace)
            s = inj.sample
            x, w = inj.x_full, s.w
            d = res[p]
            rho = _pearson(x, w)
            d["rho_obs"].append(rho)
            d["Att_real"].append(rho / rho_H_true)
            d["pi_dm"].append(_distribution_match_pi(x, S["Mref_std"], S["Href_std"]))
            fr = float(np.mean(np.asarray(s.F) > S["thr"]))
            d["pi_ac"].append(_adjusted_count_pi(fr, S["se_cal"], S["sp_cal"])[0])
            e = eiv_correct(x, w, S["Mref_std"], S["Href_std"], r_H,
                            c_known=p * pred[1.0]["c"])
            d["rho_H_hat"].append(e["rho_H_hat"])
            d["rho_H_hat_c0"].append(
                eiv_correct(x, w, S["Mref_std"], S["Href_std"], r_H, c_known=0.0)["rho_H_hat"])

    A = {p: {k: np.array(v, float) for k, v in d.items()} for p, d in res.items()}
    m = lambda p, k: float(np.nanmean(A[p][k]))

    # the two-term transfer law from LAYERB-SWEEP.md section 5, now as a function of pi
    denom = S["se_cal"] - (1.0 - S["sp_cal"])
    pred_ac_bias = (pi * (S["se_inj"] - S["se_cal"])
                    + (1 - pi) * ((1 - S["sp_base"]) - (1 - S["sp_cal"]))) / denom if denom > 0 else float("nan")

    zmax = 0.0
    for p in ARMS:
        se = mcse(A[p]["rho_obs"])
        if se > 0:
            zmax = max(zmax, abs((m(p, "rho_obs") - pred[p]["rho_obs_pred"]) / se))

    contrast = pred[1.0]["rho_obs_pred"] - pred[0.0]["rho_obs_pred"]
    sd1 = float(np.std(A[1.0]["rho_obs"] - A[0.0]["rho_obs"], ddof=1))
    return {
        "pi": pi, "n": n, "replace": replace, "r_H": r_H, "rho_H_true": rho_H_true,
        "Att_pred": {str(p): pred[p]["Att"] for p in ARMS},
        "Att_real": {str(p): m(p, "Att_real") for p in ARMS},
        "rho_mcse": {str(p): mcse(A[p]["rho_obs"]) for p in ARMS},
        "zmax_rho": zmax,
        "contrast_pred": contrast, "contrast_obs": m(1.0, "rho_obs") - m(0.0, "rho_obs"),
        "contrast_sd_1rep": sd1,
        "z_1rep": contrast / sd1 if sd1 > 0 else float("nan"),
        "pi_dm": {str(p): m(p, "pi_dm") for p in ARMS},
        "pi_dm_bias": m(0.0, "pi_dm") - pi,
        "pi_ac": {str(p): m(p, "pi_ac") for p in ARMS},
        "pi_ac_bias": m(0.0, "pi_ac") - pi,
        "pi_ac_bias_pred": pred_ac_bias,
        "eiv_err": {str(p): m(p, "rho_H_hat") / rho_H_true - 1.0 for p in ARMS},
        "c0_err_p1": m(1.0, "rho_H_hat_c0") / rho_H_true - 1.0,
    }


def main() -> int:
    raw = load_lane3()
    print(f"Layer B (pi, n) expansion: {len(CELLS)} cells x {len(PIS)} pi x {len(NS)} n")
    print(f"pi={PIS} n={NS} p in {ARMS} reps={REPS} rho_T={RHO_T} k=1 replace=True\n")
    rows, t0 = [], time.perf_counter()
    for ci, (pool, trait) in enumerate(CELLS):
        S = cell_setup(pool, trait, raw, SEED + 1000 * ci)
        for pi in PIS:
            for n in NS:
                pt = run_point(S, pi, n, SEED + 1000 * ci + int(pi * 1000) + n)
                pt.update(pool=pool, trait=trait)
                rows.append(pt)
            print(f"  {pool:30s} {trait} pi={pi:.2f} "
                  f"Att(1)={rows[-1]['Att_real']['1.0']:.3f} "
                  f"dm_bias={rows[-1]['pi_dm_bias']:+.4f} "
                  f"ac_bias={rows[-1]['pi_ac_bias']:+.4f} "
                  f"({time.perf_counter()-t0:.0f}s total)", flush=True)
        # bridge: the design point without replacement, to tie back to the k=1 sweep
        b = run_point(S, 0.10, 1000, SEED + 1000 * ci + 100 + 1000, replace=False)
        b.update(pool=pool, trait=trait, bridge=True)
        rows.append(b)

    out = {"pis": PIS, "ns": NS, "reps": REPS, "rho_T": RHO_T,
           "rows": rows, "seconds": time.perf_counter() - t0}
    Path("results").mkdir(exist_ok=True)
    Path("results/layerb_pin.json").write_text(json.dumps(out, indent=2))
    print(f"\n-> results/layerb_pin.json ({out['seconds']:.0f}s)\n")
    report(rows)
    return 0 if not _FAILURES else 1


def report(rows: list[dict]) -> None:
    main_rows = [r for r in rows if not r.get("bridge")]
    bridge = [r for r in rows if r.get("bridge")]

    print("\n=== identities survive the whole (pi, n) box ===")
    zm = max(r["zmax_rho"] for r in main_rows)
    check("(E7) predicted rho_obs within 4 MCSE of the realized mean, every (cell, pi, n, p)",
          zm < 4.0, f"max |z| = {zm:.2f} over {len(main_rows) * 3} arm-points")
    dc = max(abs(r["contrast_obs"] - r["contrast_pred"]) / (r["rho_mcse"]["1.0"] + r["rho_mcse"]["0.0"])
             for r in main_rows)
    check("observed matched-vs-random contrast agrees with (E7) across pi and n",
          dc < 4.0, f"max {dc:.2f} MCSE")

    print("\n=== what n does and does not change ===")
    # bias is a population property: it must not move with n. variance must fall as 1/sqrt(n).
    worst_bias_n, worst_key = 0.0, ""
    for key in ("Att_real", "eiv_err"):
        for pool, trait in {(r["pool"], r["trait"]) for r in main_rows}:
            for pi in PIS:
                grp = [r for r in main_rows if r["pool"] == pool and r["trait"] == trait and r["pi"] == pi]
                v = [(g["Att_real"]["1.0"] if key == "Att_real" else g["eiv_err"]["1.0"]) for g in grp]
                if max(v) - min(v) > worst_bias_n:
                    worst_bias_n, worst_key = max(v) - min(v), f"{key} {pool}/{trait} pi={pi}"
    check("Att and the EIV error are n-invariant (bias is a population property)",
          worst_bias_n < 0.05, f"max spread across n = {worst_bias_n:.4f} at {worst_key}")

    ratios = []
    for pool, trait in {(r["pool"], r["trait"]) for r in main_rows}:
        for pi in PIS:
            g = {r["n"]: r for r in main_rows if r["pool"] == pool and r["trait"] == trait and r["pi"] == pi}
            if 500 in g and 2500 in g:
                ratios.append(g[500]["rho_mcse"]["1.0"] / g[2500]["rho_mcse"]["1.0"])
    check("MCSE(rho_obs) scales as 1/sqrt(n): the n=500 / n=2500 ratio is sqrt(5) = 2.24",
          all(2.0 <= x <= 2.5 for x in ratios),
          f"observed {min(ratios):.2f}-{max(ratios):.2f} over {len(ratios)} (cell, pi) pairs")

    print("\n=== the amplification threshold in pi ===")
    xs = []
    for pool, trait in sorted({(r["pool"], r["trait"]) for r in main_rows}):
        g = sorted([r for r in main_rows if r["pool"] == pool and r["trait"] == trait
                    and r["n"] == 1000], key=lambda r: r["pi"])
        below = [r["pi"] for r in g if r["Att_real"]["1.0"] < 1.0]
        above = [r["pi"] for r in g if r["Att_real"]["1.0"] >= 1.0]
        xs.append((f"{pool.split('_')[-1]}/{trait}", max(below) if below else None,
                   min(above) if above else None))
    crossed = [x for x in xs if x[2] is not None]
    check("Att(p=1) is monotone increasing in pi wherever g > 0",
          all(all(a["Att_real"]["1.0"] <= b["Att_real"]["1.0"] + 1e-3
                  for a, b in zip(s_, s_[1:]))
              for s_ in [sorted([r for r in main_rows if r["pool"] == P and r["trait"] == T
                                 and r["n"] == 1000], key=lambda r: r["pi"])
                         for P, T in {(r["pool"], r["trait"]) for r in main_rows}]),
          f"{len(crossed)} of {len(xs)} cells cross Att=1 inside pi<=0.30")

    print("\n=== estimators as a function of pi ===")
    dmb = [abs(r["pi_dm_bias"]) for r in main_rows]
    check("distribution-match prevalence unbiased within 0.01 across the (pi, n) box",
          max(dmb) <= 0.01,
          f"|bias| spans {min(dmb):.4f}-{max(dmb):.4f}; "
          f"{sum(1 for x in dmb if x > 0.01)} of {len(dmb)} points outside 0.01")
    ok_ac = [r for r in main_rows if np.isfinite(r["pi_ac_bias_pred"])]
    resid = [abs(r["pi_ac_bias"] - r["pi_ac_bias_pred"]) for r in ok_ac]
    check("the two-term transfer law predicts the adjusted-count bias at every pi",
          max(resid) < 0.02,
          f"max residual {max(resid):.4f} over {len(ok_ac)} defined points "
          f"(corr {np.corrcoef([r['pi_ac_bias'] for r in ok_ac], [r['pi_ac_bias_pred'] for r in ok_ac])[0,1]:.4f})")
    acb = [abs(r["pi_ac_bias"]) for r in ok_ac]
    check("adjusted-count prevalence unbiased within 0.01 across the (pi, n) box",
          max(acb) <= 0.01,
          f"|bias| spans {min(acb):.4f}-{max(acb):.4f}; "
          f"{sum(1 for x in acb if x > 0.01)} of {len(acb)} defined points outside 0.01")
    eiv = [abs(r["eiv_err"][str(p)]) for r in main_rows for p in ARMS]
    check("EIV correction recovers rho_H within 25% across the (pi, n) box",
          max(eiv) <= 0.25,
          f"max |err| {max(eiv):.1%}; {sum(1 for x in eiv if x > 0.25)} of {len(eiv)} "
          "cell-pi-n-arms outside 25%")

    print("\n=== with vs without replacement at the design point ===")
    worst = 0.0
    for b in bridge:
        m_ = [r for r in main_rows if r["pool"] == b["pool"] and r["trait"] == b["trait"]
              and r["pi"] == 0.10 and r["n"] == 1000][0]
        worst = max(worst, abs(b["Att_real"]["1.0"] - m_["Att_real"]["1.0"]))
    check("drawing machine texts with replacement reproduces the without-replacement Att",
          worst < 0.02, f"max |dAtt(p=1)| = {worst:.4f} over {len(bridge)} cells")

    print(f"\n{_CHECKS - len(_FAILURES)}/{_CHECKS} checks passed")
    if _FAILURES:
        print("FAILED: " + ", ".join(_FAILURES))


if __name__ == "__main__":
    raise SystemExit(main())
