# Literature scan, 2023 to 2026: LLM-text detection and survey-fraud detection

Internal, 2026-09-11. What the current literature establishes and exactly where each result
lands against the claims in `paper/GHOST-RESPONDENTS-DRAFT.md`. Companion to
`FOLLOWUP-EXPERIMENTS.md`, which cites this file for detector candidates (E3) and the
gold-subsample methods (E5).

**Verification.** Three Sonnet scouts searched and fetched; every entry below carries the URL
that was fetched. I re-fetched every 2026-dated item and every item a scout flagged, and
confirmed the two publisher-walled records (PNAS, Nature) through the NCBI E-utilities API.
Status codes: **V** fetched abstract or publisher page this session; **V-mirror** record
confirmed through PubMed, PMC, RePEc, or an NCBI summary because the publisher page returned
403; **U** a detail that could not be confirmed, stated as such. Items that could not be
verified at all are listed at the end, not cited. Nothing here is invented.

Where a number below disagrees with what a scout reported, the number is the one I read on
the fetched page, and the disagreement is noted.

---

## 0. The paper's claims, numbered for the mapping

- **C1** Respondent LLM use is common enough (tens of percent) that open-ended data are a
  two-component mixture (section 1.1; the 34% self-report from Zhang, Xu, Alvero).
- **C2** The field's default response is detect-and-delete (section 1.1).
- **C3** Machine text is homogenized: lower dispersion than human text, kappa below 1
  (sections 1.1, 4.2; kappa = 0.798 for gpt-4, 0.537 for llama-2).
- **C4** Detector sensitivity is a generator property, not a constant, and is low on
  frontier text: 27% on gpt-4-0613, 62% on llama-2, at 99% specificity, for a GPT-2-era
  RoBERTa used zero-shot (Table 1, section 7).
- **C5** A classifier detector's score correlates with writer fluency, and fluency with the
  trait, so deletion selects on the trait through r_F; measured r_F is about 0.05 and the
  selection channel is negligible at that level (sections 2.3, 5.6, Table 11).
- **C6** A watermark-style detector has r_F = 0 by construction, so the deletion-selection
  channel vanishes and the se/sp asymmetry of Prop. 14 flips (section 5.7).
- **C7** No correction estimator exists in the survey literature; the literature is
  detection only (section 1.3).
- **C8** Without gold labels, the two-class EM mixture and the label-free prevalence
  estimator fail on real text: prevalence off by five to six points, coverage far below
  nominal (sections 5.3, 5.5, Table 10).
- **C9** Misclassification SIMEX at a known (se, sp) does not beat detect-and-delete on RMSE
  (section 5.3; `ESTIMATOR-FIX-REPORT.md` section 4).
- **C10** The partial-identification bound on c, with the Imbens-Manski union of sampling
  and identification uncertainty, is the one estimator that meets its width target in most
  cells (`ESTIMATOR-FIX-REPORT.md` section 3).
- **C11** The paper assumes no labeled validation subsample is available (section 3).
- **C12** The two-component model treats every response as either human or machine; edited
  or polished text is outside it (INJECT.md 7a, section 7).

Mapping labels: **SUPPORT** the result backs the claim; **TENSION** the result cuts against
the claim as written; **BOUNDARY** the result marks where the claim stops applying.

---

## A. LLM-text detection

### A1. Zero-shot detectors

**Mitchell, E., Lee, Y., Khazatsky, A., Manning, C. D., Finn, C. (2023). DetectGPT: Zero-shot
machine-generated text detection using probability curvature. ICML 2023.** V,
https://arxiv.org/abs/2301.11305.
Machine text sits in negative-curvature regions of the source model's log-probability;
the score needs log-probabilities plus perturbations, no training. AUROC 0.95 on
GPT-NeoX fake-news detection against 0.81 for the best prior zero-shot baseline.
Mapping: SUPPORT C4 (the score is model-specific by construction; transfer across
generators is weaker). BOUNDARY C5: a curvature score is a function of token
predictability, so it is entangled with any writer trait that shifts predictability, the
same mechanism as a trained classifier.

**Bao, G., Zhao, Y., Teng, Z., Yang, L., Zhang, Y. (2024). Fast-DetectGPT: Efficient
zero-shot detection of machine-generated text via conditional probability curvature.
ICLR 2024.** V, https://arxiv.org/abs/2310.05130.
Replaces DetectGPT's perturbation step with sampling under conditional probability
curvature; about 75% relative accuracy gain over DetectGPT in white-box and black-box
settings at about 340x the speed.
Mapping: SUPPORT C4 (black-box setting, scoring model differs from generator, gains less).
Candidate for E3's zero-shot slot.

