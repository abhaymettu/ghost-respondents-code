# Voice gate: PASS

Gate run 2026-09-13 on commit c5136ad ("paper: state the estimates, drop the ceremony").
Working tree under paper/ was clean at gate time; the voice pass is fully committed.
No rewrites were made by this gate.

## Receipts

### 1. VOICE-FIX.md rewrites read as plain reporting

All 39 before/after pairs were read against the live files. Each "after" states an estimate,
a status, or a cross-reference and moves on. No honesty announcement, no withdrawal
ceremony, no honesty-as-strength framing survives in any of the 39 sites.

Facts preserved as required: 0/372 labelfree coverage (5.1), three-of-four thresholds fail
outright (abstract, 1.2, Table 4), SPEC 1.5 "kills detect-and-delete" does not hold at the
measured r_F (5.6), WITHDRAWN status on Open item 5 and on GAPS-CLOSURE-SPEC items 1, 3, 4,
naive lowest RMSE in 274/336 cells (5.3, 6), EM slightly harmful (abstract, 5.5).

### 2. Numbers identical

Per-file multiset comparison of every numeric token removed vs added in
`git diff c5136ad~1 c5136ad -- paper/` (VOICE-FIX.md excluded as a new file):

| file | removed-only numbers | added-only numbers |
|---|---|---|
| GHOST-RESPONDENTS-DRAFT.md | none | 0.053 (r_F, already in abstract and 5.6), 5.3 and 7 (section cross-refs) |
| FINAL-PASS-REPORT.md | none | none |
| GAPS-CLOSURE-SPEC.md | none | none |
| REWRITE-NOTES.md | none | none |

No numeric value was dropped, and the only additions are section pointers and a restated
measured value. QUEUE.md, README.md, FRAMING-DECISION.md are untouched by the commit.

### 3. Register grep across paper/ (VOICE-FIX.md excluded)

Pattern set: honest, we report / I report, we withdraw, withdrawn, transparen, candor,
candid, failed hypothes, failure is the finding, at full magnitude, worth naming,
flattering, papered over, smoothed, kill claim, own failure, stated plainly, nothing was
tuned, declines to, refuses to, admit, concede, concession.

Hits and disposition:

- `GHOST-RESPONDENTS-DRAFT.md:409, 590, 608` and `tables/tab_t4_rmse.md:11`: "concede
  oracle" / "conceded" / "the SPEC-anticipated concession". This is the pre-registered T4
  wording for the oracle arm, a status label, not a virtue claim. Stays.
- `GHOST-RESPONDENTS-DRAFT.md:1226` and `GAPS-CLOSURE-SPEC.md:19, 52, 66, 106`: "WITHDRAWN".
  Historical status labels the brief requires to remain. The "-honestly" suffix is gone at
  every site.
- `FINAL-PASS-REPORT.md:89-90, 135`: describes a cut made under the rule ("an announcement
  about honesty rather than a fact") and a scan for "self-announced honesty". Change-log
  prose about the rule, in a process report, not paper text. Stays.
- `REWRITE-NOTES.md:36, 58`: "the kill claim" as a historical name for SPEC 1.5's
  unconditional claim. Descriptive, not ceremonial. Stays.
- `QUEUE.md:40`: "treated as a concession/upper bound" refers to the oracle arm. Stays.

No hit for honesty, transparent, candor, we report, we withdraw, or "failed hypothesis" as a
virtue anywhere in the swept files.

### 4. Coherence read

Read end to end: front matter, Abstract, 1.2, 1.3, 4.3, all of section 5 (5.1 through 5.7,
the section carrying rewrites 10 through 16), section 6, Open items. The draft reads as one
paper. The abstract runs algebra, corrections, bound, deliverable in order with no seam;
section 5 keeps its through-line from Layer A thresholds to the boundary map to the
r_F-conditional deletion result, and section 6 recommendation 2 now points at the bound
without the "declines to return a number" flourish.

## Follow-ups, not blocking

These predate the voice pass or are cosmetic. Left in place because this gate makes no
rewrites.

- Draft 5.4, the partial-identification bullet: "Two scope statements. First ... Second ...
  Third, and most limiting for practice ...". Count mismatch. Present in c5136ad~1 at the
  same lines (694, 701), so not introduced by the voice pass.
- Draft line 52 (abstract) is 145 characters where the file wraps near 95; ragged breaks
  also at "At five times the / replications" (abstract), "Each remains outside its
  threshold. The simex column / was re-run" (5.1), and 1.2 item 4. Rewrap when convenient.
- Draft 5.7, watermark paragraph, says within one paragraph both "this is not a contradiction
  of Prop. 14, it is outside its scope" and "not a refutation of Prop. 14". One of the two
  can go. Defensive repetition, not ceremony.
