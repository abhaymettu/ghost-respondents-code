# Re-gate after iteration A-F

Judged 2026-09-13 against `paper/GHOST-RESPONDENTS-DRAFT.md` at a1b0334 (the A-F commit is
c05af7a), reading `notes/PUBLISH-BAR.md` as the bar and `notes/ITER-AF.md` as the receipts.
Nothing in the repo was edited. Every receipt below was re-run or re-read in this session.

## Re-run receipts

| check | ITER-AF says | re-run here |
|---|---|---|
| `check_numbers.py` pass 1 | 448 of 452 | 448 of 452 |
| `check_numbers.py` pass 2 (unsourced tokens) | 135 distinct | 135 distinct |
| `test_estimators.py` | 39/39 | 39/39 (`python test_estimators.py`; the venv has no pytest) |
| voice-gate pattern set on the draft | zero hits | zero hits; em dashes zero |
| release tree (`git archive HEAD`) | pyc/log/pid excluded | 0 `.pyc`, `.log`, `.pid`; no RADAR/ASTRA/ZHANG-OCT1 files; no `layerb-grid-insample-partial`; `prompts/`, `notes/`, `.claude/` are empty directory entries with 0 files |
| tracked `.pyc` | 0 | 0 |

Voice gate confirmed: `paper/VOICE-GATE.md` is a PASS on the A-F draft, and the pattern grep
reproduces its zero-hit result.

## Gap by gap

**G1 (constructive half overclaimed): CLOSED.** The three quoted sentences are gone: grep
for "constructive half", "meets its target", "does need pi" returns nothing. The abstract now
reads "What is left is a conditional sensitivity band. Taking the prevalence, the
homogenization, the mean gap and the human reliability as known, treating only the coupling
as unidentified inside [0, 1] ... Coverage at that level is what the construction guarantees
... The band is what a sensitivity analysis reports, not a field-usable bound." 1.2 item 4:
"Coverage at that level follows from the construction rather than from the data ... Its four
conditioning inputs are what a field application would have to supply, and pi is not
estimable here." 5.4: "Coverage at that level is not evidence that the construction works,
and the grid is not a test of it." The 372/372 wider-than-naive fact is now computed and
asserted in `make_tables.py` (`bc_wider_than_naive` = 372, `bc_width_ratio_median` = 1.276)
rather than stated. One residual clause survives in 6.2; see "New or residual overclaims".

**G2 (pre-registered): CLOSED.** Zero hits for "pre-registered" or "preregist" in the draft.
4.3: "SPEC.md is a file in this repository, frozen at commit db7c171; it was not registered
with OSF, AsPredicted, or any other external registry, and it was amended after the grids ran
to add the `bounds_c` estimator of section 5.4. 'Fixed in the analysis plan' below means
exactly that and not pre-registration." The appendix row calls SPEC.md "a repository file,
not an external registration". The abstract carries the same qualifier once.

**G3 (boundary map winners are noise): CLOSED.** Table 7 is now naive relative bias with its
relative MCSE per cell, bold where |bias| > 2 MCSE, no estimator named. 5.4 says why the old
statistic went: "a minimum taken over five near-zero quantities is biased toward zero and its
argmin is a draw rather than a finding." The majority sentence and the winner tally are gone
(grep for "uniformly won" and "wins a majority" is empty). The eight cells above 0.30 are
asserted in `make_tables.py:344` to be exactly the p = 1, pi >= 0.20 set. Figure 2 was
regenerated 12:55 with the title "Resolvability map: naive relative bias (relative MCSE);
bold where |bias| > 2 MCSE". The resolvable count is 33 of 72, not the three the bar
guessed; the draft states the computed number. One downstream sentence in 6.3 still leans on
the old table; see below.

**G4 (r_F under-reported): CLOSED.** `lane3-testbed/analysis/detector_r_f.py` exists and its
JSON gives point-biserial r of -0.0139, +0.0199, +0.0271, +0.0450, -0.0127 across EXT, NEU,
AGR, CON, OPE on 2467 essays, Spearman max 0.0702 on CON. 5.6 leads with it: "That is the
anchor: on this corpus and with this detector, |r_F| <= 0.045." The 0.161 proxy is stated:
"average word length against OPE at 0.161, three times the composite and outside the range
Table 11 treats as measured", with the reason it is excluded from the composite. Table 11's
last column is retitled "(surface proxy)" and the caption says the anchor "sits inside the
r_F = 0.05 column". The abstract names the detector score as the variable r_F is about.

**G5 (discussion overreach): CLOSED.** "The results license a set of recommendations at the
operating points the field faces" is gone. Section 6 now opens: "The recommendations below
hold on this testbed, and elsewhere only where the operating point matches it: a validity
coefficient near rho_H = 0.068, a detector whose sensitivity on frontier text is under a
third at 99% specificity, and prevalence at or under 0.30 ... recommendation 3 in particular
is a statement about a GPT-2-era classifier and should not be read as one about current
commercial detection." 1.2 item 2 is now the measurement alone: "The detector's realized
sensitivity on frontier-model text at a 99% specificity operating point is 27% (Table 1)."
The "does more to explain" sentence is gone.