**Hans, A., Schwarzschild, A., Cherepanova, V., Kazemi, H., Saha, A., Goldblum, M.,
Geiping, J., Goldstein, T. (2024). Spotting LLMs with Binoculars: Zero-shot detection of
machine-generated text. ICML 2024.** V, https://arxiv.org/abs/2401.12070.
Contrasts perplexity under one model with cross-perplexity under a related model; detects
over 90% of ChatGPT generations at 0.01% false-positive rate without ChatGPT training data.
Mapping: TENSION C4 as a general statement (a zero-shot detector can generalize across
generators far better than the paper's RoBERTa did), SUPPORT C4 as stated (the paper
claims detectability is a generator property, and Binoculars' own numbers vary by
generator). Candidate for E3's second zero-shot slot.

**Verma, V., Fleisig, E., Tomlin, N., Klein, D. (2024). Ghostbuster: Detecting text
ghostwritten by large language models. NAACL 2024.** V, https://arxiv.org/abs/2305.15047
and https://aclanthology.org/2024.naacl-long.95/.
Classifier over features from weaker proxy LMs; 99.0 F1 in domain, +7.5 F1 over baselines
cross-domain, +4.4 F1 cross-LLM, and the authors state it is tuned toward ChatGPT and weak
on LLaMA output.
Mapping: SUPPORT C4 (a trained detector's sensitivity is generator-specific, stated by the
authors themselves). SUPPORT C5 mechanism (a learned function of surface text statistics
is entangled with writer style by construction).

### A2. Benchmarks and generalization

**Dugan, L., Hwang, A., Trhlík, F., Ludan, J. M., Zhu, A., Xu, H., Ippolito, D.,
Callison-Burch, C. (2024). RAID: A shared benchmark for robust evaluation of
machine-generated text detectors. ACL 2024.** V, https://arxiv.org/abs/2405.07940,
https://aclanthology.org/2024.acl-long.674/.
Over six million generations across 11 generators, 8 domains, 11 adversarial attacks, 4
decoding strategies; 8 open and 4 closed detectors. Detectors that claim 99%+ accuracy
are "easily fooled by adversarial attacks, variations in sampling strategies, repetition
penalties, and unseen generative models."
Mapping: SUPPORT C4, at scale. The right training corpus for E3's supervised detector.

**Li, Y., Li, Q., Cui, L., Bi, W., Wang, Z., Wang, L., Yang, L., Shi, S., Zhang, Y.
(2024). MAGE: Machine-generated text detection in the wild. ACL 2024.** V,
https://aclanthology.org/2024.acl-long.3/.
Multi-domain, multi-generator testbed; the best detector reaches 84.12% accuracy on
out-of-domain text from unseen generators, well below in-domain performance.
Mapping: SUPPORT C4.

**Wang, Y., Mansurov, J., Ivanov, P., Su, J., Shelmanov, A., Tsvigun, A., Afzal, O. M.,
Mahmoud, T., Puccetti, G., Arnold, T., Aji, A. F., Habash, N., Gurevych, I., Nakov, P.
(2024). M4GT-Bench: Evaluation benchmark for black-box machine-generated text detection.
ACL 2024.** V, https://arxiv.org/abs/2402.11175 (M4 predecessor:
https://arxiv.org/abs/2305.14902).
Three tasks: binary detection, generator attribution, and human-machine boundary detection
in mixed text. "Obtaining good performance in MGT detection usually requires access to
training data from the same domain and generators."
Mapping: SUPPORT C4. BOUNDARY C12: the boundary-detection task is the mixed-authorship
case the paper's model excludes.

### A3. Robustness and attacks

**Sadasivan, V. S., Kumar, A., Balasubramanian, S., Wang, W., Feizi, S. (2023). Can
AI-generated text be reliably detected? arXiv 2303.11156; later journal venue U.** V,
https://arxiv.org/abs/2303.11156.
Recursive paraphrasing defeats watermark, classifier, zero-shot, and retrieval detectors;
watermarks can be spoofed so that human text is flagged; detector AUROC is bounded by the
total-variation distance between human and machine text distributions.
Mapping: SUPPORT C4 (detectability falls as the generator's distribution approaches the
human one, which is the mechanism behind 27% on gpt-4 versus 62% on llama-2). BOUNDARY C6:
a spoofed watermark produces false positives on human text, so "r_F = 0 by construction"
holds only when the watermark cannot be spoofed on the target population.

