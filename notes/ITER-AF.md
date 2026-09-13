# Iteration A-F: receipts

Rounds A through F of `notes/PUBLISH-BAR.md` section 4, run 2026-09-13 on
`paper/GHOST-RESPONDENTS-DRAFT.md` at 01321cd. G and H (the E3 detector panel and the E2
document-pooled box) were not started; they are a later lane. Nothing was published.

Gate results, both re-run on the finished draft: `check_numbers.py` clean against baseline
(below), estimator unit tests 39/39, voice gate PASS (`paper/VOICE-GATE.md`).

---

## A. The bound becomes a conditional sensitivity band; "pre-registered" goes; G5 scoping

Closes G1, G2, G5.

**The band.** Four sites rewritten so the construction reads as what `fit_bounds_c` does:
takes pi, kappa, delta and rel_H as known, brackets c alone in [0, 1], and unions a Fisher-z
interval.

| site | was | is |
|---|---|---|
| Abstract para 4 | "The partial-identification bound meets its target." | "What is left is a conditional sensitivity band", with the four conditioning inputs named, coverage attributed to the construction, and the width ratio against the naive interval |
| 1.2 item 4 | "meets its pre-registered target ... Given pi is a real condition" | conditioning stated first; coverage "follows from the construction rather than from the data"; four inputs named |
| 1.2 closer | "The fourth is the constructive half of the paper." | cut |
| 5.4 bullet | "meets its target once sampling uncertainty is included" | "its coverage is a property of the construction rather than a result", with the argument for why (true c inside [0,1] by definition, Att monotone, four inputs supplied) |
| 6.2 | "report a bound instead ... It does need pi" | "report a sensitivity band around it", with the four assumed inputs and the sweep-and-union the field use requires |

New evidence for the framing, computed this round and added to `numbers.json`: the band is
wider than the naive Fisher interval in 372 of 372 cells, median ratio 1.28, narrower in none
(`bc_width_ratio_median`, `bc_wider_than_naive`; asserted in `make_tables.py`). This is the
number that makes "the naive interval widened by the identification range of c" a measurement
rather than an assertion. `make_tables.py` now reads `results/grid-bounds-c/` directly, so the
93.6 / 97.4 / 0.1405 / 178-of-228 / 0.0749 figures are generated rather than transcribed from
`ESTIMATOR-FIX-REPORT.md`.

**Pre-registration.** Seven uses removed. 4.3 now carries one sentence saying what SPEC.md
actually is: a repository file frozen at db7c171, not registered with OSF or AsPredicted,
amended after the grids ran to add `bounds_c`, and "fixed in the analysis plan" means exactly
that. Every other site reads "the analysis plan" or "the analysis-plan thresholds". The
appendix row for SPEC.md no longer calls it a registered supplement.

**G5 scoping.** Section 6 opens with the operating point the recommendations hold at
(rho_H near 0.068, frontier sensitivity under a third at 99% specificity, pi <= 0.30), says
the testbed is a GPT-2-era detector on 2023-era text against a field running 2026 detectors on
questionnaire-length answers, singles out recommendation 3, and says what carries over where
the operating point does not match: the algebra of section 2 and the method of 5.4, not these
numbers. One paragraph scopes all eight recommendations, which is cleaner than eight appended
clauses. The 1.2 item 2 sentence ("That single number does more to explain the correction
results than any property of any estimator") is cut; item 2 is now the measurement alone.

## B. Hygiene

Closes G6.

- **Internal-memo citations.** All three gone: "(lane 2 positioning memo, claim (c))" in 1.1,
  "The novelty gate (lane 2 positioning memo) checked three claims" in 1.3, "(lane 2 pivot
  positioning)" in 1.3. The claims they carried stayed; only the pointer a reader cannot open
  was removed.
- **Missing joint-scoring reference: cut, not added.** "The Psychometrika joint-IRT model for
  manual and automatic scores" had no reference entry and no verified citation on file. Adding
  one would have meant inventing it, so the sentence went, along with the trailing clause that
  distinguished it from Wu, Ma, and Chen (2026). That 2026 paper is now named in the text
  instead of appearing as "a 2026 Psychometrika paper".
- **Two orphaned reference entries fixed.** Both were uncited before this round. Huang et al.
  (2025) is now cited in 1.1 at the depth its entry supports (NORC's AAPOR presentation on
  detection tooling and bias mitigation). Zhang and Tong (2024) was `unverified`, sourced only
  to an internal radar log, and cited nowhere; it is cut.
