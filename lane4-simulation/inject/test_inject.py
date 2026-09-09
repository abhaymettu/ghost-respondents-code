"""Layer B injection tests.

    lane4-simulation/.venv/bin/python -m inject.test_inject

Plain script, no pytest (the venv has none). Every check prints PASS/FAIL and the run
exits non-zero if any fails. The E67 checks are EXACT (1e-14): the assignment law is a
finite mixture over a finite pool, so its moments are arithmetic, not Monte Carlo.
"""

from __future__ import annotations

import sys
from dataclasses import replace as dc_replace

import numpy as np

from dgp import Sample

from .assign import (
    PoolCapacityError,
    assign_indices,
    assignment_moments,
    pool_coupling,
    raw_pool_coupling,
    realized_coupling,
)
from . import build as build_mod
from .build import build_injected_sample, detector_flags, exact_mixture_law, layer_b_moments
from .pools import (
    CALIBRATION_SEED,
    LANE3_MEASUREMENTS,
    LANE3_TRAITS,
    Pool,
    PoolContractError,
    PoolText,
    calibration_split,
    calibration_stream,
    chunk_text,
    lane3_labeled_pools,
    lane3_pool,
    lane3_scores_path,
    lane3_trait_key,
    load_lane3,
    load_measurements,
    normalize_measurements,
    personallm_label,
    split_id,
    split_reference,
    synthetic_pool,
    transfer_reference,
)

RESULTS: list[tuple[str, bool, str]] = []
EXACT = 1e-13


def check(name: str, cond: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))


def mc_tol(n: int, mult: float = 4.0) -> float:
    return mult / np.sqrt(n)


def _with_detector(pool: Pool, rng, shift: float) -> Pool:
    texts = [
        PoolText(t.text_id, t.label, t.score, detector=float(shift + rng.standard_normal()),
                 chunk_scores=t.chunk_scores, n_words=t.n_words, path=t.path)
        for t in pool.texts
    ]
    return Pool(pool.name, pool.trait, texts, pool.kind, pool.generator, pool.source)


def _with_chunks(pool: Pool, rng, k: int) -> Pool:
    texts = []
    for t in pool.texts:
        cs = tuple(float(t.score + 0.4 * rng.standard_normal()) for _ in range(k))
        texts.append(PoolText(t.text_id, t.label, t.score, t.detector, cs, t.n_words, t.path))
    return Pool(pool.name, pool.trait, texts, pool.kind, pool.generator, pool.source)


P_GRID = (0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0)


# ------------------------------------------------------------------ (a) E67, exact
def test_e67_exact_balanced() -> None:
    rng = np.random.default_rng(11)
    pool = synthetic_pool(rng, 400, c_pool=0.55, balance=0.5)
    c1 = pool_coupling(pool, q1=0.5)
    base = assignment_moments(pool, 0.0, q1=0.5)
    err_c = max(abs(assignment_moments(pool, p, 0.5).c - p * c1) for p in P_GRID)
    err_v = max(abs(assignment_moments(pool, p, 0.5).var - base.var) for p in P_GRID)
    err_m = max(abs(assignment_moments(pool, p, 0.5).mean - base.mean) for p in P_GRID)
    check("E67 c(p) = p * c_pool exactly (balanced pool)", err_c < EXACT, f"max err {err_c:.2e}")
    check("E67 kappa invariant in p (balanced pool)", err_v < EXACT, f"max err {err_v:.2e}")
    check("E67 delta invariant in p (balanced pool)", err_m < EXACT, f"max err {err_m:.2e}")


# ------------------------------------------------ (b) E67 by Monte Carlo, weaker check
def test_e67_monte_carlo() -> None:
    rng = np.random.default_rng(12)
    pool = synthetic_pool(rng, 600, c_pool=0.5, balance=0.5)
    n = 40000
    labels = rng.integers(0, 2, size=n)
    ok = True
    worst = 0.0
    for p in (0.0, 0.5, 1.0):
        idx = assign_indices(rng, labels, pool, p, replace=True)
        c_hat = realized_coupling(pool.scores[idx], labels)
        target = p * pool_coupling(pool, q1=float(labels.mean()))
        worst = max(worst, abs(c_hat - target))
        ok &= abs(c_hat - target) < mc_tol(n, 5.0)
    check("E67 holds in Monte Carlo within 5 MCSE", ok, f"worst |c_hat - p*c_pool| {worst:.4f}")


