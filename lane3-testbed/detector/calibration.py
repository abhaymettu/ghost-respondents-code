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
    """Corrected 2026-09-09 (pass-3 review T5/M3): each pair now carries a question_id
    (source, index-within-source), so the human/machine answers to one HC3 question are
    always assignable to the same calibrate/test side. Return value/order unchanged
    (question_id is an added key) so existing consumers (pass3_nlp_checks.py) still match."""
    rng = random.Random(seed)
    pairs = []  # (text, label) label 1=human, 0=machine ; kept alongside source + question_id
    for source in SOURCES:
        recs = list(load_source(source))
        rng.shuffle(recs)
        take = [r for r in recs if r.get("human_answers") and r.get("chatgpt_answers")][:n_per_source]
        for i, r in enumerate(take):
            human_text = r["human_answers"][0].strip()
            machine_text = r["chatgpt_answers"][0].strip()
            if not human_text or not machine_text:
                continue
            qid = (source, i)
            pairs.append({"text": human_text, "label": 1, "source": source, "question_id": qid})
            pairs.append({"text": machine_text, "label": 0, "source": source, "question_id": qid})
    rng.shuffle(pairs)
    return pairs


def split_calibrate_test(items, frac_calibrate=0.5, seed=RNG_SEED):
    """Corrected 2026-09-09 (pass-3 review T5/M3): split by question_id, not by flattened
    row, so a question's human and machine answers never straddle calibrate/test. Previously
    622/1250 questions straddled the split (see PASS3-FIXES.md T5)."""
    rng = random.Random(seed + 1)
    question_ids = sorted({item["question_id"] for item in items})
    rng.shuffle(question_ids)
    k = int(len(question_ids) * frac_calibrate)
    calibrate_qids = set(question_ids[:k])
    calibrate = [item for item in items if item["question_id"] in calibrate_qids]
    test = [item for item in items if item["question_id"] not in calibrate_qids]
    return calibrate, test


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


def question_cluster_bootstrap_ci(test_items, scores, threshold, n_boot=2000, seed=RNG_SEED + 2):
    """Pass-3 review T5/M3: se/sp CI by resampling whole HC3 questions (both the human and
    machine answer move together), not individual rows -- a naive per-row CI understates
    uncertainty because each question contributes a correlated pair."""
    rng = random.Random(seed)
    qids = sorted({it["question_id"] for it in test_items})
    q_to_rows = {q: [] for q in qids}
    for i, it in enumerate(test_items):
        q_to_rows[it["question_id"]].append(i)
    scores = np.array(scores)
    y = np.array([1 - it["label"] for it in test_items])  # 1 = machine
    se_boot, sp_boot = [], []
    for _ in range(n_boot):
        sampled_q = [rng.choice(qids) for _ in range(len(qids))]
        rows = np.concatenate([q_to_rows[q] for q in sampled_q])
        se, sp = se_sp_at_threshold(y[rows], scores[rows], threshold)
        if se is not None:
            se_boot.append(se)
        if sp is not None:
            sp_boot.append(sp)
    return {
        "se_ci95": [float(np.percentile(se_boot, 2.5)), float(np.percentile(se_boot, 97.5))],
        "sp_ci95": [float(np.percentile(sp_boot, 2.5)), float(np.percentile(sp_boot, 97.5))],
        "n_boot": n_boot,
    }


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
    print("Question-clustered bootstrap CI (roberta)...", file=sys.stderr)
    roberta_ci = question_cluster_bootstrap_ci(test, test_scores, threshold)

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
    feat_ci = question_cluster_bootstrap_ci(test, test_probs, feat_threshold)

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
            "split_note": "corrected 2026-09-09 (pass-3 review T5/M3): split is grouped by "
                          "HC3 question, not flattened answer row -- every test question's "
                          "human and machine answers are on the test side only, zero straddle "
                          "by construction (previously 622/1250 questions straddled). "
                          "'new-question' is therefore the only regime measured below; there "
                          "is no more same-question-different-answer case to distinguish.",
        },
        "roberta_base_openai_detector": {
            "model": MODEL_NAME,
            "license": "MIT",
            "note": "trained on GPT-2 outputs, applied zero-shot to ChatGPT/HC3 text -- realistic off-the-shelf transfer scenario",
            "threshold_P_machine": float(threshold),
            "calibrated_in_domain": {
                "split": "HC3 held-out test (question-grouped, new-question)",
                "se": test_se,
                "sp": test_sp,
                "auc": roberta_auc,
                "question_cluster_bootstrap_ci": roberta_ci,
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
                "split": "HC3 held-out test (question-grouped, new-question)",
                "se": feat_test_se,
                "sp": feat_test_sp,
                "auc": feat_auc,
                "question_cluster_bootstrap_ci": feat_ci,
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
            # Corrected 2026-09-09 (pass-3 review T7b): the prior "out_of_domain_se_ballpark:
            # mid-80s" was a misattribution. Huang et al., AAPOR 2025 slide 7 reports
            # general-population precision 0.989/recall 0.999/accuracy 0.990, and
            # technical-domain accuracy upper-80s-to-mid-90s, precision up to 85.7%,
            # recall up to 100% -- it does not report an out-of-domain sensitivity figure.
            "general_population_precision": 0.989,
            "general_population_recall": 0.999,
            "general_population_accuracy": 0.990,
            "technical_domain_accuracy_range": "upper-80s to mid-90s (%)",
            "technical_domain_precision_max": 0.857,
            "technical_domain_recall_max": 1.0,
            "note": "no out-of-domain sensitivity figure is published in this source; do not compare our out-of-domain se/sp to a 'mid-80s' NORC number",
            "source": "https://www.norc.org/content/dam/norc-org/pdf2025/AAPOR%20Detecting%20AI-Generated%20Survey%20Responses%20-%20Lilian%20Huang.pdf",
        },
    }

    OUT_PATH.write_text(json.dumps(results, indent=2))
    print(f"Wrote {OUT_PATH}", file=sys.stderr)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
