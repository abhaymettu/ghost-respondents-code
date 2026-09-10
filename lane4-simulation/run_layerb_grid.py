"""The Layer B full grid: SPEC 4.3's box on real text, scored by SPEC 4.4's thresholds.

    .venv/bin/python run_layerb_grid.py --out results/layerb-grid

Layer A's grid is a parametric proof; this one is the ecological-validity layer. Same
estimator suite, same metric definitions (`metrics._target_metrics` is imported, not
reimplemented, so a Layer A number and a Layer B number mean the same thing), but the trait
scores, the texts, the class means and the detector are all real, and only `w` is constructed
(`inject/build.py`: w = rho_T theta + u; no corpus carries an outcome).

Three things differ from Layer A by nature, not by choice, and each is recorded per cell:

1. The detector sets SPECIFICITY only. `detector_flags` thresholds at a quantile of the human
   detector scores, so `sp` is set and `se` is MEASURED. On same-genre text the realized
   sensitivity is 0.29 at sp = 0.99 and 0.72 at sp = 0.85. Layer A's (se, sp) pairs do not
   exist here; SPEC 4.3's "calibrated" and "degraded" are read as those two specificity
   targets, and the realized se is a result.
2. The single indicator x is chunk 1 of the essay, and the k = 4 items are its four chunks,
   read from lane 3's OUT-OF-FOLD columns (`score_version="oof"`, pools.SCORE_VERSIONS). On
   OOF scores the four chunks are near-parallel in trait signal (EXT: 0.135, 0.131, 0.134,
   0.094) -- the 0.350/0.218/0.175/0.124 decay visible on the in-sample columns was leakage
   concentrated in chunk 1, which is the whole reason this grid was relaunched (orchestrator
   decision D1, lane3-testbed pass-3 review finding B3).
   What survives the fix is the weak-H2 failure itself, larger than it looked: the
   between-chunk correlation is 0.210 against a true rel_H = r_H^2 = 0.0183, an
   overstatement of 11.5x, inside WEAK-H2-DIAGNOSIS.md's 5.4x-41.7x range. Every rho_T-scale
   number divides by sqrt(rel_hat) and inherits it. Measured, reported, never used as a truth
   value and never rescued.
3. The base is the injection half of the FROZEN calibration split (SPEC-FIXES-ROUND3.md fix
   1), restricted to texts lane 3 could chunk into 4: 1208 of the 1234 human texts, 160
   machine texts. n = 2400 is therefore a 2x bootstrap oversample of 1208 unique respondents,
   not 2400 distinct people. SPEC 6 caps Layer B's n at 2400 for exactly this reason.

Frozen record. Writes only to its own --out directory. results/grid/ and
results/grid-nonignorable/ are never opened.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
from dataclasses import asdict, dataclass, field
from functools import lru_cache, partial
from multiprocessing import Pool as ProcPool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from estimators import ESTIMATORS, _distribution_match_pi
from inject.build import build_injected_sample
from inject.pools import calibration_split, lane3_pool, load_lane3, reference_detector, split_id
from metrics import _target_metrics

MASTER_SEED = 20260909
SCORE_VERSION = "oof"          # lane 3's out-of-fold chunk columns; see pools.SCORE_VERSIONS
REPS = 100                    # SPEC 4.3: Layer B 100 reps per cell
RHO_T = 0.5
K_CHUNKS = 4
HUMAN_POOL = "pk_human"
FRONTIER, OPEN_MODEL = "personallm_gpt-4-0613", "personallm_llama-2"
PI_LEVELS = (0.01, 0.02, 0.05, 0.10, 0.20, 0.30)
N_LEVELS = (500, 1000, 2400)          # SPEC 6: Layer B is capped by data, n = 5000 is Layer A only
P_LEVELS = (0.0, 0.5, 1.0)            # assignment coupling; c = p * c_pool, SPEC 4.3's {0, partial, high}
DETECTORS = ("none", "calibrated", "degraded", "oracle")
SP_TARGET = {"none": 1.0, "calibrated": 0.99, "degraded": 0.85, "oracle": 1.0}
CORES_LEFT_FREE = 2


@dataclass(frozen=True)
class LBCell:
    pi: float
    n: int
    p: float
    detector: str
    pool: str = FRONTIER
    trait: str = "EXT"
    arm: str = "box"

    @property
    def cell_id(self) -> str:
        payload = "|".join(f"{k}={v}" for k, v in sorted(asdict(self).items()) if k != "arm")
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


def box() -> list[LBCell]:
    """SPEC 4.3's cross on real text, plus the generator and trait arms.

    Core box, 216 cells: pi (6) x detector (4) x n (3) x p (3) at the reference cell
    (frontier generator, EXT). This is the full (pi, n, detector) box the brief asks for,
    crossed with coupling because SPEC 4.4's headline threshold is conditioned on c: the
    success claim lives at `pi <= 0.20 and c <= partial`, so p = 0 and p = 0.5 must both be
    present at every (pi, n, detector), and p = 1 is the boundary map's high-c edge.

    Generator arm, 72 cells: SPEC 4.3's second generator (open model) at n = 1000, full
    pi x detector x p. Reduced on n only, because n moves sampling variance and not the
    population moments (verified on the Layer A grid and in LAYERB-SWEEP.md's (pi, n) box).

    Trait arm, 48 cells: the other four traits at n = 1000, p = 0.5, the two real detector
    points. Trait is not a SPEC 4.3 axis -- it is a lane-3 artifact -- but the whole box sits
    at EXT, so this is the check that the headline does not hinge on one trait.

    336 cells x 100 reps x ~1.3 s/rep = ~12 core-hours, one overnight batch on 10 workers.
    """
    cells = [LBCell(pi=pi, n=n, p=p, detector=d)
             for pi in PI_LEVELS for d in DETECTORS for n in N_LEVELS for p in P_LEVELS]
    cells += [LBCell(pi=pi, n=1000, p=p, detector=d, pool=OPEN_MODEL, arm="generator")
              for pi in PI_LEVELS for d in DETECTORS for p in P_LEVELS]
    cells += [LBCell(pi=pi, n=1000, p=0.5, detector=d, trait=t, arm="trait")
              for t in ("NEU", "AGR", "CON", "OPE") for d in ("calibrated", "degraded")
              for pi in PI_LEVELS]
    seen: dict[str, LBCell] = {}
    for c in cells:
        seen.setdefault(c.cell_id, c)
    return list(seen.values())


def _ref_chunk1(pool_all, ref, mu: float, sd: float) -> np.ndarray:
    """Chunk-1 scores of a held-out Reference, looked up by text id and standardized.

    SPEC 3.2's distribution matching compares the OBSERVED score distribution to a mixture of
    two reference distributions, so the references have to be the same statistic as the
    observed score. At k = 4 the observed score is chunk 1 (`Sample.x = X[:, 0]`), so a
    whole-text reference would mismatch at every pi including 0 and the estimator would read
    the mismatch as prevalence. Reference texts lane 3 could not chunk are dropped.
    """
    by_id = {t.text_id: t for t in pool_all.texts}
    vals = [by_id[tid].chunk_scores[0] for tid in ref.text_ids
            if tid in by_id and len(by_id[tid].chunk_scores) == K_CHUNKS]
    return (np.asarray(vals, dtype=float) - mu) / sd


def _k4(pool, name: str):
    """Keep only texts lane 3 chunked into K_CHUNKS. `_chunks_or_none` refuses a draw that
    touches an unchunkable text, so the restriction has to happen before the bootstrap."""
    idx = [i for i, t in enumerate(pool.texts) if len(t.chunk_scores) == K_CHUNKS]
    return pool.subset(idx, name=name)


@lru_cache(maxsize=None)
def _raw():
    return load_lane3()


@lru_cache(maxsize=None)
def setup(pool_name: str, trait: str) -> dict:
    """Everything fixed by (pool, trait): the frozen split, the truth constants, the detector.

    Reused across every (pi, n, p, detector) cell of that pool and trait -- which is the point
    of fix 1. The split is NOT re-drawn per cell, and `split_id` is recorded so the identity is
    recoverable from the output.
    """
    raw = _raw()
    H_all = lane3_pool(HUMAN_POOL, trait, raw, score_version=SCORE_VERSION)
    M_all = lane3_pool(pool_name, trait, raw, score_version=SCORE_VERSION)
    H_base, H_ref = calibration_split(H_all, frac=0.5)      # frozen, keyed on pool identity
    M_inj, M_ref = calibration_split(M_all, frac=0.5)
    H_b = _k4(H_base, f"{HUMAN_POOL}:k{K_CHUNKS}")
    M_i = _k4(M_inj, f"{pool_name}:k{K_CHUNKS}")

    mu, sd = float(H_b.scores.mean()), float(H_b.scores.std(ddof=0))
    Hs = H_b.standardized(mu, sd)
    C = np.array([t.chunk_scores for t in Hs.texts], dtype=float)
    q1 = float(Hs.labels.mean())
    theta = (Hs.labels - q1) / np.sqrt(q1 * (1 - q1))
    # Truth. x is chunk 1, so rho_H := Cor(x, w | H) = rho_T * Cor(chunk_1, theta) exactly
    # (w = rho_T theta + u with u independent and Var(w) = 1).
    #
    # The loading truth is r_H itself, NOT the between-chunk correlation. LAYERB-SWEEP2.md
    # ("What rel_H's truth value is at k = 4") rules it: Layer A defines rel_H through
    # rho_H = sqrt(rel_H) rho_T, theta is the standardized label, and rho_H_true = rho_T r_H,
    # so sqrt(rel_H_true) = r_H and rel_H_true = r_H^2. The between-chunk correlation is what
    # rel_hat ESTIMATES, and it overstates the truth (EXT: 0.220 against 0.122) because chunks
    # of one essay share style, length and topic variance that is not trait variance. That
    # ratio is recorded per cell as the weak-H2 failure it is, not used as a truth.
    r_H1 = float(np.corrcoef(C[:, 0], theta)[0, 1])
    R = np.corrcoef(C, rowvar=False)
    iu = np.triu_indices(K_CHUNKS, 1)
    rel_between_chunk = float(R[iu].mean())
    rel_H = r_H1 ** 2

    det_Href = reference_detector(H_all, H_ref)
    det_Mref = reference_detector(M_all, M_ref)
    op = {}
    for name, sp_target in SP_TARGET.items():
        if name == "oracle":
            op[name] = {"sp_target": None, "thr": None, "sp_cal": 1.0, "se_cal": 1.0}
        elif name == "none":
            op[name] = {"sp_target": 1.0, "thr": None, "sp_cal": 1.0, "se_cal": 0.0}
        else:
            thr = float(np.quantile(det_Href, sp_target))
            op[name] = {"sp_target": sp_target, "thr": thr,
                        "sp_cal": float(np.mean(det_Href <= thr)),
                        "se_cal": float(np.mean(det_Mref > thr))}
    return {
        "H_b": H_b, "M_i": M_i,
        "split_id": split_id(M_ref, H_ref),
        "n_human_base": len(H_b), "n_machine_inj": len(M_i),
        "n_human_dropped_unchunked": len(H_base) - len(H_b),
        "n_machine_dropped_unchunked": len(M_inj) - len(M_i),
        "q1": q1, "r_H_chunk1": r_H1, "r_H_by_chunk": [float(np.corrcoef(C[:, j], theta)[0, 1])
                                                       for j in range(K_CHUNKS)],
        "rel_H_true": rel_H, "rel_between_chunk": rel_between_chunk,
        "rel_overstatement": rel_between_chunk / rel_H if rel_H > 0 else float("nan"),
        "rho_H_true": RHO_T * r_H1, "rho_T_true": RHO_T, "loading_true": abs(r_H1),
        "Mref_c1": _ref_chunk1(M_all, M_ref, mu, sd), "Href_c1": _ref_chunk1(H_all, H_ref, mu, sd),
        "n_ref_machine": int(len(_ref_chunk1(M_all, M_ref, mu, sd))),
        "n_ref_human": int(len(_ref_chunk1(H_all, H_ref, mu, sd))),
        "operating_points": op,
        "score_version": SCORE_VERSION,
        "chunk_scoring_human": H_all.metrics.get("chunk_scoring"),
        "chunk_scoring_machine": M_all.metrics.get("chunk_scoring"),
        "whole_text_scoring_human": H_all.metrics.get("whole_text_scoring"),
        "whole_text_scoring_machine": M_all.metrics.get("whole_text_scoring"),
    }


def rep_rng(cell: LBCell, rep: int) -> np.random.Generator:
    key = int(hashlib.sha256(f"{cell.cell_id}:{rep}".encode()).hexdigest()[:16], 16)
    return np.random.default_rng(np.random.SeedSequence([MASTER_SEED, key]))


def run_cell(cell: LBCell, reps: int = REPS) -> dict:
    S = setup(cell.pool, cell.trait)
    opp = S["operating_points"][cell.detector]
    se_bel, sp_bel = opp["se_cal"], opp["sp_cal"]     # what the researcher BELIEVES, from the
                                                      # calibration half -- not an oracle value
    fits_per_rep: list[dict] = []
    realized = {"sp": [], "se": [], "flag_rate": []}
    for rep in range(reps):
        rng = rep_rng(cell, rep)
        inj = build_injected_sample(S["H_b"], S["M_i"], cell.n, cell.pi, cell.p, rng,
                                    rho_T=RHO_T, k_chunks=K_CHUNKS,
                                    sp=SP_TARGET[cell.detector], replace=True)
        s = inj.sample
        if cell.detector == "oracle":
            s.flag = s.A == 1                          # perfect detection, by construction
        elif cell.detector == "none":
            s.flag = np.zeros(cell.n, dtype=bool)
        H, M = s.A == 0, s.A == 1
        realized["sp"].append(float(np.mean(~s.flag[H])) if H.any() else float("nan"))
        realized["se"].append(float(np.mean(s.flag[M])) if M.any() else float("nan"))
        realized["flag_rate"].append(float(s.flag.mean()))

        opts = {
            "naive": {}, "delete": {},
            "simex": {"se": se_bel, "sp": sp_bel, "rng": np.random.default_rng(rng.integers(0, 2**31 - 1))},
            "labelfree": {"se": se_bel, "sp": sp_bel,
                          "machine_ref": S["Mref_c1"], "human_ref": S["Href_c1"],
                          "c_known": 0.0,               # the researcher does not know c
                          "rng": np.random.default_rng(rng.integers(0, 2**31 - 1))},
            "em": {"rng": np.random.default_rng(rng.integers(0, 2**31 - 1))},
        }
        fits_per_rep.append({name: fn(s, **opts.get(name, {})) for name, fn in ESTIMATORS.items()})

    truth = {"rho_H": S["rho_H_true"], "rho_T": S["rho_T_true"],
             "pi": cell.pi, "loading": S["loading_true"]}
    estimators_out = {}
    for name in sorted(ESTIMATORS):
        rf = [r[name] for r in fits_per_rep]
        conv = np.array([bool(f is not None and f.converged) for f in rf])
        out = {}
        for target, attr, ci_attr in (("rho_H", "rho_H_hat", "ci_H"), ("rho_T", "rho_T_hat", "ci_T")):
            est = np.array([float(getattr(f, attr)) for f in rf])
            out[target] = _target_metrics(est, conv, [getattr(f, ci_attr) for f in rf], truth[target])
        pis = [f.pi_hat for f in rf if f.converged and f.pi_hat is not None]
        out["pi_abs_err"] = (
            {"value": float(np.mean(np.abs(np.array(pis) - cell.pi))),
             "mcse": float(np.std(np.abs(np.array(pis) - cell.pi), ddof=1) / np.sqrt(len(pis))),
             "bias": float(np.mean(np.array(pis) - cell.pi)), "n": len(pis)} if len(pis) > 1 else None)
        loads = [f.loading_hat for f in rf if f.converged and f.loading_hat is not None
                 and np.isfinite(f.loading_hat)]
        out["loading_bias"] = float(np.mean(loads) - truth["loading"]) if loads else None
        out["n_converged"] = int(conv.sum())
        estimators_out[name] = out

    return {
        "cell_id": cell.cell_id, "cell": asdict(cell), "reps": reps, "master_seed": MASTER_SEED,
        "truth": truth,
        "setup": {k: S[k] for k in ("split_id", "n_human_base", "n_machine_inj",
                                    "n_human_dropped_unchunked", "n_machine_dropped_unchunked",
                                    "q1", "r_H_chunk1", "r_H_by_chunk", "rel_H_true",
                                    "rel_between_chunk", "rel_overstatement",
                                    "n_ref_machine", "n_ref_human")},
        "detector": {"level": cell.detector, **opp,
                     "realized_sp": float(np.nanmean(realized["sp"])),
                     "realized_se": float(np.nanmean(realized["se"])),
                     "flag_rate": float(np.nanmean(realized["flag_rate"]))},
        # self-describing per brief item 3: which split, which n_bins era produced these numbers
        "era": {"n_bins_default": _distribution_match_pi.__defaults__[0],
                "frozen_calibration_split": True, "k_chunks": K_CHUNKS, "replace": True,
                "score_version": S["score_version"],
                "chunk_scoring_human": S["chunk_scoring_human"],
                "chunk_scoring_machine": S["chunk_scoring_machine"],
                "whole_text_scoring_human": S["whole_text_scoring_human"],
                "whole_text_scoring_machine": S["whole_text_scoring_machine"]},
        "estimators": estimators_out,
    }


def _run_one(cell: LBCell, reps: int, cells_dir: str) -> dict:
    t0 = time.time()
    try:
        result = run_cell(cell, reps)
        result["wall_seconds"] = time.time() - t0
        result["host"] = platform.node()
        Path(cells_dir, f"{cell.cell_id}.json").write_text(json.dumps(result, indent=1))
        return {"cell_id": cell.cell_id, "result": result, "seconds": time.time() - t0, "error": None}
    except Exception as e:
        return {"cell_id": cell.cell_id, "result": None, "seconds": time.time() - t0,
                "error": f"{type(e).__name__}: {e}"}


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the Layer B full grid.")
    ap.add_argument("--out", default="results/layerb-grid")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--reps", type=int, default=REPS)
    ap.add_argument("--cells-only", action="store_true", help="print the box and exit")
    ap.add_argument("--max-pi", type=float, default=None,
                    help="keep only cells with pi <= this (D7: the pi <= 0.20 slice at 500 reps)")
    args = ap.parse_args()

    here = Path(__file__).resolve().parent
    out_dir = (here / args.out).resolve()
    assert out_dir.name not in ("grid", "grid-nonignorable"), "those are frozen records"
    cells = sorted(box(), key=lambda c: c.cell_id)
    if args.max_pi is not None:
        cells = [c for c in cells if c.pi <= args.max_pi + 1e-12]
    by_arm: dict[str, int] = {}
    for c in cells:
        by_arm[c.arm] = by_arm.get(c.arm, 0) + 1
    print(f"Layer B grid: {len(cells)} cells {by_arm}, reps={args.reps}, "
          f"master_seed={MASTER_SEED}, k={K_CHUNKS}"
          + (f", max_pi={args.max_pi}" if args.max_pi is not None else ""), flush=True)
    if args.cells_only:
        for c in cells:
            print(f"  {c.arm:10s} {c.pool:24s} {c.trait} pi={c.pi:<5} n={c.n:<5} p={c.p:<4} "
                  f"det={c.detector:11s} {c.cell_id}")
        return

    (out_dir / "cells").mkdir(parents=True, exist_ok=True)
    jsonl_path = out_dir / "grid.jsonl"
    done: set[str] = set()
    if jsonl_path.exists():
        for line in jsonl_path.read_text().splitlines():
            if line.strip():
                done.add(json.loads(line)["cell_id"])
    todo = [c for c in cells if c.cell_id not in done]
    n_workers = args.workers or max(1, (os.cpu_count() or 4) - CORES_LEFT_FREE)
    print(f"  {len(done)} already done, {len(todo)} to run, {n_workers} workers", flush=True)
    if not todo:
        print("nothing to do")
        return

    S = setup(FRONTIER, "EXT")
    print(f"  score_version={S['score_version']}  frozen split_id={S['split_id']} "
          f"human base {S['n_human_base']} (dropped {S['n_human_dropped_unchunked']} unchunkable), "
          f"machine inj {S['n_machine_inj']}", flush=True)
    print(f"  truth: rho_H={S['rho_H_true']:.4f} loading={S['loading_true']:.4f} "
          f"rel_H_true={S['rel_H_true']:.4f} between-chunk={S['rel_between_chunk']:.4f} "
          f"(overstatement {S['rel_overstatement']:.1f}x)", flush=True)
    for name, op in S["operating_points"].items():
        print(f"  detector {name:11s} sp_target={op['sp_target']} -> sp_cal={op['sp_cal']:.4f} "
              f"se_cal={op['se_cal']:.4f}", flush=True)

    t0, n_done, failures = time.time(), len(done), []
    with open(jsonl_path, "a") as out_f:
        with ProcPool(n_workers) as pool:
            worker = partial(_run_one, reps=args.reps, cells_dir=str(out_dir / "cells"))
            for payload in pool.imap_unordered(worker, todo, chunksize=1):
                n_done += 1
                if payload.get("error"):
                    failures.append((payload["cell_id"], payload["error"]))
                    print(f"lbgrid: {n_done}/{len(cells)} FAILED {payload['cell_id']}: "
                          f"{payload['error'][:200]}", flush=True)
                    continue
                out_f.write(json.dumps(payload["result"]) + "\n")
                out_f.flush()
                c = payload["result"]["cell"]
                print(f"lbgrid: {n_done}/{len(cells)} {c['arm']:10s} {c['trait']} pi={c['pi']:<5} "
                      f"n={c['n']:<5} p={c['p']:<4} det={c['detector']:11s} "
                      f"({payload['seconds']:.1f}s, {time.time() - t0:.0f}s elapsed)", flush=True)

    print(f"lbgrid: COMPLETE {n_done - len(failures)}/{len(cells)} in {time.time() - t0:.0f}s"
          + (f", {len(failures)} FAILED (listed above)" if failures else ""))
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