# --------------------------- (c) unbalanced POOL: hook exact, naive 'pool' mode broken
def test_unbalanced_pool() -> None:
    rng = np.random.default_rng(13)
    pool = synthetic_pool(rng, 500, c_pool=0.5, balance=0.8)
    c1 = pool_coupling(pool, q1=0.5, mode="respondent_marginal")
    err = max(abs(assignment_moments(pool, p, 0.5, "respondent_marginal").c - p * c1)
              for p in P_GRID)
    check("E67 exact on an UNBALANCED pool with the reweighting hook", err < EXACT,
          f"max err {err:.2e}, pool balance {pool.balance:.2f}")

    v = [assignment_moments(pool, p, 0.5, "pool").var for p in P_GRID]
    c_naive = [assignment_moments(pool, p, 0.5, "pool").c for p in P_GRID]
    c1n = c_naive[-1]
    dev = max(abs(cn - p * c1n) for p, cn in zip(P_GRID, c_naive))
    check("naive 'pool' mode DOES break E67 (so the hook is necessary, not cosmetic)",
          dev > 1e-3 or (max(v) - min(v)) > 1e-3,
          f"max |c(p) - p*c_pool| {dev:.4f}, kappa spread {max(v) - min(v):.4f}")


# ------------------- (d) unbalanced RESPONDENTS: hook exact, 'balanced' (memo) broken
def test_unbalanced_respondents() -> None:
    rng = np.random.default_rng(14)
    pool = synthetic_pool(rng, 500, c_pool=0.8, balance=0.5)
    q1 = 0.1
    c1 = pool_coupling(pool, q1=q1, mode="respondent_marginal")
    err = max(abs(assignment_moments(pool, p, q1, "respondent_marginal").c - p * c1)
              for p in P_GRID)
    check("E67 exact with UNBALANCED respondent labels (hook)", err < EXACT,
          f"max err {err:.2e}, q1={q1}")

    cb = [assignment_moments(pool, p, q1, "balanced").c for p in P_GRID]
    devb = max(abs(cn - p * cb[-1]) for p, cn in zip(P_GRID, cb))
    check("memo-as-written 'balanced' branch breaks under respondent imbalance",
          devb > 1e-3, f"max |c(p) - p*c_pool| {devb:.4f}")


# ------------------------------------- (e) with/without replacement, capacity failure
def test_replacement_and_capacity() -> None:
    rng = np.random.default_rng(15)
    pool = synthetic_pool(rng, 4000, c_pool=0.5, balance=0.5)
    n = 1200
    labels = rng.integers(0, 2, size=n)
    c_wo = realized_coupling(pool.scores[assign_indices(rng, labels, pool, 0.6)], labels)
    c_wr = realized_coupling(
        pool.scores[assign_indices(rng, labels, pool, 0.6, replace=True)], labels)
    check("without-replacement agrees with with-replacement within MC error",
          abs(c_wo - c_wr) < mc_tol(n, 6.0), f"{c_wo:.4f} vs {c_wr:.4f}")

    small = synthetic_pool(rng, 40, c_pool=0.5, balance=0.5, name="tiny")
    raised = ""
    try:
        assign_indices(rng, rng.integers(0, 2, size=300), small, 1.0)
    except PoolCapacityError as e:
        raised = str(e)
    check("exhausting a label cell raises PoolCapacityError, no silent fallback",
          "exceeds" in raised and "tiny" in raised, raised[:80])


# -------------------------------------------------------------- (f) chunking is lossless
def test_chunk_text() -> None:
    words = [f"w{i}" for i in range(97)]
    text = " ".join(words)
    ok_all = True
    for k in (1, 2, 3, 4, 7):
        parts = chunk_text(text, k)
        ok_all &= len(parts) == k
        ok_all &= " ".join(parts).split() == words
        ok_all &= all(len(p.split()) > 0 for p in parts)
    check("chunk_text partitions into k non-empty chunks losslessly", ok_all, "k in 1,2,3,4,7")
    too_short = ""
    try:
        chunk_text("one two", 5)
    except ValueError as e:
        too_short = str(e)
    check("chunk_text refuses a text too short for k chunks (no empty pseudo-items)",
          "cannot make" in too_short, too_short[:60])


# ------------------------------------------------------- (g) reference splits, transfer
def test_reference_splits() -> None:
    rng = np.random.default_rng(16)
    pool = synthetic_pool(rng, 300, c_pool=0.4, balance=0.5)
    inj_pool, ref = split_reference(pool, rng, frac=0.3)
    ids_i = {t.text_id for t in inj_pool.texts}
    check("held-out reference is disjoint from the injection pool",
          not (ids_i & set(ref.text_ids)) and len(ref.scores) > 0,
          f"{len(inj_pool)} injected / {len(ref.scores)} reference")

    other = synthetic_pool(rng, 120, c_pool=0.4, name="other_gen")
    tr = transfer_reference(other, injected_from=inj_pool)
    check("transfer reference accepts a different pool", tr.kind == "transfer", tr.name)
    bad = False
    try:
        transfer_reference(inj_pool, injected_from=inj_pool)
    except ValueError:
        bad = True
    check("transfer reference REFUSES the pool being injected from", bad)


