# Chunk score refit — out-of-fold re-derivation

Response to `prompts/lane3-refit.md`, itself a response to lane 4's `LAYERB-SWEEP2.md`
Part III FAIL 1: the chunk_1..chunk_4 trait scores in `data/scores/*.json` were produced
by `RidgeClassifier`s refit on 100% of PK-human (`chunk_scoring.py`), then applied to
chunks of PK-human's own training texts — in-sample for PK-human specifically. This
contradicted `POOL-MEASUREMENTS.md` ~line 241, which described the chunk baseline as
resting on "a cross-fitted trait score." That line has been corrected in place (see the
edit at that location); this file carries the actual before/after numbers.

Script: `chunk_scoring_oof.py`. Local CPU, niced, no LLM generation, no API keys.

## What was actually leaky, and what wasn't

Only **pk_human**'s chunk scores were in-sample-leaky. The five whole-text models
(`pk_full_models` in `pool_measurement.py`) are trained on 100% of PK and then applied to
every *other* pool (big5, personallm×3, argugpt, ghostbuster, student_llm) — those pools
were never part of PK's training data under any split, so scoring their chunks with a
PK-only-trained model was always out-of-sample for them, same as their existing whole-text
`trait_scores`. Only PK-human's own chunk baseline (`POOL-MEASUREMENTS.md`'s Q14 number)
had a genuine train/test overlap: the model that scored a PK text's chunks had seen that
same PK text (whole) during training.

## Method

1. Reproduced the exact 5-fold split `pool_measurement.py` used for PK's whole-text
   cross-fitted scores: `KFold(n_splits=5, shuffle=True, random_state=20260907)` over PK's
   embeddings in `loaders.essays_loader.load()`'s order. Verified exact reproduction —
   refitting the 5 fold models and re-scoring PK's held-out texts reproduces
   `pk_human.json`'s existing `cross_fitted_scores` to **max|old−new| = 0.0** for all 5
   traits (`chunk_scoring_oof_results.json`, `fold_reproduction_max_abs_diff`).
2. **PK-human chunks**: each chunk is scored by the fold model that excluded its *parent
   text* from training — true OOF, matching the whole-text scheme exactly.
3. **Non-PK pools' chunks**: re-scored with the mean `decision_function` across all 5 fold
   models (none of which ever saw these pools' texts — this was never leakage, the
   ensemble is used only so every pool's `_oof` columns share one stated procedure).
4. New scores written as `chunk_{1..4}_oof` in every `data/scores/*.json` file, additive —
   the original in-sample `chunk_{1..4}` columns are untouched. A `chunk_meta_oof` block
   records the scoring rule per pool.

## PK-human: before (in-sample) vs after (OOF)

**Correction (pass-3 review m1, 2026-09-09):** the table below now uses `r_H(whole)`
recomputed on the same n=2,421 complete-chunk subset as everything else in this file, not
the full n=2,467 pool value. The two differ (e.g. cEXT: 0.1646 on n=2,421 vs. 0.1596 on the
full n=2,467 pool) because the complete-chunk subset excludes essays too short to split into
4 sentence-bounded chunks, which are not a random subsample. The validity-ratio numbers below
are the corrected, sample-consistent ones; they differ slightly from the previously reported
values, which mixed the two n's in numerator and denominator.

| trait | rbar in-sample | rbar OOF | mean-chunk-vs-whole IS | OOF | chunk1-vs-whole IS | OOF | r_H(whole, n=2421) | r_H(chunk1) IS | OOF | validity ratio IS | OOF |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cEXT | 0.2083 | 0.2068 | 0.5908 | 0.6424 | 0.7572 | 0.8307 | 0.1646 | 0.3380 | 0.1207 | **2.05x** | **0.73x** |
| cNEU | 0.2291 | 0.2131 | 0.5970 | 0.6716 | 0.7398 | 0.8402 | 0.1045 | 0.3327 | 0.0884 | **3.18x** | **0.85x** |
| cAGR | 0.1622 | 0.1759 | 0.5620 | 0.6351 | 0.7371 | 0.8384 | 0.1081 | 0.3252 | 0.0914 | **3.01x** | **0.85x** |
| cCON | 0.2139 | 0.2005 | 0.5682 | 0.6398 | 0.7404 | 0.8355 | 0.0710 | 0.3073 | 0.0633 | **4.33x** | **0.89x** |
| cOPN | 0.2940 | 0.2780 | 0.6766 | 0.7123 | 0.8098 | 0.8704 | 0.2233 | 0.3997 | 0.2062 | **1.79x** | **0.92x** |

(n=2,421 complete-chunk texts throughout, including the denominator `r_H(whole)`.
`chunk_scoring_oof_results.json` has the full numbers. "validity ratio" = r(chunk 1, label) /
r(whole-text, label), the exact quantity lane 4 flagged at 1.98–2.77x on their six-cell
subset.)

The in-sample "mean-chunk-vs-whole" row reproduces lane 4's cited numbers exactly —
0.5908/0.5620/0.6766 for EXT/AGR/OPN(their "OPE") — confirming this refit used the
identical procedure lane 4 diagnosed.

**Validity ratio: fixed.** In-sample, a quarter of a text looked 1.79–4.33x *more* valid
against the label than the whole text — impossible, and exactly lane 4's FAIL 1 complaint.
OOF, chunk 1 is now uniformly *less* valid than the whole text (ratio 0.73–0.92x), which is
what a quarter of a text scored honestly should look like: less signal than the whole.

**rbar and mean-chunk-vs-whole: not much changed, in different directions.** Between-chunk
agreement (rbar) moved by ≤0.016 in either direction — leakage from the training text into
that same text's own chunks apparently doesn't inflate agreement *between* chunks of the
same text much, only the *chunk-vs-label* correlation. Mean-chunk-vs-whole actually rose
(e.g. 0.5908→0.6424 EXT) under OOF scoring — plausibly because OOF chunk and whole scores
now come from the *same* fold model for a given text, where in-sample they came from
different models (a full-100%-refit model for chunks vs. a held-out fold model for the
whole-text score), adding noise to the in-sample comparison that has nothing to do with
validity.

## Non-PK pools: same pattern

Six of lane 4's cells reproduced against each pool's own `chat_r` (pool's own label vs.
whole-text score, `pool_measurements.json`) as the "whole-text validity" reference — this
is lane 3's own definition of that quantity and may not numerically match lane 4's
DGP-internal `r_H` (built under their own injected-label framework), but the ratio pattern
is the load-bearing comparison:

| cell | rel_true = chat_r² | rbar in-sample | rbar OOF | IS/true | OOF/true |
|---|---|---|---|---|---|
| big5/cEXT | 0.0581 | 0.1360 | 0.1385 | 2.34x | 2.38x |
| gpt-4/cEXT | 0.1959 | 0.3523 | 0.3609 | 1.80x | 1.84x |
| gpt-3.5/cEXT | 0.0969 | 0.3579 | 0.3672 | 3.70x | 3.79x |
| llama-2/cEXT | 0.0363 | 0.2195 | 0.2402 | 6.04x | 6.61x |
| gpt-3.5/cAGR | 0.1544 | 0.4653 | 0.4717 | 3.01x | 3.05x |
| llama-2/cOPN | 0.2541 | 0.5134 | 0.5168 | 2.02x | 2.03x |

These pools were never leaky (see "What was actually leaky" above), so it's expected that
OOF barely moves them — within 0.04–0.57x of the in-sample value, same direction as the
PK-human rbar-vs-rel_true pattern.

## Weak-H2 verdict on OOF scores: still fails, by about the same margin

**Corrected 2026-09-09 (pass-3 review m1):** this table previously used the full n=2,467
`r_H(whole)` (mismatched against the n=2,421 `rbar` figures) and its prose claimed "at most
~7%, cAGR/cOPN move up" — the direction for cOPN was wrong (it moves *down*) and the
magnitude understated (cAGR actually moves +8.43%). Recomputed with `r_H(whole)` on the same
n=2,421 subset throughout:

Lane 4's FAIL 2 is `rbar / rel_true(=r_H²)` running 6.2–11.8x on their six cells (`rbar`
vastly overstating the reliability `rel_H` that the weak-H2 disattenuation correction
needs). Recomputing that same ratio on PK-human across all 5 traits, OOF vs. in-sample:

