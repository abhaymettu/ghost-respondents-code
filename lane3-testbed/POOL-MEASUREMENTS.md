# P1' Pool Measurements

Design-pivot-memo §8.2 step 1. Local compute only, no generation, no API keys.
Script: `pool_measurement.py` (PID 91058, ran 19:25:18–19:41:55, log: `pool_measurement.log`).
Raw numbers: `pool_measurement_raw.json`. Per-text scores: `data/scores/*.json` (8 files).

## Method note (definitions as implemented, not just as named in the memo)

- **r_H** — PK-human trait recoverability: 5-fold cross-fitted `RidgeClassifier` on
  `all-MiniLM-L6-v2` embeddings (n=2467, full-length PK-essays), point-biserial r between
  the cross-fit decision score and the PK trait label. One value per trait, shared across
  all pools (it's a property of PK, not of the machine pool).
- **c-hat** (`chat_r` in the raw JSON) — pool-own-label recoverability: PK-trained
  *full-refit* trait model (all 2467 PK texts, no held-out fold) scored against each
  labeled pool's own texts, correlated against that pool's own trait label.
- **g** — `chat_r / r_H`, the ratio of pool-label recoverability to PK-baseline
  recoverability. g≈1 means the PK-trained model recovers the trait in this pool about as
  well as it recovers it in PK itself; g≫1 or g<0 means the model is picking up something
  systematically different in the pool (see cOPN below).
- **kappa** — `s2_M / V_H`, ratio of the machine pool's trait-score variance to PK's
  cross-fitted trait-score variance.
- **delta** — `(mu_M − mu_H) / sqrt(V_H)`, the pool's mean trait score minus PK's mean,
  in PK-standard-deviation units.
- **AUC** — roberta-base-openai-detector AUC discriminating PK-human texts from the pool's
  machine texts (machine-vs-human detectability, not trait-related).
- **A3** — within-pool correlation between the roberta detector's raw machine-probability
  score and the pool's own trait label. Tests whether the detector is silently sensitive to
  the trait itself (would confound trait effects with detectability).

## Labeled pools

### big5_personality_essays (n=399)

| trait | r_H | c-hat (chat_r) | g | kappa | delta | A3 r (p) |
|---|---|---|---|---|---|---|
| cEXT | 0.1596 | 0.2410 (p=1.1e-06) | 1.31 | 0.754 | -0.453 | -0.013 (p=.79) |
| cNEU | 0.1023 | 0.1061 (p=.034) | 0.93 | 0.797 | -0.236 | 0.033 (p=.51) |
| cAGR | 0.1060 | 0.1416 (p=.0046) | 1.24 | 0.866 | -0.788 | -0.067 (p=.18) |
| cCON | 0.0694 | 0.1231 (p=.014) | 1.75 | 0.968 | 0.317 | -0.042 (p=.40) |
| cOPN | 0.2267 | -0.0295 (p=.56) | -0.10 | 0.602 | 2.128 | 0.099 (p=.049) |

detector AUC vs PK = **0.4724** (n=399) — essentially chance; roberta doesn't distinguish
these essays from PK-human at all.

### personallm_gpt-4-0613 (n=320)

| trait | r_H | c-hat | g | kappa | delta | A3 r (p) |
|---|---|---|---|---|---|---|
| cEXT | 0.1596 | 0.4426 (p=8.8e-17) | 2.52 | 0.823 | -0.492 | 0.070 (p=.21) |
| cNEU | 0.1023 | 0.1096 (p=.050) | 0.99 | 0.861 | -0.287 | -0.028 (p=.62) |
| cAGR | 0.1060 | 0.1674 (p=.0027) | 1.65 | 1.091 | -0.434 | 0.146 (p=.0090) |
| cCON | 0.0694 | 0.0248 (p=.66) | 0.33 | 0.846 | 0.239 | -0.039 (p=.48) |
| cOPN | 0.2267 | 0.3142 (p=9.3e-09) | 1.27 | 0.842 | 2.107 | 0.004 (p=.95) |

detector AUC vs PK = **0.8359** (n=320).

### personallm_gpt-3.5-turbo-0613 (n=320)

| trait | r_H | c-hat | g | kappa | delta | A3 r (p) |
|---|---|---|---|---|---|---|
| cEXT | 0.1596 | 0.3112 (p=1.3e-08) | 1.64 | 0.707 | -0.535 | -0.162 (p=.0037) |
| cNEU | 0.1023 | 0.0047 (p=.93) | 0.04 | 0.922 | -0.374 | 0.103 (p=.065) |
| cAGR | 0.1060 | 0.3930 (p=2.9e-13) | 3.45 | 0.868 | -0.403 | 0.138 (p=.013) |
| cCON | 0.0694 | 0.0538 (p=.34) | 0.66 | 0.721 | 0.239 | -0.103 (p=.066) |
| cOPN | 0.2267 | 0.0566 (p=.31) | 0.18 | 0.502 | 2.576 | 0.042 (p=.45) |

detector AUC vs PK = **0.7775** (n=320).

### personallm_llama-2 (n=320)

| trait | r_H | c-hat | g | kappa | delta | A3 r (p) |
|---|---|---|---|---|---|---|
| cEXT | 0.1596 | 0.1906 (p=6.1e-04) | 0.88 | 0.542 | -0.228 | -0.176 (p=.0016) |
| cNEU | 0.1023 | 0.1989 (p=3.4e-04) | 1.96 | 1.017 | -0.414 | -0.050 (p=.38) |
| cAGR | 0.1060 | 0.3395 (p=4.5e-10) | 2.99 | 0.870 | -0.507 | 0.046 (p=.41) |
| cCON | 0.0694 | 0.1680 (p=.0026) | 2.18 | 0.813 | -0.515 | 0.057 (p=.31) |
| cOPN | 0.2267 | 0.5040 (p=5.1e-22) | 2.43 | 1.195 | 1.630 | -0.044 (p=.43) |

detector AUC vs PK = **0.9452** (n=320) — highest of the three PersonaLLM generators;
llama-2 text is the most detectable against PK-human of the labeled machine pools.

## Unlabeled pools (kappa, delta, AUC only — no gold labels, so no c-hat/g/A3)

### argugpt (n_pool_total=3338, n_used=500)

| trait | kappa | delta |
|---|---|---|
| cEXT | 1.385 | 0.062 |
| cNEU | 1.493 | -0.542 |
| cAGR | 1.517 | -0.064 |
| cCON | 1.331 | 0.138 |
| cOPN | 0.814 | 1.146 |

detector AUC vs PK = **0.9809** (n=500) — highest AUC of all 7 machine pools measured.

### ghostbuster_gpt_writing (n_pool_total=694, n_used=500)

| trait | kappa | delta |
|---|---|---|
| cEXT | 1.262 | -0.030 |
| cNEU | 1.497 | -0.208 |
| cAGR | 1.569 | -0.034 |
| cCON | 1.701 | 0.022 |
| cOPN | 1.012 | 1.142 |

detector AUC vs PK = **0.6356** (n=500).

### student_llm_essays (n_pool_total=2078, n_used=500)

| trait | kappa | delta |
|---|---|---|
| cEXT | 1.704 | 0.360 |
| cNEU | 0.931 | 0.008 |
| cAGR | 0.776 | -1.353 |
| cCON | 2.020 | -0.591 |
| cOPN | 0.399 | 1.457 |

detector AUC vs PK = **0.5725** (n=500) — lowest AUC of the unlabeled pools; closest to
chance-level detectability against PK-human.

All three unlabeled pools show the same cOPN pattern as the labeled pools: large positive
delta (machine text scores far higher on the PK-trained Openness model than PK-human text
does), consistent across every one of the 7 machine pools measured.

## Side-check (a): A3 — detector score vs. own trait label

Per-pool A3 tables are folded into the labeled-pool sections above. Summary: of the 20
(pool × trait) A3 correlations across the 4 labeled pools, only 4 reach p<.05 — big5_OPN
(r=0.099, p=.049), gpt-4_AGR (r=0.146, p=.0090), gpt-3.5_EXT (r=-0.162, p=.0037),
gpt-3.5_AGR (r=0.138, p=.013) — and none exceed |r|=0.18. The roberta detector's raw
machine-probability score is not meaningfully correlated with any Big Five trait label
within any labeled pool. A3 holds: detectability and trait content are not confounded in
these pools.

## Side-check (b): Spearman-Brown truncation recheck

PK cross-fitted r_H re-run at 100-word and 190-word truncations vs. the full-length
baseline (memo §3.2/E72 predicts truncated r_H < full-length r_H, shrinking toward zero
as length drops, roughly following a Spearman-Brown reliability curve):

| trait | full-length r_H | 190w r_H | 100w r_H |
|---|---|---|---|
| cEXT | 0.1596 | 0.1532 | 0.1204 |
| cNEU | 0.1023 | 0.1009 | 0.0987 |
| cAGR | 0.1060 | 0.1112 | 0.0888 |
| cCON | 0.0694 | 0.0849 | 0.0684 |
| cOPN | 0.2267 | 0.2182 | 0.1566 |

The premise holds directionally for 4 of 5 traits at 100w (cEXT, cNEU, cAGR, cOPN all drop
below full-length) and for 3 of 5 at 190w (cEXT, cOPN drop; cNEU roughly flat; cAGR and
cCON actually rise slightly above full-length — noise at this sample size, not a
Spearman-Brown violation, since cAGR/cCON r_H are small to begin with, p=1.3e-07/5.7e-04
respectively at full length). The memo's specific numeric cEXT prediction (0.245 at
190w-or-full, 0.180 at 100w) is *not* matched by the measured cEXT r_H (0.1596 full, 0.1532
at 190w, 0.1204 at 100w) — measured values run about 0.06–0.09 below the memo's predicted
values at every length, a systematic gap, not just truncation-driven decay. The
memo prediction should be treated as stale/miscalibrated against this measurement, not as
confirmed.

