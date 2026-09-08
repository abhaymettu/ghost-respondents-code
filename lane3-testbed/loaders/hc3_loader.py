"""Loader for the HC3 (Hello-SimpleAI/HC3) human-vs-ChatGPT comparison corpus.

Source: https://huggingface.co/datasets/Hello-SimpleAI/HC3
Files expected under lane3-testbed/data/hc3/: all.jsonl plus the five
per-source files (finance, medicine, open_qa, reddit_eli5, wiki_csai).
License: CC-BY-SA-4.0 (per dataset card), with the caveat that any source
dataset with a stricter license overrides CC-BY-SA for that subset.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "hc3"

SOURCES = ["finance", "medicine", "open_qa", "reddit_eli5", "wiki_csai"]


def load_all(path: Path = DATA_DIR / "all.jsonl"):
    """Yield one dict per question: question, human_answers, chatgpt_answers, source."""
    with open(path, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            yield {
                "question": rec["question"],
                "human_answers": rec["human_answers"],
                "chatgpt_answers": rec["chatgpt_answers"],
                "source": rec.get("source"),
                "index": rec.get("index"),
            }


def load_source(source: str, data_dir: Path = DATA_DIR):
    """Load one per-source jsonl file (finance/medicine/open_qa/reddit_eli5/wiki_csai)."""
    if source not in SOURCES:
        raise ValueError(f"unknown source {source!r}, expected one of {SOURCES}")
    path = data_dir / f"{source}.jsonl"
    with open(path, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            rec["source"] = source
            yield rec


def summarize(data_dir: Path = DATA_DIR) -> dict:
    """Record counts per source, from both all.jsonl and the per-source files."""
    all_counts = {}
    for rec in load_all(data_dir / "all.jsonl"):
        src = rec["source"]
        all_counts[src] = all_counts.get(src, 0) + 1

    per_file_counts = {}
    for source in SOURCES:
        per_file_counts[source] = sum(1 for _ in load_source(source, data_dir))

    return {
        "total_in_all_jsonl": sum(all_counts.values()),
        "per_source_from_all_jsonl": all_counts,
        "per_source_from_individual_files": per_file_counts,
    }


if __name__ == "__main__":
    summary = summarize()
    print(json.dumps(summary, indent=2))
