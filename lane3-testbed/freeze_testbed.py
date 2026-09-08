"""Day 2 part 4: freeze the testbed. Writes testbed_freeze.json --
verified counts, license notes, detector operating points, and SHA-256
fingerprints of every data file lane 4 should code against. Re-run this
any time a data file changes; a changed hash means lane 4's cached
results are stale.
"""

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from loaders.hc3_loader import summarize as hc3_summarize  # noqa: E402
from loaders.essays_loader import summarize as essays_summarize  # noqa: E402

ROOT = Path(__file__).resolve().parent
OUT_PATH = ROOT / "testbed_freeze.json"

FILES_TO_HASH = [
    "data/hc3/all.jsonl",
    "data/hc3/finance.jsonl",
    "data/hc3/medicine.jsonl",
    "data/hc3/open_qa.jsonl",
    "data/hc3/reddit_eli5.jsonl",
    "data/hc3/wiki_csai.jsonl",
    "data/essays/essays.csv",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    fingerprints = {}
    for rel in FILES_TO_HASH:
        p = ROOT / rel
        fingerprints[rel] = {
            "sha256": sha256_file(p),
            "bytes": p.stat().st_size,
        }

    calibration_path = ROOT / "detector" / "calibration_results.json"
    calibration = json.loads(calibration_path.read_text()) if calibration_path.exists() else None

    fluency_path = ROOT / "analysis" / "fluency_r_f_results.json"
    fluency = json.loads(fluency_path.read_text()) if fluency_path.exists() else None

    freeze = {
        "frozen_at_utc": "2026-09-07",
        "hc3": {
            "source": "https://huggingface.co/datasets/Hello-SimpleAI/HC3",
            "paper": "https://arxiv.org/abs/2301.07597",
            "license": "cc-by-sa-4.0 (per dataset card; source-dataset-specific stricter licenses override per the card's own caveat)",
            "counts": hc3_summarize(),
        },
        "essays": {
            "canonical_source": "https://doi.org/10.21227/dyfp-7f45 (IEEE DataPort, login-gated for download -- see TESTBED-REPORT.md)",
            "actual_source_used": "https://raw.githubusercontent.com/SenticNet/personality-detection/master/essays.csv",
            "license": "CC-BY-4.0 (per IEEE DataPort dataset card; the GitHub mirror does not restate a license)",
            "counts": essays_summarize(),
            "known_limitation": "binary median-split Big Five labels only, not continuous BFI scores (blocked on IEEE DataPort login, Abhay's call)",
        },
        "detector_calibration": calibration,
        "fluency_r_f_anchor": fluency,
        "fingerprints_sha256": fingerprints,
    }

    OUT_PATH.write_text(json.dumps(freeze, indent=2))
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
