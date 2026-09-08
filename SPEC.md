# Ghost respondents: research spec

A psychometric treatment of covert AI authorship in human survey data. Respondents paste questions into an LLM and submit the output; the field's only answer today is detect and delete. This project models the contaminated sample as a mixture of two measurement processes, derives the bias, estimates the contamination rate without gold-standard labels, and corrects the validity coefficients. Target: working paper and preprint inside one week of fleet execution, then submission to Psychological Methods (primary) or JBDS (secondary).

## 1. Problem formalization

### 1.1 Setup and notation

Respondent i = 1..n answers open-ended survey items. Each has a latent trait theta_i (anxiety, depression severity, a Big Five dimension) and an outcome w_i predicted by theta_i in the human population. The open-ended response is scored (by human coders or an LLM scoring pipeline) into an indicator x_i. The object of study is the validity coefficient rho = Cor(theta, w), estimated through x.

Authorship A_i in {H, M} is unobserved: H means the human wrote it, M means an LLM did. The contamination fraction pi = P(A_i = M) is unknown.

### 1.2 The two measurement processes

Human process: x_i | theta_i, H follows a classical measurement model, x_i = theta_i + e_i, Var(e) = s2_H, reliability rel_H.

Machine process: x_i | M is generated from the item text plus whatever the respondent leaked into the prompt. Parameterize by coupling c = Cor(x, theta | M):
- c = 0: zero coupling, the LLM knows nothing about the respondent. x independent of theta, mean mu_M, variance s2_M. Empirically s2_M < s2_H: machine answers are samey. This is the homogenization term.
- 0 < c < 1: partial coupling, the respondent pasted their draft or described themselves. The machine response carries a diluted signal.
- c near 1: the LLM is a faithful amanuensis. Contamination is nearly harmless; the paper should say so and move on.

The c grid is what turns this from a one-case claim into a map of when contamination matters.

### 1.3 Estimands

Primary: rho_H, the validity coefficient in the human subpopulation.
Secondary: pi (prevalence), rel_H (human reliability), and the human factor loadings when items are multi-indicator.
Bound estimand: when pi is not point-identified (high coupling), bounds on rho_H under partial identification, reported instead of a point fix.

### 1.4 Bias derivation plan

Derive observed moments under the mixture. Covariance with outcome: Cov(x, w) = (1 - pi) Cov(x, w | H) + pi Cov(x, w | M), with the machine term equal to c times the human-scale covariance. Observed correlation attenuates through two channels: dilution (the 1 - pi factor) and reliability compression (s2_M < s2_H shrinks the denominator in a way that partially offsets dilution; net direction depends on the mean gap mu_H - mu_M). Deliverables: closed form for bias(rho_obs) as a function of (pi, c, rel_H, mean gap); the conditions under which homogenization inflates between-item correlations among machine cases even while attenuating trait-outcome correlation; the specific region of the grid where naive estimates are sign-stable versus sign-flipped. First verification target: Layer A simulation must reproduce every derived moment before any prose ships.

### 1.5 The deletion fallacy

Formalize detect-and-delete. Detector D with sensitivity se = P(D flags | M) and specificity sp = P(D passes | H). After deletion, residual contamination pi' = (1 - se) pi / [(1 - se) pi + sp (1 - pi)], which looks small. The real result to prove: deletion preserves the human joint law of (theta, w, x), hence every human-sample correlation, if the pass indicator S is independent of (theta, w, x) given H; for one particular correlation, trait-independent detection is neither necessary nor sufficient (pass-1 diff report, item D4, two counterexamples). What lane 1 proves (Prop. 11 in derivations/lane1-zero-coupling.md) is the parametric version: with (theta, F) bivariate normal, r_F = Cor(theta, F) != 0, a monotone threshold pass rule with sp_bar < 1, and the human measurement not simultaneously perfectly reliable and perfectly valid, the survivor validity Cor(x, w | H, pass) is strictly below Cor(x, w | H) through the range-restriction factor q = 1 - r_F^2 psi < 1. [Edited 2026-09-07 after pass 1, item D4; the sentence originally read "deletion is unbiased only if detector errors are independent of theta", which is false in both directions.] Detectors flag non-native and low-fluency human writing at higher rates; fluency correlates with the traits being measured. So conditioning on D = pass induces selection on theta: a collider-flavored bias that survives even at pi' = 0. This result, more than the attenuation algebra, is the argument that kills detect-and-delete as the field's default.

