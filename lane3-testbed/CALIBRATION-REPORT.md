# Lane 3 testbed report — Day 2

Continues `TESTBED-REPORT.md` (Day 1: data pull, loaders, license/count verification). Today: detector calibration, the r_F fluency anchor, the rho_v measurement plan/code, and the testbed freeze. No LLM counterpart generation was run — that batch stays gated on the burn report to Abhay.

## 1. Detector calibration

Two detectors, both calibrated on HC3 pairs (`detector/calibration.py`, results in `detector/calibration_results.json`):

1. **Published open-weights classifier**: `openai-community/roberta-base-openai-detector` (MIT license, downloaded from Hugging Face, not gated). It was trained to detect GPT-2 output, not ChatGPT — used zero-shot here, no fine-tuning, which is the realistic "off-the-shelf detector, threshold picked by calibration only" scenario the SPEC describes.
2. **Simple feature baseline**: logistic regression over 7 stylometric features (word count, sentence count, avg word length, avg sentence length, type-token ratio, punctuation rate, comma rate — `detector/features.py`).

Calibration procedure: stratified sample of 250 questions per HC3 source (5 sources × 250 × 2 texts = 2,500 texts), split 50/50 into a calibrate set (pick threshold via Youden's J, maximizing se + sp − 1) and a held-out test set (report se/sp there). Same procedure, same split, for both detectors.

### Operating points

| detector | split | se | sp | AUC |
|---|---|---|---|---|
| roberta-base-openai-detector | HC3 held-out test (**calibrated**, in-domain) | 0.911 | 0.940 | 0.971 |
| roberta-base-openai-detector | essays, human-only (**degraded**, out-of-domain) | n/a — see below | 0.926 | — |
| roberta-base-openai-detector | **oracle** | 1.0 | 1.0 | — (definitional) |
| feature-baseline logreg | HC3 held-out test (**calibrated**, in-domain) | 0.829 | 0.818 | 0.891 |
| feature-baseline logreg | essays, human-only (**degraded**, out-of-domain) | n/a — see below | 0.916 | — |
| feature-baseline logreg | **oracle** | 1.0 | 1.0 | — (definitional) |

**The degraded/out-of-domain se cells are not computable yet.** The essays testbed has no LLM-authored counterparts — that generation batch hasn't run. So the only out-of-domain quantity available today is specificity: apply the HC3-calibrated threshold to 500 sampled essays (all genuinely human) and measure the false-positive rate. Sensitivity out-of-domain (does the detector still catch machine essays once they exist?) needs the counterpart batch. Once that batch runs, re-run `detector/calibration.py`'s essays block on the machine-authored essays to fill in `se` there.

### Comparison to NORC PACT

NORC PACT's honest range is roughly 99% in-domain down to mid-80s out-of-domain (se, presumably against a detector purpose-tuned for survey/ChatGPT text). Our in-domain se (91.1% roberta, 82.9% feature baseline) sits below their 99% figure — expected, since our detector was never fine-tuned on ChatGPT or HC3 at all (it's a GPT-2 detector applied zero-shot); NORC's in-domain number likely reflects a detector actually trained for the task. The out-of-domain sp we can measure (92.6% roberta, 91.6% feature baseline) is not directly comparable to NORC's out-of-domain se figure — different quantity (specificity on human text vs. sensitivity on machine text) — but it's a useful independent finding for the deletion-selection story: on real personal-essay text, the false-positive rate isn't dramatically worse than on HC3's Reddit/QA-style human text, at least for these two detectors.

## 2. r_F empirical anchor (lane 1 Q6)

Code: `analysis/fluency_anchor.py`, results in `analysis/fluency_r_f_results.json`.

**Constraint used exactly as given**: the local essays mirror has binary, median-split Big Five labels only (`cEXT`/`cNEU`/`cAGR`/`cCON`/`cOPN`, each `y`/`n`), not continuous BFI scores. Continuous scores live on the IEEE DataPort original, which requires an IEEE login to download — getting that account is Abhay's call, not something to script around (see `TESTBED-REPORT.md` Day 1 open items). Every correlation below is therefore a **point-biserial correlation** between a continuous fluency proxy and the binary trait label the local data actually has, on all 2,467 essays.

Fluency proxies used (no continuous BFI available, so no calibrated readability formula — these are surface fluency/disfluency signals suited to unedited stream-of-consciousness text): average word length, type-token ratio, average sentence length, punctuation rate, and filler-word rate (um/uh/like/you know/i mean/sort of/kind of/kinda/basically/actually/literally — counted per 100 words). Also a composite (mean of z-scored ttr, sentence length, and negative filler rate).

Composite-fluency vs. trait, all 5 traits:

| trait | r (point-biserial) | p |
|---|---|---|
| cEXT | −0.017 | 0.399 |
| cNEU | −0.053 | 0.009 |
| cAGR | −0.007 | 0.718 |
| cCON | −0.010 | 0.638 |
| cOPN | 0.018 | 0.372 |

Individual proxy strongest signal: **openness (cOPN)** correlates positively with type-token ratio (r = 0.071, p < 0.001) and with punctuation rate (r = 0.071, p < 0.001) — the most theoretically expected pattern (openness ↔ lexical/stylistic richness) and the only one that's both significant and directionally sensible across two independent proxies. **Conscientiousness (cCON)** correlates negatively with filler-word rate (r = −0.073, p < 0.001) — also expected (fewer disfluencies for more conscientious writers).

