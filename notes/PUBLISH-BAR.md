# Publish bar: ghost-respondents draft 2

Judged 2026-09-13 against `paper/GHOST-RESPONDENTS-DRAFT.md` at commit 9e90bc6 (voice gate
PASS on c5136ad). Every number this verdict leans on was recomputed from the grid JSONL in
this session (`scratchpad/recompute.py`, `recompute2.py`); the estimator unit tests were
re-run (39/39, `test_estimators.py`; `test_population.py` all pass); `check_numbers.py` was
re-run (427 of 430 keyed numbers present in the draft). Nothing in the repo was edited.

## 1. Verdict

**Publishable after iteration.** Not publishable now, and not at Psychological Methods in
this form. The numbers are sound and reproducible; the claims around them are not yet what
the evidence supports, and the testbed is too weak to carry the practice recommendations
the discussion makes. A trimmed version is a preprint-tier working paper in one or two
writing rounds. A version a survey-methods journal would take needs two follow-up
experiments the repo has already designed (docs/FOLLOWUP-EXPERIMENTS.md E2 and E3).

## 2. What the paper actually shows

A two-component mixture (human process plus machine process with coupling c to the trait,
homogenization kappa, mean gap delta) gives a closed-form multiplier Att(pi, c) on the
observed validity coefficient; the algebra is exact against 372 parametric Monte Carlo cells
(max |z| = 3.16 against a 4.08 bar, 1116 moment checks). On a semi-synthetic testbed
(Pennebaker-King essays, binary median-split Big Five labels, MiniLM 256-token chunk scorer,
PersonaLLM gpt-4-0613 and llama-2 pools from 2023, roberta-base-openai-detector), the
single-chunk human validity is rho_H = 0.068 and the naive RMSE at n = 1000 is 0.032, so
contamination bias (from -29% to +47% relative at pi = 0.30, under 0.01 absolute below
pi = 0.10) is resolvable in 34% of cells at 100 reps and 46% at 500 reps. In that regime none
of detect-and-delete, misclassification SIMEX, label-free prevalence + EIV, or two-class EM
beats the naive correlation: naive has the lowest RMSE in 274/336 cells, the best corrector
meets the "20% of naive bias" bar in 37/130 resolvable cells, prevalence estimates miss by
0.05 to 0.06 against a 0.02 bar, and EM's |bias| exceeds naive's in 157/280 cells. In the
parametric layer (rho_H = 0.418, bias-dominated, median |naive bias|/MCSE = 6.6) the
corrections are still weak: SIMEX meets the bias bar in 38.6% of 210 applicable cells,
label-free in 0% (60 bins) or 9.5% (8 bins), and only deletion reaches nominal rho_H coverage
regularly (309/372). The deletion-selection channel is O(r_F^2); the surface-proxy r_F on
this corpus is 0.053 (composite) and the detector's own score correlates with the labels at
|r| <= 0.045 (computed here from `pk_human.json`), so it is negligible at any tested operating
point. A partial-identification interval that takes pi, kappa, delta and rel_H as known and
brackets c in [0, 1], unioned with a Fisher-z interval, covers rho_H in 93.6% to 100% of
replications per cell (median 97.4%) at a median width of 0.14, which is 1.28 times the naive
Fisher interval and never narrower than it in any of the 372 cells.

That is a clean, reproducible negative result on one testbed, plus exact algebra. It is not
yet a general statement about survey practice.

## 3. Gap list: current draft to PhD-publishable

Sized in agent rounds (his estimate rule), with the hours/days label the brief asked for.
One round is one discovery-or-build-or-verify pass by a lane.

### Claim-level gaps (writing, hours-class)

**G1. The "constructive half" is overclaimed.** Abstract: "The partial-identification bound
meets its target." 1.2: "The fourth is the constructive half of the paper." 6.2: "It does not
need labels, a detector, or a correctly specified mixture. It does need pi." What
`fit_bounds_c` does (estimators.py:798-861): reads pi, rel_H, kappa, delta from the true
cell parameters, divides a 95% Fisher interval on rho_obs by Att at c = 0 and c = 1. With
four nuisance parameters known and the true c inside [0, 1] by definition, coverage at or
above 95% is guaranteed by construction, and my recompute shows the interval is wider than the
naive Fisher interval in 372/372 cells (median ratio 1.28). It is the naive interval inflated
by a known-nuisance identification band, not a field-usable bound. Section 3 states the
four known inputs; the abstract, 1.2 and 6.2 name only pi. Fix: report it once, in 5.4, as a
sensitivity band conditional on (pi, kappa, delta, rel_H), drop it from the abstract's
headline and from 1.2 item 4, and rewrite 6.2 to say what it actually requires. 1 round.

