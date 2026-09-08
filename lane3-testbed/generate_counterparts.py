"""SPEC 2.3: LLM counterpart generation for the essays testbed.

Frozen parameters live in GEN-CONFIG.md -- this script must match that file;
if you change a constant here, update GEN-CONFIG.md in the same commit.

Two model families x three coupling levels = 6 cells:
  families: frontier (Anthropic API, Sonnet-class), openweight (API-served
            open-weight model via an OpenAI-compatible endpoint)
  coupling: c0 (prompt only), partial (coarse trait-band sketch),
            high (actual trait labels stated as fact)

c-high caveat: local essays data has binary median-split trait labels only,
not continuous BFI scores (IEEE DataPort login-gated, Abhay's call -- see
GEN-CONFIG.md). c-high here is those binary labels stated as fact; no score
is invented.

Modes:
  --dry-run          10 generations per cell (60 total), writes GEN-DRYRUN.md
                      with measured tokens, cost extrapolation to the full
                      14,874-generation batch, and response snippets for a
                      quality eyeball. Safe, cheap (<$1), does not touch the
                      real output files.
  --fire             Runs the full batch (14,874 generations) against every
                      essay in essays.csv. NOT invoked by staging -- only run
                      on explicit go after the dry-run cost check and
                      Abhay's no-objection window.

API keys are read from environment only, never printed, never written
anywhere. Missing key -> stop immediately and report which family is
blocked; no partial/mixed run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from loaders.essays_loader import load as load_essays, TRAIT_COLUMNS  # noqa: E402

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "data" / "generated"
DRYRUN_REPORT = ROOT / "GEN-DRYRUN.md"

CONFIG_VERSION = 1
RNG_SEED_BASE = 20260907
TEMPERATURE = 0.7
TOP_P = 1.0
MAX_TOKENS = 600

FRONTIER_MODEL = "claude-sonnet-5"
FRONTIER_MODEL_FALLBACK = "claude-sonnet-4-5"
OPENWEIGHT_MODEL = "meta-llama/Llama-3.3-70B-Instruct"

COUPLING_LEVELS = ["c0", "partial", "high"]
FAMILIES = ["frontier", "openweight"]

# Rough per-1M-token pricing for extrapolation only (documented estimates,
# not billing-accurate -- update if provider/model choice changes).
PRICE_PER_1M_TOKENS = {
    "frontier": {"input": 3.00, "output": 15.00},   # Sonnet-class list price
    "openweight": {"input": 0.35, "output": 0.40},  # cheap-provider Llama-3.3-70B ballpark
}

FULL_BATCH_TOTAL = 14874  # from the approved burn report

GENERATION_PROMPT = (
    "Write a stream-of-consciousness reflection, roughly 200-400 words. "
    "Write whatever comes to mind -- don't plan it out, don't edit, just keep "
    "writing continuously as your thoughts occur to you."
)

TRAIT_NAMES = {
    "cEXT": "Extraversion",
    "cNEU": "Neuroticism",
    "cAGR": "Agreeableness",
    "cCON": "Conscientiousness",
    "cOPN": "Openness",
}


def stable_seed(essay_id: str, family: str, coupling_level: str) -> int:
    h = hashlib.sha256(f"{essay_id}|{family}|{coupling_level}".encode()).hexdigest()
    return RNG_SEED_BASE + (int(h[:8], 16) % 1_000_000)


def prompt_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _label(v: str) -> str:
    return "y" if v.strip().lower() == "y" else "n"


def build_persona_partial(traits: dict) -> str:
    bits = []
    for col, name in TRAIT_NAMES.items():
        high = _label(traits[col]) == "y"
        bits.append(f"somewhat more {name.lower()}-leaning" if high else f"somewhat less {name.lower()}-leaning")
    return (
        "For context, you tend to be " + "; ".join(bits) + " than average, relative to other people. "
        "Let that come through naturally in how you write, without stating it directly."
    )


def build_persona_high(traits: dict) -> str:
    bits = []
    for col, name in TRAIT_NAMES.items():
        high = _label(traits[col]) == "y"
        bits.append(f"{name}: above the sample median" if high else f"{name}: below the sample median")
    return "Your five-factor profile: " + "; ".join(bits) + ". Let that come through naturally in how you write."


def build_prompt(coupling_level: str, traits: dict) -> str:
    if coupling_level == "c0":
        return GENERATION_PROMPT
    if coupling_level == "partial":
        return GENERATION_PROMPT + "\n\n" + build_persona_partial(traits)
    if coupling_level == "high":
        return GENERATION_PROMPT + "\n\n" + build_persona_high(traits)
    raise ValueError(coupling_level)


def get_frontier_key() -> str | None:
    return os.environ.get("ANTHROPIC_API_KEY")


def get_openweight_key() -> tuple[str | None, str | None]:
    """Returns (key, provider_env_name) -- first of the fallback provider vars found."""
    for name in ("OPENWEIGHT_API_KEY", "OPENROUTER_API_KEY", "TOGETHER_API_KEY", "FIREWORKS_API_KEY", "GROQ_API_KEY"):
        v = os.environ.get(name)
        if v:
            return v, name
    return None, None


def call_frontier(prompt: str, api_key: str) -> dict:
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": FRONTIER_MODEL,
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    text = "".join(block.get("text", "") for block in data.get("content", []))
    usage = data.get("usage", {})
    return {
        "text": text,
        "model": data.get("model", FRONTIER_MODEL),
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
    }


def call_openweight(prompt: str, api_key: str, base_url: str, seed: int) -> dict:
    resp = requests.post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "content-type": "application/json"},
        json={
            "model": OPENWEIGHT_MODEL,
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "seed": seed,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    choice = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    return {
        "text": choice,
        "model": data.get("model", OPENWEIGHT_MODEL),
        "input_tokens": usage.get("prompt_tokens", 0),
        "output_tokens": usage.get("completion_tokens", 0),
    }


# Default OpenAI-compatible base URL per provider env var found.
OPENWEIGHT_BASE_URLS = {
    "OPENROUTER_API_KEY": "https://openrouter.ai/api/v1",
    "TOGETHER_API_KEY": "https://api.together.xyz/v1",
    "FIREWORKS_API_KEY": "https://api.fireworks.ai/inference/v1",
    "GROQ_API_KEY": "https://api.groq.com/openai/v1",
    "OPENWEIGHT_API_KEY": None,  # must be paired with OPENWEIGHT_BASE_URL env var
}


def generate_one(essay_id: str, traits: dict, family: str, coupling_level: str, frontier_key, openweight_key, openweight_base) -> dict:
    prompt = build_prompt(coupling_level, traits)
    seed = stable_seed(essay_id, family, coupling_level)
    t0 = time.time()
    if family == "frontier":
        result = call_frontier(prompt, frontier_key)
    else:
        result = call_openweight(prompt, openweight_key, openweight_base, seed)
    elapsed = time.time() - t0
    return {
        "essay_id": essay_id,
        "prompt_hash": prompt_hash(prompt),
        "family": family,
        "coupling_level": coupling_level,
        "model": result["model"],
        "seed": seed,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "response": result["text"],
        "usage": {"input_tokens": result["input_tokens"], "output_tokens": result["output_tokens"]},
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_s": round(elapsed, 2),
    }


def check_keys() -> tuple[str | None, str | None, str | None]:
    """Returns (frontier_key, openweight_key, openweight_base) or raises SystemExit
    with a report of exactly which key is missing."""
    frontier_key = get_frontier_key()
    openweight_key, openweight_env_name = get_openweight_key()

    missing = []
    if not frontier_key:
        missing.append("frontier: ANTHROPIC_API_KEY not set")
    if not openweight_key:
        missing.append("openweight: none of OPENWEIGHT_API_KEY/OPENROUTER_API_KEY/TOGETHER_API_KEY/FIREWORKS_API_KEY/GROQ_API_KEY set")

    if missing:
        print("GEN-BLOCKED: missing API key(s):", file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        raise SystemExit(1)

    if openweight_env_name == "OPENWEIGHT_API_KEY":
        openweight_base = os.environ.get("OPENWEIGHT_BASE_URL")
        if not openweight_base:
            print("GEN-BLOCKED: OPENWEIGHT_API_KEY set but OPENWEIGHT_BASE_URL not set (needed for a custom provider)", file=sys.stderr)
            raise SystemExit(1)
    else:
        openweight_base = OPENWEIGHT_BASE_URLS[openweight_env_name]

    return frontier_key, openweight_key, openweight_base


def run_dry_run(n_per_cell: int = 10):
    frontier_key, openweight_key, openweight_base = check_keys()

    essays = list(load_essays())
    sample = essays[: max(n_per_cell, 1) * 3]  # enough distinct essays to avoid repeats across coupling levels

    records = []
    for family in FAMILIES:
        for coupling in COUPLING_LEVELS:
            cell_essays = sample[:n_per_cell]
            for rec in cell_essays:
                traits = {c: rec["traits"][c] for c in TRAIT_COLUMNS}
                out = generate_one(
                    essay_id=str(rec["author_id"]),
                    traits=traits,
                    family=family,
                    coupling_level=coupling,
                    frontier_key=frontier_key,
                    openweight_key=openweight_key,
                    openweight_base=openweight_base,
                )
                records.append(out)
                print(f"  {family}/{coupling} essay={out['essay_id']} in={out['usage']['input_tokens']} out={out['usage']['output_tokens']} ({out['elapsed_s']}s)", file=sys.stderr)

    write_dryrun_report(records, n_per_cell)


def write_dryrun_report(records: list[dict], n_per_cell: int):
    by_family = {f: [r for r in records if r["family"] == f] for f in FAMILIES}

    lines = ["# Counterpart generation dry run", "", f"Cells: {len(FAMILIES)} families x {len(COUPLING_LEVELS)} coupling levels, {n_per_cell} generations each = {len(records)} total.", ""]

    total_cost = 0.0
    lines.append("## Measured tokens and cost extrapolation")
    lines.append("")
    lines.append("| family | n | avg tokens in | avg tokens out | dry-run cost | extrapolated cost (14,874 total, split evenly) |")
    lines.append("|---|---|---|---|---|---|")
    for family in FAMILIES:
        recs = by_family[family]
        if not recs:
            continue
        avg_in = sum(r["usage"]["input_tokens"] for r in recs) / len(recs)
        avg_out = sum(r["usage"]["output_tokens"] for r in recs) / len(recs)
        price = PRICE_PER_1M_TOKENS[family]
        dry_cost = sum(
            (r["usage"]["input_tokens"] / 1e6) * price["input"] + (r["usage"]["output_tokens"] / 1e6) * price["output"]
            for r in recs
        )
        family_share = FULL_BATCH_TOTAL / len(FAMILIES)
        extrap_cost = (avg_in / 1e6) * price["input"] * family_share + (avg_out / 1e6) * price["output"] * family_share
        total_cost += extrap_cost
        lines.append(
            f"| {family} | {len(recs)} | {avg_in:.0f} | {avg_out:.0f} | ${dry_cost:.4f} | ${extrap_cost:.2f} |"
        )
    lines.append("")
    lines.append(f"**Extrapolated full-batch cost: ${total_cost:.2f}** (burn report estimate: Sonnet-class ~$105, open-weight <$10, ~14,874 generations total).")
    lines.append("")

    lines.append("## Quality eyeball notes (response snippets, first 200 chars)")
    lines.append("")
    for r in records:
        snippet = r["response"][:200].replace("\n", " ")
        lines.append(f"- **{r['family']}/{r['coupling_level']}** essay={r['essay_id']}: {snippet}...")
    lines.append("")
    lines.append("_Manual eyeball: read a handful above per cell and confirm responses are on-topic, non-degenerate, and (for partial/high) show a plausible trait lean without literally repeating the label sentence back. Fill in a one-line verdict per cell before firing the full batch._")

    DRYRUN_REPORT.write_text("\n".join(lines))
    print(f"Wrote {DRYRUN_REPORT}", file=sys.stderr)


def run_full_batch():
    frontier_key, openweight_key, openweight_base = check_keys()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    essays = list(load_essays())

    writers = {}
    for family in FAMILIES:
        for coupling in COUPLING_LEVELS:
            path = OUT_DIR / f"{family}_{coupling}.jsonl"
            writers[(family, coupling)] = open(path, "a", encoding="utf-8")

    try:
        for rec in essays:
            traits = {c: rec["traits"][c] for c in TRAIT_COLUMNS}
            for family in FAMILIES:
                for coupling in COUPLING_LEVELS:
                    out = generate_one(
                        essay_id=str(rec["author_id"]),
                        traits=traits,
                        family=family,
                        coupling_level=coupling,
                        frontier_key=frontier_key,
                        openweight_key=openweight_key,
                        openweight_base=openweight_base,
                    )
                    writers[(family, coupling)].write(json.dumps(out) + "\n")
                    writers[(family, coupling)].flush()
    finally:
        for w in writers.values():
            w.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--n-per-cell", type=int, default=10)
    parser.add_argument("--fire", action="store_true", help="Run the full ~14,874-generation batch. Only on explicit go.")
    args = parser.parse_args()

    if args.fire:
        run_full_batch()
    elif args.dry_run:
        run_dry_run(args.n_per_cell)
    else:
        parser.print_help()
        print("\nNo mode selected. Use --dry-run to stage-check, or --fire to run the full batch (explicit go only).", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