## Side-check (c): Big5PersonalityEssays label balance (n=399)

| trait | label=0 | label=1 |
|---|---|---|
| cEXT | 182 | 217 |
| cNEU | 198 | 201 |
| cAGR | 178 | 221 |
| cCON | 185 | 214 |
| cOPN | 185 | 214 |

All five traits are within ~55/45 of balanced; cNEU is closest to 50/50 (198/201), cAGR is
the most skewed (178/221, 44.6%/55.4%). No trait is severely imbalanced enough to threaten
the memo's Prop 16 balance assumption.

## Side-check (d): PersonaLLM human_stories vs. PK essays.csv hash match

- `human_stories` files: 2467
- PK `essays.csv` rows: 2467 (same count)
- Exact SHA-256 match (whitespace-normalized): **185 / 2467 = 7.50%**

Only 1 in 13 PersonaLLM `human_stories` texts hashes identically to a PK essay after
whitespace normalization, despite matching counts. The `human_stories` files carry
LOCNAME/PROPNAME anonymization tokens not present in the raw `essays.csv` text, so the low
match rate is consistent with PersonaLLM's `human_stories` being the *same underlying PK
corpus run through additional anonymization preprocessing*, not a different corpus — the
matching count (2467=2467) is the stronger signal here than the low exact-hash rate, which
mechanically drops from any preprocessing divergence (anonymization, whitespace/casing
changes beyond simple whitespace collapse, etc.). This is consistent with, not proof of,
same-corpus-different-preprocessing; a token-level diff would be needed to fully confirm it,
which is out of scope for this measurement pass.

