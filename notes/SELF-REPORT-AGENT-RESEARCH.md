# A unified agent for self-report: research note

**Verdict: BUILD, narrowly.** Build the measurement harness and run the one study that needs no
participants and no IRB. Do not build the consumer product. Repo name and the first two phases are
in section 7.

Written 2026-09-13 in `ghost-respondents/notes/` as the adjacent research home. No new repo yet.
Every external claim carries a source URL. Claims a source could not confirm are marked UNVERIFIED
and are not load-bearing anywhere in the argument.

---

## 0. The short version

The appealing pitch is that a conversational agent fixes self-report because it can clarify,
probe, and adapt the way a trained human interviewer does. That pitch is already in the literature
as a named call to action: Terheyden et al. coined "LLM-PROMs" in March 2025
(https://doi.org/10.1186/s41687-025-00867-4), and Weinfurt et al. endorsed it that September with
the exact sentence a researcher wants to see, that the field "should actively inquire into what
patient experience data can be collected via GenAI and rigorously evaluate the quality of the
assessments obtained" (https://doi.org/10.1186/s41687-025-00950-w, PMC12474825).

Nobody has done the rigorous evaluation. A PubMed title/abstract search on 2026-09-13 for
(chatbot OR conversational agent OR large language model) AND "measurement invariance" returns
**zero results**. Differential item functioning crossed with those terms returns two, neither on
agent administration. The one large psychometric study of a chatbot-administered scale, Dosovitsky,
Kim & Bunge 2021 (N = 3,902, chatbot PHQ-9, alpha = 0.896, one-factor fit CFI 0.925 / RMSEA 0.080,
https://doi.org/10.3389/fdgth.2021.645805), reports the chatbot mode's psychometrics in isolation
and never compares it against standard administration in the same people.

One study comes close and is worth naming up front rather than burying in section 2. Serafimovska
et al. automated the TICS-M cognitive screen as a chatbot and ran it against psychologist
administration in the same 100 people, reaching concurrent validity r = 0.81 and concluding in
favor of equivalence (2025, https://doi.org/10.1080/13803395.2025.2542248, PMID 40794461). That is
a genuine feasibility signal and it shows the sample sizes are small. It is not the study in
question: TICS-M is a performance test with a correct answer, the paper reports concurrent validity
and test-retest rather than an invariance ladder, and its chatbot does not adapt.

So there is a real hole, it is on the field's stated agenda, one adjacent study suggests the design
is feasible, and it is the kind of hole a measurement person fills.

The point of view underneath the rest of this note:

> **The agent buys clarification and pays for it in standardization. The research question is the
> exchange rate, and nobody has measured it.**

Classical measurement requires the same stimulus for everyone, because that is what makes two
people's scores comparable. Every conversational affordance that makes the agent feel better,
rephrasing an item into the respondent's own words, probing a vague answer, skipping what seems
irrelevant, is a per-person change to the stimulus. Computerized adaptive testing solved this once,
for item *selection*, by putting the items on a common IRT scale so different subsets still yield
comparable thetas. There is no analogous theory for item *rewording* or for conversational probing.
That absence is the research object.

Two consequences that shape everything below:

1. **On burden, the agent has nothing to offer.** CAT already administers about 4 to 5 PROMIS items
   per domain while holding reliability above 0.90 (PROMIS CAT efficiency figures, HealthMeasures
   and the PROMIS validation literature, https://doi.org/10.1016/j.jclinepi.2010.04.011; specific
   mean item counts UNVERIFIED against a single opened primary source, see section 2.3). An agent
   pitched on "fewer questions" is competing against a solved problem.
2. **The product is a bad bet and the instrument is a good one.** Not one AI journaling, coaching,
   memory, or AI-interviewer product surveyed in section 2.8 ships a validated score, and not one
   publishes psychometrics. Abandonment is the documented default outcome for self-tracking tools
   (section 2.8). Meanwhile there is no reporting standard for LLM-elicited measures at all
   (section 2.4), which is what an instrument could help establish. A harness plus a protocol is the
   thing with a shelf life; the app is not.

---

## 1. Defining the research object

Four things get conflated under "a unified agent for self-report." They are not variants, they
depend on each other, and only one of them is testable right now.

### A. Conversational asker
The agent administers existing validated items in dialogue instead of on a form. Same items, same
constructs, same scoring targets, different mode.

### B. Longitudinal diary or EMA agent
The agent replaces the scheduled EMA prompt with a conversational check-in, repeated over days or
weeks.

### C. Agent-mediated response
The agent answers surveys on the person's behalf from what it knows about them.

### D. Personal memory agent
The agent converts lived events, captured passively or recounted after the fact, into structured
scores.

### Choose A. Here is why.

**C is the thing ghost-respondents already models as contamination, not a product.** In that
framework the machine process at zero coupling produces a response independent of the respondent's
latent trait; at high coupling it is a faithful amanuensis and contamination is harmless
(`SPEC.md` section 1.2). Shipping C as a feature is arguing the other side of his own paper. Keep C
as a **comparison arm only**, because it is the reductio that sets the floor: if the agent answers
for you, there is no self-report left to validate, and whatever validity the scores retain is an
upper bound on how much of the measure was ever about the person.

**D is the most exciting and the least supported.** Its ceiling is pinned twice over:

- Text to validated score tops out around r = 0.4 to 0.5. Language-based Big Five assessment
  converged with self-report at mean r = 0.38 across traits in 66,732 people (Park et al. 2015,
  *JPSP*, https://doi.org/10.1037/pspp0000020). GPT-4o estimating depression severity from about
  15,000 narrative clinical notes with the real PHQ-9 censored explained roughly r-squared = 0.264,
  so r near 0.51 (https://doi.org/10.1016/j.jad.2025.04.014, PMC via
  https://pmc.ncbi.nlm.nih.gov/articles/PMC13489508/). A 2024/2025 comparison found a paper-and-pencil
  questionnaire outperformed GPT for measuring cognitive vulnerability to depression
  (https://pmc.ncbi.nlm.nih.gov/articles/PMC12141452/).
- Retrospective reconstruction of moments is weak at exactly the granularity D needs. The Day
  Reconstruction Method agrees with experience sampling at r ~ 0.97 on aggregate time use and
  r ~ 0.76 to 0.90 between persons, but within-person day-to-day affect agreement averages only
  r ~ 0.26 to 0.30, with situation-identity kappa ~ 0.34 (Lucas et al. 2020, *JPSP*,
  https://pmc.ncbi.nlm.nih.gov/articles/PMC7508776/).

D therefore has to be validated against B, and B has to be validated against A. D also carries the
worst privacy and clinical-safety posture of the four (section 3). It is a later chapter, not the
first one.

**B is where construct drift becomes unmeasurable.** Longitudinal invariance requires that the same
items mean the same thing at each occasion (Meredith 1993, *Psychometrika*,
https://doi.org/10.1007/bf02294825; Vandenberg & Lance 2000, *ORM*,
https://doi.org/10.1177/109442810031002). If each session's phrasing is generated fresh and
conditioned on the last session's transcript, there is no fixed item to test invariance on. B is
not merely harder than A; it makes the standard diagnostic inapplicable. B also has to beat a
mature, well-measured baseline: pooled EMA compliance is about 79% across 496 samples and 677,536
participants (Wrzus & Neubauer 2023, *Assessment*,
https://doi.org/10.1177/10731911211067538), about 75% in substance-use EMA across 126 studies and
19,431 participants (Jones et al. 2019, *Addiction*, https://doi.org/10.1111/add.14503), and
notably, the number of daily assessments did not predict compliance in Wrzus & Neubauer, which
undercuts "the agent makes it less burdensome so compliance rises."

**A is the base case, it has an accepted evaluation playbook, and it is the load-bearing assumption
under B, C and D.** If a conversational agent cannot administer a fixed scale invariantly, then no
conversational diary and no memory agent produces comparable scores, and the class fails at its
base. A negative result at A is therefore informative about all four. And A is the one the field
asked for out loud (section 0).

### The sharpest statement of the object

> Does administering a validated self-report instrument through an LLM agent preserve measurement
> invariance with the standard form mode, and how does that break down as conversational adaptivity
> increases?

Call the quantity the **adaptivity-invariance frontier**. Each conversational affordance spends from
a fixed standardization budget. The paper measures the spend rate.

---

## 2. Prior art

Direct prior art, ordered by how close it sits to the object in section 1. Keyword cousins are
excluded; the ones retained each stop short at a nameable point.

### 2.1 The explicit call to action (closest prior art, 18 months old)

- Terheyden JH et al., "A new generation of patient-reported outcome measures with large language
  models," *Journal of Patient-Reported Outcomes*, 2025-03-24,
  https://doi.org/10.1186/s41687-025-00867-4. Coins **LLM-PROM**. Argues the "highly structured
  questionnaire format of PROMs currently limits their real-world validity and acceptability," and
  that LLM-PROMs "will need to be developed with multi-stakeholder input and careful validation
  against established PROMs." A commentary, no data.
- Weinfurt KP et al., "Artificial intelligence and the future of patient-centered outcomes,"
  *Journal of Patient-Reported Outcomes*, 2025-09-26,
  https://doi.org/10.1186/s41687-025-00950-w. The argument in their words: standardized items
  "may introduce ambiguity about the health concept being assessed," whereas a trained interviewer
  "can tailor questions to the respondent's experience and conversation style and have a
  back-and-forth clarification of meaning"; the shortcoming "is that it cannot be done at scale
  with human interviewers." Their conclusion is a research call, not a finding.

**Where they stop:** both are commentaries. Neither reports a score, a reliability coefficient, or
an invariance test. The evaluation they ask for is unclaimed.

### 2.2 Chatbot-administered scales and survey chatbots

- Dosovitsky G, Kim E, Bunge EL, "Psychometric Properties of a Chatbot Version of the PHQ-9 With
  Adults and Older Adults," *Frontiers in Digital Health*, 2021,
  https://doi.org/10.3389/fdgth.2021.645805. N = 3,902 recruited via Facebook; 3,895 (99.82%)
  completed; alpha = 0.896; one-factor model fit CFI 0.925, TLI 0.900, RMSEA 0.080 (90% CI
  0.073-0.088), SRMR 0.039. **Stops at:** single-mode psychometrics. No form comparison, no
  invariance test, no criterion.
- Xiao Z et al., "Tell Me About Yourself: Using an AI-Powered Chatbot to Conduct Conversational
  Surveys with Open-ended Questions," *ACM TOCHI* 27(3), 2020,
  https://doi.org/10.1145/3381804. About 600 participants split between a Qualtrics web survey and
  a chatbot, over 5,200 free-text responses; chatbot condition showed significantly higher
  engagement and better response quality on Gricean maxims. Exact effect sizes UNVERIFIED (ACM
  paywall). **Stops at:** open-ended response quality, not scored instruments.
- Kim S, Lee J, Gweon G, "Comparing Data from Chatbot and Web Surveys," *CHI 2019*,
  https://doi.org/10.1145/3290605.3300316. 2x2, chatbot vs web crossed with formal vs casual style;
  chatbot with casual style reduced satisficing and raised enjoyment.
- Zarouali B, Araujo T, Ohme J, de Vreese C, "Comparing Chatbots and Online Surveys for
  (Longitudinal) Data Collection," *Communication Methods and Measures*, 2023,
  https://doi.org/10.1080/19312458.2022.2156489. The important counterweight: over a two-week
  longitudinal design they found **no evidence chatbots outperform web surveys**, with the web
  survey often showing more favorable response characteristics and shorter answers in the chatbot
  condition.
- Jacobsen RM, Cox SR, Griggio CF, van Berkel N, "Chatbots for Data Collection in Surveys: A
  Comparison of Four Theory-Based Interview Probes," arXiv:2503.08582, 2025-03-11,
  https://arxiv.org/abs/2503.08582. Compares probe types, which is the mechanism question rather
  than the mode question. Specific results UNVERIFIED.
- Deveci, Fuchs, Metzler, experimental comparison of chatbot-like vs traditional web questionnaire
  design, Sage, 2026, https://journals.sagepub.com/doi/10.1177/07591063261424249. Existence noted,
  results UNVERIFIED.

**Read on this cluster:** the evidence is genuinely split, with gains in Xiao 2020 and
Wambsganss 2020 (https://doi.org/10.1145/3334480.3382805, N = 127 course evaluations) and a null or
negative result in the more rigorous longitudinal design (Zarouali 2023). That split is itself
load-bearing: "conversation beats forms" is not settled, and every one of these studies measured
response quality or enjoyment rather than the psychometric properties of a scored instrument.

### 2.3 Adaptive administration, the baseline to beat on burden

- PROMIS and the HealthMeasures platform, https://www.healthmeasures.net, foundational validation
  Cella D et al., *J Clin Epidemiol*, 2010, https://doi.org/10.1016/j.jclinepi.2010.04.011. PROMIS
  measures are free for non-commercial research use; electronic administration permissions and the
  Assessment Center API can carry fees (HealthMeasures pricing page returned 404 on re-fetch,
  so the fee detail is UNVERIFIED).
- Reported CAT efficiency: PROMIS CATs averaging about 4.7 items per domain with a wider accurate
  range than any fixed short form, and optimized stopping rules reaching mean 4.8 to 5.6 items at
  reliability above 0.90 (from PubMed 31595451 and related, https://pubmed.ncbi.nlm.nih.gov/31595451/;
  exact figures UNVERIFIED, not opened directly). A real-world burden anchor that was opened
  directly: an 11-domain PROMIS CAT battery took about 11.9 minutes in 143 patients, with
  PROMIS-legacy correlations r = 0.61 to 0.82 (https://pmc.ncbi.nlm.nih.gov/articles/PMC3457915/,
  2011).
- Tang J, Shang Y, "AURA: A Reinforcement Learning Framework for AI-Driven Adaptive Conversational
  Surveys," arXiv:2510.27126, 2025-10-31, https://arxiv.org/abs/2510.27126. The closest existing
  work to "an LLM runs an adaptive loop": epsilon-greedy policy over follow-up question types,
  scored on a four-dimension quality metric, +0.076 mean quality gain vs non-adaptive baseline
  (p = 0.044, d = 0.66). **Stops at:** it optimizes open-ended follow-up quality, not latent-trait
  standard error. No IRT, no stopping rule on precision.

**Where the whole cluster stops:** no work puts a psychometric stopping rule (an SE threshold on
theta) inside a generative dialogue. CAT's guarantee has never been ported into conversation, and
conversation's adaptivity has never been given CAT's comparability argument.

### 2.4 The equivalence playbook this study should borrow, and the standard that does not exist

This is the most useful thing in the whole scan, because it means the evaluation bar does not have
to be invented.

- Coons SJ et al., ISPOR ePRO Good Research Practices Task Force Report, *Value in Health* 12(4),
  2009, https://doi.org/10.1111/j.1524-4733.2008.00470.x. Tiered framework: **minor** migrations
  (paper to screen, no content change) can be cleared with cognitive debriefing and usability
  testing; **substantive** migrations require full quantitative equivalence testing. An ISPOR task
  force updated this in 2023 to cover comparability across all modes of collection
  (https://pubmed.ncbi.nlm.nih.gov/37121630/, abstract UNVERIFIED).
- Gwaltney CJ, Shields AL, Shiffman S, "Equivalence of Electronic and Paper-and-Pencil
  Administration of Patient-Reported Outcome Measures: A Meta-Analytic Review," *Value in Health*
  11(2):322-333, 2008, https://doi.org/10.1111/j.1524-4733.2007.00231.x. Across 233 direct
  comparisons the mean mode difference averaged 0.2% of scale range and 93% of comparisons fell
  within plus or minus 5% of scale range. Numbers from search snippet, primary blocked, so treat the
  exact figures as UNVERIFIED, but the framework and the de facto 5% threshold are the precedent.
- FDA PRO guidance, 2009, https://www.federalregister.gov/documents/2009/12/09/E9-29273/guidance-for-industry-on-patient-reported-outcome-measures-use-in-medical-product-development-to,
  and the Patient-Focused Drug Development guidance series including the fit-for-purpose COA
  guidance finalized November 2025
  (https://www.fda.gov/drugs/development-approval-process-drugs/fda-patient-focused-drug-development-guidance-series-enhancing-incorporation-patients-voice-medical;
  Federal Register notice 2025-11-18,
  https://www.federalregister.gov/documents/2025/11/18/2025-20153/patient-focused-drug-development-selecting-developing-or-modifying-fit-for-purpose-clinical-outcome).
  The bar for any instrument is content-validity evidence from qualitative work with the target
  population plus item-level psychometrics.
- Reporting standards: CONSORT-AI and SPIRIT-AI exist (Liu X et al., *Nature Medicine* 26:1364-1374,
  2020, https://pmc.ncbi.nlm.nih.gov/articles/PMC7598943/), DECIDE-AI covers early live evaluation
  (https://www.nature.com/articles/s41591-022-01772-9, 2022). **No reporting standard specific to
  LLM-elicited self-report or PRO data was found.** Multiple targeted searches returned only the
  general AI-trial guidelines. Treat this as an absence, not an unverified presence.

**Implication:** a chat agent is obviously a "substantive" migration under Coons 2009, so the field's
own playbook says it needs a full quantitative equivalence study. That study has not been run. The
threshold to report against (mean difference within 5% of scale range, plus the invariance ladder)
is already agreed on by the community that would review the paper.

### 2.5 Conversational assessment, disclosure, and the mode effect that has been measured

- Lucas GM, Gratch J, King A, Morency L-P, "It's only a computer: Virtual humans increase
  willingness to disclose," *Computers in Human Behavior* 37:94-100, 2014,
  https://doi.org/10.1016/j.chb.2014.04.043. The canonical result: believing the interviewer was
  computer-controlled lowered fear of self-disclosure and impression management.
- A direct qualification, 2025: a three-arm randomized trial (N = 160, realistic virtual human vs
  text chatbot vs online questionnaire) found **more human likeness amplified social desirability
  and reduced disclosure** of sensitive health information
  (https://doi.org/10.1016/j.chb.2025.108683). First author UNVERIFIED. This runs opposite to the
  product intuition that a warmer agent gets more truth.
- **The nearest methodological precedent, and it is positive.** Serafimovska, Swavley, Zhang Qian Ao,
  Challinor, Florio, "Cognitive status assessment of older adults: test administration by
  conversational artificial intelligence (AI) chatbot," *Journal of Clinical and Experimental
  Neuropsychology*, 2025-07, https://doi.org/10.1080/13803395.2025.2542248, PMID 40794461 (abstract
  read directly via NCBI efetch). They automated the Telephone Interview for Cognitive
  Status-Modified as TICS-M-AI and ran four studies: concurrent validity against psychologist
  administration in the same 100 participants a week apart (r = 0.81, 88% classification agreement,
  kappa = 0.73); test-retest of the AI version (n = 82, r = 0.76, ICC = 0.72, 83% agreement,
  kappa = 0.65); a construct-validity replication of a published item-response-pattern result using
  TICS-M-AI data (n = 264); and a safety study comparing assessment-related distress rates across
  modes. Their conclusion is that TICS-M-AI "is reliable, valid, and equally safe with added
  advantages of lower cost, scalability, and broader accessibility."

  **What this changes and what it does not.** It changes the prior: a chatbot-administered
  instrument cleared a crossover comparison against clinician administration at n = 100, which is
  both an encouraging feasibility signal and a demonstration that the sample sizes involved are
  small. It does not answer the question in section 1 for three reasons. TICS-M is a **performance
  test**, not a self-report scale, so it has a correct answer and therefore a criterion, which is
  exactly what psychological self-report lacks (section 6). They report concurrent validity and
  test-retest, **not an invariance ladder**, so whether the two modes share a measurement model is
  still untested. And the AI arm has no adaptivity manipulation, so it sits at roughly arm 1 in
  section 4.2 and says nothing about the frontier. A secondary search snippet suggested the
  discussion also reports a mode effect and offers "absence of adaptive conversational cues" and
  "reduced perceived social presence" as explanations, and that ICC 0.72 compares against 0.85 for
  traditional administration; none of that appears in the abstract, so treat it as UNVERIFIED until
  the full text is read. **Read this paper first.** It is the closest thing to the proposed design
  that exists, and it should shape the protocol rather than be discovered after it.
- Tourangeau R, Yan T, "Sensitive Questions in Surveys," *Psychological Bulletin* 133(5):859-883,
  2007, https://doi.org/10.1037/0033-2909.133.5.859. Their meta-analysis of seven studies found no
  significant effect of computerized self-administration on social-desirability bias. The "make it a
  computer and people tell the truth" intuition was already weakly supported before chatbots.
- Interviewer variance: ICC above 0.10 is treated as substantively important, and attitudinal,
  non-factual, complex and open-ended items are the most affected, confirmed across 29,000
  intra-interviewer correlations in 28 ESS countries (Stefkovics et al., *Sociological Methods &
  Research*, 2025, https://doi.org/10.1177/00491241251372509). Those are exactly the item types
  psychological scales are made of.
- Maharjan R, Rohani DA, Bækgaard P, Bardram J, Doherty K, "Can We Talk? Design Implications for the
  Questionnaire-Driven Self-Report of Health and Wellbeing via Conversational Agent," *CUI '21*,
  https://doi.org/10.1145/3469595.3469600, and the companion empirical study in *IEEE Pervasive
  Computing*, 2022, https://doi.org/10.1109/MPRV.2022.3147374: N = 22 people with affective
  disorders, agent rated novel and attractive with engagement similar to a web app, but users found
  discrete response options "more habitable" than open-ended speech.
- Evaluating conversational agents for mental health, scoping review, *JMIR*, 2023,
  https://www.jmir.org/2023/1/e44548: only 12 of 75 user-experience outcomes (16%) included or cited
  validity evidence.

### 2.6 LLM interviewers, 2023 to 2026

All verified against arXiv or SSRN metadata directly.

- Chopra F, Haaland I, "Conducting Qualitative Interviews with AI," CESifo Working Paper 10666,
  first posted 2023-09, https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4583756. 381 AI-led
  interviews on stock-market non-participation; richer than open-text survey fields, predictive of
  behavior six months later. Still a working paper; a journal version was not confirmed (UNVERIFIED).
- Geiecke L, Jaravel X, "Conversations at Scale: Robust AI-led Interviews with a Simple Open-Source
  Platform," CEPR DP19705, 2024-10, https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4974382.
  Headline: a 142% increase in words written versus conventional open-text fields.
- Wuttke A, Lang MM, Klamm C, Würschinger Q, Kreuter F, "AI Conversational Interviewing: Scaling Up
  Semi-Structured and In-depth Interviews," arXiv:2606.20064, 2026-06-18,
  https://arxiv.org/abs/2606.20064 (title, date and authors verified via arXiv metadata). Current
  frontier baseline.
- Tirumala S, Jain N, Leybzon DD, Buskirk TD, "Mic Drop or Data Flop? Evaluating the Fitness for
  Purpose of AI Voice Interviewers," arXiv:2509.01814, 2025, https://arxiv.org/abs/2509.01814.
  Position paper: AI interviewers exceed IVR for both quantitative and qualitative collection, with
  three named deficits, real-time transcription error rates, limited emotion detection, and uneven
  follow-up quality.
- Keep separate, because it is simulation and not measurement: Park JS, Zou CQ, Kamphorst J, Egan N
  et al., "LLM Agents Grounded in Self-Reports Enable General-Purpose Simulation of Individuals,"
  arXiv:2411.10109, 2024-11-15, https://arxiv.org/abs/2411.10109 (this is the paper circulated as
  "Generative Agent Simulations of 1,000 People"; the current arXiv title is the one given here,
  verified 2026-09-13). N = 1,052 interviewed once to build generative personas. This is category C
  from section 1, the reductio arm, not the instrument.

**Where this cluster stops:** none of the three academic LLM-interviewer papers validates against a
standardized instrument with known reliability. They demonstrate richer text and downstream
prediction. Richer text has never been shown to equal a better measurement on an instrument with a
psychometric bar.

### 2.7 EMA, passive sensing, digital phenotyping

The infrastructure and the honest effect sizes, which matter because they set the realistic ceiling
for anything in category B or D.

- Canonical methodology: Shiffman S, Stone AA, Hufford MR, *Annual Review of Clinical Psychology*
  4:1-32, 2008, https://doi.org/10.1146/annurev.clinpsy.3.022806.091415; Trull TJ,
  Ebner-Priemer UW, same series 9:151-176, 2013,
  https://doi.org/10.1146/annurev-clinpsy-050212-185510.
- Reporting and item infrastructure: CREMAS checklist, Liao Y et al., *JMIR* 18(6):e151, 2016,
  https://doi.org/10.2196/jmir.4954; the ESM Item Repository, https://www.esmitemrepository.com and
  https://osf.io/kg376/; ESM-Q consensus quality tool, *Behavior Research Methods*, 2025,
  https://doi.org/10.3758/s13428-025-02626-1; Fritz J et al., "So You Want to Do ESM? 10 Essential
  Topics," *AMPPS*, 2024, https://doi.org/10.1177/25152459241267912.
- Compliance baselines: 79% pooled across 496 samples / 677,536 participants (Wrzus & Neubauer 2023,
  https://doi.org/10.1177/10731911211067538); ~75% in substance-use EMA across 126 studies / 19,431
  participants (Jones et al. 2019, https://doi.org/10.1111/add.14503); 72.9% in clinical-high-risk
  psychosis, 78.1% adults vs 69.3% children and adolescents
  (https://pmc.ncbi.nlm.nih.gov/articles/PMC9116495/, 2022); 77.5% pooled in older-adult behavioral
  nutrition and activity studies (https://doi.org/10.1186/s12966-024-01629-z, 2024).
- The effect-size collapse story, which is the single most useful cautionary result in this section.
  Saeb S et al., *JMIR* 17(7):e175, 2015, https://doi.org/10.2196/jmir.4273 (page
  https://www.jmir.org/2015/7/e175/) found GPS location entropy correlating r = -0.63 with PHQ-9 in
  28 analyzed participants. Currey D, Torous J, *BJPsych Open*, 2022,
  https://doi.org/10.1192/bjo.2022.507, with 147 students and 270 weeks of mindLAMP data, found
  passive-feature to survey correlations "on the order of 0.1," against 0.54, above 0.6, and 0.38 in
  the small early studies. Pratap A et al., *Depression and Anxiety*, 2018,
  https://doi.org/10.1002/da.22822, N = 271, found passive sensors performed poorly for
  population-level daily mood prediction, with idiographic models more promising.
- A 2026 systematic review of passive-sensing relapse prediction states that most digital phenotype
  studies "suffer from poor replicability, often fail to detect clinically relevant events, and use
  measures of depression that are not validated"
  (https://doi.org/10.1186/s12888-026-08157-z, https://pmc.ncbi.nlm.nih.gov/articles/PMC13330314/).
- Platforms that are genuinely free or open for a solo researcher: AWARE (Apache 2.0,
  https://awareframework.com/), Beiwe (https://github.com/onnela-lab/beiwe-backend), RADAR-base
  (Apache 2.0, https://radar-base.org/about/), mindLAMP (https://www.digitalpsych.org/mindlamp.html),
  SEMA3 (https://doi.org/10.3758/s13428-024-02445-w), ExpiWell free tier, m-Path free up to 50
  participants per year then from EUR 1,599 (https://m-path.io/pricing/). The open ones require
  self-hosting a backend, which is a time cost rather than a license cost.
- Closest framing of the gap from inside this literature: Chen C et al., "Toward a Unified Metadata
  Schema for Ecological Momentary Assessment with Voice-First Virtual Assistants," *CUI 2021*,
  https://doi.org/10.1145/3469595.3469626, PMC11257172: "Collecting real-time and temporally-dense
  participants' self-report EMA data in an ecologically valid setting is valuable, yet challenging,
  especially for under-represented groups."
- A very recent entrant worth watching: "Conversational, Longitudinal, Ecological Assessment
  (CLEA)," medRxiv preprint 2026, https://www.medrxiv.org/content/10.64898/2026.01.20.26344494
  (existence confirmed, content UNVERIFIED, PDF text extraction failed). If this is what its title
  suggests, it is the nearest competitor to category B and should be read before any B work starts.

### 2.8 Lifelogging, quantified self, and the products

- Lifelog review does improve episodic recall in clinical case studies, sometimes dramatically
  (Hodges S et al., SenseCam, UbiComp 2006,
  https://www.microsoft.com/en-us/research/wp-content/uploads/2006/09/sensecam-ubicomp-2006-camera-ready.pdf;
  Silva et al. PRISMA review, *Neuropsychology Review*, 2016,
  https://doi.org/10.1007/s11065-016-9337-x), but the benchmarks in this field measure retrieval
  quality, not measurement validity (NTCIR-14 Lifelog-3 overview,
  https://research.nii.ac.jp/ntcir/workshop/OnlineProceedings14/pdf/ntcir/01-NTCIR14-OV-LIFELOG-GurrinC.pdf).
  Survey: Gurrin, Smeaton, Doherty, "LifeLogging: Personal Big Data," *FnT IR* 8(1), 2014,
  https://doras.dcu.ie/19998/1/FnTIR_lifelogging_journal.pdf.
- Abandonment is the dominant outcome in self-tracking, documented qualitatively rather than as a
  survival curve: Clawson J et al., "No Longer Wearing," UbiComp 2015,
  https://www.andrewmiller.net/pdf/2015_Clawson.pdf; Lazar A et al., "Why We Use and Abandon Smart
  Devices," UbiComp 2015, https://doi.org/10.1145/2750858.2804288; Epstein DA et al., "A Lived
  Informatics Model of Personal Informatics," UbiComp 2015,
  https://homes.cs.washington.edu/~jfogarty/publications/ubicomp2015.pdf; Choe EK et al.,
  "Understanding Quantified-Selfers' Practices," CHI 2014, https://doi.org/10.1145/2556288.2557372.
  No clean pooled attrition percentage exists; any specific figure should be treated as UNVERIFIED.
- Products: not one AI journaling, coaching or memory product surveyed outputs a validated
  psychometric score as a first-class feature. Rosebud (https://www.rosebud.app), Mindsera,
  Bearable (https://bearable.app), Exist.io (https://exist.io), Oura Advisor
  (https://www.businesswire.com/news/home/20250331565896/en/, 2025), Whoop Coach. Limitless was
  acquired by Meta in December 2025 with pendant sales halted and support ending late 2026
  (https://legendmemory.ai/blogs/the-archive/limitless-pendant-discontinued-the-best-alternatives-in-2026,
  2026; secondary source, UNVERIFIED against a Meta or Limitless announcement). Apple ships a
  consumer State of Mind logging feature and exposed `HKStateOfMind` plus Depression Risk and Anxiety
  Risk types to third parties at WWDC24 (https://developer.apple.com/videos/play/wwdc2024/10109/).
- Commercial AI interviewers exist and publish no psychometrics: Outset (https://outset.ai), Listen
  Labs (https://listenlabs.ai), Genway (https://www.genway.ai), Versive
  (https://www.getversive.com). Wondering entered voluntary liquidation on 2025-10-02 (UNVERIFIED
  against a filing). The absence of published validation across this whole commercial category is
  the strongest signal that the measurement question is open rather than quietly solved.

### 2.9 The one-line summary of the scan

Three literatures, each mature, none of which cites the others' validity methods: survey chatbots
measure response quality, clinical conversational agents measure disclosure and outcomes, and CAT
measures precision per item. A conversational instrument that is evaluated against the ePRO
equivalence playbook does not exist in any of them.

---

## 3. Measurement risks, and the honest ledger

Which risks the agent actually improves, which it worsens, and which it makes *unmeasurable*, which
is the category people forget.

### Improves

| Risk | Why the agent helps | Evidence |
|---|---|---|
| Item comprehension error | The agent can answer "what counts as nearly every day." This is precisely Weinfurt's argument, and the reason cognitive interviewing exists in the FDA content-validity pathway at all. | https://doi.org/10.1186/s41687-025-00950-w (2025); FDA PRO guidance 2009 |
| Item nonresponse and abandonment mid-instrument | 99.82% completion on a chatbot PHQ-9 in 3,902 people. | https://doi.org/10.3389/fdgth.2021.645805 (2021) |
| Response-option mismatch | Free text can record "between a 2 and a 3" and then resolve it, instead of forcing a guess. | Users nonetheless preferred discrete options as "more habitable": https://doi.org/10.1109/MPRV.2022.3147374 (2022) |
| Richness for qualitative purposes | 142% more words than open-text fields; thematically richer than survey text boxes. | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4974382 (2024); https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4583756 (2023) |

Note what is *not* on this list. **Burden is not an improvement** (CAT already gets to ~5 items at
reliability above 0.90, section 2.3). **Compliance is not a safe bet** either: assessment frequency
did not predict EMA compliance in a 496-sample meta-analysis
(https://doi.org/10.1177/10731911211067538, 2023), so making each prompt nicer has no established
mechanism for raising it.

### Worsens

| Risk | Why the agent hurts | Evidence |
|---|---|---|
| Standardization and measurement invariance | Adaptive rephrasing changes the stimulus per person. CAT has a comparability theory for item selection; nothing has one for item rewording. | Meredith 1993 https://doi.org/10.1007/bf02294825; Vandenberg & Lance 2000 https://doi.org/10.1177/109442810031002 |
| Interviewer variance, now as model variance | Attitudinal, non-factual, complex and open-ended items carry the largest interviewer effects, and ICC above 0.10 counts as important. Psychological scales are made of exactly those items. | https://doi.org/10.1177/00491241251372509 (2025) |
| Leading prompts | Documented LLM deference to the user in follow-up turns. In an interview, that is the misinformation-effect mechanism with a motivated confabulator on the other end of it. | Sharma M et al., arXiv:2310.13548 (2023-10-20) https://arxiv.org/abs/2310.13548; Perez E et al., arXiv:2212.09251 (2022) https://arxiv.org/abs/2212.09251 |
| Experimenter demand | A conversation carries far more cues about what answer is wanted than a form does, and the agent generates those cues afresh each turn. Unlike most threats on this list, this one has a bounding method that can be ported directly (see 4.3, outcome 8). | de Quidt J, Haushofer J, Roth C, "Measuring and Bounding Experimenter Demand," 2017/2018, https://doi.org/10.3386/w23470 |
| Social desirability | The intuition that a machine gets more truth is weakly supported at best, and a more human-feeling agent appears to make it worse. | Tourangeau & Yan 2007 https://doi.org/10.1037/0033-2909.133.5.859 (no significant effect of computerized administration, 7 studies); https://doi.org/10.1016/j.chb.2025.108683 (2025, human likeness raised social desirability and lowered disclosure) |
| Reactivity | A conversation is a more salient stimulus than a form, so if reactivity scales with salience, conversation is the worse mode. EMA reactivity evidence is mixed and mostly small and early-days, which means it is unbounded here, not absent. | Null side: https://pmc.ncbi.nlm.nih.gov/articles/PMC9971140/ (2023). Positive side: measurement reactivity in movement-behavior EMA, first 1-3 days elevated, *J Meas Phys Behav* 7(1), 2024, https://pmc.ncbi.nlm.nih.gov/articles/PMC12922600/ |
| Mode-level score shift | Unresolved rather than established. The one crossover study of a chatbot-administered instrument reported concurrent validity r = 0.81 and concluded in favor of equivalence, but it tested a performance instrument with no adaptivity manipulation and reported no invariance ladder, so a self-report mode shift is neither shown nor ruled out. | Serafimovska et al. 2025, https://doi.org/10.1080/13803395.2025.2542248, PMID 40794461 (abstract verified) |
| Privacy exposure | A form yields a 0 to 3 rating. A conversation yields a verbatim transcript of the worst week of someone's life, and on a free-tier API that transcript leaves the device. | FTC enforcement precedent against mental-health apps: *In the Matter of BetterHelp, Inc.*, FTC file 2023169, final decision and order 2023-07-14, banning the sharing of sensitive mental-health data for targeted advertising and requiring a $7.8M payment, https://www.ftc.gov/legal-library/browse/cases-proceedings/2023169-betterhelp-inc-matter |
| Clinical-safety boundary | A fixed form with PHQ-9 item 9 returns a number. A probing conversation produces a person saying something, which creates a duty the form does not. | Documented harm precedent: NEDA/Tessa 2023. Mitigation in section 5. |

### Makes unmeasurable, which is the worst category

1. **Missingness stops being diagnosable.** On a form, a skipped item is visibly skipped, and the
   missingness mechanism can be reasoned about. Under adaptive administration you cannot distinguish
   "the respondent declined" from "the agent decided not to ask," and the second is missing not at
   random by construction. This is fixable only in the build: **log every item the agent considered,
   not just the ones it asked**, with the reason for each skip. That is a measurement requirement
   that flows directly into the data model (section 5).
2. **Longitudinal invariance stops being testable.** If items are generated fresh and conditioned on
   prior sessions, there is no fixed item set to test across occasions. Any category-B agent must
   freeze its item wording or abandon the standard diagnostic. There is no third option.
3. **Between-run variance is invisible without deliberate instrumentation.** The same respondent
   cannot be re-run through the same session. But the *scoring* step can be re-run arbitrarily many
   times on the same transcript, which is what makes section 4's Phase 0 possible.

### Temporal aggregation, worth stating separately

Group-level structure does not transfer to individuals: in a direct test, group-level and
individual-level results diverged substantially (Fisher AJ, Medaglia JD, Jeronimus BF, *PNAS*, 2018,
https://doi.org/10.1073/pnas.1711978115), the general argument being Molenaar's idiographic
manifesto (*Measurement*, 2004, https://doi.org/10.1207/s15366359mea0204_1). Any agent that
aggregates a week of conversation into one score is making an ergodicity assumption, and the
aggregation window should be treated as a reported analytic choice rather than an implementation
detail.

---

## 4. The research contribution

### 4.1 The claim to test

Administering a fixed, validated instrument through an LLM agent is a "substantive" mode migration
under the ePRO framework (Coons 2009), and therefore requires a quantitative equivalence study that
has never been run. Run it, and run it as a **dose-response on adaptivity** rather than a two-arm
chatbot-versus-form comparison, because the two-arm comparison has already been done several times
with mixed results (section 2.2) and because the dose-response is what produces a usable answer:
not "does it work" but "how much conversation can you add before the scores stop being comparable."

### 4.2 Design

Within-person crossover, order randomized, one form reference plus four agent arms that differ only
in adaptivity:

| Arm | What the agent does | What it isolates |
|---|---|---|
| 0 | Static web form, standard presentation | Reference mode |
| 1 | Reads items verbatim, fixed order, accepts only the scale's response options | The medium alone, zero adaptivity |
| 2 | Verbatim items plus clarifications drawn from a fixed, pre-written clarification bank | Bounded clarification |
| 3 | Verbatim items plus free LLM clarification and one probe when an answer is vague | Unbounded clarification, the Weinfurt vision |
| 4 | Paraphrases each item into the respondent's own vocabulary, probes freely | Full tailoring |

Plus, if budget allows, arm C: the agent answers on the respondent's behalf from a prior interview,
as the reductio floor (section 1). Its scores bound how much of the measure was ever about the
person rather than about the population.

**Instruments.** Two scales with different sensitivity. One low-stakes (PANAS, or a sleep or fatigue
PROMIS short form; PROMIS is free for non-commercial research,
https://www.healthmeasures.net). One clinically flavored but safe to administer: **PHQ-8, not
PHQ-9.** PHQ-8 drops the suicidality item and is an established general-population measure
(Kroenke K et al., *J Affect Disord*, 2009, https://doi.org/10.1016/j.jad.2008.06.026), which is
also what BRFSS does. This is a design choice, not squeamishness: it removes the single item most
likely to turn a measurement session into a crisis-response obligation.

### 4.3 Outcomes, each with a pre-registered threshold

1. **Invariance ladder across mode**: configural, metric, scalar, with pre-registered delta-CFI and
   delta-RMSEA cutoffs (Meredith 1993; Vandenberg & Lance 2000). The primary result.
2. **Mean-difference bound**: report against the ePRO field's de facto criterion, mean mode
   difference within plus or minus 5% of scale range (Gwaltney 2008). Borrowed, not invented.
3. **Reliability by mode**: alpha and omega per mode, plus cross-mode ICC. Benchmark against
   TICS-M-AI, the nearest precedent, which reached concurrent validity r = 0.81 with 88%
   classification agreement against clinician administration and test-retest ICC 0.72 for the AI
   mode itself (Serafimovska et al. 2025, https://doi.org/10.1080/13803395.2025.2542248, section 2.5).
   Those are the numbers to beat or to fall short of visibly.
4. **Criterion validity.** The hard part, because for subjective constructs there is no criterion
   outside self-report. The OECD states the problem plainly for subjective well-being: "there is no
   way for a person other than the respondent to provide the correct answer"
   (https://www.ncbi.nlm.nih.gov/books/NBK189563/). Two cheap options that are standard anyway:
   informant report (one acquaintance rates the respondent, the norm in personality research, where
   self-report to informant correlations run about 0.28 to 0.58 for well-being per Pavot and
   Diener 1993, UNVERIFIED at primary level) and a same-period EMA or diary average used as the
   criterion for the retrospective scale. Report the criterion's own ceiling alongside the result,
   because a correlation of 0.4 against a criterion that tops out at 0.5 is a different finding from
   a correlation of 0.4 against a clean one.
5. **Response distortion**: sensitive-item endorsement rates by mode, plus an impression-management
   subscale administered once outside the agent.
6. **Burden**: completion time, items administered, self-reported burden, dropout.
7. **Scorer reliability**: see Phase 0 below. This is the one that can be measured first.
8. **A demand bound.** Borrow de Quidt, Haushofer and Roth's design (https://doi.org/10.3386/w23470):
   run two extra cells in which the agent carries an explicit cue about the expected direction of
   response, one positive and one negative, and use the spread between them to bound how much an
   agent-administered score can be moved by conversational cueing. This turns "the agent might lead
   the respondent" from a caveat into a reported interval, and it costs two extra cells rather than a
   new study. It is the single highest-value addition to the design.

### 4.4 The negative-result path, and why it is the strong version

Three clean negative results, any one of which is publishable as stated:

- **Scalar invariance fails at every adaptivity level above 0.** Then agent-administered scores are
  not on the same metric as form scores, LLM-PROMs as described by Terheyden cannot be compared to
  the established PROMs they are meant to complement, and the field has a concrete reason to require
  frozen item wording. This is the most likely outcome and the most useful one.
- **Scalar invariance holds at arms 1 and 2 and fails at 3 and 4.** Then the frontier has a
  location, and the paper reports the exchange rate: bounded clarification is free, free-form
  probing is not. This is the best outcome for everyone including the people building products.
- **Scorer reliability alone is too low to matter** (Phase 0 below). Then nothing built on top can
  exceed it, the whole class is capped, and that cap is the contribution.

None of these requires the agent to win. The paper is informative in every branch, which is the
property to want.

### 4.5 Phase 0: the study that needs no participants and no IRB

This is the part to run first, and it is a complete study on its own.

**Question.** How reliably does an LLM map a free-text response onto an item's response category,
and how much does that mapping move under perturbations that should not matter?

**Why it bounds everything.** Every conversational instrument has a scoring step: free text in,
ordinal category out. If that step has ICC 0.7 under innocuous perturbation, no administration
design on top of it can do better. The ceiling is the product of the administration and scoring
reliabilities, and Phase 0 measures the second factor with zero human subjects.

**There is already an existence proof that this step is tunable, which makes the study worth running
rather than obviously doomed.** An LLM estimating energy and macronutrients from 24-hour dietary
recall text on 11,281 NHANES adolescents went from MAE 652 kcal and Lin's concordance below 0.46
zero-shot to MAE 171 to 191 kcal and concordance above 0.89 with 10-shot fine-tuning
(Carrillo-Larco RM, arXiv:2509.13268, 2025-09, https://arxiv.org/abs/2509.13268). That is accuracy
on a continuous quantity rather than reliability on an ordinal category, so it does not answer the
Phase 0 question. It does establish that the free-text-to-number step is not hopeless and that
few-shot calibration moves it a great deal, which is itself a reason the perturbation sweep matters:
if ten examples move accuracy that far, prompt-level choices are a live source of variance that
nobody is currently reporting.

**Perturbations to sweep**: sampling seed and temperature, model swap (two families, as in
`SPEC.md` section 2.3), item paraphrase, response-option order, position of the item in the
transcript, and presence or absence of surrounding conversational context.

**Stimuli, in order of how fast they can be obtained:**

1. **Synthetic transcripts with planted ground truth**, generated at controlled latent levels. This
   is exactly the machinery ghost-respondents already has, where machine responses are generated at
   three coupling levels against known trait values (`SPEC.md` section 2.3). Ground truth is true by
   construction, no DUA, available immediately, and it reuses code already on disk.
2. **The essays corpus already at `lane3-testbed/data/essays/essays.csv`** (8.2 MB on disk,
   Pennebaker-King stream-of-consciousness essays with binary median-split Big Five labels;
   original source https://doi.org/10.21227/dyfp-7f45, mirror and encoding caveats documented in
   `lane3-testbed/loaders/essays_loader.py`). Binary labels limit the accuracy arm but are fine for
   the reliability arm. Zero marginal cost.
3. **DAIC-WOZ / E-DAIC** (https://dcapswoz.ict.usc.edu/), 189 interview sessions averaging 16
   minutes with transcripts, from the Ellie virtual-interviewer corpus. Item-level PHQ-8 scores are
   widely reported to ship with the AVEC challenge label files but the dataset page did not confirm
   this, so treat item-level availability as UNVERIFIED until the labels are in hand. Access needs a
   signed form submitted from an academic email address, which is a live risk given he graduated in
   May 2026.
4. **LifeSnaps** (https://doi.org/10.1038/s41597-022-01764-x, Zenodo DOI
   10.5281/zenodo.7229547), 71 participants, 4+ months of Fitbit data with SEMA3 EMA and validated
   surveys, openly downloadable. Best single corpus if the work later extends toward category B.
5. **MIDUS National Study of Daily Experiences** via ICPSR (https://www.icpsr.umich.edu/web/NACDA/studies/3725),
   8-day telephone diary plus salivary cortisol, free, no institutional affiliation required. The
   fastest real-data option and the one with an actual biological signal alongside diary self-report.

**Deliverable.** A reliability and sensitivity table for LLM item scoring, with the perturbation
budget stated. That is a methods paper, it needs no participants, and it slots directly into the
calibration-ledger machinery in `quantpsych-agent` where every reported number resolves to a
hashed artifact.

### 4.6 Human-subjects constraints, stated plainly

**He cannot be PI at UW-Madison, and this is decisive.** UW-Madison policy states that
"undergraduate students, graduate students, postdoctoral scholars, visiting professors, visiting
academic staff and those with adjunct or zero-dollar appointments are not eligible to apply for
limited PI status" (https://research.wisc.edu/compliance-policy/principal-investigator-status/).
He graduated in May 2026, which puts him further from eligibility, not closer. Submissions run
through ARROW and require a NetID plus CITI training
(https://research.wisc.edu/compliance-policy/human-research-protection-program/education-and-social-behavioral-science-irb/arrow-ed-sbs-irb/,
https://irb.wisc.edu/submission-guidance/new-study/). No published review turnaround figure was
found on any reachable UW HRPP page, so do not plan against an assumed timeline.

Therefore: **the human-subjects arms of section 4.2 are not available to him now.** The play is to
run Phase 0, write the protocol, and bring the protocol to a lab as a ready-to-submit first-year
project. For a quant-psych application that is a stronger artifact than a half-run study.

For completeness on what the regulations would allow with a faculty PI: a survey or interview study
of adults is exempt under 45 CFR 46.104(d)(2), which explicitly names "survey procedures, interview
procedures, or observation of public behavior (including visual or auditory/audio recording)," with
the identity or risk conditions in (i) to (iii); (d)(3) covers benign behavioral interventions on
adults, but the exemption is void if deception is used without prospective authorization
(https://www.law.cornell.edu/cfr/text/45/46.104). Secondary use of public de-identified data is
generally not human-subjects research; the OHRP decision charts are the authority
(https://www.hhs.gov/ohrp/regulations-and-policy/decision-charts-2018/index.html).

Self-experimentation is not a loophole. The Common Rule's trigger is a systematic investigation
designed to contribute to generalizable knowledge (45 CFR 46.102(l)), and at least one university
IRB requires review even when the sole subject is the investigator
(https://www.uh.edu/research/compliance/irb/policies/self-experimentation/index.php). Use self-use
for engineering validation, not as data in a paper.

**Do not price a study against MTurk.** Amazon Mechanical Turk closes permanently on 2026-09-30
per its own pricing page: "Following an assessment, we've made the decision to close Amazon
Mechanical Turk, effective September 30, 2026" (https://www.mturk.com/pricing, fetched
2026-09-13). That is 17 days from today. Prolific's allowed minimum is GBP 6.00 / USD 8.00 per hour
with a recommended USD 12.00, and the platform fee is roughly 33% for academic customers
(https://researcher-help.prolific.com/en/articles/445266-how-much-should-i-pay-participants,
https://www.prolific.com/pricing). At USD 12/hr for a 30-minute two-mode session that is about
USD 8 per participant, so a 300-person crossover is roughly USD 2,400. Real money, and out of scope
at a zero budget.

### 4.7 Where it would go

*Psychological Methods* or *Assessment* for the invariance framing; *Quality of Life Research* or
*Journal of Patient-Reported Outcomes* for the PRO framing, and JPRO is where both the Terheyden
and Weinfurt commentaries ran, so the editors have already signaled interest in exactly this
question; *Behavior Research Methods* for the Phase 0 scoring-reliability paper. Report against
CONSORT-AI-style items even though no LLM-self-report standard exists, and say that no such
standard exists.

---

## 5. Buildability

### 5.1 Smallest useful thing

Two components, both of which are research instruments rather than products.

**`score`**: free text plus an item plus its response options in, an ordinal category out, with the
full perturbation sweep wired in as a first-class feature rather than an experiment script. This is
Phase 0's entire apparatus. It is not a chat interface at all.

**`administer`**: a scripted instrument runner with adaptivity as a configuration level 0 to 4, and
a log that records every item **considered**, not only those asked. Output is a transcript plus a
scored response vector plus an administration log. That is the artifact a lab can put in front of
participants the day an IRB clears.

Nothing else. No app, no mobile client, no passive sensing, no dashboard.

### 5.2 Architecture

Python, one package, no agent framework, matching the posture already established in
`quantpsych-agent` ("no agent framework, no paid API in the offline path, no service to run").

```
items/          item banks as frozen JSON: text, options, scoring, clarification bank
agent/          score() and administer(), plus one backend interface
analysis/       invariance ladder and reliability, in R via lavaan and mirt
```

Three directories, because Phase 1 is two functions and a sweep. `score()` and `administer()` share
the backend interface and the item banks, so splitting them into separate packages buys nothing;
split them when a second caller appears. Backends are one protocol with a local implementation, a
free-tier implementation, and a scripted one for tests, which is three implementations of a real
interface rather than speculative flexibility. The claim ledger is reused from `quantpsych-agent`
rather than rebuilt.

The analysis layer should be R, because `lavaan`, `mirt`, `psych` and `survey` are already installed
and the vault's tooling hub records that decision
(`03-Resources/_Dev-Tooling Hub.md`, "Survey and health-data analysis (R)").

### 5.3 Data model

Two tables in Phase 1. Three more in Phase 2. Do not build Phase 2's schema during Phase 1.

**Phase 1:**

1. `response`: id, source (corpus or synthetic spec), item id, raw text, planted level where known.
2. `score_replicate`: response id, perturbation spec, scorer model, scorer seed, scored category.
   This is where Phase 0's reliability coefficients come from, and it is the only table the Phase 0
   result depends on.

**Phase 2, when `administer` exists:**

3. `session`: id, respondent id, arm, instrument, mode, model id, seed, timestamps.
4. `turn`: session id, index, speaker, text, token counts.
5. `item_event`: session id, item id, status in {considered, asked, answered, skipped}, reason for
   skip, turn index. **This one exists for a measurement reason, not an engineering one: without it
   the missingness mechanism is not recoverable** (section 3). It is the one table in the whole
   design that a normal engineer would not think to add.

### 5.4 Privacy model

Transcripts are the sensitive artifact, not the scores. Three rules:

1. **Local-first for any real transcript.** Self-use and any pilot runs use a local model so
   nothing leaves the machine. Note the standing decision against local models on this hardware
   (vault tooling hub, "No local model, deliberately," 2026-08-16: a 15.7 GB mmap on a 24 GB machine
   held the page cache under permanent pressure). The resolution is an 8B-class quantized model,
   which was named in that same note as the workload that would have been fine, and which is enough
   for a scoring step.
2. **Separate the transcript store from the score store**, with the score store carrying no verbatim
   text. Analysis runs on scores.
3. **Free-tier terms are a disclosure item.** None of the free tiers reviewed states that research
   use is a permitted category; they are framed for evaluation and prototyping. Google's logs policy
   states logging is "only available for billing-enabled projects"
   (https://ai.google.dev/gemini-api/docs/logs-policy, https://ai.google.dev/gemini-api/docs/rate-limits),
   which is the most favorable primary-source language found and which contradicts several
   third-party summaries claiming free-tier retention. Groq's free-tier numbers were not exposed on
   its docs page (https://console.groq.com/docs/rate-limits); commonly cited figures of ~30 requests
   per minute and ~1,000 per day are UNVERIFIED. Any protocol must disclose that a vendor's
   free-tier terms may permit human review of transcripts.

### 5.5 Clinical-safety boundary

State it in the repo README, not just in a paper:

- The instrument measures. It does not screen, diagnose, or advise. No feedback of scores to the
  respondent during a session.
- PHQ-8 rather than PHQ-9, so the suicidality item is not administered (section 4.2).
- A keyword and classifier escalation path that ends the session and surfaces standard crisis
  resources, logged as an event. This exists because free-text probing surfaces disclosures a fixed
  form never would, which is a duty the form does not create.
- No claim of clinical validity anywhere in the repo or the paper.

The boundary is now a legal one, not only an ethical one. Illinois enacted the Wellness and
Oversight for Psychological Resources Act, which is already being analyzed in the law reviews
(*SMU Science and Technology Law Review* 29(1), 2026, https://doi.org/10.25172/smustlr.29.1.5;
the statute's text was not read directly, so its exact prohibitions are UNVERIFIED here). The
takeaway does not depend on the details: a state has legislated on AI and psychological services,
so an instrument that measures must say in writing that it does not treat, and must be built so that
the claim is true.

### 5.6 Cost

Zero, and the zero is real rather than aspirational:
- Local 8B-class model for transcript-touching work.
- Free-tier hosted models for synthetic-stimulus generation, which touches no personal data.
- R and lavaan and mirt, already installed.
- Corpora: synthetic and essays.csv are on disk now; MIDUS NSDE and LifeSnaps are free downloads;
  DAIC-WOZ is free but gated.

### 5.7 What waits for an IRB

| Buildable now | Waits |
|---|---|
| `score` plus the full perturbation sweep | Any arm with recruited participants |
| Synthetic-stimulus generation at planted trait levels | Informant-report criterion |
| `administer` with all five arms, exercised against scripted and synthetic respondents | Sensitive-item endorsement comparison |
| Self-use for engineering validation, not as paper data | The invariance ladder on real respondents |
| Reanalysis of MIDUS NSDE, LifeSnaps, and (if granted) DAIC-WOZ | Anything reported as a human-subjects finding |

### 5.8 Effort, in agent rounds

Per the standing rule, no calendar time.

- Phase 1, `score` plus the sweep plus the Phase 0 result: roughly 1 discovery round, 3 to 4
  implementation rounds, 2 verification rounds, 1 to 2 rework. The synthetic-stimulus generator is
  mostly a port of existing ghost-respondents code, which is what keeps this small.
- Phase 2, `administer` with the five arms and the item-event log: roughly 1 discovery, 3
  implementation, 2 verification, 1 rework.
- The protocol document for a future IRB submission: 1 to 2 rounds, and it should be written while
  Phase 2's arms are fresh, since the arms *are* the protocol.

### 5.9 Run the spec-kit flow first

This is greenfield, so per the standing rule it gets the full flow before any code: `specify init`,
then constitution, `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, then implement.

---

## 6. Other fields

The transfer rule, in one line, because it predicts the table below better than any field-by-field
reasoning does:

> **The agent helps where the respondent wants to be understood, and hurts where the respondent has
> a stake in the answer.**

Clarification is a gift when the respondent's goal is to be measured accurately. It is an attack
surface when the respondent's goal is a particular score. A probing agent in a high-stakes setting
is not an interviewer, it is an interrogator, and it will reduce reporting rather than improve it.
Aviation already ran this experiment: NASA's Aviation Safety Reporting System is built on
confidentiality plus an FAA commitment not to use reports against reporters in enforcement actions
(https://asrs.arc.nasa.gov/), a design that exists because unprotected safety self-report failed and
had to be rebuilt around immunity. No conversational interface substitutes for that.

There is a second, sharper distinction that cuts across the first: **whether the field has an
objective criterion at all.**

- Fields with a criterion have already measured their self-report gap, and the gap is large. Dietary
  recall underreports energy intake by 12 to 13% in middle-aged men and up to 25% in elderly women
  against doubly labeled water, with food-frequency questionnaires off by 24 to 33% (Subar AF et al.,
  *J Nutr* 145(12):2639-2645, 2015, https://doi.org/10.3945/jn.115.219634,
  https://pmc.ncbi.nlm.nih.gov/articles/PMC4656907/). Self-reported physical activity correlates with
  objective measures at mean r = 0.37 (SD 0.25) across 187 studies, range -0.71 to 0.96 (Prince SA
  et al., *IJBNPA* 5:56, 2008, https://doi.org/10.1186/1479-5868-5-56,
  https://pmc.ncbi.nlm.nih.gov/articles/PMC2588639/). Retrospective habitual sleep correlates with
  polysomnography at r = 0.14, against r = 0.66 for actigraphy and r = 0.56 for a diary (Matthews KA
  et al., *Sleep Health* 4(1):96-103, 2018,
  https://pmc.ncbi.nlm.nih.gov/articles/PMC5771411/).
- Fields without a criterion cannot benchmark at all. The OECD's own guidance on measuring subjective
  well-being states that for a subjective concept "there is no way for a person other than the
  respondent to provide the correct answer"
  (https://www.ncbi.nlm.nih.gov/books/NBK189563/). The IASP's pain terminology holds that "a
  person's report of an experience as pain should be respected"
  (https://www.iasp-pain.org/resources/terminology/), though the field contests its own dogma,
  including a Pain Research Forum piece titled "Pain cannot (just) be whatever the person says"
  (https://www.iasp-pain.org/publications/pain-research-forum/papers-of-the-week/paper/pain-cannot-just-be-whatever-the-person-says-a-critique-of-a-dogma/).

That matters for the research plan in section 4: in criterion-bearing fields the agent can be
evaluated on accuracy, and in criterion-free fields the only available evaluation is the invariance
and reliability argument, which is exactly what section 4 proposes. **Psychology sits in the
criterion-free half, so invariance is not a warm-up for a validity study. It is the whole available
argument.**

### Ranked transfer

| Field | Transfer | Reasoning |
|---|---|---|
| Health outcomes and epidemiology (dietary recall, activity, sleep) | **Strongest** | Validated free instruments already exist (NCI's ASA24, https://epi.grants.cancer.gov/asa24/, over 1.2M recall-days 2009-2025 and 1,100+ published studies), the self-report gap is quantified (above), and the field already treats self-report as a signal to be corrected rather than as truth. There is also a direct existence proof for the scoring step: an LLM estimating energy and macronutrients from 24-hour-recall text alone on 11,281 NHANES adolescents had MAE 652 kcal and Lin's concordance below 0.46 zero-shot, improving to MAE 171 to 191 kcal and concordance above 0.89 after 10-shot fine-tuning (Carrillo-Larco RM, arXiv:2509.13268, 2025-09, https://arxiv.org/abs/2509.13268). |
| Patient-reported outcomes | **Strongest** | The equivalence playbook exists (section 2.4) and the field issued the call to action (section 2.1). This is the home venue. |
| Customer and market research | Strong commercially, weak scientifically | Already live at scale and verified: Outset advertises hundreds of simultaneous AI-moderated interviews with dynamic probing (https://www.outset.ai/) and Listen Labs advertises an AI moderator with smart follow-ups in 120+ languages (https://www.listenlabs.ai/). Respondents have little incentive to conceal. But nobody in the category publishes psychometrics, so there is a market here and no contribution. |
| Workplace listening | Moderate and contested, and already happening | Perceptyx launched a Conversational Listening Agent on 2025-09-16, claiming employees prefer conversational listening to surveys (vendor claim, https://www.globenewswire.com/news-release/2025/09/16/3150720). Viva Glint Copilot reached general availability 2026-04-20 but is summarization, not conversation (https://mc.merill.net/message/MC1247887). The problem the agent does not solve: the employee is observed by the employer, faking in selection-adjacent contexts is estimated at roughly 30% of applicants (Griffith and Converse meta-analytic literature, UNVERIFIED at primary level), and common-method variance is the field's known measurement disease (Podsakoff PM et al., *JAP* 88(5):879-903, 2003, https://doi.org/10.1037/0021-9010.88.5.879). A verbatim transcript under a confidential-but-not-anonymous regime is worse than a Likert grid, not better. |
| Education | Moderate to weak | Self-reported GPA is more accurate than people expect, mean r = 0.84 across 37 samples and N = 60,926, with lower performers inflating more (Kuncel NR, Credé M, Thomas LL, *Review of Educational Research* 75(1):63-82, 2005, https://doi.org/10.3102/00346543075001063, UNVERIFIED at primary level, 403 on fetch). Self-regulated-learning self-report calibrates poorly against trace data (Winne and Jamieson-Noel 2007; Zhou and Winne 2012, both UNVERIFIED). NSSE response rates averaged 25% in 2025 with an institutional range of 5 to 93% (https://nsse.indiana.edu/nsse/psychometric-portfolio/responserate-faq.html), so there is a real nonresponse problem to attack. The one live conversational deployment reports low uptake rather than data-quality gains: Khan Academy's own account of Khanmigo cites roughly 15% student usage, prompting a redesign (UNVERIFIED, not independently opened). |
| Compliance, safety and incident self-reporting | **No-go** | Underreporting is the dominant failure and the incentive is structural. Hospital staff did not report an estimated 86% of adverse events experienced by Medicare beneficiaries (HHS OIG, OEI-06-09-00091, 2012, primary document read directly). Workplace accidents go unreported at roughly 2.48 unreported per 1 reported across 425 employees in five high-risk industries, predicted by weaker safety climate and inconsistent supervisor enforcement (Probst TM, Estrada AX, *Accident Analysis and Prevention* 42(5):1438-1444, 2010). An agent that makes reporting feel more human without removing the incentive to conceal makes bad data feel trustworthy, which is worse than an obviously imperfect form. |
| Financial and regulatory self-attestation | **No-go** | SOX 302 and 404 self-certification is self-report whose content is legal evidence against the reporter. The frequently cited finding that companies with adverse Section 404 audit opinions had self-reported effective Section 302 controls about 90% of the time (Lord and Benoit, UNVERIFIED at primary level) is the shape of the problem. |
| Personnel selection and performance appraisal tied to pay | **No-go** | Maximal incentive to distort, legal exposure on employment decisions, and appraisal inflation is documented specifically where ratings feed administrative rather than developmental use. |
| Clinical diagnosis | **No-go** | Out of scope by design (section 5.5), and the boundary where the documented harms in this space occurred. |

## 7. Verdict

**BUILD, narrowly.** Build the two components in section 5.1 and run the Phase 0 study. Do not
build the consumer unified agent, and do not plan a human-subjects study he cannot be PI on.

The reasoning in four lines:
1. The measurement question is real, named in the literature, and unanswered. Zero PubMed hits for
   the invariance question as of 2026-09-13.
2. The evaluation bar already exists in the ePRO equivalence framework, so the paper does not have
   to invent its own standard.
3. Phase 0 needs no participants, no IRB, and no money, and it bounds the whole class of designs.
4. The product is the weak part of the idea, and the instrument plus protocol is the part with a
   shelf life and a natural home in a lab he is applying to.

### Repo name

**`conversational-invariance`**

It names the research object rather than the product, it does not overclaim, and it reads as
psychometrics rather than as an app.

### Phase 1

`score`, plus the perturbation sweep, plus the Phase 0 result.

1. Run the spec-kit flow (section 5.9). Greenfield, so this is not optional.
2. Freeze two item banks as JSON: PHQ-8 and one low-stakes scale, each with item text, response
   options, scoring rules, and a written clarification bank for arm 2.
3. Port the ghost-respondents counterpart generator (`lane3-testbed/generate_counterparts.py`,
   config in `lane3-testbed/GEN-CONFIG.md`) to emit free-text item responses at planted latent
   levels instead of essays.
4. Implement `score`: item plus options plus free text in, ordinal category out. One backend
   interface, a local 8B-class model and a scripted backend first.
5. Implement the sweep: seed, temperature, model family, item paraphrase, option order, item
   position, context presence or absence. Every replicate lands in `score_replicate`.
6. Report: ICC and exact-agreement across replicates per perturbation, plus recovery of the planted
   level. Wire every number through the claim ledger so it resolves to a hashed artifact.
7. Gate: if scorer ICC under innocuous perturbation is below the pre-registered floor, that is the
   Phase 0 paper and Phase 2 is deferred rather than started.

### Phase 2

`administer`, with the five arms and the item-event log.

1. Implement the runner with adaptivity as a config level 0 to 4, exactly as defined in section 4.2.
2. Implement `item_event` logging, including the reason for every skip. This is a measurement
   requirement, not telemetry.
3. Exercise all five arms against scripted and synthetic respondents so every arm is known to run
   end to end before a human ever sees it.
4. Implement the escalation path and the no-feedback rule from section 5.5.
5. Write the analysis layer in R: the invariance ladder with pre-registered delta-fit thresholds, the
   Gwaltney 5%-of-scale-range mean-difference bound, and per-mode reliability.
6. Write the human-subjects protocol document as the deliverable, ready for a faculty PI to submit
   through ARROW. The arms are the protocol, so write it while they are fresh.

### No blocking question

The one ambiguity that could have blocked this, whether to chase the memory agent or the asker, is
settled on the evidence in section 1: the memory agent has to be validated against the diary agent,
which has to be validated against the asker, and the asker's validation is the one that has never
been done. Build from the base.

The one thing worth knowing when convenient, which does not block anything: whether his UW email
still resolves, since DAIC-WOZ access requires an academic address. If it does not, Phase 0 runs on
synthetic stimuli plus `essays.csv` plus MIDUS NSDE, all of which are already reachable.

---

## Appendix: verification status

Verified directly in this session, by fetching the source or its indexed metadata:
Terheyden 2025 and Weinfurt 2025 abstracts (NCBI efetch, PMIDs 40126736 and 41003894);
Dosovitsky 2021 abstract and psychometrics (PMID 34713116); Serafimovska et al. 2025 title,
authors, date and all four studies' numbers (PMID 40794461); the FTC BetterHelp case page and its
$7.8M order; the zero-result PubMed searches for
chatbot / conversational agent / LLM crossed with measurement invariance and with differential item
functioning (esearch, 2026-09-13); the MTurk closure notice and date (mturk.com/pricing);
arXiv titles, dates and authors for 2606.20064, 2510.27126, 2503.08582, 2411.10109, 2310.13548 and
2212.09251; and Crossref DOI records for Zarouali 2023, Lucas 2014, Gwaltney 2008, de Quidt 2017,
Fisher 2018, Molenaar 2004, Kim 2019, Xiao 2020, Currey 2022, Pratap 2018, Meredith 1993,
Kroenke 2009, Vandenberg 2000, Cella 2010, Coons 2009, Stefkovics 2025 and Tourangeau 2007. The
essays corpus path, size and loader caveats were read off disk. For section 6, the cross-field
scout opened and confirmed directly: Subar 2015, Prince 2008, Matthews 2018, Carrillo-Larco 2025,
the HHS OIG 2012 report, the NASA ASRS pages, the NCI ASA24 page, the NSSE response-rate FAQ, the
OECD subjective-well-being guidance, the IASP terminology pages, the Outset and Listen Labs product
pages, the Perceptyx launch release, and the Viva Glint Copilot notice.

Reported by research scouts and not independently opened, so carried here with the marking the
scouts gave them: the Gwaltney 0.2% and 93% figures, the PROMIS CAT mean-item-count figures, the
2025 human-likeness disclosure trial, the Limitless acquisition, the Wondering liquidation,
DAIC-WOZ item-level PHQ-8 availability, and the Groq free-tier limits. None of these carries an
argument on its own in this note.

One scout claim was checked and found wrong, recorded because the corrected version matters more
than the original. The scout reported that the 2025 chatbot cognitive-assessment study found its
psychometrics "not robust enough to consider AI-administered versions fully equivalent." The
abstract, read directly (PMID 40794461), concludes the opposite: "TICS-M-AI is reliable, valid, and
equally safe." Section 2.5 carries the corrected reading, and the argument there now rests on the
narrower and defensible points, that the study reports concurrent validity and test-retest rather
than an invariance ladder, that it tests a performance instrument rather than a self-report scale,
and that its AI arm has no adaptivity manipulation.

Searched for and not found, which is a finding rather than a gap: a reporting standard specific to
LLM-elicited self-report or PRO data; a published psychometric validation from any commercial AI
interviewer; a published UW-Madison IRB review-turnaround figure; any study testing measurement
invariance between conversational-agent and form administration of a validated scale; and, in the
customer-research row of section 6, the NPS methodological critique and the online-panel
fraud literature, which were delegated and not returned, so that row rests on the two vendor pages
named in it rather than on measurement evidence.

The session's WebSearch budget (200 calls) was exhausted partway through, so later claims lean on
Crossref, NCBI E-utilities and direct fetches rather than search. Where a scout hit that wall it
said so, and those items are the ones marked above.
