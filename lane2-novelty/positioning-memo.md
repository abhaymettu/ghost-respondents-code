# Lane 2 positioning memo — novelty verification gate

## Verdicts

- **arXiv 2604.11581 (Messing, "Hidden Measurement Error in LLM Pipelines")**: **NO.** Does not do the respondent-side mixture correction. The paper's entire object is LLM-as-annotator/judge/benchmark pipeline variance (item × prompt-variant × temperature × model × replicate), decomposed via a mixed-model "Total Evaluation Error" (TEE) framework (Sections 3–3.3, pp. 3–4, Eq. 1–2). There is no respondent, no survey-taker, no authorship variable, and no mixture-of-measurement-processes model of a *sample* — the "mixture" of interest here is variance components within one automated scoring pipeline, not human-vs-machine authorship of the underlying data. Confirmed by full-text search: zero hits for "respondent," "authorship," "contamina[te]" (beyond benchmark train/test leakage), "mixture" (one unrelated hit about refusal/compliance responses, p. ~30), and zero hits for "validity coefficient." Related Work (Section 2, pp. 2–3) and Limitations (Section 6, p. 8) situate the paper entirely within LLM-evaluation/benchmarking measurement error, generalizability theory, and total survey error *as a borrowed analogy for coverage error*, not as a treatment of AI-contaminated survey respondents.

- **SMR 2025 preprint (Zhang, Xu, Alvero, "Generative AI Meets Open-Ended Survey Responses")**: **NO.** Descriptive only, no correction estimator. Section 3–5 (pp. 8–32) report self-reported LLM-use prevalence (34%) from an original Prolific survey and document homogenization/sentiment/dehumanizing-language differences between human (TESS, pre-ChatGPT) and LLM-simulated responses. Section 6, Conclusion (pp. 33–40), explicitly frames "developing methods and standards for detecting, monitoring, and managing AI-influenced writing products" as future work (p. 40) and recommends practical mitigations — pretesting, discouraging AI use, sensitivity analyses, detection-based filtering with an explicit warning that filtering "may raise similar issues as traditional attention checks... introducing selection bias" (p. 37) — but derives no bias formula, no validity-coefficient correction, no mixture measurement model, and no prevalence *estimator* (their 34% is a survey self-report, not a label-free statistical estimate from response text). Full-text search confirms zero hits for "mixture," "correction," "validity coefficient," or "estimator" in a methodological sense. Notably, the paper's own selection-bias caution about detection-based filtering (p. 37) is consistent with, not competing with, this project's deletion-selection (collider) result — it flags the problem but does not formalize or prove it.

**Neither paper does the respondent-side two-process mixture model with a coupling parameter, label-free prevalence estimation with validity-coefficient correction, or the deletion-selection bias proof. No overlap found; proceed.**

---

## 1. Claim-by-claim diff

### (a) Respondent-side two-process mixture model with coupling parameter c

| Source | Coverage |
|---|---|
| Messing 2604.11581 | None. Models pipeline stages (item, prompt-variant, temperature, model, replicate) as crossed random/fixed effects (Eq. 1, p. 3). No authorship variable, no human/machine measurement-process split, no coupling parameter. |
| SMR 2025 | None. Documents empirical divergence (homogeneity, sentiment, vocabulary) between human and LLM-simulated text (Sections 5.1–5.5, pp. 15–32) but never formalizes this as a statistical mixture of measurement processes with a continuous coupling parameter analogous to this project's c. Their LLM simulations are unconditioned (generic prompts observed from real users, Section 4.3, pp. 18–19) — closer to this project's c = 0 case only, with no partial/high-coupling analog and no formal model of it. |
| Psychometrika (abstract only) | Partial adjacency, different object. Its "manual vs. automatic" is human-rater vs. machine-*scorer* of the same response, not human-vs-machine *authorship* of the response. No coupling parameter; error rates (CER/VER) attach to classification of an already-human-written answer, not to how much of the response content the machine independently generated. |

**Gap confirmed on all three.**

### (b) Label-free prevalence estimation plus validity-coefficient correction

| Source | Coverage |
|---|---|
| Messing 2604.11581 | None on prevalence-of-authorship. The paper's "prevalence" usages (pp. 1805–1864 in extracted text) refer to Likert-pathology/scoring-method robustness at varying label-class prevalence in an unrelated judge-scoring simulation, not to estimating what fraction of respondents used AI. No validity-coefficient correction anywhere in the text. |
| SMR 2025 | Prevalence reported (34%) is a self-report survey estimate, not a label-free statistical estimator from response distributions. No errors-in-variables or classify-and-count/quantification apparatus; no validity-coefficient correction. |
| Psychometrika (abstract) | Addresses classifier misclassification of scores (false-positive/negative rates on scoring, not authorship) inside an IRT ability-estimation model — mechanically adjacent (both correct for a fallible auto-classifier) but does not estimate class *prevalence* label-free, and its outcome is ability estimation, not a bias-corrected validity coefficient between a trait and an external outcome. |

**Gap confirmed on all three.** The quantification/prevalence-estimation literature (see Section 3 below) supplies label-free prevalence machinery in principle but has not been coupled to a validity-coefficient correction for a latent psychological construct.

### (c) Deletion-selection (collider) bias result against detect-and-delete