**Headline r_F for lane 1**: use |r| ≈ 0.05–0.07 as the empirical anchor magnitude (composite: 0.053 on cNEU; individual proxies up to 0.073 on cOPN/cCON), **explicitly as a lower bound**. Two things compress this number below the true continuous fluency-trait correlation: (a) median-split binary trait labels attenuate correlation magnitude relative to continuous BFI scores (a well-known dichotomization effect), and (b) these are surface stylometric proxies for fluency, not a validated fluency/readability instrument. If the deletion-selection derivation needs a less-attenuated anchor, that requires either the continuous BFI scores (IEEE login) or a better fluency instrument — flagging both as Day 3+ candidates, not blocking today's deliverable.

## 3. rho_v measurement plan (lane 1 Q7)

Full design rationale is in the docstring of `measurement/rho_v_plan.py` — summary here.

**What it measures**: rho_v is the average residual correlation between items among machine-authored responses, after removing the fitted trait signal — the empirical target for SPEC's H2 homogenization prediction (between-item correlations inflate among machine cases).

**The confound it isolates**: a nonzero rho_v could come from genuine coupling (the model sees the same respondent-level signal for every item) or from a same-session artifact (all of one respondent's items generated inside one LLM conversation share hidden generation state — persona drift, stylistic momentum — regardless of coupling level). These need to be told apart before lane 4 treats rho_v as a coupling-c property.

**Two arms**, once counterpart generation runs:
- `same_session`: generate all k item responses for a respondent inside one LLM call.
- `independent_calls`: generate each item response via its own stateless call, same coupling condition, no shared context.

**Procedure**: score each response into a numeric item indicator (the same scoring pipeline used for human responses) → fit a per-item baseline against the trait input the generator saw (linear regression against persona-band/exact score at partial/high coupling, item mean at c=0) → residual = observed − fitted → rho_v = mean off-diagonal item-residual correlation, computed separately per arm → bootstrap over respondents for a CI on each arm and on the same_session − independent_calls difference (the session-artifact estimate).

**Code**: `measurement/rho_v_plan.py` implements `GenerationRecord`, `compute_rho_v`, `bootstrap_rho_v`, `compare_arms`, and defines the exact schema the (not-yet-run) generation batch must emit. It ships with a synthetic self-test — data built with a known injected session-state correlation of 0.4 — that verifies the pipeline recovers it: `independent_calls` rho_v ≈ −0.006 (expected ~0), `same_session` rho_v ≈ 0.292 (expected > 0), session-artifact estimate ≈ 0.298. Run `python3 measurement/rho_v_plan.py` to reproduce. **No real generation was run** — this only validates the measurement code against synthetic data with a known-true answer, per the constraint for today.

## 4. Testbed freeze

`freeze_testbed.py` writes `testbed_freeze.json`: verified HC3/essays counts, license notes, the full detector calibration results, the fluency r_F results, and SHA-256 fingerprints of every data file lane 4 should code against.

| file | sha256 |
|---|---|
| data/hc3/all.jsonl | `ee231f82283d754050a4dc58ecf9331afaf5daea7283c6da0b096ed0fb2774cf` |
| data/hc3/finance.jsonl | `72e3a439714c4693e115f8ad0b917988688abc07acba8de812198cb13cd5d72e` |
| data/hc3/medicine.jsonl | `7141b0f5b3477543e95e24a2b268f46c375b08703a390e9a04ff69f5193caa28` |
| data/hc3/open_qa.jsonl | `4d968e1e1473cbdf5978024872768f0c6f27dacf681f35166dc191733dccd664` |
| data/hc3/reddit_eli5.jsonl | `448cebaf7fdf27560daf6cc87cc1464be4988cf8110c0ec40c40b21c2c0193db` |
| data/hc3/wiki_csai.jsonl | `4f78105c72e7edd3b619b3b44abac1e6f8bdb42211f22e43191d4dae889e1968` |
| data/essays/essays.csv | `3e0ec809f1ca98c6ecdd15b688af4006a28931e226537619fc414238c3f7bc7f` |

If any lane 4 result stops matching what's in `testbed_freeze.json`, re-run `freeze_testbed.py` and diff the hashes first — a changed hash means the underlying data file moved, not that lane 4's code is wrong.

## Environment additions since Day 1

`lane3-testbed/.venv` gained: `scikit-learn`, `torch` (CPU wheel, ARM build, 121MB), `transformers`. Detector model weights (`openai-community/roberta-base-openai-detector`) cached under `~/.cache/huggingface`, not committed to the repo.

## Open items for Day 3+

1. Out-of-domain **se** for both detectors is still unmeasured — needs the LLM counterpart generation batch (gated on the burn report). Re-run `detector/calibration.py`'s essays block once machine-authored essays exist.
2. r_F anchor is a lower bound (binary labels + surface proxies). If lane 1's derivation is sensitive to the exact magnitude rather than sign/order, the continuous-BFI IEEE DataPort login is the next lever — Abhay's call, not scripted around here.
3. `rho_v_plan.py`'s two-arm design assumes the generation batch actually supports both `same_session` and `independent_calls` calling patterns; confirm with whoever specs the generation batch that both are feasible before freezing the batch design.
