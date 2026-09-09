# Weak-H2 mechanism diagnosis: why `rbar/rel_true` still fails OOF

Response to the follow-on brief after `CHUNK-REFIT.md` (commit `5cab003`): fixing chunk-score
leakage moved `rbar/rel_true` by at most 7% (44.46x→41.67x, cCON) and left it at **5.41x–41.67x**
on PK-human — essentially the same failure `LAYERB-SWEEP2.md` reported at 6.2x–11.8x on its
six-cell subset. This is a mechanism investigation, not a re-measurement: it identifies *why*,
with computed evidence, not restated numbers.

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

### 2.4 Trait signal (label) as the driver of rbar — ruled out, decisively

The core test: if two chunks of a text correlate *because* they both carry the (weak) trait
signal, partialling the trait label out of the chunk-pair correlation should shrink it toward
the residual measurement-noise correlation (near zero, since independent chunks under CTT
should only share the true-score component). Partial correlation of each chunk pair controlling
for the binary trait label, averaged over all 6 pairs, all 5 traits (OOF scores):

| trait | raw rbar | partial rbar (control: label) | % of raw surviving |
|---|---|---|---|
| cEXT | 0.2068 | 0.2068 | **100.0%** |
| cNEU | 0.2131 | 0.2131 | **100.0%** |
| cAGR | 0.1759 | 0.1759 | **100.0%** |
| cCON | 0.2005 | 0.2005 | **100.0%** |
| cOPN | 0.2780 | 0.2780 | **100.0%** |

Controlling for the trait label removes **0.0%** of rbar, in every trait, to 4 decimal places.
The between-chunk correlation is, empirically, orthogonal to the very construct it is being
used to estimate the reliability of. This is the single strongest piece of evidence in this
report: `rbar` cannot be a valid proxy for `rel_H` if it carries zero measurable relationship
to the label whose reliability `rel_H` is supposed to describe.

(Caveat stated plainly: the label is a *binary median split*, not the continuous trait — see
`GEN-CONFIG.md`'s c-high blocker for the same underlying data limitation. A continuous label
might absorb a nonzero share of rbar that the binary split cannot. This is not testable on this
corpus — the continuous BFI scores are behind IEEE DataPort's login gate, unfetched. Flagging
as an open uncertainty, not closing it.)

### 2.5 Essay length as the driver of rbar — mostly ruled out

Word count is an obvious candidate nuisance shared by all chunks of the same essay (verbosity
correlates with itself across any split of the same document). Controlling for length alone,
and length + label together, same 6-pair/5-trait average:

| trait | raw rbar | partial (control: length) | partial (control: length + label) |
|---|---|---|---|
| cEXT | 0.2068 | 0.1938 | 0.1938 |
| cNEU | 0.2131 | 0.2048 | 0.2048 |
| cAGR | 0.1759 | 0.1754 | 0.1754 |
| cCON | 0.2005 | 0.1974 | 0.1974 |
| cOPN | 0.2780 | 0.2740 | 0.2740 |

Length explains 1–6% of rbar (cEXT largest at 6.3%, cAGR smallest at 0.3%), and adding the
label on top of length changes nothing further (matches §2.4). **>93% of rbar survives
controlling for the two most obvious candidate nuisances (label, length) in every trait.**

### 2.6 Anchor/off-manifold mechanism — inapplicable to this number, and contradicted by the pattern

"Machine reference off-manifold" as a mechanism would predict PK-human's *own* within-corpus
ratio should be *better behaved* than the machine pools' ratios (PK-human has no manifold-shift
problem — it's the reference itself). The opposite holds: PK-human's ratio (5.41x–41.67x) is
larger than every one of the six non-PK cells `CHUNK-REFIT.md` measured (1.84x–6.61x). Whatever
drives the PK-human ratio is not a machine-text artifact; it is present, and worse, in pure
human text. This mechanism is not the explanation for PK-human's own number (it may still be a
real, additional effect for machine pools specifically — out of scope to isolate here since the
non-PK numbers were not decomposed the way PK-human's were in this pass).

### 2.7 What remains, by elimination

Ruled out: split dependence (2.1), score compression (2.2), chunking-amplified cross-trait
leakage (2.3), trait-label-mediated signal (2.4, 100% survives), essay length (2.5, >93%
survives on top of length). Not applicable / doesn't fit the pattern: machine-reference
off-manifold (2.6). What is left, unfalsified, and consistent with every test above (global to
the whole document per §1.2, present and *worse* in pure human text per §2.6, essentially
unrelated to label or length per §2.4/2.5): **a document-level stylistic/topical consistency
factor** — word choice, register, syntax, and topic that all four chunks of one essay share
simply because they are four pieces of the same essay written in one sitting by one person on
one prompt — picked up by the shared `all-MiniLM-L6-v2` embedding space that all five ridge
models are built on, and correlated across chunks for reasons that have nothing to do with any
of the five Big-Five traits. This is exactly `LAYERB-SWEEP2.md` FAIL 2's stated hypothesis
("Chunks of one text share topic, length, register and author idiom, none of which is the
trait"); this pass adds the quantitative confirmation (100% survival controlling for label,
>93% surviving length on top of that) and rules out the four alternative mechanisms that could
have explained the same symptom.

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

### Verdict

**Weak-H2, as specified (a label-free, within-document chunk-correlation estimate of `rel_H`),
is not recoverable on this testbed at any n or pi.** The failure is not a leakage bug (fixed in
`CHUNK-REFIT.md`, moved the ratio by ≤7%), not a split artifact (§2.1, ruled out by
construction), not score compression (§2.2, ruled out), not amplified cross-trait bleed (§2.3,
ruled out), and not explained by the trait signal itself (§2.4) or by essay length (§2.5) — it
is explained by the chunking scheme producing items that are not valid parallel forms of the
trait construct, a structural property of splitting one document into four pieces, present
*more* strongly in the pure-human reference corpus than in any machine pool (§2.6). Proof
sketch: if rbar's shared variance were the trait's true-score variance (weak-H2's load-bearing
assumption), removing the trait label from the chunk-pair correlation would remove that
variance; it removes 0.0% of it in all 5 traits (§2.4), which falsifies the assumption directly
rather than just showing the resulting ratio is large.

**For the paper's H2 claim:** this confirms and sharpens `LAYERB-SWEEP2.md`'s existing verdict
("between-chunk consistency does not identify `rel_H` on this corpus... not usable as
specified") — the OOF re-derivation removes the one open objection to that verdict (that it was
measured on leaky scores), and the mechanism work here removes four more plausible objections
(split draw, compression, cross-trait bleed, and "maybe it just needs the OOF fix"). What
remains standing is that weak-H2's own assumption — that within-document chunk correlation
approximates trait reliability — is false on this corpus, by construction of what a chunk is,
not by any fixable measurement error. The paper should report H2 as **not established via the
label-free multi-item route**, with the single-item route (`r_H`, which does hold up per the
oracle check) as the only validated path, contingent on having gold labels for calibration —
which is itself the paper's honest finding about what weak-H2 requires and does not deliver on
real (unlabeled) survey data.

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
