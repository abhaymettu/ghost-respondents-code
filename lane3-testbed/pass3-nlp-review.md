# Pass 3 — adversarial NLP review

**Verdict: BLOCK.** The strongest mechanism result is numerically false, a machine corpus is repeatedly described as a human negative control, and the live Layer B loader still consumes the leaky chunk scores. The evidence supports a narrower failure of the current scoring/correction setup; it does not establish the claimed impossibility of recovering trait reliability from text.

Reviewed 2026-09-09: all five requested lane 3 reports; their scoring, loading, calibration, and fluency code and saved data; `INJECT.md`, all three requested Layer B reports and their relevant consumers; and SPEC §2. Source locations below are repository-relative and refer to the files inspected, including historical reports whose implementations have since changed. No scientific code, source data, or simulation results were changed by this review.

Reproduction: from the repository root, run:

```sh
PYTHONDONTWRITEBYTECODE=1 lane3-testbed/.venv/bin/python lane3-testbed/analysis/pass3_nlp_checks.py
```

The saved output is `lane3-testbed/analysis/pass3_nlp_results.json`. It includes input hashes, verified row alignment, two independent partial-correlation calculations, a live loader check, tokenizer counts, HC3 split reconstruction, and descriptive detector transfer estimates. The script uses the existing local environment and cached tokenizer; it does not refit models or download anything. The tokenizer warning concerns measuring untruncated sequence lengths, not feeding overlong sequences into a model.

## BLOCKER findings

### B1. The “0.0% removed” partial-correlation result does not reproduce

**Location:** `lane3-testbed/WEAK-H2-DIAGNOSIS.md:117–161`, propagated into §2.7 and the verdict at lines 236–261.

**Claim:** controlling for each trait label leaves every chunk-pair correlation unchanged to four decimals; the label therefore explains none of the agreement. The report explicitly makes this its strongest evidence and its proof sketch.

**Counter-evidence:** the saved `labels` are numeric 0/1. Restricting all variables to the same 2,421 complete-chunk essays, regressing each OOF chunk score on an intercept and its numeric label, then correlating residuals gives:

| Trait | Raw mean pair r | Partial r, label | Relative reduction in r | Partial r, length + label |
|---|---:|---:|---:|---:|
| cEXT | 0.206778 | 0.198191 | 4.15% | 0.185030 |
| cNEU | 0.213103 | 0.205443 | 3.59% | 0.197655 |
| cAGR | 0.175856 | 0.170981 | 2.77% | 0.170498 |
| cCON | 0.200527 | 0.197434 | 1.54% | 0.194062 |
| cOPN | 0.277998 | 0.251276 | 9.61% | 0.247840 |

The closed-form partial correlation `(r_xy-r_xL*r_yL)/sqrt((1-r_xL²)*(1-r_yL²))` reproduces the residualization results within 1e-12. The raw and length-only values reproduce the report, isolating the contradiction to its label adjustment. Every chunk has a nonzero positive empirical correlation with its label. After length + label adjustment, EXT and OPN retain about 89.5% and 89.2% of raw r, contradicting the “>93% in every trait” claim as well. These percentages describe changes in correlation, not a causal decomposition of variance.

**What survives:** substantial residual agreement remains; correcting this error does not make weak-H2 succeed. But “most remains” cannot support “orthogonal to the construct” or the purported proof. No executable script for the original diagnosis's partial-correlation calculation was found in lane 3, so its precise implementation error is unverified. A constant/misdecoded control could produce this symptom, but that is a hypothesis, not an established cause.

**Required:** replace both partial-correlation tables, withdraw the zero-signal proof and dependent elimination claims, and retain an executable calculation with assertions on label variance and row alignment.

### B2. Big5PersonalityEssays is machine-generated, not the reported human negative control