**Krishna, K., Song, Y., Karpinska, M., Wieting, J., Iyyer, M. (2023). Paraphrasing evades
detectors of AI-generated text, but retrieval is an effective defense. NeurIPS 2023.** V,
https://arxiv.org/abs/2303.13408.
DIPPER, an 11B paraphraser, drops DetectGPT from 70.3% to 4.6% detection at 1% FPR and
evades watermarking, GPTZero, and OpenAI's classifier; retrieval against a store of known
generations recovers 80 to 97% at 1% FPR.
Mapping: SUPPORT C4. BOUNDARY C12: a paraphrased machine answer is the "polish" case of
E1, and the paper's detectors have not been tested on it. The retrieval defense is a third
detector type, provenance-based, with r_F = 0 like a watermark but requiring the generating
service to log outputs.

### A4. Who gets flagged

**Liang, W., Yuksekgonul, M., Mao, Y., Wu, E., Zou, J. (2023). GPT detectors are biased
against non-native English writers. Patterns 4(7).** V, https://arxiv.org/abs/2304.02819
and https://www.cell.com/patterns/fulltext/S2666-3899(23)00130-7.
Seven commercial detectors on US eighth-grade essays versus TOEFL essays: over half of the
TOEFL essays flagged as AI, native essays near-perfect; 18 of 91 TOEFL essays flagged by
all seven, 97% by at least one. Simplifying native text raises its flag rate; enriching
non-native word choice lowers it. The mechanism is perplexity.
Mapping: SUPPORT C5, the load-bearing citation for the mechanism (already cited in the
draft). The paper's measured r_F of about 0.05 is an order of magnitude below what this
result would suggest for a non-native population; the essays corpus is native student
writing, which is the reason. E4's r_F measurement should stratify by first language.

**Park, H., Jeong, G., Kim, B. (2026). Style as a confound: False positives in AI detection
of non-native academic writing. EMNLP 2026 (arXiv 2608.26710, submitted 2026-08-27).** V,
https://arxiv.org/abs/2608.26710.
135,389 pairs of unedited and professionally edited manuscripts from an editing service,
isolating style from authorship. Across 13 detectors the human-text FPR ranges from 0.0% to
100.0%, and editing that changes style but not authorship moves detector scores in both
directions.
Mapping: SUPPORT C5, with a refinement the draft should carry: the collider is style, not
nativeness per se, which is what the paper's fluency proxy already assumes. TENSION for
any single number for r_F: the FPR range across detectors means r_F is a detector property,
which is E3's premise.

### A5. Watermarking

**Kirchenbauer, J., Geiping, J., Wen, Y., Katz, J., Miers, I., Goldstein, T. (2023). A
watermark for large language models. ICML 2023, PMLR 202, 17061 to 17084.** V,
https://proceedings.mlr.press/v202/kirchenbauer23a.html.
Green-list token biasing at sampling time, detected by a statistical test with p-values and
no model access; sensitivity depends on the entropy of the generated text.
Mapping: SUPPORT C6 (the flag depends on the generation process, not on any property of
the surface text a human would share). BOUNDARY C6: low-entropy text (short, formulaic
answers) carries a weak watermark, so se near 1 is not free for survey-length responses.

**Dathathri, S., See, A., Ghaisas, S., et al. (2024). Scalable watermarking for identifying
large language model outputs. Nature 634, 818 to 823.** V-mirror (Nature page is behind a
login redirect; record confirmed via NCBI esummary for PMID 39443777).
Production watermark (SynthID-Text) integrated with speculative sampling, quality-neutral
in a live experiment on Gemini traffic.
Mapping: SUPPORT C6 as a deployed instance. BOUNDARY C6: coverage depends on the
generating service adopting it; a respondent using an unwatermarked model is invisible to
it, so se in the watermark cell is bounded by adoption, not by the detector.

**Christ, M., Gunn, S., Zamir, O. (2023). Undetectable watermarks for language models.
arXiv 2306.09194; COLT 2024 per scout, U.** V, https://arxiv.org/abs/2306.09194.
Cryptographic watermark detectable only with a secret key, indistinguishable from
unwatermarked output without it.
Mapping: SUPPORT C6 in the strongest form: the flag carries no information about the text
beyond the key, so r_F = 0 is a theorem rather than an assumption.

### A6. Commercial detectors under academic evaluation

**Jabarian, B., Imas, A. (2025). Artificial writing and automated detection. NBER Working
Paper 34223, September 2025.** V, https://www.nber.org/papers/w34223 (also
https://bfi.uchicago.edu/insights/artificial-writing-and-automated-detection/).
1,992 human pre-2020 texts and 1,992 machine texts from four frontier LLMs across six
genres; Pangram, GPTZero, Originality, and open-source RoBERTa. Pangram reaches
near-zero FPR and FNR and is the only tool meeting a strict FPR cap of 0.005 without
losing accuracy; GPTZero's FNR reaches about 50% against humanizer tools; open-source
RoBERTa has 30 to 78% FPR across scenarios (scout's read of the BFI summary; the NBER
abstract gives the Pangram and FPR-cap statements).
Mapping: TENSION C4 for the RoBERTa detector specifically: the paper's instrument is the
weakest detector class in this evaluation, and its 27% sensitivity is a property of that
pairing, which section 7 already says. SUPPORT C4 in the sense the paper intends: the
generator and detector jointly determine the operating point. E3 must include at least one
commercial detector or the paper's detection axis is stuck at its weakest point.