# ------------------------------ (g2) the frozen calibration split (SPEC-FIXES-ROUND3.md fix 1)
def test_frozen_calibration_split() -> None:
    """LAYERB-ROUND3.md 1.2/2.3: the calibration split must be the same texts at every wave.

    The sweeps drew it from `default_rng(base + 1000 * cell_index)`, which makes the split a
    function of a cell's POSITION in a loop. These checks pin it to the pool's identity
    instead, and the third one shows the old pattern really did move -- so the fix is not
    checking something that was already true.
    """
    rng = np.random.default_rng(4242)
    M = synthetic_pool(rng, 300, c_pool=0.5, name="mach_a", balance=0.5)
    M2 = synthetic_pool(rng, 300, c_pool=0.5, name="mach_b", balance=0.5)
    H = synthetic_pool(rng, 400, c_pool=0.3, name="pk_human", balance=0.4, kind="human")

    inj_a, ref_a = calibration_split(M)
    inj_b, ref_b = calibration_split(M)
    check("calibration split is deterministic across calls",
          ref_a.text_ids == ref_b.text_ids
          and [t.text_id for t in inj_a.texts] == [t.text_id for t in inj_b.texts],
          f"{len(ref_a.text_ids)} held out of {len(M)}")

    # wave 2: unrelated draws in between, and the human pool visited in a different order
    np.random.default_rng(99).permutation(1000)
    _, ref_h_alone = calibration_split(H)
    calibration_split(M2)
    _, ref_h_after_m2 = calibration_split(H)
    _, ref_a2 = calibration_split(M)
    check("the split ignores caller RNG state, cell ordering, and which pools preceded it",
          ref_h_alone.text_ids == ref_h_after_m2.text_ids and ref_a2.text_ids == ref_a.text_ids)

    rng_old = np.random.default_rng(20260907)          # the sweep's cell 0
    split_reference(M, rng_old)
    _, old_h0 = split_reference(H, rng_old)            # human split rides the machine split
    _, old_h1 = split_reference(H, np.random.default_rng(20260907 + 1000))   # cell 1
    check("the old per-cell pattern really did move the reference (fix is not vacuous)",
          old_h0.text_ids != old_h1.text_ids,
          f"{len(set(old_h0.text_ids) ^ set(old_h1.text_ids))} ids differ between cells")

    _, ref_shift = calibration_split(M, seed=CALIBRATION_SEED + 1)
    check("the master seed is live: changing it re-draws the split",
          ref_shift.text_ids != ref_a.text_ids)
    check("the stream is a function of the pool name and the seed alone",
          calibration_stream(M).integers(0, 2 ** 32, 8).tolist()
          == calibration_stream(M.subset(np.arange(0, len(M), 2), name="mach_a"))
          .integers(0, 2 ** 32, 8).tolist())

    check("held-out reference stays disjoint from the injection pool",
          not ({t.text_id for t in inj_a.texts} & set(ref_a.text_ids))
          and len(ref_a.scores) == len(M) - len(inj_a))

    _, ref_h = calibration_split(H)
    check("split_id is equal iff the held-out ids are equal",
          split_id(ref_a, ref_h) == split_id(ref_a2, ref_h_after_m2)
          and split_id(ref_a, ref_h) != split_id(ref_shift, ref_h)
          and split_id(ref_a, ref_h) != split_id(ref_h, ref_a),
          split_id(ref_a, ref_h))
    check("split_id is a content hash, not an ordering hash",
          split_id(dc_replace(ref_a, text_ids=tuple(reversed(ref_a.text_ids))))
          == split_id(ref_a))


