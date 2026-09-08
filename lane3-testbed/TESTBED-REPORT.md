# Lane 3 testbed report — Day 1

Scope: pull HC3 and the Pennebaker-King essays dataset, write loaders, verify counts/schema/license. No machine-text generation today (per SPEC 2.3, that's a later step).

## HC3 (Hello-SimpleAI/HC3)

- Source: https://huggingface.co/datasets/Hello-SimpleAI/HC3 (paper: arXiv 2301.07597)
- Downloaded via `huggingface_hub.hf_hub_download`, no login required, into `data/hc3/`: `all.jsonl`, `finance.jsonl`, `medicine.jsonl`, `open_qa.jsonl`, `reddit_eli5.jsonl`, `wiki_csai.jsonl`.
- License, from the dataset card (README.md front matter and body): `cc-by-sa-4.0`, with the card's stated caveat — "If the source datasets used in this corpus has a specific license which is stricter than CC-BY-SA, our products follow the same."

### Verified counts

`all.jsonl` has 24,322 records — matches the paper's "~24k questions" claim. Per-source breakdown (from both `all.jsonl`'s `source` field and the matching per-source files independently, counts agree exactly):

| source | count |
|---|---|
| reddit_eli5 | 17,112 |
| finance | 3,933 |
| medicine | 1,248 |
| open_qa | 1,187 |
| wiki_csai | 842 |
| **total** | **24,322** |

Note: the SPEC (2.1) names "open QA, Reddit ELI5, medicine, and finance" as the four sources; the actual dataset ships a fifth category, `wiki_csai` (842 records, CS/AI wiki questions), not mentioned in the SPEC. Included here for completeness — exclude it downstream if the SPEC's four-source scope is intentional.

### Schema

`all.jsonl` records: `question` (str), `human_answers` (list[str], usually 1 answer but sometimes more), `chatgpt_answers` (list[str]), `source` (str), `index` (int, present for `all`/`reddit_eli5`, absent elsewhere). Per-source files carry the same `question`/`human_answers`/`chatgpt_answers` fields without the `source` key (the loader injects it).

### Loader

`loaders/hc3_loader.py` — `load_all()`, `load_source(name)`, `summarize()`. Ran clean; output above reproduced by `python3 loaders/hc3_loader.py`.

## Pennebaker-King stream-of-consciousness essays

- SPEC target: 2,479 essays with BFI trait scores, ~1.9M words (Pennebaker & King 1999).
- **IEEE DataPort mirror (https://doi.org/10.21227/dyfp-7f45) — blocked.** The DOI resolves cleanly (no login needed to reach `https://ieee-dataport.org/documents/dataset-9`) and the page's schema.org JSON-LD confirms the dataset ("Essays-Big5 and Kaggle-MBTI datasets... over 2,000 personal essays annotated with Big Five personality traits") and its license (`CC-BY-4.0`). But there is no public download link or `contentUrl` anywhere in the static HTML or JSON-LD — the only actionable link found is `/saml_login?idp=IEEEDataport`, an IEEE SAML login. IEEE DataPort gates the actual file download behind an authenticated account even for CC-BY-licensed datasets. Stopped here per instructions rather than attempting to script around a login wall. A snapshot of the fetched page is at `data/essays/_pages/ieee_dataport.html` for reference.
- **Fallback used: the widely-mirrored `essays.csv`.** Fetched with no login from `https://raw.githubusercontent.com/SenticNet/personality-detection/master/essays.csv` (public raw GitHub content), saved to `data/essays/essays.csv`. This is the standard mirror used throughout the personality-detection ML literature (author id, essay text, five binary median-split Big Five labels). The source repo (`SenticNet/personality-detection`) does not itself state a license for `essays.csv`; provenance is the original Pennebaker & King corpus, whose canonical license (per the IEEE DataPort card above) is CC-BY-4.0.

### Verified counts vs. SPEC claim

- Rows: **2,467** essays (SPEC/paper claims 2,479 — 12 short, ~0.5% off; likely a slightly different release/cleaning pass of the same corpus, not a truncated download — file line count matches row count exactly, no truncation).
- Words (whitespace `str.split()`): **1,608,813** (SPEC/paper claims ~1.9M). Undercount is expected — whitespace splitting isn't the same tokenization the paper's ~1.9M-word figure was computed with (e.g. LIWC-style word counts differ from a plain split); order of magnitude matches.
- File encoding: **cp1252 / Windows-1252**, not UTF-8 (contains smart-quote byte `0x92`). Loader reads with `encoding="cp1252"`.

### Schema

Columns: `#AUTHID`, `TEXT`, `cEXT`, `cNEU`, `cAGR`, `cCON`, `cOPN` — author id, essay text, and five binary (median-split, `y`/`n`) Big Five trait labels. These are **binary trait labels, not continuous BFI scores** — SPEC 2.2 says "BFI trait scores"; this mirror only carries the median-split binary version. If continuous scores are needed for the validity-coefficient work in section 1, that requires either the IEEE DataPort original (login-gated, see above) or another source — flagging as a possible blocker for Lane 3 Day 2 / Layer B design.

Trait label balance (roughly balanced, as expected from a median split):

| trait | y | n |
|---|---|---|
| cEXT | 1,276 | 1,191 |
| cNEU | 1,233 | 1,234 |
| cAGR | 1,310 | 1,157 |
| cCON | 1,253 | 1,214 |
| cOPN | 1,271 | 1,196 |

### Loader

`loaders/essays_loader.py` — `load()`, `summarize()`. Ran clean; output above reproduced by `python3 loaders/essays_loader.py`.

## Environment

`lane3-testbed/.venv` (uv-managed), packages: `datasets`, `huggingface_hub`, `pandas`, `requests`.

## Open items for Day 2

1. Essays row count (2,467 vs. 2,479) and word count (1.6M vs. 1.9M) are close but not exact matches to the SPEC/paper figures — worth a second source cross-check if exactness matters for the paper's data-description section.
2. Essays mirror provides binary trait labels only; continuous BFI scores are not available from this fallback source. IEEE DataPort has the authoritative version behind a login — flag for Abhay if an account/download is wanted, since scripted bypass wasn't attempted.
3. `data/hc3/raw/` and `data/essays/_pages/` contain what look like concurrent/earlier fetch artifacts (HF cache copies, an IEEE page snapshot) from filesystem state that predates this run — left in place, not cleaned up, since ownership wasn't clear.
