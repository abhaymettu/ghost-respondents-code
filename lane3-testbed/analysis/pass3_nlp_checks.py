"""Read-only evidence checks for pass3-nlp-review.md. Run from any directory.

Uses saved scores, local source data and the cached tokenizer; no model fitting,
generation or downloads. Prints JSON to stdout. Disable bytecode when invoking.
"""
import csv
import hashlib
import json
import os
import random
import sys
from pathlib import Path

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import numpy as np
from sklearn.model_selection import KFold

ROOT = Path(__file__).resolve().parents[2]
L3 = ROOT / "lane3-testbed"
sys.path.insert(0, str(L3))
sys.path.insert(0, str(ROOT / "lane4-simulation"))
from inject.pools import lane3_pool, calibration_split


def residual(x, covariates):
    z = np.column_stack([np.ones(len(x)), covariates])
    return x - z @ np.linalg.lstsq(z, x, rcond=None)[0]


def rbar(x):
    return float(np.corrcoef(x.T)[np.triu_indices(4, 1)].mean())


def main():
    paths = [L3 / "data/scores/pk_human.json", L3 / "data/essays/essays.csv",
             L3 / "data/big5_personality_essays/essays.xlsx",
             ROOT / "lane4-simulation/inject/pools.py",
             L3 / "pool_measurement.py", L3 / "detector/calibration.py"]
    out = {"input_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in paths}}
    d = json.loads(paths[0].read_text())
    with paths[1].open(encoding="cp1252", newline="") as f:
        rows = list(csv.DictReader(f))
    assert [r["#AUTHID"] for r in rows] == d["ids"]
    assert len(set(d["ids"])) == len(rows)
    idx = np.array([i for i in range(len(rows))
                    if all(d[f"chunk_{j}_oof"][i] is not None for j in range(1, 5))])
    length = np.array([len(r["TEXT"].split()) for r in rows])[idx]
    out["n_complete_chunks"] = len(idx)
    out["partial_correlations"] = {}
    for trait in d["labels"]:
        y = np.array(d["labels"][trait], dtype=float)[idx]
        assert set(y) == {0, 1}
        x = np.array([[d[f"chunk_{j}_oof"][i][trait] for j in range(1, 5)] for i in idx])
        raw = rbar(x)
        part = rbar(residual(x, y))
        corr = np.corrcoef(np.column_stack([x, y]).T)
        ij = np.triu_indices(4, 1)
        direct = ((corr[:4, :4] - np.outer(corr[:4, 4], corr[:4, 4])) /
                  np.sqrt(np.outer(1 - corr[:4, 4] ** 2, 1 - corr[:4, 4] ** 2)))[ij].mean()
        assert abs(part - direct) < 1e-12
        out["partial_correlations"][trait] = {
            "raw": raw, "label_partial": part,
            "relative_reduction_pct": 100 * (1 - part / raw),
            "length_partial": rbar(residual(x, length)),
            "length_label_partial": rbar(residual(x, np.column_stack([length, y]))),
            "chunk_label_correlations": corr[:4, 4].tolist(),
        }

    h = lane3_pool("pk_human", "EXT")
    selected = [i for i, t in enumerate(h.texts) if t.chunk_scores]
    live = np.array([h.texts[i].chunk_scores for i in selected])
    old = np.array([[d[f"chunk_{j}"][i]["cEXT"] for j in range(1, 5)] for i in selected])
    new = np.array([[d[f"chunk_{j}_oof"][i]["cEXT"] for j in range(1, 5)] for i in selected])
    out["live_chunk_loader"] = {"max_diff_original": float(abs(live - old).max()),
                                "max_diff_oof": float(abs(live - new).max()), "rbar": rbar(live)}
    base, ref = calibration_split(h)
    base_ids, ref_ids = {t.text_id for t in base.texts}, set(ref.text_ids)
    assert not base_ids & ref_ids
    fold = np.empty(len(rows), dtype=int)
    for f, (_, te) in enumerate(KFold(5, shuffle=True, random_state=20260907).split(fold)):
        fold[te] = f
    out["scorer_training_crosses_reference_split"] = [
        {"fold": f,
         "base_labels_in_train": sum(t.text_id in base_ids and fold[i] != f for i, t in enumerate(h.texts)),
         "reference_labels_in_train": sum(t.text_id in ref_ids and fold[i] != f for i, t in enumerate(h.texts))}
        for f in range(5)]

    cal = json.loads((L3 / "detector/calibration_results.json").read_text())
    threshold = cal["roberta_base_openai_detector"]["threshold_P_machine"]
    transfer = {"threshold": threshold,
                "pk_specificity": float(np.mean(np.array(d["detector_p_machine"]) < threshold))}
    for name in ["big5_personality_essays", "personallm_gpt-4-0613",
                 "personallm_gpt-3.5-turbo-0613", "personallm_llama-2"]:
        blob = json.loads((L3 / f"data/scores/{name}.json").read_text())
        transfer[name] = {"n": len(blob["ids"]),
                          "sensitivity": float(np.mean(np.array(blob["detector_p_machine"]) >= threshold))}
    out["hc3_threshold_transfer_descriptive"] = transfer

    from detector.calibration import sample_hc3_pairs, split_calibrate_test, RNG_SEED, N_PER_SOURCE
    from loaders.hc3_loader import SOURCES, load_source
    rng = random.Random(RNG_SEED)
    pairs = []
    for source in SOURCES:
        records = list(load_source(source))
        rng.shuffle(records)
        take = [r for r in records if r.get("human_answers") and r.get("chatgpt_answers")][:N_PER_SOURCE]
        for i, r in enumerate(take):
            human, machine = r["human_answers"][0].strip(), r["chatgpt_answers"][0].strip()
            if human and machine:
                pairs.extend([dict(text=human, label=1, source=source, question_id=(source, i)),
                              dict(text=machine, label=0, source=source, question_id=(source, i))])
    rng.shuffle(pairs)
    # calibration.py's sample_hc3_pairs now returns question_id too (pass-3 fix T5) -- direct compare.
    assert pairs == sample_hc3_pairs(N_PER_SOURCE, RNG_SEED)
    calibrate, test = split_calibrate_test(pairs)
    cids, tids = {r["question_id"] for r in calibrate}, {r["question_id"] for r in test}
    out["hc3_split"] = {"questions": len(cids | tids), "shared_questions": len(cids & tids),
                        "test_texts_with_calibration_question": sum(r["question_id"] in cids for r in test),
                        "test_texts": len(test)}

    from transformers import AutoTokenizer
    cached = Path.home() / ".cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/snapshots"
    snapshot = cached / "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
    tokenizer = AutoTokenizer.from_pretrained(str(snapshot), local_files_only=True)
    lengths = np.array([len(t) for t in tokenizer([r["TEXT"] for r in rows],
                                                 truncation=False, add_special_tokens=True)["input_ids"]])
    out["tokenization"] = {"cached_revision": snapshot.name,
                           "sentence_bert_config": json.loads((snapshot / "sentence_bert_config.json").read_text()),
                           "n": len(rows), "over256": int((lengths > 256).sum()),
                           "median_tokens_including_specials": float(np.median(lengths)),
                           "retained_content_token_fraction": float(np.minimum(lengths - 2, 254).sum() / (lengths - 2).sum())}
    import openpyxl
    wb = openpyxl.load_workbook(paths[2], read_only=True, data_only=True)
    essays = [r for r in list(wb["Foaie1"].values)[1:] if r[0] is not None]
    norm = lambda s: " ".join(s.lower().split())
    pk = {norm(r["TEXT"]) for r in rows}
    out["big5_workbook"] = {"n": len(essays), "normalized_exact_matches_pk": sum(norm(r[0]) in pk for r in essays)}
    wb.close()
    print(json.dumps(out, indent=2, default=lambda v: v.item()))


if __name__ == "__main__":
    main()
