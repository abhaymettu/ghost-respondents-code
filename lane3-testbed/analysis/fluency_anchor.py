"""Day 2 part 2: empirical anchor for r_F (fluency-trait correlation),
for lane 1's Q6 deletion-selection derivation (SPEC 1.5): detectors flag
low-fluency human writing at higher rates, and if fluency correlates with
the trait being measured, conditioning on "detector passes" is a
collider -- selection on theta. r_F is the magnitude of that fluency-trait
correlation; this script gives an empirical estimate from real text.

CONSTRAINT: the local essays mirror (data/essays/essays.csv, see
TESTBED-REPORT.md) has only binary, median-split Big Five labels
(cEXT/cNEU/cAGR/cCON/cOPN), not continuous BFI scores. Continuous scores
are on the IEEE DataPort original, which is login-gated -- getting an
account is Abhay's call, not something scripted around here. So every
correlation below is a POINT-BISERIAL correlation (continuous fluency
proxy vs. binary trait label), computed on exactly the labels the local
data has. Median-split dichotomization is known to attenuate a true
continuous correlation (Cohen 1983) -- so |r_F| here is a lower bound on
the true fluency-trait correlation, not an unbiased estimate of it.

Fluency proxies (no continuous BFI, so no readability formula calibrated
against reading level -- these are surface fluency/disfluency signals
appropriate to stream-of-consciousness essays):
  - avg_word_len, type_token_ratio, avg_sentence_len_words,
    punct_per_100_words  (from detector/features.py)
  - filler_per_100_words: rate of disfluency markers (um, uh, like,
    you know, i mean, sort of, kind of) -- a direct fluency signal in
    unedited stream-of-consciousness text.
  - composite_fluency: mean of z-scored (ttr, avg_sentence_len_words,
    -filler_per_100_words) -- higher = more fluent. One combined proxy
    alongside the individual features, not a replacement for them.

Run: python3 analysis/fluency_anchor.py
Writes analysis/fluency_r_f_results.json.
"""

import json
import re
import sys
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from loaders.essays_loader import load as load_essays, TRAIT_COLUMNS  # noqa: E402
from detector.features import feature_dict  # noqa: E402

OUT_PATH = Path(__file__).resolve().parent / "fluency_r_f_results.json"

FILLER_RE = re.compile(
    r"\b(um+|uh+|like|you know|i mean|sort of|kind of|kinda|basically|actually|literally)\b",
    re.IGNORECASE,
)


def fluency_features(text: str) -> dict:
    d = feature_dict(text)
    n_words = max(d["n_words"], 1)
    filler_count = len(FILLER_RE.findall(text))
    d["filler_per_100_words"] = 100 * filler_count / n_words
    return d


def point_biserial(continuous: np.ndarray, binary: np.ndarray):
    r, p = stats.pointbiserialr(binary, continuous)
    return float(r), float(p)


def main():
    essays = list(load_essays())
    print(f"Loaded {len(essays)} essays", file=sys.stderr)

    feature_names = [
        "avg_word_len",
        "type_token_ratio",
        "avg_sentence_len_words",
        "punct_per_100_words",
        "filler_per_100_words",
    ]

    feats = {name: [] for name in feature_names}
    traits = {t: [] for t in TRAIT_COLUMNS}
    skipped = 0

    for rec in essays:
        d = fluency_features(rec["text"])
        row_traits = {}
        ok = True
        for t in TRAIT_COLUMNS:
            v = rec["traits"][t].strip().lower()
            if v not in ("y", "n"):
                ok = False
                break
            row_traits[t] = 1 if v == "y" else 0
        if not ok:
            skipped += 1
            continue
        for name in feature_names:
            feats[name].append(d[name])
        for t in TRAIT_COLUMNS:
            traits[t].append(row_traits[t])

    n = len(next(iter(feats.values())))
    print(f"Usable rows: {n} (skipped {skipped})", file=sys.stderr)

    arrs = {name: np.array(v, dtype=float) for name, v in feats.items()}
    trait_arrs = {t: np.array(v, dtype=int) for t, v in traits.items()}

    # composite fluency: z(ttr) + z(avg_sentence_len_words) - z(filler_per_100_words)
    def z(a):
        return (a - a.mean()) / a.std(ddof=0)

    composite = (z(arrs["type_token_ratio"]) + z(arrs["avg_sentence_len_words"]) - z(arrs["filler_per_100_words"])) / 3
    arrs["composite_fluency"] = composite

    results = {"n_essays_used": n, "n_skipped_missing_label": skipped, "correlations": {}}
    for fname, fvals in arrs.items():
        results["correlations"][fname] = {}
        for t in TRAIT_COLUMNS:
            r, p = point_biserial(fvals, trait_arrs[t])
            results["correlations"][fname][t] = {"r": round(r, 4), "p": round(p, 5)}

    # headline r_F: |r| of composite_fluency vs each trait, max across traits
    composite_rs = {t: results["correlations"]["composite_fluency"][t]["r"] for t in TRAIT_COLUMNS}
    max_trait = max(composite_rs, key=lambda t: abs(composite_rs[t]))
    results["headline_r_F"] = {
        "definition": "|point-biserial r| between composite_fluency and the binary trait label with the largest magnitude",
        "max_abs_trait": max_trait,
        "r": composite_rs[max_trait],
        "all_composite_r": composite_rs,
        "caveat": "lower bound on the true continuous r_F: binary median-split traits attenuate correlation magnitude vs. continuous BFI scores (blocked behind IEEE DataPort login)",
    }

    OUT_PATH.write_text(json.dumps(results, indent=2))
    print(f"Wrote {OUT_PATH}", file=sys.stderr)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
