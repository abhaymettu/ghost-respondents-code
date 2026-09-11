# Follow-up experiments for the boundary-map paper

Internal, 2026-09-11. Five experiment designs that would strengthen
`paper/GHOST-RESPONDENTS-DRAFT.md` in its boundary-map form. Each one targets a named seam in
`paper/REWRITE-NOTES.md` ("Open seams") or `lane4-simulation/ESTIMATOR-FIX-REPORT.md`, and each
is written so a lane could be dispatched from it: design, conditions, measures, a power sketch,
threats to validity. Nothing here is run; the one new number in this file is the pilot
correlation in E3, computed today from files already on disk, with the script inline.

Ordering is by expected value per unit of work, not by how interesting the result would be.

| # | experiment | seam it closes | new data collection | rough cost |
|---|---|---|---|---|
| E1 | High-coupling pools from generation-time prompting | c capped at 0.379; high-c corner unreachable | LLM generations (lane 3 already has the runner) | API spend plus one Layer B grid |
| E2 | Layer B on a document-pooled scorer, on the trait it helps most | rho_H = 0.068 makes the box variance-dominated | none (re-score existing corpus) | one scoring pipeline plus one grid |
| E3 | Detector transfer panel measuring the real collider r_F | one detector, two 2023 generators, r_F from a proxy | none for the panel; E1 pools if available | detector runs only |
| E4 | Live respondent experiment with randomized AI assistance | synthetic outcome; rematched texts; binary labels; r_F is a lower bound | yes, n about 1,200 on Prolific | participant payments, IRB |
| E5 | Survivor-sample bound and a gold-subsample arm for `bounds_c` | H5 bound ignores the detector; no labeled subsample anywhere | none for part (a); E4's labels for part (b) | derivation plus Layer A column re-runs |

Shared conventions: Layer A means the 372-cell parametric grid (`lane4-simulation/results/grid/`),
Layer B means the 336-cell real-text grid (`results/layerb-grid/`). MCSE figures assume the
Pearson sampling SD of about 1/sqrt(n) at small rho, which is what section 4.2 of the draft uses.

---

## E1. Reaching the high-coupling corner with generation-time prompting

**Why.** The boundary map's real-text evidence stops at c = 0.379 because assignment coupling
cannot exceed the pool's own coupling (Prop. 16, c(p) = p c_pool). SPEC's failure mode 1
(identifiability collapse at high c, correction reverts to bounds) is the corner the paper
most wants to show and cannot. Coupling is a property of how the machine text was produced,
so the lever is generation, not assignment.

**Design.** Generate new machine pools from the same 2,467 Pennebaker-King essays at three
prompting levels, then run the injection design at p = 1 on each pool. `generate_counterparts.py`
already implements two model families times three coupling levels (`c0` prompt only,
`partial` trait-band sketch, `high` trait labels stated as fact) against every essay, 14,874
generations, gated behind a dry run and a cost check (`GEN-CONFIG.md`). Add one level above
`high`:

- `c0`: persona-free prompt (the PersonaLLM-style baseline the current pools approximate).
- `high`: the respondent's five binary labels stated as fact in the system prompt.
- `polish` (new): the respondent's own essay is supplied and the model is asked to rewrite it
  as a submitted answer. This is the "paste my answer into the model and submit what it
  returns" behaviour the introduction describes, and it should push c toward its ceiling
  because the machine text inherits the human text's trait signal directly.

Two generators: one 2026 frontier model and one open-weight model, so the generator axis of
the current paper (gpt-4-0613 versus llama-2) is reproduced with current models.

**Conditions.** 3 prompting levels x 2 generators = 6 pools. For each pool: lane 3's pool
measurement (c_pool, kappa, delta, g) at all five traits, then a Layer B core box on the
trait with the highest c_pool (pi in the six current levels x detector in four levels x n in
{1000, 2400}, p = 1 only, 100 reps) = 48 cells per pool, 288 cells total.

**Measures.**

1. Primary: c_pool per pool. The experiment succeeds as infrastructure if `polish` gives
   c_pool above 0.6 on at least one trait, which puts a Layer A "high" cell (c = 0.9 is the
   Layer A value) within reach on real text.