# ---------------------------------------------- (h) Sample contract, exact n and pi counts
def test_sample_contract() -> None:
    rng = np.random.default_rng(17)
    human = synthetic_pool(rng, 2467, c_pool=0.35, balance=0.245, kind="human", name="pk")
    mach = synthetic_pool(rng, 900, c_pool=0.6, balance=0.5, name="gpt4", mean=0.4, sd=1.1)
    n, pi = 800, 0.05
    inj = build_injected_sample(human, mach, n=n, pi=pi, p=0.5, rng=rng, replace=True)
    s = inj.sample
    ok = (
        isinstance(s, Sample)
        and s.theta.shape == (n,) and s.w.shape == (n,) and s.X.shape == (n, 1)
        and s.A.shape == (n,) and s.A.dtype == np.uint8
        and s.F.shape == (n,) and s.flag.shape == (n,) and s.flag.dtype == bool
    )
    check("injected Sample matches the CONVENTIONS field/shape/dtype contract", ok,
          f"X{s.X.shape} A{s.A.dtype} flag{s.flag.dtype}")
    c = s.cell
    check("Layer B Cell NaNs every field that is a Layer A knob but a Layer B outcome",
          all(np.isnan(getattr(c, f)) for f in ("c", "kappa", "rel_H", "delta", "rho_v", "r_F"))
          and c.arm == "layerB",
          "c/kappa/rel_H/delta/rho_v/r_F all NaN")
    se_sp_raised = False
    try:
        c.se_sp
    except (KeyError, AttributeError, ValueError):
        se_sp_raised = True
    check("Cell.se_sp raises on a Layer B cell rather than returning a set (se, sp)",
          se_sp_raised, f"detector={c.detector!r}")
    check("headline indicator X[:, 0] is the whole-text score",
          np.array_equal(s.x, inj.x_full))
    check("exactly round(n*pi) machine respondents", int(s.A.sum()) == round(n * pi),
          f"{int(s.A.sum())} of {n}")
    check("theta is standardized on the drawn sample (mean 0, var 1)",
          abs(s.theta.mean()) < 1e-10 and abs(s.theta.var() - 1) < 1e-10)
    check("machine status is independent of theta (A1): |Cor(A, theta)| small",
          abs(np.corrcoef(s.A.astype(float), s.theta)[0, 1]) < mc_tol(n, 4.0))
    check("machine respondents carry machine-pool text ids",
          all(str(t).startswith("gpt4") for t in inj.text_ids[s.A == 1])
          and all(str(t).startswith("pk") for t in inj.text_ids[s.A == 0]))

    with_det_h = _with_detector(human, rng, 0.0)
    with_det_m = _with_detector(mach, rng, 1.5)
    inj2 = build_injected_sample(with_det_h, with_det_m, n=n, pi=0.2, p=0.5, rng=rng,
                                 sp=0.99, replace=True)
    sp_real = inj2.provenance["realized_sp"]
    check("detector threshold hits the target specificity by construction",
          abs(sp_real - 0.99) < 0.01, f"realized sp {sp_real:.4f}, se {inj2.provenance['realized_se']:.4f}")

    ch_h = _with_chunks(human, rng, 4)
    ch_m = _with_chunks(mach, rng, 4)
    inj3 = build_injected_sample(ch_h, ch_m, n=400, pi=0.1, p=0.5, rng=rng, k_chunks=4,
                                 replace=True)
    check("k_chunks=4 produces 4 pseudo-item columns", inj3.sample.X.shape == (400, 4))
    missing = False
    try:
        build_injected_sample(human, mach, n=400, pi=0.1, p=0.5, rng=rng, k_chunks=4,
                              replace=True)
    except ValueError as e:
        missing = "chunk" in str(e).lower()
    check("k_chunks>1 without chunk scores fails loudly (lane 3 dependency)", missing)


# ------------------------------------------------------- (i) lane 3 loader contract
def test_loader_contract() -> None:
    raised = ""
    try:
        load_measurements("lane3-testbed/pool_measurements.json")
    except (PoolContractError, FileNotFoundError) as e:
        raised = str(e)
    check("missing pool_measurements.json fails with a locatable message",
          "pool_measurements" in raised, raised[:80])

    good = {"pools": {"gpt-4-0613": {"traits": {"EXT": {"g": 1.2, "kappa": 0.8, "delta": 0.3,
                                                        "auc": 0.71, "scores": "x.csv"}}}}}
    norm = normalize_measurements(good)
    check("normalize_measurements accepts the documented shape",
          norm["gpt-4-0613"]["traits"]["EXT"]["kappa"] == 0.8)
    bad = False
    try:
        normalize_measurements({"nonsense": 1})
    except PoolContractError as e:
        bad = "nonsense" in str(e)
    check("an unrecognized shape raises PoolContractError naming the keys seen", bad)
    check("PersonaLLM filename tokens decode to trait labels",
          personallm_label("extr_agre_cons_neur_open_01.txt", "EXT") == 1
          and personallm_label("intr_agre_cons_neur_open_01.txt", "EXT") == 0)


