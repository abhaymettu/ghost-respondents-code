# Weak-H2 mechanism diagnosis: why `rbar/rel_true` still fails OOF

Response to the follow-on brief after `CHUNK-REFIT.md` (commit `5cab003`): fixing chunk-score
leakage changed `rbar/rel_true` per trait by amounts and directions that vary by trait (not a
uniform "at most 7%" — see `PASS3-FIXES.md` m1 for the corrected per-trait deltas) and left it at
**5.41x–41.67x** on PK-human — essentially the same failure `LAYERB-SWEEP2.md` reported at
6.2x–11.8x on its six-cell subset. This is a mechanism investigation, not a re-measurement: it
identifies *why*, with computed evidence, not restated numbers.

**Revision note (pass-3 review, 2026-09-09):** an adversarial NLP review found this file's
original §2.4 partial-correlation table did not reproduce — recomputing it correctly gives real,
nonzero reductions (4–10%), not the claimed 0.0%. §2.4, §2.5, §2.7 and the Verdict below have
been rewritten to the corrected numbers and a narrower claim. See `PASS3-FIXES.md` T1 for the
full withdrawal list. The over-claims withdrawn: "0.0% removed" / "100.0% survives" (every
trait), ">93% of rbar survives... in every trait", "quantitative confirmation", "not recoverable
on this testbed at any n or pi", and the "orthogonal to the very construct" framing.

All new numbers below computed directly from `data/scores/pk_human.json`'s `chunk_{1..4}_oof`,
`cross_fitted_scores`, and `labels` (n=2,467; n=2,421 for chunk-pair statistics, same as
`CHUNK-REFIT.md`), plus `data/essays/essays.csv` for word counts. Local CPU, niced, no new
model fitting — every computation here is a correlation, partial correlation, or variance ratio
on scores that already exist on disk. `lane4-simulation/results/` was not read for numbers
(read-only per constraint) beyond the already-published `LAYERB-SWEEP2.md`/`LAYERB-ROUND3.md`
text.

## 1. WHERE it fails

### 1.1 By trait (PK-human, OOF, from `CHUNK-REFIT.md`)

| trait | r_H (whole) | rel_true = r_H² | rbar OOF | rbar/rel_true OOF |
|---|---|---|---|---|
| cOPN | 0.2267 | 0.0514 | 0.2780 | **5.41x** |
| cEXT | 0.1596 | 0.0255 | 0.2068 | **8.11x** |
| cAGR | 0.1060 | 0.0112 | 0.1759 | **15.66x** |
| cNEU | 0.1023 | 0.0105 | 0.2131 | **20.37x** |
| cCON | 0.0694 | 0.0048 | 0.2005 | **41.67x** |

Sorted by ratio. The ordering tracks `r_H` almost exactly (Spearman rho = −1.0, worst trait
has smallest r_H) while `rbar` itself is confined to a narrow band, 0.176–0.278, a 1.6x span
against r_H's 3.3x span (0.069–0.227) and rel_true's ~11x span (0.0048–0.0514). **The ratio's
range is being driven almost entirely by variation in the denominator (rel_true), not by
variation in the numerator (rbar).** This is the first structural fact and it reappears in
§2.3 as the leading mechanism.

### 1.2 By chunk pair (all 6 pairs of {1,2,3,4}, mean over 5 traits, OOF)

| pair | mean r | vs adjacent-only mean | vs non-adjacent-only mean |
|---|---|---|---|
| (1,2) adjacent | 0.2071 | | |
| (2,3) adjacent | 0.2073 | | |
| (3,4) adjacent | 0.2135 | | |
| (1,3) non-adj | 0.2087 | | |
| (1,4) non-adj | 0.2027 | | |
| (2,4) non-adj | 0.2074 | | |
| **adjacent mean** | | **0.2093** | |
| **non-adjacent mean** | | | **0.2063** |

No decay with distance (adjacent 0.2093 vs non-adjacent 0.2063, a 1.5% gap — noise at this n).
A topic-drift mechanism (chunk 1 and chunk 4 talk about different sub-topics within the essay,
so distant chunks should correlate less) predicts decay with distance. It is absent. Whatever
drives rbar is **global to the text**, not local to chunk adjacency — consistent with a single
per-document nuisance factor shared identically by all four chunks, not a slowly-drifting one.

### 1.3 By anchor / n

Not applicable in the form the brief anticipated: this ratio is computed entirely within
PK-human (no machine pool, no injected label, no prevalence estimate, no anchor choice) — it is
the human-only within-text consistency baseline (design-pivot-memo Q14), consumed by lane4's
multi-item correction downstream. There is no "anchor" or "n" free parameter at this stage; `n`
is fixed at 2,421 (the split-into-4 PK subset), reused unchanged from `CHUNK-REFIT.md`. Where an
anchor/n decomposition *is* meaningful — the six non-PK cells lane4 measured — those ratios
(1.84x–6.61x, `CHUNK-REFIT.md` §"Non-PK pools") are smaller than PK's own 5.41x–41.67x. That is
a genuine, somewhat counterintuitive finding in its own right and is used as evidence in §2.4.