**Glickenhaus, B., Thai, K., Russell, J., Masrour, E., Han, Y., Spero, M., Emi, B. (2026).
Pangram 4 technical report. arXiv 2607.27183, submitted 2026-07-29.** V,
https://arxiv.org/abs/2607.27183 and https://arxiv.org/html/2607.27183.
AUROC 0.9916, FPR 0.0041%, FNR 0.3396% overall; FNR by family (Table 3) Anthropic 0.195%,
OpenAI 0.316%, Google 0.498%. Non-native section (5.7): four learner corpora (ELLIPSE,
ICNALE, PELIC, the Liang TOEFL set), 24,586 texts, one false positive, FPR 0.0041%, the
same as the overall rate. Mixed authorship: lightly edited human text flagged as fully AI
0.01% of the time; recall on substantially edited mixed text 55.01% (the scout reported
65.7%; 55.01% is what the fetched HTML states). Vendor report, not peer reviewed.
Mapping: TENSION C5 and Table 11's premise: for this detector the non-native FPR equals the
overall FPR, so the fluency collider is empirically near zero without a watermark. The
draft's argument that only a decoupled detector removes the selection channel (C6) is too
strong as written; a classifier trained at this scale can also make r_F negligible. This is
the single most important item in the scan for the paper's framing. SUPPORT C4 (per-family
FNR differs). BOUNDARY C12 (mixed-text recall of 55% means the polish case is half-visible
to the best current detector).

### A7. Mixed and edited text

**Zhang, Q., Gao, C., Chen, D., Huang, Y., Huang, Y., Sun, Z., Zhang, S., Li, W., Fu, Z.,
Wan, Y., Sun, L. (2024). LLM-as-a-coauthor: Can mixed human-written and machine-generated
text be detected? NAACL 2024 Findings.** V, https://arxiv.org/abs/2401.05952 and
https://aclanthology.org/2024.findings-naacl.29/.
Defines mixtext (human text polished, completed, or rewritten by an LLM) and the MixSet
dataset; current detectors "struggle to identify mixtext, particularly in dealing with
subtle" modifications.
Mapping: BOUNDARY C12, the direct citation for why the paper's two-component model stops at
polished text, and for E1's polish arm.

---

## B. Survey fraud, respondent AI use, and bots

### B1. Prevalence

**Veselovsky, V., Horta Ribeiro, M., West, R. (2023). Artificial artificial artificial
intelligence: Crowd workers widely use large language models for text production tasks.
arXiv 2306.07899.** V, https://arxiv.org/abs/2306.07899.
Keystroke dynamics plus a synthetic-text classifier on an MTurk summarization task;
33 to 46% of workers estimated to have used an LLM.
Mapping: SUPPORT C1. The two-instrument (telemetry plus classifier) estimate is the design
E4 borrows.

