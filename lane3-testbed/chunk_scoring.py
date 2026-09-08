"""Chunk-level trait scoring for lane4's weak-H2 rescue (INJECT.md section 9).

Reuses pool_measurement.py's exact code path (same SentenceTransformer, same
full-refit RidgeClassifier(alpha=1.0) per trait, same loaders/sampling/seed)
so chunk scores don't drift from the already-reported per-text numbers.
Splits each text into k=4 chunks at sentence boundaries (design-pivot-memo.md
line 162: "Truncation at a sentence boundary is a legitimate length control").

Adds chunk_1..chunk_4 arrays to the EXISTING data/scores/*.json files without
touching their existing keys. Exports the 5 fitted RidgeClassifiers + the
sentence-transformer model name to data/models/.

No LLM generation, no API keys, local compute only.

Run: source .venv/bin/activate && python3 chunk_scoring.py
"""
import glob
import json
import re
import sys
import time
from pathlib import Path

import joblib
import numpy as np
from scipy.stats import pearsonr
from sklearn.linear_model import RidgeClassifier

sys.path.insert(0, str(Path(__file__).resolve().parent))
from loaders.essays_loader import load as load_pk, TRAIT_COLUMNS  # noqa: E402
from audit2_genre_confound import (  # noqa: E402
    load_argugpt, load_ghostbuster_machine, load_student_llm_machine, sample,
)
from pool_measurement import (  # noqa: E402
    SEED, N_SAMPLE, RIDGE_ALPHA, PERSONA_POLE_ORDER,
    load_big5, load_personallm, BIG5_TRAIT_COL, embed, fit_full_trait_model,
)

K = 4
SCORES_DIR = Path(__file__).resolve().parent / "data" / "scores"
MODELS_DIR = Path(__file__).resolve().parent / "data" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", file=sys.stderr)


def split_sentences(text):
    sents = [s.strip() for s in SENT_SPLIT_RE.split(text.strip()) if s.strip()]
    return sents


def chunk_at_sentence_boundaries(text, k=K):
    """Split text into k contiguous, near-equal-count groups of sentences.

    Returns None if the text has fewer than k sentences (can't form k
    non-trivial chunks without splitting mid-sentence). Any remainder
    sentences (len(sents) % k) go one-each to the first chunks, so group
    sizes differ by at most one sentence.
    """
    sents = split_sentences(text)
    n = len(sents)
    if n < k:
        return None
    base, rem = divmod(n, k)
    chunks = []
    idx = 0
    for i in range(k):
        size = base + (1 if i < rem else 0)
        chunks.append(" ".join(sents[idx:idx + size]))
        idx += size
    return chunks


def score_chunks(st, model_by_trait, texts, desc):
    """For each text, split into K chunks (or None if too short) and score every
    chunk with every trait's fitted model. Returns dict[trait] -> list[list[float] | None]
    (None entries mean that text could not be split into K chunks), and a count of skips."""
    chunk_lists = [chunk_at_sentence_boundaries(t) for t in texts]
    n_skipped = sum(1 for c in chunk_lists if c is None)
    flat_chunks = []
    owner = []  # (text_idx, chunk_idx)
    for ti, cl in enumerate(chunk_lists):
        if cl is None:
            continue
        for ci, c in enumerate(cl):
            flat_chunks.append(c)
            owner.append((ti, ci))
    if flat_chunks:
        emb = embed(st, flat_chunks, f"{desc} chunks (k={K}, n_texts_chunked={len(texts) - n_skipped})")
    else:
        emb = np.zeros((0, 384))
    out = {t: [None] * len(texts) for t in TRAIT_COLUMNS}
    for trait in TRAIT_COLUMNS:
        if len(flat_chunks) == 0:
            continue
        s = model_by_trait[trait].decision_function(emb)
        per_text = {}
        for (ti, ci), val in zip(owner, s):
            per_text.setdefault(ti, {})[ci] = float(val)
        for ti in range(len(texts)):
            if ti in per_text:
                out[trait][ti] = [per_text[ti][ci] for ci in range(K)]
    return out, n_skipped


def update_score_file(pool_name, ids, chunk_scores_by_trait, n_skipped, texts_len):
    path = SCORES_DIR / f"{pool_name}.json"
    data = json.loads(path.read_text())
    assert data["ids"] == ids, f"{pool_name}: id order mismatch between existing score file and reloaded texts"
    for j in range(K):
        col = {}
        for i in range(texts_len):
            per_trait = {}
            for trait in TRAIT_COLUMNS:
                cs = chunk_scores_by_trait[trait][i]
                if cs is not None:
                    per_trait[trait] = cs[j]
            col[ids[i]] = per_trait if per_trait else None
        data[f"chunk_{j + 1}"] = [col[ids[i]] for i in range(texts_len)]
    data["chunk_meta"] = {
        "k": K,
        "split_rule": "sentence-boundary, near-equal sentence count per chunk (design-pivot-memo.md line 162)",
        "n_texts_too_short_to_chunk": n_skipped,
        "n_texts_total": texts_len,
    }
    path.write_text(json.dumps(data))
    log(f"  updated {path} (+{K} chunk columns, {n_skipped}/{texts_len} texts skipped)")
    return n_skipped


