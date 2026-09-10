# Pass-3 NLP review fixes (T1–T8)

Response to `pass3-nlp-review.md` (verdict BLOCK, 3 blockers/8 majors/3 minors) per
`pass3-nlp-fixes-brief.md`. Per-item status below; every corrected number is either cited from
`analysis/pass3_nlp_checks.py`'s output (`analysis/pass3_nlp_results.json`, which reproduces
the review's own numbers exactly, verified this pass) or computed fresh with a script listed
in that item's provenance.

## T1 (blocker B1) — partial-correlation redo — FIXED

`WEAK-H2-DIAGNOSIS.md`'s §2.4 originally reported "0.0% removed" partial correlation in every
trait (a constant/misdecoded control), withdrawn and replaced. Recomputed with
`analysis/pass3_nlp_checks.py` (closed-form partial correlation, cross-checked against direct
residualization to 1e-12), matching the review's own numbers exactly:

| trait | raw rbar | partial rbar (label) | relative reduction | partial rbar (label+length) | % surviving |
|---|---|---|---|---|---|
| cEXT | 0.20678 | 0.19819 | 4.15% | 0.18503 | 89.5% |
| cNEU | 0.21310 | 0.20544 | 3.59% | 0.19765 | 92.8% |
| cAGR | 0.17586 | 0.17098 | 2.77% | 0.17050 | 97.0% |
| cCON | 0.20053 | 0.19743 | 1.54% | 0.19406 | 96.8% |
| cOPN | 0.27800 | 0.25128 | 9.61% | 0.24784 | 89.2% |

**Claims withdrawn from `WEAK-H2-DIAGNOSIS.md`:** "controlling for the trait label removes
0.0% of rbar, in every trait, to 4 decimal places"; "The between-chunk correlation is,
empirically, orthogonal to the very construct it is being used to estimate the reliability
of"; ">93% of rbar survives controlling for the two most obvious candidate nuisances (label,
length) in every trait" (cEXT 89.5%, cOPN 89.2% both fall under 93%); every "ruled out,
decisively"/"100.0%" framing in §2.4–2.5; §2.7's "quantitative confirmation... rules out the
four alternative mechanisms"; the Verdict's "not recoverable on this testbed at any n or pi",
"structural property... not by any fixable measurement error", "falsifies the assumption
directly". §2.4, §2.5, §2.7, and the Verdict in `WEAK-H2-DIAGNOSIS.md` are rewritten to the
narrower, evidence-supported claim: **the current scoring/correction setup fails to recover
`rel_H` from chunk correlations on this corpus**, most (89–98%) residual agreement survives
label+length control and remains unattributed to a tested cause — consistent with, but not
proof of, a document-level style/topic factor. This does **not** establish impossibility at
any n/pi, and does **not** establish orthogonality to the construct (a binary median-split
label is too coarse a control to rule that out).

Reproduction: `nice -n 15 lane3-testbed/.venv/bin/python analysis/pass3_nlp_checks.py`
(read-only, asserts label variance > 0 and row alignment before computing).

## T2 (blocker B2) — Big5PersonalityEssays provenance — FIXED

Corrected `lane4-simulation/LAYERB-SWEEP.md` (top-of-file note + §"The defect" + §7 disclosure)
and `lane4-simulation/LAYERB-ROUND3.md` (§2.1 + the OPE-slope discussion): the pool is
GPT-4-turbo synthetic text (source repo + arXiv:2407.17586, already flagged machine in
`CORPUS-AUDIT.md`), correctly placed in the machine slot by the loader. Its AUC≈0.44–0.48 /
near-zero sensitivity is now described as a **detector failure on synthetic text** (a genuine
boundary datum), not a human negative control. No numeric result changed — the code already
scored it as machine; only the prose interpretation was wrong, in both files.

**Claims withdrawn:** "`big5_personality_essays` is a human corpus... standing in the machine
slot... the negative control for the detector route" (LAYERB-SWEEP.md); "big5-essays is human
text" (LAYERB-SWEEP.md §"The defect"); "`big5_personality_essays` is human text in the machine
slot... a negative control, not a detector result" (LAYERB-SWEEP.md §7); "The essays pool is
human-written" (LAYERB-ROUND3.md §2.1); "whose 'machine' texts are human-written" (LAYERB-ROUND3.md, OPE slope discussion).

