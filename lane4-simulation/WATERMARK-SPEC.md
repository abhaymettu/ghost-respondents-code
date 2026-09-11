# Watermark (near-perfect-detection) cell: spec (QUEUE item 4)

Written before any code, per the standing spec-first rule. Judgment-sized: per QUEUE.md's own
scope note this needs only a new detector spec plus documentation, no new estimator and no new
simulation layer -- so the spec is brief, not a full spec-kit flow.

## 1. The question

LAYERB-GRID.md section 5's boundary map is read against four detectors: `none`, `calibrated`
(sp=0.99, measured se=0.276 on frontier text), `degraded` (sp=0.85, se=0.683), and `oracle`
(se=sp=1, by construction: `flag = (A==1)`). All four except `oracle` are **classifier-based**:
`detector_flags` (inject/build.py) sets `sp` as a quantile of the human detector-score
distribution and `se` falls out as whatever fraction of machine texts clear that same
threshold -- the two are coupled through one ROC curve, and Layer B measures 28% se at 99% sp
because frontier-model text and human text overlap heavily in detector-score space (section
1.2). `oracle` is not on that curve; it is the deleted mechanism (perfect knowledge of `A`),
used in LAYERB-GRID.md as a concession/upper bound, not explored as its own regime.

A **watermark** detector (arxiv.org/html/2607.10103, arxiv.org/abs/2506.05594) is mechanically
different: it depends on the generator embedding a signal at generation time, not on a
classifier reading text statistics post hoc. That decouples `se` and `sp` -- a watermark
scheme's false-positive rate on human text and its catch rate on generated text are set by
independent design choices (key length, tolerance thresholds), not by one shared operating
point on a single ROC curve. This cell asks the mirror question to the robust-estimator arm
(ROBUST-ARM.md): as detection accuracy approaches the near-perfect corner **through a
mechanism that can push `se` and `sp` toward 1 independently**, does the boundary map's worst
region (undetected, fully-coupled, high-prevalence contamination) stop being the worst region?

**Why this is not just "run the oracle cell again."** Section 2.3 / Prop. 14 of the memo
(quoted in QUEUE.md) already establishes analytically that the deletion-selection bias does
NOT vanish as `se -> 1` alone -- only `sp -> 1` removes it. `oracle` sets both to exactly 1
simultaneously and so cannot show which axis is doing the work. A watermark detector's
distinguishing property is that it can approach 1 on both axes independently, so the cell has
to sweep `se` and `sp` separately near the top of the range, not just add one more point at
(1, 1).

## 2. Two grids, sharing one mechanism

