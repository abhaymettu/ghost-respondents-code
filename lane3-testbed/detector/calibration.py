"""Detector calibration for SPEC 2.4.

Two detectors:
  1. A published open-weights AI-text classifier:
     openai-community/roberta-base-openai-detector (MIT license). Trained
     originally to detect GPT-2 output, not ChatGPT -- using it as-is
     (no fine-tuning) is the realistic "off-the-shelf detector calibrated
     by threshold-picking only" scenario the SPEC describes, and its
     domain mismatch (GPT-2 vs ChatGPT vs essays) is exactly the kind of
     transfer gap section 2.4 wants measured.
  2. A simple feature baseline: logistic regression over the stylometric
     features in detector/features.py (word count, sentence length,
     type-token ratio, punctuation rate), fit on the same HC3 split.

Calibration procedure:
  - Stratified sample of HC3 (question, human_answer, chatgpt_answer)
    triples across all five sources, split into calibrate/test.
  - Threshold chosen on the calibrate split via Youden's J (maximizes
    se + sp - 1); "calibrated" operating point is se/sp of that threshold
    on the held-out HC3 test split (in-domain).
  - "Degraded" operating point: the same HC3-calibrated threshold applied
    to the essays testbed. Essays currently contains ONLY human-authored
    text (no LLM counterparts yet -- generation is gated on the burn
    report). So only specificity (false-positive rate on genuine human
    text, out of domain) is measurable there; sensitivity is not
    computable until counterpart generation exists. This is reported as
    a partial operating point, not a full (se, sp) pair.
  - "Oracle" operating point is se = sp = 1 by construction (the ceiling
    case used in the SPEC 4.3 simulation grid), not something to measure.

Run: python3 detector/calibration.py
Writes detector/calibration_results.json.
"""

import json
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, auc

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from loaders.hc3_loader import SOURCES, load_source  # noqa: E402
from loaders.essays_loader import load as load_essays  # noqa: E402
from detector.features import feature_vector  # noqa: E402

RNG_SEED = 20260907
N_PER_SOURCE = 250  # HC3 questions sampled per source (human+chatgpt = 2x texts)
ESSAYS_SAMPLE_N = 500  # essays sampled for the out-of-domain sp check
MODEL_NAME = "openai-community/roberta-base-openai-detector"
BATCH_SIZE = 16
MAX_LEN = 256

OUT_PATH = Path(__file__).resolve().parent / "calibration_results.json"


def sample_hc3_pairs(n_per_source: int, seed: int):
    rng = random.Random(seed)
    pairs = []  # (text, label) label 1=human, 0=machine ; kept alongside source
    for source in SOURCES:
        recs = list(load_source(source))
        rng.shuffle(recs)
        take = [r for r in recs if r.get("human_answers") and r.get("chatgpt_answers")][:n_per_source]
        for r in take:
            human_text = r["human_answers"][0].strip()
            machine_text = r["chatgpt_answers"][0].strip()
            if not human_text or not machine_text:
                continue
            pairs.append({"text": human_text, "label": 1, "source": source})
            pairs.append({"text": machine_text, "label": 0, "source": source})
    rng.shuffle(pairs)
    return pairs


def split_calibrate_test(items, frac_calibrate=0.5, seed=RNG_SEED):
    rng = random.Random(seed + 1)
    items = items[:]
    rng.shuffle(items)
    k = int(len(items) * frac_calibrate)
    return items[:k], items[k:]


def run_roberta_scores(texts, batch_size=BATCH_SIZE):
    from transformers import AutoTokenizer, AutoModelForSequenceClassification

    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()
    # id2label: {0: 'Fake', 1: 'Real'} -- score_machine = P(Fake)
    scores = []
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            inputs = tok(batch, return_tensors="pt", padding=True, truncation=True, max_length=MAX_LEN)
            out = model(**inputs)
            probs = torch.softmax(out.logits, dim=-1)
            scores.extend(probs[:, 0].tolist())  # P(machine)
    print(f"  roberta scored {len(texts)} texts in {time.time() - t0:.1f}s", file=sys.stderr)
    return scores


def youden_threshold(y_true_machine, scores_machine):
    """y_true_machine: 1 if actually machine-authored, 0 if human.
    scores_machine: detector's P(machine) score. Returns threshold maximizing se+sp-1."""
    fpr, tpr, thresholds = roc_curve(y_true_machine, scores_machine)
    # fpr = P(flag | human) = 1 - sp ; tpr = P(flag | machine) = se
    j = tpr - fpr
    best = int(np.argmax(j))
    return thresholds[best], float(tpr[best]), float(1 - fpr[best])


def se_sp_at_threshold(y_true_machine, scores_machine, threshold):
    y_true_machine = np.array(y_true_machine)
    scores_machine = np.array(scores_machine)
    flagged = scores_machine >= threshold
    machine_mask = y_true_machine == 1
    human_mask = y_true_machine == 0
    se = flagged[machine_mask].mean() if machine_mask.any() else None
    sp = (~flagged[human_mask]).mean() if human_mask.any() else None
    return (float(se) if se is not None else None, float(sp) if sp is not None else None)


