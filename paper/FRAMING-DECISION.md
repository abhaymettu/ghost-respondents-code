# Framing decision: nonignorable-missingness / IRT lineage (Day-8 radar item 2)

Sources read in full before this assessment: Rose, von Davier & Nagengast (2015), "Commonalities
and differences in IRT-based methods for nonignorable item nonresponses," Psychological Test and
Assessment Modeling 57(4), 472-498 (`https://www.psychologie-aktuell.com/fileadmin/download/ptam/4-2015_20151218/03_Rose.pdf`,
pages 1-15 read, PDF cached at `/tmp/rose_ptam.pdf`); and the Psychometrika 2026 Bayesian
IRT nonignorable-missing-data paper abstract/summary (fetched via
`https://www.cambridge.org/core/journals/psychometrika/article/bayesian-modeling-and-inference-for-item-response-model-with-nonignorable-missing-data/99A2DADDECC0C35A568E6A559D915299`).

## What the lineage actually says

Rose et al. formalize nonignorable item nonresponse in IRT under Rubin's (1976) taxonomy:
missingness is MCAR/MAR ("ignorable") when the response indicator D is independent of the
unobserved data given the observed data and covariates; it is NMAR ("nonignorable") when D
stays stochastically dependent on the latent trait even after conditioning on what's observed.
Two model classes handle the nonignorable case: selection models (SLM; Heckman 1976/1979),
which posit a latent response-propensity variable — in the univariate normal case, literally
a threshold on a normal variate correlated with the trait — and pattern-mixture models (PMM;
Little 1993/2008), which stratify by observed missingness pattern and let parameters vary by
pattern. Rose et al.'s own contribution is deriving multidimensional IRT (MIRT), latent
regression (LRM), and multiple-group (MG-IRT) models as computationally lighter alternatives
to full SLM/PMM, useful when the missingness is driven by omitted/not-reached test items. The
2026 Psychometrika paper extends this to a joint Bayesian model of item responses, response
times, and two missingness types (not-reached, omitted), again via shared latent propensity
parameters correlated with ability.

## Structural match to this paper

Section 2.3's detector model is, without the authors having named it as such, already a
univariate normal selection model in the Heckman/Rose sense: F = r_F * theta/sqrt(s2_T) +
sqrt(1 - r_F^2) * eta, pass iff F > tau. That is exactly the SLM machinery Rose et al. survey —
a latent response-propensity variable (here, detector-pass status) built from a threshold on a
normal variate correlated with the trait being measured. Framed this way: detect-and-delete is
complete-case analysis; the missingness mechanism is the classifier; and the classifier's
dependence on theta through r_F is precisely Rubin's NMAR condition (D not independent of the
unobserved variable given the observed data). The paper's own Prop. 11/14 results (range
restriction under the detector, non-monotone bias along a ROC curve) are things the IRT
nonignorable-nonresponse literature would recognize immediately and has vocabulary for.

## Verdict: lineage/citation layer, not a restructure

This does not change the paper's center of gravity. The paper's contribution — the closed-form
mixture-model bias derivation, the four-estimator simulation grid, and the boundary map — is
self-contained and does not depend on IRT machinery to exist or to be argued for; nothing in
Section 2 through 6 needs re-derivation in selection-model or pattern-mixture notation to hold.
The IRT lineage is formally adjacent (same missingness-mechanism class, same selection-model
structure) but substantively distant (their nonresponse is unanswered test items; this paper's
"nonresponse" is complete responses authored by the wrong process and then discarded by a noisy
classifier) — closer to a citation that supplies reviewer vocabulary and prior sensitivity-
analysis machinery than to a body of technique this paper reuses.

**Section-level impact if adopted (recommended, lightweight):**
- **Section 1.3 (Relation to prior work):** add one sentence naming the lineage and citing
  Rose et al. and the 2026 Psychometrika paper, positioning detect-and-delete as complete-case
  analysis under a classifier-driven nonignorable missingness mechanism.
- **Section 2.3:** one clause noting that the fluency-threshold model is formally a univariate
  normal selection model in the sense of Heckman/Rose, so the survivor-sample bias derived here
  is the same NMAR phenomenon the IRT nonresponse literature treats generally.
- **References:** add both citations.
- **No other section changes.** Sections 3-6 (estimators, simulation design, results,
  discussion, limitations) are untouched — the paper does not need pattern-mixture or
  selection-model estimators to make its argument, only the vocabulary for framing what it
  already derived.

Applied below (this pass): Section 1.3 and Section 2.3 additions and the two references, as
scoped above. No restructuring performed — that call belongs to the paper's owner, not this
pass.