2. The boundary map extended along c: for each estimator, RMSE relative to naive and bias
   relative to the T1 bar, in the new cells.
3. Whether the bounds estimator's width grows with c as (E36) predicts (affine, increasing).
4. Detector realized sensitivity on each pool at sp = 0.99 and 0.85. `polish` text is the
   interesting case: it is machine-written but anchored to a human draft, and current
   detectors are known to weaken on edited or mixed text (see `LIT-SCAN.md`, detection
   section, mixed-authorship entries).

**Power sketch.** c_pool is a correlation between the scored machine text and the label, so
its 95% half-width at 320 texts is about 0.11, and at 2,467 texts (every essay gets a
counterpart, as the script already does) about 0.04. The full batch is the right size; a
320-text pilot cannot distinguish c = 0.5 from c = 0.38. For the grid cells the question is
whether bias differs across c levels, and Table 3's per-cell MCSE of about 0.003 at 100 reps
resolves differences of 0.006 at 2 MCSE; the c = 0.38 to c = 0 difference at pi = 0.30 is
already 0.051, so 100 reps per cell is enough if `polish` lands anywhere near its ceiling.

**Threats to validity.**

- `polish` text shares surface content with the human essay, so an out-of-fold scorer that
  never saw the parent essay still sees a paraphrase of it. That is the intended mechanism
  (coupling), not leakage, but the scorer's fold assignment must treat the counterpart as
  belonging to the parent essay's fold. Verify this before the grid, not after.
- kappa and delta will move together with c, so the new pools are not a clean c-only
  manipulation. Report the (c, kappa, delta, g) tuple per pool and compare against the
  (E7) closed form, as lane 3 already does, rather than attributing everything to c.
- Generator-specific homogenization: the 2026 frontier model may produce text with kappa far
  below 0.8, which changes which regime a cell lands in independent of c. This is a finding,
  not a confound, provided the tuple is reported.
- Cost gate: `GEN-CONFIG.md` requires a dry run and a no-objection window before `--fire`.
  Adding a fourth prompting level raises the batch by a third.

---

## E2. Layer B on a document-pooled scorer, on the trait where it matters

**Why.** The draft's own explanation for every threshold failure is that rho_H = 0.068 is
smaller than the sampling noise of the coefficient. `PASS3-FIXES.md` T3 shows document
pooling raises whole-text validity, but unevenly: EXT barely moves (0.165 to 0.168) while
NEU (0.105 to 0.228) and OPE (0.223 to 0.311) roughly double. The current core box is on EXT,
which is the trait document pooling helps least. The right follow-up is not "rerun EXT
doc-pooled" but "rerun the box on OPE, where the estimand is 2.3x larger."

**Design.** Swap the chunk-1 prefix-ridge scorer for the 4-chunk-mean-embedding scorer,
keeping the strict out-of-fold protocol from `CHUNK-REFIT.md` (fold model never saw the
parent essay), and rerun the Layer B core box on OPE and NEU. The machine pools are scored by
the same fold ensemble, so their (c, kappa, delta, g) tuples are re-measured under the new
scorer; nothing from the EXT tuple carries over.

**Conditions.** Core box shape, two traits: pi(6) x detector(4) x n in {500, 1000, 2400} x
p in {0, 0.5, 1} = 216 cells per trait, 432 cells. Replications: see the power sketch; the
current 100 is too few at the current estimand and probably enough at the new one.

**Measures.**

1. rho_H under the new scorer per trait (the estimand), with its chunk-consistency check
   (the 11.5x reliability overstatement in section 4.2 should shrink if the pooled score
   is closer to a whole-document measurement; report the ratio).
