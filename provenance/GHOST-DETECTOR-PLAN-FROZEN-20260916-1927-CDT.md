# GHOST detector plan - frozen provenance copy

**Frozen:** 2026-09-16 19:27 CDT (America/Chicago)
**Provenance condition:** Frozen 2026-09-16 prior to reviewing ASURRE internals. This is a faithful capture of the GHOST detector plan already present in this repository today. It does not use arXiv:2609.17317 implementation details and contains no improvements prompted by that paper.

## Repository state at freeze

- Repository:   `ghost-respondents`
- Source HEAD before this provenance commit: `9eb4b7bb72c525b15ba181ab2d0458ab29de44a5`
- Source HEAD committer time: `2026-09-13T21:56:06-05:00`
- Primary plan source: `docs/FOLLOWUP-EXPERIMENTS.md`, blob `ee405ba8679318aecde7303672e2e51adae5e89c`, E3 "Detector transfer panel that measures the real collider"
- Existing direct-feature implementation: `lane3-testbed/analysis/detector_r_f.py`, blob `959acade048a1ed46bb6dc0dd6dfb860370171ea`
- Candidate literature inventory: `docs/LIT-SCAN.md`, blob `0ad62a3098379b81472ad1200af99f9683a1fa0d`
- Current paper context: `paper/GHOST-RESPONDENTS-DRAFT.md`, blob `b39fd068f8809bd2e3af6336dfed5d2b3fedd5c5`

The worktree had unrelated existing changes at freeze time. This provenance commit stages only this document; it does not absorb those changes.

## Detector suite as planned today

The planned panel contains four to six detectors:

1. **Current anchor:** `roberta-base-openai-detector`, already used in GHOST and scored on the Pennebaker-King human essays.
2. **Modern supervised detector:** a classifier trained on a 2024-2026 multi-generator benchmark.
3. **Zero-shot statistic A:** a perplexity-curvature method.
4. **Zero-shot statistic B:** a cross-model-perplexity method.
5. **Optional commercial detector:** one API if budget allows, scored once and cached with date and version because commercial systems change without notice.

The source plan intentionally leaves the exact modern supervised model, scoring model for each zero-shot method, and optional commercial service to be fixed later from `docs/LIT-SCAN.md`. They were not selected in the plan as of this freeze.

## Features and quantities as planned today

Per detector, the planned analysis uses:

- the detector's continuous machine-likelihood score, rather than only its binary decision;
- the score logit where appropriate, matching the existing direct `r_F` pilot;
- detector thresholds calibrated on the 2,467 human Pennebaker-King essays at specificity `sp = 0.99` and `sp = 0.85`;
- realized sensitivity on every machine-text pool at both specificity points;
- direct `r_F = corr(detector score, trait)` on human essays, with a 95% interval;
- point-biserial correlation against each binary median-split Big Five label, plus Spearman rho as a monotonicity check in the existing implementation;
- the Big Five trait composition of the human false-positive/flagged set at both operating points;
- the tuple `(se at sp=.99, se at sp=.85)` for each detector-pool pair;
- Table 11 recomputed using each detector's measured `r_F`;
- a decision boundary already stated in the plan: if any detector has `|r_F| > 0.2`, deletion selection is no longer treated as negligible for that detector;
- for the two best detectors, rerun the Layer B degraded and calibrated columns, 72 cells each.

Existing pilot quantities already recorded before this freeze are not new results: direct correlations between the current RoBERTa detector logit and binary labels were EXT -0.004, NEU +0.020, AGR +0.031, CON +0.064, and OPE -0.009. The plan treats these as a consistency check and a lower bound because median splits attenuate correlations relative to continuous BFI scores.

## Evaluation grid as planned today

### Detector axis

- 4-6 detectors: current RoBERTa anchor; one modern supervised multi-generator classifier; two zero-shot methods; optional commercial API.

### Machine-pool axis

Existing pools:

- PersonaLLM GPT-4-0613;
- PersonaLLM Llama-2;
- Big5PersonalityEssays GPT-4-turbo.

Planned future pools from E1, when they exist:

- two generator families crossed with three prompting levels: `c0`, `high`, and `polish`, six pools total.

### Human reference axis

- all 2,467 Pennebaker-King essays scored by every detector;
- thresholds set independently for each detector on these human scores at `sp=.99` and `sp=.85`.

### Outputs per cell and panel

For every detector x pool pair:

- sensitivity at `sp=.99`;
- sensitivity at `sp=.85`.

For every detector on human essays:

- direct `r_F` for each Big Five trait and its 95% interval;
- flagged-set trait composition at both operating points;
- false-positive-set characteristics, especially whether informal or older student prose is disproportionately flagged.

For the two best detectors:

- 72-cell degraded Layer B column;
- 72-cell calibrated Layer B column.

Power targets already in the plan:

- about 300 machine texts supports sensitivity near 0.27 with about 0.05 half-width; existing pools have 320 texts;
- 2,467 humans gives about 0.04 half-width for `r_F`, enough to distinguish 0.2 from zero but not 0.05 from zero.

## Pre-existing validity constraints

- Fix and report one scoring model for each zero-shot detector.
- Cache commercial scores once with a date and version string; do not re-query silently.
- Treat domain shift on 1999 stream-of-consciousness student essays as a measured corpus property, not something to hide.
- Without the future E1 pools, the transfer panel tests modern detectors on older machine text and must be described that way.
- The planned panel measures detector behavior; it does not alter GHOST's estimands or retrofit detector choices after seeing ASURRE.

## Freeze boundary

This document freezes only what the named repository sources say as of the timestamp above. Any later model choice, implementation, feature, benchmark condition, threshold, or analysis inspired by ASURRE or other later reading must be documented in a separate post-freeze change and must not be backdated into this file.
