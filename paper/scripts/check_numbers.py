"""Self-check: does every number the draft quotes trace to paper/tables/numbers.json?

Two passes.
1. For each key in numbers.json, render the value the way the draft would print it (several
   candidate formats) and report keys whose value appears nowhere in the draft. That list is
   informational: many keys are intermediate.
2. Extract every numeric token from the draft prose and tables and report those that match no
   rendering of any numbers.json value, no table cell in paper/tables/*.md, and none of the
   whitelisted document-sourced constants below. Every survivor is either an unsourced number
   or a number quoted from a lane document (which the draft must attribute).

Run:  lane4-simulation/.venv/bin/python paper/scripts/check_numbers.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DRAFT = (ROOT / "paper" / "GHOST-RESPONDENTS-DRAFT.md").read_text()
NUM = json.loads((ROOT / "paper" / "tables" / "numbers.json").read_text())
TABLE_TEXT = "\n".join(p.read_text() for p in (ROOT / "paper" / "tables").glob("*.md"))

# Numbers the draft quotes from lane documents rather than from the grids, with their source.
DOC_SOURCED = {
    "1116": "pass2-numerical-check.md sec 9", "4092": "pass2 sec 9", "4.4e-16": "pass2 sec 9", "142": "pass2 sec 9",
    "4.081": "pass2 sec 1.3 z*", "2.6": "LAYERB-GRID.md sec 6 (estimand shrink)",
    "0.379": "pool_measurements gpt-4/EXT c_pool", "0.798": "kappa gpt-4/EXT", "0.534": "delta gpt-4/EXT", "1.862": "g gpt-4/EXT",
    "0.194": "c_pool llama-2/EXT", "0.537": "kappa llama-2", "0.264": "delta llama-2", "0.780": "g llama-2",
    "0.895": "LAYERB-PILOT closed form p=0", "1.135": "LAYERB-PILOT closed form p=1", "0.868": "LAYERB-PILOT MC p=0", "1.138": "LAYERB-PILOT MC p=1", "400": "LAYERB-PILOT reps",
    "1.79": "CHUNK-REFIT validity ratio min", "4.33": "CHUNK-REFIT validity ratio max",
    "2,467": "TESTBED-REPORT essay count", "256": "MiniLM token window", "320": "PersonaLLM pool size",
    "34": "SMR self-reported prevalence (lane 2 memo)", "0.0075": "PASS3-FIXES T7d Big5 sensitivity",
    "9.9": "PASS3-FIXES T4 kappa inflation low", "18.1": "PASS3-FIXES T4 kappa inflation high",
    "0.10": "grid pi level / r_F column", "0.23": "PASS3 T3 NEU document-pooled", "0.22": "PASS3 T3 OPE prefix", "0.31": "PASS3 T3 OPE document-pooled",
    "10,844": "LAYERB-GRID run seconds", "44,629": "LAYERB-GRID sec 7 run seconds", "42,950": "pass2 10.10 run seconds", "48,763": "GRID-PROGRESS core-seconds",
    "20260907": "Layer A master seed", "20260909": "Layer B master seed", "176": "in-sample partial run cells", "50": "LAYERB-GRID sec 7 recorded fields",
    "0.458": "sqrt(0.2096), computed in prose", "0.073": "CALIBRATION-REPORT sec 2 max proxy r", "2.24": "sqrt(5), theory MCSE ratio",
    "3.12.13": "python", "2.5.3": "numpy", "1.18.1": "scipy", "1.9.0": "sklearn",
    "2301.07597": "arXiv", "2604.11581": "arXiv", "2305.02547": "arXiv", "2608.26710": "arXiv", "2510.07175": "arXiv", "2511.21140": "arXiv",
    "2026": "year", "2025": "year", "2024": "year", "2023": "year", "1999": "year", "2.2": "SPEC section", "1.5": "SPEC section",
    "0.7": "rel_H", "0.5": "rho_T / p / kappa level", "0.95": "Layer A calibrated se", "0.99": "sp", "0.85": "sp", "0.3": "r_F Layer A", "0.2": "kappa", "1.0": "kappa/p",
    "0.4": "c level", "0.9": "c level", "0.20": "pi level", "0.30": "pi level", "0.01": "pi level", "0.02": "pi level", "0.05": "pi level",
    "500": "n / reps", "1000": "n", "2400": "n", "5000": "n", "100": "reps", "60": "n_bins", "8": "n_bins", "4": "k", "20": "simex B", "10": "em n_init", "2": "T3 bar pts",
    "10.10": "addendum section", "4.4": "SPEC section", "4.3": "SPEC section", "4.1": "SPEC section", "4.2": "SPEC section", "3.1": "SPEC section", "3.2": "SPEC section", "3.3": "SPEC section",
    "7d": "PASS3 item", "7a": "INJECT section", "7c": "INJECT section", "0.0": "p level", "1.5": "lambda", "0.5": "lambda",
    "12": "resolvability pp shift / rho_v cells", "216": "core cells", "144": "kappa arm", "72": "cells", "48": "trait arm cells", "180": "slice core", "40": "slice trait",
    "336": "cells", "372": "cells", "280": "cells", "210": "Layer A T1 cells", "228": "Layer A n=1000 cells", "102": "Layer A calibrated cells", "90": "Layer A degraded cells",
    "96": "cells per detector", "192": "n=1000 cells", "160": "slice n=1000 / cal+deg cells",
}

RENDERERS = [
    lambda v: f"{v:.4f}", lambda v: f"{v:.3f}", lambda v: f"{v:.2f}", lambda v: f"{v:.5f}",
    lambda v: f"{v:+.4f}", lambda v: f"{100 * v:.0f}%", lambda v: f"{100 * v:+.0f}%", lambda v: f"{100 * v:.1f}%",
    lambda v: f"{100 * v:.2f}%", lambda v: f"{v:.1f}", lambda v: str(int(v)) if float(v).is_integer() else None,
    lambda v: f"{v:.0f}", lambda v: f"{100 * v:.0f}",
]


def renderings(v):
    out = set()
    if isinstance(v, bool) or v is None:
        return out
    if isinstance(v, (int, float)):
        for r in RENDERERS:
            try:
                s = r(v)
            except Exception:
                s = None
            if s:
                out.add(s)
    elif isinstance(v, str):
        out.add(v)
    elif isinstance(v, list):
        for x in v:
            out |= renderings(x)
    elif isinstance(v, dict):
        for x in v.values():
            out |= renderings(x)
    return out


# pass 1: keys whose value never appears
missing_keys = [k for k, v in NUM.items() if not any(s in DRAFT for s in renderings(v))]
print(f"pass 1: {len(NUM) - len(missing_keys)} of {len(NUM)} numbers.json keys appear in the draft in some rendering")

# pass 2: every numeric token in the draft
all_renders = set()
for v in NUM.values():
    all_renders |= renderings(v)
table_tokens = set(re.findall(r"[+-]?\d[\d,]*\.?\d*", TABLE_TEXT))
tokens = re.findall(r"[+-]?\d[\d,]*(?:\.\d+)?(?:e-?\d+)?%?", DRAFT)
unsourced = {}
for t in tokens:
    core = t.lstrip("+").rstrip("%")
    if core in DOC_SOURCED or t in DOC_SOURCED:
        continue
    if t in all_renders or core in all_renders or t.lstrip("+") in all_renders:
        continue
    if core in table_tokens or t in table_tokens:
        continue
    if re.fullmatch(r"\d{1,2}", core):  # small integers: section numbers, list numbers, counts in tables
        continue
    unsourced[t] = unsourced.get(t, 0) + 1

print(f"pass 2: {len(unsourced)} distinct numeric tokens in the draft match no artifact rendering and no whitelisted document number:")
for t, n in sorted(unsourced.items(), key=lambda kv: -kv[1]):
    # show one context
    i = DRAFT.find(t)
    ctx = DRAFT[max(0, i - 50): i + len(t) + 40].replace("\n", " ")
    print(f"  {t!r} x{n}: ...{ctx}...")
