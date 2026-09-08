"""Fork audit 3: trait recoverability / realized coupling c-hat.

Fit per-FFM-dimension ridge on PK essay embeddings vs PK binary trait
labels, sanity-check on PK held-out split, apply to Big5PersonalityEssays
machine essays, correlate predicted trait vs Big5's own stated label.
"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
from sklearn.linear_model import RidgeClassifier  # noqa: E402
from sklearn.model_selection import train_test_split  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402
from scipy.stats import pointbiserialr  # noqa: E402
from loaders.essays_loader import load as load_pk, TRAIT_COLUMNS  # noqa: E402

SEED = 20260907


def load_big5():
    import openpyxl
    wb = openpyxl.load_workbook("data/big5_personality_essays/essays.xlsx", read_only=True, data_only=True)
    ws = wb["Foaie1"]
    rows = []
    header = None
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            header = row
            continue
        if row[0] is None:
            continue
        rows.append(row)
    # header: Essay, Openness, Conscienciousness, Extraversion, Agreeableness, Neuroticism
    return header, rows


def main():
    from sentence_transformers import SentenceTransformer

    st = SentenceTransformer("all-MiniLM-L6-v2")

    pk = list(load_pk())
    pk_texts = [r["text"] for r in pk]
    print(f"Embedding {len(pk_texts)} PK essays...", file=sys.stderr)
    pk_emb = st.encode(pk_texts, show_progress_bar=True, batch_size=64)

    header, big5_rows = load_big5()
    big5_texts = [r[0] for r in big5_rows]
    print(f"Embedding {len(big5_texts)} Big5 machine essays...", file=sys.stderr)
    big5_emb = st.encode(big5_texts, show_progress_bar=True, batch_size=64)

    # header col order: Openness, Conscienciousness, Extraversion, Agreeableness, Neuroticism
    # local PK trait cols: cEXT cNEU cAGR cCON cOPN (y/n)
    trait_map = {
        "cOPN": 1,  # Openness col idx in big5_rows
        "cCON": 2,  # Conscienciousness
        "cEXT": 3,  # Extraversion
        "cAGR": 4,  # Agreeableness
        "cNEU": 5,  # Neuroticism
    }

    results = {}
    idx = np.arange(len(pk))
    train_idx, test_idx = train_test_split(idx, test_size=0.25, random_state=SEED)

    for trait in TRAIT_COLUMNS:
        y = np.array([1 if r["traits"][trait] == "y" else 0 for r in pk])
        clf = RidgeClassifier(alpha=1.0)
        clf.fit(pk_emb[train_idx], y[train_idx])

        # sanity check: held-out PK AUC
        held_scores = clf.decision_function(pk_emb[test_idx])
        held_auc = roc_auc_score(y[test_idx], held_scores)

        # refit on all PK data for the Big5 application
        clf_full = RidgeClassifier(alpha=1.0)
        clf_full.fit(pk_emb, y)
        big5_pred_score = clf_full.decision_function(big5_emb)

        big5_col = trait_map[trait]
        big5_label = np.array([float(r[big5_col]) for r in big5_rows])

        # c-hat: correlation between predicted trait score and Big5's stated (binary) label
        r, p = pointbiserialr(big5_label, big5_pred_score)

        results[trait] = {
            "pk_heldout_auc": float(held_auc),
            "chat_r": float(r),
            "chat_p": float(p),
            "n_pk_train": int(len(train_idx)),
            "n_pk_heldout": int(len(test_idx)),
            "n_big5": int(len(big5_rows)),
        }
        print(f"{trait}: heldout_AUC={held_auc:.3f}  c-hat(r)={r:.3f} (p={p:.4f})", file=sys.stderr)

    print(json.dumps({
        "method": "sentence-transformers all-MiniLM-L6-v2 embeddings (384-d) -> RidgeClassifier(alpha=1.0) per FFM dim, "
                  "target = PK binary median-split label (y/n), trained on 75% PK / held out 25% for sanity AUC, "
                  "refit on 100% PK for Big5 application; c-hat = point-biserial r between predicted decision_function "
                  "score and Big5's own stated binary (0/1) label per dimension.",
        "results": results,
    }, indent=2))


if __name__ == "__main__":
    main()