## Per-text score files

All under `data/scores/`, one file per pool, each containing per-text ids, labels (where
available), trait scores, and (for labeled/unlabeled machine pools) detector probabilities:

- `pk_human.json` (343K) — PK ids, trait labels, cross-fitted trait scores
- `big5_personality_essays.json` (66K)
- `personallm_gpt-4-0613.json` (58K)
- `personallm_gpt-3.5-turbo-0613.json` (59K)
- `personallm_llama-2.json` (58K)
- `argugpt.json` (70K)
- `ghostbuster_gpt_writing.json` (79K)
- `student_llm_essays.json` (76K)

## Chunk scoring

Fulfills lane4's `INJECT.md` section 9 dependency (the chunk-level scores for the
weak-H2 rescue, design-pivot-memo.md line 142). Script: `chunk_scoring.py`.

**Split rule.** k=4 chunks per text, split at sentence boundaries, sentences grouped
into contiguous near-equal-count chunks (remainder sentences, if any, go one each to
the first chunks, so group sizes differ by at most one sentence). Sentence-boundary
splitting is the memo-sanctioned length control (design-pivot-memo.md line 162:
"Truncation at a sentence boundary is a legitimate length control"). A text with fewer
than 4 sentences cannot be split into 4 non-trivial chunks and is skipped (not padded,
not silently dropped) — its `chunk_1..chunk_4` entries are `null` for that text, and the
count is reported in `chunk_meta` (see below) and in `chunk_scoring_summary.json`.