**Zhang, S., Xu, J., Alvero, A. J. (2025). Generative AI meets open-ended survey responses:
Research participant use of AI and homogenization. Sociological Methods and Research 54(3),
1197 to 1242.** V, https://journals.sagepub.com/doi/10.1177/00491241251327130.
34% self-reported LLM use on open-ended items; simulated LLM text is more homogeneous and
more positive than human text, most on sensitive questions.
Mapping: SUPPORT C1 and C3 (already the draft's anchor for both). The draft's section 1.1
says this paper names the selection concern in one sentence without formalizing it; that
reading stands.

**Xu, Z., Malkin, N. (2026). A penny for your prompts: Experiments detecting and mitigating
LLM usage by survey respondents. arXiv 2607.00403, submitted 2026-07-01.** V,
https://arxiv.org/abs/2607.00403.
Prevalence of LLM-assisted responses "varied widely, from under 10% on Prolific to over 80%
on Mechanical Turk"; in-survey mitigation reduced LLM use "but did not necessarily improve
data quality."
Mapping: SUPPORT C1 with a range the draft does not yet have: pi is a platform property
spanning the whole grid axis (0.01 to 0.30) and beyond it. The draft should cite this
range beside the 34% figure. BOUNDARY C7: mitigation is prevention, not correction, so C7
stands. E4's Prolific choice puts it at the low end of this range; state that.

### B2. Detection of AI-generated survey responses

**Lebrun, B., Temtsin, S., Vonasch, A., Bartneck, C. (2024). Detecting the corruption of
online questionnaires by artificial intelligence. Frontiers in Robotics and AI.** V,
https://www.frontiersin.org/articles/10.3389/frobt.2023.1277635/full.
Human judges distinguish AI from human open-ended answers at 76% accuracy; automated
detectors perform at or near chance, "completely unusable" in the authors' words.
Mapping: SUPPORT C2 (detection is the frame) and SUPPORT C4 (near-chance automated
detection on survey-length text is worse than the paper's 27%). BOUNDARY: text length.
Survey answers are shorter than the essays in Layer B, and every detector above degrades
with length.

**Sepulvado, B., Huang, L., Lerner, J. (NORC, 2025). Detecting AI responses in survey data:
NORC's next leap for data quality; presented at AAPOR 2025 as "Detecting AI-generated
survey responses: tool development and bias mitigation."** V,
https://www.norc.org/research/library/detecting-ai-responses-survey-data-norcs-next-leap-data-quality.html.
Classifier trained on matched AmeriSpeak panelist versus LLM answers to identical items;
over 99% precision and recall reported; deployed with human review before removal.
Mapping: SUPPORT C2 (the deployed pipeline is detect, review, delete). TENSION C4 for the
claim that sensitivity is low on frontier text: matched-item in-domain training gives a
different operating point from zero-shot RoBERTa. The draft already cites this as
Huang et al.; the NORC page lists Sepulvado, Huang, Lerner for the library write-up and the
AAPOR schedule lists Huang alone, so keep both attributions as the draft's reference note
already does.

**Gerber, S., Cash, S. B. (2026). Identifying generative AI use among genuine responders in
online survey research. Communications Psychology.** V,
https://pmc.ncbi.nlm.nih.gov/articles/PMC13438544/.
Bot checks, logic and timing checks, cross-response similarity tests validated by running
the survey's own prompts through GPT, Gemini, and Copilot; ten linguistic markers of AI
text; cites the 34% figure and Westwood's 99.8% attention-check pass rate.
Mapping: SUPPORT C2 and C7 (a detection pipeline, no correction step). This is the
"Communications Psychology" motivation source the draft's section 1.1 TODO 1 asks to
verify: title, authors, and venue now confirmed.

**Panda, S., Chona, H., Das, R. K., Kale, S., Soneji, S., Dodge, J. (2026). The race
between agentic AI capabilities and data quality control in online surveys. arXiv
2608.28597, submitted 2026-06-21.** V, https://arxiv.org/abs/2608.28597.
LLM agents complete web surveys and pass embedded attention checks by reading exposed DOM
metadata; DOM obfuscation degrades agent accuracy on image items while leaving humans
unaffected.
Mapping: SUPPORT C2 and the draft's Muse framing (section 1.1). This is the "agentic AI
against survey quality control" motivation source in TODO 1: confirmed.

### B3. Bots and fraud in panels

**Pew Research Center (2026-08-27). No easy fix for bogus respondents in online opt-in
polls.** V,
https://www.pewresearch.org/methods/2026/08/27/no-easy-fix-for-bogus-respondents-in-online-opt-in-polls/.
11,114 opt-in respondents, November 2024; trap questions and CloudResearch Sentry each cut
low-quality response rates from about 7% to 1 to 2%; voter-file matching made quality
worse (yea-saying rose to 9%) by dropping valid respondents who declined to share contact
details; all three screens moved the 18 to 29 Trump-Harris margin by 3 to 7 points.
Mapping: SUPPORT C2. SUPPORT C5's mechanism in a non-AI setting: a screen that selects on
a respondent property (willingness to share contact details) shifts the estimate. This is
the cleanest published example of screen-induced selection in survey data and belongs in
section 2.3's framing. The draft already lists this report; TODO 1 can close for it.

**Westwood, S. J. (2025). The potential existential threat of large language models to
online survey research. PNAS 122(47), e2518075122.** V-mirror (pnas.org returns 403;
record confirmed via NCBI esummary for PMID 41264250, DOI 10.1073/pnas.2518075122).
An LLM agent passed 99.8% of attention checks over more than 43,000 completions, tailored
answers to assigned demographics, and under a directional prompt moved approval and
generic-ballot estimates by tens of points; 10 to 52 injected responses could have
flipped 2024 national poll margins (numbers per the EurekAlert release and the Gerber and
Cash citation; abstract text not read directly, U for the exact figures).
Mapping: SUPPORT C2 and C7: the threat is framed as detection failure, the remedy as
better detection. BOUNDARY C1: this is bot injection, not respondent outsourcing; the
mixture's machine component has no respondent behind it, so c is undefined rather than
measured. The draft should keep the two threats distinct.

**Prolific (2026). Authenticity checks: How we tested the most accurate method for
identifying agentic AI.** V,
https://www.prolific.com/resources/authenticity-checks-how-we-tested-the-most-accurate-method-for-identifying-agentic-ai.
Vendor test against GPT, Claude, Perplexity, Gemini, and a custom bot versus 125 humans;
bot checks at 100%, a May 2025 open-ended LLM detector at 98.7% precision and 0.6% FPR,
attention checks at 59.7%. Vendor page, not peer reviewed.
Mapping: SUPPORT C2. Useful as the operating point a platform actually runs.

**CloudResearch (2026). The Bot Olympics: A $50K industry challenge.** V,
https://www.cloudresearch.com/resources/blog/bot-olympics-50k-challenge-ai-agents-survey-fraud/.
Claims about five billion online surveys a year with 30 to 40% fraudulent or unusable;
describes an adversarial competition mixing 500 humans and 500 agents per round. Vendor
page; the 30 to 40% figure covers all fraud, not LLM assistance.
Mapping: weak SUPPORT C1; do not cite the 30 to 40% as an LLM-use prevalence.

### B4. Silicon samples (background, different problem)

**Argyle, L. P., Busby, E. C., Fulda, N., Gubler, J. R., Rytting, C., Wingate, D. (2023).
Out of one, many. Political Analysis 31(3).** V, https://arxiv.org/abs/2209.06899.
**Bisbee, J., Clinton, J. D., Dorff, C., Kenkel, B., Larson, J. M. (2024). Synthetic
replacements for human survey data? The perils of large language models. Political
Analysis.** V, Cambridge Core page fetched.
**Santurkar, S., Durmus, E., Ladhak, F., Lee, C., Liang, P., Hashimoto, T. (2023). Whose
opinions do language models reflect? ICML 2023.** V, https://arxiv.org/abs/2303.17548.
Mapping: background only. Bisbee et al. is a second, independent source for C3
(persona-prompted LLM responses have too little variance for inference), from the
simulation side rather than the contamination side; worth one sentence in section 1.3.

---

## C. Inference with imperfect labels, mixtures, and partial identification

### C1. Prediction-powered inference and relatives (all need a labeled subsample)

**Angelopoulos, A. N., Bates, S., Fannjiang, C., Jordan, M. I., Zrnic, T. (2023).
Prediction-powered inference. Science 382(6671), 669 to 674.** V-mirror (Science page
403; PubMed 37943906 confirms).
**Angelopoulos, A. N., Duchi, J. C., Zrnic, T. (2023, rev. 2024). PPI++: Efficient
prediction-powered inference. arXiv 2311.01453.** V.
**Zrnic, T., Candès, E. J. (2024). Cross-prediction-powered inference. PNAS 121(15).**
V-mirror (PMC11009639).
**Egami, N., Hinck, M., Stewart, B. M., Wei, H. (2023). Using imperfect surrogates for
downstream inference: Design-based supervised learning for social science applications of
large language models. NeurIPS 2023.** V, https://arxiv.org/abs/2306.04746.
**Gligorić, K., Zrnic, T., Lee, C., Candès, E. J., Jurafsky, D. (2025). Can unconfident LLM
annotations be used for confident conclusions? NAACL 2025.** V,
https://aclanthology.org/2025.naacl-long.179/.
**Xu, S., Sun, W. W. (2026). Do more predictions improve statistical inference? Filtered
prediction-powered inference. arXiv 2602.10464, submitted 2026-02-11.** V.

What the family establishes: valid intervals for means, quantiles, and regression
coefficients from a small gold-labeled set plus a large ML-predicted set, with no
assumption on the predictor; tighter predictions give tighter intervals; cross-fitting
(Zrnic and Candès) and confidence-driven label selection (Gligorić et al.) cut the labels
needed; filtering (Xu and Sun) restricts to regions where predictions are reliable.
Egami et al.'s DSL is the closest to the paper's setting: LLM surrogate labels plus a
small expert-coded sample give unbiased downstream regression estimates even at 80 to 90%
label accuracy.

Mapping: BOUNDARY C11, and the most useful boundary in this scan. Every method here needs
gold labels, so none applies under the paper's assumption, and the paper's negative
results (C8, C9) are about the no-label regime these methods do not claim. The paper
should say this in section 3: "the label-free failure is the price of having no
validation subsample; with one, the design-based and prediction-powered estimators apply
and are expected to dominate." E5 part (b) is that experiment. TENSION with C7 only if
C7 is read as "no correction exists anywhere"; the accurate form is "no correction exists
for the survey-contamination problem without labels," which is what section 1.3 says.

**Ludwig, J., Mullainathan, S., Rambachan, A. (2024, rev. 2025). Large language models: An
applied econometric framework. NBER WP 33344; Annual Review of Economics 2026 per the arXiv
listing, U for the volume.** V, https://arxiv.org/abs/2412.07031.
Separates prediction tasks from measurement tasks; argues that without a validation sample,
estimates from LLM measurements can move arbitrarily with model and prompt choice.
Mapping: SUPPORT C8 and C11 (a formal statement that the no-validation regime is where
label-free estimators are fragile). The draft's section 6 recommendation 3 ("do not report a
prevalence estimate from score distributions") is this paper's warning in the survey
setting.

### C2. Measurement error in LLM pipelines

**Messing, S. (2026). Hidden measurement error in LLM pipelines distorts annotation,
evaluation, and benchmarking. arXiv 2604.11581, submitted 2026-04-13.** V.
Standard intervals in LLM annotation and evaluation ignore judge choice, temperature, and
prompt phrasing; under-coverage worsens with more data; a total-evaluation-error
decomposition restores coverage.
Mapping: already in the draft as the closest paper (section 1.3); the scan adds that its
"under-coverage that worsens with scale" is the same pathology the EM estimator shows in
section 5.5 (EM gets worse with more resolution). Parallel finding, different object.

### C3. Misclassification correction

**Küchenhoff, H., Mwalili, S. M., Lesaffre, E. (2006). A general method for dealing with
misclassification in regression: The misclassification SIMEX. Biometrics 62(1), 85 to
96.** Origin citation, outside the window, Wiley page not fetched (403); standard reference.
Mapping: the method behind C9. The paper's SIMEX result should cite this as the origin if
it does not already.

No 2023 to 2026 misclassification-SIMEX extension could be verified this session (see the
dropped list). C9 therefore stands against the 2006 method as implemented, not against a
newer variant; say so in section 3.

### C4. Partial identification

**Horowitz, J. L., Manski, C. F. (1995). Identification and robustness with contaminated
and corrupted data. Econometrica 63(2), 281 to 302.** V-mirror (RePEc).
**Imbens, G. W., Manski, C. F. (2004). Confidence intervals for partially identified
parameters. Econometrica 72(6), 1845 to 1857.** V-mirror (RePEc).
Horowitz and Manski: under contaminated sampling (errors independent of the true value) or
corrupted sampling (errors arbitrary), parameters are set-identified with sharp bounds, and
the two cases give different bounds. Imbens and Manski: intervals that cover the true
parameter, not the whole identified set, at a fixed rate, uniformly in the set's width.
Mapping: SUPPORT C10; these are the two citations `fit_bounds_c` rests on and the
`ESTIMATOR-FIX-REPORT.md` already names the second. One refinement: the paper's mixture is
Horowitz-Manski "corrupted" rather than "contaminated" whenever c > 0 (the machine text
depends on the true trait), so the bound's sharpness argument should cite the corrupted
case. E5 part (a) should check which case the survivor-sample bound falls in.

### C5. Prevalence estimation without labels

**Esuli, A., Fabris, A., Moreo, A., Sebastiani, F. (2023). Learning to quantify. Springer,
Information Retrieval Series 47.** V (Springer book page).
**Ramaswamy, H. G., Scott, C., Tewari, A. (2016). Mixture proportion estimation via kernel
embeddings of distributions. ICML 2016.** V (PMLR page); anchor, outside window.
**Balabdaoui, F., Besdziek, H. (2025). Simple estimators of the mixing proportion in a
semi-parametric mixture with known component. Sankhya A.** V-mirror (PMC12967557).
**Lecestre, A. (2025, rev. 2026). Robust label shift quantification. arXiv 2502.03174.** V.
What they establish: classify-and-count is biased; adjusted-count and distribution-matching
methods need the class-conditional score distributions to be stable between training and
deployment; parametric rates for the mixing proportion need the background component known
and the signal's support strictly nested in it (Balabdaoui and Besdziek); robust
quantification handles contamination in the label-shift setting (Lecestre).
Mapping: SUPPORT C8 with a mechanism: the paper's label-free prevalence estimator is a
quantifier applied where its assumptions fail (the human score distribution is estimated
out of fold from the same corpus, the machine component's support is not nested, and the
class-conditionals shift with the generator). The five-to-six-point miss is what the
quantification literature predicts under those conditions. Section 5.3 should say which
assumption fails rather than only reporting the miss.

### C6. Selection from classifier-based screening

**Ulichney, R., Coston, A. (2026). Beyond the training distribution: Evaluating predictions
under distribution shift and selection bias. arXiv 2606.14506, submitted 2026-06-12.** V.
Double-ML, influence-function estimator for target risk under simultaneous covariate shift
and selective labels (outcomes observed only where a screening decision allowed).
Mapping: SUPPORT C5's structure (screening by a predicted label is a selection mechanism)
and BOUNDARY C11 (the correction needs labeled data on both sides of the screen). The
survey-specific version of this, deletion by an AI detector, has no published analysis
that the scouts could find, which is C7 in its narrow form.

---

## D. Synthesis: what the scan changes in the paper

| claim | net verdict | sources that decide it |
|---|---|---|
| C1 prevalence | SUPPORT, and the range is wider than the draft says | Veselovsky 2023; Zhang 2025; Xu and Malkin 2026 (under 10% to over 80% by platform) |
| C2 detect-and-delete default | SUPPORT | Lebrun 2024; NORC 2025; Gerber and Cash 2026; Pew 2026; Prolific 2026 |
| C3 homogenization | SUPPORT, plus an independent second source | Zhang 2025; Bisbee 2024 |
| C4 sensitivity is generator-dependent and low | SUPPORT for the mechanism, TENSION for the level | RAID, MAGE, M4GT (mechanism); Jabarian and Imas 2025 and Pangram 4 (a 2026 detector is at sub-1% FNR on frontier text; the paper's 27% is a RoBERTa-on-GPT-4 fact) |
| C5 fluency collider | SUPPORT for the mechanism, TENSION for universality | Liang 2023, Park 2026 (mechanism); Pangram 4 section 5.7 (non-native FPR equals overall FPR for one detector) |
| C6 watermark decouples | SUPPORT, with two boundaries | Kirchenbauer 2023, Christ 2023, Dathathri 2024 (support); Sadasivan 2023 (spoofing), adoption (coverage) |
| C7 no correction estimator | SUPPORT in the narrow form | scouts found none for survey contamination without labels; PPI family exists with labels |
| C8 label-free estimators fail | SUPPORT with a mechanism | Esuli 2023; Balabdaoui 2025; Ludwig 2024 |
| C9 SIMEX loses to deletion | stands, against the 2006 method | Küchenhoff 2006; no verified newer variant |
| C10 the bound works | SUPPORT, cite the corrupted case | Horowitz and Manski 1995; Imbens and Manski 2004 |
| C11 no validation subsample | BOUNDARY, the paper's most consequential assumption | PPI, PPI++, cross-PPI, DSL, CDI, FPPI |
| C12 two components only | BOUNDARY | Zhang 2024 mixtext; M4GT boundary task; Pangram 4 mixed recall 55% |

Five concrete edits the scan supports:

1. **Section 1.1, TODO 1.** Three motivation sources are now confirmed with authors and
   venues: Gerber and Cash (2026, Communications Psychology), Panda et al. (2026, arXiv
   2608.28597), Pew (2026-08-27). Add Xu and Malkin (2026) for the prevalence range.
2. **Section 5.6 and 5.7.** Add Pangram 4's non-native result as the empirical case where a
   classifier reaches r_F near zero without a watermark, and restate C6 as "a detector whose
   flag is independent of the trait," of which a watermark is the constructive case and a
   sufficiently trained classifier may be an empirical one. Table 11 then covers both.
3. **Section 3.** State that the no-label assumption is what separates this paper from the
   prediction-powered family, cite Angelopoulos 2023 and Egami 2023, and point to the
   gold-subsample experiment (E5) as the bridge.
4. **Section 5.3.** Name which quantification assumption the label-free estimator violates
   (Esuli et al. 2023), rather than reporting the miss alone.
5. **Section 7.** Add mixed-authorship text (Zhang 2024; Pangram 4 mixed recall) as the
   stated boundary of the two-component model, and cite Lebrun 2024 for the length caveat.

---

## Not found or dropped

- No published correction estimator for LLM-contaminated survey responses without labels
  (searched "detect and delete", "bias correction", "downstream inference" with survey and
  LLM terms). Recorded as searched-and-not-found, not as a citable negative.
- No survey-specific study of who gets flagged (by first language or literacy) by a deployed
  survey detector; vendor pages report aggregate rates only.
- No paper focused on detection of survey-length short texts as its own object; Lebrun 2024
  is the nearest.
- Sevilimedu et al. (2026), an MC-SIMEX extrapolation refinement in Statistics in Medicine:
  Wiley page 403, abstract unread, dropped.
- Bail (2024) PNAS perspective: not fetched, tangential, dropped.
- "Attacks on machine-text detectors retain stylistic fingerprints" (arXiv 2505.14608) and
  "Self-disguise attack" (arXiv 2508.15848): surfaced in search, not fetched, dropped.
- "Feeding LLM annotations to BERT classifiers at your own risk" (arXiv 2504.15432) and
  "Bias inheritance in LLM-based data augmentation" (arXiv 2502.04419): surfaced, not
  fetched, dropped.
- Corbin, Baiocchi, Chen (2022), label selection in clinical ML evaluation (arXiv
  2209.09188): on topic for C6 of section C but outside the window.
