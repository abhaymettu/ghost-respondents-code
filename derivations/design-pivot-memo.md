# Design pivot memo: what each no-generation shape does to the estimand

Lane 1 (derivation), 2026-09-07, evening. Analysis only: no generation, no code run, every number below is either on file (cited) or derived here from numbers on file. Notation is the lane-1 notation of derivations/lane1-zero-coupling.md (day 1) and lane1-partial-coupling.md (day 2); equation numbers continue from (E63), propositions from Prop. 15. rho_H := Cor(x, w | H) throughout (N2, lane-1 reading).

Steering being answered (Abhay, 6:30pm): do not burn weeks or money on the 15k shape if a smarter design gets the same answer. Corpus-first audit verdict: FALLBACK-AB, 1,950 to 3,900 residual generations (lane3-testbed/CORPUS-AUDIT.md).

## 0. Bottom line

1. Coupling never entered any estimator as a covariate, so nothing in the identification of rho_H or pi depends on how c is produced. c enters the design (which machine text is injected) and the bias closed form only through g = c sqrt(kappa / rel_H), (E7). Any design that realizes a known g, with kappa and delta measured, validates the same map.
2. There is a design that realizes g without generation: inject a labeled machine pool by an assignment rule. Random assignment gives c = 0 exactly; assigning respondent i a machine text whose persona label equals respondent i's label gives the pool's realized coupling; matching with probability p gives c = p c_q exactly (Prop. 16, with lane 4's reweighting hook (E73) in the random branch; c_q is the pool's coupling at the base's label prevalence, section 9.1). Text, generator, genre and length are held fixed across coupling levels, which the frozen design could not do.
3. The pools for it are already on disk. Big5PersonalityEssays (399, GPT-4-turbo, same genre as PK, 100 words, audited) and the PersonaLLM release at lane3-testbed/data/personallm: 320 labeled stories for each of gpt-4-0613, gpt-3.5-turbo-0613 and llama-2 (32 label cells x 10 replicates, labels in the file names), mean length 472 to 650 words against PK's 652, MIT license, plus 2,467 labeled human files that by count and mean length are the PK essays. Lane 3's wide hunt scored PersonaLLM for the c = 0 role and rejected it on genre (roberta AUC 0.78 to 0.95 against PK; a story-writing prompt, not stream of consciousness). That rejection is for a different role. In the assignment design the coupling contrast is within one pool, so genre is constant across coupling levels and enters only through the measured (kappa, delta) and the detector's separability, which Layer B has to span anyway. Nothing about the pool's coupling is on file yet.
4. Money was never the constraint. From the burn report the frozen batch is about 115 dollars as designed; every residual shape is under 60. The constraint is the key, dry-run, quality-check loop plus the c-high blocker (binary labels make the partial and high arms the same information; GEN-CONFIG.md).
5. Recommended path: P1' (assignment-coupled injection) as the Layer B design, with the 1,800-generation P3' batch demoted to an optional robustness appendix that does not gate the preprint. Three to four lane rounds to a Layer B pilot cell, no external gate. Section 8.

## 1. What each estimator actually consumes

Model (day 1, section 0 and (E1) to (E7)): x | H = mu_H + theta + e, x | M = mu_M + g theta + v, g = c sqrt(kappa / rel_H), kappa = s2_M / V_H, delta = (mu_H - mu_M) / sqrt(V_H) [sign corrected 2026-09-07 20:05 to day-1 line 38 and CONVENTIONS.md line 46, section 9.2; the draft had it reversed; Att uses delta^2 only, so no number moves], w = b theta + u clean. Under A1 and A2,

    rho_obs = rho_H Att(pi, c),   Att = N / sqrt(Den),   N = (1 - pi) + pi g,   Den = (1 - pi) + pi kappa + pi (1 - pi) delta^2.     (E7)

Att is a function of (pi, g, kappa, delta) only; c and rel_H enter through g and nowhere else (this is (E36), Att linear in c with slope pi sqrt(kappa / rel_H) / sqrt(Den)).

What the SPEC estimators need, read against SPEC 3.1 to 3.3:

- 3.3 mixture EM: the likelihood has two authorship components with free (mean, variance, covariance with w) each; SPEC 3.3 puts no detector-score term in it and lane 4 fits it at detector = none [corrected 2026-09-07, verify pass; the draft added a detector-score indicator]. c is not a parameter. g is a derived quantity of the fitted machine component. Identification of (pi, rho_H) comes from the class structure alone and is the same whatever process produced the machine texts.
- 3.2 label-free prevalence plus errors-in-variables correction: pi-hat from distribution matching against a machine reference, then rho_H-hat = rho_obs-hat / Att(pi-hat, g, kappa, delta). It needs pool-level (g, kappa, delta). SPEC 3.2 says the reference is "generated on demand"; with no generation the reference is the injected pool itself (held-out split) or another pool (transfer). Circularity is avoided by the split; the transfer case is the realistic one and is available for free from the multi-pool corpora.
- 3.1 SIMEX: SPEC 3.1's SIMEX perturbs the detector's misclassification matrix (powers of Pi built from a calibrated (se, sp)) and extrapolates the naive moments back to zero error; it adds no machine text and consumes no pool [corrected 2026-09-07, verify pass; the draft said it needed injected text at pi increments]. It needs a calibrated (se, sp) on the sample at hand, which is 2.3's problem, not a coupling problem.

So the only place where a c estimate is consumed is 3.2's moment correction, and there it is g at the pool level. That is the whole answer to "does the mixture still identify rho_H and pi when c is measured with error": the mixture never asked for c; the moment correction asks for g, whose sampling error is a variance term (section 3.3), not an errors-in-variables attenuation.

## 2. Cross-cutting: what the testbed has already fixed, whatever the pivot

These bind every Layer B design, generated or not. They are stated once here and referenced below.

### 2.1 The realized human reliability of the trait pipeline is 0.002 to 0.06, not 0.7

Audit 3 (lane3-testbed/audit3_results.json): MiniLM-L6-v2 embeddings, RidgeClassifier per trait, held-out AUC on PK (75/25 split, n_test = 617): cEXT 0.639, cOPN 0.629, cAGR 0.572, cNEU 0.551, cCON 0.528. For a balanced binary label under the equal-variance normal model, AUC converts to a point-biserial correlation by

    d' = sqrt(2) Phi^{-1}(AUC),   r_pb = (d' / 2) / sqrt(1 + d'^2 / 4).                                                         (E64)

In Layer B on the local mirror the trait is the binary label (theta := L, the only trait data available without the IEEE login), so r_H := Cor(x, L | H) is the human "sqrt(rel_H)" and the coupling scale that (E7) cares about is

    c / sqrt(rel_H) = c-hat / r_H,   g = (c-hat / r_H) sqrt(kappa).                                                            (E65)

| trait | held-out AUC | r_H by (E64) | rel_H = r_H^2 | c-hat (audit 3, Big5 pool) | c-hat / r_H | SE of the ratio |
|---|---|---|---|---|---|---|
| cEXT | 0.639 | 0.244 | 0.060 | 0.241 | 0.99 | 0.26 |
| cOPN | 0.629 | 0.227 | 0.051 | -0.029 (n.s.) | -0.13 | 0.22 |
| cAGR | 0.572 | 0.128 | 0.016 | 0.142 | 1.10 | 0.52 |
| cNEU | 0.551 | 0.090 | 0.008 | 0.106 | 1.17 | 0.76 |
| cCON | 0.528 | 0.049 | 0.002 | 0.123 | 2.49 | 2.3 |

SE column: delta method with SE(c-hat) = 1 / sqrt(399) = 0.050 and SE(r_H) = 1 / sqrt(617) = 0.040; the column is the absolute SE of the ratio, |c-hat / r_H| x sqrt[(0.050 / c-hat)^2 + (0.040 / r_H)^2] (relative SEs: EXT 0.26, OPN 1.71, AGR 0.47, NEU 0.65, CON 0.91). Ratios and SEs use the unrounded AUCs and c-hats in audit3_results.json [precision corrected 2026-09-07, verify pass: EXT r_H 0.244 not 0.245, ratio 0.99 not 0.98; c-hat here is audit 3's raw pool coupling, see section 9.1 for the reweighted c_q]. Three readings:

(a) The rel_H = 0.7 that lane 4's pilot and DGP default use (PILOT.md, CONVENTIONS.md; SPEC.md fixes no value) is a survey-scale number. The text pipeline realizes 10 to 300 times less. Every absolute bias in Layer B is rho_H times (Att - 1) with rho_H at most 0.25, so absolute biases are hundredths of a correlation. The SPEC 4.4 bias criterion is a ratio and survives; the coverage and pi-hat criteria do not involve rho_H's scale at all; the RMSE comparison against detect-and-delete becomes mostly a variance comparison (section 4).

(b) On the coupling scale that matters, persona-conditioned GPT-4-turbo text already has the human-replica machine's coupling on extraversion (c-hat / r_H = 0.99, so g = 0.99 sqrt(kappa); the human-replica point (E54) itself also needs kappa = 1 and delta = 0, neither on file, Q11), and zero coupling on openness. The "c high" arm the frozen design was to generate is what this pool already is, on a different prompt.

(c) The three ratios above 1 (AGR, NEU, CON) are the day-1 inflation regime (g > 1 at kappa = 1, delta = 0, Prop. 5) if they hold, but their SEs say they are not established at these sample sizes; CON's human signal is indistinguishable from zero (r_H = 0.049, SE 0.040). Only EXT and OPN are usable Layer B traits at present.

### 2.2 Deletion-selection is empirically invisible at the measured r_F

Prop. 11 gives rho_H,pass / rho_H = q / sqrt[(1 - rel_H (1 - q)) (1 - rho_T^2 (1 - q))] with 1 - q = r_F^2 psi. CALIBRATION-REPORT's anchor is |r_F| between 0.05 and 0.07 on binary labels (a lower bound; surface fluency proxies). At SPEC's a priori sp_bar = 0.85 (psi = 0.36) and r_F = 0.06, 1 - q = 0.0013 and the ratio is 0.999: a 0.1 percent effect; at the testbed's calibrated out-of-domain sp of 0.926 (CALIBRATION-REPORT) fewer humans are deleted and the effect is smaller still. Day 1's 1.7 percent at r_F = 0.3 and 5 percent at r_F = 0.5 (Q6) are not reachable on this testbed unless continuous BFI scores raise r_F by a factor of five (to 0.3) or about eight (to 0.5). What Layer B can show about detect-and-delete under every pivot is Prop. 14's residual contamination and manufactured mean gap, and the sensitivity failure in 2.3, not the fluency collider.

### 2.3 The calibrated detector has no power on same-genre GPT-4-turbo text

Audit 2: the HC3-calibrated roberta detector (openai-community/roberta-base-openai-detector, a GPT-2-era model with its threshold set on HC3; "the roberta detector" below) has AUC 0.472 on PK-human versus Big5-machine (same genre, GPT-4-turbo). Audit 2 computes AUC only, so the machine-side flag rate at the calibrated point is an inference, not a measurement: with AUC at chance and the human flag rate at 1 - sp = 7.4 percent (OOD sp 0.926, CALIBRATION-REPORT), the machine flag rate is about the same, so detect-and-delete removes roughly a random 7 percent and leaves pi' close to pi; and 3.2's distribution matching on detector scores has no signal on that pool. On that pool pi must be identified from trait-score moments (delta, kappa) or a different detector. This is SPEC failure mode 2 realized before any generation, and it is the identifiability limit Layer B will hit first, at every c. The pools that are separable (student_llm 0.601, Ghostbuster 0.644, PersonaLLM 0.777 to 0.945 by generator, ArguGPT 0.982; CORPUS-AUDIT audit 2 and wide hunt) are separable partly by genre; for estimator recovery that does not matter (the estimator only sees score distributions), for the interpretation of the machine process it does.

### 2.4 The trait pipeline already truncates at about 190 words

audit3_trait_recoverability.py encodes with SentenceTransformer("all-MiniLM-L6-v2") at default settings, whose window is 256 word-pieces, roughly 190 words. PK scores were therefore computed from the first 190 words or so of essays whose mean length is 652; the Big5 essays (mean 100) fit inside the window. For the trait signal the effective length ratio between PK and Big5 is about 2, not 6.5. The 6.5 still applies to anything that reads the full text (the detectors, the feature baseline, PK-side chunking). This changes P2's arithmetic (section 4).

### 2.5 The PersonaLLM pool on disk: scored for c = 0 in the wide hunt, not scored for coupling

lane3-testbed/data/personallm/text has four folders. Read from the directory only (counts, names, word counts); nothing was run here. The roberta AUCs below are from CORPUS-AUDIT's wide hunt (audit_widehunt.py, the audit-2 path).

| folder | files | naming | mean words |
|---|---|---|---|
| gpt-4-0613 | 320 | five poles in the name (extr/intr, agre/anta, cons/unco, neur/emot, open/clos) plus replicate p1 to p10 | 583 |
| gpt-3.5-turbo-0613 | 320 | same | 650 |
| llama-2 | 320 | same | 472 |
| human_stories | 2,467 | same naming; essays.csv with named entities masked (L3-a) | 652 |

32 label cells x 10 per generator; the license file is MIT (Hang Jiang, 2023). The human folder's count (2,467) and mean length (652) equal PK's usable rows and mean (CORPUS-AUDIT audit 1: 2,467 and 652.1), and a read-only comparison on 2026-09-07 (lane 1; open-questions item L3-a) shows it is essays.csv with named entities masked to PROPNAME and LOCNAME: 175 files match verbatim after whitespace normalization, the rest differ only at masked names, and the filename label slots reproduce the essays.csv binary labels on all 2,060 unambiguously paired files. So the human side of step 1 is scored on essays.csv itself, and human_stories is scored only to measure what the masking does to the detector and to the trait score. CORPUS-AUDIT does not record which human file the wide-hunt AUCs below used.

Wide-hunt result (CORPUS-AUDIT.md, 18:30 steer): roberta AUC against PK human is 0.836 (gpt-4-0613), 0.777 (gpt-3.5-turbo-0613), 0.945 (llama-2), 0.859 combined at the 500 cap; verdict genre-confound, rejected for the c = 0 role. Lane 3's reading is that the prompt asked for a story, so the texts are plotted first-person fiction rather than unedited stream of consciousness, and the detector separates on the task. The wide hunt also declines PersonaLLM as a conditioned-arm source on two grounds: the same-genre assumption behind audit 3 does not hold for it, and its labels are coarse bands. Neither ground bites in the assignment design. The coupling contrast is matched versus random inside one pool, so genre is constant across coupling levels and enters only through the pool's measured (kappa, delta) and its detector separability; and Layer B's theta is the binary label in any case. What the genre does cost is realism: a PersonaLLM story injected into an essay sample is not what a respondent pasting a chatbot answer to the essay prompt produces, and (kappa, delta) measured on it are genre plus authorship effects. The Big5 pool has the opposite profile (same genre, 100 words, one generator, invisible to the detector), so the two labeled pools bracket the realistic case from both sides, and only generation at PK's own prompt (P3') sits inside the bracket.

Consequences for the pivot: 960 labeled machine texts across three generators at PK length; the single-generator objection to P1 goes away; the coupled arm's length confound goes away; the detector has power on this pool, so the SPEC's detector arms and the 3.2 distribution-matching estimator are testable on it, which they are not on the Big5 pool (2.3). Caveats: 2023-era generators; extreme-pole personas; none of (c-hat, kappa, delta) is on file for these pools yet. PersonaLLM's own human-judge study (section 7) found text-recoverable persona signal only for extraversion, so the expectation is a c_pool profile like Big5's, EXT usable and OPN near zero, to be measured in step 1 of section 8.2.

## 3. P1: coupling as a measured quantity

### 3.1 What is and is not identifiable about c

Per item, nothing. A single text gives one score x_i; c is a correlation across items and has no item-level analogue. What exists per pool (or per stratum: generator x prompt condition x trait) is the realized coupling c_pool = Cor(x, L | pool) and the derived g. So P1 as phrased in the brief ("estimate per-item realized coupling") reduces to pool-level g with sampling error. That is enough, because section 1 showed g at the pool level is all any estimator consumes.

Under binary labels the estimator of g is a ratio of label mean differences. With m_l = E[x | M, L = l] and h_l = E[x | H, L = l],

    g = Cov(x, L | M) / Cov(x, L | H) = (m_1 - m_0) / (h_1 - h_0).                                                          (E66)

Derivation: for a label with prevalence q_1 in both classes, Cov(x, L) = q_0 q_1 (E[x | L = 1] - E[x | L = 0]) in each class; the q_0 q_1 cancels, so (E66) needs no balance [generalized 2026-09-07 20:05 from the balanced case]. Whatever attenuation dichotomizing theta into L imposes on c-hat imposes the same factor on r_H and cancels in (E66). The "attenuation on c" the brief worried about is therefore not a bias in g. The only attenuation that survives is the one in (E70) below, and it arises only if w is later built from a continuous theta.

### 3.2 The assignment-coupling design (Prop. 16)

Take a labeled machine pool with N_l texts in label cell l in {0, 1}, within-cell score law F_l with mean m_l and variance V_l. Replace a fraction pi of the human sample; the replaced respondents have label prevalence q_1 = P(L_i = 1), q_0 = 1 - q_1 (under A1 the base's own prevalence; on PK 0.500 to 0.531 by trait). Assign the machine text to respondent i by one of three rules: random; matched (the text's pool label equals L_i); or matched with probability p and random otherwise. The random branch draws text t with probability

    u_t = q_{L_t} / N_{L_t},                                                                                                    (E73)

i.e. a label at the respondent prevalence, then a text uniformly inside that cell (lane 4's reweighting hook, INJECT.md section 2). The outcome w_i stays attached to respondent i (w = b L_i + u_i, or w = L_i). [Restated 2026-09-07 20:05: the draft drew the random branch uniformly from a pool assumed balanced and its proof assumed a balanced base as well; section 9.1 has what the draft rule does on an unbalanced base.]

Prop. 16 (assignment coupling, restated). For every pool balance (N_0, N_1), every respondent prevalence q_1 in (0, 1) and every p in [0, 1], with the random branch drawn by (E73): under random assignment (p = 0), c = 0 and g = 0 exactly; and

    c(p) = p c_q,   g(p) = p g_pool,   kappa(p) = kappa_q,   delta(p) = delta_q,                                                (E67)

where g_pool = (m_1 - m_0) / (h_1 - h_0) is (E66) and the q-subscripted quantities are the pool's under the joint law L ~ (q_0, q_1), x | L = l ~ F_l:

    m_q = q_0 m_0 + q_1 m_1,   Var_q(x) = q_0 V_0 + q_1 V_1 + q_0 q_1 (m_1 - m_0)^2,   c_q = sqrt(q_0 q_1) (m_1 - m_0) / sqrt(Var_q(x)),   kappa_q = Var_q(x) / V_H,   delta_q = (mu_H - m_q) / sqrt(V_H).     (E74)

Proof. Given L_i = l, x_M ~ p F_l + (1 - p) G with G := q_0 F_0 + q_1 F_1 the random branch's law under (E73). Integrating over L_i ~ (q_0, q_1), the marginal of x_M is p G + (1 - p) G = G for every p, so E[x_M] = m_q and Var(x_M) = Var_q(x) do not depend on p, which gives kappa(p) = kappa_q and delta(p) = delta_q. For the covariance, E[x_M | L_i = l] = p m_l + (1 - p) m_q, so Cov(x_M, L_i) = q_1 (E[x_M | L_i = 1] - E[x_M]) = p q_1 (m_1 - m_q) = p q_0 q_1 (m_1 - m_0). Dividing by sqrt(Var_q(x) q_0 q_1) gives c(p) = p c_q; dividing by Cov(x, L | H) = q_0 q_1 (h_1 - h_0), which carries the same q_0 q_1 because the replaced set and the human remainder share the prevalence under A1, gives g(p) = p g_pool. At p = 0 the text is drawn without reference to L_i, so both covariances vanish. QED.

Check at p = 1: c(1) = c_q, the pool's coupling reweighted to the base's prevalence; it equals audit 3's raw c-hat (the pool at its own label shares) only when those shares equal q, and the two are reported as different numbers (section 9.1). At p = 0: c = 0. The three SPEC arms are p = 0, an intermediate p, and p = 1; the axis is continuous and costs nothing. Unlike the frozen design, the three arms share generator, prompt, genre, length and detectability, so a c-contrast is a c-contrast and nothing else. What the design cannot do is let kappa and delta move with c (a persona-conditioned generator might homogenize less at high c); that covariation is only reachable by generation (section 5).

One reading to state in the paper (lane 2's point, section 7.3): the p = 0 arm is persona-conditioned text decorrelated from its recipient, not unconditioned text. In the model the persona component sits in v at p = 0 and moves into g theta as p rises, with Var(x | M) fixed. An unconditioned generator would have a smaller Var(x | M), a lower kappa, and that difference is exactly the kappa-c covariation the design holds fixed by construction and the frozen design would have confounded with c.

Coverage without replacement (single-trait matching, two cells): Big5 pool 178 to 221 per cell (measured 2026-09-07, Q12), PersonaLLM 160 per cell per generator, 480 pooled, 680 with Big5. A balanced base needs n pi / 2 draws per cell: n = 1,000 at pi = 0.30 needs 150, inside every pool separately; n = 2,400 at pi = 0.30 needs 360, which only the pooled labeled set covers without replacement. Full-vector matching (32 cells, about 10 per cell per generator) is not needed for a one-trait Layer B and would exhaust at n pi of a few hundred.

Implementation rule that matters for the numbers: human scores must be cross-fitted (K-fold ridge), because the machine pools are scored out of sample by construction and in-sample human scores would manufacture kappa < 1 and c-hat / r_H < 1.

### 3.3 The sampling error of g-hat is variance, not attenuation

From (E66) with n_M / 2 and n_H / 2 per label cell (for pool cells at shares (s_0, s_1) the first term becomes 1 / (4 s_0 s_1 c_pool^2 n_M), about 1 percent larger at the measured Big5 shares),

    SE(g-hat) / g = sqrt[ 1 / (c_pool^2 n_M) + 1 / (r_H^2 n_H) ].                                                                (E68)

Numbers: EXT on the Big5 pool alone (c = 0.241, n_M = 399; r_H = 0.244, with n_H = 2,467 projected for the cross-fitted scores of step 1) gives 0.224, or 0.265 on the current held-out estimate (n_H = 617); with the three PersonaLLM generators pooled (n_M = 960, if their c is similar) 0.157. The correction rho_H-hat = rho_obs-hat / Att(pi-hat, g-hat, kappa-hat, delta-hat) inherits, by the delta method,

    [d log Att / d g] SE(g-hat) = (pi / N) SE(g-hat),   N = (1 - pi) + pi g.                                                      (E69)

At pi = 0.10, kappa = 0.5, EXT matched (g = 0.99 sqrt(0.5) = 0.70, N = 0.970): 0.103 x 0.224 x 0.70 = 0.016, i.e. 1.6 percent of rho_H, against a naive bias of 0.5 percent at that cell (Att = 0.995) and 7.7 percent at c = 0 (Att_0 = 0.923). At pi = 0.30: (0.3 / 0.909) x 0.156 = 5.1 percent, against a naive bias of 1.4 percent matched and 24 percent at c = 0. So the g-uncertainty is larger than the bias it corrects in the matched arm and a fifth of it in the random arm; a paper that reports the corrected estimate with this SE is honest and still beats the naive estimate at c = 0 by a wide margin. The nonlinearity bias E[1 / Att(g-hat)] - 1 / Att(g) is second order, of order (pi / N)^2 Var(g-hat), under 0.3 percent at the cells above.

If w is built from a continuous theta rather than from L (only possible with the IEEE scores), matching on a binary label couples the text to L, not to theta, and

    g_eff = g_ratio Cor(L, theta)^2 = (2 / pi_circle) g_ratio = 0.637 g_ratio                                                    (E70)

for a median split of a normal theta (pi_circle = 3.14159, to avoid the prevalence symbol). This is the one place a dichotomization factor survives; it is a known constant, not an unknown attenuation, and it is irrelevant while Layer B defines theta := L.

### 3.4 What survives, what dies, what weakens

Survives, unchanged: identification of rho_H and pi (section 1); the entire Layer A map, which is parametric and needs no text; the Layer B validation of (E7) along a designed g axis from 0 to g_pool at fixed (kappa, delta), including the c = 0 row (Prop. 1 sign and bounds; Prop. 3 monotonicity, which is day 1's H1 statement), and the human-replica cell (E54) if some pool has kappa near 1 and delta near 0; the label-free prevalence estimator's recovery test, on every pool; the errors-in-variables correction (H4); deletion versus correction (H3) in the Prop. 14 form, with 2.2's caveat; the Prop. 15 both-endpoints extension (Layer A only, as before).

Dies in Layer B, lives in Layer A: the between-item homogenization signature (Prop. 8, Prop. 9, H2) in its same-session versus independent-call form, because it needs several items per respondent generated in one session versus separately (Q7, the rho_v two-arm plan in CALIBRATION-REPORT section 3). Partial rescue: split each text into k chunks scored separately and compare residual between-chunk correlation in machine versus human texts; this is the same-session form only and measures within-text consistency, so it is a weaker H2, flagged as such.

Weakens: the map's top end is capped at g_pool (near sqrt(kappa) on EXT), and nothing above it is reachable; but nothing above it was reachable under the frozen design either, since binary labels made c-high a rephrased c-partial (GEN-CONFIG). The kappa-c covariation is unobservable. Detector sensitivity on machine text written to PK's own prompt (CALIBRATION-REPORT open item 1; that report files essays as out-of-domain for the HC3-calibrated detector, so this is its missing out-of-domain se cell, not an in-domain number) cannot be measured; what is measurable is sensitivity on the pools, genre-confounded for the unlabeled ones and near zero for the same-genre one (2.3).

Identifiability cost, stated once: on the same-genre pool pi is identified only through (delta, kappa) of the trait score or a detector better than the roberta detector; expect the SPEC 4.4 pi-hat criterion (within 2 points at n = 1,000) to fail there at every c, and to pass on the separable pools (PersonaLLM 0.78 to 0.95, ArguGPT 0.98; the two student-essay pools at 0.60 to 0.64 are the intermediate cases). This is the honest boundary result Layer B will produce: the collapse axis is detector separability d', not c. Layer A already covers it through the "none" and "degraded" detector arms. A3 (detector error independent of theta given class) becomes checkable inside the labeled pools (detector score against pool label), which is the pass-3 attack target in Q9, now testable for free.

## 4. P2: transforming the human side to the machine pool's genre

Two transforms were on the table: LLM-based style normalization of PK essays, and truncation to the pool's length.

LLM normalization is disallowed by the model itself. A rewritten human essay is a machine output with the human's text as input: x_H^norm = mu_N + g_N theta + v_N with some coupling c_N < 1. The "human" reference class then has validity rho_H c_N / sqrt(rel_H) instead of rho_H (the pi = 1 boundary of (E7), day-1 line 104: Att(1) = g / sqrt(kappa) = c / sqrt(rel_H)), i.e. the base sample is contaminated at pi = 1 with an unknown c_N, and the detector flags it. There is no rho_H left to recover: the target has been replaced by the normalizer's coupling, which can sit above or below rho_H (c / sqrt(rel_H) is 0.99 for the Big5 pool on EXT) and is not the quantity the paper is about.

    rho_H^norm = rho_H c_N / sqrt(rel_H) = rho_H g_N / sqrt(kappa_N),   g_N = c_N sqrt(kappa_N / rel_H)   [corrected 2026-09-07, verify pass; the draft had rho_H g_N].     (E71)

Truncation is a different matter. If the score is a near-linear aggregate of local features (mean pooling is exactly that), text of length n behaves like n parallel units and Spearman-Brown gives, for rel(n_2) = R,

    rel(n_1) = n_1 R / [ n_2 - (n_2 - n_1) R ].                                                                                   (E72)

With 2.4, the pipeline's effective PK length is about 190 words, so truncating PK to the Big5 length of 100 words takes EXT from r_H = 0.244 (R = 0.060 at n_2 = 190) to sqrt(6.0 / 184.6) = 0.180, a 26 percent loss. The measured R belongs to the 190-word window and cannot be re-used as the reliability of a scorer that reads all 652 words; Spearman-Brown from the one measured point gives the same 0.180 at 100 words for any single scorer, and the draft's aside that a full-text scorer would land at 0.099, a 60 percent loss, rested on an unmeasured premise and is withdrawn [2026-09-07, verify pass]. What the brief's "fatal" reading would need is a pipeline whose r_H at 100 words is near 0.10: there the Layer B bias at pi = 0.10, c = 0, kappa = 0.5 is 0.0077 correlation units against a per-replicate SE of 0.031 at n = 1,000; mean bias over 100 replicates is still estimable (SE 0.003) but the H3 RMSE comparison is then decided by variance, i.e. by how many cases deletion throws away, not by bias. With the actual pipeline it is a 26 percent loss, survivable.

Verdict: cleared, narrowly. Truncation at a sentence boundary is a legitimate length control for the detector-side features and for measuring (kappa, delta) against a length-matched human comparator, and it makes the base more like a survey open-end. It is not needed for the coupled arm once PersonaLLM's length-matched pools are used, and it should not be the base for the validity target if the Big5 pool is dropped to a robustness role. The Spearman-Brown premise is testable with the existing audit3 script on PK truncated at 100 and 190 words (one existing-script run, lane 3).

## 5. P3: hybrid minimum

As written (corpus c = 0 pool plus a 600-essay, two-level, single-family, 1,200-generation batch), the c-contrast is confounded with generator, genre and prompt: the c = 0 arm is student or argumentative essays from generators CORPUS-AUDIT does not confirm per pool and the c > 0 arms are Sonnet-5 stream-of-consciousness at PK's prompt. Every difference between the arms is attributable to any of the three. As a map it is uninterpretable; as a prevalence and correction test it is fine. The fix is to generate the c = 0 arm for the same 600 essays too (P3': 600 x 3 x 1 = 1,800 generations) and use the corpus pools as cross-generator robustness instead of as the c = 0 arm.

What generation buys that no assignment design can:
- PK's own prompt and length, so the machine text is a counterpart, not a neighbor.
- Same-session versus independent-call arms, hence rho_v and the H2 between-item signature in its intended form.
- The kappa-c covariation (does persona conditioning de-homogenize).
- Detector sensitivity on text written to PK's own prompt, at the calibrated operating point (open item 1).
- A 2025 generator; the on-disk labeled pools are 2023 to 2024 models.
- The realism check that 2.5's genre bracket makes reviewers ask for: machine text that is the answer to the survey's own prompt, not a neighbor of it.

What it does not fix: the c-partial versus c-high degeneracy under binary labels (GEN-CONFIG), so the generated axis has two informative levels, the same as the assignment axis; and the generation-realism attack (SPEC 8.6), which the assignment design dodges because its arms share text.

Cost, from the burn report line (prompts/lane3-genstage.md: Sonnet-class about 105 dollars, open-weight under 10, for 14,874 generations) and GEN-CONFIG's even family split (7,437 per family): 0.0141 dollars per frontier generation, under 0.0014 per open-weight generation. P3 at 1,200 frontier generations: 17 dollars. P3' at 1,800: 25. FALLBACK-AB at 1,950 to 3,900: 28 to 55 all-frontier, about 30 (30.15) with an even family split at the high end. The frozen batch: 115 as designed, 210 if all frontier. Nothing here is a budget decision. The cost is the gate sequence: key (absent on this machine, GEN-DRYRUN), dry run, quality eyeball, detector recalibration on generated text, then the same injection code P1' needs.

## 6. P4: the paper with no generation at all

The strongest no-generation paper is P1' with the coupling axis removed: prevalence estimation, the validity correction, and the deletion-selection theorem validated on observational pools at c = 0 (one to four generators per pool, detectability from 0.47 on the same-genre pool to 0.98 on ArguGPT), with coupling as a measured moderator at the realized c-hat / r_H of the labeled pools (one point per pool and trait: EXT near 1, OPN near 0, the others uncertain; g itself needs the unmeasured kappa). Since the labeled pools are on disk, there is no reason to stop at one point per pool when Prop. 16 gives the whole segment [0, g_pool] from the same files at the same cost. P4 is P1' with a self-imposed loss, and that loss is exactly the c-grid map in Layer B. The headline losses of P4 relative to the frozen design are the union of section 3.4's list and the map; relative to P1' they are only the map.

## 7. Lane 2: positioning consequences

Lane 2 ran this section's search and reads as a Sonnet pass this evening (sources fetched: SPEC.md, CORPUS-AUDIT.md, lane2-novelty/positioning-memo.md and pivot-positioning.md, and the papers below); the text here is lane 1's condensation of that report, with lane 2's verification labels kept. That report was returned in-session as an agent result and is not yet written to any lane2-novelty file (checked 2026-09-07: positioning-memo.md and pivot-positioning.md contain none of the claims below), so this section is its only on-disk record until lane 2 files it; every "lane 2" attribution below is to that report, not to a file.

Sources (URLs verified by fetch unless marked): PersonaLLM, Jiang et al., NAACL 2024 Findings, https://arxiv.org/abs/2305.02547, data and code https://github.com/hjian42/PersonaLLM; Serapio-Garcia et al. 2023, https://arxiv.org/abs/2307.00184; Argyle et al. 2023, Political Analysis, https://arxiv.org/abs/2209.06899; Bisbee et al. 2024, Political Analysis (journal page only, no preprint located); Santurkar et al. 2023, https://arxiv.org/abs/2303.17548; Big5PersonalityEssays, Floroiu 2024, https://arxiv.org/abs/2407.17586; Big5-Chat, https://arxiv.org/abs/2410.16491 (100,000 trait-conditioned dialogues, Apache-2.0, generator of the dialogue text not confirmed); PersonalityChat, https://arxiv.org/abs/2401.07363 (ChatGPT dialogues with ChatGPT-inferred trait labels; search summary only, unverified).

### 7.1 What the persona literature asks, and the two PersonaLLM measurements

Its question is fidelity: told to be a person with trait profile X, does the output carry X (PersonaLLM, Serapio-Garcia), and does a population of such outputs reproduce human subgroup distributions? Argyle: yes, within roughly 80 to 90 percent on many ANES items. Bisbee (per the journal abstract; full text not located): group means track but individual-level distributions are far too narrow, so the paper argues against substitution. Santurkar: misalignment with subgroup opinion persists after explicit steering. None of them substitutes machine text into a human sample at an unknown rate and asks what a third-variable correlation does.

PersonaLLM reports two measurements that pull in opposite directions and matter for how c-hat is read. Self-report BFI administered to the persona: effect sizes d between 4.2 and 6.3 for GPT-4, openness the largest. Human judges reading the story text alone: 0.68 individual and 0.84 majority-vote accuracy on extraversion, near chance (about 0.50) on the other four traits, lower still once judges are told the text is machine-written. c-hat is the second kind of quantity, text-embedded signal recoverable by a reader or a classifier, not self-report consistency, and the audit-3 ordering (EXT 0.241 highest, OPN not significant) matches the text-judge ordering at both ends. The paper should say which of the two c-hat is where it first appears.

### 7.2 The collision and its answer

A reviewer who knows this literature will say, correctly, that audit 3's c-hat (a trait classifier's decision score correlated with the pool's own label) is mechanically a persona-fidelity measurement restated. The answer is what the estimator does with it, not a denial: c-hat enters as a measured input to the Att correction and to the label-free prevalence estimator, which no fidelity paper computes; and under P1' coupling is a property of the assignment rule, disclosed as a design parameter, rather than a claim about what conditioning achieved. Lane 2 searched for prior use of label-matched assignment of synthetic text as a coupling manipulation in survey or psychometric work and found only the general matched-pairs and covariate-balancing literature: apparently new, not confirmed absent by an exhaustive search.

### 7.3 Consequence for the three claims

Claim (a), the respondent-side mixture with coupling, is the one that moves. Under P1' it is an injected experimental factor with a stated scope limit, c = p c_pool for p in [0, 1]; under P4 it drops to a passively observed moderator, which nearly eliminates the collision and concedes most of claim (a)'s substance. Claims (b), label-free prevalence and the errors-in-variables correction of a validity coefficient, and (c), the collider analysis of detect-and-delete, are untouched by every pivot; no source found does either.

Lane 2's flagged cost, that the accessible coupling range is bounded by the realized c-hat between 0.11 and 0.24, reads differently on the scale (E7) uses. The coupling that moves Att is c / sqrt(rel_H) = c-hat / r_H by (E65), which is 0.99 on EXT, so the labeled pool matches the human-replica machine's coupling, c = sqrt(rel_H), on the one trait with usable human signal; the human-replica point (E54) itself also needs kappa = 1 and delta = 0, which are not on file (Q11). What is out of reach is the inflation regime g > sqrt(kappa) at kappa = 1, and that was out of reach under the frozen design too, by GEN-CONFIG's c-high blocker. Lane 2's second nuance, that the p = 0 arm is persona-conditioned text decorrelated from its recipient rather than unconditioned text, is stated with its model consequence in section 3.2.

### 7.4 A second labeled pool

Lane 2's corpus search adds nothing usable beyond PersonaLLM. Big5-Chat and PersonalityChat are multi-turn dialogue, further from essay prose than PersonaLLM's stories, and were not scored; lane 2 presumes a genre gap at least as large. Its four-row candidate table (Big5PersonalityEssays verified by audit 1; PersonaLLM verified on disk and in the wide hunt; Big5-Chat partially verified; PersonalityChat search summary only) is in the lane-2 output and is not repeated here.

## 8. Recommendation

### 8.1 Matrix

| shape | rho_H and pi identification | Layer B c-map | H2 homogenization (between-item) | H3 deletion vs correction | boundary results | dollars | external gates | rounds to a Layer B pilot cell |
|---|---|---|---|---|---|---|---|---|
| S0 frozen (14,874 gens) | intact | designed, 2 informative levels, 2 families, kappa-c covariation observable | full (rho_v arms) | Prop. 14 form; collider invisible (2.2) | detector-limited (2.3) plus se at PK's prompt | 115 as designed, 210 all-frontier | key, dry run, quality loop, recalibration | 6 or more plus the key gate |
| P1' assignment-coupled (0 gens) | intact; g-hat SE by (E68), (E69) | designed by p, continuous on [0, g_pool], 1 to 4 generators, kappa-c fixed; genre bracketed by two pools, not matched, and (kappa, delta) on the PersonaLLM pools conflate genre with authorship | Layer A only; chunk form as weak rescue | same as S0 | same, minus se at PK's prompt; A3 checkable; detectability range 0.47 to 0.98 across pools | 0 | none | 3 to 4 |
| P2 truncation of PK (0 gens) | intact; r_H down 26 percent by (E72) | as P1' if combined; none alone | as P1' | variance-dominated at 100 words | as P1' | 0 | none | plus 1 to any design |
| P3 as written (1,200 gens) | intact | confounded contrast, not a map | Layer A only unless the batch adds session arms | as S0 | as S0 | 17 | key, dry run, quality loop, recalibration | 5 to 6 plus the key gate |
| P3' (1,800 gens, all three levels) | intact | designed, 2 informative levels, 1 family, kappa-c observable, PK's own prompt | full if session arms are added (more gens) | as S0 | as S0 | 25 | same as P3 | 5 to 6 plus the key gate |
| P4 reframe (0 gens) | intact | one realized point per labeled pool | as P1' | as P1' | as P1' | 0 | none | 3 to 4 |

Rounds are lane rounds (one round bundles discovery, implementation, review and run for one lane); the cost pass's finer decomposition of the same work counts 8 to 9 steps for P1' and 8 to 10 for the generation shapes, plus a key gate that no file can clear. Not calendar time; the estimate-actual log is empty, so no wall-clock range is calibrated. Dollar rates: 105 / 7,437 = 0.0141 per frontier generation under GEN-CONFIG's even family split; open-weight under 0.0014. The Layer B injection module exists in no lane (grep for inject across the tree, cost pass), so every shape pays for it once.

### 8.2 The path

P1' is the Layer B design. Concretely:

1. Lane 3, one round, existing scripts extended to save per-text scores: score the PersonaLLM pools (three generators), the Big5 pool and the three unlabeled pools with the audit3 trait models (PK cross-fitted) and the roberta detector; report per trait and pool (r_H, raw c-hat, kappa, delta, detector AUC), with per-text scores persisted so lane 4's inject module can compute the reweighted c_q, kappa_q and delta_q at the base's prevalence (section 9.1), the A3 check (detector score against label inside each labeled pool), the Spearman-Brown check at 100 and 190 words, and human_stories scored against essays.csv to measure what the name masking does to both scores (human_stories is essays.csv with named entities masked, L3-a; the human side is scored on essays.csv itself). This is also the first empirical content of the paper: the realized (g, kappa, delta) of persona-conditioned text on four generators.
2. Lane 4, one round plus Fable review: pool loader, assignment rules (random, matched, p-matched), bootstrap of the PK base at the SPEC n and pi cells, held-out and transfer references for 3.2, chunk pseudo-items for the weak H2.
3. Layer B pilot cell: EXT, pi = 0.10, n = 1,000, p in {0, 1}, one generator; closed form (E7) at the measured (g, kappa, delta) against the injected mixture, the same PASS discipline as PILOT.md.

Predicted contrast at that cell, conditional on kappa = 0.5 and delta = 0: Att = 0.923 random versus 0.994 matched, a difference of 0.017 in correlation units at rho_H = 0.244, resolvable over 100 replicates (SE of the mean 0.003). At pi = 0.30 the difference is 0.055.

Layer A does not gate any of this. GRID-PROGRESS.md is a live file that refreshes as cells finish; at 19:48 it showed the 372-cell grid running since 16:29 with 28 cells done, cost-weighted ETA 2026-09-10 13:31, and per-rep cost 2.6 to 4.6 times GRID-CONFIG's projection; board.md's lane-4 line was updated on 2026-09-07 evening to say the grid is running (its BLOCKED clause was stale). The Layer B pilot cell compares the injected mixture with the closed form directly and needs no grid output.

P3' (1,800 generations, with two extra session arms for rho_v if the budget for a few hundred more generations is accepted) is the robustness appendix. It fires when a key exists, and its results go in an appendix column: PK's own prompt, a 2025 generator, the kappa-c covariation, and detector sensitivity at PK's prompt. It does not gate the preprint. The frozen 14,874 batch stays shelved: the two-family, three-level structure it paid for is delivered by four generators and a continuous p axis at zero generations.

Two things this path asks of Abhay: nothing on money or keys for the critical path; the N2 estimand call was still open when this memo was written [decided 2026-09-07 20:58: observed-score headline; day-2 section 8, marker DONE-N2], and under the decree the amanuensis sentence is signed as inflation; the EXT arm made it concrete in LAYERB-PILOT.md at g = 2.42 on the PersonaLLM gpt-4-0613 pool with the ridge score, not the g near sqrt(kappa) projected here for the Big5 pool.

### 8.3 New open items (to be appended to lane1-open-questions.md)

Q11. kappa and delta of the trait score are not on file for any pool; every Att number in this memo is conditional on kappa = 0.5, delta = 0. Owner: lane 3, step 1 above.
Q12 (closed 2026-09-07 20:05, two ways). Balance of the Big5 pool's labels per trait, counted read-only from essays.xlsx sheet Foaie1: 399 essays, high-label counts OPN 214, CON 214, EXT 217, AGR 221, NEU 201 (shares 0.504 to 0.554), so the pool is near balance; and with lane 4's reweighting hook (E73) Prop. 16 is exact at any pool balance, so the matching step reweights nothing in any case.
Q13. Whether either labeled corpus has an unconditioned arm. Lane 2's in-session report found none for Big5PersonalityEssays in the abstract, repo or paper (PDF fetch failed): unverified-absent, not confirmed-absent. PersonaLLM's prompt is a story-writing prompt with a word target (same report, from the paper); an unconditioned arm was not looked for. Owner: lane 2, which should also file that report under lane2-novelty (section 7).
Q14. Whether the chunk form of H2 is worth reporting or only mentioning; depends on the human between-chunk baseline on PK. Owner: lane 1 after step 1.

DONE-PIVOT-MEMO

## 9. Addendum (2026-09-07, 20:05): reconciliation with lane4-simulation/INJECT.md

Lane 4's injection module (INJECT.md, 41/41 tests, INJECT-DONE) raised two items for lane 1. Both are settled here; the body of the memo was corrected in place with dated tags at the places this section cites.

### 9.1 Prop. 16 restated with the reweighting hook, both balance assumptions dropped

What the draft assumed. The draft's Prop. 16 drew the random branch uniformly from a pool taken to be label-balanced, and its proof integrated over "a balanced L_i". That is two balance assumptions: the pool's (Q12) and the base's. The base's was never written down, and it does not hold: PK's label prevalence by trait is cEXT 0.517, cNEU 0.500, cAGR 0.531, cCON 0.508, cOPN 0.515 (essays.csv, counted read-only 2026-09-07), and any target sample has its own.

The hook. Draw the random branch by (E73): a label at the respondent prevalence q, then a text uniformly inside that label cell. Prop. 16 as now stated in 3.2, with (E67) and (E74), is exact for every pool balance, every respondent prevalence and every p. The proof in 3.2 is the whole argument; the one-line reason is that the p-mixture of "the respondent's own cell" and "a respondent-marginal draw" has, marginally over respondents, the same law G = q_0 F_0 + q_1 F_1 for every p, so the only p-dependence left is in the covariance with L_i, and that is linear.

What the draft rule does. Under any random branch whose label marginal differs from q (uniform over the pool, or the draft's 50/50 across labels), the marginal of x_M is p G + (1 - p) S with S the random branch's law, which depends on p unless S = G. The covariance is still p q_0 q_1 (m_1 - m_0) and g(p) = p g_pool still holds exactly, because (E66) divides two covariances at the same prevalence; what bends is kappa(p) and delta(p), and through them c(p) = g(p) sqrt(rel_H / kappa(p)). Lane 4 measured this as arithmetic identities on a finite pool, not by Monte Carlo (INJECT.md section 3): table E (balanced pool, base at q_1 = 0.1, draft rule) has c(p) off the line by up to 1.4e-2 and kappa sliding from 0.981 to 0.791 across the sweep; table C (80/20 pool, uniform draws) has kappa 1.004 to 1.153 and delta 0 to 0.415. A p sweep under the draft rule moves three of Att's four arguments at once. On PK's own prevalences the bend would have been small (q_1 within 0.031 of 1/2 on every trait; table E's 0.1 is a stress case), but the hook costs nothing and removes it exactly, so it is the rule.

Two coupling numbers, not one (INJECT.md section 4). The p = 1 endpoint the design realizes is c_q of (E74), the pool's coupling under the base's label prevalence. Audit 3's c-hat is the pool at its own label shares s = (N_0 / N, N_1 / N): c_s = sqrt(s_0 s_1) (m_1 - m_0) / sqrt(Var_s(x)). They coincide iff s = q. On this testbed the difference is small (Big5 shares 0.504 to 0.554 against PK's 0.500 to 0.531, so sqrt(q_0 q_1) / sqrt(s_0 s_1) is within 1 percent of 1 and the variance term moves less); on an 80/20 pool lane 4's example gives reweighted 0.574 against raw 0.489. The paper indexes the attenuation curve by c_q at the realized q_1 and reports raw c-hat in the pool-measurement table as a property of the corpus; captions name which one they show. The tables in 2.1 and the ratios c-hat / r_H are raw c-hat, as lane 3 measured them; step 1 of 8.2 now asks for per-text scores so lane 4's module can compute c_q, kappa_q and delta_q at the base's q.

Sampling error. (E68) was written for balanced cells; with pool cells at shares s the first term becomes 1 / (4 s_0 s_1 c^2 n_M), about 1 percent larger at the Big5 shares, and the human term is unchanged because cross-fitting scores every PK essay. Nothing else in 3.2 or 3.3 changes: the coverage arithmetic (now with the measured Big5 cells, 178 to 221) and the cross-fitting rule stand.

Where it lives. Prop. 16, (E73) and (E74) are stated in 3.2 above with a dated tag; lane1-partial-coupling.md is not touched (its propositions end at 15 and it never stated Prop. 16). Q12 in 8.3 and in lane1-open-questions.md is closed on both grounds: measured near-balance, and irrelevance under the hook.

### 9.2 delta's sign: one convention, binding

Binding definition: delta := (mu_H - mu_M) / sqrt(V_H), positive when the human mean exceeds the machine mean. It is day 1's (lane1-zero-coupling.md line 38), inherited unchanged by day 2 (which defines no delta of its own; (E47)'s delta_pass = delta + r_F lambda sqrt(rel_H) adds the survivors' human-mean shift to delta, which is this orientation), and it is CONVENTIONS.md line 46, which lane 4 codes. The draft of this memo's section 1 wrote (mu_M - mu_H); that was the odd one out and is corrected in place. No number in any lane-1 or lane-4 file moves: Att depends on delta^2, and every signed use of delta in day 2 was derived under the day-1 orientation. The notation table carries the day-1 form and cites CONVENTIONS.md line 46 as its code-side twin.

DONE-RECONCILE
