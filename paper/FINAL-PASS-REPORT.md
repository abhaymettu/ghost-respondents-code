# Final writing pass: what changed, what landed, what is still open

Pass run 2026-09-13 on `paper/GHOST-RESPONDENTS-DRAFT.md`, which goes from draft 1 to draft 2.
Writing only: no simulation was run, no estimator written, no grid touched. Every number added
below was already on disk before this pass started.

---

## 1. Changes, one line each, by section

**Front matter**
- Affiliation, corresponding address, and acknowledgements are now an explicit bold
  PLACEHOLDER rather than an absence; the author name stays as it was.
- The provenance sentence was corrected: `make_tables.py` / `make_figures.py` cover sections
  4-6, and the three Layer A column re-runs are read from `b2-tables-recomputed.json` and the
  grids beside it.
- "Items marked TODO" is gone; unresolved items now live in one Open items section at the end.

**Abstract**
- Rewritten in four paragraphs (mixture, the algebra holds, the corrections do not, the bound
  does). First person singular throughout.
- Added the partial-identification bound as the fourth paragraph and the paper's one clean
  positive, with the "given the prevalence" condition stated in the same breath.

**1.1**
- Added the prevalence range: 34% (Zhang, Xu, Alvero 2025) and under 10% to over 80% by
  platform (Xu and Malkin 2026), with the note that the grid's pi <= 0.30 is conservative.
- Closed the draft's oldest TODO. The three motivation sources are now named, attributed, and
  described by what each actually does: Pew (2026), Gerber and Cash (2026), Panda et al.
  (2026).
- "Style as a confound" and "the SMR 2025 study" replaced with author-year citations.

**1.2**
- Rewritten as four numbered positive results instead of three in prose, with the bound added
  as the fourth.
- New closing line, which is the one-sentence stress test the brief asked for: at this
  validity level the honest output of a contaminated open-ended item is a bracket, not a
  coefficient.

**1.3**
- Closed the second TODO. Two paragraphs added: the terminological separation from
  training-data contamination (Han et al. 2025), and the rectification / prediction-powered
  lineage (Krsteski et al. 2026; Lee et al. 2025; Angelopoulos et al. 2023; Egami et al.
  2023), all of which need labels this paper assumes away.

**3**
- Header corrected: five estimators make the frozen grid's field, three more are registered.
- simex bullet rewritten: the B_boot = 0 statement was stale. Layer A now has intervals
  (B_boot = 50, 372/372), Layer B does not, and the point estimate is unchanged by either.
- Küchenhoff, Mwalili and Lesaffre (2006) added as the method's origin, with the note that
  C9 stands against the 2006 method as implemented.
- New `bounds_c` bullet, including that it conditions on known pi, rel_H, kappa and delta.
- New closing paragraph stating the no-label assumption as the thing that separates this
  setting from the PPI/DSL families.

**5.1**
- Layer A numbers updated to the shipped estimator configuration: simex coverage 105/372
  added, labelfree RMSE-vs-delete 0/102 and 13/90 added.
- New paragraph explaining the two column re-runs, what each moved, and why simex's coverage
  getting *worse* as n grows is an extrapolation-bias signature rather than a bootstrap-size
  problem.

**5.3**
- T2 table: a line added saying simex is unevaluable on Layer B specifically, and pointing to
  the Layer A number.
- T3: new paragraph naming the three quantification assumptions the label-free estimator
  violates (Esuli et al. 2023; Balabdaoui and Besdziek 2025), so the five-to-six-point miss is
  explained rather than only reported.

**5.4**
- The H5 bullet was replaced. It now carries both layers: the Layer B point-estimate bound and
  its 8/18 coverage, the diagnosis (it treats a Monte Carlo estimate as exact), the
  Imbens-Manski fix, and the registered Layer A `bounds_c` result across all 372 cells.
- Three scope statements added: the Layer B bound still covers only detector=none; the bound
  is not claimed sharp (Horowitz-Manski corrupted, not contaminated, whenever c > 0); it
  conditions on known pi, which section 5.3 says is not recoverable here.