## 2. WHY

Five candidate mechanisms, each tested with a number computed this pass, not argued from priors.

### 2.1 Split dependence — ruled out by construction

`rbar` and `rel_true` are both computed from PK's single deterministic 5-fold
`KFold(random_state=20260907)` assignment, reproduced to `max|old−new| = 0.0` in
`CHUNK-REFIT.md`. There is no split re-draw anywhere in this computation — unlike lane4's
calibration-split pipeline (`LAYERB-ROUND3.md` §2, which found 54% of *its* variance was the
split draw), this quantity has exactly one split, fixed by seed, and both numerator and
denominator are computed from the same fold assignment. Split variance cannot be the mechanism
here; it isn't a live variable. (Lane4's frozen-split finding is real and important for the
EIV/adjusted-count pipeline, but that pipeline is downstream of and separate from this ratio.)

### 2.2 Chunk-score compression — ruled out

If chunk scores were compressed toward the mean (less signal, narrower range) relative to
whole-text scores, that would inflate correlation among chunks through restricted range while
also weakening chunk-vs-label correlation. Measured variance ratio (chunk-1 / whole-text),
all 5 traits:

| trait | var(whole) | var(chunk 1) | ratio |
|---|---|---|---|
| cEXT | 0.10123 | 0.11664 | 1.152 |
| cNEU | 0.10076 | 0.11364 | 1.128 |
| cAGR | 0.09877 | 0.11211 | 1.135 |
| cCON | 0.08791 | 0.09850 | 1.120 |
| cOPN | 0.14249 | 0.15328 | 1.076 |

Chunk-1 variance is **higher** than whole-text variance in all 5 traits (1.08x–1.15x), the
opposite of compression. Ruled out.

### 2.3 Cross-trait / embedding-space contamination amplified by chunking — ruled out

If splitting into chunks amplified the known cross-trait leakage in the 5 ridge models (all
fit on the same `all-MiniLM-L6-v2` embedding space, so not fully independent axes), the
off-diagonal correlation among the 5 trait scores should be *larger* at chunk level than at
whole-text level. Mean |off-diagonal| of the 5×5 cross-trait correlation matrix:

| basis | mean \|off-diag\| cross-trait r |
|---|---|
| whole-text cross-fitted scores | 0.1518 |
| chunk-1 OOF scores | 0.1417 |

Chunk-1 cross-trait leakage is *slightly lower*, not higher, than whole-text. Cross-trait
contamination exists (it is not the same-trait signal weak-H2 needs, and it is a real caveat
for the pipeline generally — cOPN's known sign anomaly in `POOL-MEASUREMENTS.md` is part of
this same phenomenon), but chunking does not amplify it. Ruled out as the driver of the
in-sample→OOF-persistent rbar inflation specifically.

### 2.4 Trait signal (label) as the driver of rbar — corrected 2026-09-09 (pass-3 review)

**The table originally here was wrong.** The residualization used a constant/misdecoded control
and produced 0.0% reduction in every trait; recomputing with `analysis/pass3_nlp_checks.py`
(closed-form partial correlation, cross-checked against direct residualization to 1e-12) gives
real, nonzero reductions. Complete-case n=2,421 (same subset as §1.1), numeric 0/1 label,
verified label variance > 0 and row alignment before computing:

| trait | raw rbar | partial rbar (control: label) | relative reduction |
|---|---|---|---|
| cEXT | 0.20678 | 0.19819 | **4.15%** |
| cNEU | 0.21310 | 0.20544 | **3.59%** |
| cAGR | 0.17586 | 0.17098 | **2.77%** |
| cCON | 0.20053 | 0.19743 | **1.54%** |
| cOPN | 0.27800 | 0.25128 | **9.61%** |

Controlling for the trait label removes a small but real and consistently positive share of
rbar in every trait (1.5%–9.6%, largest for cOPN). This rules out the "0.0%, fully orthogonal"
reading, but the corrected numbers still show that **most (90–98%) of rbar survives label
control** — the label explains only a minority of between-chunk agreement. That the surviving
majority is unexplained is real evidence that something beyond the trait drives rbar; it is not
evidence that the trait contributes *nothing*, and it does not establish that the remainder is
"orthogonal to the construct" — a binary median-split label leaves real within-band variation in
the continuous trait that no linear control on the binary label can remove (see caveat below).

