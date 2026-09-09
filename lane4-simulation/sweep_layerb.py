"""Layer B sweep: the pilot cell, repeated over all 4 labeled pools x all 5 traits.

Same cell as LAYERB-PILOT.md (n=1000, pi=0.10, p in {0, 0.5, 1}, 400 reps, rho_T=0.5,
k_chunks=1); the only thing that varies is which (pool, trait) supplies the injected texts.
Each cell gets its OWN held-out split, so each has its own r_H, c_pool, kappa and delta --
they are reported per cell, never pooled.

New since the pilot: lane 3's FIXES-DONE (2026-09-07 21:03) added detector_p_machine to
pk_human.json, so SPEC 3.2's adjusted_count prevalence branch now runs. It is calibrated on
the held-out reference halves (threshold, se and sp all from texts the survey never sees).

Nothing here touches dgp.py or the Layer A grid. Single-threaded by construction.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from estimators import _adjusted_count_pi, _distribution_match_pi, _pearson  # SPEC 3.2 code
from inject.assign import capacity_report, pool_coupling, raw_pool_coupling, realized_coupling
from inject.build import build_injected_sample, layer_b_moments
from inject.pools import (
    LANE3_TRAITS,
    calibration_split,
    lane3_labeled_pools,
    lane3_pool,
    load_lane3,
    reference_detector,
    split_id,
)
from layerb_pilot import eiv_correct, mcse  # the pilot's estimator chain, not a re-write

N = 1000
PI = 0.10
RHO_T = 0.5
K_CHUNKS = 1
REPS = 400
ARMS = (0.0, 0.5, 1.0)
SP_TARGET = 0.99
SEED = 20260907

_FAILURES: list[str] = []
_CHECKS = 0


def check(name: str, ok: bool, detail: str = "") -> bool:
    global _CHECKS
    _CHECKS += 1
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else ""))
    if not ok:
        _FAILURES.append(name)
    return ok


def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    """P(score(machine) > score(human)), ties at 0.5. Mann-Whitney, no sklearn needed."""
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    pos, neg = pos[np.isfinite(pos)], neg[np.isfinite(neg)]
    if pos.size == 0 or neg.size == 0:
        return float("nan")
    order = np.argsort(np.concatenate([pos, neg]), kind="mergesort")
    ranks = np.empty(order.size, float)
    ranks[order] = np.arange(1, order.size + 1)
    # average ranks over ties so an exactly-tied detector reads 0.5, not 1.0
    allv = np.concatenate([pos, neg])[order]
    i = 0
    while i < allv.size:
        j = i
        while j + 1 < allv.size and allv[j + 1] == allv[i]:
            j += 1
        if j > i:
            ranks[order[i:j + 1]] = ranks[order[i:j + 1]].mean()
        i = j + 1
    return float((ranks[:pos.size].sum() - pos.size * (pos.size + 1) / 2) / (pos.size * neg.size))


def run_cell(pool_name: str, trait: str, raw: dict, cell_seed: int) -> dict:
    t0 = time.perf_counter()
    H_all = lane3_pool("pk_human", trait, raw)
    M_all = lane3_pool(pool_name, trait, raw)
    l3 = raw["labeled_pools"][pool_name]["trait_stats"][M_all.metrics["lane3_trait_key"]]

    # Frozen calibration split (SPEC-FIXES-ROUND3.md fix 1): keyed on pool identity, not cell_seed.
    M_inj, M_ref = calibration_split(M_all, frac=0.5)
    H_base, H_ref = calibration_split(H_all, frac=0.5)
    disjoint = (not (set(t.text_id for t in M_inj.texts) & set(M_ref.text_ids))
                and not (set(t.text_id for t in H_base.texts) & set(H_ref.text_ids)))

    mu_h, sd_h = float(H_base.scores.mean()), float(H_base.scores.std(ddof=0))
    Href_std = (H_ref.scores - mu_h) / sd_h
    Mref_std = (M_ref.scores - mu_h) / sd_h

    q1 = H_base.balance
    xh = (H_base.scores - mu_h) / sd_h
    th = (H_base.labels - q1) / np.sqrt(q1 * (1 - q1))
    r_H = float(np.mean((xh - xh.mean()) * th))
    rho_H_true = RHO_T * r_H

    pred = {p: layer_b_moments(H_base, M_inj, PI, p, RHO_T, q1=q1) for p in ARMS}
    c_pool = pool_coupling(M_inj, q1)

    # g the covariance way vs the label-mean-difference way (E66 with no definition needed)
    m_s = (M_inj.scores - mu_h) / sd_h
    lm = M_inj.labels
    denom_lm = xh[H_base.labels == 1].mean() - xh[H_base.labels == 0].mean()
    g_labelmean = float((m_s[lm == 1].mean() - m_s[lm == 0].mean()) / denom_lm)

    n_m = int(round(N * PI))
    lab_typ = (np.random.default_rng(1).random(n_m) < q1).astype(int)
    cap = {p: capacity_report(lab_typ, M_inj, p, q1=q1) for p in ARMS}
    cap_ok = all(d <= a for p in ARMS for d, a in cap[p].values())
    cap_worst = max(((d, a) for p in ARMS for d, a in cap[p].values()), key=lambda t: t[0] / t[1])

    # ---- adjusted-count calibration, entirely on the held-out reference halves ----------
    det_Href = reference_detector(H_all, H_ref)
    det_Mref = reference_detector(M_all, M_ref)
    thr = float(np.quantile(det_Href, SP_TARGET))
    sp_cal = float(np.mean(det_Href <= thr))
    se_cal = float(np.mean(det_Mref > thr))
    det_auc = auc(det_Mref, det_Href)
    # The estimator inverts flag_rate with the REFERENCE half's (se, sp), but the survey's
    # humans come from H_base and its machines from M_inj. These two are the transfer error
    # the adjusted count actually pays; at se ~ 0.3 a 1pp error in sp moves pi_hat by ~0.04.
    sp_base = float(np.mean(H_base.detector <= thr))
    se_inj = float(np.mean(M_inj.detector > thr))

    keys = ("rho_obs", "c_real", "Att_real", "kappa_real", "delta_real", "pi_hat", "Att_hat",
            "rho_H_hat", "rho_H_hat_or", "rho_H_hat_c0", "flag_rate", "pi_ac")
    res = {p: {k: [] for k in keys} for p in ARMS}
    for r in range(REPS):
        for p in ARMS:
            rng = np.random.default_rng([cell_seed, r, int(p * 100)])
            inj = build_injected_sample(H_base, M_inj, N, PI, p, rng,
                                        rho_T=RHO_T, k_chunks=K_CHUNKS, sp=SP_TARGET)
            s = inj.sample
            x, w = inj.x_full, s.w
            mpos = np.flatnonzero(s.A == 1)
            d = res[p]
            rho = _pearson(x, w)
            d["rho_obs"].append(rho)
            d["c_real"].append(realized_coupling(x[mpos], s.theta[mpos]))
            d["Att_real"].append(rho / rho_H_true)
            d["kappa_real"].append(float(np.var(x[mpos], ddof=1)))
            d["delta_real"].append(float(-np.mean(x[mpos])))
            e = eiv_correct(x, w, Mref_std, Href_std, r_H, c_known=p * c_pool)
            d["pi_hat"].append(e["pi_hat"]); d["Att_hat"].append(e["Att_hat"])
            d["rho_H_hat"].append(e["rho_H_hat"])
            d["rho_H_hat_c0"].append(
                eiv_correct(x, w, Mref_std, Href_std, r_H, c_known=0.0)["rho_H_hat"])
            d["rho_H_hat_or"].append(
                eiv_correct(x, w, Mref_std, Href_std, r_H, c_known=p * c_pool,
                            pi_fixed=PI)["rho_H_hat"])
            # adjusted count: flag at the HELD-OUT threshold, invert with the held-out (se, sp)
            fr = float(np.mean(np.asarray(s.F) > thr))
            d["flag_rate"].append(fr)
            d["pi_ac"].append(_adjusted_count_pi(fr, se_cal, sp_cal)[0])

    A = {p: {k: np.array(v, float) for k, v in d.items()} for p, d in res.items()}

    zmax = 0.0
    for p in ARMS:
        for key, pk_ in (("c_real", "c"), ("kappa_real", "kappa"), ("delta_real", "delta"),
                         ("rho_obs", "rho_obs_pred"), ("Att_real", "Att")):
            se = mcse(A[p][key])
            if se > 0:
                zmax = max(zmax, abs((float(np.nanmean(A[p][key])) - pred[p][pk_]) / se))

    d_pred = pred[1.0]["rho_obs_pred"] - pred[0.0]["rho_obs_pred"]
    diff = A[1.0]["rho_obs"] - A[0.0]["rho_obs"]
    d_obs, d_se = float(np.mean(diff)), mcse(diff)
    sd_rep = float(np.std(diff, ddof=1))
    z_one = d_pred / sd_rep if sd_rep > 0 else float("nan")
    reps_needed = int(np.ceil((2.8 / z_one) ** 2)) if np.isfinite(z_one) and z_one > 0 else -1
    n_needed = int(np.ceil(N * (2.8 / z_one) ** 2)) if np.isfinite(z_one) and z_one > 0 else -1

    out = {
        "pool": pool_name, "trait": trait, "seed": cell_seed,
        "split_id": split_id(M_ref, H_ref),
        "n_human_base": len(H_base), "n_machine_inj": len(M_inj), "q1": q1,
        "disjoint": disjoint,
        "r_H": r_H, "r_H_lane3_fullpool": float(l3["r_H"]), "rho_H_true": rho_H_true,
        "c_pool": c_pool, "c_pool_raw": raw_pool_coupling(M_inj),
        "chat_r_lane3_fullpool": float(l3["chat_r"]),
        "kappa": pred[0.0]["kappa"], "kappa_lane3": float(l3["kappa"]),
        "delta": pred[0.0]["delta"], "delta_lane3_memo_sign": float(l3["delta"]),
        "g": pred[1.0]["g"], "g_labelmean": g_labelmean,
        "g_lane3_fixed": float(l3["g"]), "g_lane3_old_ratio": float(l3["g_old_ratio_form"]),
        "capacity_ok": cap_ok, "capacity_worst": [float(cap_worst[0]), int(cap_worst[1])],
        "e7_max_abs_error": max(pred[p]["e7_abs_error"] for p in ARMS),
        "e67_c_max_dev": max(abs(pred[p]["c"] - p * c_pool) for p in ARMS),
        "e67_kappa_max_dev": max(abs(pred[p]["kappa"] - pred[0.0]["kappa"]) for p in ARMS),
        "e67_delta_max_dev": max(abs(pred[p]["delta"] - pred[0.0]["delta"]) for p in ARMS),
        "z_max_moment": zmax,
        "predicted": {str(p): pred[p] for p in ARMS},
        "monte_carlo": {str(p): {k: {"mean": float(np.nanmean(v)), "mcse": mcse(v)}
                                 for k, v in A[p].items()} for p in ARMS},
        "contrast": {"predicted": d_pred, "observed": d_obs, "mcse": d_se,
                     "sd_per_replicate": sd_rep, "z_one_replicate": z_one,
                     "z_over_reps": d_obs / d_se if d_se > 0 else float("nan"),
                     "reps_for_z2.8_at_n1000": reps_needed, "n_for_z2.8_in_one_survey": n_needed},
        "detector": {"threshold": thr, "sp_target": SP_TARGET, "sp_calibrated": sp_cal,
                     "se_calibrated": se_cal, "auc_machine_vs_human": det_auc,
                     "denominator_se_minus_fpr": se_cal - (1.0 - sp_cal),
                     "n_ref_human": int(det_Href.size), "n_ref_machine": int(det_Mref.size),
                     "sp_on_survey_base": sp_base, "se_on_injected_texts": se_inj},
        "seconds": time.perf_counter() - t0,
    }
    return out


def main() -> int:
    t_start = time.perf_counter()
    raw = load_lane3()
    pools = lane3_labeled_pools(raw)
    cells = [(p, t) for p in pools for t in LANE3_TRAITS]
    print(f"Layer B sweep: {len(cells)} cells = {len(pools)} pools x {len(LANE3_TRAITS)} traits")
    print(f"cell: n={N} pi={PI} p in {ARMS} reps={REPS} rho_T={RHO_T} k_chunks={K_CHUNKS}\n")

    rows = []
    for i, (pool_name, trait) in enumerate(cells):
        row = run_cell(pool_name, trait, raw, SEED + 1000 * i)
        rows.append(row)
        print(f"  [{i + 1:2d}/{len(cells)}] {pool_name:29s} {trait} "
              f"r_H={row['r_H']:+.4f} c={row['c_pool']:+.4f} kappa={row['kappa']:.3f} "
              f"delta={row['delta']:+.3f} g={row['g']:+.3f} "
              f"Att(0)={row['predicted']['0.0']['Att']:.3f}->Att(1)="
              f"{row['predicted']['1.0']['Att']:.3f} "
              f"({row['seconds']:.0f}s, {time.perf_counter() - t_start:.0f}s total)")

    Path("results").mkdir(exist_ok=True)
    Path("results/layerb_sweep.json").write_text(json.dumps(
        {"cell": {"n": N, "pi": PI, "rho_T": RHO_T, "k_chunks": K_CHUNKS, "reps": REPS,
                  "arms": list(ARMS), "sp_target": SP_TARGET, "seed": SEED},
         "cells": rows, "seconds": time.perf_counter() - t_start}, indent=2))
    print(f"\n-> results/layerb_sweep.json ({time.perf_counter() - t_start:.0f}s)")
    return rows_report(rows)


def rows_report(rows: list[dict]) -> int:
    def col(k):
        return [r[k] for r in rows]

    print("\n=== identities (exact, closed form) ===")
    check("(E7) closed form == direct mixture correlation, every cell and arm",
          max(col("e7_max_abs_error")) < 1e-13,
          "max |rho_pred - rho_direct| = %.2e over %d cells" % (max(col("e7_max_abs_error")), len(rows)))
    check("(E67) c(p) = p * c_pool exactly, every cell",
          max(col("e67_c_max_dev")) < 1e-12, "max dev = %.2e" % max(col("e67_c_max_dev")))
    check("(E67) kappa and delta invariant in p, every cell",
          max(col("e67_kappa_max_dev")) < 1e-12 and max(col("e67_delta_max_dev")) < 1e-12,
          "max dev kappa %.2e delta %.2e" % (max(col("e67_kappa_max_dev")),
                                             max(col("e67_delta_max_dev"))))
    rel_g = [abs(r["g"] - r["g_labelmean"]) / max(abs(r["g_labelmean"]), 1e-9) for r in rows]
    check("g by (E66) covariance ratio == g by label-mean-difference ratio, every cell",
          max(rel_g) < 0.02,
          "worst %s/%s: cov %.4f vs label-mean %.4f (%.1f%%)" % (
              rows[int(np.argmax(rel_g))]["pool"], rows[int(np.argmax(rel_g))]["trait"],
              rows[int(np.argmax(rel_g))]["g"], rows[int(np.argmax(rel_g))]["g_labelmean"],
              100 * max(rel_g)))
    check("held-out references disjoint from injection pools, every cell",
          all(col("disjoint")), f"{len(rows)} cells")
    check("without-replacement capacity holds, every cell and arm",
          all(col("capacity_ok")),
          "worst cell: demand %.1f of %d" % tuple(max(col("capacity_worst"),
                                                      key=lambda t: t[0] / t[1])))

    print("\n=== Monte Carlo recovers the closed form ===")
    zbad = [r for r in rows if r["z_max_moment"] > 4.0]
    check("every realized moment within 4 MCSE of its closed form, every cell",
          not zbad, "%d cells x 3 arms x 5 quantities = %d z-scores, max |z| = %.2f at %s/%s"
          % (len(rows), 15 * len(rows), max(col("z_max_moment")),
             rows[int(np.argmax(col("z_max_moment")))]["pool"],
             rows[int(np.argmax(col("z_max_moment")))]["trait"]))
    dz = [abs(r["contrast"]["observed"] - r["contrast"]["predicted"]) / r["contrast"]["mcse"]
          for r in rows]
    check("observed matched-vs-random contrast agrees with (E7), every cell",
          max(dz) < 4.0, "max |obs - pred| = %.2f MCSE at %s/%s"
          % (max(dz), rows[int(np.argmax(dz))]["pool"], rows[int(np.argmax(dz))]["trait"]))

    print("\n=== estimators ===")
    bias = [r["monte_carlo"]["0.0"]["pi_hat"]["mean"] - PI for r in rows]
    ses = [r["monte_carlo"]["0.0"]["pi_hat"]["mcse"] for r in rows]
    n_biased = sum(1 for b, s in zip(bias, ses) if abs(b) > max(0.01, 2.8 * s))
    check("label-free prevalence unbiased for pi=0.10 (tol 0.01) in every cell",
          n_biased == 0,
          "%d of %d cells biased beyond 0.01; bias range %+.4f to %+.4f, mean %+.4f"
          % (n_biased, len(rows), min(bias), max(bias), float(np.mean(bias))))
    rho_bad = [(r["pool"], r["trait"], p, r["monte_carlo"][p]["rho_H_hat"]["mean"] / r["rho_H_true"] - 1)
               for r in rows for p in ("0.0", "0.5", "1.0")
               if abs(r["monte_carlo"][p]["rho_H_hat"]["mean"] - r["rho_H_true"])
               > 0.25 * abs(r["rho_H_true"])]
    check("EIV correction recovers rho_H within 25%, every cell and arm",
          not rho_bad, "%d of %d cell-arms outside 25%%" % (len(rho_bad), 3 * len(rows))
          + ("" if not rho_bad else "; worst " + max(rho_bad, key=lambda t: abs(t[3]))[0]
             + "/" + max(rho_bad, key=lambda t: abs(t[3]))[1]
             + " %+.0f%%" % (100 * max(rho_bad, key=lambda t: abs(t[3]))[3])))
    ac = [r["monte_carlo"]["0.0"]["pi_ac"]["mean"] for r in rows]
    check("adjusted-count prevalence branch scored (lane 3 FIXES-DONE landed)",
          all(np.isfinite(ac)) and all(r["detector"]["se_calibrated"] >= 0 for r in rows),
          "pi_hat_ac in [%.4f, %.4f] vs pi=%.2f; detector se@sp=%.2f ranges %.3f-%.3f"
          % (min(ac), max(ac), PI, SP_TARGET,
             min(r["detector"]["se_calibrated"] for r in rows),
             max(r["detector"]["se_calibrated"] for r in rows)))
    ac_bad = sum(1 for v in ac if abs(v - PI) > 0.01)
    check("adjusted-count prevalence unbiased for pi=0.10 (tol 0.01) in every cell",
          ac_bad == 0, "%d of %d cells outside 0.01; range %+.4f to %+.4f"
          % (ac_bad, len(rows), min(ac) - PI, max(ac) - PI))

    print(f"\n{_CHECKS - len(_FAILURES)}/{_CHECKS} checks passed")
    if _FAILURES:
        print("FAILED: " + ", ".join(_FAILURES))
    return 1 if _FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