Chunk boundaries are on sentences only; no chunk is a word-count truncation of another,
so results are not confounded with the audit-3 truncation check.

**Models.** `pool_measurement.py`'s per-trait full-refit `RidgeClassifier(alpha=1.0)`
models (fit on 100% of PK-human, same `all-MiniLM-L6-v2` embeddings) were **not** saved
to disk when that script ran, so they were **refit from scratch** here using the
identical code path (same loader, same embedding call, same hyperparameters, same seed)
rather than reused — this avoids drift from the already-reported per-text numbers, but
is a refit, not a reload. The 5 refit RidgeClassifiers plus a reference file naming the
sentence-transformer are now exported to `data/models/` (`ridge_cEXT.joblib`,
`ridge_cNEU.joblib`, `ridge_cAGR.joblib`, `ridge_cCON.joblib`, `ridge_cOPN.joblib`,
`sentence_transformer.txt` = `all-MiniLM-L6-v2`), so a future run can reuse them directly.

**PK-human between-chunk baseline (Q14).** Mean pairwise Pearson r of cEXT across the 4
chunks, computed on every PK text that could be split into 4 chunks (n=2,421 of 2,467;
46 texts had fewer than 4 sentences and were excluded, not padded):

  **r = 0.2083** (n=2,421)

This is the human within-text consistency baseline design-pivot-memo.md Q14 asks for —
any machine-pool chunk-level H2 result should be read against this number, not against 0
or 1, since even human-written chunks of the same essay do not correlate perfectly on a
cross-fitted trait score.

**Per-pool chunking snags** (from `chunk_scoring_summary.json`, texts skipped for having
fewer than 4 sentences, out of pool size):

| pool | skipped | n |
|---|---|---|
| pk_human | 46 | 2,467 |
| big5_personality_essays | 65 | 399 |
| personallm_gpt-4-0613 | 0 | 320 |
| personallm_gpt-3.5-turbo-0613 | 0 | 320 |
| personallm_llama-2 | 0 | 320 |
| argugpt | 2 | 500 |
| ghostbuster_gpt_writing | 0 | 500 |
| student_llm_essays | 0 | 500 |

big5_personality_essays has the highest skip rate (16%, short essays); all other machine
pools are near-zero.

**File changes.** Every file in `data/scores/*.json` (the 8 listed above) gained four
additive keys — `chunk_1`, `chunk_2`, `chunk_3`, `chunk_4` (each a list, aligned to `ids`,
of either `null` or a dict `{cEXT, cNEU, cAGR, cCON, cOPN}` giving that chunk's trait
scores) — plus a `chunk_meta` dict (`k`, `split_rule`, `n_texts_too_short_to_chunk`,
`n_texts_total`). No existing key (`ids`, `trait_scores`/`labels`, `detector_p_machine`,
`cross_fitted_scores`) was altered; verified by re-reading all 8 files after the write.