## T3 (major M1) — prefix-only embedding disclosure + stronger baselines — FIXED

Disclosed in `POOL-MEASUREMENTS.md`: `all-MiniLM-L6-v2` truncates at 256 tokens; 2,433/2,467
PK essays (98.62%) exceed that window; median input length 759 tokens; the encoder retains
32.15% of total content tokens (numbers reproduced from `analysis/pass3_nlp_checks.py`,
`tokenization` block, matching the review exactly).

Ran two new comparator baselines (`analysis/t3_baselines.py`, n=2,421 complete-chunk PK
subset, same 5-fold split as the prefix-ridge scorer):

| trait | prefix-ridge (r_H, n=2421) | document-pooled (4-chunk mean embed) | lexical TF-IDF + ridge |
|---|---|---|---|
| cEXT | 0.1646 | 0.1678 | 0.1593 |
| cNEU | 0.1045 | **0.2275** | 0.1488 |
| cAGR | 0.1081 | 0.1365 | 0.0853 |
| cCON | 0.0710 | 0.1436 | 0.1226 |
| cOPN | 0.2233 | **0.3111** | 0.2425 |

Document-pooling (mean of the 4 sentence-count chunk embeddings) beats prefix-ridge in all 5
traits, consistent with M1's prediction that truncation was suppressing recoverable signal.
Each of the 4 chunks is still subject to the encoder's 256-token limit on its own; chunking is
sentence-count-based (`chunk_at_sentence_boundaries`, k=4 near-equal groups), not token-bounded,
so complete token coverage of the document is not guaranteed and was not separately verified.
Broader document coverage than the single-prefix baseline should not be reported beyond that.
Prefix-ridge is kept as the stated baseline throughout; construct-validity language elsewhere in
`POOL-MEASUREMENTS.md`/`CHUNK-REFIT.md` is now scoped to that instrument unless a table cites a
comparator explicitly.

## T4 (major M2) — nested-evaluation asymmetry — FIXED (scoring-protocol sensitivity analysis)

Chose option (a): measured the effect directly rather than only scoping claims. Human scores
use a single held-out-fold ridge model per point; machine scores in the existing report use a
100%-refit model. `analysis/t4_scoring_asymmetry.py` rescored all 4 labeled machine pools
(big5, personallm×3, 20 trait/pool cells) with a 5-fold-ensemble-mean protocol instead and
compared against the existing 100%-refit `kappa`/`delta`. This is a sensitivity analysis on the
scoring protocol, not a measured correction for the asymmetry — a 5-model ensemble mean over
folds is still not identical to the single held-out-fold protocol used on the human side, and
the script's own docstring notes the asymmetry remains. Numerical conclusions below are
restricted to these four rerun pools.

- **kappa drops 9.0%–15.4%** under the ensemble protocol relative to the existing full-refit
  values, consistently (every cell).
- **delta moves by only −0.069 to +0.064** (absolute, PK-SD units) — small relative to typical
  |delta| > 0.2 elsewhere in the report.

Documented in `POOL-MEASUREMENTS.md`: for these four pools, that 9.0–15.4% full-refit-to-ensemble
decrease corresponds to the full-refit kappa being approximately **9.9–18.1% inflated relative
to the ensemble-protocol kappa**; delta is largely unaffected. Unlabeled pools (argugpt,
ghostbuster, student_llm) were not rerun — same asymmetry applies by construction, magnitude not
separately measured, flagged as scoped.

## T5 (major M3) — HC3 question-grouped split — FIXED

`detector/calibration.py`: `sample_hc3_pairs` now carries `question_id=(source, index)` per
pair; `split_calibrate_test` splits by question, not flattened row. Previously 622/1250
questions straddled calibrate/test (reproduced exactly via `pass3_nlp_checks.py`'s `hc3_split`
block); now zero straddle by construction. Recomputed calibration:

