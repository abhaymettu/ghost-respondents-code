"""Loader for the Pennebaker-King stream-of-consciousness essays dataset.

Original source: IEEE DataPort, https://doi.org/10.21227/dyfp-7f45
(Essays-Big5; license CC-BY-4.0 per the dataset landing page). That page
requires an IEEE DataPort login to actually download the files -- no
public/anonymous download link is exposed in the page HTML or its
schema.org JSON-LD (checked 2026-09-07). See TESTBED-REPORT.md.

Fallback actually used: the widely-mirrored essays.csv, fetched from
https://raw.githubusercontent.com/SenticNet/personality-detection/master/essays.csv
(public raw GitHub content, no login required). This is the standard
essays.csv used across the personality-detection literature: author id,
essay text, and five binary (median-split) Big Five trait labels.

File encoding is cp1252/latin-1, not UTF-8 (contains Windows smart-quote
bytes like 0x92).
"""

import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "essays"
CSV_PATH = DATA_DIR / "essays.csv"

TRAIT_COLUMNS = ["cEXT", "cNEU", "cAGR", "cCON", "cOPN"]


def load(path: Path = CSV_PATH):
    """Yield one dict per essay: author_id, text, and binary trait labels (0/1 as 'n'/'y')."""
    with open(path, encoding="cp1252", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield {
                "author_id": row["#AUTHID"],
                "text": row["TEXT"],
                "traits": {t: row[t] for t in TRAIT_COLUMNS},
            }


def summarize(path: Path = CSV_PATH) -> dict:
    n = 0
    total_words = 0
    trait_counts = {t: {"y": 0, "n": 0} for t in TRAIT_COLUMNS}
    for rec in load(path):
        n += 1
        total_words += len(rec["text"].split())
        for t in TRAIT_COLUMNS:
            val = rec["traits"][t].strip().lower()
            if val in trait_counts[t]:
                trait_counts[t][val] += 1

    return {
        "n_essays": n,
        "total_words_whitespace_split": total_words,
        "trait_label_counts": trait_counts,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(summarize(), indent=2))
