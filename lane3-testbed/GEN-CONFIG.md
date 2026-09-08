# Counterpart generation config (SPEC 2.3)

Frozen parameters for the ~15k-generation LLM counterpart batch. Any change to
a value on this page invalidates a generation run already done under the old
value — bump the `config_version` and re-freeze rather than editing in place
once real generation has started.

```
config_version: 1
rng_seed: 20260907          # same seed used throughout lane 3 (calibration, essays sampling)
temperature: 0.7
top_p: 1.0
max_tokens: 600              # essay-length response, generous headroom over the ~200-400 word source essays
```

Per-call seeding: `seed = rng_seed_base + stable_hash(essay_id, family, coupling_level)`, deterministic and reproducible from `essay_id` alone — no run-to-run randomness in which seed a given (essay, family, coupling) cell gets. Anthropic's API does not currently expose a `seed` parameter (unlike OpenAI-compatible APIs) — `temperature` is set low-ish (0.7, not 0/1) as the closest available control; the `seed` value is still recorded per record for provenance and for the open-weight family, where the provider's OpenAI-compatible endpoint does accept it.

## Model families

| family | model | provider | notes |
|---|---|---|---|
| frontier proprietary | `claude-sonnet-5` (fallback `claude-sonnet-4-5` if unavailable) | Anthropic API, direct | Sonnet-class per the approved burn report |
| open-weight | `meta-llama/Llama-3.3-70B-Instruct` (placeholder pending provider selection) | API-served, cheap provider (OpenRouter/Together/Fireworks — whichever has the model and lowest per-token cost at fire time) | provider chosen at fire time by cost, not frozen here; the model family and instruct-tuning tier is what's frozen |

## Coupling levels

- **c = 0** (no coupling): prompt is the essay-writing prompt only ("Write a stream-of-consciousness reflection on your day/life/thoughts, roughly N words"), no persona or trait information given to the model at all.
- **c = partial** (coarse persona sketch): prompt + a coarse trait-band sketch in prose, not exact scores — e.g. "You tend to be somewhat more [reserved/outgoing] and somewhat more [organized/spontaneous] than average." Built from the same binary labels as c-high (see blocker below), phrased as tendencies rather than as a stated fact.
- **c = high** (actual trait scores): prompt + the respondent's actual trait information stated directly, as data rather than tendency-language.

### c-high blocker: local data is binary, not continuous

**What SPEC 2.3 wants for c-high**: the model conditioned on the respondent's actual (continuous) Big Five scores.

**What the local essays data actually has**: `data/essays/essays.csv` carries only binary, median-split labels per trait (`cEXT`/`cNEU`/`cAGR`/`cCON`/`cOPN`, each `y`/`n` — see `TESTBED-REPORT.md` Day 1 and `CALIBRATION-REPORT.md` Day 2). The continuous BFI scores live on the IEEE DataPort original (`https://doi.org/10.21227/dyfp-7f45`), which is login-gated — getting that account is Abhay's call, not something to script around. No score has been invented to fill this gap.

**What c-high concretely is with local data**: the five binary labels stated as facts, e.g. "Your five-factor profile: Extraversion — above the sample median. Neuroticism — below the sample median. Agreeableness — above the sample median. Conscientiousness — below the sample median. Openness — above the sample median." This is real data (each respondent's actual median-split position), just binary rather than a continuous score.

**Consequence — c-partial and c-high are less differentiated than SPEC intends**: SPEC's design contrasts "coarse band, not exact score" (partial) against "exact score" (high) as two different information resolutions. With only binary labels available, there is no continuous score to give at c-high — both conditions are built from the same 5 binary flags, differing only in *how* that binary information is phrased (tendency language at partial vs. stated-as-fact at high), not in *information content*. This is a real weakening of the c-partial vs. c-high contrast for this batch. If lane 1's derivation needs the two conditions to differ in information resolution (not just phrasing), that requires the continuous BFI scores — flagging as a Day 3+ item, same as the r_F anchor's lower-bound caveat in `CALIBRATION-REPORT.md`.

## Output layout

One JSONL file per (family, coupling) cell, 6 files total:

```
data/generated/frontier_c0.jsonl
data/generated/frontier_partial.jsonl
data/generated/frontier_high.jsonl
data/generated/openweight_c0.jsonl
data/generated/openweight_partial.jsonl
data/generated/openweight_high.jsonl
```

One JSON object per line:

```json
{
  "essay_id": "<row index/id from essays.csv>",
  "prompt_hash": "<sha256 of the exact prompt text sent>",
  "family": "frontier | openweight",
  "coupling_level": "c0 | partial | high",
  "model": "<exact model string used>",
  "seed": 123456789,
  "temperature": 0.7,
  "max_tokens": 600,
  "response": "<generated text>",
  "usage": {"input_tokens": 0, "output_tokens": 0},
  "timestamp_utc": "2026-09-07T21:00:00Z"
}
```

## API keys

Read only from environment variables — `ANTHROPIC_API_KEY` for the frontier family, `OPENWEIGHT_API_KEY` (provider-agnostic name; script also checks `OPENROUTER_API_KEY`/`TOGETHER_API_KEY`/`FIREWORKS_API_KEY`/`GROQ_API_KEY` as fallbacks) for the open-weight family. Never printed, never written to the repo. If either is missing, `generate_counterparts.py` stops immediately and reports which one.

**Status as of this staging pass (2026-09-07 16:22 CDT)**: neither key is present on this machine (checked `env` and `~/.config`) — see `GEN-DRYRUN.md` for the blocked-run report. The dry run has not been executed.