| detector | split | se | sp | AUC |
|---|---|---|---|---|
| roberta-base-openai-detector | HC3 held-out test (new-question) | 0.9136 | 0.9360 | 0.9748 |
| feature-baseline logreg | HC3 held-out test (new-question) | 0.8304 | 0.7968 | 0.8730 |

Threshold moved 0.7537 → 0.7907 (roberta) because it's chosen on a differently-composed
calibrate set. Added a question-clustered bootstrap CI (`question_cluster_bootstrap_ci`,
2,000 resamples of whole questions) to `calibration_results.json` for both detectors, since a
naive per-row CI understates uncertainty from paired human/machine answers to one question:
roberta se 95% CI [0.890, 0.936], sp 95% CI [0.917, 0.954]; feature baseline se 95% CI
[0.802, 0.861], sp 95% CI [0.763, 0.827].
"New-answer-same-question" is no longer a distinct case to report — the corrected split
guarantees every test question is entirely new relative to calibrate, so there is nothing left
to distinguish it from. `CALIBRATION-REPORT.md` §1 rewritten with all of the above.

## T6 (major M4) — P1 arm naming + SPEC.md wording list — FIXED (doc) / SCOPED (SPEC.md)

`lane4-simulation/INJECT.md`: added a naming-correction note after §1's design paragraph
("random/matched text assignment," not c=0/partial/high prompt-disclosure — varying `p` only
rematches pre-existing text to a label, never touches generation) and a new §7a-ii after §7a
restricting ecological claims to scored-text marginals and stating that respondent-level
outsourcing validity requires a separate experiment with independently generated,
disclosure-varied text per respondent. SPEC.md was **not edited** per the hard constraint;
needed wording changes are listed below for the orchestrator.

### SPEC.md wording changes needed (not applied — for the orchestrator)