**Mechanism.** Layer A's `dgp.simulate` (dgp.py:143-146) already implements a watermark-style
detector: `flag_M = rng.random(n) < se`, `flag_H = F <= tau` with `tau` set from `sp` --
`se` and `sp` are independent SET knobs, not one classifier operating point. Layer B's
`detector_flags` (inject/build.py) has no equivalent (it always derives `se` from `sp` via a
shared real-score threshold), so this cell adds one: draw `flag_M ~ Bernoulli(se)` and
`flag_H ~ Bernoulli(1-sp)` directly and independently, bypassing the real detector-score
column (`F`) entirely -- the same "set both knobs directly" logic Layer A already uses,
ported to Layer B so the cell composes with the boundary map's real-text truth (`rho_H =
0.068`) instead of Layer A's synthetic one. This is a new detector-flag function, not a new
estimator or a new simulation layer, matching QUEUE's scope note.

**Grid A -- joint near-perfect, boundary-map-shaped (main deliverable).** Same `pi(6) x p(3)`
box as the boundary map, `n=1000`, core box (frontier generator, EXT), two new detector levels
at `se=sp=0.95` (`wm95`) and `se=sp=0.99` (`wm99`) -- chosen to sit strictly between `degraded`
(sp=0.85) and `oracle` (=1.0) on the accuracy axis without duplicating either. 36 cells, the
full five-estimator suite (`naive`, `delete`, `simex`, `labelfree`, `em`), 100 reps, identical
`rep_rng`/`build_injected_sample` call pattern to LAYERB-GRID.md so the truth values and human
draws match. `oracle` (already committed, `se=sp=1.0` exactly) is reused as this grid's
`acc=1.0` endpoint rather than recomputed -- it already IS the joint-push limit. Together
`degraded -> wm95 -> wm99 -> oracle` is a four-point accuracy trajectory at fixed `sp:se`
ratio pinned to 1, addable as two new rows on the existing boundary-map table.

**Grid B -- asymmetry check (Prop. 14, direct test).** At the boundary map's hardest cell
(`p=1, pi=0.30`, best-of-five 39.8% relative bias) and one low-difficulty control (`p=0,
pi=0.05`), sweep `se` and `sp` separately at {0.90, 0.95, 0.99} holding the other at 1.0:
`wm_se90/95/99` (se swept, sp=1 exactly) and `wm_sp90/95/99` (sp swept, se=1 exactly). 2 base
cells x 6 detector levels = 12 cells, `naive` and `delete` only (the bias mechanism Prop. 14
is about is visible in these two without needing the heavier correctors), 100 reps. This is
the cheap, decisive test of the asymmetry claim: if the memo's Prop. 14 holds, `delete`'s bias
should collapse as `sp` climbs regardless of `se`, and stay non-trivial as `se` climbs alone
even at `sp=1`... except at `sp=1` deletion is exact by construction for THIS mechanism
(`flag_H` is Bernoulli(1-sp), so `sp=1` means zero human false positives and `delete` removes
exactly the true machine set that got flagged) -- so the sharper reading is: does raising `se`
alone (at `sp<1`, some fixed shortfall like 0.90) buy less bias reduction than raising `sp`
alone by the same amount. Both readings are reported, not just the one that confirms Prop. 14.

## 3. What "watermark wins" looks like operationally

Two falsifiable readings, mirroring ROBUST-ARM-SPEC.md section 3's structure:

1. **Boundary-corner test (Grid A).** At the hardest cells (`p=1, pi in {0.20, 0.30}`), does
   `wm95`/`wm99`'s best-of-five relative bias fall below the `none`-detector best-of-five
   figure (33.5%/39.8%), and does it fall further than `degraded`'s figure at the same cells?
   If detection accuracy is what the boundary map's corner is missing, near-perfect watermark
   detection should shrink it substantially even short of exact oracle.
2. **Asymmetry test (Grid B).** Does `delete`'s relative bias at fixed `se` fall faster as `sp`
   climbs through {0.90, 0.95, 0.99} than it does at fixed `sp` as `se` climbs through the same
   levels? A "yes" is the mirror-image confirmation of Prop. 14 already used to motivate this
   cell; a "no" (or a result where both axes matter comparably in this real-text, coupled-
   contamination regime) is reported as found, since Prop. 14 was derived under Layer A's
   assumptions and Layer B's `p>0` coupling is exactly the ingredient Layer A's proposition
   does not carry.

If accuracy short of exact oracle does NOT rescue the corner (bias stays large at wm95/wm99),
that complicates the "watermark is a distinct, better-than-classifier regime" framing QUEUE.md
proposes, and gets reported as such.

## 4. Artifacts

- New detector-flag helper (Bernoulli se/sp, independent of real detector scores):
  `run_watermark_grid.py`.
- Runner reusing `run_layerb_grid.py`'s `setup`/`rep_rng`/`build_injected_sample`, producing
  Grid A (36 cells, 5 estimators) and Grid B (12 cells, naive+delete):
  `run_watermark_grid.py` -> `results/watermark/grid.jsonl`, `results/watermark/cells/`.
- Results addendum alongside ROBUST-ARM.md: `WATERMARK.md`, boundary-map-shaped table with
  the two new detector rows, the hardest-corner comparison, the asymmetry table, and the
  headline verdict stated plainly.
