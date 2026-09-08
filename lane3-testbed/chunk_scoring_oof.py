"""Out-of-fold chunk-level trait scoring (fix for lane4 LAYERB-SWEEP2.md Part III FAIL 1).

chunk_scoring.py scored every pool's chunks with a RidgeClassifier refit on
100% of PK-human. For pk_human itself this is in-sample: a chunk's score
comes from a model that saw that chunk's own parent text during training.
For all other pools (never part of PK's training data under any fold) this
was never leaky, but this script re-scores them too, using the SAME 5-fold
ensemble as pk_human, so every pool's *_oof columns share one procedure.

Reuses pool_measurement.py's exact fold scheme: KFold(n_splits=5,
shuffle=True, random_state=SEED) over PK's whole-text embeddings, in PK's
load order -- identical to cross_fit_trait_scores(), verified by
reproducing pk_human.json's existing cross_fitted_scores before doing
anything else.

For pk_human: chunk i (belonging to PK text i, which sits in test fold f)
is scored with fold f's model -- true OOF, no leakage.
For non-PK pools: chunks are scored with the mean decision_function across
all 5 fold models (none of which ever saw that pool's texts, so any single
fold model would already be valid OOF; the ensemble average is used purely
so the same "5-fold scheme" language applies uniformly across pools).

Adds chunk_{1..K}_oof arrays to the existing data/scores/*.json files.
Does not overwrite the existing (in-sample) chunk_{1..K} columns.

No LLM generation, no API keys, local compute only.
Run: source .venv/bin/activate && nice -n 15 python3 chunk_scoring_oof.py
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.stats import pearsonr, pointbiserialr
from sklearn.linear_model import RidgeClassifier
from sklearn.model_selection import KFold

sys.path.insert(0, str(Path(__file__).resolve().parent))
from loaders.essays_loader import load as load_pk, TRAIT_COLUMNS  # noqa: E402
from audit2_genre_confound import (  # noqa: E402
    load_argugpt, load_ghostbuster_machine, load_student_llm_machine, sample,
)
from pool_measurement import (  # noqa: E402
    SEED, N_SAMPLE, RIDGE_ALPHA, KFOLDS,
    load_big5, load_personallm, embed,
)
from chunk_scoring import (  # noqa: E402
    K, SCORES_DIR, chunk_at_sentence_boundaries,
)

RESULTS_PATH = Path(__file__).resolve().parent / "chunk_scoring_oof_results.json"


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", file=sys.stderr)


def score_chunks_oof_pk(fold_models_by_trait, fold_of_text, texts):
    """Score PK-human's own chunks OOF: chunk of text i scored by the
    fold model that excluded text i from training."""
    chunk_lists = [chunk_at_sentence_boundaries(t) for t in texts]
    n_skipped = sum(1 for c in chunk_lists if c is None)
    out = {t: [None] * len(texts) for t in TRAIT_COLUMNS}
    # group chunks by fold so each fold's model embeds/scores its own texts' chunks in one batch
    for f in range(KFOLDS):
        idxs = [i for i in range(len(texts)) if chunk_lists[i] is not None and fold_of_text[i] == f]
        if not idxs:
            continue
        flat_chunks = []
        owner = []
        for ti in idxs:
            for ci, c in enumerate(chunk_lists[ti]):
                flat_chunks.append(c)
                owner.append((ti, ci))
        emb = embed(ST, flat_chunks, f"PK fold {f} chunks (n_texts={len(idxs)})")
        for trait in TRAIT_COLUMNS:
            s = fold_models_by_trait[trait][f].decision_function(emb)
            for (ti, ci), val in zip(owner, s):
                if out[trait][ti] is None:
                    out[trait][ti] = [None] * K
                out[trait][ti][ci] = float(val)
    return out, n_skipped


def score_chunks_oof_ensemble(fold_models_by_trait, texts, desc):
    """Score a non-PK pool's chunks with the mean decision_function across
    all 5 fold models (each fold model never saw this pool's texts)."""
    chunk_lists = [chunk_at_sentence_boundaries(t) for t in texts]
    n_skipped = sum(1 for c in chunk_lists if c is None)
    flat_chunks = []
    owner = []
    for ti, cl in enumerate(chunk_lists):
        if cl is None:
            continue
        for ci, c in enumerate(cl):
            flat_chunks.append(c)
            owner.append((ti, ci))
    out = {t: [None] * len(texts) for t in TRAIT_COLUMNS}
    if not flat_chunks:
        return out, n_skipped
    emb = embed(ST, flat_chunks, f"{desc} chunks (k={K}, n_texts_chunked={len(texts) - n_skipped})")
    for trait in TRAIT_COLUMNS:
        fold_scores = np.stack([m.decision_function(emb) for m in fold_models_by_trait[trait]], axis=0)
        s = fold_scores.mean(axis=0)
        per_text = {}
        for (ti, ci), val in zip(owner, s):
            per_text.setdefault(ti, {})[ci] = float(val)
        for ti in range(len(texts)):
            if ti in per_text:
                out[trait][ti] = [per_text[ti][ci] for ci in range(K)]
    return out, n_skipped


def update_score_file_oof(pool_name, ids, chunk_scores_by_trait, n_skipped, texts_len):
    path = SCORES_DIR / f"{pool_name}.json"
    data = json.loads(path.read_text())
    assert data["ids"] == ids, f"{pool_name}: id order mismatch"
    for j in range(K):
        col = {}
        for i in range(texts_len):
            per_trait = {}
            for trait in TRAIT_COLUMNS:
                cs = chunk_scores_by_trait[trait][i]
                if cs is not None:
                    per_trait[trait] = cs[j]
            col[ids[i]] = per_trait if per_trait else None
        data[f"chunk_{j + 1}_oof"] = [col[ids[i]] for i in range(texts_len)]
    data["chunk_meta_oof"] = {
        "k": K,
        "fold_scheme": f"same {KFOLDS}-fold KFold(shuffle=True, random_state={SEED}) as whole-text cross_fit_trait_scores in pool_measurement.py",
        "scoring_rule": ("pk_human: chunk scored by the fold model that excluded its parent text from training (true OOF)"
                          if pool_name == "pk_human" else
                          "non-PK pool: chunk scored by mean decision_function across all 5 fold models (none saw this pool's texts; ensemble used only for procedural consistency, not to fix leakage -- this pool was never leaky)"),
        "n_texts_too_short_to_chunk": n_skipped,
        "n_texts_total": texts_len,
    }
    path.write_text(json.dumps(data))
    log(f"  updated {path} (+{K} chunk_*_oof columns, {n_skipped}/{texts_len} skipped)")


def between_chunk_rbar(chunk_arrays):
    """chunk_arrays: list of K lists (each length n, entries float or None aligned across chunks).
    Returns mean pairwise pearson r across chunk pairs, using rows where all K present."""
    n = len(chunk_arrays[0])
    complete_idx = [i for i in range(n) if all(chunk_arrays[j][i] is not None for j in range(K))]
    if len(complete_idx) < 3:
        return None, len(complete_idx)
    arr = np.array([[chunk_arrays[j][i] for j in range(K)] for i in complete_idx])
    pair_rs = []
    for a in range(K):
        for b in range(a + 1, K):
            r, _ = pearsonr(arr[:, a], arr[:, b])
            pair_rs.append(r)
    return float(np.mean(pair_rs)), len(complete_idx)


def mean_chunk_vs_whole(chunk_arrays, whole_scores, ids_order):
    n = len(chunk_arrays[0])
    complete_idx = [i for i in range(n) if all(chunk_arrays[j][i] is not None for j in range(K))]
    if len(complete_idx) < 3:
        return None, None, len(complete_idx)
    mean_chunk = np.array([np.mean([chunk_arrays[j][i] for j in range(K)]) for i in complete_idx])
    whole = np.array([whole_scores[i] for i in complete_idx])
    r, p = pearsonr(mean_chunk, whole)
    chunk1 = np.array([chunk_arrays[0][i] for i in complete_idx])
    r1, p1 = pearsonr(chunk1, whole)
    return float(r), float(r1), len(complete_idx)


def main():
    global ST
    from sentence_transformers import SentenceTransformer
    ST = SentenceTransformer("all-MiniLM-L6-v2")

    log("loading PK")
    pk = list(load_pk())
    pk_texts = [r["text"] for r in pk]
    pk_ids = [r["author_id"] for r in pk]
    pk_emb = embed(ST, pk_texts, "PK full")
    pk_y = {t: np.array([1 if r["traits"][t] == "y" else 0 for r in pk]) for t in TRAIT_COLUMNS}

    # ---------- reproduce the exact fold scheme + fold models ----------
    kf = KFold(n_splits=KFOLDS, shuffle=True, random_state=SEED)
    splits = list(kf.split(pk_emb))
    fold_of_text = np.zeros(len(pk_texts), dtype=int)
    fold_models_by_trait = {t: [None] * KFOLDS for t in TRAIT_COLUMNS}
    reproduced_scores = {t: np.zeros(len(pk_texts)) for t in TRAIT_COLUMNS}
    for f, (train_idx, test_idx) in enumerate(splits):
        fold_of_text[test_idx] = f
        for trait in TRAIT_COLUMNS:
            clf = RidgeClassifier(alpha=RIDGE_ALPHA)
            clf.fit(pk_emb[train_idx], pk_y[trait][train_idx])
            fold_models_by_trait[trait][f] = clf
            reproduced_scores[trait][test_idx] = clf.decision_function(pk_emb[test_idx])

    # verify reproduction against pk_human.json's existing cross_fitted_scores
    existing = json.loads((SCORES_DIR / "pk_human.json").read_text())
    assert existing["ids"] == pk_ids, "PK id order mismatch vs existing score file"
    verify = {}
    for trait in TRAIT_COLUMNS:
        old = np.array(existing["cross_fitted_scores"][trait])
        new = reproduced_scores[trait]
        max_abs_diff = float(np.max(np.abs(old - new)))
        verify[trait] = max_abs_diff
        log(f"fold-reproduction check {trait}: max|old-new|={max_abs_diff:.2e}")
    if max(verify.values()) > 1e-6:
        log("WARNING: fold reproduction does not exactly match existing cross_fitted_scores -- "
            "proceeding anyway but flagging in results")

    # ---------- PK-human chunk scores, true OOF ----------
    log("scoring PK-human chunks OOF")
    pk_chunk_oof, pk_skipped = score_chunks_oof_pk(fold_models_by_trait, fold_of_text, pk_texts)
    update_score_file_oof("pk_human", pk_ids, pk_chunk_oof, pk_skipped, len(pk_texts))

    results = {"fold_reproduction_max_abs_diff": verify, "pools": {}}

    # PK-human rbar + chunk-vs-whole, OOF and in-sample, per trait
    for trait in TRAIT_COLUMNS:
        oof_chunks = [pk_chunk_oof[trait]]  # placeholder, replaced below
    # reload updated file for both in-sample and oof columns
    pk_data = json.loads((SCORES_DIR / "pk_human.json").read_text())
    pool_res = {"n": len(pk_ids), "traits": {}}
    for trait in TRAIT_COLUMNS:
        whole = pk_data["cross_fitted_scores"][trait]
        chunks_is = [pk_data[f"chunk_{j+1}"] for j in range(K)]
        chunks_is_trait = [[(c[trait] if c is not None else None) for c in col] for col in chunks_is]
        chunks_oof = [pk_data[f"chunk_{j+1}_oof"] for j in range(K)]
        chunks_oof_trait = [[(c[trait] if c is not None else None) for c in col] for col in chunks_oof]

        rbar_is, n_is = between_chunk_rbar(chunks_is_trait)
        rbar_oof, n_oof = between_chunk_rbar(chunks_oof_trait)
        mcw_is, c1w_is, _ = mean_chunk_vs_whole(chunks_is_trait, whole, pk_ids)
        mcw_oof, c1w_oof, _ = mean_chunk_vs_whole(chunks_oof_trait, whole, pk_ids)

        lab = pk_y[trait]
        c1_is = np.array([chunks_is_trait[0][i] for i in range(len(lab)) if chunks_is_trait[0][i] is not None])
        lab_c1_is = np.array([lab[i] for i in range(len(lab)) if chunks_is_trait[0][i] is not None])
        c1_oof = np.array([chunks_oof_trait[0][i] for i in range(len(lab)) if chunks_oof_trait[0][i] is not None])
        lab_c1_oof = np.array([lab[i] for i in range(len(lab)) if chunks_oof_trait[0][i] is not None])
        r_whole = existing["cross_fitted_scores"][trait]
        r_H_whole, _ = pointbiserialr(lab, r_whole)
        r_chunk1_is, _ = pointbiserialr(lab_c1_is, c1_is)
        r_chunk1_oof, _ = pointbiserialr(lab_c1_oof, c1_oof)

        pool_res["traits"][trait] = {
            "rbar_between_chunk_in_sample": rbar_is,
            "rbar_between_chunk_oof": rbar_oof,
            "n_complete_in_sample": n_is,
            "n_complete_oof": n_oof,
            "mean_chunk_vs_whole_in_sample": mcw_is,
            "mean_chunk_vs_whole_oof": mcw_oof,
            "chunk1_vs_whole_in_sample": c1w_is,
            "chunk1_vs_whole_oof": c1w_oof,
            "r_H_whole_cross_fitted": float(r_H_whole),
            "r_H_chunk1_in_sample": float(r_chunk1_is),
            "r_H_chunk1_oof": float(r_chunk1_oof),
            "validity_ratio_chunk1_over_whole_in_sample": float(r_chunk1_is / r_H_whole) if r_H_whole else None,
            "validity_ratio_chunk1_over_whole_oof": float(r_chunk1_oof / r_H_whole) if r_H_whole else None,
        }
        log(f"PK {trait}: rbar IS={rbar_is:.4f} OOF={rbar_oof:.4f} | mean-chunk-vs-whole IS={mcw_is:.4f} OOF={mcw_oof:.4f} | "
            f"r_H whole={r_H_whole:.4f} chunk1 IS={r_chunk1_is:.4f} OOF={r_chunk1_oof:.4f}")
    results["pools"]["pk_human"] = pool_res

    # ---------- non-PK pools: re-derive chunk scores via 5-fold ensemble ----------
    log("re-loading labeled pools")
    big5_rows = load_big5()
    big5_texts = [r[0] for r in big5_rows]
    big5_ids = [f"big5_{i}" for i in range(len(big5_texts))]

    non_pk_pools = {"big5_personality_essays": (big5_ids, big5_texts)}
    for gen in ["gpt-4-0613", "gpt-3.5-turbo-0613", "llama-2"]:
        recs = load_personallm(gen)
        non_pk_pools[f"personallm_{gen}"] = ([r["id"] for r in recs], [r["text"] for r in recs])

    unlabeled_loaders = {
        "argugpt": load_argugpt,
        "ghostbuster_gpt_writing": load_ghostbuster_machine,
        "student_llm_essays": load_student_llm_machine,
    }
    for pool_name, loader in unlabeled_loaders.items():
        texts_all = loader()
        n = min(N_SAMPLE, len(texts_all))
        pool_sample = sample(texts_all, n, SEED + hash(pool_name) % 1000)
        non_pk_pools[pool_name] = ([f"{pool_name}_{i}" for i in range(n)], pool_sample)

    for pool_name, (ids, texts) in non_pk_pools.items():
        log(f"scoring {pool_name} chunks via 5-fold ensemble OOF (n={len(texts)})")
        cs, skipped = score_chunks_oof_ensemble(fold_models_by_trait, texts, pool_name)
        update_score_file_oof(pool_name, ids, cs, skipped, len(texts))

        data = json.loads((SCORES_DIR / f"{pool_name}.json").read_text())
        pool_res = {"n": len(texts), "traits": {}}
        for trait in TRAIT_COLUMNS:
            whole = data["trait_scores"][trait]
            chunks_is = [data[f"chunk_{j+1}"] for j in range(K)]
            chunks_is_trait = [[(c[trait] if c is not None else None) for c in col] for col in chunks_is]
            chunks_oof = [data[f"chunk_{j+1}_oof"] for j in range(K)]
            chunks_oof_trait = [[(c[trait] if c is not None else None) for c in col] for col in chunks_oof]
            rbar_is, n_is = between_chunk_rbar(chunks_is_trait)
            rbar_oof, n_oof = between_chunk_rbar(chunks_oof_trait)
            mcw_is, c1w_is, _ = mean_chunk_vs_whole(chunks_is_trait, whole, ids)
            mcw_oof, c1w_oof, _ = mean_chunk_vs_whole(chunks_oof_trait, whole, ids)
            pool_res["traits"][trait] = {
                "rbar_between_chunk_in_sample": rbar_is,
                "rbar_between_chunk_oof": rbar_oof,
                "n_complete_in_sample": n_is,
                "n_complete_oof": n_oof,
                "mean_chunk_vs_whole_in_sample": mcw_is,
                "mean_chunk_vs_whole_oof": mcw_oof,
                "chunk1_vs_whole_in_sample": c1w_is,
                "chunk1_vs_whole_oof": c1w_oof,
            }
        results["pools"][pool_name] = pool_res

    RESULTS_PATH.write_text(json.dumps(results, indent=2))
    log(f"wrote {RESULTS_PATH}")
    print("DONE")


if __name__ == "__main__":
    main()
