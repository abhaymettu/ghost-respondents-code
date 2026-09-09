"""Pass-3 review T3/M1: matched-fold full-document-aggregation baseline and a lexical/
stylometric baseline, compared against the existing prefix-ridge scorer's r_H(whole).

Both baselines use the SAME complete-chunk PK subset (n=2,421) and the SAME 5-fold
KFold(shuffle=True, random_state=20260907) split lane 3 uses throughout, so numbers are
directly comparable to POOL-MEASUREMENTS.md / CHUNK-REFIT.md's r_H(whole, n=2421) column.

Baseline A (full-document aggregation): embed each text's 4 sentence-boundary chunks with
all-MiniLM-L6-v2 (each chunk well under the 256-token window), mean-pool the 4 chunk
embeddings into one document vector -- this sees the entire document, unlike the prefix-only
whole-text embedding.

Baseline B (lexical/stylometric): TF-IDF (max 2000 features, fit inside training folds only)
+ RidgeClassifier, same 5-fold cross-fit.

Local CPU, niced by the caller. No LLM generation, no API keys.
Run: nice -n 15 .venv/bin/python analysis/t3_baselines.py
Writes: analysis/t3_baselines_results.json
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np  # noqa: E402
from sklearn.feature_extraction.text import TfidfVectorizer  # noqa: E402
from sklearn.linear_model import RidgeClassifier  # noqa: E402
from sklearn.model_selection import KFold  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402

from loaders.essays_loader import load as load_pk, TRAIT_COLUMNS  # noqa: E402
from chunk_scoring import chunk_at_sentence_boundaries  # noqa: E402

SEED = 20260907
KFOLDS = 5
OUT = Path(__file__).resolve().parent / "t3_baselines_results.json"


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", file=sys.stderr)


def main():
    log("loading PK essays")
    rows = list(load_pk())
    texts = [r["text"] for r in rows]
    chunk_lists = [chunk_at_sentence_boundaries(t) for t in texts]
    idx = np.array([i for i, c in enumerate(chunk_lists) if c is not None])
    log(f"complete-chunk subset n={len(idx)}")

    log("embedding chunks for document-pooled baseline")
    from sentence_transformers import SentenceTransformer
    st = SentenceTransformer("all-MiniLM-L6-v2")
    all_chunks_flat = [c for i in idx for c in chunk_lists[i]]
    flat_emb = st.encode(all_chunks_flat, show_progress_bar=False, batch_size=64)
    pooled_emb = flat_emb.reshape(len(idx), 4, -1).mean(axis=1)

    lexical_texts = [texts[i] for i in idx]

    fold = np.empty(len(rows), dtype=int)
    kf = KFold(n_splits=KFOLDS, shuffle=True, random_state=SEED)
    for f, (_, te) in enumerate(kf.split(np.zeros(len(rows)))):
        fold[te] = f
    fold_sub = fold[idx]

    out = {"n": int(len(idx)), "baselines": {}}
    for trait in TRAIT_COLUMNS:
        y = np.array([1 if rows[i]["traits"][trait] == "y" else 0 for i in idx], dtype=float)

        pooled_scores = np.zeros(len(idx))
        for f in range(KFOLDS):
            tr, te = fold_sub != f, fold_sub == f
            clf = RidgeClassifier(alpha=1.0)
            clf.fit(pooled_emb[tr], y[tr])
            pooled_scores[te] = clf.decision_function(pooled_emb[te])
        r_pooled = float(np.corrcoef(y, pooled_scores)[0, 1])

        lex_scores = np.zeros(len(idx))
        for f in range(KFOLDS):
            tr, te = fold_sub != f, fold_sub == f
            pipe = Pipeline([
                ("tfidf", TfidfVectorizer(max_features=2000, sublinear_tf=True, min_df=2)),
                ("ridge", RidgeClassifier(alpha=1.0)),
            ])
            pipe.fit([lexical_texts[i] for i in np.where(tr)[0]], y[tr])
            lex_scores[te] = pipe.decision_function([lexical_texts[i] for i in np.where(te)[0]])
        r_lex = float(np.corrcoef(y, lex_scores)[0, 1])

        out["baselines"][trait] = {
            "r_H_document_pooled": r_pooled,
            "r_H_lexical_tfidf": r_lex,
        }
        log(f"{trait}: pooled r={r_pooled:.4f}  lexical r={r_lex:.4f}")

    OUT.write_text(json.dumps(out, indent=2))
    log(f"wrote {OUT}")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
