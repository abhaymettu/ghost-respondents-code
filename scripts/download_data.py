#!/usr/bin/env python3
"""Download the third-party corpora that lane3-testbed reads.

The corpora are not committed to this repository because they belong to other
authors and carry their own terms. This script fetches each one from its public
source into lane3-testbed/data/, which .gitignore keeps untracked.

Usage:
    python3 scripts/download_data.py            # everything
    python3 scripts/download_data.py essays hc3 # a subset

Sources and licence notes (details in lane3-testbed/TESTBED-REPORT.md and
lane3-testbed/CORPUS-AUDIT.md):

  essays     Pennebaker and King stream-of-consciousness essays with binary
             Big Five labels. Mirror: SenticNet/personality-detection
             essays.csv. The mirror states no licence; the canonical copy on
             IEEE DataPort (doi 10.21227/dyfp-7f45) is CC-BY-4.0 and needs a
             login, so the public mirror is used. About 8 MB.
  hc3        HC3 (Hello-SimpleAI/HC3 on Hugging Face, arXiv 2301.07597).
             CC-BY-SA-4.0, or stricter where a source dataset is stricter.
             About 150 MB.
  big5       Big5PersonalityEssays (stnflri/Big5PersonalityEssays),
             Brief-State-of-Consciousness-Essays.xlsx. CC BY 4.0 per the
             arXiv listing. Under 1 MB.
  personallm PersonaLLM generated and human stories (hjian42/PersonaLLM,
             text/ folder plus LICENSE). MIT licence. About 16 MB unpacked.

data/scores/ and data/models/ are derived outputs, not downloads. Regenerate
them with lane3-testbed/pool_measurement.py and
lane3-testbed/pk_human_detector_scores.py after downloading the corpora.

Uses only the Python standard library.
"""
import io
import shutil
import sys
import tarfile
import urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "lane3-testbed" / "data"

HC3_FILES = ["all.jsonl", "finance.jsonl", "medicine.jsonl", "open_qa.jsonl",
             "reddit_eli5.jsonl", "wiki_csai.jsonl"]


def fetch(url):
    print(f"  get {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "ghost-respondents-download"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def save(path, blob):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    print(f"  wrote {path.relative_to(DATA.parent.parent)} ({len(blob) / 1e6:.1f} MB)")


def essays():
    save(DATA / "essays" / "essays.csv",
         fetch("https://raw.githubusercontent.com/SenticNet/personality-detection/master/essays.csv"))


def hc3():
    base = "https://huggingface.co/datasets/Hello-SimpleAI/HC3/resolve/main/"
    for name in HC3_FILES:
        save(DATA / "hc3" / name, fetch(base + name))


def big5():
    save(DATA / "big5_personality_essays" / "essays.xlsx",
         fetch("https://raw.githubusercontent.com/stnflri/Big5PersonalityEssays/main/"
               "Brief-State-of-Consciousness-Essays.xlsx"))


def personallm():
    blob = fetch("https://codeload.github.com/hjian42/PersonaLLM/tar.gz/refs/heads/v2.0")
    dest = DATA / "personallm"
    if (dest / "text").exists():
        shutil.rmtree(dest / "text")
    n = 0
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tar:
        for m in tar.getmembers():
            parts = Path(m.name).parts
            if len(parts) < 2 or not m.isfile():
                continue
            rel = Path(*parts[1:])
            if rel.parts[0] == "text" or rel == Path("LICENSE"):
                out = (dest / rel).resolve()
                if dest.resolve() not in out.parents:
                    continue
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(tar.extractfile(m).read())
                n += 1
    print(f"  wrote {n} files under {dest.relative_to(DATA.parent.parent)}")


STEPS = {"essays": essays, "hc3": hc3, "big5": big5, "personallm": personallm}


def main(argv):
    names = argv or list(STEPS)
    unknown = [n for n in names if n not in STEPS]
    if unknown:
        sys.exit(f"unknown dataset: {', '.join(unknown)} (choose from {', '.join(STEPS)})")
    for n in names:
        print(n)
        STEPS[n]()


if __name__ == "__main__":
    main(sys.argv[1:])
