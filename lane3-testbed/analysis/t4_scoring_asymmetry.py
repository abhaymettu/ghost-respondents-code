"""Pass-3 review T4/M2: quantify how much of the reported machine/human kappa (variance
ratio) and delta (mean gap) is attributable to the scoring-model asymmetry -- human whole-text
scores come from a 1-fold-held-out ridge model, machine whole-text scores from a 100%-refit
ridge model -- rather than to any real difference between machine and human text.

Method: score each labeled machine pool with BOTH scoring protocols:
  (existing) full-refit model (pk_full_models, unchanged, from pool_measurement.py)
  (matched)  5-fold-ensemble mean decision_function (same protocol already used for the
             non-PK pools' chunk_*_oof columns in chunk_scoring_oof.py, and structurally the
             closest machine-side analogue of "a model that did not see 100% of PK")
Compare kappa/delta computed each way. This does not remove the asymmetry (a 5-model ensemble
mean over folds is still not identical to a single-fold OOF score), but it directly measures
how much kappa/delta move when the model-fitting protocol changes, holding the text fixed.

Local CPU, niced by the caller. No LLM generation, no API keys.
Run: nice -n 15 .venv/bin/python analysis/t4_scoring_asymmetry.py
Writes: analysis/t4_scoring_asymmetry_results.json
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np  # noqa: E402
from sklearn.linear_model import RidgeClassifier  # noqa: E402
from sklearn.model_selection import KFold  # noqa: E402

from loaders.essays_loader import load as load_pk, TRAIT_COLUMNS  # noqa: E402
from pool_measurement import embed, load_big5, load_personallm, fit_full_trait_model, SEED, KFOLDS, RIDGE_ALPHA  # noqa: E402

OUT = Path(__file__).resolve().parent / "t4_scoring_asymmetry_results.json"


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", file=sys.stderr)


def main():
    from sentence_transformers import SentenceTransformer
    st = SentenceTransformer("all-MiniLM-L6-v2")

    log("loading PK, fitting full-refit + 5 fold models")
    pk = list(load_pk())
    pk_texts = [r["text"] for r in pk]
    pk_emb = embed(st, pk_texts, "PK full")
    pk_y = {t: np.array([1 if r["traits"][t] == "y" else 0 for r in pk]) for t in TRAIT_COLUMNS}

    full_models = {}
    fold_models = {t: [] for t in TRAIT_COLUMNS}
    kf = KFold(n_splits=KFOLDS, shuffle=True, random_state=SEED)
    fold_idx = list(kf.split(pk_emb))
    mu_H, V_H = {}, {}
    for trait in TRAIT_COLUMNS:
        full_models[trait] = fit_full_trait_model(pk_emb, pk_y[trait])
        cs = np.zeros(len(pk))
        for tr, te in fold_idx:
            clf = RidgeClassifier(alpha=RIDGE_ALPHA)
            clf.fit(pk_emb[tr], pk_y[trait][tr])
            fold_models[trait].append(clf)
            cs[te] = clf.decision_function(pk_emb[te])
        mu_H[trait] = float(np.mean(cs))
        V_H[trait] = float(np.var(cs, ddof=1))

    log("loading big5 + personallm pools")
    big5_rows = load_big5()
    pools = {"big5_personality_essays": [r[0] for r in big5_rows]}
    for gen in ["gpt-4-0613", "gpt-3.5-turbo-0613", "llama-2"]:
        recs = load_personallm(gen)
        pools[f"personallm_{gen}"] = [r["text"] for r in recs]

    out = {"n_pk": len(pk), "pools": {}}
    for pool_name, texts in pools.items():
        log(f"scoring {pool_name} (n={len(texts)}) both ways")
        emb = embed(st, texts, pool_name)
        out["pools"][pool_name] = {"n": len(texts), "traits": {}}
        for trait in TRAIT_COLUMNS:
            s_full = full_models[trait].decision_function(emb)
            s_ens = np.mean([m.decision_function(emb) for m in fold_models[trait]], axis=0)
            kappa_full = float(np.var(s_full, ddof=1) / V_H[trait])
            kappa_ens = float(np.var(s_ens, ddof=1) / V_H[trait])
            delta_full = float((np.mean(s_full) - mu_H[trait]) / np.sqrt(V_H[trait]))
            delta_ens = float((np.mean(s_ens) - mu_H[trait]) / np.sqrt(V_H[trait]))
            out["pools"][pool_name]["traits"][trait] = {
                "kappa_full_refit": kappa_full, "kappa_5fold_ensemble": kappa_ens,
                "kappa_pct_change": 100 * (kappa_ens - kappa_full) / kappa_full if kappa_full else None,
                "delta_full_refit": delta_full, "delta_5fold_ensemble": delta_ens,
                "delta_abs_change": delta_ens - delta_full,
            }
        log(f"  done {pool_name}")

    OUT.write_text(json.dumps(out, indent=2))
    log(f"wrote {OUT}")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