**Compatibility note for lane4.** `lane4-simulation/inject/pools.py` was read in full to
confirm what shape it expects for `chunk_1..chunk_k`. Its `_read_rows`/`pool_from_rows`
path expects one row per **text** (a JSON list-of-dicts, JSON `{"rows": [...]}`, or CSV),
with `chunk_1`, `chunk1`, or `chunk_{j}_{trait}` as flat per-row columns, reached via a
`scores_path` that `load_measurements()` resolves per (pool, trait) out of
`pool_measurements.json`. Lane3's actual per-pool files are dict-of-arrays keyed by
`ids`/`trait_scores`/`detector_p_machine` (one file per **pool**, all 5 traits together,
no `scores_path` field set anywhere in `pool_measurements.json`) — this was already true
of the base per-text scores before this task and is **not** fixed by adding
`chunk_1..chunk_4` in this same shape: `pools.py`'s loader cannot parse either format as
written. This is a pre-existing lane3/lane4 format mismatch, not something introduced or
resolved here; `_pick()`'s alias resolution covers column-name near-misses (e.g. `EXT`
vs `cEXT`), not this structural difference. Flagging for lane4/whoever wires the loader
next, rather than silently assuming it will work.

MEASURE-DONE
CHUNKS-DONE

## Pilot fixes

Two fixes requested from `lane4-simulation/LAYERB-PILOT.md` sections 1 and 5.

### Fix 1 — PK-human detector scores now saved

`pool_measurement.py:253` ran the roberta detector over `pk_this_texts + pool_texts_for_auc`
to get each labeled pool's AUC-vs-PK, but only kept `scores_auc[n:]` — the pool half. The
PK-human half was used for the AUC computation and discarded, so `data/scores/pk_human.json`
never got a `detector_p_machine` column, unlike every pool score file. This blocked SPEC
3.2's `adjusted_count` prevalence branch, which needs `sp` from human detector scores
(LAYERB-PILOT.md section 5).

Fixed by `pk_human_detector_scores.py`: reruns the roberta detector over all 2467 PK-human
essays (not just the ≤500 sampled for AUC) and writes `detector_p_machine` into
`data/scores/pk_human.json`, aligned 1:1 to the file's existing `ids` order (same
`load_pk()`/CSV order used to build `ids` originally — asserted in-script before writing).

**Coverage: 2467/2467 (100%)**. 207.9s on CPU, single roberta pass, no sampling. All other
keys in `pk_human.json` (`ids`, `labels`, `cross_fitted_scores`, `chunk_1..4`, `chunk_meta`)
are untouched.

### Fix 2 — `g` recomputed as a covariance ratio, not a ratio of correlations

`pool_measurement.py:245` computed `g = chat_r / r_H`, a ratio of two correlations. Per
(E66), `g := Cov(x_M, theta) / Cov(x_H, theta)`, and since `Cov(x_M, theta) = c_hat * sd_M`,
the correct form is `g = c_hat * sqrt(kappa) / r_H`. The old formula is high by exactly
`1/sqrt(kappa)` — confirmed exactly (to float precision) across every one of the 20 labeled
`(pool, trait)` cells that have a `g` value (4 pools × 5 traits: Big5PersonalityEssays,
PersonaLLM gpt-4/gpt-3.5-turbo/llama-2).

Recomputed every `g` in both `pool_measurements.json` (in place, old value preserved
per-trait as `g_old_ratio_form`) and every table below in this file, using quantities
already stored from the P1' pass (`chat_r`, `kappa`, `r_H` — no re-embedding, no re-fit).
`pool_measurements.json.meta.g_formula` records the method.

Example (`personallm_gpt-4-0613`, cEXT, whole pool, n=320):

| quantity | value |
|---|---|
| chat_r | 0.4426 |
| kappa | 0.8232 |
| r_H | 0.1596 |
| g, old (chat_r / r_H) | 2.7725 |
| g, corrected (chat_r·sqrt(kappa) / r_H) | 2.5157 |

Full old-vs-new for that same pool/trait set (all 20 labeled cells) is in
`pool_measurements.json`; the tables above (`## Labeled pools`) now show corrected `g`
values directly. Unlabeled pools (argugpt, ghostbuster_gpt_writing, student_llm_essays)
have no `c-hat`/`g`/A3 to begin with (no gold labels) and are unaffected.

FIXES-DONE