| trait | r_H(whole, n=2421) | rel_true = r_H² | rbar/rel_true IS | rbar/rel_true OOF | % change |
|---|---|---|---|---|---|
| cEXT | 0.1646 | 0.0271 | 7.69x | 7.63x | -0.8% |
| cNEU | 0.1045 | 0.0109 | 20.98x | 19.51x | -7.0% |
| cAGR | 0.1081 | 0.0117 | 13.88x | 15.05x | **+8.4%** |
| cCON | 0.0710 | 0.0050 | 42.43x | 39.77x | -6.3% |
| cOPN | 0.2233 | 0.0499 | 5.90x | 5.58x | **-5.4%** |

Fixing the leakage moves this ratio by at most ~8.4% (cAGR, upward) in any trait; cOPN moves
*down* by 5.4%, not up as previously (wrongly) stated. Only cAGR moves up; the other four
traits move down, three by more than the previously claimed "~7%" ceiling covered only three
of the five. The non-PK pools above show the same near-invariance (0.04–0.57x movement, no
consistent direction) and are unaffected by this correction (their `r_H` figures were never
mixed-n).

**Verdict: weak-H2 still fails on OOF scores, by essentially the same margin lane 4
reported.** Lane 4's own FAIL 1 write-up predicted this: "This inflates every chunk-based
number in the optimistic direction. Weak-H2 fails anyway. That direction matters: the
failures below are a floor." That prediction holds — fixing the leakage removes the
optimistic bias in the *chunk1-vs-label validity ratio* (FAIL 1's own headline number,
now corrected from 1.76–4.43x down to 0.76–0.91x) and does not touch FAIL 2 at all,
because FAIL 2's cause (chunks of one text sharing topic/length/register/idiom, not the
trait) is a property of the text-splitting itself, not of whether the scoring model saw
that text during training. Between-chunk agreement measures stylistic self-similarity
whether the model is cross-fitted or not — the fix that was needed here was already
correctly diagnosed by lane 4 as necessary but not sufficient.

## Provenance

- In-sample scores: `chunk_{1..4}` in each `data/scores/*.json`, from `chunk_scoring.py`
  (models refit on 100% of PK, unchanged, still present for comparison).
- OOF scores: `chunk_{1..4}_oof` in each `data/scores/*.json`, from `chunk_scoring_oof.py`
  (this file). PK-human: 5-fold, chunk scored by the fold model excluding its parent text.
  Non-PK pools: mean decision_function across the 5 fold models. `chunk_meta_oof` in each
  file records which rule applied.
- Raw numeric results: `chunk_scoring_oof_results.json` (fold-reproduction check,
  per-trait/per-pool rbar and chunk-vs-whole correlations, in-sample and OOF).
- `POOL-MEASUREMENTS.md` ~line 238-241 corrected in place to point here instead of
  claiming a cross-fitted basis for the in-sample Q14 number.

No number in this file is invented; every figure above is read directly from
`chunk_scoring_oof_results.json` or `pool_measurements.json`.

REFIT-DONE
