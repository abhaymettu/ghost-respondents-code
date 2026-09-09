"""P1' pool measurement (design-pivot-memo.md section 8.2, step 1).

Scores every labeled/unlabeled machine-text pool against PK-human with
audit3-style trait models (K-fold cross-fitted ridge, not in-sample) and the
roberta detector. Extends audit3_trait_recoverability.py (cross-fitting),
audit2_genre_confound.py (unlabeled-pool loaders/sampling), audit_widehunt.py
(PersonaLLM loader), and detector/calibration.py (run_roberta_scores).

No LLM generation, no API keys, local compute only.

Run: source .venv/bin/activate && python3 pool_measurement.py
Writes: pool_measurement_raw.json, data/scores/*.json
"""
import glob
import hashlib
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
from sklearn.linear_model import RidgeClassifier  # noqa: E402
from sklearn.model_selection import KFold  # noqa: E402
from sklearn.metrics import roc_curve, auc  # noqa: E402
from scipy.stats import pointbiserialr  # noqa: E402

from loaders.essays_loader import load as load_pk, TRAIT_COLUMNS  # noqa: E402
from detector.calibration import run_roberta_scores  # noqa: E402
from audit2_genre_confound import (  # noqa: E402
    load_argugpt, load_ghostbuster_machine, load_student_llm_machine, sample,
)

SEED = 20260907
N_SAMPLE = 500  # audit2's convention for unlabeled pools
RIDGE_ALPHA = 1.0
KFOLDS = 5

SCORES_DIR = Path(__file__).resolve().parent / "data" / "scores"
SCORES_DIR.mkdir(parents=True, exist_ok=True)
RAW_OUT = Path(__file__).resolve().parent / "pool_measurement_raw.json"

# PersonaLLM filename trait-pole encoding (order: EXT AGR CON NEU OPN);
# label=1 for the first-listed pole, 0 for the second.
PERSONA_POLES = {
    "cEXT": ("extr", "intr"),
    "cAGR": ("agre", "anta"),
    "cCON": ("cons", "unco"),
    "cNEU": ("neur", "emot"),
    "cOPN": ("open", "clos"),
}
PERSONA_POLE_ORDER = ["cEXT", "cAGR", "cCON", "cNEU", "cOPN"]


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", file=sys.stderr)


def truncate_words(text, n):
    if n is None:
        return text
    return " ".join(text.split()[:n])


def embed(st, texts, desc):
    log(f"embedding {len(texts)} texts ({desc})")
    return st.encode(texts, show_progress_bar=False, batch_size=64)


def cross_fit_trait_scores(emb, y, seed=SEED, k=KFOLDS):
    """K-fold cross-fitted RidgeClassifier decision scores: every text
    scored by a model that did NOT see it in training. Returns scores
    aligned to input order."""
    n = len(y)
    scores = np.zeros(n)
    kf = KFold(n_splits=k, shuffle=True, random_state=seed)
    for train_idx, test_idx in kf.split(emb):
        clf = RidgeClassifier(alpha=RIDGE_ALPHA)
        clf.fit(emb[train_idx], y[train_idx])
        scores[test_idx] = clf.decision_function(emb[test_idx])
    return scores


def fit_full_trait_model(emb, y, seed=SEED):
    clf = RidgeClassifier(alpha=RIDGE_ALPHA)
    clf.fit(emb, y)
    return clf


def load_big5():
    import openpyxl
    wb = openpyxl.load_workbook("data/big5_personality_essays/essays.xlsx", read_only=True, data_only=True)
    ws = wb["Foaie1"]
    rows = []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0 or row[0] is None:
            continue
        rows.append(row)
    return rows  # col0=Essay,1=Openness,2=Conscienciousness,3=Extraversion,4=Agreeableness,5=Neuroticism


BIG5_TRAIT_COL = {"cOPN": 1, "cCON": 2, "cEXT": 3, "cAGR": 4, "cNEU": 5}


def load_personallm(model_dir):
    files = sorted(glob.glob(f"data/personallm/text/{model_dir}/*.txt"))
    out = []
    for fp in files:
        t = Path(fp).read_text(encoding="utf-8", errors="ignore").strip()
        if not t:
            continue
        name = Path(fp).stem
        parts = name.split("_")[:5]
        labels = {}
        for trait, pos in zip(PERSONA_POLE_ORDER, parts):
            hi, lo = PERSONA_POLES[trait]
            if pos == hi:
                labels[trait] = 1
            elif pos == lo:
                labels[trait] = 0
            else:
                labels[trait] = None
        out.append({"id": name, "text": t, "labels": labels, "path": fp})
    return out


