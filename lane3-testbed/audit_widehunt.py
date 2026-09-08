"""Wide corpus hunt: genre-confound check for personal-narrative-genre c=0 candidates
found beyond the original three (ArguGPT / Ghostbuster / student_llm_essays).

Same machinery as audit2_genre_confound.py: PK-human vs candidate pool, roberta
zero-shot detector, AUC vs the 0.472 same-genre benchmark from Audit 2.
"""
import glob
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sklearn.metrics import roc_curve, auc  # noqa: E402
from detector.calibration import run_roberta_scores  # noqa: E402
from loaders.essays_loader import load as load_pk  # noqa: E402

SEED = 20260907
N_SAMPLE = 500


def sample(items, n, seed):
    rng = random.Random(seed)
    items = list(items)
    rng.shuffle(items)
    return items[:n]


def auc_for(human_texts, machine_texts):
    texts = human_texts + machine_texts
    y = [0] * len(human_texts) + [1] * len(machine_texts)
    scores = run_roberta_scores(texts)
    fpr, tpr, _ = roc_curve(y, scores)
    return float(auc(fpr, tpr))


def load_personallm(model_dir):
    files = sorted(glob.glob(f"data/personallm/text/{model_dir}/*.txt"))
    out = []
    for fp in files:
        t = Path(fp).read_text(encoding="utf-8", errors="ignore").strip()
        if t:
            out.append(t)
    return out


def main():
    pk = [r["text"] for r in load_pk()]

    pools = {
        "personallm_gpt4": load_personallm("gpt-4-0613"),
        "personallm_gpt35": load_personallm("gpt-3.5-turbo-0613"),
        "personallm_llama2": load_personallm("llama-2"),
        "personallm_combined": (
            load_personallm("gpt-4-0613")
            + load_personallm("gpt-3.5-turbo-0613")
            + load_personallm("llama-2")
        ),
    }

    results = {}
    for name, texts in pools.items():
        n = min(N_SAMPLE, len(texts))
        pool_sample = sample(texts, n, SEED + hash(name) % 1000)
        pk_this = sample(pk, n, SEED)
        a = auc_for(pk_this, pool_sample)
        results[name] = {"n_pool": len(texts), "n_used": n, "auc": a}
        print(f"{name}: n_pool={len(texts)} n_used={n} AUC={a:.4f}", file=sys.stderr)

    import json
    Path("widehunt_results.json").write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