## 2. Data testbed

### 2.1 HC3

Human ChatGPT Comparison Corpus (https://huggingface.co/datasets/Hello-SimpleAI/HC3; paper: arXiv 2301.07597). Roughly 24k questions with paired human-expert and ChatGPT answers across open QA, Reddit ELI5, medicine, and finance. Verify exact counts and license at download. Role: detector calibration (sensitivity and specificity on known pairs) and text-level mixture experiments where construct labels are not needed.

### 2.2 Pennebaker-King essays

Stream-of-consciousness essays dataset (Pennebaker and King 1999): 2,479 essays with Big Five (BFI) trait scores, about 1.9M words. Accessible via IEEE DataPort mirror (https://doi.org/10.21227/dyfp-7f45) and widely mirrored as essays.csv. Role: the construct-linked human base. Real human text tied to real trait scores, which is what HC3 lacks.

### 2.3 LLM counterpart generation

For each essays prompt, generate machine responses at three coupling levels:
- c = 0: the LLM sees only the prompt.
- c partial: the LLM sees the prompt plus a coarse persona sketch (trait band, not the exact score).
- c high: the LLM sees the prompt plus the respondent's actual BFI scores.

Generate with two model families (one frontier proprietary, one open-weight) so results are not a single-model artifact. Cost is trivial at fleet scale. Freeze generation parameters and seeds.

### 2.4 Detector calibration

Calibrate a detector (a published open-weights AI-text classifier plus a simple feature baseline) on HC3 pairs, then re-calibrate on the essays testbed. Record operating points; the honest range from the NORC PACT work is roughly 99% in-domain down to mid-80s out of domain (https://www.norc.org/content/dam/norc-org/pdf2025/AAPOR%20Detecting%20AI-Generated%20Survey%20Responses%20-%20Lilian%20Huang.pdf). The simulation grid runs detectors at calibrated, degraded, and oracle quality.

## 3. Correction estimator options

### 3.1 SIMEX-style

Treat detector-calibrated misclassification as known measurement error on the authorship variable. Add synthetic extra contamination in increments, refit, extrapolate back to zero. Simple and robust, but the known-error assumption is only as good as the calibration transfer.

### 3.2 Label-free prevalence plus errors-in-variables

Estimate pi without any labels by treating it as a quantification problem: compare the pooled sample distribution against a pure machine reference distribution generated on demand by querying LLMs with the same items. Calibrated classify-and-count with distribution matching gives pi-hat; then correct rho via the errors-in-variables algebra using pi-hat and the estimated machine reliability. Anchors: items where human and machine response distributions are best separated, with separation estimated from the reference corpora.

### 3.3 Full joint mixture measurement model

Latent-class model with one class per authorship state, each with its own measurement parameters, estimated by EM or in Stan. Most efficient when correctly specified, most fragile when not; reviewers will attack the specification.

### 3.4 Recommendation

Primary pipeline: 3.2 for prevalence, 3.1 as robustness check, 3.3 in the appendix as the parametric ceiling. Rationale: 3.2 makes the weakest assumptions and directly answers the question every applied researcher has (how dirty is my sample), while 3.1 covers the researcher who already runs a detector. Never ship 3.3 as the headline.

## 4. Simulation design

### 4.1 Layer A: parametric Monte Carlo

theta ~ N(0,1); human indicators from a factor model with k items; machine indicators from the coupling-c process; outcome w = b theta + noise. Purpose is not realism, it is proof: every closed-form result from section 1 gets checked against empirical bias at 500 replications per cell. A mismatch invalidates the derivation, not the simulation.

### 4.2 Layer B: semi-synthetic on real text

Base sample: essays dataset human responses with BFI traits. Inject machine counterparts at grid values of pi. Validity target: text-predicted trait score against a held-out trait or an outcome simulated with known dependence on the trait. This layer supplies ecological validity: real words, real trait distributions, real detector behavior.

### 4.3 Grid

pi in {0.01, 0.02, 0.05, 0.10, 0.20, 0.30}; coupling c in {0, partial, high}; n in {500, 1000, 5000}; detector in {none, calibrated, degraded, oracle}; generator in {frontier model, open model}. Layer A: 500 reps per cell. Layer B: 100 reps per cell.

### 4.4 Metrics and what "correction works" means numerically

Metrics: bias and RMSE of rho-hat_H; coverage of nominal 95% CI; absolute error of pi-hat; factor loading bias.
Success thresholds, pre-registered:
- corrected bias at most 20% of naive bias in every cell with pi <= 0.20 and c <= partial
- CI coverage back inside [92, 98]
- pi-hat error at most 2 points at n = 1000
- correction beats detect-and-delete on RMSE at calibrated and degraded detector operating points; concede oracle deletion wins and say so
Boundary report: cells where nothing works (high pi with high c) are reported as the method's limits, with bounds from the partial-identification analysis. The boundary map is a deliverable, not an embarrassment.

## 5. Analysis plan, pre-registration ready

H1: naive bias is monotone in pi and negative for validity coefficients in the small-mean-gap regime (attenuation dominates).
H2: homogenization signature: between-item correlations inflate among machine cases while trait-outcome correlation attenuates.
H3: at realistic detector operating points, detect-and-delete has higher RMSE for rho_H than the correction, and its residual bias is driven by selection on fluency-correlated traits, not by residual contamination.
H4: the correction restores nominal coverage.
H5 (boundary): beyond the identifiable region, bounds on rho_H remain informative (width under 0.2 correlation units at n = 1000).
Analysis code for Layers A and B is frozen after the pilot cells and before the full grid. Any post-freeze change is logged with justification.

## 6. Execution plan, fleet pace

Orchestration: Instinct runs the project board: lane assignments, day-gate checks, and go/no-go at each verification pass. Execution happens in Claude Code sessions on the MacBook. Default stack: Fable 5.1 on Ultra Mode as lane orchestrator with Sonnet subagents (never Fable subagents), Opus reserved for hard reasoning spots, Astra (GPT-6) orchestrating its own subagents on the lanes chosen to evaluate it on real work.

Per-lane stack:

Lane 1, derivation and writeup spine. Reasoning-model-led. Fable 5.1 Ultra does the derivation itself; Sonnet subagents handle algebra expansion, notation audits, and draft assembly. Opus steps in on the deletion-selection proof if the first pass stalls. The independent re-derivation (verification pass 1) goes to Astra: a different model family is a genuinely independent derivation, and it doubles as a real-work evaluation of Astra on the hardest reasoning in the project.
Lane 2, literature and novelty gate. Astra candidate lane. Bounded inputs, checkable outputs: the positioning memo's claims can be verified claim by claim. Fallback is Fable+Sonnet if Astra's memo fails spot checks.
Lane 3, testbed. Implementation-led. Fable orchestrator plus Sonnet subagents writing loaders, generation scripts, and calibration runs.
Lane 4, simulation harness. Implementation-led. Fable+Sonnet builds the engine; Fable itself (not a subagent) reviews estimator code line by line before any grid run.
Lane 5, reproducibility. Sonnet-led under Fable supervision: seeds, environment lock, repo, preprint plumbing.

Compute budget, one MacBook 24/7:

- LLM counterpart generation is the main token cost, and it is one-time: 2,479 prompts x 3 coupling levels x 2 model families, about 15k generations of roughly 700 output tokens each. Generate once, freeze, reuse across every simulation rep. Cheaper fallback if the bill matters: generate for a 1,200-essay subsample, which costs Layer B nothing at the n <= 1000 cells.
- Layer A grid: 6 pi x 3 coupling x 3 n x 4 detector cells x 500 reps, about 108k model fits. At roughly 2 s average per fit single-core that is about 60 core-hours, so one overnight batch across the laptop's cores. Fits are embarrassingly parallel; shard by cell.
- Layer B is capped by data, not compute. The essays dataset has 2,479 human responses, so its n cells are {500, 1000, 2400} via bootstrap resampling; the n = 5000 cell exists only in Layer A. 100 reps per cell, another overnight batch.
- The one step that genuinely exceeds a laptop: full Bayesian estimation (Stan MCMC) of the joint mixture model across the grid. Cheaper alternative, flagged rather than assumed: EM with multi-start initialization plus parametric bootstrap intervals for the grid, full Bayesian only on a 6-cell confirmation subset.
- Scoring and detection stay local: sentence embeddings and the open-weights AI-text detector run on the MacBook, so simulation loops carry no API dependency or per-call cost.

Day by day:

Day 1: Lane 3 and Lane 4 build in parallel (Fable+Sonnet). Lane 2 (Astra) does the novelty-gate reads and positioning memo. Lane 1 (Fable) derives the zero-coupling closed forms. Overnight: counterpart generation batch 1.
Day 2: Lane 1 derives partial coupling and the deletion-selection result; Astra runs the independent re-derivation and the two get diffed line by line. Lane 3 calibrates detectors and freezes the testbed with summary stats. Overnight: Layer A grid.
Day 3: Lane 1 drafts the estimator sections; verification pass 2 checks every derived moment against Layer A output. Lane 4 runs Layer B pilot cells. Overnight: Layer B full grid.
Day 4: results tables and figures; failure-modes section; Lane 5 locks seeds and environment. Overnight: rerun anything flagged by passes 2 and 3.
Day 5: full draft assembled. Adversarial reviews: Opus briefed as a methods reviewer, Astra briefed as an NLP reviewer. Verification pass 3 against final numbers. Working paper complete.
Day 6: revisions. Analysis plan frozen as the registered supplement. PsyArXiv formatting.
Day 7: preprint posted. One-page summary and cover note for Zhang drafted per the standing protocol; Abhay sends it himself.

## 7. Derivation verification protocol

This is the human-pace element, kept deliberately slow because derivation errors are where agent fleets produce confident wrongness. Three passes, all mandatory before any math ships:
1. Independent re-derivation. Astra derives from the problem statement alone, without seeing Lane 1's work. The two derivations are diffed line by line. Using a different model family here is the point: correlated reasoning errors are the failure mode this pass exists to catch.
2. Numerical check. Every closed-form moment must match Layer A simulation output within Monte Carlo error. Runs on Fable against the overnight grid results.
3. Adversarial review. Opus, briefed to find the error, not to confirm.
An unresolved discrepancy at any pass blocks the preprint. No exceptions for deadline pressure; a wrong derivation is worse than a late one.

## 8. Failure modes, what kills it

1. Identifiability collapse. High coupling makes machine and human distributions nearly identical; pi is not point-identifiable and the correction reverts to bounds. The correction headline dies, the boundary-map paper survives. This is the most likely honest outcome in the c-high regime and the spec already treats it as a deliverable.
2. Calibration non-transfer. If detector error rates calibrated on HC3 do not transfer to survey open-ends, the SIMEX assumption breaks. Mitigation: per-domain recalibration in the testbed and a sensitivity grid over se and sp.
3. Textbook-only results. If the derivation yields only classical attenuation, a reviewer calls it a homework exercise. The mixture-specific results (homogenization inflation, between-mean term, deletion-selection bias) are what must carry the paper. If they do not materialize, reposition as a measurement note, not a methods paper.
4. Realism attack. "Nobody pastes survey items into ChatGPT." Counter with the SMR 2025 homogenization evidence (https://ideas.repec.org/a/sae/somere/v54y2025i3p1197-1242.html) and the NORC and PMC identification studies (https://pmc.ncbi.nlm.nih.gov/articles/PMC13438544/). If real-world prevalence evidence stays thin, the paper is preemptive rather than reactive, still publishable, weaker hook.
5. Overlap found at the novelty gate. If arXiv 2604.11581 or the SMR paper already contains the correction, pivot to whichever component they do not cover (most likely deletion-selection bias or label-free prevalence) and reposition as extension. Do not ship an overlapping novelty claim.
6. Generation realism attack. Conditioned generation may produce machine text too easy to detect, flattering the method. Primary results use unconditioned generation; conditioned generation is the stress test.
7. A math error ships. The fleet-specific risk. Section 7 exists for this.

## 9. Novelty verification gate, locked

Before any novelty claim appears in any draft, Lane 2 produces a one-page positioning memo from full-text reads of:
- Hidden Measurement Error in LLM Pipelines Distorts Annotation, Evaluation, and Benchmarking, https://arxiv.org/abs/2604.11581 (search excerpts suggest annotator-side pipelines; full text must confirm it does not touch respondent-side mixtures)
- Generative AI Meets Open-Ended Survey Responses, SMR 2025, preprint https://osf.io/preprints/socarxiv/4esdp_v3 (excerpts say descriptive homogenization documentation; confirm no correction estimator)
- Joint Item Response Models for Manual and Automatic Scores on Open-Ended Test Items, Psychometrika, https://www.cambridge.org/core/journals/psychometrika/article/joint-item-response-models-for-manual-and-automatic-scores-on-openended-test-items/FE2D892AB16F10705B6099D4151A6F90 (adjacent rater-mixture machinery; position against it)
- a scan of the quantification / class-prevalence estimation literature for prior label-free prevalence methods with latent constructs
Both closest papers resisted automated full-text fetch during the scan (title-level retrieval only), so these reads need a real browser session or library access. The memo diffs claims one by one. No memo, no novelty sentence.

## 10. Venues and path

Psychological Methods first: threat named, bias derived, correction built, recovery proven. JBDS second: Zhang edits it and the fit argument is direct. MBR or Sociological Methods and Research as fallbacks. Preprint on PsyArXiv at day 7; submission after one external read, realistically week 3. The Zhang one-pager frames it as his JBDS 2024 measurement-error line extended to the respondent side, which is the honest genealogy.

## References

- HC3: https://huggingface.co/datasets/Hello-SimpleAI/HC3 and https://arxiv.org/abs/2301.07597
- Essays-Big5: https://doi.org/10.21227/dyfp-7f45 (Pennebaker and King 1999; described in https://www.jair.org/index.php/jair/article/download/10520/25197)
- SMR 2025 homogenization: https://ideas.repec.org/a/sae/somere/v54y2025i3p1197-1242.html
- NORC PACT: https://www.norc.org/content/dam/norc-org/pdf2025/AAPOR%20Detecting%20AI-Generated%20Survey%20Responses%20-%20Lilian%20Huang.pdf
- Identifying generative AI use among genuine responders: https://pmc.ncbi.nlm.nih.gov/articles/PMC13438544/
- Hidden measurement error in LLM pipelines: https://arxiv.org/abs/2604.11581
- Debiased inference for AI-generated data: https://arxiv.org/abs/2608.18294
- Debiasing AI-generated regressors: https://doi.org/10.1287/isre.2024.1370
- Joint IRT manual and automatic scores, Psychometrika: https://www.cambridge.org/core/journals/psychometrika/article/joint-item-response-models-for-manual-and-automatic-scores-on-openended-test-items/FE2D892AB16F10705B6099D4151A6F90