- **Muse opener.** Seven lines of product description reduced to one sentence: persistent
  cross-service agents that act on a person's behalf are now a consumer product, sitting
  between that person and every service they touch (Meta, 2026-09-08). The paragraph that
  follows, which is the actual argument, is untouched.
- **"Two/Third" scope list.** 5.4 said "Two scope statements. First ... Second ... Third".
  Now "Three scope statements", reordered so the conditioning on four known inputs is first,
  since it is the one that decides how the band can be used.
- **Generative-AI-use statement.** Added to the Reproducibility appendix, ahead of the
  verification record: models derived the closed forms, wrote the code, ran the grids, and
  drafted the manuscript; the verification passes are themselves model-run and pass 1 is
  deliberately a different model family; every number is generated and checked by script; the
  author is responsible for the content. Factual, sourced to SPEC sections 6 and 7, no
  apology. A short version is in the root README.

## C. Direct detector-score r_F

Closes G4.

New script `lane3-testbed/analysis/detector_r_f.py`, writing
`analysis/detector_r_f_results.json`. It reads `detector_p_machine` from
`data/scores/pk_human.json` (roberta-base-openai-detector's P(machine) for all 2467
Pennebaker-King essays) and computes point-biserial and Spearman correlations against the five
binary labels.

| trait | point-biserial r | p | Spearman |
|---|---|---|---|
| cEXT | -0.0139 | 0.491 | +0.0149 |
| cNEU | +0.0199 | 0.324 | +0.0039 |
| cAGR | +0.0271 | 0.179 | +0.0241 |
| cCON | +0.0450 | 0.025 | +0.0702 |
| cOPN | -0.0127 | 0.527 | -0.0272 |

Anchor: |r_F| <= 0.045, only CON reaching p < 0.05 on 2467 essays, Spearman no larger than
0.070. This reproduces the values PUBLISH-BAR G4 quoted.

5.6 was rewritten to lead with this. The paragraph order is now: what the derivation needs,
the direct measurement, then the surface-proxy composite (0.053 on NEU) as secondary, then the
0.161 result explicitly - `avg_word_len` against cOPN, three times the composite, excluded
from it because it enters only through type-token ratio and is a lexical-complexity signal
rather than a fluency one, and covered by Table 11's r_F = 0.30 column. Both measurements are
stated as lower bounds against continuous BFI scores.

Table 11's last column is retitled from "(measured)" to "(surface proxy)" and its caption now
names the direct anchor, says the 0.045 value sits inside the r_F = 0.05 column, and says
which file each value comes from. The table body is unchanged: the proxy value is the larger
of the two, so the column as printed is the conservative one. Downstream sentences in 5.6 that
said "the measured r_F" now say "either measured value", and the section closes on both
numbers rather than on 0.053 alone. The abstract's r_F sentence now names the detector score
as the variable r_F is about.

## D. Boundary map becomes a resolvability map

Closes G3.

Table 7 and Figure 2 now report the naive relative bias per cell with its relative MCSE in
parentheses, bold where |bias| > 2 MCSE, shaded by |bias| / MCSE. No estimator is named per
cell. `make_tables.py` and `make_figures.py` both rewritten; the table note and the figure
caption say why the old statistic was dropped (a minimum over five near-zero noisy quantities
is biased toward zero and its argmin is not identified at a 4.6% relative MCSE).

Computed, not assumed:

- 33 of 72 cells have a resolvable naive bias; 39 do not.
- 8 cells exceed 0.30 relative bias, and they are exactly the 8 at p = 1 with pi >= 0.20, one
  per detector level at each of the two prevalences. `make_tables.py` asserts this set
  equality rather than leaving it as prose.
- Worst cell: p = 1, pi = 0.30, calibrated, at +0.597.

PUBLISH-BAR G3 predicted "the map has three resolvable cells". That was the count of cells
above 0.30 on the old best-of-five statistic, not the count of resolvable cells; the real
resolvability count is 33 of 72. The draft states the computed number.

The two 5.4 reading sentences were rewritten and the majority sentence dropped:

- The "method's limit" bullet now reads on resolvability: more than half the box has no
  visible contamination bias, the resolvable cells behave as (E39) requires (growing in pi,
  negative at p = 0, positive at p = 1), and the boundary is the eight-cell p = 1 corner.
- The "degraded detector" bullet was re-founded on the delete column, because the naive column
  cannot separate detector levels. Delete's bias is resolvable in 2 of 18 degraded cells
  (worst 0.172) against 6 of 18 calibrated (worst 0.472, essentially the undeleted value).
  The claim survived the change of evidence; it is now supported by the right quantity.
