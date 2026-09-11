"""T3 (section 5.3): machine vs. human chunk-1 score distributions, core box (gpt-4/EXT).

Replaces an unsourced quote (LAYERB-GRID.md's -0.536/-0.242, SDs 0.92/1.03 do not reproduce
from any pool/trait/field in lane3-testbed/data/scores/*.json; see GAPS-CLOSURE-SPEC.md #1).
Uses chunk_1_oof, the field the grid's own era block documents as its score_version.

Run:  lane4-simulation/.venv/bin/python paper/scripts/t3_chunk1_dist.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SCORES = ROOT / "lane3-testbed" / "data" / "scores"
TRAIT = "cEXT"


def chunk1_oof(pool_file: str) -> np.ndarray:
    rows = json.loads((SCORES / pool_file).read_text())["chunk_1_oof"]
    return np.array([r[TRAIT] for r in rows if r is not None and r.get(TRAIT) is not None])


def main() -> None:
    machine = chunk1_oof("personallm_gpt-4-0613.json")
    human = chunk1_oof("pk_human.json")
    result = {
        "trait": TRAIT,
        "field": "chunk_1_oof",
        "machine_pool": "personallm_gpt-4-0613",
        "machine_n": int(machine.size),
        "machine_mean": float(machine.mean()),
        "machine_sd": float(machine.std(ddof=1)),
        "human_pool": "pk_human",
        "human_n": int(human.size),
        "human_mean": float(human.mean()),
        "human_sd": float(human.std(ddof=1)),
    }
    out = ROOT / "paper" / "tables" / "t3_chunk1_dist.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
