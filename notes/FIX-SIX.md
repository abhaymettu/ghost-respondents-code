# The six sentence fixes from the re-gate

Applied 2026-09-13 to `paper/GHOST-RESPONDENTS-DRAFT.md`, against the conditions in
`notes/REGATE-AF.md`. Nothing else in the draft was touched; no numbers were invented, and no
table, figure, script or artifact was regenerated.

## 1. Section 6.2, recommendation 2

**Old.** "The construction of section 5.4 needs no labels, no detector, and no correctly
specified mixture, but it does need four numbers the analyst has to assume: pi, kappa, delta
and rel_H."

**New.** "The construction of section 5.4 needs no labels, no detector, and no fitted mixture,
but it does need four numbers the analyst has to assume: pi, kappa, delta and rel_H."

## 2. Section 6.2, recommendation 3 (the degraded column)

**Old.** "The degraded (sp = 0.85) column is the best-behaved in Table 7 because it catches 69%
of frontier text; the calibrated (sp = 0.99) column leaves 73% of machine text in and discards
sample. The deleted set at pi = 0.20 is 86% machine, so the cost is missed contamination, not
removed humans."

**New.** "The degraded (sp = 0.85) detector catches 69% of frontier text, and after deletion
the delete estimator's bias is resolvable in 2 of its 18 cells, worst case 0.172 relative; the
calibrated (sp = 0.99) detector leaves 73% of machine text in, discards sample, and leaves
delete's bias resolvable in 6 of 18 cells, worst case 0.472 (section 5.4). The deleted set at
pi = 0.20 is 86% machine, so the cost is missed contamination, not removed humans."

The Table 7 pointer is gone. The four numbers quoted (69%, 2 of 18, 0.172, 6 of 18, 0.472, 27%
via the retained 73%) are the ones already in the 5.4 prose at draft lines 661-663; none is new.

## 3. Appendix, verification record

**Old.** "... followed by an independent re-review of the reporting
(`lane4-simulation/ASTRA-REREVIEW-20260909.md`) whose required fixes are applied in
`LAYERB-GRID.md` and the 10.10 addendum."

**New.** "... followed by an independent re-review of the reporting whose required fixes are
recorded in `lane4-simulation/LAYERB-GRID.md` and section 10.10 of
`lane4-simulation/pass2-numerical-check.md`."

**Verified against disk before writing:**

| check | command | result |
|---|---|---|
| re-review file tracked? | `git ls-files --error-unmatch lane4-simulation/ASTRA-REREVIEW-20260909.md` | `did not match any file(s) known to git` - untracked (and `.gitattributes` export-ignores `lane4-simulation/ASTRA-REREVIEW-*.md`) |
| section 10.10 exists? | `grep -n "10\.10" lane4-simulation/pass2-numerical-check.md` | line 615, `## 10.10 Addendum, 2026-09-09: M1, the labelfree column re-run at n_bins = 8` |
| both replacements tracked and released? | `git ls-files`; `git archive HEAD \| tar -t` | `lane4-simulation/LAYERB-GRID.md` and `lane4-simulation/pass2-numerical-check.md` are tracked and both appear in the release tree |

So the new sentence cites only files the released tree contains, and names the addendum's file
explicitly instead of leaving "the 10.10 addendum" unresolved.

## 4. Appendix, Excluded runs

**Old.** "It is kept in the development repository and excluded from the released tree."

**New.** "It is kept on the development machine and excluded from the released tree."

**Verified against disk before writing:** `lane4-simulation/results/layerb-grid-insample-partial/`
holds `cells/`, `grid.jsonl`, `README.md`, `run.log` on disk. `git ls-files` on that path returns
only `README.md` and `run.log`; the run's actual output (`cells/`, `grid.jsonl`) is untracked, and
the whole directory is export-ignored. The run itself therefore lives on the machine, not in the
repository, which is what the new wording says.

## 5. Front matter, line 3

**Old.** "Working paper, draft 2 (2026-09-13). Target shape: Psychological Methods."

**New.** "Working paper, draft 2 (2026-09-13)."

## 6. Section 1.3

**Old.** "The SMR 2025 paper documents homogenization and self-reported prevalence (34%) and
frames correction as future work."

**New.** "Zhang, Xu, and Alvero (2025) document homogenization and self-reported prevalence
(34%) and frame correction as future work."

Verb agreement followed the subject change (documents/frames -> document/frame). The citation
matches the form used at draft lines 82 and 102 and the reference entry at line 1255.

## Gates re-run after the edits

`python3 paper/scripts/check_numbers.py`, run on the pre-edit draft (HEAD) and the post-edit
draft in the same session:

| | HEAD (a1b0334 + 88e43c3) | after these six |
|---|---|---|
| pass 1: numbers.json keys appearing in the draft | 448 of 452 | 448 of 452 |
| pass 2: distinct unsourced numeric tokens | 135 | 134 |

Token-list set difference between the two runs: one token removed (`-20260909`, from the
dropped re-review filename), zero tokens added. No new unsourced number entered the draft.

Voice gate, the `paper/VOICE-GATE.md` pattern set run case-insensitively over the draft
(honest, we report / I report, we withdraw, transparen, candor, candid, failed hypothes,
failure is the finding, at full magnitude, worth naming, flatter, papered over, smoothed, own
failure, stated plainly, nothing was tuned, declines to, refuses to, I admit, to be fair, it is
worth noting, delve, crucial, robustly, comprehensive, nuanced, leverage, underscore,
testament, landscape, realm, tapestry, "not only ... but also"): **zero hits**. Em dashes:
zero.

Not done, by instruction: no publish, no table or figure regeneration, no other edits.