# ----------------------------------------------------------------- (j) E7 on Layer B
def test_e7_layer_b() -> None:
    """E7 against a law enumerated from the assignment RULE, not from the same moments.

    `rho_H * Att` and the mixture correlation assembled from (kappa, delta, g) are the same
    algebraic expression -- `Den` is identically `Var(x)` once the human base sets V_H = 1 --
    so comparing those two proves nothing. `exact_mixture_law` rebuilds the joint law text by
    text from the rule and never touches kappa, delta, g or Att. The mutation check below
    shows the comparison has teeth.
    """
    rng = np.random.default_rng(18)
    human = synthetic_pool(rng, 2467, c_pool=0.35, balance=0.245, kind="human", name="pk")
    mach = synthetic_pool(rng, 900, c_pool=0.6, balance=0.5, name="gpt4", mean=0.4, sd=1.1)
    worst = 0.0
    rows = []
    for pi in (0.0, 0.01, 0.05, 0.1, 0.3, 1.0):
        for p in (0.0, 0.5, 1.0):
            m = layer_b_moments(human, mach, pi=pi, p=p, rho_T=0.5)
            enum = exact_mixture_law(human, mach, pi=pi, p=p, rho_T=0.5)
            worst = max(worst, abs(m["rho_obs_pred"] - enum["rho_obs"]))
            rows.append(m)
    check("E7 rho_obs = rho_H * Att matches the independently enumerated law", worst < 1e-13,
          f"max |Att path - enumerated| {worst:.2e} over 18 (pi, p) cells")

    # non-vacuity: corrupt assignment_moments and the check must FAIL
    real = build_mod.assignment_moments

    def corrupt(pool, p, q1=0.5, mode="respondent_marginal"):
        m = real(pool, p, q1, mode)
        return dc_replace(m, var=m.var * 1.01)

    def corrupt_c(pool, p, q1=0.5, mode="respondent_marginal"):
        m = real(pool, p, q1, mode)
        return dc_replace(m, c=m.c * 1.01)

    truth = exact_mixture_law(human, mach, pi=0.3, p=0.5)["rho_obs"]
    gaps = {}
    for label, fn in (("kappa", corrupt), ("c", corrupt_c)):
        build_mod.assignment_moments = fn
        try:
            bad = layer_b_moments(human, mach, pi=0.3, p=0.5, rho_T=0.5)
        finally:
            build_mod.assignment_moments = real
        gaps[label] = abs(bad["rho_obs_pred"] - truth)
    # the real check runs at 1e-13; a 1% error must land orders of magnitude above that
    check("that comparison is NOT vacuous: a 1% error in kappa or c breaks it",
          min(gaps.values()) > 1e-10,
          f"kappa {gaps['kappa']:.1e}, c {gaps['c']:.1e} vs clean {worst:.1e} (tol 1e-13)")

    check("the internal Att algebra is self-consistent (Den == Var(x))",
          max(r["e7_abs_error"] for r in rows) < 1e-13,
          f"max {max(r['e7_abs_error'] for r in rows):.2e} -- an identity, not a design check")

    linear = [r for r in rows if r["pi"] == 0.1]
    g0, g1 = linear[0]["g"], linear[2]["g"]
    check("g is linear in p (E66 inherits E67)", abs(linear[1]["g"] - 0.5 * (g0 + g1)) < 1e-12,
          f"g(0)={g0:.4f} g(.5)={linear[1]['g']:.4f} g(1)={g1:.4f}")
    check("kappa and delta do not move with p",
          abs(linear[0]["kappa"] - linear[2]["kappa"]) < 1e-12
          and abs(linear[0]["delta"] - linear[2]["delta"]) < 1e-12,
          f"kappa={linear[0]['kappa']:.4f} delta={linear[0]['delta']:.4f}")

    m = layer_b_moments(human, mach, pi=0.0, p=1.0)
    check("pi = 0 recovers Att = 1 exactly", abs(m["Att"] - 1.0) < 1e-14)


