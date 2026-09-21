# DRAFT - Oct 1 monthly update to Johnny Zhang (draft only, not sent; Abhay sends from his own address after edits)

Subject: October update - ghost respondents: the thresholds failed, and that became the paper

Johnny -

One month in on the project I mentioned: survey respondents quietly pasting items into ChatGPT, treated as a measurement problem instead of a detection problem. The short version: my pre-registered thresholds mostly failed on real text, and the failure turned out to be the finding.

The framing is close to your APS talk with Lingbo - text data inside an SEM. Covert AI authorship makes the sample a mixture of two measurement processes (human and machine) with different reliabilities and factor structures at an unknown contamination rate. Detect-and-delete assumes you can identify the machine half; detectors misclassify, and deletion is non-random (it preferentially kills non-native and stilted human writers). So I derived the mixture, estimated the contamination fraction without gold-standard labels, and built an errors-in-variables correction that recovers human-only construct relations.

What September produced:

- The full simulation grid completed: 372/372 cells, plus a 336-cell Layer B grid on out-of-fold scores. One headline from the pilot survived everything: the assignment rule alone flips the sign of the bias (random assignment attenuates, trait-matched amplifies), and the three-regime contamination map confirmed on real text (-29% dilution to +47% inflation).
- The honest part: 3 of 4 pre-registered thresholds fail on real text. At real operating points the regime is variance-dominated, so every correction adds more variance than it removes and the naive estimator has the lowest RMSE. The anti-deletion headline I wanted only survives conditionally, with an r_F sensitivity table.
- Two adversarial reviewers (blind to each other) independently said the publishable paper is the boundary map: here is exactly when deletion helps, when correction helps, and when nothing beats naive. That is the pivot I am writing now.
- Rigor notes, since you will ask: the math survived blind independent re-derivation to 2.7e-15. Two artifacts were caught by process, not luck - a calibration-split draw that faked an EIV failure (splits are now frozen across waves), and a leaky chunk-scoring path that inflated validity 1.76-4.43x before out-of-fold scoring brought it to 0.76-0.91x.

Where this sits, since you asked in September whether the framing fits the program: my research is about what happens when a person's behavioral record includes their conversation with an agent. Your text-in-SEM work treats text as an instrument whose measurement error has to be carried into the model; I want to do the same for a multimodal record, the passive digital-phenotyping streams the field already has (sleep, activity, screen time broken down by content type) fused with the conversation and interaction stream an agent holds, which may be the densest longitudinal behavioral data psychology has had. The target is not a depression score but a trajectory: is this person drifting toward depressive symptoms, and can the agent's own responses lead them away from it. The design is incremental by construction, every model of the agent stream against the phone and wearable baseline, with the fusion tested rather than assumed; my validity ceiling paper gives that baseline a number on NHANES (sleep, activity and alcohol self-reports cover 0.384 of PHQ-9 trait variance, 89% of the cross-validated signal in the sleep block). It is a psychometrics problem first because the agent adapts: in a linear-Gaussian simulation (72 cells, 15,450 replicates) the ordinary validation battery, including longitudinal metric invariance, passes .93 to .98 of the time while the latent variance is inflated up to three times, and a correction built on a logged nonadaptive anchor recovers it within .02 where its assumptions hold and refuses to report where they do not. The same NHANES work found the PHQ-9 non-invariant across race-ethnicity and income by item-level effect size while the conventional fit-index rule declared all fifteen constrained steps supported. No diagnosis, no labels, no medication, and no claim that conversation data alone is clinical ground truth. Ghost is the concrete piece of method inside that frame, and the writing sample you asked for is the next one.

Two threads that connect to your line on validating AI instruments:

- Prompt sensitivity is alternate-forms reliability. I am treating the NLP prompt-robustness literature as a reliability problem and running prompt-paraphrase robustness as a reliability analysis of the machine half of the mixture.
- Zero-self-report streams avoid the reactivity that EMA documentation keeps showing (KULEuven/JMIR Formative cites on file) - relevant to where the behavior-stream work goes after the preprint.

Next month: boundary-map tables and figures, the working paper, and the reproducibility bundle. Lingbo and I met on the 14th - [ONE LINE ON HOW THAT WENT, fill in before sending].

Abhay

---
NOTES FOR ABHAY (delete before sending): bracketed Tong line needs the meeting outcome. The direction paragraph was added 2026-09-21 from the vault's 08-Sharp-Statement ("For Zhang" variant); its numbers come from agentsem-trap-world MORNING-HANDOFF.md and depression-behavior-modeling VALIDITY-CEILING.md, re-read them before sending. Radar backup for every claim: RADAR-DAY6/7/8 in lane4-simulation/. The 3/4 threshold failure is stated plainly on purpose - Zhang respects honest nulls more than polished ones.