**5.6**
- New closing paragraph. Pangram 4's non-native FPR equalling its overall FPR means a
  classifier can reach r_F near zero without a watermark, so Table 11 is a sensitivity table
  over r_F rather than a claim about any detector's position on it.

**5.7**
- **Corrected an error.** The restatement of Prop. 14 read "no improvement in sensitivity
  alone removes the deletion bias, only sensitivity toward 1 does" - self-contradictory, and
  the second word should be specificity. Fixed.
- The watermark cell is restated as being about a detector whose flag is independent of the
  trait, of which a watermark is the constructive case and a large classifier may be an
  empirical one. Heading updated to match.
- Cut "this is stated as found, not smoothed toward a cleaner story" (an announcement about
  honesty rather than a fact).
- Six em dashes converted to the hyphen form the rest of the draft uses.

**6**
- New recommendation 2: where a point estimate has to carry weight, report a bound. Includes
  the known-pi caveat and the fact that a real application's union is wider than anything
  computed here.
- New recommendation 8: if any authorship labels can be bought, buy them.
- Recommendation 4 (prevalence) grounded in Ludwig, Mullainathan and Rambachan (2024).
- Recommendation 7 (deletion-selection) picks up the Pangram result.
- List renumbered 1-8; "a short set" corrected to "a set".

**7**
- simex/H5 bullet rewritten for the two-layer state, plus the sharpness and known-pi caveats.
- Detector bullet: added that RoBERTa is the weakest detector class in the published
  comparisons (Jabarian and Imas 2025; Glickenhaus et al. 2026), so this study's detection
  axis is pinned at its weakest point.
- Four new bullets: no validation subsample (named as the most consequential assumption);
  mixed and edited authorship outside the two-component model (Zhang et al. 2024; Pangram 4's
  55.01% mixed recall); essays are not survey-length answers (Lebrun et al. 2024); and the
  pool generators may have memorized the instrument (Han et al. 2025), so part of the measured
  c_pool could be provenance rather than trait expression.

**8**
- Artifact table gained seven rows: `grid-simex-boot50`, `grid-bounds-c`, `h5-bounds`,
  `robust-arm`, `watermark`, `b2-tables-recomputed.json`.
- Added the note that the three column re-runs use `run_grid_column.py` and leave every other
  estimator's draws bit-identical to the frozen grid.

**References**
- Header rewritten to state provenance per entry class rather than as one blanket claim:
  2026-09-10 live checks, the 2026-09-11 scan's V / V-mirror codes with `docs/LIT-SCAN.md` as
  the record, and three abstract-page reads done in this pass.
- 19 entries added. Every one carries its status; three are marked "abstract page read, full
  text not read"; `unverified` entries stay `unverified` (Küchenhoff 2006, Zhang and Tong
  2024, the Ludwig et al. journal placement).
- The NORC entry now carries both attributions (AAPOR schedule lists Huang; the library
  write-up lists Sepulvado, Huang, Lerner) because they are different documents.

**Open items** (replaces the TODO list)
- Rewritten with current status per item.

**Voice, throughout**
- Authorial "we" converted to "I" (11 occurrences). Em dash count: 11 to 0.
- No instances found of the banned tells on a scan for "delve", "crucially", "moreover",
  "leverage", "robust" as an adjective, or self-announced honesty.

---

## 2. Final numbers folded in, and where they come from

Everything in this table was verified in this pass by reading the grid JSONL directly, not by
quoting the report that summarizes it.