def main():
    from sentence_transformers import SentenceTransformer
    st = SentenceTransformer("all-MiniLM-L6-v2")

    # ---------- refit PK full-refit trait models (identical code path to pool_measurement.py) ----------
    log("loading PK, refitting full-refit trait models")
    pk = list(load_pk())
    pk_texts = [r["text"] for r in pk]
    pk_ids = [r["author_id"] for r in pk]
    pk_emb = embed(st, pk_texts, "PK full")
    pk_y = {t: np.array([1 if r["traits"][t] == "y" else 0 for r in pk]) for t in TRAIT_COLUMNS}
    pk_full_models = {}
    for trait in TRAIT_COLUMNS:
        pk_full_models[trait] = fit_full_trait_model(pk_emb, pk_y[trait])
        joblib.dump(pk_full_models[trait], MODELS_DIR / f"ridge_{trait}.joblib")
    (MODELS_DIR / "sentence_transformer.txt").write_text("all-MiniLM-L6-v2\n")
    log(f"exported 5 fitted RidgeClassifiers + sentence-transformer reference to {MODELS_DIR}")

    snags = {}

    # ---------- PK-human chunk scoring (baseline spot check) ----------
    log("chunking PK-human texts")
    pk_chunk_scores, pk_skipped = score_chunks(st, pk_full_models, pk_texts, "PK")
    snags["pk_human"] = {"n_skipped": pk_skipped, "n_total": len(pk_texts)}
    update_score_file("pk_human", pk_ids, pk_chunk_scores, pk_skipped, len(pk_texts))

    # PK-human between-chunk cEXT correlation baseline (mean pairwise Pearson r across the 4 chunks)
    cext_chunks = pk_chunk_scores["cEXT"]
    complete = [cs for cs in cext_chunks if cs is not None]
    arr = np.array(complete)  # (n_complete, K)
    pair_rs = []
    for a in range(K):
        for b in range(a + 1, K):
            r, _ = pearsonr(arr[:, a], arr[:, b])
            pair_rs.append(r)
    pk_between_chunk_cext_r = float(np.mean(pair_rs))
    log(f"PK-human between-chunk cEXT mean pairwise r = {pk_between_chunk_cext_r:.4f} (n_complete={len(complete)})")

    # ---------- labeled pools ----------
    log("re-loading labeled pools (same loaders/sampling as pool_measurement.py)")
    big5_rows = load_big5()
    big5_texts = [r[0] for r in big5_rows]
    big5_ids = [f"big5_{i}" for i in range(len(big5_texts))]

    labeled = {"big5_personality_essays": (big5_ids, big5_texts)}
    for gen in ["gpt-4-0613", "gpt-3.5-turbo-0613", "llama-2"]:
        recs = load_personallm(gen)
        labeled[f"personallm_{gen}"] = ([r["id"] for r in recs], [r["text"] for r in recs])

    for pool_name, (ids, texts) in labeled.items():
        log(f"chunking labeled pool {pool_name} (n={len(texts)})")
        cs, skipped = score_chunks(st, pk_full_models, texts, pool_name)
        update_score_file(pool_name, ids, cs, skipped, len(texts))
        snags[pool_name] = {"n_skipped": skipped, "n_total": len(texts)}

    # ---------- unlabeled pools (audit2 loaders, same sample() call/seed) ----------
    unlabeled_loaders = {
        "argugpt": load_argugpt,
        "ghostbuster_gpt_writing": load_ghostbuster_machine,
        "student_llm_essays": load_student_llm_machine,
    }
    for pool_name, loader in unlabeled_loaders.items():
        log(f"re-loading + re-sampling unlabeled pool {pool_name}")
        texts_all = loader()
        n = min(N_SAMPLE, len(texts_all))
        pool_sample = sample(texts_all, n, SEED + hash(pool_name) % 1000)
        ids = [f"{pool_name}_{i}" for i in range(n)]
        log(f"chunking unlabeled pool {pool_name} (n={n})")
        cs, skipped = score_chunks(st, pk_full_models, pool_sample, pool_name)
        update_score_file(pool_name, ids, cs, skipped, n)
        snags[pool_name] = {"n_skipped": skipped, "n_total": n}

    summary = {
        "k": K,
        "split_rule": "sentence-boundary, near-equal sentence count per chunk",
        "models_reused": False,
        "models_note": "pk_full_models were NOT saved by pool_measurement.py; refit here with the identical "
                        "code path (same SentenceTransformer, same RidgeClassifier(alpha=1.0) full refit on "
                        "100% of PK, same embeddings) rather than reused from disk.",
        "pk_human_between_chunk_cEXT_mean_pairwise_r": pk_between_chunk_cext_r,
        "pk_human_between_chunk_cEXT_n_complete": len(complete),
        "snags": snags,
    }
    (Path(__file__).resolve().parent / "chunk_scoring_summary.json").write_text(json.dumps(summary, indent=2))
    log("wrote chunk_scoring_summary.json")
    print("DONE")


if __name__ == "__main__":
    main()