**Location:** `lane4-simulation/LAYERB-SWEEP.md:43–45, 197–199, 272–274`; `LAYERB-ROUND3.md:249–252, 331–334`. The misclassification changes the explanation of results in all subsequent references to the “essays” control.

**Counter-evidence:** `lane3-testbed/CORPUS-AUDIT.md:9–18` already identifies the exact downloaded workbook and GPT-4-turbo generator. The [source repository](https://github.com/stnflri/Big5PersonalityEssays) identifies its essays as generated with GPT-4-turbo, and the [dataset paper](https://arxiv.org/abs/2407.17586) describes synthetic essays. The local workbook contains 399 usable rows, and none exactly matches a PK essay after lowercasing and whitespace normalization. That overlap check is corroboration; authorship is established by provenance, not by text appearance or detector score.

The live loader correctly places this pool in the machine slot (`inject/pools.py:692–696`). Its AUC ≈0.472 and near-zero sensitivity are consequently **detector failures on actual synthetic text**, not a successful negative control on humans. The reports dismiss precisely the low-detectability machine corpus needed to characterize the method's boundary. A detector output cannot validate the gold authorship label it is being evaluated against.

**What survives:** the numerical mixture calculations need not change solely because of this prose error; the code already treats the pool as machine. A human negative control would be useful, but this corpus is not one.

**Required:** correct the provenance and all affected interpretations, count this pool among machine-domain failures, and remove the claimed human-control result unless a genuine disjoint human corpus is evaluated.

### B3. The OOF repair never reached the live Layer B chunk loader

**Location:** `lane3-testbed/CHUNK-REFIT.md:30–38`; `lane4-simulation/inject/pools.py:628–666, 723–724`; `LAYERB-SWEEP2.md` Part III.

**Counter-evidence:** the repair added `chunk_1_oof` through `chunk_4_oof` while deliberately preserving the old columns. `_lane3_chunks()` still unconditionally reads `chunk_meta` and `chunk_{j}`, with no OOF option. Calling `lane3_pool('pk_human','EXT')` today gives a maximum difference of **0.0** from the original scores and **0.592864** from the repaired scores. Its full-pool mean between-chunk r is **0.208311**, the in-sample baseline, not the repaired **0.206778**.

**What survives:** lane 3's OOF columns exist and its direct OOF calculation is distinct from this consumer failure. The historical sweep explicitly disclosed leakage. The problem is treating the repair as completed across the pipeline or rerunning Layer B and expecting repaired results.

**Required:** route the multi-item pipeline to an explicit scoring-version choice, require OOF human scores for confirmatory runs, record that version in result provenance, and rerun the affected k=4 results. Existing historical numbers must remain marked as in-sample. A matching whole-pool r is not sufficient verification of the score source.

## MAJOR findings

### M1. “Full-length” scoring discards most essay content; scorer adequacy is untested

**Location:** `lane3-testbed/pool_measurement.py:66–88, 154–183`; `POOL-MEASUREMENTS.md:9–14, 135–158`; `CHUNK-REFIT.md:59–62`; `chunk_scoring.py:45–76`.

**Counter-evidence:** the pipeline calls `SentenceTransformer('all-MiniLM-L6-v2').encode()` without document pooling or a sequence-length override. The cached model's `sentence_bert_config.json` sets **256 tokens**, consistent with the [model card's stated 256-wordpiece truncation and short-paragraph use](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2). Tokenizing the actual PK inputs yields:

- **2,433/2,467 essays (98.62%) exceed 256 tokens.**
- Median input length is **759 tokens**, including special tokens.
- The prefix encoder retains **32.15% of total content tokens**, counting at most 254 content tokens per essay.

Thus the purported full-text baseline is predominantly a prefix score. The 190-word comparison is often close to that same token budget; it does not validate full-document length effects. Four separately embedded chunks can expose later content the whole-text embedding never sees. Equal sentence counts also do not imply equal word/token lengths, and the punctuation regex is not a validated sentence segmenter for these unedited essays. Claims that a quarter-text scorer *cannot* outperform a whole-text scorer are false even without leakage: irrelevant content, pooling, and truncation can all reverse that ranking.