def main():
    print("Sampling HC3 pairs...", file=sys.stderr)
    pairs = sample_hc3_pairs(N_PER_SOURCE, RNG_SEED)
    calibrate, test = split_calibrate_test(pairs)
    print(f"  {len(pairs)} texts total ({len(calibrate)} calibrate / {len(test)} test)", file=sys.stderr)

    # --- Detector 1: published open-weights classifier ---
    print("Running roberta-base-openai-detector on calibrate split...", file=sys.stderr)
    cal_texts = [p["text"] for p in calibrate]
    cal_labels_machine = [1 - p["label"] for p in calibrate]  # 1 = machine
    cal_scores = run_roberta_scores(cal_texts)
    threshold, cal_se, cal_sp = youden_threshold(cal_labels_machine, cal_scores)

    print("Running roberta-base-openai-detector on test split...", file=sys.stderr)
    test_texts = [p["text"] for p in test]
    test_labels_machine = [1 - p["label"] for p in test]
    test_scores = run_roberta_scores(test_texts)
    test_se, test_sp = se_sp_at_threshold(test_labels_machine, test_scores, threshold)
    fpr, tpr, _ = roc_curve(test_labels_machine, test_scores)
    roberta_auc = float(auc(fpr, tpr))

    # --- Detector 2: simple feature baseline (logistic regression) ---
    print("Fitting feature-baseline logistic regression...", file=sys.stderr)
    X_cal = np.array([feature_vector(t) for t in cal_texts])
    y_cal = np.array(cal_labels_machine)
    X_test = np.array([feature_vector(t) for t in test_texts])
    y_test = np.array(test_labels_machine)

    clf = LogisticRegression(max_iter=2000)
    clf.fit(X_cal, y_cal)
    cal_probs = clf.predict_proba(X_cal)[:, 1]
    feat_threshold, feat_cal_se, feat_cal_sp = youden_threshold(y_cal, cal_probs)
    test_probs = clf.predict_proba(X_test)[:, 1]
    feat_test_se, feat_test_sp = se_sp_at_threshold(y_test, test_probs, feat_threshold)
    fpr_f, tpr_f, _ = roc_curve(y_test, test_probs)
    feat_auc = float(auc(fpr_f, tpr_f))

    # --- Out-of-domain degraded check: essays (human-only) ---
    print(f"Sampling {ESSAYS_SAMPLE_N} essays for out-of-domain sp check...", file=sys.stderr)
    essays = list(load_essays())
    rng = random.Random(RNG_SEED + 2)
    rng.shuffle(essays)
    essays_sample = essays[:ESSAYS_SAMPLE_N]
    essay_texts = [e["text"] for e in essays_sample]

    print("Running roberta detector on essays sample...", file=sys.stderr)
    essay_scores_roberta = run_roberta_scores(essay_texts)
    essay_flagged_roberta = [s >= threshold for s in essay_scores_roberta]
    ood_sp_roberta = 1 - (sum(essay_flagged_roberta) / len(essay_flagged_roberta))

    X_essays = np.array([feature_vector(t) for t in essay_texts])
    essay_probs_feat = clf.predict_proba(X_essays)[:, 1]
    essay_flagged_feat = essay_probs_feat >= feat_threshold
    ood_sp_feat = 1 - essay_flagged_feat.mean()

    results = {
        "meta": {
            "seed": RNG_SEED,
            "n_per_source": N_PER_SOURCE,
            "hc3_calibrate_n": len(calibrate),
            "hc3_test_n": len(test),
            "essays_ood_n": len(essay_texts),
        },
        "roberta_base_openai_detector": {
            "model": MODEL_NAME,
            "license": "MIT",
            "note": "trained on GPT-2 outputs, applied zero-shot to ChatGPT/HC3 text -- realistic off-the-shelf transfer scenario",
            "threshold_P_machine": float(threshold),
            "calibrated_in_domain": {
                "split": "HC3 held-out test",
                "se": test_se,
                "sp": test_sp,
                "auc": roberta_auc,
            },
            "degraded_out_of_domain": {
                "split": "essays (human-only, no machine counterparts yet)",
                "se": None,
                "se_note": "not computable: essays testbed has no LLM-authored text yet (generation gated on burn report)",
                "sp": float(ood_sp_roberta),
            },
            "oracle": {"se": 1.0, "sp": 1.0, "note": "definitional ceiling, not measured"},
        },
        "feature_baseline_logreg": {
            "features": [
                "n_words", "n_sentences", "avg_word_len", "avg_sentence_len_words",
                "type_token_ratio", "punct_per_100_words", "comma_per_100_words",
            ],
            "threshold_P_machine": float(feat_threshold),
            "calibrated_in_domain": {
                "split": "HC3 held-out test",
                "se": feat_test_se,
                "sp": feat_test_sp,
                "auc": feat_auc,
            },
            "degraded_out_of_domain": {
                "split": "essays (human-only, no machine counterparts yet)",
                "se": None,
                "se_note": "not computable: essays testbed has no LLM-authored text yet (generation gated on burn report)",
                "sp": float(ood_sp_feat),
            },
            "oracle": {"se": 1.0, "sp": 1.0, "note": "definitional ceiling, not measured"},
        },
        "norc_pact_reference_range": {
            "in_domain_se_ballpark": 0.99,
            "out_of_domain_se_ballpark": "mid-80s (%)",
            "source": "https://www.norc.org/content/dam/norc-org/pdf2025/AAPOR%20Detecting%20AI-Generated%20Survey%20Responses%20-%20Lilian%20Huang.pdf",
        },
    }

    OUT_PATH.write_text(json.dumps(results, indent=2))
    print(f"Wrote {OUT_PATH}", file=sys.stderr)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