**G2. "Pre-registered" is not pre-registration.** Used 7 times (abstract, 1.2, 3, 4.3, 5.1,
5.4, 6.2). SPEC.md is a file in a private repository, frozen at commit db7c171, amended
2026-09-10 after the grids ran (commit 4fcceb2), never registered on OSF or AsPredicted, and
the H5 estimator it names did not exist at freeze time. A methods reviewer will treat the
word as a misuse. Fix: "thresholds fixed in the analysis plan before the grid ran (SPEC.md,
commit db7c171; not externally registered)", once, and "the analysis-plan thresholds"
thereafter. Combine with G1. 0 extra rounds.

**G3. The boundary map's cell winners are Monte Carlo noise.** Table 7 and Figure 2 report
min over five estimators of |relative bias| at 100 reps, where the relative MCSE is 4.6% per
estimator. Taking the minimum of five noisy near-zero quantities yields 0.00 to 0.05 by
chance; 61 of 72 cells are under 0.10, and the winner tally (naive 17, delete 17, simex 17,
em 11, labelfree 10) is what a uniform draw looks like. The sentence "No cell is uniformly won
by a correction ... no estimator wins a majority anywhere" presents noise as a finding. Only
the three cells above 0.30 (p = 1, pi >= 0.20, none and calibrated) carry signal, and Table 3
already shows them. Fix: shade the map by whether the naive bias is resolvable (> 2 MCSE),
print per-cell MCSE, drop the winner labels and the majority sentence, and say the map has
three resolvable cells. 1 to 2 rounds (regenerate fig2 via make_figures.py).

**G4. r_F is under-reported against the repo's own files.** 5.6: "individual proxies up to
0.073 on OPE and CON". `fluency_r_f_results.json` has avg_word_len vs cOPN at r = 0.161,
three times the headline and excluded from the composite without a stated reason. Separately,
the model's F is the detector score, and the detector score is on disk
(`pk_human.json::detector_p_machine`): point-biserial against the five labels is -0.014,
+0.020, +0.027, +0.045, -0.013 (Spearman max 0.070 on CON). That is the r_F the derivation
actually needs, it is smaller than the proxy, and it strengthens 5.6. Fix: report the direct
detector-score r_F as the anchor, the proxy composite as secondary, and the 0.161 explicitly.
1 to 2 rounds (script plus rewrite of one paragraph and Table 11 caption).

**G5. Overreach in the discussion.** 6: "The results license a set of recommendations at the
operating points the field faces". The field's operating points are 2026 detectors on
questionnaire-length answers; the testbed is a GPT-2-era detector on 2023 essays, and the
Limitations section says so. 1.2 item 2: "That single number [27% sensitivity] does more to
explain the correction results than any property of any estimator", yet the corrections also
lose on Layer A with a (0.95, 0.99) detector and naive still wins 47/72 oracle cells; the
explanation the paper itself gives is variance dominance at rho_H = 0.068. Fix: recommendations
1 to 7 become "on this testbed, and where the operating point matches"; cut the 1.2 item 2
sentence. 1 round, combine with G1.

**G6. Reader-facing hygiene.** Citations to internal memos a reader cannot open ("lane 2
positioning memo, claim (c)" in 1.1 and 1.3; "lane 2 pivot positioning"); "the joint-scoring
model cited above" in 1.3 has no reference entry; the Muse product launch as the opening
paragraph of a methods paper; "Two scope statements. First ... Second ... Third" in 5.4; no
generative-AI-use statement although the verification record cites re-derivation "by a second
model family" and SPEC section 6 describes the whole build as agent-run (APA journals require
the statement). Fix: one pass. 1 round.

### Evidence-level gaps (days-class)

**G7. The negative result is pinned to one weak testbed.** rho_H = 0.068 from a 256-token
chunk scorer on median-split labels, one 2019 detector, two 2023 generators, a synthetic
outcome, essays rather than survey answers. Every threshold failure is downstream of the
estimand being small relative to sampling noise. The draft's own follow-up doc names the fix:
E2, the core box on OPE and NEU with the document-pooled scorer (whole-text validity 0.31 and
0.23 versus 0.068 here), with the pre-stated prediction that naive's 274/336 falls below one
half. Without it, a reviewer's first comment is "your corrections failed because your
measurement is noise, not because they fail." 5 to 8 rounds plus grid compute (the 336-cell
grid took 3 hours on 10 workers; 432 cells at 200+ reps is an overnight run).

