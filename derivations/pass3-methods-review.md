# Pass 3: adversarial methods review

SPEC section 7, verification gate 3 of 3. Reviewer briefed to find the error, not to confirm.
Scope: `derivations/lane1-zero-coupling.md`, `derivations/lane1-partial-coupling.md`,
`lane4-simulation/pass2-numerical-check.md` including its section 10 addendum, and `SPEC.md`
sections 1.5, 4.4 and 5.

---

## Bottom line

**BLOCK.** Not on the mathematics. Every load-bearing derivation the brief named was
re-derived blind and reproduced exactly; pass 2's entire numerical certification reproduces
from committed artifacts. The derivations are the strongest part of this project and I could
not break them.

The block is on the claims. Three findings are fatal to the paper as SPEC specifies it:

1. **The anti-deletion headline is contradicted by the project's own measurement.** SPEC 1.5
   says deletion-selection "kills detect-and-delete". The effect is O(r_F^2). Lane 3 measured
   r_F ~ 0.053. At that value the selection channel removes 0.09% of trait variance and
   deletion *helps* by five percentage points of attenuation. The grid never ran anything but
   r_F = 0.3; the derivation's hard claim needs 0.5.
2. **H3, H4 and every pre-registered numeric threshold in SPEC 4.4 are contradicted by the
   completed Layer A grid.** Detect-and-delete beats all three correction estimators on RMSE
   in 82-98% of realistic-detector cells. The primary correction reaches nominal coverage in
   0 of 372 cells.
3. **H5 has no estimator.** No bounds or partial-identification code exists in the repo.

These are not pass-2 failures. Pass 2 correctly declared estimator performance out of scope
and said so. They are failures of SPEC 5 against the evidence now on disk, and pass 3 is the
last gate before the preprint.

---

## How this was checked

Independent work done in this pass, not inherited from pass 1 or 2:

- Four blind re-derivations from the DGP statement alone, with no access to the derivation
  files, each verified against exact moment construction and 5e6-2e7-draw Monte Carlo:
  (E7)/(E17)/(E15-16)/(E26)/(E28a); (E32)/(E33)/(E34)/(E52) and Prop. 11; (E48)-(E51) and
  Prop. 14; (E40)-(E45) and the A1' flip boundary (E22)/(E23).
- Independent reproduction of pass 2 section 3.1 and addendum 10.3 from `results/grid/grid.jsonl`
  and `results/grid-nonignorable/grid.jsonl` plus `population.py`, including a from-scratch
  transcription of (E48)-(E51), which exists nowhere in the codebase.
- Independent recomputation of every H1-H5 metric from the grid.
- A parametric-bootstrap null for the singular-value statistic retired in addendum 10.2.
- A closed form for the survivor sample under a violated A3 (machine-side detector score
  loading on theta, giving q_M != 1), validated against 4e6-draw Monte Carlo and against
  table 3.5 at r_M = 0.

Scripts are in this session's scratchpad and are not committed, matching pass 2's own
constraint. Nothing in the repo was modified except this file.

---

# BLOCKER

## B1. The deletion-selection headline dies at the measured r_F