# --------------------------------------------- Monte Carlo corroboration of layer_b_moments
def test_moments_match_simulation() -> None:
    rng = np.random.default_rng(19)
    human = synthetic_pool(rng, 3000, c_pool=0.4, balance=0.5, kind="human", name="pk")
    mach = synthetic_pool(rng, 2000, c_pool=0.6, balance=0.5, name="gpt4", mean=0.3, sd=1.2)
    n, pi, p = 20000, 0.2, 0.5
    inj = build_injected_sample(human, mach, n=n, pi=pi, p=p, rng=rng, rho_T=0.5, replace=True)
    s = inj.sample
    rho_obs = float(np.corrcoef(s.x, s.w)[0, 1])
    m = layer_b_moments(human, mach, pi=pi, p=p, rho_T=0.5, q1=human.balance)
    check("simulated rho_obs matches the exact Layer B prediction",
          abs(rho_obs - m["rho_obs_pred"]) < mc_tol(n, 6.0),
          f"sim {rho_obs:.4f} vs exact {m['rho_obs_pred']:.4f}")
    kappa_sim = float(s.x[s.A == 1].var() / s.x[s.A == 0].var())
    check("simulated kappa matches the exact prediction",
          abs(kappa_sim - m["kappa"]) < mc_tol(int(s.A.sum()), 8.0),
          f"sim {kappa_sim:.4f} vs exact {m['kappa']:.4f}")
    c_sim = realized_coupling(s.x[s.A == 1], (s.theta[s.A == 1] > 0).astype(int))
    check("simulated coupling matches p * c_pool",
          abs(c_sim - m["c"]) < mc_tol(int(s.A.sum()), 6.0),
          f"sim {c_sim:.4f} vs exact {m['c']:.4f}")


# ------------------------------------------------------- c_pool: reweighted vs lane 3 raw
def test_c_pool_definitions() -> None:
    rng = np.random.default_rng(20)
    bal = synthetic_pool(rng, 800, c_pool=0.5, balance=0.5)
    unbal = synthetic_pool(rng, 800, c_pool=0.5, balance=0.8)
    check("on a BALANCED pool the design's c_pool equals lane 3's raw c-hat",
          abs(pool_coupling(bal, q1=0.5) - raw_pool_coupling(bal)) < 1e-12,
          f"{pool_coupling(bal, 0.5):.6f} vs {raw_pool_coupling(bal):.6f}")
    d = abs(pool_coupling(unbal, q1=0.5) - raw_pool_coupling(unbal))
    check("on an UNBALANCED pool they DIFFER (INJECT.md says which goes in the paper)",
          d > 1e-3, f"reweighted {pool_coupling(unbal, 0.5):.4f} vs raw {raw_pool_coupling(unbal):.4f}")


# --------------------------------------------------- lane 3's real files, as they shipped
# Everything above runs on synthetic pools and needs no lane 3. These read
# ../lane3-testbed/ and SKIP (not fail) when it is absent, so the suite stays runnable in a
# checkout that has lane 4 only.
def test_lane3_real_files() -> None:
    if not LANE3_MEASUREMENTS.exists():
        print(f"  SKIP: no lane 3 measurements at {LANE3_MEASUREMENTS}")
        return
    raw = load_lane3()
    names = lane3_labeled_pools(raw)
    check("lane 3 ships the four labeled pools",
          len(names) == 4 and "big5_personality_essays" in names, ", ".join(names))

    # The trap this loader exists for: openness is cOPN, NOT c + the PersonaLLM token OPE.
    check("openness resolves to lane 3's cOPN, not cOPE",
          lane3_trait_key("OPE") == "cOPN" and lane3_trait_key("OPN") == "cOPN",
          f'OPE -> {lane3_trait_key("OPE")!r}')
    try:
        lane3_trait_key("cOPE")
    except PoolContractError as exc:
        check("an unknown trait raises rather than silently reading the wrong column",
              "cOPE" in str(exc), str(exc)[:70])
    else:
        check("an unknown trait raises rather than silently reading the wrong column",
              False, "lane3_trait_key('cOPE') returned instead of raising")

    n_cells = 0
    bad: list[str] = []
    for name in names:
        for trait in LANE3_TRAITS:
            pool = lane3_pool(name, trait, raw)
            n_cells += 1
            if len(pool) < 100:
                bad.append(f"{name}/{trait}: n={len(pool)}")
            if set(pool.labels) != {0, 1}:
                bad.append(f"{name}/{trait}: labels {sorted(set(pool.labels))}")
            if not np.all(np.isfinite(pool.scores)):
                bad.append(f"{name}/{trait}: non-finite scores")
            if not np.all(np.isfinite(pool.detector)):
                bad.append(f"{name}/{trait}: non-finite detector")
    check("all 20 labeled cells load with binary labels and finite scores",
          n_cells == 20 and not bad, "; ".join(bad) if bad else "4 pools x 5 traits")

    # Both sides carry per-text detector scores as of lane 3's FIXES-DONE (2026-09-07 21:03):
    # pool_measurement.py:253 had discarded the PK-human half of the AUC pass, which blocked
    # SPEC 3.2's adjusted_count branch (it needs sp from HUMAN detector scores).
    p4 = lane3_pool("personallm_gpt-4-0613", "EXT", raw)
    pk = lane3_pool("pk_human", "EXT", raw)
    det_pk = pk.detector
    check("both the labeled pools and pk_human carry detector_p_machine (lane 3 FIXES-DONE)",
          p4.metrics["has_detector"] and pk.metrics["has_detector"]
          and det_pk.size == len(pk) and np.all(np.isfinite(det_pk))
          and float(det_pk.min()) >= 0.0 and float(det_pk.max()) <= 1.0,
          f"pk_human {det_pk.size}/{len(pk)} finite in [0,1], "
          f"mean p_machine {float(det_pk.mean()):.4f}")
    check("pk_human loads as the human pool with a scalar r_H",
          pk.kind == "human" and isinstance(pk.metrics.get("r_H"), float),
          f"kind={pk.kind} r_H={pk.metrics.get('r_H')}")

    # Trait slicing: a different trait must give a different score column, and the score
    # column must be the one lane 3 filed under that trait key.
    import json
    with lane3_scores_path("personallm_gpt-4-0613", raw).open() as fh:
        blob = json.load(fh)
    ope = lane3_pool("personallm_gpt-4-0613", "OPE", raw)
    check("the trait slice is lane 3's own column, verbatim",
          np.allclose(ope.scores, np.array(blob["trait_scores"]["cOPN"], dtype=float))
          and not np.allclose(ope.scores, p4.scores),
          "OPE slice == trait_scores['cOPN'] and != the EXT slice")


