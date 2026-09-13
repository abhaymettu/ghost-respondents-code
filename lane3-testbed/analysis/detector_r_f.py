"""Direct r_F: the correlation between the detector's own score and the trait label.

`fluency_anchor.py` estimates r_F from surface fluency proxies (type-token ratio,
sentence length, filler rate). That is a stand-in. The quantity the deletion-selection
derivation actually needs is the correlation between the variable the detector thresholds
on and the trait, and that variable is on disk: `detector_p_machine` in
`data/scores/pk_human.json` is roberta-base-openai-detector's P(machine) for every
Pennebaker-King essay, and the pass/flag rule of section 2.3 is a threshold on it.

So this computes, for each of the five binary median-split labels, the point-biserial
correlation between the label and the detector score, plus Spearman rho as a
monotone-but-not-linear check (the score is heavily mass-concentrated near zero).

Same dichotomization caveat as fluency_anchor.py: median-split labels attenuate the
correlation against continuous BFI scores, so these magnitudes are a lower bound.

Run: python3 analysis/detector_r_f.py
Writes analysis/detector_r_f_results.json.
"""

import json
from pathlib import Path

import numpy as np
from scipy import stats

SCORES = Path(__file__).resolve().parent.parent / "data" / "scores" / "pk_human.json"
OUT_PATH = Path(__file__).resolve().parent / "detector_r_f_results.json"


def main() -> None:
    d = json.loads(SCORES.read_text())
    score = np.asarray(d["detector_p_machine"], dtype=float)
    out = {}
    for trait, labels in d["labels"].items():
        y = np.asarray(labels, dtype=float)
        r, p = stats.pointbiserialr(y, score)
        rho, p_rho = stats.spearmanr(y, score)
        out[trait] = {
            "r": round(float(r), 4), "p": round(float(p), 5),
            "spearman": round(float(rho), 4), "spearman_p": round(float(p_rho), 5),
        }
    max_pb = max(out, key=lambda t: abs(out[t]["r"]))
    max_sp = max(out, key=lambda t: abs(out[t]["spearman"]))
    results = {
        "source": "lane3-testbed/data/scores/pk_human.json::detector_p_machine",
        "detector": "roberta-base-openai-detector",
        "n_essays": int(score.size),
        "correlations": out,
        "headline_r_F": {
            "definition": "|point-biserial r| between the detector score P(machine) and the "
                          "binary trait label, largest magnitude over the five traits",
            "max_abs_trait": max_pb,
            "r": out[max_pb]["r"],
            "max_abs_spearman_trait": max_sp,
            "spearman": out[max_sp]["spearman"],
            "caveat": "lower bound: median-split labels attenuate against continuous BFI scores",
        },
    }
    OUT_PATH.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results["headline_r_F"], indent=2))
    for t, v in out.items():
        print(f"{t}: r={v['r']:+.4f} (p={v['p']}), spearman={v['spearman']:+.4f}")


if __name__ == "__main__":
    main()