**Literature comparison:** Mairesse et al.'s essay regression results report Pearson r **0.24 for emotional stability and 0.33 for openness**, with weak results on other traits; see [§5.1, pp. 24–25 of the linked manuscript](https://sites.socsci.uci.edu/~lpearl/courses/readings/MairesseEtAl2007_PersonalityCues.pdf). Those are continuous self-report targets, whereas this pipeline uses binary labels. Under the illustrative assumptions of a normal latent trait, an exact median split and a linear conditional score mean, dichotomization multiplies r by `sqrt(2/pi) ≈ 0.798`: the comparison becomes roughly 0.19 and 0.26, not a universal target. Local NEU 0.102 is notably weaker; OPN 0.227 is closer. Neither comparison proves the local model is optimal or broken.

More recent work explicitly models which text carries personality signal; [Lynn et al. (ACL 2020)](https://aclanthology.org/2020.acl-main.472/) uses hierarchical word/message attention, on a different social-media corpus. Its metrics are not an interchangeable PK benchmark. It establishes a relevant modeling alternative, not a numeric ceiling for these essays.

**Assessment:** r_H in 0.07–0.23 is compatible with a difficult binary personality task and a weak baseline. It is not evidence of an intrinsic information limit. A semantic-similarity encoder plus fixed-alpha linear head lacks explicit coverage of function-word frequencies, lexical diversity, syntax, discourse structure and trait-specific aggregation; it may encode some of them, but no ablation establishes how well. Scorer error directly inflates `rbar/r_H²` and changes measured coupling.

**Required:** disclose prefix coverage; compare matched-fold full-document aggregation and a lexical/stylometric baseline, with hyperparameters selected inside training folds. Before broad construct-validity conclusions, include a stronger document/personality scorer or narrow all conclusions to this fixed prefix-ridge scoring instrument. Preserve the existing scorer as a baseline.

### M2. Text-ID disjointness does not establish an independent scoring/calibration evaluation

**Location:** `pool_measurement.py:71–88, 162–183, 227–245`; `chunk_scoring_oof.py:91–111`; `lane4-simulation/sweep_layerb.py:90–106`; `inject/pools.py:413–445`.

**Counter-evidence:** PK scoring models are fitted before the later Layer B reference/injection split. Each PK observation's own label is withheld, but a reference observation's scoring model includes labels of other observations in the survey base, and vice versa. On the live frozen EXT split, each fold model contains **972–996 base labels and 977–1,002 reference labels**. Machine whole-text scores come from a full-PK refit, which includes all survey-base labels. This is not an externally trained, frozen scorer evaluated against independent calibration and survey sets.

There is a second comparability problem: human whole-text scores use one 80%-trained fold model per row; machine scores use the 100% refit. Human OOF chunks use one fold model; machine OOF chunks average five models. Training size and ensemble variance differ by authorship. Machine/human variance ratios and mean gaps can therefore partly reflect scoring procedures rather than text generation.

**What survives:** the own-row OOF protection is real. Frozen pretrained embeddings computed in a batch are not themselves supervised leakage; no fold-fitted standardizer/PCA was found in this scoring path. Conditional simulations on fixed scores are legitimate, and their moment identities remain conditional identities. The unchecked leap is to independent-population validation and uncertainty that includes scorer estimation.

**Required:** introduce an outer split for scorer training, calibration/reference, and evaluation; fit learned preprocessing inside training; apply the same fitted scoring rule to both authorships. Alternatively, explicitly scope the results to the finite, pre-scored corpus and omit claims of independent external validation. Quantify the asymmetric-scoring effect before interpreting kappa as homogenization.

### M3. HC3 calibration splits answers, not question pairs

**Location:** `lane3-testbed/detector/calibration.py:61–90`; `CALIBRATION-REPORT.md:12`.

**Counter-evidence:** `sample_hc3_pairs()` flattens each question into two rows, discards question identity, then shuffles. `split_calibrate_test()` shuffles those individual answers again. Exact reconstruction of the seeded sampling shows **622/1,250 questions straddle calibration and test**; 622 of 1,250 test answers have their paired answer in calibration. Sampling is balanced by source, but the subsequent split is not grouped by question or explicitly stratified.

**What survives:** the exact same row is not deliberately reused, and RoBERTa is pretrained and only threshold-tuned here. This is not proof of a large numeric optimism bias. However, related answers share topic and prompt, and the feature baseline is fitted on the calibration answers, so the reported held-out test is not a new-question test. Its uncertainty also ignores pair clustering.

**Required:** retain question IDs, split by question with source/class checks, and recompute the held-out operating points. Distinguish new answers, new questions, and new domains in the report.

### M4. P1 controls assignment covariance, not what a respondent tells an LLM

**Location:** `lane4-simulation/INJECT.md:21–29, 177–185, 210–222`; `SPEC.md:48–55, 87–89`; `LAYERB-SWEEP2.md:295–302`.

**Counter-evidence:** varying p rematches already conditioned texts to a binary respondent label. At p=0 the *recipient label* is independent of the assigned score, but the original text was still generated under a persona prompt. This is not the same intervention as removing personal information from a prompt. At p=1 the recipient shares one binary trait pole with the source persona; there is no respondent-specific draft, biography or continuous BFI score in the generation process. [PersonaLLM](https://arxiv.org/abs/2305.02547) evaluates simulated personas through BFI and story writing, not actual respondents outsourcing these survey answers.

The invariance of kappa, delta and marginal detector distribution in p is enforced by the assignment design. Real prompt disclosure can alter length, style, specificity, content and detectability as well as covariance. Matching one trait at a time does not preserve an individual's joint five-trait profile. Sampling with replacement adds repeated realizations of a small existing pool; it does not add independent prompts, authors, or generation sessions. Agreement of replacement schemes on a moment is not empirical validation of a respondent-farm model.

**What INJECT answers:** it clearly explains assignment coupling, synthetic outcomes, and the binary-label estimand. That licenses a controlled finite-pool experiment. Its §7a disclosure addresses outcome realism but does not resolve the generation-intervention mismatch. Exact moment checks validate the sampler, not the construct interpretation.

**Required:** name the arms “random/matched text assignment,” and state that they are not empirical c=0/partial/high prompt-disclosure arms. Limit ecological claims to scored text marginals. To claim respondent-level outsourcing validity, add prompt-matched generations with independently varied disclosure and separately generated references, or direct data from such behavior.

### M5. Detector transfer is partly measured, but the published benchmark and transfer claims are wrong

**Location:** `SPEC.md:59`; `CALIBRATION-REPORT.md:17–29, 89`; `detector/calibration.py:231–235`; `LAYERB-SWEEP.md:175–192`; `sweep_layerb.py:120–134`.

**Counter-evidence to the brief's premise:** Layer B does **not** simply reuse HC3 se/sp. It sets a threshold at the PK-human reference's 0.99 quantile, measures sensitivity on a held-out essay-pool reference, and evaluates the other halves. The sweep documents GPT-4 sensitivity 0.219–0.269, GPT-3.5 0.100–0.119 and Llama-2 0.562–0.637 at that operating point. Thus there is essay-domain calibration evidence on disk; “all transfer is assumed” would be an incorrect finding.

What is missing is a clearly separated account of fixed-HC3-threshold transfer versus essay recalibration versus external-domain deployment. Using the saved detector scores at the actual HC3 threshold **0.7536994815**, this review obtains:

| Corpus | n | Fixed-HC3-threshold rate |
|---|---:|---:|
| PK humans | 2,467 | specificity 0.9473 |
| Big5PersonalityEssays, GPT-4-turbo | 399 | sensitivity 0.0075 |
| PersonaLLM GPT-4 | 320 | sensitivity 0.5000 |
| PersonaLLM GPT-3.5 | 320 | sensitivity 0.3344 |
| PersonaLLM Llama-2 | 320 | sensitivity 0.8188 |

These are descriptive full-pool transfer checks, not new independent test sets. The 0.9473 specificity uses all PK essays and therefore need not equal the earlier 500-essay estimate 0.926. The large sensitivity differences show why no single “mid-80s” essay operating point is warranted.

The NORC source is also misread. [Huang et al., AAPOR 2025, slide 7](https://www.norc.org/content/dam/norc-org/pdf2025/AAPOR%20Detecting%20AI-Generated%20Survey%20Responses%20-%20Lilian%20Huang.pdf) reports general-population precision 0.989, recall 0.999, accuracy 0.990; technical-domain **accuracy in the upper 80s to mid 90s**, precision **up to 85.7%**, and recall **up to 100%**. It does not supply an out-of-domain sensitivity of approximately 0.85. The code's `out_of_domain_se_ballpark` and the calibration report's comparison conflate metrics.

**What survives:** the report correctly identifies the detector as GPT-2-trained and initially distinguishes measured OOD specificity from unavailable sensitivity. Later corpus scores permit more measurements. Same-corpus held-out calibration is useful, but it does not establish transfer across new survey prompts, populations, generators or editing practices; AUC cannot replace a specified se/sp operating point.

**Required:** correct the NORC attribution, publish separately labeled transfer/recalibration tables with uncertainty and provenance, and validate externally or limit deployment claims to the tested essay pools.

### M6. Freezing a split improves repeatability; it does not remove split uncertainty or domain drift

**Location:** `WEAK-H2-DIAGNOSIS.md:70–79`; `LAYERB-ROUND3.md:222–237, 270–307`; `inject/pools.py:448–485`.

**Counter-evidence:** a fixed KFold seed conditions on a fitted scorer; it cannot prove its correlations would be unchanged under another fold assignment or a different training sample. Reproducing a split to zero difference establishes repeatability. Shared fold-specific scoring effects can also enter correlations among chunks of the same document. The diagnostic never reruns scorer folds to rule this out.

For repeated surveys, the report's cancellation `b(pi)=b0+b1*pi` assumes the human and machine conditional text distributions stay fixed across waves. Changing prompt, respondent composition, generator or editing behavior can change sensitivity/specificity and the offset despite identical calibration IDs. No empirical multi-wave text-shift test is reported.

Even under the fixed-pool experiment, the “mean zero” wording contradicts the table: GPT-3.5/AGR has mean offset **0.0287**, SD **0.1386** over 400 splits. Its approximate Monte Carlo SE is 0.00693, making the mean about **4.1 SE from zero**. Comparing a mean to the SD of individual draws does not establish zero mean. The table's mean b1 of **0.1186** is also not unbiased change recovery. “The sign is never at risk” overstates a calibration-only calculation and omits survey sampling variability.

**What survives:** reusing calibration is a sensible paired design under stable conditional distributions. The report's 54% split-variance analysis is direct evidence that split uncertainty matters. Neither implies freezing is a validity guarantee. The pool-name RNG is stable for a given trait/data ordering; because the split stratifies by trait labels, the same pool has different held-out IDs across traits, which should be recorded rather than inferred from its name.

**Required:** keep the frozen operational split, report sensitivity across scorer/calibration splits, distinguish conditional from unconditional uncertainty, and limit the between-wave claim to stable distributions pending a shift experiment. Correct the zero-mean and guaranteed-sign claims.

### M7. Residual chunk agreement does not identify its cause or prove structural impossibility

**Location:** `WEAK-H2-DIAGNOSIS.md:81–115, 163–190, 225–261`; `LAYERB-SWEEP2.md:174–190, 251–265`.

**Counter-evidence:** beyond B1, the elimination logic is not identifying:

- A binary label leaves within-band variation in the continuous trait. Even perfect control for that binary variable cannot remove all shared continuous-trait signal. Calling `r_H²` “true reliability” is a definition of this label-based simulation target, not validation of latent BFI reliability.
- Higher chunk variance does not rule out weaker trait signal mixed with more nuisance variance. Pure linear score compression does not change Pearson correlation at all.
- A lower average cross-trait correlation does not rule out same-trait, document-shared scoring error. Correlated trait predictions are not automatically “leakage”; the labels themselves may correlate.
- No adjacent/nonadjacent difference, without an uncertainty analysis, does not identify a single global stylistic factor. A diffuse trait, topic or scorer factor could each produce it.
- Topic, syntax, register and word choice can be personality indicators. Declaring them unrelated to personality is precisely the hypothesis that needs validation.

Splitting one text makes independent-error parallel forms doubtful, not logically impossible. Conversely, multiple texts from different sittings are not automatically parallel forms: loadings, content and residual dependence still require testing. An oracle correction that reuses the simulation's defining label/outcome relation validates arithmetic, not construct validity or a deployable “single-item route.”

**What survives:** raw chunk agreement is a poor replacement for squared label validity in the tested instrument. Substantial residual agreement is consistent with document-specific nuisance, and the failure remains after own-row OOF scoring. The supported conclusion is **weak-H2 is not established by this experiment**. “Not recoverable at any n or pi,” “by construction,” and “quantitative confirmation” of a unique nuisance mechanism go beyond the evidence.

**Required:** rewrite as a scoring- and corpus-conditional failure; retain the binary-label limitation in the conclusion; test proposed nuisance mechanisms rather than declaring them identified by elimination.

### M8. The fluency proxy is not a validated lower bound on the deletion mechanism

**Location:** `CALIBRATION-REPORT.md:35–51`; `analysis/fluency_anchor.py:15–31, 54–59, 108 onward`.

**Counter-evidence:** the composite combines type-token ratio, sentence length and negative filler count without independent fluency validation. The regex counts every occurrence of “like,” including preference and comparison uses. Type-token ratio depends on text length. Taking the strongest observed correlations across traits/proxies and calling their absolute values a lower bound has no general measurement-error guarantee: nuisance correlations and selection among estimates can increase as well as decrease the observed magnitude.

Nor does a proxy–label correlation establish the required detector–proxy–trait selection pathway. The cited [NORC slides 13–17](https://www.norc.org/content/dam/norc-org/pdf2025/AAPOR%20Detecting%20AI-Generated%20Survey%20Responses%20-%20Lilian%20Huang.pdf) describe misclassified humans as writing longer responses with higher reading levels; they do not establish the assumed low-fluency direction for this detector and corpus.

**What survives:** the point-biserial descriptive correlations are useful and their small size is disclosed. **Required:** label them exploratory proxy associations, remove “lower bound,” and measure detector errors against a validated fluency measure and the target traits before claiming this empirically anchors the deletion mechanism.

## MINOR findings

### m1. The refit's “at most 7%” summary and one direction are wrong

**Location:** `CHUNK-REFIT.md:109–110`; repeated at `WEAK-H2-DIAGNOSIS.md:3–5`.

**Counter-evidence:** AGR rises from 14.44 to 15.66, about **8.45%**; OPN falls from 5.72 to 5.41, although the prose names OPN as increasing. Also, `CHUNK-REFIT.md:51–54` says n=2,421 throughout while its whole-score validity comes from the n=2,467 baseline; the complete-case EXT whole validity is approximately 0.1646, not 0.1596. **What survives:** the ratio remains large. **Required:** correct the percentages/direction and report numerator/denominator sample sizes consistently.

### m2. SPEC's actual-data description remains stale

**Location:** `SPEC.md:46`; `TESTBED-REPORT.md:39–48`.

**Counter-evidence:** the acquired corpus has **2,467 essays, 1,608,813 whitespace-counted words, and binary labels**, not the described 2,479/1.9M/continuous-score resource. The report discloses these differences but attributes the word deficit to tokenization without demonstrating that explanation. An unfetched mirror does not establish that continuous BFI is available there. **What survives:** the downloaded corpus is a documented, usable binary-label testbed. **Required:** describe the acquired data exactly and mark release/tokenization/continuous-score provenance as unresolved rather than explained.

### m3. The reported g correction is not reproducible from the named measurement script

**Location:** `POOL-MEASUREMENTS.md:16–19, 316–345`; `pool_measurement.py:245`.

**Counter-evidence:** the report's appended correction and stored measurement table use the covariance ratio, but both the opening definition and the executable scoring script still use `chat_r/r_H`. Rerunning the named script recreates the old value in its output. **What survives:** Layer B computes its own covariance-consistent quantity, so this is not evidence that the current Layer B result uses the stale formula. **Required:** reconcile code, opening definition, and generation of the corrected artifact; record the pipeline that produces the published table.

## NOT-A-FINDING — rejected attacks

### N1. All other pools necessarily leaked into PK training

**Location:** `CHUNK-REFIT.md:13–22`; `pool_measurement.py:162–183, 205–238`.

The supervised training corpus is PK. The scored PersonaLLM pools are the generator directories, not its `human_stories` directory. The report's 185 matching human stories (`POOL-MEASUREMENTS.md:174–189`) therefore do not establish train/test overlap in these machine pools. B2 also rules out treating Big5PersonalityEssays as another PK release. No cross-pool supervised text overlap was demonstrated here. Own-row OOF hygiene, nested evaluation and scorer asymmetry are separate issues addressed above.

### N2. A frozen pretrained encoder necessarily leaks through joint preprocessing

**Location:** `pool_measurement.py:66–81`.

Batch encoding with a fixed pretrained model does not fit to held-out labels. No corpus-fitted scaling, PCA or representation adaptation appears before this KFold routine. This review does not establish PK pretraining contamination either. The verified defects are truncation and evaluation design, not an invented preprocessing leak.

### N3. Essay-domain detector calibration is wholly absent

**Location:** `LAYERB-SWEEP.md:175–192, 214–251`; `sweep_layerb.py:120–134`.

Essay reference thresholds, sensitivity, specificity and transfer offsets are present and measured. They contradict a blanket “HC3 rates assumed on essays” criticism. M5 identifies the narrower, supported problems: mistaken metric attribution, incomplete reporting of fixed-threshold transfer, and lack of external deployment validation.

## Verdict and release conditions

**BLOCK.** Before shipping the NLP evidence:

1. Correct the false partial-correlation result and its dependent mechanism verdict; correct the synthetic corpus's authorship and detector interpretation.
2. Connect OOF scores to the actual Layer B consumer and regenerate affected multi-item evidence with explicit scoring provenance.
3. Resolve or explicitly scope the prefix-only representation, asymmetric scoring and nested evaluation problems. A finite-pool, fixed-scorer demonstration must not be presented as a validated continuous-trait measurement system.
4. Repair question-level HC3 evaluation and the NORC metric attribution; report essay calibration separately from external transfer.
5. Restrict P1 claims to assignment coupling and fixed-pool sampling unless actual prompt-disclosure generation is validated. Restrict frozen-wave claims to stable conditional text distributions and include calibration/sampling uncertainty.
6. Replace structural-impossibility and fluency-lower-bound assertions with conclusions supported by the measurements; reconcile the reproducibility and data-description inconsistencies above.

The algebraic simulation may remain useful. The current NLP evidence cannot support the stronger construct-validity, detector-generalization, and mechanism claims attached to it.