def test_lane3_chunks() -> None:
    """chunk_1..chunk_k are per-text DICTS of all five traits, with nulls for short texts."""
    if not LANE3_MEASUREMENTS.exists():
        print(f"  SKIP: no lane 3 measurements at {LANE3_MEASUREMENTS}")
        return
    raw = load_lane3()
    import json

    for name, expect_unchunked in (("personallm_gpt-4-0613", 0), ("big5_personality_essays", 65)):
        with lane3_scores_path(name, raw).open() as fh:
            blob = json.load(fh)
        k = blob["chunk_meta"]["k"]
        pool = lane3_pool(name, "OPE", raw)
        lens = np.array([len(t.chunk_scores) for t in pool.texts])
        n_empty = int(np.sum(lens == 0))
        check(f"{name}: chunk widths are k={k} or 0, never partial",
              set(np.unique(lens).tolist()) <= {0, k}, f"widths {sorted(set(lens.tolist()))}")
        check(f"{name}: unchunked count matches lane 3's chunk_meta",
              n_empty == expect_unchunked == blob["chunk_meta"]["n_texts_too_short_to_chunk"],
              f"loader {n_empty}, chunk_meta {blob['chunk_meta']['n_texts_too_short_to_chunk']}, "
              f"expected {expect_unchunked}")
        check(f"{name}: n_unchunked is reported on the pool, not silently swallowed",
              pool.metrics["n_unchunked"] == n_empty and pool.metrics["k_chunks_available"] == k,
              f"n_unchunked={pool.metrics['n_unchunked']} k={pool.metrics['k_chunks_available']}")
        # The values must come from the requested trait's key in each chunk dict, in order.
        i = int(np.flatnonzero(lens == k)[0])
        want = tuple(float(blob[f"chunk_{j}"][i]["cOPN"]) for j in range(1, k + 1))
        check(f"{name}: chunk values are the requested trait, in chunk order",
              pool.texts[i].chunk_scores == want, f"text {pool.texts[i].text_id}: {want}")

    # A pool with any unchunkable text must NOT be silently usable at k > 1:
    # build._chunks_or_none returns None, and build_injected_sample raises on it.
    big5 = lane3_pool("big5_personality_essays", "OPE", raw)
    lens = np.array([len(t.chunk_scores) for t in big5.texts])
    short = np.flatnonzero(lens == 0)
    ok = np.flatnonzero(lens == 4)
    with_short = np.concatenate([ok[:8], short[:1]])
    check("_chunks_or_none refuses an index set containing any unchunkable text",
          build_mod._chunks_or_none(big5, with_short, 4) is None
          and build_mod._chunks_or_none(big5, ok[:8], 4) is not None,
          f"{short.size} of {len(big5)} big5 texts are too short to chunk; a draw that "
          "touches one degrades the whole k=4 matrix to None")