- "No cell is uniformly won by a correction ... no estimator wins a majority anywhere": cut,
  with the winner tally.

## E. Verification

| check | baseline | after |
|---|---|---|
| `check_numbers.py` pass 1 (keys appearing in the draft) | 427 of 430 | 448 of 452 |
| `check_numbers.py` pass 2 (unsourced numeric tokens) | 156 distinct | 135 distinct |
| new unsourced tokens introduced | - | none |
| `lane4-simulation/test_estimators.py` | 39/39 | 39/39 |
| voice gate | PASS (c5136ad) | PASS (`paper/VOICE-GATE.md`) |

The unsourced-token set was compared as a set, not a count: nothing in the new draft is
unsourced that was not unsourced before. Two tokens that were new mid-round were fixed rather
than whitelisted-by-default - `5000,` by rewording, and `171` (the `db7c171` commit fragment)
by one whitelist entry naming what it is. The four pass-1 misses are non-numeric values
(`None`, `False`, and two label strings).

Both gates were run on the finished draft, after the ponytail review fixes, not before.

## F. Repo prepared for release

Closes G9. Nothing published.

**Public tree is `git archive`.** `.gitattributes` marks as `export-ignore` everything the
paper does not cite: `prompts/`, `notes/`, `board/` and `board.md`, `.claude/`, `.remember/`,
all `*.log` and `*.pid`, `lane4-simulation/RADAR-DAY*.md`,
`lane4-simulation/ASTRA-REREVIEW-*.md`, `lane4-simulation/ZHANG-OCT1-DRAFT.md`, and
`lane4-simulation/results/layerb-grid-insample-partial/`. Nothing was deleted: the material
stays in the repository and in history, and the released tree is an export. This is a git
feature, not a script, and it is reversible by deleting a line.

Build and inspect the release tree before publishing anything:

```
git archive --format=tar --prefix=ghost-respondents/ HEAD | tar -x -C /tmp
```

**pyc.** 29 tracked `.pyc` files and one `.pid` untracked via `git rm --cached`; new
`.gitignore` covers `__pycache__/`, `*.pyc`, `.venv/`, `*.pid`.

**Root README.md.** New, and the deliverable G9 asks for: a paper-section-to-file table
covering sections 2 through 8, the repository layout, the regeneration commands, the data
provenance pointer, the release-tree instructions, and a short AI-use note. Every path it
names was checked to exist.

**Appendix consistency.** The "Excluded runs" paragraph said the in-sample partial grid is
"preserved and unused". Since that directory is now export-ignored, the sentence would have
been false in the released tree; it now says the run contributes no number and is kept in the
development repository, excluded from the release.

**Repo vs Zenodo, the decision F asks for:** public repo, with the Zenodo route still open.
The export-ignore mechanism makes the public tree a deterministic function of a tag, so a
Zenodo snapshot is `git archive` of that tag if he wants a DOI later. Nothing about this
choice is load-bearing for the paper, and it needs no rework to change.

---

## Ponytail review, applied before commit

Reviewed the diff of `make_tables.py`, `make_figures.py`, `check_numbers.py`,
`detector_r_f.py`, `.gitignore`, `.gitattributes`, `README.md`. Findings applied:

- `make_tables.py:41` `ABBR` unused once the winner labels went. Deleted.
- Eleven `numbers.json` keys no prose reads: `lb_bm_rel_mcse_min` / `_max`,
  `lb_bm_over_0.30_detectors`, `lb_bm_naive_resolvable_*` (4), `lb_bm_cells_*` (4),
  `bc_narrower_than_naive`, `rF_detector_spearman_max_trait`, `rF_proxy_max_feature` /
  `_trait`. Deleted. Three of them were carrying claims that an `assert` states better, so the
  claims moved into asserts: the eight-cell set equality, "narrower in none", and "the largest
  proxy is avg_word_len against cOPN".
- `detector_r_f.py` `detector_score_mean`, read by nothing. Deleted.

Key count went 467 to 452 with no loss of sourcing: the unsourced-token set is unchanged.

## Not done, deliberately

- **G7 and G8 (rounds G and H).** Out of scope for this lane by instruction. The draft still
  says, in Limitations and in section 6, that the document-pooled Layer B run and a modern
  detector panel are the two things that would change the evidence class.
- **G10.** His, not the paper's.
- **Affiliation and acknowledgements** stay BLOCKED-OWNER in the front matter and in Open
  items. Not mine to fill in.
- **Nothing published.** No preprint server, no Zenodo, no push.