| Source | Coverage |
|---|---|
| Messing 2604.11581 | Not addressed; off-topic (benchmark contamination/train-test leakage only, e.g. p. 993, 1069, unrelated to detect-and-delete of respondent text). |
| SMR 2025 | Flags the *risk* qualitatively — "filtering... may raise similar issues as traditional attention checks... falsely flagging genuine human-written responses... introducing selection bias" (p. 37) — but does not formalize sensitivity/specificity, does not derive the collider structure (detector error correlated with the trait via fluency), and does not prove deletion is biased even at zero residual contamination. This is the single closest passage in either paper to this project's Claim (c), and it is a one-sentence caution, not an argument or a result. |
| Psychometrika (abstract) | Not addressed; the model corrects for classifier error in scoring, it does not analyze deletion/filtering of flagged cases or selection-induced bias on the latent trait. |

**Gap confirmed on all three; SMR's p. 37 caution is the nearest precedent and should be cited as motivating prior concern, not as prior art that must be distinguished away.**

---

## 2. Quantification / label-free class-prevalence literature scan

Web search (this session) surfaced the following as the relevant prior-art family for Claim (b)'s prevalence-estimation half. None couples to a latent psychometric construct or validity-coefficient correction:

- **Classify-and-Count (CC) and Adjusted Classify-and-Count (ACC)** — classical quantification baselines; ACC corrects CC's prevalence estimate using the classifier's confusion matrix. Directly relevant as the "distribution matching" mechanism SPEC 3.2 proposes, but applied historically to sentiment/topic classes, not authorship-of-survey-response with a downstream validity coefficient.
- **freq-e** (Card & Smith) — Bayesian class-prevalence estimation from a classifier's predicted probabilities: https://slanglab.cs.umass.edu/doc_prevalence/
- **Calibrate-Extrapolate** (arXiv 2401.09329) — rethinks prevalence estimation with black-box classifiers via calibration; recent (2024) and squarely in the CC/ACC family: https://arxiv.org/pdf/2401.09329
- **LeQua@CLEF2022** (arXiv 2111.11249) — shared task / survey framing "Learning to Quantify" as a field: https://arxiv.org/pdf/2111.11249
- **Multi-Label Quantification** (ACM TKDD, 2023): https://dl.acm.org/doi/10.1145/3606264
- **Quantification via Gaussian Latent Space Representations** (arXiv 2501.13638) — closest name-collision with "latent," but the latent space is an embedding representation for the classifier, not a psychometric latent trait: https://arxiv.org/html/2501.13638
- **Latent class models for prevalence estimation in disease screening with imperfect tests** (PMC2879599) — epidemiological analog with the same logical structure (estimate prevalence without a gold standard, using imperfect classifiers), but no coupling parameter, no validity-coefficient/outcome-correlation correction, different domain: https://pmc.ncbi.nlm.nih.gov/articles/PMC2879599/
- **Classical disattenuation / correction-for-attenuation** literature (Spearman; recent treatments at https://arxiv.org/pdf/2507.22218 "Attenuation Bias with Latent Predictors" and https://pmc.ncbi.nlm.nih.gov/articles/PMC4787301/ "Correcting for Measurement Error in Latent Variables Used as Predictors") — supplies the errors-in-variables half of Claim (b), well established, but never combined in the literature found with quantification-style label-free prevalence estimation of a human/machine authorship mixture.

**Assessment**: the two halves of Claim (b) — label-free class-prevalence estimation, and errors-in-variables correction of a validity coefficient using an estimated reliability/prevalence — each have deep independent literatures, but no source found in this scan combines them for respondent-side AI-authorship contamination of a psychometric construct. This is consistent with, not a substitute for, a fuller structured search; if the lane owner wants deeper coverage, run:

- `"quantification" "prevalence" "validity coefficient" psychometric` (Google Scholar)
- `"errors in variables" "class prevalence" latent trait correction` (Google Scholar)
- `"AI-generated" OR "LLM-generated" respondent contamination validity survey correction estimator` (Google Scholar, 2024–2026)
- `quantification learning psychometrics latent construct` (Google Scholar)
- `"detect and delete" selection bias survey AI screening collider` (Google Scholar) — targeted check for Claim (c) precedent beyond SMR's one-sentence flag

## 3. Psychometrika joint IRT paper — positioning note

Abstract-only (full text paywalled; WebFetch on the Cambridge page returned the abstract and model description, not the full article). The paper proposes two joint IRT models — Constant Error Rate (CER) and Variable Error Rate (VER) — for open-ended test items scored both by human raters and by an automatic (ML) classifier, extending IRT to marginalize over classifier misclassification so ability can be estimated from automatic scores alone. Under CER with a 2PL manual-score model, the marginal automatic-score model becomes a 4PL IRT model with extra parameters for the classifier's false-positive/false-negative rates.

**Positioning**: this is the closest adjacent machinery in the gate — a rater-mixture measurement model correcting for a fallible automated process — but it corrects *scoring* of human-written responses, not *authorship*. Its "automatic" is a scorer of the response, not a co-author or generator of the response content; there is no coupling parameter, no prevalence-of-authorship estimand, and no validity-coefficient-with-an-external-outcome correction (its target is ability estimation within the test, not Cor(theta, w) against an external criterion). This project should cite it as the nearest technical relative for framing (a mixture model over measurement processes, with error rates that may depend on the latent trait — directly analogous to this project's coupling parameter c and to the VER model's ability-dependent error) and note explicitly in the positioning section of the writeup that the CER/VER error-rate-depends-on-ability mechanism is structurally the same move as coupling c depending on the strength of the human-machine trait signal, applied to a different substantive problem (rater error vs. respondent authorship). Recommend requesting full text (institutional access or interlibrary loan) before the draft ships, to confirm no discussion-section remark anticipates the respondent-authorship extension.

DONE-LANE2-DAY1 — verdict: neither source paper contains the respondent-side mixture correction; no overlap found, proceed with all three claimed contributions.