2. All four SPEC 4.4 thresholds, scored exactly as in section 5.3.
3. The primary boundary-map statistic: the fraction of cells in which naive has the lowest
   RMSE (274/336 on EXT). The pre-stated prediction is that this falls below one half at
   pi >= 0.10, which is what Layer A shows at rho_H = 0.418 ("deletion beats naive in 60% of
   calibrated cells", section 6).
4. Where the bias-dominated boundary sits in (pi, c) under the new estimand, as a contour.

**Power sketch.** On OPE the truth becomes about 0.5 x 0.311 = 0.156. Contamination bias at
pi = 0.30, c = 0.38 scales with rho_H, so the analogue of Table 3's +0.032 becomes roughly
+0.073 while the per-rep sampling SD at n = 1000 stays near 0.031. Replications needed so
that 2 MCSE equals half a T1-sized bias (20% of naive bias, about 0.015 at pi = 0.30) are
about 70 at n = 1000 and 17 at n = 5000; 100 reps per cell is adequate for pi >= 0.10 and the
pi <= 0.05 cells will remain unresolved noise, as they are now. Run 100 reps everywhere and a
500-rep slice at pi <= 0.05 only if the boundary contour lands there.

**Threats to validity.**

- Document-pooled scores of the machine pools may shift kappa more than they shift c, because
  averaging four chunk embeddings suppresses within-text variance for both classes. Re-measure
  the tuple and compare against the chunk-1 tuple before interpreting any grid difference as
  "higher validity."
- The detector still scores the whole text, so nothing changes on the detection side. The
  experiment moves the estimand only; any change in the boundary map is attributable to
  rho_H alone, which is the point.
- T3's caution: chunks are sentence-count based, each chunk is still truncated at 256 tokens,
  and complete token coverage was not verified. Report the retained-token fraction per essay
  alongside the validity, or the "document-pooled" label overstates what was scored.
- Trait choice is post hoc (picked because it helps). State it as such; the EXT result
  stands as the pre-registered case and the OPE result as the sensitivity case.

---

## E3. Detector transfer panel that measures the real collider

**Why.** Two limitations compound. First, one detector (a GPT-2-era RoBERTa) on two 2023
generators is the whole detection evidence, and section 7 says a 2026 detector on 2026 text
"would differ in an unknown direction." Second, r_F was measured as a point-biserial between a
surface fluency proxy and the binary label, not between the detector's own score and the
trait. The selection channel in section 2.3 runs on the detector score. The proxy stands in
for it.

**Pilot number (computed 2026-09-11, not in the paper).** `data/scores/pk_human.json` already
holds the RoBERTa detector's p(machine) for all 2,467 human essays, so the direct quantity is
available for the one detector on file. Point-biserial between the detector logit and each
binary label:

| trait | r(logit, label) | P(flag given L=1) minus P(flag given L=0), sp = 0.85 |
|---|---|---|
| EXT | -0.004 | -0.004 |
| NEU | +0.020 | +0.018 |
| AGR | +0.031 | +0.025 |
| CON | +0.064 | +0.039 |
| OPE | -0.009 | -0.009 |

The largest magnitude, 0.064 on CON, is the same order as the proxy's 0.053 and lands in the
same row of Table 11 (under 0.2% of trait variance destroyed). This is a consistency check on
the paper's r_F, not a replacement, because the labels are still median splits. Script:

```
cd lane3-testbed && .venv/bin/python - <<'EOF'
import json, numpy as np
s = json.load(open('data/scores/pk_human.json'))
d = np.clip(np.array(s['detector_p_machine'], float), 1e-6, 1-1e-6)
lg = np.log(d/(1-d)); f85 = d >= np.quantile(d, .85)
for t, l in s['labels'].items():
    l = np.array(l, float)
    print(t, round(np.corrcoef(lg, l)[0,1], 4), round(f85[l==1].mean()-f85[l==0].mean(), 4))
EOF
```

**Design.** A detector x generator panel, run zero-shot on pools already on disk plus E1's
pools when they exist. For every (detector, pool) pair, realized sensitivity at sp = 0.99 and
0.85 with the threshold set on human scores exactly as in section 4.2; for every detector,
r_F measured directly as corr(detector score, trait) on the human essays, and the trait
composition of the flagged set at both operating points.

**Conditions.**

- Detectors (4 to 6): the current RoBERTa (anchor); a supervised classifier trained on a
  2024-2026 multi-generator benchmark; two zero-shot statistics (a perplexity-curvature method
  and a cross-model-perplexity method, both open source); one commercial API if budget allows,
  scored once and cached. Named candidates and what each is known to do on GPT-4-class text
  are in `LIT-SCAN.md`.
- Pools: PersonaLLM gpt-4-0613 and llama-2 (on disk), Big5PersonalityEssays GPT-4-turbo (on
  disk; sensitivity 0.0075 at the fixed HC3 threshold in `PASS3-FIXES.md` T7d), E1's six pools.
- Humans: the 2,467 PK essays, scored by every detector.

**Measures.**

1. The (se at sp = 0.99, se at sp = 0.85) pair per (detector, pool). This is Table 1
   re-populated. The pre-stated prediction from the detection literature is that a 2026
   supervised detector recovers most of the sensitivity lost on GPT-4-class text, and that
   zero-shot methods recover some of it at a cost in specificity on the essays domain.
2. r_F per detector, as above, with a 95% interval.
3. Table 11 recomputed at each detector's measured r_F. If any detector shows |r_F| above 0.2,
   the deletion-selection channel stops being negligible for that detector and section 5.6
   gains a second row.
4. For the two best detectors, the Layer B degraded and calibrated columns re-run (72 cells
   each) so the boundary map has a modern-detector row.

**Power sketch.** Sensitivity at se near 0.27 to a half-width of 0.05 needs about 300 machine
texts, which the 320-text pools provide. r_F on 2,467 humans has a half-width of about 0.04,
so the panel can distinguish r_F = 0.2 from 0 for every detector but cannot distinguish 0.05
from 0; that is acceptable because Table 11 says nothing under 0.1 matters. Continuous BFI
scores (E4) are what would tighten this, not more essays.

**Threats to validity.**

- Domain: the essays are stream-of-consciousness student writing from 1999; zero-shot
  detectors that rely on a scoring model's perplexity may flag archaic or informal human text
  at higher rates, which would inflate r_F for those detectors in a way that is real for
  this corpus and not general. Report the human false-positive set's characteristics.
- Zero-shot detectors depend on the choice of scoring model; fix one and report it.
- Commercial detectors change without notice; cache scores with a date and version string and
  do not re-query.
- The pools are 2023 text. Without E1, the panel says how modern detectors do on old machine
  text, which is the less interesting direction of transfer.

---

## E4. Live respondent experiment with randomized AI assistance

**Why.** Everything the paper says about real respondents is inferred from rematched 2023
persona essays and a synthetic outcome (INJECT.md 7a, restated in section 7). Nothing on disk
has a real respondent choosing to use a model, a real coupling produced by that choice, a
continuous trait score, or a real outcome. One modest experiment supplies all four, and it is
the only follow-up that turns "we model the mixture" into "we observed the mixture."

**Design.** Online panel (Prolific), pre-registered, three arms randomized between subjects.
Every participant completes a continuous Big Five inventory (BFI-2, 60 items), three
open-ended prompts of the kind the paper models (one is the Pennebaker-King
stream-of-consciousness instruction, so the corpus on disk stays the human anchor), and a
short criterion battery for a real outcome (self-reported behaviours with known Big Five
correlates, for example social activity frequency for EXT and a brief affect measure for NEU).

- Arm A, no assistance: standard instruction, paste disabled, typing telemetry recorded.
- Arm B, assistance permitted: participants are told they may use any tool including AI
  assistants; paste events and inter-keystroke timing recorded; a post-survey self-report of
  AI use with an incentive-compatible framing (no penalty, bonus unaffected).
- Arm C, assistance required: participants are instructed to paste the prompt into a named
  assistant and submit what it returns, optionally edited; the assistant's raw output is
  captured separately from the submitted text.

**Conditions.** n = 400 per arm, 1,200 total. Arm B is the estimate of pi and its selection
into who uses AI; arm C is the pool measurement with a real respondent behind each machine
text; arm A is the human process at the same instrument.

**Measures.**

1. pi in arm B, three ways: self-report, paste telemetry, detector. Agreement among the three
   is itself a result the survey-fraud literature lacks (see `LIT-SCAN.md`, prevalence
   section).
2. c, directly: in arm C, corr(scored submitted text, BFI-2 trait) against corr(scored arm A
   text, BFI-2 trait). Because the outsourcing decision is randomized, this is the coupling a
   real outsourcing respondent produces, not a persona-conditioned proxy.
3. r_F, directly and continuously: corr(detector score, BFI-2 trait) in arm A, for each
   detector in E3's panel.
4. kappa and delta on the scored text, arm C versus arm A.
5. The outcome check: the naive correlation between scored text and the criterion battery in
   arm A alone, in arm A plus B pooled (the natural mixture), and in A plus C at a chosen pi.
   The (E7) prediction from the measured tuple is compared to the observed pooled coefficient.
   This is the paper's contamination map on one real outcome.
6. In arm B, who uses AI: regress use on BFI-2 scores and demographics. Nonzero coefficients
   mean the mixing is nonignorable in the sense of section 2.3, which the paper currently
   assumes away (d_theta = 0).

**Power sketch.** At alpha = 0.05 and power 0.80 for two independent correlations:
detecting c = 0.38 versus 0.19 needs about 370 per arm; c = 0.38 versus 0 needs about 100;
r_H = 0.135 versus 0 needs about 430 in arm A. For r_F, 400 humans give a half-width of about
0.10, and pooling arms A and B (about 700 humans, if pi in B is near a third) gives about 0.075,
so the experiment can rule out r_F above 0.2 but cannot pin 0.05. For pi in arm B, 400
participants give a half-width of about 0.045 at pi = 0.34. n = 400 per arm is the minimum
that makes every primary measure informative; 600 per arm would bring r_F's half-width to
about 0.06 and is the version to run if the budget allows.

**Threats to validity.**

- Arm C is compliance-dependent; participants who edit heavily produce mixed text, which is a
  legitimate part of the phenomenon but breaks the two-component model. Record the edit
  distance between assistant output and submission and analyze at two cutoffs.
- Telemetry as gold label: paste events miss retyped text and flag pasted human text. The
  three-way agreement measure is designed to expose this, not to hide it.
- Prolific participants are not opt-in panel respondents; prevalence generalizes to Prolific
  only. The coupling and r_F measurements generalize better because they are properties of
  the writing process, not of the panel.
- The criterion battery is self-report, so the outcome inherits common-method variance with
  the BFI-2. This inflates all three correlations in measure 5 equally and does not affect
  the comparison among them.
- Median-split labels are gone, so r_H, c, and r_F are no longer lower bounds. If continuous
  r_F comes in above 0.2, section 5.6's headline moves and Table 11 becomes the result rather
  than the sensitivity analysis.
- Ethics: arm C instructs participants to use an AI assistant; the consent form must say so,
  and the assistant's terms must permit it. IRB before pre-registration.

---

## E5. A survivor-sample bound, and what a small gold subsample buys

**Why.** `ESTIMATOR-FIX-REPORT.md` section 5 calls `bounds_c` the strongest single result in the
estimator track: structural width under 0.2 everywhere, honest coverage after the Imbens-Manski
fix, and the T-width bar met in 78% of n = 1000 cells. Two things limit it. It bounds rho_H from
the full undeleted sample, so it never uses the detector at all, and the sampling component of
its width (the part that fails the bar at n <= 1000) would shrink if the residual contamination
were smaller. And the paper assumes no labeled validation subsample exists, which is the one
assumption the prediction-powered-inference literature says is cheap to relax (see
`LIT-SCAN.md`, methods section). Part (a) is a derivation plus a grid column. Part (b) is a
simulation now and a real analysis once E4's labels exist.

**Part (a) design: the survivor-sample bound.** Extend the c-affine bound from (E36) to the
post-deletion sample using the selection terms (E30 to E34): after deletion at a known (se, sp),
the survivor sample is a mixture with residual fraction pi_res = pi(1 - se) / (pi(1 - se) +
(1 - pi) sp), and the survivor's observed correlation is rho_H Att(pi_res, c) times the selection
factor q(r_F, sp). Invert at the endpoints of c in [0, 1] and r_F in [0, r_F_max] jointly, union
the Fisher-z sampling interval as `fit_bounds_c` already does, and register the result as
`bounds_surv`. Run it as a single-column re-run on the 372 Layer A cells with
`run_grid_column.py` (the report puts a `bounds_c` column at about 34 seconds).

**Part (a) measures.** Width and coverage by detector level and n, in the report's table shape.
Predictions: at the calibrated point (se = 0.95, sp = 0.99 in Layer A) pi_res is under 0.01 at
every pi in the grid, so the identification component collapses toward zero and the width is
almost entirely sampling; at the degraded point the r_F uncertainty adds width proportional to
r_F_max^2. The interesting comparison is `bounds_surv` at r_F_max = 0.1 (the paper's measured
range) against `bounds_c`: if the survivor bound is narrower at n = 1000 in most cells, the
paper gains a constructive recommendation ("delete, then bound") to put beside "report naive
with the map."

**Part (b) design: the gold-subsample arm.** Simulate, in Layer A first and Layer B second, a
design in which m of the n responses carry a known authorship label (m in {0, 50, 100, 200,
300, 500}). Three uses of the labels, each a separate estimator column:

1. pi_hat from the labeled subsample (binomial), plugged into `bounds_c` in place of the known
   pi, so the estimator no longer assumes pi is a known structural parameter.
2. c_hat from the labeled machine texts (corr of scored text with theta among labeled machine
   responses), replacing the [0, 1] prior interval with a data interval, which is what
   `h5_bounds.py` did with c_pool = 0.379 on Layer B.
3. A prediction-powered point estimate: the detector's flag as the prediction, the m labels
   as the calibration set, rho_H estimated with the rectifier. This is the estimator the paper
   currently lacks and the one the methods literature says is the right tool when a small
   gold set exists.

**Part (b) measures.** Width of the bound and RMSE of the PPI point estimate as a function of
m, against the boundary map's existing columns. The question the paper can then answer is: how
many labeled responses turn "nothing beats naive" into "a correction beats naive," at each
(pi, c, detector) cell.

**Power sketch.** A binomial pi_hat with half-width 0.05 needs m of about 140 at pi = 0.10 and
250 at pi = 0.20; half-width 0.02 needs 860 and 1,540, which is most of the sample and not a
"small" subsample, so the realistic regime is m in 100 to 300 with pi pinned to about 0.05.
c_hat from labeled machine texts has half-width about 1.96/sqrt(m pi), which at m = 300, pi =
0.20 (60 machine texts) is 0.25: too wide to replace the prior interval on its own but enough
to exclude c = 0 from c = 0.38 at the edge. This says the labels help the bound mainly
through pi, not through c, which is a testable prediction of part (b).

**Threats to validity.**

- Part (a)'s joint inversion over (c, r_F) assumes the selection factor q is separable from
  Att, which holds in the derivation at delta = 0 and d_theta = 0 (the Layer A regime) and
  is not established otherwise. State the regime; do not extend the bound to Layer B's
  delta > 0 pools without re-deriving.
- Gold labels in practice come from self-report or telemetry, both noisy (E4, threats). A
  misclassified calibration set biases the rectifier; simulate label noise at 5% and 15% in
  part (b) as a robustness row.
- The prediction-powered estimator is designed for a mean or a regression coefficient with a
  prediction of the outcome; here the prediction is of the mixture membership, not of the
  score, so the mapping is not one-to-one. Write the estimator down before simulating it and
  check the unbiasedness argument on a Layer A cell where the answer is known.
- Adding estimator columns to a frozen grid: use `run_grid_column.py` so every other column's
  RNG stream is untouched, and record the run as a new results directory, never by editing
  `results/grid/grid.jsonl`.

---

## What this list does not include, and why

- A document-pooled EXT rerun: EXT's validity does not move under document pooling (T3), so
  the rerun would reproduce the current box. E2 picks the traits that move.
- More replications of the existing box: section 5.5 already did 5x and the failure sharpened.
  More reps resolve noise; they do not move the estimand.
- A third detector operating point between sp = 0.85 and 0.99: Prop. 14 says the bias is
  non-monotone in the threshold with an interior optimum, which is worth showing, but it
  is a one-figure addition inside E3, not a separate experiment.
- Non-ignorable authorship (d_theta != 0) in Layer A beyond the 9-cell arm: E4's measure 6
  is the empirical version, and without a measured d_theta the Layer A arm is algebra the
  paper already certifies.