| number | value | source |
|---|---|---|
| simex rho_H coverage in [0.92, 0.98] | 105/372 (28.2%), median 0.910 | `results/grid-simex-boot50/grid.jsonl` |
| simex coverage by n (fraction in band) | 0.319 / 0.303 / 0.181 at n = 500 / 1000 / 5000 | same |
| simex median CI width | 0.0995 (max 0.196) | same |
| labelfree coverage at n_bins = 8 | 59/372 (was 0/372 at 60 bins) | `results/b2-tables-recomputed.json`, `h4_coverage` |
| labelfree median pi_hat error at n = 1000 | 0.0707 (was 0.148) | same, `pi_hat_err` |
| labelfree median bias ratio vs naive | 1.916 (was 5.917) | same, `corrected_bias` |
| labelfree RMSE beats delete | 0/102 calibrated, 13/90 degraded | same, `h3_rmse_beats_delete` |
| bounds_c coverage, all 372 cells | median 0.974, minimum 0.936, none below 0.90 | `results/grid-bounds-c/grid.jsonl` |
| bounds_c width < 0.2 | 48/72 at n = 500, 178/228 at n = 1000, 72/72 at n = 5000 | same |
| bounds_c median width | 0.1780 / 0.1312 / 0.0749 by n; 0.1405 overall | same |
| bounds_c point-estimate version coverage | median 0.349 | `ESTIMATOR-FIX-REPORT.md` section 3 |
| grid-simex-boot50 runtime | 36,376 s, 372/372 | `GRID-PROGRESS.md`, `simex_boot50_run.log` |

Unchanged and re-confirmed: delete 309/372, naive 224/372, em 52/372 coverage; simex T1
38.6%, delete 34.3%, em 11.9%; em pi_hat median 0.0679 with 7/228 passing; simex RMSE 22/102
and 12/90. The B_boot re-run touches only the CI, never the point estimate, so no bias or RMSE
number anywhere in the paper moved.

Literature numbers were taken from `docs/LIT-SCAN.md`, which records the fetched URL and a
status code per entry. Three papers (arXiv 2510.07175, aclanthology 2026.acl-long.498, arXiv
2511.21140) were fetched at their abstract pages in this pass to close TODO 2; the References
say so.

---

## 3. What is still open

**Owner**
- Affiliation, corresponding address, acknowledgements. Explicit placeholder in the front
  matter. Not invented here.

**Queued, owner-scheduled (`paper/QUEUE.md`)**
- The robust-estimator column beyond the 72-cell boundary map (Layer A, other sample sizes).
- A measured rather than assumed watermark operating point. `WATERMARK.md`'s se = sp =
  0.95/0.99 remain assumption.
- Both arms were already run as the follow-on cells reported in section 5.7; nothing was added
  to either in this pass.

**Known gaps the draft states rather than hides**
- The Layer B H5 bound is still the point-estimate version over 18 detector=none cells.
  Extending a bound to detected cells on real text needs a derivation combining the c-affine
  bound with the detection selection term (E30-E34).
- The bound conditions on a known pi, and section 5.3 shows pi is not recoverable from score
  distributions at this separation. A field application has to sweep pi and report the union;
  that sweep is not computed.
- simex has no interval on Layer B.
- Document-pooled Layer B is future work, not run.
- Coupling capped at c = 0.379 by the pools; SPEC's high-c corner is unreachable here.
- The full texts of the three papers added to section 1.3 were not read.

---

## 4. State of the draft

This is now a reviewable draft rather than scaffolding. It is 1,249 lines, complete through
section 8 plus references, with every claim traced to a file in this repository and every
unresolved item listed in one place with a status instead of scattered as inline TODOs. The
spine it lost when the kill claim failed has been replaced rather than papered over: the
boundary map is the descriptive deliverable, and the partial-identification bound is the
prescriptive one, and the bound is the first thing in the project that meets a pre-registered
target without qualification beyond a condition the paper states plainly. The paper's
strongest feature is still that it reports its own failures at full magnitude - 0/372 nominal
coverage for the pre-registered primary, the withdrawn kill claim, EM getting worse with more
resolution, the naive estimator winning 274 of 336 cells - and this pass added failures rather
than removing any, including one internal contradiction in the section 5.7 restatement of
Prop. 14 and three new limitations that a reviewer would otherwise have found first. What it
cannot do yet is claim a working correction, and it does not try to. The remaining risk is not
in the writing: it is that the whole boundary map sits at rho_H = 0.068, a validity level set
by a 256-token chunk scorer, and the one experiment that would tell you whether the negative
results survive a better scoring pipeline is named as future work rather than run.