def test_lane3_moments_match() -> None:
    """kappa/delta/chat_r recomputed from the per-text files reproduce lane 3's summary."""
    if not LANE3_MEASUREMENTS.exists():
        print(f"  SKIP: no lane 3 measurements at {LANE3_MEASUREMENTS}")
        return
    raw = load_lane3()
    pk_scores = {t: lane3_pool("pk_human", t, raw).scores for t in LANE3_TRAITS}
    worst = ("", 0.0)
    worst_g = ("", 0.0)
    for name in lane3_labeled_pools(raw):
        for trait in LANE3_TRAITS:
            pool = lane3_pool(name, trait, raw)
            m = pool.metrics
            h = pk_scores[trait]
            mu_H, V_H = float(np.mean(h)), float(np.var(h, ddof=1))
            x = pool.scores
            kappa = float(np.var(x, ddof=1)) / V_H
            delta = (mu_H - float(np.mean(x))) / np.sqrt(V_H)
            chat = raw_pool_coupling(pool)
            for key, mine, theirs in (
                ("kappa", kappa, m["kappa"]),
                ("delta", delta, -m["delta"]),   # lane 3 files the memo sign; see CONVENTIONS
                ("chat_r", chat, m["chat_r"]),
            ):
                d = abs(mine - theirs)
                if d > worst[1]:
                    worst = (f"{name}/{trait} {key}: {mine:.6f} vs {theirs:.6f}", d)
            # g in the covariance form c*sqrt(kappa)/r_H -- the form lane 3 now reports
            # after its fix, and NOT the chat_r/r_H ratio it reported before.
            g = chat * np.sqrt(kappa) / m["r_H"]
            dg = abs(g - m["g"])
            if dg > worst_g[1]:
                worst_g = (f"{name}/{trait}: mine {g:.4f} vs lane 3 {m['g']:.4f}", dg)
    check("kappa, delta, chat_r recomputed from the per-text files match lane 3's summary",
          worst[1] < 5e-4, f"worst {worst[0] or 'exact'} (|d| = {worst[1]:.2e})")
    check("g in the covariance form matches lane 3's post-fix g on all 20 cells",
          worst_g[1] < 5e-3, f"worst {worst_g[0]} (|d| = {worst_g[1]:.2e})")


def test_lane3_injection_runs() -> None:
    """A real lane-3 cell goes end to end: split, standardize, assign, build, moments."""
    if not LANE3_MEASUREMENTS.exists():
        print(f"  SKIP: no lane 3 measurements at {LANE3_MEASUREMENTS}")
        return
    raw = load_lane3()
    rng = np.random.default_rng(4)
    pool = lane3_pool("personallm_llama-2", "CON", raw)
    human = lane3_pool("pk_human", "CON", raw)
    inj, ref = split_reference(pool, rng, frac=0.5)
    base, _ = split_reference(human, rng, frac=0.5)
    mu, sd = float(np.mean(base.scores)), float(np.std(base.scores, ddof=1))
    inj_s = inj.standardized(mu, sd)
    q1 = float(np.mean(base.labels))
    m = assignment_moments(inj_s, p=1.0, q1=q1)
    # 100 machine respondents is the sweep's cell (pi = 0.10 of n = 1000). The 160-text
    # injection half cannot serve many more than that at p = 1 without replacement.
    lab = base.labels[:100]
    idx = assign_indices(rng, lab, inj_s, p=1.0, q1=q1)
    c_real = realized_coupling(inj_s.scores[idx], lab)
    check("a real lane-3 cell assigns at p=1 with the realized c near the exact c",
          abs(c_real - m.c) < 0.2, f"realized {c_real:.4f} vs exact {m.c:.4f} on 100 draws")
    check("the reference split is disjoint from the injection pool",
          not ({t.text_id for t in inj.texts} & set(ref.text_ids)),
          f"{len(inj)} injected / {len(ref)} reference, no shared text id")


def main() -> int:
    for fn in (
        test_e67_exact_balanced,
        test_e67_monte_carlo,
        test_unbalanced_pool,
        test_unbalanced_respondents,
        test_replacement_and_capacity,
        test_chunk_text,
        test_reference_splits,
        test_frozen_calibration_split,
        test_sample_contract,
        test_loader_contract,
        test_e7_layer_b,
        test_moments_match_simulation,
        test_c_pool_definitions,
        test_lane3_real_files,
        test_lane3_chunks,
        test_lane3_moments_match,
        test_lane3_injection_runs,
    ):
        print(f"\n--- {fn.__name__}")
        fn()
    n_pass = sum(1 for _, ok, _ in RESULTS if ok)
    print(f"\n{n_pass}/{len(RESULTS)} checks passed")
    return 0 if n_pass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
