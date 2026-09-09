"""Layer B pilot cell: design-pivot-memo section 8.2 step 3, on lane 3's real measurements.

One cell -- trait EXT, PersonaLLM gpt-4-0613 injected into the PK essays -- run at three
coupling levels p in {0, 0.5, 1}. Scores (E7)/(E67) against the realized (g, kappa, delta),
the random-vs-matched contrast, and the SPEC 3.2 label-free prevalence estimator with its
EIV correction. PASS/FAIL discipline copied from PILOT.md and inject/test_inject.py.

Nothing here touches dgp.py or the Layer A grid. Single-threaded by construction.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from estimators import (  # SPEC 3.2 code, not a re-write
    _adjusted_count_pi,
    _distribution_match_pi,
    _pearson,
)
from inject.assign import capacity_report, pool_coupling, raw_pool_coupling, realized_coupling
from inject.build import build_injected_sample, layer_b_moments
from inject.pools import calibration_split, lane3_pool, load_lane3, reference_detector, split_id

TRAIT = "EXT"
POOL = "personallm_gpt-4-0613"
N = 1000
PI = 0.10
RHO_T = 0.5
K_CHUNKS = 1
SP_TARGET = 0.99
REPS = 400
ARMS = (0.0, 0.5, 1.0)
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


def mcse(v: np.ndarray) -> float:
    v = np.asarray(v, dtype=float)
    v = v[np.isfinite(v)]
    return float(v.std(ddof=1) / np.sqrt(v.size)) if v.size > 1 else float("nan")


def eiv_correct(x, w, machine_ref, human_ref, r_H, c_known, pi_fixed=None):
    """SPEC 3.2 label-free prevalence + the EIV correction, in Layer B units.

    Layer B's r_H plays the role Layer A's sqrt(rel_H) plays in N: with the human base
    normalization V_H = 1, N = (1 - pi) + pi * c * sqrt(kappa) / r_H. Everything else is the
    Layer A moment chain verbatim (estimators.fit_labelfree, lines 402-425). rho_T is NOT
    recovered: that step needs rel_H, which at k_chunks = 1 is not identified (INJECT.md 9).
    """
    mu_M = float(np.mean(machine_ref))
    s2_M = float(np.var(machine_ref, ddof=1))
    pi_hat = _distribution_match_pi(x, machine_ref, human_ref) if pi_fixed is None else pi_fixed
    if not np.isfinite(pi_hat):
        return {k: float("nan") for k in
                ("pi_hat", "kappa_hat", "delta_hat", "Den_hat", "Att_hat", "rho_H_hat")}
    pi_hat = float(np.clip(pi_hat, 1e-6, 1 - 1e-6))
    mean_x, var_x = float(np.mean(x)), float(np.var(x, ddof=1))
    mu_H_hat = (mean_x - pi_hat * mu_M) / (1 - pi_hat)
    Delta_hat = mu_H_hat - mu_M
    V_H_hat = (var_x - pi_hat * s2_M - pi_hat * (1 - pi_hat) * Delta_hat**2) / (1 - pi_hat)
    if not np.isfinite(V_H_hat) or V_H_hat <= 0:
        return {"pi_hat": pi_hat, **{k: float("nan") for k in
                ("kappa_hat", "delta_hat", "Den_hat", "Att_hat", "rho_H_hat")}}
    kappa_hat = s2_M / V_H_hat
    delta_hat = Delta_hat / np.sqrt(V_H_hat)
    Den_hat = var_x / V_H_hat
    N_hat = (1 - pi_hat) + pi_hat * c_known * np.sqrt(kappa_hat) / r_H
    Att_hat = N_hat / np.sqrt(Den_hat)
    rho_H_hat = _pearson(x, w) / Att_hat if Att_hat else float("nan")
    return {"pi_hat": pi_hat, "kappa_hat": kappa_hat, "delta_hat": delta_hat,
            "Den_hat": Den_hat, "Att_hat": float(Att_hat), "rho_H_hat": float(rho_H_hat)}


def main() -> int:
    t_start = time.perf_counter()
    raw = load_lane3()
    H_all = lane3_pool("pk_human", TRAIT, raw)
    M_all = lane3_pool(POOL, TRAIT, raw)
    print(f"lane 3: human {H_all.name} n={len(H_all)} bal={H_all.balance:.4f} | "
          f"machine {M_all.name} n={len(M_all)} bal={M_all.balance:.4f}")

    # Disjoint held-out references. SPEC 3.2 generates its reference on demand; with no
    # generation budget the reference is a held-out split, and it must be disjoint from the
    # injected texts AND from the respondent base or the estimator reads its own input back.
    # Frozen calibration split (SPEC-FIXES-ROUND3.md fix 1): keyed on pool identity, not cell_seed.
    M_inj, M_ref = calibration_split(M_all, frac=0.5)
    H_base, H_ref = calibration_split(H_all, frac=0.5)
    check("references disjoint from injection pools",
          not (set(t.text_id for t in M_inj.texts) & set(M_ref.text_ids))
          and not (set(t.text_id for t in H_base.texts) & set(H_ref.text_ids)),
          f"machine {len(M_inj)}/{len(M_ref)}, human {len(H_base)}/{len(H_ref)}")

    mu_h, sd_h = float(H_base.scores.mean()), float(H_base.scores.std(ddof=0))
    Href_std = (H_ref.scores - mu_h) / sd_h
    Mref_std = (M_ref.scores - mu_h) / sd_h

    # ---- adjusted-count calibration (lane 3 FIXES-DONE, 2026-09-07 21:03) ---------------
    # Section 5 of this file recorded the adjusted_count branch as unscorable: pk_human.json
    # had no detector_p_machine. It does now, so the branch runs. Threshold, se and sp all
    # come from the HELD-OUT halves -- the survey's own texts never enter the calibration.
    det_Href = reference_detector(H_all, H_ref)
    det_Mref = reference_detector(M_all, M_ref)
    thr = float(np.quantile(det_Href, SP_TARGET))
    sp_cal = float(np.mean(det_Href <= thr))
    se_cal = float(np.mean(det_Mref > thr))
    sp_base = float(np.mean(H_base.detector <= thr))   # what the survey's humans actually do
    se_inj = float(np.mean(M_inj.detector > thr))      # what the injected texts actually do
    print(f"\ndetector: thr={thr:.4f} at target sp={SP_TARGET} | calibration half "
          f"sp={sp_cal:.4f} se={se_cal:.4f} | survey side sp={sp_base:.4f} se={se_inj:.4f} "
          f"| denominator se-(1-sp)={se_cal - (1 - sp_cal):.4f}")

    q1 = H_base.balance
    xh = (H_base.scores - mu_h) / sd_h
    th = (H_base.labels - q1) / np.sqrt(q1 * (1 - q1))
    r_H = float(np.mean((xh - xh.mean()) * th))
    rho_H_true = RHO_T * r_H
    print(f"\nhuman base: n={len(H_base)} q1={q1:.4f} r_H={r_H:.6f} "
          f"(lane 3 full-pool r_H={raw['pk_human']['r_H']['c'+TRAIT]['r']:.6f}) "
          f"rho_H_true={rho_H_true:.6f}")

    # ---- closed form at the realized (g, kappa, delta) --------------------------------
    pred = {p: layer_b_moments(H_base, M_inj, PI, p, RHO_T, q1=q1) for p in ARMS}
    c_pool = pool_coupling(M_inj, q1)
    print(f"\nc_pool: reweighted={c_pool:.6f} raw Cor(x,L)={raw_pool_coupling(M_inj):.6f} "
          f"(lane 3 whole-pool chat_r={raw['labeled_pools'][POOL]['trait_stats']['c'+TRAIT]['chat_r']:.6f})")
    print("\n%-5s %9s %9s %9s %9s %9s %9s %11s" %
          ("p", "c", "kappa", "delta", "g", "Den", "Att", "rho_obs_pred"))
    for p in ARMS:
        m = pred[p]
        print("%-5.2f %9.5f %9.5f %9.5f %9.5f %9.5f %9.5f %11.6f" %
              (p, m["c"], m["kappa"], m["delta"], m["g"], m["Den"], m["Att"], m["rho_obs_pred"]))

    # The held-out split halves both pools, so the pilot's r_H and c_pool are NOT lane 3's
    # whole-pool numbers. Report what the whole pool would have predicted, so the drift the
    # split introduces is visible rather than buried.
    full = {p: layer_b_moments(H_all, M_all, PI, p, RHO_T) for p in ARMS}
    print("whole-pool (no held-out split) comparison: r_H=%.6f c_pool=%.6f -> "
          "contrast %.6f vs split-half %.6f"
          % (full[0.0]["r_H"], pool_coupling(M_all, H_all.balance),
             full[1.0]["rho_obs_pred"] - full[0.0]["rho_obs_pred"],
             pred[1.0]["rho_obs_pred"] - pred[0.0]["rho_obs_pred"]))

    check("(E7) closed form == direct mixture correlation, all arms",
          all(pred[p]["e7_abs_error"] < 1e-13 for p in ARMS),
          "max |rho_pred - rho_direct| = %.2e" % max(pred[p]["e7_abs_error"] for p in ARMS))
    check("(E67) c(p) = p * c_pool exactly",
          all(abs(pred[p]["c"] - p * c_pool) < 1e-12 for p in ARMS),
          "max dev = %.2e" % max(abs(pred[p]["c"] - p * c_pool) for p in ARMS))
    check("(E67) kappa, delta invariant in p",
          max(abs(pred[p]["kappa"] - pred[0.0]["kappa"]) for p in ARMS) < 1e-12
          and max(abs(pred[p]["delta"] - pred[0.0]["delta"]) for p in ARMS) < 1e-12,
          "kappa=%.6f delta=%.6f at every p" % (pred[0.0]["kappa"], pred[0.0]["delta"]))
    g1 = pred[1.0]["g"]
    m_s = (M_inj.scores - mu_h) / sd_h
    lm = M_inj.labels
    g_ratio = float((m_s[lm == 1].mean() - m_s[lm == 0].mean()) /
                    (xh[H_base.labels == 1].mean() - xh[H_base.labels == 0].mean()))
    check("g by (E66) covariance ratio == g by label-mean-difference ratio",
          abs(g1 - g_ratio) / abs(g_ratio) < 0.02,
          f"cov form {g1:.5f} vs label-mean form {g_ratio:.5f} "
          f"(lane 3 reports {raw['labeled_pools'][POOL]['trait_stats']['c'+TRAIT]['g']:.5f})")

    # ---- capacity ---------------------------------------------------------------------
    n_m = int(round(N * PI))
    lab_typ = (np.random.default_rng(1).random(n_m) < q1).astype(int)
    cap = {p: capacity_report(lab_typ, M_inj, p, q1=q1) for p in ARMS}
    check("without-replacement capacity holds at every arm",
          all(d <= a for p in ARMS for d, a in cap[p].values()),
          "worst cell: demand %.1f of %d" % max(
              ((d, a) for p in ARMS for d, a in cap[p].values()), key=lambda t: t[0] / t[1]))

    # ---- Monte Carlo ------------------------------------------------------------------
    print(f"\nrunning {REPS} replicates x {len(ARMS)} arms at n={N}, pi={PI} ...")
    res: dict[float, dict[str, list]] = {
        p: {k: [] for k in ("rho_obs", "c_real", "Att_real", "kappa_real", "delta_real",
                            "pi_hat", "Att_hat", "rho_H_hat", "pi_hat_or", "rho_H_hat_or",
                            "rho_H_hat_c0", "flag_rate", "pi_ac")} for p in ARMS}
    detector_note = ""
    for r in range(REPS):
        for p in ARMS:
            rng = np.random.default_rng([SEED, r, int(p * 100)])
            inj = build_injected_sample(H_base, M_inj, N, PI, p, rng,
                                        rho_T=RHO_T, k_chunks=K_CHUNKS)
            s = inj.sample
            x, w = inj.x_full, s.w
            mpos = np.flatnonzero(s.A == 1)
            d = res[p]
            d["rho_obs"].append(_pearson(x, w))
            d["c_real"].append(realized_coupling(x[mpos], s.theta[mpos]))
            d["Att_real"].append(_pearson(x, w) / rho_H_true)
            d["kappa_real"].append(float(np.var(x[mpos], ddof=1)))
            d["delta_real"].append(float(-np.mean(x[mpos])))
            fr = float(np.mean(np.asarray(s.F) > thr))
            d["flag_rate"].append(fr)
            d["pi_ac"].append(_adjusted_count_pi(fr, se_cal, sp_cal)[0])
            e = eiv_correct(x, w, Mref_std, Href_std, r_H, c_known=p * c_pool)
            d["pi_hat"].append(e["pi_hat"]); d["Att_hat"].append(e["Att_hat"])
            d["rho_H_hat"].append(e["rho_H_hat"])
            e0 = eiv_correct(x, w, Mref_std, Href_std, r_H, c_known=0.0)
            d["rho_H_hat_c0"].append(e0["rho_H_hat"])
            eo = eiv_correct(x, w, Mref_std, Href_std, r_H, c_known=p * c_pool, pi_fixed=PI)
            d["pi_hat_or"].append(eo["pi_hat"]); d["rho_H_hat_or"].append(eo["rho_H_hat"])
            if not detector_note:
                detector_note = inj.provenance["detector"]
        if (r + 1) % 25 == 0:
            print(f"  {r + 1}/{REPS}  ({time.perf_counter() - t_start:.1f}s)")

    A = {p: {k: np.array(v, dtype=float) for k, v in d.items()} for p, d in res.items()}

    # ---- realized vs predicted ---------------------------------------------------------
    print("\n%-5s %-10s %11s %11s %11s %8s" % ("p", "quantity", "predicted", "MC mean", "MCSE", "z"))
    ok_recover = True
    for p in ARMS:
        for key, pk_ in (("c_real", "c"), ("kappa_real", "kappa"), ("delta_real", "delta"),
                         ("rho_obs", "rho_obs_pred"), ("Att_real", "Att")):
            v = A[p][key]; predv = pred[p][pk_]
            se = mcse(v); z = (float(np.nanmean(v)) - predv) / se if se > 0 else float("nan")
            print("%-5.2f %-10s %11.6f %11.6f %11.6f %8.2f" %
                  (p, pk_, predv, float(np.nanmean(v)), se, z))
            if abs(z) > 4.0:
                ok_recover = False
    check("every realized moment within 4 MCSE of its closed form", ok_recover,
          f"{len(ARMS)} arms x 5 quantities over {REPS} replicates")

    # ---- the contrast -------------------------------------------------------------------
    d_pred = pred[1.0]["rho_obs_pred"] - pred[0.0]["rho_obs_pred"]
    diff = A[1.0]["rho_obs"] - A[0.0]["rho_obs"]  # arms share no rng stream: independent
    d_obs, d_se = float(np.mean(diff)), mcse(diff)
    se_rep = float(np.std(diff, ddof=1))
    z_rep = d_pred / se_rep
    reps_needed = int(np.ceil((2.8 * se_rep / d_pred) ** 2))
    print(f"\nmatched-vs-random contrast: predicted {d_pred:.6f}, observed {d_obs:.6f} "
          f"+/- {d_se:.6f} (MCSE)")
    print(f"  per-replicate SD of the contrast {se_rep:.5f} -> z at ONE replicate = {z_rep:.2f}"
          f"; z over {REPS} replicates = {d_obs / d_se:.2f}; reps for z>=2.8 at n={N}: {reps_needed}")
    check("contrast resolvable at this (n, reps)", d_obs / d_se >= 2.8,
          f"z = {d_obs / d_se:.2f} over {REPS} reps; a SINGLE replicate gives z = {z_rep:.2f}, "
          "so the contrast is a design-level claim, not a per-survey one")
    check("observed contrast agrees with (E7)", abs(d_obs - d_pred) / d_se < 4.0,
          f"|obs - pred| = {abs(d_obs - d_pred):.6f} = {abs(d_obs - d_pred) / d_se:.2f} MCSE")

    # ---- estimator recovery --------------------------------------------------------------
    print("\n%-5s %-16s %11s %11s %11s" % ("p", "estimator", "target", "mean", "bias"))
    ok_pi = ok_rho = True
    for p in ARMS:
        for key, tgt, lbl in (("pi_hat", PI, "pi (dist-match)"),
                              ("pi_ac", PI, "pi (adj. count)"),
                              ("rho_H_hat", rho_H_true, "rho_H (c known)"),
                              ("rho_H_hat_or", rho_H_true, "rho_H (pi oracle)"),
                              ("rho_H_hat_c0", rho_H_true, "rho_H (c=0 assumed)")):
            v = A[p][key]; mu = float(np.nanmean(v))
            print("%-5.2f %-16s %11.6f %11.6f %+11.6f" % (p, lbl, tgt, mu, mu - tgt))
            if key == "pi_hat" and abs(mu - tgt) > 0.01:
                ok_pi = False
            if key == "rho_H_hat" and abs(mu - tgt) > 0.25 * abs(tgt):
                ok_rho = False
    pi_means = np.array([float(np.nanmean(A[p]["pi_hat"])) for p in ARMS])
    pi_ses = np.array([mcse(A[p]["pi_hat"]) for p in ARMS])
    check("label-free prevalence unbiased for pi=0.10 (tol 0.01) at every arm", ok_pi,
          "distribution match vs a disjoint held-out machine reference: mean pi_hat "
          + ", ".join("%.4f+-%.4f" % (m, s_) for m, s_ in zip(pi_means, pi_ses))
          + " -- bias %.4f = %.1f MCSE" % (pi_means.mean() - PI,
                                           (pi_means.mean() - PI) / pi_ses.mean()))
    check("(E67) prevalence estimate invariant in p",
          float(np.max(np.abs(pi_means - pi_means.mean()))) < 3 * float(pi_ses.max()),
          "pi_hat reads only x, whose marginal law (E67) says is p-free: spread %.4f "
          "vs MCSE %.4f" % (pi_means.max() - pi_means.min(), pi_ses.max()))
    check("EIV correction recovers rho_H within 25% at every arm", ok_rho,
          f"target rho_H = rho_T * r_H = {rho_H_true:.6f}")
    ac = np.array([float(np.nanmean(A[p]["pi_ac"])) for p in ARMS])
    ac_se = np.array([mcse(A[p]["pi_ac"]) for p in ARMS])
    check("adjusted-count prevalence branch scored",
          bool(np.all(np.isfinite(ac))) and
          bool(np.nanmax([np.nanmax(A[p]["flag_rate"]) for p in ARMS]) > 0),
          "held-out operating point: thr=%.4f sp=%.4f se=%.4f (build's own in-sample "
          "threshold, not used here: %s)" % (thr, sp_cal, se_cal, detector_note))
    # The branch is scorable now, and it is biased -- by an amount the two calibration
    # transfer gaps predict exactly. Writing flag_rate = pi*se_inj + (1-pi)*(1-sp_base) and
    # inverting with the reference half's (se_cal, sp_cal),
    #   bias = [pi*(se_inj - se_cal) + (1-pi)*((1-sp_base) - (1-sp_cal))] / (se_cal - fpr_cal)
    # -- a sensitivity term and a false-positive-rate term, both divided by the denominator.
    # LAYERB-SWEEP.md confirms this on 15 machine cells: it explains 99.6% of the variance.
    den_ac = se_cal - (1 - sp_cal)
    bias_se_term = PI * (se_inj - se_cal) / den_ac
    bias_fpr_term = (1 - PI) * ((1 - sp_base) - (1 - sp_cal)) / den_ac
    predicted_bias = bias_se_term + bias_fpr_term
    check("adjusted-count prevalence unbiased for pi=0.10 (tol 0.01) at every arm",
          bool(np.all(np.abs(ac - PI) <= 0.01)),
          "mean pi_hat_ac " + ", ".join("%.4f+-%.4f" % (m, s_) for m, s_ in zip(ac, ac_se))
          + " -- bias %+.4f; calibration transfer predicts %+.4f of it (se term %+.4f from "
            "se %.4f->%.4f, fpr term %+.4f from sp %.4f->%.4f, denominator %.4f)"
          % (ac.mean() - PI, predicted_bias, bias_se_term, se_cal, se_inj,
             bias_fpr_term, sp_cal, sp_base, den_ac))

    out = {
        "cell": {"trait": TRAIT, "pool": POOL, "n": N, "pi": PI, "rho_T": RHO_T,
                 "k_chunks": K_CHUNKS, "reps": REPS, "arms": list(ARMS), "seed": SEED,
                 "split_id": split_id(M_ref, H_ref)},
        "base": {"human_n": len(H_base), "machine_n": len(M_inj), "q1": q1, "r_H": r_H,
                 "rho_H_true": rho_H_true, "c_pool": c_pool,
                 "c_pool_raw": raw_pool_coupling(M_inj)},
        "predicted": {str(p): pred[p] for p in ARMS},
        "monte_carlo": {str(p): {k: {"mean": float(np.nanmean(v)), "mcse": mcse(v)}
                                 for k, v in A[p].items()} for p in ARMS},
        "contrast": {"predicted": d_pred, "observed": d_obs, "mcse": d_se,
                     "sd_per_replicate": se_rep, "z_one_replicate": z_rep,
                     "z_over_reps": d_obs / d_se, "reps_for_z2.8": reps_needed},
        "detector": {"build_in_sample_note": detector_note, "threshold": thr, "sp_target": SP_TARGET,
                     "sp_calibration_half": sp_cal, "se_calibration_half": se_cal,
                     "sp_survey_base": sp_base, "se_injected_texts": se_inj,
                     "denominator": se_cal - (1 - sp_cal),
                     "bias_predicted_by_transfer": predicted_bias,
                     "bias_se_term": bias_se_term, "bias_fpr_term": bias_fpr_term},
        "checks": {"total": _CHECKS, "failed": _FAILURES},
        "seconds": time.perf_counter() - t_start,
    }
    Path("results").mkdir(exist_ok=True)
    Path("results/layerb_pilot.json").write_text(json.dumps(out, indent=2))
    print(f"\n{_CHECKS - len(_FAILURES)}/{_CHECKS} checks passed "
          f"in {time.perf_counter() - t_start:.1f}s -> results/layerb_pilot.json")
    if _FAILURES:
        print("FAILED: " + ", ".join(_FAILURES))
    return 1 if _FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