(Caveat stated plainly: the label is a *binary median split*, not the continuous trait — see
`GEN-CONFIG.md`'s c-high blocker for the same underlying data limitation. Even a perfect binary
control cannot remove all shared continuous-trait signal, so the reductions above are a lower
bound on how much of rbar the true continuous trait would explain, not an upper bound. This is
not testable on this corpus — the continuous BFI scores are behind IEEE DataPort's login gate,
unfetched. Flagging as an open uncertainty, not closing it.)

### 2.5 Essay length as the driver of rbar — corrected 2026-09-09 (pass-3 review)

Word count is an obvious candidate nuisance shared by all chunks of the same essay (verbosity
correlates with itself across any split of the same document). Controlling for length alone,
and length + label together (recomputed with the corrected label-partial method above), same
6-pair/5-trait average, n=2,421:

| trait | raw rbar | partial (control: length) | partial (control: length + label) | % of raw surviving (length+label) |
|---|---|---|---|---|
| cEXT | 0.20678 | 0.19381 | 0.18503 | 89.5% |
| cNEU | 0.21310 | 0.20481 | 0.19765 | 92.8% |
| cAGR | 0.17586 | 0.17540 | 0.17050 | 97.0% |
| cCON | 0.20053 | 0.19736 | 0.19406 | 96.8% |
| cOPN | 0.27800 | 0.27401 | 0.24784 | 89.2% |

Length alone explains little (0.3%–6.3% of rbar), and length + label together leaves
**89.2%–97.0%** of raw rbar standing (not ">93% in every trait" — cEXT and cOPN both drop below
93%). Most residual chunk-pair agreement remains unexplained by either of the two most obvious
candidate nuisances.

### 2.6 Anchor/off-manifold mechanism — inapplicable to this number, and contradicted by the pattern

"Machine reference off-manifold" as a mechanism would predict PK-human's *own* within-corpus
ratio should be *better behaved* than the machine pools' ratios (PK-human has no manifold-shift
problem — it's the reference itself). The opposite holds: PK-human's ratio (5.41x–41.67x) is
larger than every one of the six non-PK cells `CHUNK-REFIT.md` measured (1.84x–6.61x). Whatever
drives the PK-human ratio is not a machine-text artifact; it is present, and worse, in pure
human text. This mechanism is not the explanation for PK-human's own number (it may still be a
real, additional effect for machine pools specifically — out of scope to isolate here since the
non-PK numbers were not decomposed the way PK-human's were in this pass).

### 2.7 What remains — narrowed 2026-09-09 (pass-3 review)

Ruled out by construction or direct measurement: split dependence (2.1), score compression
(2.2), chunking-amplified cross-trait leakage (2.3). Partially explained but mostly unresolved:
trait-label-mediated signal (2.4, corrected — label explains 1.5%–9.6% of rbar, not 0%) and
essay length (2.5, corrected — length+label together explain 3.0%–10.8%, leaving 89.2%–97.0%
of rbar standing). Not applicable / doesn't fit the pattern: machine-reference off-manifold
(2.6).

What survives, stated at the strength the evidence supports: **most between-chunk agreement is
not explained by the (binary) trait label or essay length**, and it is global to the document
rather than adjacency-decaying (§1.2). A document-level stylistic/topical consistency factor —
word choice, register, syntax, topic shared by all four chunks of one essay — is the leading
candidate mechanism, consistent with `LAYERB-SWEEP2.md` FAIL 2's hypothesis. But this pass does
**not** establish that mechanism by elimination the way the original draft claimed: (a) a
binary median-split label cannot fully remove continuous-trait signal even if the trait *is* the
true driver, so the residual majority is also consistent with "the binary label is too coarse a
control," not only "the true driver is non-trait"; (b) no positive test of the stylistic/topical
hypothesis was run this pass (e.g. residualizing on an embedding-derived style/topic factor) —
it remains the leading candidate on elimination-plus-plausibility grounds, not a demonstrated
cause. Topic, syntax, register, and word choice can themselves be legitimate personality
indicators; declaring them "not the trait" is an assumption this pass has not tested, not a
finding it established.

## 3. WHAT WOULD FIX IT

Ranked by how much of the failure the evidence above says each would close, with cost.

### Option A — bypass `rbar`, correct with the known `r_H` directly (validates the pipeline, not deployable)

`LAYERB-SWEEP2.md` Part III already ran this as the oracle control: dividing `rho_H` by the
*true* `sqrt(rel_H) = r_H` recovers `rho_T = 0.5` within 1.71 MCSE, worst cell. That is because
`rel_H = r_H²` is the correct quantity by definition (§"What rel_H's truth value is at k=4" in
`LAYERB-SWEEP2.md`); the failure was never in the disattenuation algebra, only in what estimated
`rel_H`. **This closes 100% of the gap, at zero additional engineering cost — the code path
already exists.** The reason it isn't "the fix": `r_H` requires PK's gold trait labels to
compute, which exist only because this is a testbed built for validation. A real ghost-respondent
survey has no gold Big-Five labels for its live respondents (that is the entire reason a
label-free reliability estimator like weak-H2 was wanted). Value: confirms the correction
machinery is sound (already known) and gives a ceiling for how well any label-free estimator
could hope to do; not a deployable fix.