**G8. The detector axis is at its weakest point.** Sensitivity 27% on frontier text is a
RoBERTa-on-GPT-4-0613 fact. E3 (a detector transfer panel: at least one 2025-26 open
detector on the existing pools, with the direct detector-score r_F per detector) turns Table 1
from an artifact into a measured axis and makes recommendation 3 defensible. 3 to 5 rounds,
detector runs only, no new text generation.

**G9. Repo not in publishable state.** The paper cites repo paths throughout. The repo holds
prompts/, lane logs, Astra re-reviews, in-sample partial grids and pyc files. Publishing the
paper means publishing a cleaned repo (or a Zenodo snapshot of the artifacts of record) with
a README that maps sections to files. 1 to 2 rounds.

### Reputational gap (his, not the paper's)

**G10. He has to be able to defend it unprompted.** The derivations, the re-derivation, the
adversarial review and the draft were produced by agent lanes (SPEC section 6). A committee
member who asks him to derive E39 or explain why Imbens-Manski unions the two intervals will
find out in one question whether the paper is his. Before the name goes on it: re-derive E7,
E39 and Prop. 11 by hand and be able to state G1 in his own words. Not sized; it is his
time.

## 4. Iteration list, priority order, smallest first

Rounds A through F are writing only and produce the preprint-tier version. G and H produce
the journal-tier version.

| # | item | closes | size |
|---|---|---|---|
| A | Rewrite abstract, 1.2 item 4, 5.4 bullet and 6.2 so the bound is a conditional sensitivity band; replace "pre-registered" per G2; cut the 1.2 item 2 sentence; scope recommendations per G5 | G1, G2, G5 | 1 round, hours |
| B | Hygiene pass: internal-memo citations, missing reference, Muse opener to one sentence, "Two/Third" fix, AI-use statement | G6 | 1 round, hours |
| C | Direct detector-score r_F script into lane3/analysis, report it and the 0.161 proxy in 5.6 and Table 11 | G4 | 1 to 2 rounds, hours |
| D | Boundary map regenerated as a resolvability map with per-cell MCSE; Table 7 and the two sentences in 5.4 rewritten | G3 | 1 to 2 rounds, hours |
| E | Re-run check_numbers.py and the voice gate on the result | verification | 1 round |
| F | Repo cleanup and a mapped README; decide public repo vs Zenodo snapshot | G9 | 1 to 2 rounds, hours |
| G | E3 detector panel (one modern open detector on the existing pools, direct r_F per detector); Table 1 and 5.6 updated | G8 | 3 to 5 rounds, days |
| H | E2 document-pooled box on OPE and NEU, thresholds re-scored, 274/336 prediction tested; results section restructured so Layer A and both Layer B scorers read as one ADEMP-style study | G7 | 5 to 8 rounds plus overnight compute, days |

Iteration closes the gap. A through F make the paper true to its evidence; G and H make the
evidence strong enough for the claims a survey-methods journal expects. Neither requires new
data collection; E4 (a live Prolific experiment with IRB) is the one item that would change
the paper's class and it is out of scope for an iteration list.

If H comes back with naive still winning a majority at rho_H near 0.3, the negative result
generalizes and the paper gets stronger. If corrections start winning there, the paper becomes
the boundary map it says it is, with a real boundary. Either outcome is publishable; the
current single-testbed version is not the one to put his name on.

## 5. Venue fit

- **After A through F:** working paper on PsyArXiv or arXiv (stat.ME), plus an AAPOR or
  ESRA talk. Honest tier for a single-testbed negative result with exact algebra.
- **After G and H:** Journal of Survey Statistics and Methodology, Survey Research Methods, or
  a research note in Sociological Methods and Research (where Zhang, Xu and Alvero sits). These
  venues publish "we tested the obvious corrections and here is where they fail" with a
  simulation study; Behavior Research Methods is the psychology-side equivalent.
- **Psychological Methods:** not the venue. It wants a new estimator or a general result, and
  the paper's only positive constructive piece (G1) does not survive scrutiny. Target it only
  if E4 runs and the mixture model gets validated on real respondent behavior.
- **Blog tier:** section 6's decision rules and Figure 1's three-regime map, standalone, are a
  good post today. Not a substitute for the paper and should not carry the recommendations
  as general advice.