**Location.** `SPEC.md` 1.5 ("This result, more than the attenuation algebra, is the argument
that kills detect-and-delete as the field's default"); `lane1-partial-coupling.md` 3.5 table
and its reading; `lane1-zero-coupling.md` 6.3 table.

**The mechanism is O(r_F^2).** From (E33), q = 1 - r_F^2 psi. Everything downstream — Prop. 11,
(E34), (E48)-(E51), the whole survivor result — enters through q. So the magnitude of the
paper's central anti-deletion claim scales with the *square* of the fluency-trait correlation.

**Lane 3 measured it.** `lane3-testbed/CALIBRATION-REPORT.md` section 2: "use |r| ~ 0.05-0.07 as
the empirical anchor magnitude (composite: 0.053 on cNEU; individual proxies up to 0.073 on
cOPN/cCON), explicitly as a lower bound". Machine-readable at
`lane3-testbed/analysis/fluency_r_f_results.json` (`headline_r_F.r = -0.0528`).

**Counter-evidence.** Att_pass at pi = 0.10, rel_H = 0.7, rho_T = 0.5, delta = 0, degraded
(0.85, 0.85), computed from (E48)-(E51) — the r_F = 0.3 and 0.5 columns reproduce table 3.5
exactly, so this is the derivation's own formula, extended left:

| kappa | c | r_F=0.05 | r_F=0.07 | r_F=0.10 | r_F=0.30 | r_F=0.50 | no detector |
|---|---|---|---|---|---|---|---|
| 0.2 | 0 | 0.9879 | 0.9875 | 0.9865 | 0.9713 | 0.9398 | 0.9383 |
| 0.2 | 0.9 | 0.9973 | 0.9968 | 0.9959 | 0.9808 | 0.9495 | 0.9885 |
| 1.0 | 0 | 0.9803 | 0.9798 | 0.9789 | 0.9637 | 0.9320 | 0.9000 |

The selection channel alone, at the degraded operating point (psi = 0.3595):

| r_F | 0.05 | 0.07 | 0.10 | 0.30 | 0.50 |
|---|---|---|---|---|---|
| q | 0.99910 | 0.99824 | 0.99640 | 0.96764 | 0.91011 |
| trait variance destroyed | 0.09% | 0.18% | 0.36% | 3.2% | 9.0% |

At lane 3's anchor the detector destroys **one part in a thousand** of trait variance. Deletion
moves the row-1 cell from 0.938 to 0.988: it removes five points of contamination attenuation
and pays back one. Detect-and-delete is not killed at the measured r_F. It works.

The derivation already knows this. Day-2 3.5 closes: "The paper's claim against
detect-and-delete is therefore conditional on two measurable numbers, the out-of-domain
false-positive rate and r_F; lane 3's r_F estimate on the essays testbed decides how hard the
claim can be stated (Q6, lane 3 owner)." Lane 3 has now answered, and the answer is roughly a
tenth of what the claim needs. `SPEC.md` 1.5 was never updated and still asserts the
unconditional version. **The two documents now contradict each other and SPEC is the one that
says what the paper will claim.**

**What would resolve it.** One of:
(a) Rewrite SPEC 1.5 to the conditional form the derivation already carries, and report the
r_F sensitivity table above as a headline result rather than the kill claim. The honest paper
is "deletion-selection is a real bias whose size is governed by r_F, and here is the r_F you
would need for it to matter" — that is publishable and it is what the math supports.
(b) Get a defensible r_F. The 0.053 is explicitly a lower bound: binary median-split trait
labels attenuate it, and the proxies are surface stylometry, not a validated fluency
instrument. The continuous BFI scores behind the IEEE DataPort login would raise it by an
unknown factor. But r_F would have to be ~0.5 for table 3.5's story, and nothing on disk
suggests the attenuation is a factor of ten.
Do not ship (a) and (b)'s absence silently: a reviewer who reads CALIBRATION-REPORT.md will
find this in five minutes.

## B2. H3, H4 and every pre-registered threshold in SPEC 4.4 are contradicted by the grid

**Location.** `SPEC.md` 4.4 and 5. Evidence: `lane4-simulation/results/grid/grid.jsonl`,
372 cells. Numbers below were computed twice, independently.

Estimators registered: `naive`, `delete`, `simex`, `labelfree`, `em` (`estimators.py:660-664`).

**H4, "the correction restores nominal coverage", threshold [92, 98]:**

| estimator | cells with rho_H coverage in [0.92, 0.98] |
|---|---|
| delete | 309 / 372 (0.831) |
| naive | 224 / 372 (0.602) |
| em | 52 / 372 (0.140) |
| labelfree | **0 / 372** |
| simex | coverage is `null` in all 372 cells |

`simex` never produced an interval: `fit_simex` computes `ci_H` only when `B_boot > 0` and the
grid ran with `B_boot = 0`. Its coverage claim is structurally untestable, not merely poor. The
only estimator that reaches nominal coverage with any regularity is `delete` — the baseline the
paper exists to discredit.

**"correction beats detect-and-delete on RMSE at calibrated and degraded operating points"
(SPEC 4.4) and H3:**

| estimator | calibrated (102) | degraded (90) |
|---|---|---|
| simex | 22 (0.216) | 12 (0.133) |
| em | 0 (0.000) | 10 (0.111) |
| labelfree | 0 (0.000) | 3 (0.033) |

Deletion has the lower RMSE in 82-98% of realistic-detector cells. H3 asserts the opposite.

**"corrected bias at most 20% of naive bias in every cell with pi <= 0.20 and c <= partial"**
(210 cells at pi <= 0.20, c <= 0.4):

| estimator | frac <= 0.20 | median ratio | max ratio |
|---|---|---|---|
| simex | 0.386 | 0.336 | 59.2 |
| delete | 0.343 | 0.426 | 47.4 |
| em | 0.119 | 1.254 | 50.4 |
| labelfree | **0.000** | 5.917 | **1821** |

The bar is "every cell". No estimator meets it anywhere close. `labelfree` — SPEC 3.4's primary
pipeline — has a *median* bias six times the naive bias it is supposed to remove.

**"pi-hat error at most 2 points at n = 1000"** (228 cells):

| estimator | median | max | frac <= 0.02 |
|---|---|---|---|
| em | 0.0679 | 0.2229 | 0.031 |
| labelfree | 0.1481 | 0.5028 | **0.000** |

`naive`, `delete` and `simex` do not estimate pi at all.

**Convergence.** `em` fails to converge in some fraction of replications in 305 of 372 cells,
up to 19.2% of 500 reps in the worst cell. It is simultaneously the estimator whose bias and
coverage are being credited.

**H1**, for completeness, mostly survives: naive bias is monotone and negative in 23 of 24
strata at c <= 0.4. At c = 0.9 it is non-monotone in all 12 strata with 73 of 120 cells
positive, range [-0.0149, +0.0116] — that is Monte Carlo noise around a near-zero true bias,
which the closed form predicts (Prop. 12: c = 0.9 sits in or above the U-shaped band at
kappa >= 0.5), not a contradiction. But H1's text says "monotone in pi and negative", with no
c restriction, and as written it is false on a third of the grid.

**What would resolve it.** SPEC 4.4's thresholds were pre-registered and the grid says the
estimators miss them, in most cases by an order of magnitude. There are only two honest routes:
report the failure as the result (a boundary-map paper, which SPEC 8.1 already contemplates as
"the most likely honest outcome"), or fix the estimators and re-run. What cannot happen is a
paper that states H3 and H4 as findings. Note that this is a *pass-3* finding precisely because
pass 2 was right to exclude it: pass 2 certified moments, and nobody has audited the estimators
against SPEC 4.4 until now.

## B3. H5 has no estimator

**Location.** `SPEC.md` 1.3 ("Bound estimand: when pi is not point-identified ... bounds on
rho_H under partial identification, reported instead of a point fix"), 4.4 ("Boundary report ...
with bounds from the partial-identification analysis. The boundary map is a deliverable"), and
H5 ("bounds on rho_H remain informative (width under 0.2 correlation units at n = 1000)").

**Counter-evidence.** `estimators.py:660-664` registers exactly five estimators, none of them a
bounds estimator. No interval-width-as-bound field exists in any grid output. There is no
partial-identification code anywhere in the repo.

H5 is not unsupported. It is unimplemented. SPEC calls the boundary map "a deliverable, not an
embarrassment" and SPEC 8.1 designates it the fallback paper if the correction headline dies —
which, per B2, it has. **The designated fallback does not exist.**

**What would resolve it.** Build it, or delete H5 and the bound estimand from SPEC. Given B2,
building it is the more likely path to a paper, and the identification analysis it needs is
already in the derivations (the c-affine structure of (E36) and the harmlessness curve (E17)
are exactly the ingredients for a bound on rho_H given a bound on c).

---

# MAJOR

## M1. The primary estimator has no Layer A grid at its shipped setting

`estimators.py:333`, `_distribution_match_pi(..., n_bins: int = 8)`, consumed by `fit_labelfree`
with no call-site override. The default was 60 when the 372-cell grid ran and is 8 now:

- `GRID-PROGRESS.md`: grid COMPLETE 372/372 at 2026-09-09 01:39:32.
- commit `e8d8021`, 2026-09-09 01:49:13, "apply staged n_bins default 60 -> 8 (grid complete)".

The freeze discipline of SPEC 5 was followed properly — the patch was staged in `32f96cf`
explicitly so a respawned pool worker could not pick it up mid-run, applied ten minutes after
completion, justified from `LAYERB-ROUND3.md` section 3.4 rather than from grid results, and
the consequence is stated in `staged/README.md`: "Applying it invalidates comparability with
any labelfree/distribution_match number produced before it, the completed grid included."

That is exemplary process and it does not change the consequence: **every `labelfree` number in
B2 above describes a configuration that no longer exists.** Pass 2 sidesteps this correctly
(its checks never touch `_distribution_match_pi`), but pass 2 is therefore silent about the
primary pipeline, and B2's audit is the first to use those columns — at the wrong n_bins.

**Resolution.** Re-run the `labelfree` column at n_bins = 8, or state in the paper that the
label-free prevalence results are at a superseded tuning. Re-running only `labelfree` on the
existing cells is cheap; the estimator is not the expensive part of a cell.

## M2. There is no Layer B grid

`SPEC.md` 4.2-4.3 require a semi-synthetic Layer B grid on real essay text, 100 reps per cell.
As of this review `results/layerb-grid/grid.jsonl` is 0 bytes and `results/layerb-grid/cells/`
is empty; the runner was launched at 04:34 today and the log reads "336 cells ... 0 already
done, 336 to run". The directory is untracked.

What exists is a 1-cell pilot, a 20-cell sweep, a (pi, n) box, a k=4 run and round-3
diagnostics. `GRID-PROGRESS.md` is titled "Layer A full grid" and must not be read as Layer B.
No Layer B artifact on disk contains a populated `coverage` field.

Consequence: every claim of ecological validity, every "on real text" statement, and any
Layer B coverage result is currently unsupported. Day-2 section 8.1 already leans on the Layer
B *pilot* to carry the N2 amanuensis story on real text, with appropriate caveats, from a
single cell whose middle arm sits 1.9 MCSE from its prediction on the wrong side of 1.

**Resolution.** Wait for the grid. It is running. Do not write Layer B prose until it lands,
and note that it will land at n_bins = 8 and therefore not be comparable to the Layer A
labelfree columns (M1).

## M3. The instrument retired in addendum 10.2 was retired on a diagnosis that is false as stated and cannot be checked

**Location.** `pass2-numerical-check.md` 10.2: "(E29)'s rank-one structure was first tested
through the top singular value of `Sigma_obs - (1-pi) Sigma_H - pi Sigma_M`, which flagged 2 of
21 cells. That was the instrument, not the theory: the excess was a constant +0.005 whatever
the signal (Spearman(signal, z) = -0.75 ...)".

**Counter-evidence.** I rebuilt the statistic and ran the parametric-bootstrap null the report
should have run — simulating from `dgp.py`, for which (E29) is true by construction, 500 reps
per arm cell:

- At **delta = 0, where the true rank-one signal is exactly zero**, the statistic has mean
  **0.193** against a target of 0. The statistic is upward biased. The report's *direction* is
  right and the swap was directionally justified.
- The magnitude is not. The excess ranges from ~1e-4 to ~0.19 across the 20 arm cells, roughly
  a thousandfold, and is ~40x the claimed "+0.005" wherever the signal is weak. It behaves as a
  floor at ~0.19-0.20 for delta below roughly 0.5, then collapses once the true signal clears
  the floor. "A constant +0.005 whatever the signal" is not what this statistic does.
- The count does not reproduce either: under an honest per-cell bootstrap null, 9 of 20 cells
  sit at z = 17 to 40 under the original statistic (all of them the delta = 0.3 nonignorable
  arm, which sits deep inside the floor), not "2 of 21".
- Excess scales roughly as 1/sqrt(n) (0.218, 0.139, 0.050 at n = 500, 1000, 5000), consistent
  with a finite-sample bias of a max-type statistic.
- The correct target for that statistic is k * pi(1-pi) * Delta^2, since the top singular value
  of Delta_vec Delta_vec^T is ||Delta_vec||^2 with Delta_vec uniform across k = 4 items. The
  report never states its target.

I cannot adjudicate the "+0.005" and "2 of 21" against the original run because **the script is
not on disk** (pass 2 section 9 method note). A verification document should not contain a
quantitative claim that its own artifacts cannot support.

**(E29) itself is fine.** All 11 strong-signal cells sit inside their own bootstrap null
(|z| < 2.1), and the weak-signal excess is present at exactly zero true signal, which proves it
is a property of the statistic and not of the closed form. The theory is not in trouble. The
verification narrative is.

**The replacement is strictly weaker.** `x_bar_H - x_bar_M` tests that the rank-one term's
loadings are uniformly Delta. It does not test that
`Sigma_obs - (1-pi)Sigma_H - pi Sigma_M` is *rank one*. Concrete alternative that passes the
mean-gap test and fails the rank-one claim: hold the class mean gap at Delta in every
coordinate but let the within-machine residual correlation be heterogeneous across item pairs
(rho_v = 0.5 on items 1-2, 0.1 on items 3-4), or add any shared topic factor loading unevenly
across items. First moments are blind to it. Prop. 10's asymmetry claim survives — 10.4's
demonstration that `Cov(x, w)` carries no delta term while the rank-one term runs to 2.70 in
Sigma is a genuine and well-powered result — but the rank-one-ness of the residual is now
untested.

**Resolution.** Either report the singular-value result honestly with its bootstrap null (the
right test, and it passes on every cell where the statistic has power), or state that rank-one
structure is verified only through its loadings. Do not describe a post-hoc swap as though the
retired instrument's bias had been measured when it had not.

## M4. Pass 2 verifies the algebra, not the model, and its summary language does not say so

**Location.** `pass2-numerical-check.md` 9: "the deletion bias is not merely consistent with the
data, it is required by it." Addendum 10.9: "Layer A reproduces every derived moment the DGP
can instantiate."

`dgp.py` was written from day-2 section 6.1, which is the derivations' own canonical DGP. The
transcription discipline of section 1.1 — re-typing closed forms rather than importing
`population.py` — is real and catches transcription error, and section 2's exact agreement is a
genuine receipt for it. But it cannot catch a modelling error, because a wrong model would be
wrong identically in the closed form and in the simulation.

So "72 of 90 degraded cells reject q = 1" does not mean the deletion bias is required by data.
It means the simulation implements the same Gaussian-threshold-on-a-trait-correlated-fluency
mechanism the derivation assumes. If real detectors do not work that way — and the only thing
that could break the tie is lane 3's r_F, see B1 — both are wrong together. The word "data" in
that sentence is doing work it has not earned.

"Every derived moment the DGP can instantiate" is likewise near-circular: the DGP's reach was
set by the derivations, so the sentence is close to "every moment we chose to be able to
check". The honest form is the one pass 2's own section 6 used before the addendum widened it.

**Resolution.** Wording. Replace "required by it" with "required by the simulation under the
detector model of 6.2", and keep 10.9's claim scoped to the DGP rather than to the theory.

## M5. H2 as pre-registered is not what was tested, and the label-free route is dead

**Location.** `SPEC.md` 5 H2: "homogenization signature: between-item correlations inflate among
machine cases while trait-outcome correlation attenuates."

Three separate things carry the name H2 in this project and they are not the same claim:

1. **SPEC's H2** — inflation *among machine cases* against attenuation of trait-outcome
   correlation. On the Layer A grid this is untestable: the grid records `r_obs_emp` as the
   pooled between-item correlation with no decomposition by authorship class, and Prop. 8's
   within-M condition (rho_v > (rel_H - c^2)/(1 - c^2)) is exercised only through the 12
   rho_v = 0.5 cells.
2. **The pooled inflation condition (E28a)** — genuinely and well verified by the addendum's B1,
   which straddles delta* = 1.139 and 1.291 and turns the sign on the predicted side at both
   prevalences, tens of MCSE clear. This is the single best piece of verification in the whole
   pass-2 document and the reliability paradox is real. But it is a claim about the *pooled*
   correlation driven by the between-mean term, not about machine cases being internally more
   homogeneous.
3. **"Weak H2"** — lane 3's label-free within-document chunk-correlation route to rel_H.
   `WEAK-H2-DIAGNOSIS.md:238` is unambiguous: "Weak-H2, as specified (a label-free,
   within-document chunk-correlation estimate of rel_H), is not recoverable on this testbed at
   any n or pi." Cause: chunks of one essay share a document-level stylistic factor, not the
   trait — partialling out the label removes 0.0% of rbar. The OOF refit moved the failure by
   at most ~7%.

**What H2 means now:** the homogenization *algebra* is verified (item 2), the *label-free
estimation route* to it is dead (item 3), and SPEC's actual pre-registered wording (item 1) has
never been directly tested. `WEAK-H2-DIAGNOSIS.md:258` already prescribes the fix: "report H2 as
not established via the label-free multi-item route, with the single-item route as the only
validated path, contingent on having gold labels for calibration."

**Resolution.** Rewrite SPEC 5 H2 to item 2's claim, which is proven and simulated on both
sides of its boundary, and report item 3's failure as a negative result. It is a good negative
result — it says why the obvious label-free reliability estimator does not work on open-ended
text, which is worth a section.

---

# MINOR

**m1. Prop. 11 is missing a `rho_T != 0` guard.** `lane1-zero-coupling.md:350`. The conditions
given are r_F != 0, sp_bar < 1, and (rel_H < 1 or rho_T^2 < 1). At rho_T = 0 all three can hold
while rho_H,pass = rho_H = 0, so the strict inequality fails. The proof establishes the *ratio*
is < 1, which is correct; the statement is about the coefficients. Prop. 17 in the companion
file already carries the rho_T != 0 guard, so this is an inconsistency between the two.
Degenerate, one clause.

**m2. Prop. 14(ii) is in neither inventory.** The ROC non-monotonicity claim — "a better
detector in the sense of a higher threshold is not less bias", table 3.4 — is not in pass 2
section 5's verified-propositions table and not in section 6's or 10.7's unverifiable lists. It
cannot be simulated by the current code: `dgp.py` flags machines by `rng.random(n) < se` at four
named operating points and has no mechanism to move along a ROC, and sp_bar = 0.50 is not one of
them. Table 3.4's 22 numbers are arithmetic-reproduced (and I confirm them independently), but
the *shape* claim is unsimulated and unlisted. Add it to the unverifiable list, or add a
three-point sp sweep at fixed d' = 2.073, which is cheap.

**m3. `calibrated` means two different things, and section 3.2 crosses them.** P2-1 records that
`dgp.py:16-21` sets calibrated = (0.95, 0.99) while day-2 section 0 reads it as (0.99, 0.99),
and correctly warns that table 3.5's calibrated column does not describe the grid's calibrated
cells. What P2-1 does not note: pass 2 section 3.2 then uses the grid's calibrated cells ("a
median 1.02 mcse and no cell rejects") to endorse table 3.5's reading at the *other* operating
point. The endorsement happens to survive because q depends only on sp, which is 0.99 in both,
but the sentence as written moves between two operating points without saying so.

**m4. The frozen grid's uncorrected max |z| is never stated.** Section 3.1 reports a single
"max abs z" column (3.10) without saying which reading it is, while the addendum reports both.
I computed both: uncorrected max |z| is 3.16 (`rho_obs`), 3.23 (`rho_obs,pass`), 3.22 (`r_obs`),
all inside z* = 4.081, so no verdict was hidden. Report both readings for the frozen grid as
10.3 does for the arms.

**m5. The `r_obs` aggregate is marginal and is reported as clean.** Corrected mean z for `r_obs`
is -0.106 over 372 cells; treating cells as independent that is -2.04. The overall KS distance
of 0.039 has p = 0.068 — not a comfortable pass. Section 3.3's own numbers are correct and the
residual is ~4e-5 in correlation units, which genuinely is negligible, but "distributed as
N(0,1) to KS distance 0.039" in the section 9 verdict reads as confirmation of a test that
nearly rejected.

**m6. The amanuensis cell is never simulated.** (E54), (E55), (E76) live at c = 1; the grid and
the arms top out at c = 0.9. This is correctly listed as unverifiable in section 6 and 10.7 —
but day-2 section 8.1 makes an explicit signed claim there (Att = 1 + pi(1/sqrt(rel_H) - 1),
+2% at pi = 0.10, +6% at pi = 0.30), and it is the claim SPEC 1.2's third bullet is being
rewritten around. One c = 1 column costs a few cells. Run it.

**m7. Pass 2's verification scripts are not committed.** Section 9 and 10.9 method notes. I
reproduced section 3.1 and 10.3 exactly from committed artifacts plus a from-scratch
transcription of (E48)-(E51) — mean z, corrected mean z, max |z| and the worst cell's closed
form, empirical value and mcse all match to the printed digits — so this is hygiene, not
correctness. But note that (E48)-(E51), the load-bearing survivor formula, exists in **no**
committed code: `population.py` stops at (E34) and `arm_moments.py` carries only raw moments.
The formula that certifies the paper's central mechanism has no implementation on disk. Add it
to `population.py`.

---

# NOT A FINDING

Recorded because the brief named these as attack targets and they held.

**n1. Every load-bearing derivation reproduces.** Blind re-derivations from the DGP alone, no
access to the derivation files:

| target | verdict |
|---|---|
| Att, (E7) | reproduced exactly; table 1.6's 24 values match to 4 dp |
| c*(pi), (E17); c_1, c_2, (E15)/(E16); Prop. 12's g_1 = 2kappa/S, g_2 = S/2 | reproduced, including the identity g_1 g_2 = kappa |
| pi_min, (E38) | 0.3517 vs 0.352 printed; Att(0.30/0.35/0.40) = 0.9869/0.9865/0.9869 |
| q, (E33), and Prop. 11's proof | reproduced; day-1 6.3 table reproduced to 4 dp |
| (E34), (E52) | reproduced |
| Survivor coefficient (E48)-(E51) | reproduced; **table 3.5's 16 values and table 3.4's ROC rows match to every printed digit** |
| (E22)/(E23) flip condition | reproduced, including the nonemptiness condition delta d_theta > sqrt(rel_H)/pi |
| (E40)-(E43), the unequal-variance mixture | reproduced term by term |
| (E28a) H2 threshold | reproduced; the 1.61 and 0.72 coefficients confirmed |

Max discrepancy between closed forms and exact moment construction: 2.7e-15. Against Monte
Carlo at 5e6 to 2e7 draws: within sampling noise throughout.

I found no sign error, no Jacobian error, no conditioning error, and no marker trick. The
day-1/day-2 pair is careful work and the inline pass-1 corrections (D2, D3, D17, D1/N2) are all
correctly applied.

**n2. The two normalizations really are equivalent.** The derivations use s2_T = rel_H, V_H = 1;
`dgp.py` uses s2_T = 1, V_H = 1/rel_H. I checked the parameter map by hand rather than trusting
the exactness table: delta = (mu_H - mu_M)/sqrt(V_H) maps correctly through
`Delta = delta * sqrt(V_H)` with mu_H = 0, mu_M = -Delta; kappa = s2_M/V_H maps through
`s2_M = kappa * V_H`; lam_M = c sqrt(s2_M/s2_T) reduces to `c * sqrt(s2_M)` at s2_T = 1; the
detector's F = r_F theta + sqrt(1-r_F^2) eta is already standardized at s2_T = 1. Every compared
quantity is a correlation or a standardized ratio. Pass 2 section 2's 0.000e+00 agreement is a
real receipt, not a coincidence of construction.

**n3. `dgp.py` instantiates the model the derivations describe.** Including the two places it
could easily have gone wrong: the machine branch is centered on its own class under A1'
(`X_M = mu_M + lam_M * (theta - d_theta) + v`, matching option A of day-2 2.1 with q_M = 1), and
the detector passes humans on `F > tau` with `tau = Phi^{-1}(1 - sp)`, matching (E63). I also
asserted in code that no cell combines `d_theta != 0` with a detector — where (E48)-(E51) would
be invalid, since it assumes A1 pre-selection — and the assertion holds across all 392 cells.
The addendum's choice to target `(E21) at detector none` for the A1' arms is correct.

**n4. The finite-sample correction is legitimate and changes no verdict.** `-rho(1-rho^2)/(2n)`
is the standard bivariate-normal Pearson bias and it moves the target in the right direction.
It is applied to a mixture, which the report flags. I verified 0 failures at z* = 4.081 both
with and without it, on the frozen grid and on the arms. The addendum's 10.3 note — that on
strongly bimodal cells the correction moves the mean z slightly *away* from zero and that no
per-cell verdict depends on which reading is used — reproduces exactly.

**n5. z* = 4.081 is conservative but not gamed.** A Bonferroni family-wise bar maximizes type-II
error in a check whose purpose is to confirm a null, which is backwards in principle. But the
report anticipates the objection with section 3.2's power analysis, keeps the bar verbatim for
the arms rather than loosening it for the smaller family, and reports both z readings. The two
sharp discriminations it does run (q = 1 at 5.31 median mcse separation with 72/90 rejections;
the pre-D1 survivor gap rejected at z = +15.98 against the corrected reading's -0.35) are
well-powered and correctly executed. The one criticism that stands is that for every moment
*other* than those two, power is measured against "contamination does nothing" rather than
against a plausibly-wrong closed form.

**n6. (E18), the A1 sign flip at c < 0, is honestly out of scope.** Negative coupling means the
LLM output moves against the respondent's trait. Nobody has argued for that cell and the grid
is right not to carry it.

---

# The four structural gaps of addendum 10.7

The brief asks for a verdict on each. I add a fifth the inventory misses.

**1. (E18), sign flip needs c < 0. Verdict: honestly out of scope.** See n6.

**2. (E40)-(E45) with q_M != 1. Verdict: out of scope for the headline, but only because I
measured it, and the number must go in the paper.**

This is the one the brief singles out and it deserves the full answer. 10.7 is right that it is
structurally unreachable — `dgp.py:126` draws `theta = standard_normal(n) + d_theta * A`, fixing
Var(theta|M) = Var(theta|H), and `flag_M = rng.random(n) < se` hard-codes A3.

But q_M != 1 is not an idle generalization. It is the *formal home of assumption A3*, which
day-2 section 3.1 explicitly nominates as a pass-3 attack target: "at c > 0 it is an assumption
about the detector ... and pass 3 should attack it (a detector that flags bland text more, when
blandness tracks c theta, violates it)." If the detector's machine-side score loads on theta at
r_M, then machine survivors are truncated too: a_M = r_M lambda_M and
**q_M = 1 - r_M^2 psi_M != 1**. An A3 violation *is* the q_M != 1 case. So "structurally
unreachable" understates it: the DGP cannot express the failure mode the derivation itself
flagged as most likely to break the survivor result.

So I built it. Survivor moments computed directly with class-dependent (a_M, q_M), holding the
operating point (se, sp) fixed — note Var(F|M) = 1 regardless of r_M, so se is unchanged and the
comparison is clean. The r_M = 0 branch reproduces table 3.5 to four decimals (0.971, 0.940,
0.949, 0.932 at degraded; 0.996, 0.991, 0.992, 0.991 at calibrated), and the r_M != 0 branch was
validated against 4e6-draw Monte Carlo (agreement to 0.002, within MC noise). At pi = 0.10,
rel_H = 0.7, rho_T = 0.5, delta = 0, r_F = 0.5, degraded:

| cell | r_M = 0 (A3) | r_M = 0.2 | r_M = 0.3 | r_M = 0.5 | q_M at r_M = 0.5 |
|---|---|---|---|---|---|
| kappa = 0.2, c = 0 | 0.9398 | 0.9390 | 0.9385 | 0.9372 | 0.799 |
| kappa = 0.2, c = 0.9 | 0.9495 | 0.9491 | 0.9491 | 0.9498 | 0.799 |
| kappa = 1.0, c = 0 | 0.9320 | 0.9312 | 0.9307 | 0.9295 | 0.799 |

**A3 is robust.** Even at r_M = 0.5, which destroys 20% of the machine survivors' trait variance,
Att_pass moves by at most 0.0026 — two orders of magnitude below the effects the paper reports,
and in the direction that makes deletion look slightly *worse*, not better. The reason is
structural: at c = 0 the machine carries no trait signal for q_M to scale, and at c = 0.9 the
machine's own range restriction and the shrunken between-class gap nearly cancel.

Verdict: q_M != 1 does not threaten any claim. But 10.7's "structurally unreachable in the
current DGP" is the wrong reason to stop, because it describes a limit of the code rather than a
fact about the model, and A3 is a named open question (Q9). The paper should carry the table
above as a one-paragraph sensitivity analysis. That converts the project's most exposed
assumption from unaddressed to bounded, for the cost of no new simulation.

**3. (E54), (E55), (E76) at c = 1. Verdict: matters, cheap, run it.** See m6.

**4. (E56)-(E60), rho_vw, both endpoints machine-written. Verdict: honestly out of scope,
conditionally.** Layer A's outcome is clean by construction so rho_vw = 0 identically. Day-2
section 5's ship condition is explicit: this section ships only if Layer B's target stays clean
(Q4, Abhay's call, still open per `lane1-open-questions.md:39`). If the Q4 call goes the other
way, (E60) becomes a headline — a sign flip under *ignorable* authorship, reachable on the SPEC
grid — and it would then need its own simulation, which does not exist. Fine as it stands;
becomes a blocker if Q4 flips.

**5. Missing from the inventory: Prop. 14(ii), the ROC non-monotonicity.** See m2. 10.7 opens
with "P2-3's list is now empty. Four items from section 6 remain" — there are five.

---

# Verdict

**BLOCK.**

The mathematics passes. I attacked the five results the brief named and could not break any of
them; four independent blind re-derivations reproduce every load-bearing closed form and every
hand-computed table to the printed digit, and pass 2's numerical certification reproduces
exactly from committed artifacts. On the terms SPEC section 7 sets for this gate — "an
unresolved discrepancy at any pass blocks the preprint" — there is no discrepancy in the
derivations and pass 2's PASS verdict stands.

The block is that the paper SPEC 5 describes is not the paper this evidence supports.

**Conditions to lift the block. All three of B1, B2, B3 must be resolved before any preprint.**

1. **B1.** Rewrite SPEC 1.5 to the conditional claim the derivations already carry, and report
   the r_F sensitivity as a result. Or produce an r_F that survives review. The current SPEC
   sentence is contradicted by the project's own calibration report.
2. **B2.** Either report the SPEC 4.4 threshold failures as the paper's finding (the boundary
   map SPEC 8.1 already names as the likely honest outcome), or fix the estimators and re-run.
   H3 and H4 cannot be stated as findings. Note M1 first: the `labelfree` numbers are at a
   superseded n_bins and should be re-run before anything is concluded from them.
3. **B3.** Build the bounds estimator or delete H5 and the bound estimand from SPEC. Given B2,
   build it — it is now the paper's most likely spine, and the identification ingredients are
   already in (E17) and (E36).

**Should also be done, none of them blocking:** M3's honest re-report of the rank-one test with
its bootstrap null; M4's two wording fixes; M5's rewrite of H2 to the claim that was actually
proven, with weak-H2's failure reported as a negative result; the q_M sensitivity table from
gap 2; the c = 1 column (m6); (E48)-(E51) added to `population.py` (m7); Prop. 11's rho_T guard
(m1); Prop. 14(ii) added to the unverifiable inventory or given a three-point sp sweep (m2).

**One process note.** The three blockers are all claim-versus-evidence findings, and none of
them was in scope for passes 1 or 2 — pass 1 diffed derivations, pass 2 certified moments and
said plainly that estimator performance was out of scope. The verification protocol as designed
has no gate that reads SPEC 5's hypotheses against the grid until pass 3, by which point the
grid is finished and the estimators are frozen. That ordering is worth changing for the next
project: the hypothesis audit wants to happen at pilot, when the estimators can still move.

PASS3-METHODS-DONE