### Option B — purge the document-level nuisance before computing rbar

Given §2.7's diagnosis, this would mean finding and residualizing the actual style/topic
factor (not label, not length — both tested and largely ruled out in §2.4/2.5) before computing
between-chunk correlation. **Evidence against this being cheap:** the two most standard,
cheapest candidate nuisances (label, length) explain essentially none of it; whatever the real
factor is, it is not something already sitting in the metadata used here. It would likely
require an unsupervised topic/style embedding (e.g., a low-rank projection of chunk embeddings
orthogonal to the trait directions) built and validated as a genuinely trait-orthogonal-but-
document-shared factor — nontrivial development, and the expected payoff is **unproven, not
just uncosted**: nothing computed in this pass shows how much of rbar such a factor would
actually remove, only that label and length don't. Rank: worth a bounded follow-up experiment
(residualize against, e.g., the first few PCs of the chunk embedding space, then recompute
rbar/rel_true), but not to be assumed as a fix in advance of that experiment.

### Option C — redesign the chunking to produce true parallel forms

The CTT assumption weak-H2 needs is that "items" (chunks) share only the trait's true-score
variance plus independent noise. Splitting one document into four contiguous pieces guarantees
violation of that assumption (§2.7) — the pieces are not independent occasions of measurement,
they are one occasion cut into four. A genuine fix would use multiple *independent* short texts
per person (different prompts, different sittings) as the "items," which is the actual
psychometric definition of a parallel form. **PK-essays does not have this** — one essay per
person. This fix requires a different or additional corpus; not available within this testbed.
Rank: correct in principle, out of reach here.

### Verdict — narrowed 2026-09-09 (pass-3 review)

**The original verdict overclaimed and is withdrawn as stated.** "Not recoverable on this
testbed at any n or pi", "structural property... not by any fixable measurement error", and
"falsifies the assumption directly" all rested on the 0.0%-removed result, which does not
reproduce (§2.4). What the corrected evidence actually supports:

**Weak-H2, as measured by this specific scoring/correction setup on this corpus, fails**: the
OOF-corrected `rbar/rel_true` ratio is 5.41x–41.67x, far from the ~1x weak-H2 needs, and this is
not attributable to a leakage bug (fixed in `CHUNK-REFIT.md`), a split artifact (§2.1, ruled out
by construction), score compression (§2.2, ruled out), amplified cross-trait bleed (§2.3, ruled
out), or straightforwardly to the trait label or essay length, which together explain only
3–11% of rbar (§2.4–2.5, corrected). That leaves most of the between-chunk agreement
unattributed to a tested cause — consistent with, but not proof of, a document-level
style/topic factor (§2.7).

This is **a narrower result than originally claimed**: it establishes that the current
scoring/correction setup does not recover `rel_H` from chunk correlations on this corpus, at
this n. It does **not** establish that no scoring setup, corpus, or `pi` could ever make
weak-H2 work, and it does **not** establish that the residual chunk agreement is "orthogonal to
the construct" — a binary median-split label is too coarse a control to rule that out (§2.4
caveat), and the leading style/topic hypothesis (§2.7) has not been positively tested here.

**For the paper's H2 claim:** report weak-H2 as **not established via the label-free
multi-item route on this testbed**, under this scoring/correction pipeline — a scoring- and
corpus-conditional failure, not a proof of structural impossibility. The single-item route
(`r_H`) remains the validated path (oracle-checked at 1.71 MCSE), contingent on gold labels for
calibration, which real survey data does not have — that gap is the honest finding, independent
of how strongly the multi-item route's failure is characterized.

## Provenance

All correlation, partial-correlation, and variance numbers in §1–2 computed fresh this pass
from `data/scores/pk_human.json` (`chunk_{1..4}_oof`, `cross_fitted_scores`, `labels`) and
`data/essays/essays.csv` (word counts, latin-1 encoded). §3 Option A's oracle-recovery numbers
(1.71 MCSE) are cited from `LAYERB-SWEEP2.md` Part III, not recomputed here (that would mean
re-running lane4's simulation grid, out of scope and against the read-only constraint on
`lane4-simulation/results/`). No number in this file is invented or estimated; anything not
computed is explicitly marked as not computed (§2.4's continuous-label caveat, §2.6's
machine-pool decomposition).

WH2-DONE