**G6 (reader-facing hygiene): CLOSED on the listed items.** "lane 2" and "memo" return no
hits. The uncited Psychometrika joint-IRT sentence was cut rather than given an invented
reference; Wu, Ma, and Chen (2026) is named in text and has an entry. Muse is one sentence
with a Meta (2026-09-08) reference entry. 5.4 reads "Three scope statements." The
generative-AI-use statement is in the appendix: "Models derived the closed forms of section
2, wrote the simulation and analysis code ... and drafted this manuscript ... The author is
responsible for the content, including the parts a model wrote." Huang et al. (2025) is now
cited and Zhang and Tong (2024) is gone. Same-class leftovers the pass did not reach are
listed below.

**G9 (repo not publishable): CLOSED.** `.gitattributes` export-ignores the development
material; the archive built here has no pyc, log, pid, RADAR, ASTRA, ZHANG-OCT1 or in-sample
partial files. 29 tracked pyc are untracked and `.gitignore` covers them. Root `README.md`
maps sections 2 through 8 to files and gives the regeneration and release-tree commands.
Every artifact the appendix names is tracked and present in the archive, with the one
exception named below.

G7, G8, G10 stay open by design.

## New or residual overclaims, by sentence

1. **6.2, rec 2:** "The construction of section 5.4 needs no labels, no detector, and no
   correctly specified mixture, but it does need four numbers the analyst has to assume."
   The band inverts the section 2 closed form `Att(pi, c)`, which is the mixture. If the
   two-component model with a single coupling, one kappa and one delta is wrong, the band is
   wrong. What it does not need is a *fitted* mixture. "No correctly specified mixture" is
   the G1 clause that survived the rewrite. Change to "no fitted mixture".
2. **6.3, rec 3:** "The degraded (sp = 0.85) column is the best-behaved in Table 7 because
   it catches 69% of frontier text." Table 7 is now naive bias, and 5.4 itself says "The
   naive rows are not what separates the detector levels: naive ignores the detector by
   construction." The claim is supported, but by the delete-column numbers in the 5.4 prose
   (resolvable in 2 of 18 degraded cells, worst 0.172, against 6 of 18 calibrated, worst
   0.472), not by Table 7. Repoint the sentence.
3. **Appendix, verification record:** "followed by an independent re-review of the reporting
   (`lane4-simulation/ASTRA-REREVIEW-20260909.md`) whose required fixes are applied in
   `LAYERB-GRID.md` and the 10.10 addendum." That file is untracked in git and export-ignored,
   so the released tree cites a file it does not contain. "The 10.10 addendum" names no file
   (it is `pass2-numerical-check.md` section 10.10). Either track and release the re-review or
   drop the pointer and say the fixes are recorded in LAYERB-GRID.md.
4. **Appendix, Excluded runs:** "It is kept in the development repository and excluded from
   the released tree." `layerb-grid-insample-partial/` is untracked; it is on disk, not in the
   repository. Say "kept on the development machine" or track it.
5. **Front matter, line 3:** "Target shape: Psychological Methods." The bar's venue verdict,
   which A-F accepted, is that this is not the venue. A working paper going to PsyArXiv or
   arXiv should not carry that line.
6. **1.3:** "The SMR 2025 paper documents homogenization ..." SMR is never expanded and the
   paper is cited elsewhere as Zhang, Xu, and Alvero (2025). Use the citation.

None of these is a number problem: every figure in the six sentences is sourced. Items 1 and
2 are the two that a methods reader would mark; 3 to 6 are hygiene.

## Verdict

**VERDICT: PREPRINT-READY**, with the six sentences above fixed before upload.

Reasons:

- The bar's section 4 defines the preprint tier as "A through F make the paper true to its
  evidence." The four load-bearing overclaims (bound as constructive result, pre-registration,
  boundary-map winners, unconditional practice recommendations) are out of the text and the
  replacements are supported by artifacts that `make_tables.py` asserts rather than by prose.
- The r_F anchor now uses the quantity the derivation defines, it is measured from a file in
  the release, and the 0.161 proxy that was hidden is printed with its exclusion reason.
- The numbers gate and the voice gate reproduce here, the estimator tests pass, and the
  release tree built from HEAD contains what the appendix cites, minus the one untracked
  re-review note.
- The six residuals are one-line edits. Two of them (rec 2's "correctly specified mixture"
  and rec 3's Table 7 pointer) are wrong as written and would draw a comment; neither
  reopens a gap, and neither changes a number or a conclusion.
- What this tier does not claim: the negative result is one testbed at rho_H = 0.068 with a
  2019 detector on 2023 text, and the draft says so in section 6, section 7 and the abstract.
  G7 and G8 are what would move it to a survey-methods journal; they are not preprint
  blockers.

Fix the six sentences, re-run `check_numbers.py` (items 1 to 6 introduce no numbers), and it
is ready for PsyArXiv or arXiv stat.ME and an AAPOR or ESRA abstract.