- **§2.3 (lines ~48–55, "LLM counterpart generation")**: no change needed to the c=0/partial/high
  definitions themselves — these remain the intended *design* for the not-yet-run generation
  batch. The issue (M4) is only that `INJECT.md`'s `p`-sweep is currently discussed as if it
  already exercised these three conditions; it does not (it rematches existing text, it
  doesn't vary generation-time disclosure). No SPEC.md text is factually wrong here.
- **§2.4 (line ~59, "the honest range from the NORC PACT work is roughly 99% in-domain down to
  mid-80s out of domain")**: **wrong**, same misattribution as T7b. Replace with: "NORC PACT
  (Huang et al., AAPOR 2025) reports general-population precision 0.989/recall 0.999/accuracy
  0.990, and technical-domain accuracy in the upper-80s to mid-90s, precision up to 85.7%,
  recall up to 100%; it does not publish an out-of-domain sensitivity figure — do not cite one
  from this source."
- **§4.2 (lines ~87–89, "Layer B: semi-synthetic on real text")**: add a sentence naming what
  Layer B's `pi` sweep actually manipulates — "Injection here is via random/matched
  *assignment* of already-scored text to respondent labels (see `INJECT.md` §1), not
  generation-time disclosure variation; ecological claims are restricted to scored-text
  marginals unless a separate disclosure-varied-generation experiment is run."
- **§2.2 (line 46, data description, flagged by review m2, out of this brief's explicit
  T-list but adjacent)**: describes "2,479 essays... about 1.9M words... with Big Five (BFI)
  trait scores" (continuous). The acquired corpus actually has 2,467 essays, 1,608,813
  whitespace-counted words, and **binary** median-split labels, not continuous BFI scores
  (`TESTBED-REPORT.md`). Not fixed here (out of T1–T8's explicit scope) but flagged since it's
  adjacent to T6's SPEC.md review and the orchestrator may want to batch SPEC.md edits.

## T7 (major M5) — detector-transfer and attribution fixes — FIXED

**(a) g-formula reconciliation:** `pool_measurement.py:245` computed the stale `chat_r / r_H`
ratio while `pool_measurements.json`'s stored `g` column and `POOL-MEASUREMENTS.md`'s
definition already used the corrected covariance-ratio form
`g = chat_r * sqrt(kappa) / r_H` (from an earlier pilot fix this project). Fixed the code to
match: `pool_measurement.py` now computes both, storing the corrected form as `g` and the
stale one as `g_old_ratio_form` (matching the already-published JSON's field names).
`POOL-MEASUREMENTS.md`'s method note updated to document the fix and cross-reference.
`pool_measurements.json` itself was not regenerated — it already held the corrected numbers;
only the script that would reproduce it was stale, and that staleness is now fixed.

**(b) NORC metric misattribution:** `detector/calibration.py`'s `norc_pact_reference_range`
block replaced `"out_of_domain_se_ballpark": "mid-80s (%)"` (unsourced) with the actual
Huang et al. AAPOR 2025 slide-7 figures (general-population precision/recall/accuracy,
technical-domain accuracy/precision/recall ranges) and an explicit note that no out-of-domain
sensitivity figure is published there. `CALIBRATION-REPORT.md` rewritten to match (see T5).

**(c) Essay calibration vs. external transfer, separated:** `CALIBRATION-REPORT.md` §1 now
explicitly distinguishes the essay-domain specificity-only "degraded" row (real PK essays, HC3
threshold) from the fixed-HC3-threshold sensitivity transfer table on the machine pools —
stated as two different quantities on two different corpora, not comparable or combinable.

**(d) Fixed-threshold transfer table, completed** (post-T5-fix threshold 0.790723):

| corpus | n | fixed-threshold rate |
|---|---:|---:|
| PK humans | 2,467 | specificity 0.9501 |
| Big5PersonalityEssays (GPT-4-turbo) | 399 | sensitivity 0.0075 |
| PersonaLLM GPT-4 | 320 | sensitivity 0.4969 |
| PersonaLLM GPT-3.5 | 320 | sensitivity 0.3313 |
| PersonaLLM Llama-2 | 320 | sensitivity 0.8094 |

(These differ slightly from the review's own table, which was computed at the pre-T5-fix
threshold 0.7536994815 — expected, since T5 changed the threshold. Both are internally
consistent with their respective calibration runs.)

## T8 (hygiene) — commit checks script + results — FIXED

`analysis/pass3_nlp_checks.py`, `analysis/pass3_nlp_results.json`,
`analysis/t3_baselines.py` + `analysis/t3_baselines_results.json`,
`analysis/t4_scoring_asymmetry.py` + `analysis/t4_scoring_asymmetry_results.json`, and
`pass3-nlp-review.md` itself are added to git in this pass's commit(s). Every corrected number
in this file has a script it came from (T1/T5 numbers: `pass3_nlp_checks.py`; T3:
`t3_baselines.py`; T4: `t4_scoring_asymmetry.py`; T5's se/sp/AUC/CI: `detector/calibration.py`,
one-command reproduction `python3 detector/calibration.py`).

## Files touched this pass

`WEAK-H2-DIAGNOSIS.md`, `POOL-MEASUREMENTS.md`, `CHUNK-REFIT.md` (m1 correction, unassigned a
T-number but bundled here since it shares the validity-ratio table T1 touches — see below),
`CALIBRATION-REPORT.md`, `pool_measurement.py`, `detector/calibration.py`,
`lane4-simulation/LAYERB-SWEEP.md`, `lane4-simulation/LAYERB-ROUND3.md`,
`lane4-simulation/INJECT.md` (doc-only, confirmed no code/config/inject/estimators.py touched),
plus the four new `analysis/*.py` scripts and their result JSONs.

### m1 (minor, bundled with T1's file) — FIXED

`CHUNK-REFIT.md`'s "at most ~7%" summary and its "cAGR/cOPN move up" direction claim were
wrong (cAGR actually moves +8.4%, cOPN moves *down* 5.4%). Also, its validity-ratio table
mixed `r_H(whole)` from the full n=2,467 pool with `rbar`/chunk figures from the n=2,421
complete-chunk subset (complete-case EXT whole validity is 0.1646, not 0.1596). Recomputed
`r_H(whole)` on the n=2,421 subset throughout and corrected both tables and the surrounding
prose in `CHUNK-REFIT.md`.

PASS3-NLP-FIXES-DONE