def sha256_norm(text):
    norm = " ".join(text.split())
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


def pool_stats(scores_by_trait, v_h_by_trait, mu_h_by_trait):
    """kappa, delta per trait from a machine pool's trait scores."""
    out = {}
    for trait, s in scores_by_trait.items():
        s = np.asarray(s, dtype=float)
        mu_m = float(np.mean(s))
        s2_m = float(np.var(s, ddof=1))
        v_h = v_h_by_trait[trait]
        mu_h = mu_h_by_trait[trait]
        out[trait] = {
            "mu_M": mu_m,
            "s2_M": s2_m,
            "kappa": s2_m / v_h if v_h else None,
            "delta": (mu_m - mu_h) / np.sqrt(v_h) if v_h else None,
        }
    return out


def main():
    from sentence_transformers import SentenceTransformer
    st = SentenceTransformer("all-MiniLM-L6-v2")

    raw = {"meta": {"seed": SEED, "ridge_alpha": RIDGE_ALPHA, "kfolds": KFOLDS, "n_sample_unlabeled": N_SAMPLE}}

    # ---------- 1. PK human side: cross-fitted trait scores, full-refit model ----------
    log("loading PK")
    pk = list(load_pk())
    pk_texts = [r["text"] for r in pk]
    pk_ids = [r["author_id"] for r in pk]
    pk_emb = embed(st, pk_texts, "PK full")

    pk_y = {t: np.array([1 if r["traits"][t] == "y" else 0 for r in pk]) for t in TRAIT_COLUMNS}

    pk_cross_scores = {}
    pk_full_models = {}
    r_H = {}
    mu_H = {}
    V_H = {}
    for trait in TRAIT_COLUMNS:
        log(f"cross-fitting {trait} on PK ({KFOLDS}-fold)")
        cs = cross_fit_trait_scores(pk_emb, pk_y[trait])
        pk_cross_scores[trait] = cs
        r, p = pointbiserialr(pk_y[trait], cs)
        r_H[trait] = {"r": float(r), "p": float(p)}
        mu_H[trait] = float(np.mean(cs))
        V_H[trait] = float(np.var(cs, ddof=1))
        pk_full_models[trait] = fit_full_trait_model(pk_emb, pk_y[trait])
        log(f"  r_H={r:.4f} p={p:.2e} mu_H={mu_H[trait]:.4f} V_H={V_H[trait]:.4f}")

    raw["pk_human"] = {
        "n": len(pk),
        "r_H": r_H,
        "mu_H": mu_H,
        "V_H": V_H,
    }

    # save PK per-text cross-fitted scores
    pk_score_path = SCORES_DIR / "pk_human.json"
    pk_score_path.write_text(json.dumps({
        "ids": pk_ids,
        "labels": {t: pk_y[t].tolist() for t in TRAIT_COLUMNS},
        "cross_fitted_scores": {t: pk_cross_scores[t].tolist() for t in TRAIT_COLUMNS},
    }))
    log(f"wrote {pk_score_path}")

    # ---------- 2. Labeled machine pools ----------
    labeled_pools = {}

    log("loading Big5")
    big5_rows = load_big5()
    big5_texts = [r[0] for r in big5_rows]
    big5_emb = embed(st, big5_texts, "Big5")
    big5_labels = {t: np.array([float(r[BIG5_TRAIT_COL[t]]) for r in big5_rows]) for t in TRAIT_COLUMNS}
    labeled_pools["big5_personality_essays"] = {
        "texts": big5_texts, "ids": [f"big5_{i}" for i in range(len(big5_texts))],
        "emb": big5_emb, "labels": big5_labels,
    }

    for gen in ["gpt-4-0613", "gpt-3.5-turbo-0613", "llama-2"]:
        log(f"loading personallm {gen}")
        recs = load_personallm(gen)
        texts = [r["text"] for r in recs]
        emb = embed(st, texts, f"personallm {gen}")
        labels = {t: np.array([r["labels"][t] if r["labels"][t] is not None else np.nan for r in recs]) for t in TRAIT_COLUMNS}
        labeled_pools[f"personallm_{gen}"] = {
            "texts": texts, "ids": [r["id"] for r in recs], "emb": emb, "labels": labels,
        }

    labeled_results = {}
    for pool_name, pool in labeled_pools.items():
        log(f"scoring labeled pool {pool_name}")
        trait_scores = {}
        chat = {}
        for trait in TRAIT_COLUMNS:
            model = pk_full_models[trait]
            s = model.decision_function(pool["emb"])
            trait_scores[trait] = s
            lab = pool["labels"][trait]
            mask = ~np.isnan(lab)
            if mask.sum() >= 2 and len(set(lab[mask].tolist())) > 1:
                r, p = pointbiserialr(lab[mask], s[mask])
            else:
                r, p = None, None
            chat[trait] = {"chat_r": (float(r) if r is not None else None),
                            "chat_p": (float(p) if p is not None else None),
                            "n": int(mask.sum())}

        stats = pool_stats(trait_scores, V_H, mu_H)
        for trait in TRAIT_COLUMNS:
            stats[trait]["chat_r"] = chat[trait]["chat_r"]
            stats[trait]["chat_p"] = chat[trait]["chat_p"]
            stats[trait]["r_H"] = r_H[trait]["r"]
            # g = Cov(x_M, theta) / Cov(x_H, theta), the covariance-ratio form (pass-3 review T7a /
            # PASS3-FIXES.md: this was chat_r/r_H, which drifted from the corrected form already
            # used in pool_measurements.json's "g" column, "g_old_ratio_form" is that stale ratio).
            kappa = stats[trait]["kappa"]
            stats[trait]["g_old_ratio_form"] = (chat[trait]["chat_r"] / r_H[trait]["r"]) if (chat[trait]["chat_r"] is not None and r_H[trait]["r"]) else None
            stats[trait]["g"] = (chat[trait]["chat_r"] * (kappa ** 0.5) / r_H[trait]["r"]) if (chat[trait]["chat_r"] is not None and r_H[trait]["r"] and kappa is not None and kappa >= 0) else None

        # detector AUC vs PK-human, matched sample
        n = min(N_SAMPLE, len(pool["texts"])) if pool_name != "big5_personality_essays" else len(pool["texts"])
        pk_this_texts = sample(pk_texts, n, SEED)
        pool_texts_for_auc = pool["texts"][:n] if n == len(pool["texts"]) else sample(pool["texts"], n, SEED + hash(pool_name) % 1000)
        log(f"  roberta AUC vs PK, n={n}")
        y_auc = [0] * n + [1] * len(pool_texts_for_auc)
        scores_auc = run_roberta_scores(pk_this_texts + pool_texts_for_auc)
        fpr, tpr, _ = roc_curve(y_auc, scores_auc)
        pool_auc = float(auc(fpr, tpr))
        detector_scores_pool = scores_auc[n:]

        # A3 check: correlate detector score (on the pool's own full text list, not just
        # the AUC subsample) against pool's own trait label, within pool
        log(f"  roberta detector scores for A3 (full pool, n={len(pool['texts'])})")
        det_full = run_roberta_scores(pool["texts"])
        a3 = {}
        for trait in TRAIT_COLUMNS:
            lab = pool["labels"][trait]
            mask = ~np.isnan(lab)
            if mask.sum() >= 2 and len(set(lab[mask].tolist())) > 1:
                r, p = pointbiserialr(lab[mask], np.array(det_full)[mask])
                a3[trait] = {"r": float(r), "p": float(p), "n": int(mask.sum())}
            else:
                a3[trait] = {"r": None, "p": None, "n": int(mask.sum())}

        score_path = SCORES_DIR / f"{pool_name}.json"
        score_path.write_text(json.dumps({
            "ids": pool["ids"],
            "labels": {t: [None if (isinstance(v, float) and np.isnan(v)) else float(v) for v in pool["labels"][t]] for t in TRAIT_COLUMNS},
            "trait_scores": {t: trait_scores[t].tolist() for t in TRAIT_COLUMNS},
            "detector_p_machine": det_full,
        }))
        log(f"  wrote {score_path}")

        labeled_results[pool_name] = {
            "n": len(pool["texts"]),
            "trait_stats": stats,
            "detector_auc_vs_pk": pool_auc,
            "detector_auc_n": n,
            "a3_detector_vs_own_label": a3,
            "score_file": str(score_path.relative_to(Path(__file__).resolve().parent)),
        }

    raw["labeled_pools"] = labeled_results

    # ---------- 3. Unlabeled Audit-2 pools ----------
    unlabeled_loaders = {
        "argugpt": load_argugpt,
        "ghostbuster_gpt_writing": load_ghostbuster_machine,
        "student_llm_essays": load_student_llm_machine,
    }
    unlabeled_results = {}
    for pool_name, loader in unlabeled_loaders.items():
        log(f"loading unlabeled pool {pool_name}")
        texts_all = loader()
        n = min(N_SAMPLE, len(texts_all))
        pool_sample = sample(texts_all, n, SEED + hash(pool_name) % 1000)
        pk_this = sample(pk_texts, n, SEED)

        emb = embed(st, pool_sample, pool_name)
        trait_scores = {}
        for trait in TRAIT_COLUMNS:
            trait_scores[trait] = pk_full_models[trait].decision_function(emb)
        stats = pool_stats(trait_scores, V_H, mu_H)

        log(f"  roberta AUC vs PK, n={n}")
        y_auc = [0] * n + [1] * n
        scores_auc = run_roberta_scores(pk_this + pool_sample)
        fpr, tpr, _ = roc_curve(y_auc, scores_auc)
        pool_auc = float(auc(fpr, tpr))
        det_pool = scores_auc[n:]

        score_path = SCORES_DIR / f"{pool_name}.json"
        score_path.write_text(json.dumps({
            "ids": [f"{pool_name}_{i}" for i in range(n)],
            "trait_scores": {t: trait_scores[t].tolist() for t in TRAIT_COLUMNS},
            "detector_p_machine": det_pool,
        }))
        log(f"  wrote {score_path}")

        unlabeled_results[pool_name] = {
            "n_pool_total": len(texts_all),
            "n_used": n,
            "trait_stats": stats,
            "detector_auc_vs_pk": pool_auc,
            "score_file": str(score_path.relative_to(Path(__file__).resolve().parent)),
        }

    raw["unlabeled_pools"] = unlabeled_results

    # ---------- 4. Check (b): Spearman-Brown truncation ----------
    log("truncation check: re-cross-fitting PK at 100 and 190 words")
    trunc_results = {}
    for n_words in (100, 190):
        pk_texts_trunc = [truncate_words(t, n_words) for t in pk_texts]
        emb_t = embed(st, pk_texts_trunc, f"PK truncated {n_words}w")
        r_h_trunc = {}
        for trait in TRAIT_COLUMNS:
            cs = cross_fit_trait_scores(emb_t, pk_y[trait])
            r, p = pointbiserialr(pk_y[trait], cs)
            r_h_trunc[trait] = {"r": float(r), "p": float(p)}
        trunc_results[str(n_words)] = r_h_trunc
        log(f"  {n_words}w: " + ", ".join(f"{t}={r_h_trunc[t]['r']:.3f}" for t in TRAIT_COLUMNS))
    raw["spearman_brown_truncation"] = {
        "full_length_r_H": {t: r_H[t]["r"] for t in TRAIT_COLUMNS},
        "truncated_r_H": trunc_results,
        "memo_prediction_cEXT": {"190w_or_full": 0.245, "100w": 0.180},
    }

    # ---------- 5. Check (c): Q12 Big5 label balance ----------
    q12 = {}
    for trait in TRAIT_COLUMNS:
        lab = big5_labels[trait]
        vals, counts = np.unique(lab, return_counts=True)
        q12[trait] = {str(int(v)): int(c) for v, c in zip(vals, counts)}
    raw["q12_big5_label_balance"] = q12

    # ---------- 6. Check (d): PersonaLLM human_stories vs PK hash ----------
    log("hash-comparing personallm human_stories vs PK essays.csv")
    human_stories_files = sorted(glob.glob("data/personallm/text/human_stories/*.txt"))
    hs_hashes = {}
    for fp in human_stories_files:
        t = Path(fp).read_text(encoding="utf-8", errors="ignore").strip()
        hs_hashes[Path(fp).stem] = sha256_norm(t)
    pk_hashes = set(sha256_norm(t) for t in pk_texts)
    n_exact_match = sum(1 for h in hs_hashes.values() if h in pk_hashes)
    raw["check_d_personallm_human_vs_pk_hash"] = {
        "n_human_stories_files": len(hs_hashes),
        "n_pk_essays": len(pk_texts),
        "n_exact_sha256_match_normalized_whitespace": n_exact_match,
        "fraction_matched": n_exact_match / len(hs_hashes) if hs_hashes else None,
        "note": "normalized = whitespace-collapsed text, sha256; human_stories files carry LOCNAME/PROPNAME "
                "anonymization tokens not visibly present in essays.csv raw text -- exact-match fraction reveals "
                "whether this is the same underlying corpus with different preprocessing or a different corpus.",
    }

    RAW_OUT.write_text(json.dumps(raw, indent=2))
    log(f"wrote {RAW_OUT}")
    print("DONE")


if __name__ == "__main__":
    main()
