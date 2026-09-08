# Layer B injection module (`lane4-simulation/inject/`)

Step 2 of `derivations/design-pivot-memo.md` section 8.2. Builds contaminated survey samples
out of **real machine-written text**, with the coupling `c` dialed rather than generated, so
Layer B costs **zero generations and zero dollars**.

Code + tests only. The Layer B pilot cell is **not** run here: it waits on lane 3's
`pool_measurements.json`. The Layer A grid was running throughout and was not touched.

    lane4-simulation/inject/
      __init__.py       explicit exports
      pools.py     493  lane 3 ingestion, Pool/PoolText, reference splits, chunk pseudo-items
      assign.py    234  the p-matched assignment rule and its exact moments
      build.py     270  bootstrap the human base, inject, emit a CONVENTIONS-conformant Sample
      test_inject.py 411  41 checks

Run the tests with

    lane4-simulation/.venv/bin/python -m inject.test_inject

## 1. The design in one paragraph

A respondent `i` with persona label `L_i` who is a machine user gets a real machine text
drawn as: **with probability `p`**, uniformly from the pool's `L = L_i` cell (the *matched*
branch); **with probability `1 - p`**, from a *reweighted random* branch that ignores `L_i`.
The matched branch is what creates coupling between the trait score and the label; the random
branch is what dilutes it. Nothing is generated, nothing is edited: `p` selects **which real
text goes to which respondent**, and that alone moves `c` from 0 to `c_pool` along a straight
line, holding `kappa` and `delta` fixed. That is (E67), and section 3 below proves it to
machine precision.

## 2. The reweighting hook (the substantive fix to Prop. 16, and the answer to Q12)

The memo's Prop. 16 draws the random branch **uniformly from the balanced pool**. As written
it needs *two* balance assumptions, and it silently has only one:

1. the pool is label-balanced, and
2. the respondent labels are label-balanced.

Q12 asked about (1). (2) is the one nobody wrote down, and it is the one that actually bites,
because respondent label balance is a property of the **human base** (PK essays), not of
anything lane 4 controls.

The fix is one line and it removes both assumptions. Let the random branch draw text `t` with
probability

    u_t = q_{L_t} / N_{L_t}

where `q_l` is the fraction of **respondents** with label `l` and `N_l` the number of **pool
texts** with label `l`. Then the random branch's label marginal equals the respondent label
marginal, and every text within a label cell is equally likely. Under this weighting the law
of the injected score, marginally over respondents, is

    P(text t) = p * q_{L_t}/N_{L_t} + (1 - p) * q_{L_t}/N_{L_t} = q_{L_t}/N_{L_t}

**free of `p`**. So `E[x]`, `Var(x)`, and hence `kappa` and `delta` are exactly invariant in
`p`, while `Cov(x, L*)` is exactly linear in `p`. `c(p) = p * c_pool` holds **exactly, for any
pool balance and any respondent balance**.

The naive alternatives both fail, and the module keeps them so the failure is demonstrable
rather than asserted. `random_branch_weights(pool, q1, mode)`:

| mode | random branch draws | E67 |
| --- | --- | --- |
| `"respondent_marginal"` (default) | `q_{L_t} / N_{L_t}` | **exact, always** |
| `"balanced"` | uniform within label, 50/50 across labels (memo as written) | exact only if respondents are balanced |
| `"pool"` | uniform over pool texts | exact only if the pool is balanced |

Section 3 tables C and E are those two failures, measured.

**Back to lane 1:** Prop. 16 should be restated with the `q_{L}/N_{L}` weighting and the
balance assumptions dropped. Nothing else in 3.2 changes; the coverage arithmetic and the
cross-fitting rule are untouched.

## 3. The numerical proof of (E67)

Not Monte Carlo. The assignment law is a finite mixture over a finite pool, so
`assignment_moments()` computes mean, variance, and `c` as arithmetic identities in the pool
scores. The errors below are floating-point noise, not sampling noise.

### A. balanced pool, balanced respondents  (pool balance 0.50, respondent q1 0.5, mode respondent_marginal)
| p | c(p) | p*c_pool | abs err | kappa | delta |
| --- | --- | --- | --- | --- | --- |
| 0.00 | +0.000000000000 | +0.000000000000 | 0.0e+00 | 0.981101456806 | -0.000000000000 |
| 0.25 | +0.134481691839 | +0.134481691839 | 0.0e+00 | 0.981101456806 | -0.000000000000 |
| 0.50 | +0.268963383678 | +0.268963383678 | 0.0e+00 | 0.981101456806 | -0.000000000000 |
| 0.75 | +0.403445075517 | +0.403445075517 | 0.0e+00 | 0.981101456806 | -0.000000000000 |
| 1.00 | +0.537926767356 | +0.537926767356 | 0.0e+00 | 0.981101456806 | -0.000000000000 |

### B. UNBALANCED pool, balanced respondents, hook on  (pool balance 0.80, respondent q1 0.5, mode respondent_marginal)
| p | c(p) | p*c_pool | abs err | kappa | delta |
| --- | --- | --- | --- | --- | --- |
| 0.00 | +0.000000000000 | +0.000000000000 | 0.0e+00 | 1.152920480851 | +0.415305260019 |
| 0.25 | +0.161159723224 | +0.161159723224 | 2.8e-17 | 1.152920480851 | +0.415305260019 |
| 0.50 | +0.322319446448 | +0.322319446448 | 5.6e-17 | 1.152920480851 | +0.415305260019 |
| 0.75 | +0.483479169672 | +0.483479169672 | 1.1e-16 | 1.152920480851 | +0.415305260019 |
| 1.00 | +0.644638892896 | +0.644638892896 | 0.0e+00 | 1.152920480851 | +0.415305260019 |

### C. UNBALANCED pool, naive uniform-over-texts random branch  (pool balance 0.80, respondent q1 0.5, mode pool)
| p | c(p) | p*c_pool | abs err | kappa | delta |
| --- | --- | --- | --- | --- | --- |
| 0.00 | +0.000000000000 | +0.000000000000 | 0.0e+00 | 1.004114381361 | +0.000000000000 |
| 0.25 | +0.167002775761 | +0.161159723224 | 5.8e-03 | 1.073655617296 | +0.103826315005 |
| 0.50 | +0.326783419652 | +0.322319446448 | 4.5e-03 | 1.121637045856 | +0.207652630010 |
| 0.75 | +0.484501810089 | +0.483479169672 | 1.0e-03 | 1.148058667041 | +0.311478945014 |
| 1.00 | +0.644638892896 | +0.644638892896 | 0.0e+00 | 1.152920480851 | +0.415305260019 |

### D. balanced pool, UNBALANCED respondents (q1=0.1), hook on  (pool balance 0.50, respondent q1 0.1, mode respondent_marginal)
| p | c(p) | p*c_pool | abs err | kappa | delta |
| --- | --- | --- | --- | --- | --- |
| 0.00 | +0.000000000000 | +0.000000000000 | 0.0e+00 | 0.791120548880 | +0.426255604950 |
| 0.25 | +0.089856612508 | +0.089856612508 | 0.0e+00 | 0.791120548880 | +0.426255604950 |
| 0.50 | +0.179713225016 | +0.179713225016 | 0.0e+00 | 0.791120548880 | +0.426255604950 |
| 0.75 | +0.269569837524 | +0.269569837524 | 5.6e-17 | 0.791120548880 | +0.426255604950 |
| 1.00 | +0.359426450033 | +0.359426450033 | 0.0e+00 | 0.791120548880 | +0.426255604950 |

### E. balanced pool, UNBALANCED respondents, memo-as-written branch  (pool balance 0.50, respondent q1 0.1, mode balanced)
| p | c(p) | p*c_pool | abs err | kappa | delta |
| --- | --- | --- | --- | --- | --- |
| 0.00 | +0.000000000000 | +0.000000000000 | 7.8e-34 | 0.981101456806 | -0.000000000000 |
| 0.25 | +0.081246914692 | +0.089856612508 | 8.6e-03 | 0.967673824966 | +0.106563901238 |
| 0.50 | +0.165615853503 | +0.179713225016 | 1.4e-02 | 0.931534463031 | +0.213127802475 |
| 0.75 | +0.256663598670 | +0.269569837524 | 1.3e-02 | 0.872683371002 | +0.319691703713 |
| 1.00 | +0.359426450033 | +0.359426450033 | 0.0e+00 | 0.791120548880 | +0.426255604950 |

Read across the tables:

* **A** is the memo's case, and it works.
* **B** is an unbalanced pool (80/20). With the hook, `c(p)` is exactly linear and `kappa`,
  `delta` do not move. The memo as written would not have covered this.
* **C** is the same pool with the naive uniform-over-texts random branch. `c(p)` bends away
  from the line by up to 5.8e-3, and worse, `kappa` slides from 1.004 to 1.153 and `delta`
  from 0 to 0.415 **as a function of `p`**. That is fatal for the design: sweeping `p` would
  be sweeping three parameters at once, and any attenuation curve read off it would be
  uninterpretable.
* **D** is the case nobody wrote down: a balanced pool with respondents at `q1 = 0.1`. With
  the hook, exact.
* **E** is that same case with the memo's balanced random branch. `c(p)` is off the line by up
  to 1.4e-2 and `kappa` drifts 0.981 -> 0.791 across the sweep. **This is the one that would
  have shipped**, because the PersonaLLM pools are balanced by construction and it is easy to
  assume that settles it. It does not: the PK human base is not balanced on any trait.

One thing the tables show that is *not* a defect: the **level** of `kappa` and `delta` differs
between A and D. Reweighting to the respondent marginal changes which pool texts are typical,
so it changes the machine score distribution. That is correct and intended. E67 requires
`kappa` and `delta` to be **constant in `p`**, not constant across designs, and the Layer B
pilot reports the realized `(kappa, delta)` at whatever `q1` the base has.

## 4. What `c_pool` means (two different numbers, both exposed)

Under respondent-marginal weighting the `p = 1` endpoint the design actually realizes is the
**label-marginal-reweighted** coupling, not `Cor(x, L)` computed on the pool as it sits. On a
balanced pool the two coincide exactly; on an unbalanced pool they do not:

    balanced pool:    reweighted 0.460234   raw 0.460234    (identical)
    80/20 pool:       reweighted 0.5740     raw 0.4888

Both are available: `pool_coupling(pool, q1)` is the design's endpoint, `raw_pool_coupling(pool)`
is lane 3's `c-hat`. **The paper reports `pool_coupling` at the realized `q1`**, because that
is the coupling the injected sample actually has, and it is the number the attenuation curve
is indexed by. Lane 3's raw `c-hat` belongs in the pool-measurement table as a property of the
corpus. They must not be conflated in a caption.

## 5. Normalization: Layer B is not Layer A

| | Layer A (`CONVENTIONS.md`) | Layer B (`inject/`) |
| --- | --- | --- |
| `theta` | latent, `Var(theta) = 1` by fiat | `theta := L*`, the standardized persona label, observed |
| human loading on `theta` | exactly 1 | `r_H = Cor(x_H, theta)`, **measured** |
| `rel_H` | a set parameter | measured; `r_H` plays the role of `sqrt(rel_H)` |
| standardizer | `V_H = 1 / rel_H` derived | scores divided by the **human base** `(mu, sd)`, so `mu_H = 0`, `V_H = 1` |

The two normalizations agree on every unit-free quantity (`c`, `g`, `kappa`, `delta`, `Att`,
`rho_H`) and differ only in the units of the raw score. `rho_H = rho_T * r_H` in Layer B is
exactly the Layer A `rho_H = rho_T * sqrt(rel_H)` with the measured quantity substituted for
the set one.

`g` is computed by (E66) as the **ratio of label mean differences**, `g = Cov(x_M, theta) /
Cov(x_H, theta)`, not via `g = c * sqrt(kappa / rel_H)`. The ratio is unit-free, needs no
`rel_H`, and survives Layer B's different normalization. The two forms were checked
algebraically consistent under the Layer A chain `V_H = 1/rel_H`.

## 6. (E7) holds on the injected design

**A first version of this check was vacuous, and the review caught it.** Comparing
`rho_H * Att` against the mixture correlation assembled from `(kappa, delta, g)` proves
nothing: once the human base sets `V_H = 1`, `Den` is *identically* `Var(x)` and
`Cov(x, w) = rho_H * N`, so both sides reduce to the same expression. That comparison passes
even when fed arbitrary, mutually inconsistent parameter values, so a bug in
`assignment_moments` would have sailed straight through it. It is kept, relabeled honestly as
an internal algebra self-consistency check, and it is no longer the evidence for (E7).

The real check is `exact_mixture_law()`. It rebuilds the joint distribution over
(respondent class x respondent label x pool text) **explicitly from the assignment rule**,
one probability per grid point, and computes `E[x]`, `Var(x)`, `Cov(x, theta)` as weighted
sums over that grid. It never touches `kappa`, `delta`, `g`, or `Att`. Across 18 `(pi, p)`
cells including the `pi = 0` and `pi = 1` corners, the two paths agree to **1.7e-16**.

This check has teeth, and the suite proves it rather than asserting it: corrupting
`assignment_moments` by 1% and re-running moves `rho_obs` by 5.4e-05 (via `kappa`) and
4.1e-04 (via `c`), against a 1e-13 tolerance and 1.7e-16 clean agreement. A defect eleven
orders of magnitude smaller than these would still fail the check.

Two code paths over the same law is still not an empirical test. The check against the actual
sampler is `test_moments_match_simulation`, which draws 20,000 respondents through
`assign_indices` and matches the analytic `rho_obs`, `kappa`, and `c` within Monte Carlo error.

Sanity anchors in the same check: `g` is exactly linear in `p` (E66 inherits E67), `kappa` and
`delta` are constant across the `p` sweep, and `pi = 0` gives `Att = 1` to 1e-14.

## 7. Disclosures the paper must carry

### 7a. The outcome `w` is synthetic. The texts and trait scores are not.

No corpus on file carries an outcome variable. The module constructs

    w_i = rho_T * theta_i + u_i,     Var(w) = 1,   so rho_T is set exactly

which is what the memo authorizes (3.2, "`w = b L_i + u_i`, or `w = L_i`"). The consequence is
precise and should be stated in the paper's own words: **Layer B establishes that real
machine-written text, injected at a realized `(g, kappa, delta)`, attenuates a
survey-outcome correlation by the predicted amount. It does not establish that any real
survey outcome behaves this way**, because no real outcome was involved. The realism Layer B
buys is in the contaminating text, not in the outcome.

### 7b. `delta`'s sign is defined inconsistently across the two binding documents

`CONVENTIONS.md` line 46: `delta = (mu_H - mu_M) / sqrt(V_H)`.
`design-pivot-memo.md` section 1: `delta = (mu_M - mu_H) / sqrt(V_H)`.

`Att` depends on `delta^2` only, so **no number anywhere moves**. The module follows
`CONVENTIONS.md`, which is lane 4's binding contract, and flags the disagreement here rather
than silently picking. Lane 1 should reconcile the two before the notation table is written.

### 7c. Detector `se` is measured, not set

`detector_flags()` puts the threshold at the human `sp` quantile, so `sp` is exact by
construction (realized 0.9899 against a 0.99 target in the test). `se` is then whatever the
detector achieves on the pool and is reported, never set. On same-genre text that number will
be low, and that is the boundary result memo 2.3 predicts rather than a bug in the module.
When the pools carry no detector scores the sample gets `F = NaN` and `flag` all-False, with
the reason recorded in `provenance["detector"]`.

## 8. The `pool_measurements.json` contract

**Corrected 2026-09-07, after lane 3 landed.** This section originally documented a schema
the loader was written against before lane 3 shipped. Lane 3's actual file is different in
three ways, and the speculative schema is kept below only so the difference is legible.

**Live reader: `load_lane3()` + `lane3_pool(name, trait)` in `pools.py`.** Lane 3's real
shape:

```json
{"meta": {"seed": 20260907, "ridge_alpha": 1.0, "kfolds": 5},
 "pk_human": {"n": 2467, "r_H": {"cEXT": {"r": 0.1596, "p": 1.5e-15}},
              "mu_H": {"cEXT": 0.0396}, "V_H": {"cEXT": 0.10127}},
 "labeled_pools": {"personallm_gpt-4-0613": {
     "n": 320, "detector_auc_vs_pk": 0.8359,
     "trait_stats": {"cEXT": {"mu_M": -0.1170, "s2_M": 0.08338, "kappa": 0.8233,
                              "delta": -0.4922, "chat_r": 0.4426, "r_H": 0.1596,
                              "g": 2.7725}}}},
 "unlabeled_pools": {"...": {}},
 "side_checks": {"a3_summary": {}, "spearman_brown_truncation": {}},
 "score_files": {"pk_human": "data/scores/pk_human.json", "...": "..."}}
```

Three differences from what this module was written against:

1. Top-level `pk_human` / `labeled_pools` / `unlabeled_pools`, not a single `pools` dict.
2. Traits are keyed `cEXT`, `cNEU`, ..., not `EXT`. `LANE3_TRAIT_KEY` maps between them.
3. **Per-text score files are column-shaped JSON, not rows**: `{"ids": [...], "labels":
   {"cEXT": [...]}, "cross_fitted_scores": {"cEXT": [...]}}` for `pk_human`, and
   `"trait_scores"` plus `"detector_p_machine"` for the pools. So `_read_rows`, `_pick`, and
   `pool_from_rows` do not apply to lane 3's files and `lane3_pool` reads the columns directly.

`normalize_measurements` / `load_pool` / `pool_from_rows` are kept for the row-shaped case
(they are what `synthetic_pool` and the test suite exercise), but **nothing in the Layer B
pilot goes through them**. The schema they accept is:

```json
{"pools": {"gpt-4-0613": {"kind": "machine", "traits": {
   "EXT": {"g": 1.21, "c_hat": 0.58, "kappa": 0.83, "scores_path": "...csv"}}}}}
```

with column aliases `text_id`/`id`/`file`/`path`, `score`/`trait_score`/`yhat`,
`label`/`persona`/`y`, `detector`/`detector_score`/`p_machine`, and `chunk_1`, `chunk_2`, ...

### 8a. Two numbers in lane 3's file that the pilot does not use as reported

- **`g = 2.7725` is a ratio of correlations, not of covariances.**
  `lane3-testbed/pool_measurement.py:245` computes `g = chat_r / r_H`. (E66) defines
  `g = Cov(x_M, theta) / Cov(x_H, theta)`, which in human-standardized units is
  `c * sqrt(kappa) / r_H = 2.5163`, because `Cov(x_M, theta) = c * sd_M` and `sd_M` is not 1.
  The most literal reading of (E66) settles it: the ratio of label-mean differences,
  `(m1 - m0)/(h1 - h0) = 2.5108`, agrees with the covariance form and not with lane 3's.
  Lane 3's `g` is high by the factor `1/sqrt(kappa) = 1.10`. **The pilot uses the covariance
  form and reports both.** This should go back to lane 3 as a correction.
- **`kappa`, `delta`, `chat_r` are whole-pool, `ddof=1`.** The pilot's are computed on the
  injection half after the held-out reference split, with `ddof=0` and the label-marginal
  reweighting of section 4, so they differ in the third digit. LAYERB-PILOT.md tabulates both.

## 9. Open dependency on lane 3: chunk-level scores

The weak-H2 rescue (memo 3.4) needs **per-chunk** trait scores to form parallel pseudo-items,
and the reliability/loading metrics need `k >= 2`. Lane 3's step-1 brief
(`prompts/lane3-p1step1.md`) does **not** ask for chunk-level scoring. Either lane 3 adds a
chunked scoring pass, or lane 4 needs the fitted trait model exported so it can score chunks
itself.

The module is written for both outcomes: `chunk_text()` and `chunk_pseudo_items(texts, k,
scorer)` will do the work given a scorer, the loader reads `chunk_1, chunk_2, ...` columns if
they appear, and `build_injected_sample(k_chunks=k)` **raises with a message naming this
dependency** rather than silently degrading. Until it is resolved, Layer B runs at `k = 1`:
every single-indicator closed form (E5)-(E9), (E34) works, and the between-item metrics do not.

Note also that between-chunk reliability is **not** whole-text reliability; Spearman-Brown
relates them (memo 2.4). The module keeps the whole-text score separately as
`InjectedSample.x_full` and never mixes it into the chunk columns, because a mixed column set
would corrupt `rel_hat` (the mean between-item correlation) and the implied loading.

## 10. Contract deviations, declared

**`inject/` is a package; `CONVENTIONS.md` "Style" says files stay flat in
`lane4-simulation/`.** The deliverable named `lane4-simulation/inject/` explicitly, and the
module is a coherent four-file unit with its own test suite. Per CONVENTIONS ("if a subagent
thinks the contract is wrong, it says so and does NOT unilaterally change it"), the exception
is declared rather than taken: **flat for Layer A, one package for Layer B**. A note recording
this has been appended to `CONVENTIONS.md`. Everything else in Style holds: numpy + scipy +
sklearn only, no pandas, no config framework, no plotting, type hints on public functions.

**Every `Cell` field that is a Layer A knob but a Layer B outcome is `NaN`:** `c`, `kappa`,
`rel_H`, `delta`, `rho_v`, `r_F`. They are Layer A *inputs*; in Layer B they are *outputs* of
the pool and the assignment, so writing a value into the Cell would make it look like a knob
that was set. This matters most for `rel_H` and `delta`, which have non-NaN dataclass defaults
(`0.7` and `0.0`): left alone they would have silently handed downstream code a fabricated
`rel_H = 0.7` and `delta = 0`, and `Cell.V_H` would have returned `1.4286` where Layer B's
answer is `1.0`. `arm="layerB"` marks the cell; the realized values live in
`InjectedSample.provenance` and in `layer_b_moments()`.

**`Cell.detector = "empirical"` is deliberately not one of `dgp.DETECTORS`.** Layer B's
detector operating point is measured, not chosen from the four-row table, so `Cell.se_sp`
raises a `KeyError` on a Layer B cell instead of returning an `(se, sp)` pair Layer B never
had. That is the intended behaviour and the test asserts it. It is a crude failure mode --
improving the message means editing `dgp.py`, which is off limits while the Layer A grid holds
that module.

**`Reference` gained a `text_ids` field** (default `()`, additive) so that the disjointness of
the held-out reference from the injection pool is *checkable* rather than merely constructed.
The test checks it.

## 11. Design choices worth knowing

* **Without-replacement exhaustion raises, never falls back.** Falling back to the other label
  cell would quietly change the label marginal and with it the realized `c` — the one quantity
  this design exists to control. `PoolCapacityError` carries the deficit and the memo's
  remedies (pool a second generator, lower `pi`, or `replace=True`).
* **Machine status is assigned independently of `theta`**, preserving A1. Exactly
  `round(n * pi)` slots are filled via a random permutation rather than Bernoulli draws, so
  SPEC cells hit `pi` exactly instead of within sampling noise.
* **The human base is bootstrapped with replacement** from the PK essays, so `n` can exceed
  the corpus and `theta` is standardized on the drawn sample (mean 0, variance 1 exactly).
* **`assign_indices` takes the FULL sample's `q1`,** not the machine subsample's own label
  marginal. The two agree only asymptotically, and the gap is widest exactly where pilot cells
  live (small `pi`, so few machine respondents). Since `theta` is standardized by the full
  sample's `q1`, the assignment law and `layer_b_moments()` would otherwise be describing two
  different populations. `q1` is now an explicit parameter with the subsample marginal as a
  fallback default.
* **`scorer` is injected into `chunk_pseudo_items`** rather than imported, because the fitted
  trait model lives in lane 3.

## 12. Test results

41 checks, all passing. Full output:

```

--- test_e67_exact_balanced
[PASS] E67 c(p) = p * c_pool exactly (balanced pool)  max err 1.11e-16
[PASS] E67 kappa invariant in p (balanced pool)  max err 1.11e-16
[PASS] E67 delta invariant in p (balanced pool)  max err 4.86e-17

--- test_e67_monte_carlo
[PASS] E67 holds in Monte Carlo within 5 MCSE  worst |c_hat - p*c_pool| 0.0034

--- test_unbalanced_pool
[PASS] E67 exact on an UNBALANCED pool with the reweighting hook  max err 0.00e+00, pool balance 0.80
[PASS] naive 'pool' mode DOES break E67 (so the hook is necessary, not cosmetic)  max |c(p) - p*c_pool| 0.0026, kappa spread 0.0835

--- test_unbalanced_respondents
[PASS] E67 exact with UNBALANCED respondent labels (hook)  max err 2.22e-16, q1=0.1
[PASS] memo-as-written 'balanced' branch breaks under respondent imbalance  max |c(p) - p*c_pool| 0.0646

--- test_replacement_and_capacity
[PASS] without-replacement agrees with with-replacement within MC error  0.2741 vs 0.2228
[PASS] exhausting a label cell raises PoolCapacityError, no silent fallback  pool 'tiny' label cell 0: expected demand 140.0 exceeds 20 available texts at p=

--- test_chunk_text
[PASS] chunk_text partitions into k non-empty chunks losslessly  k in 1,2,3,4,7
[PASS] chunk_text refuses a text too short for k chunks (no empty pseudo-items)  text has 2 words, cannot make 5 chunks

--- test_reference_splits
[PASS] held-out reference is disjoint from the injection pool  90 injected / 210 reference
[PASS] transfer reference accepts a different pool  other_gen:transfer
[PASS] transfer reference REFUSES the pool being injected from

--- test_sample_contract
[PASS] injected Sample matches the CONVENTIONS field/shape/dtype contract  X(800, 1) Auint8 flagbool
[PASS] Layer B Cell NaNs every field that is a Layer A knob but a Layer B outcome  c/kappa/rel_H/delta/rho_v/r_F all NaN
[PASS] Cell.se_sp raises on a Layer B cell rather than returning a set (se, sp)  detector='empirical'
[PASS] headline indicator X[:, 0] is the whole-text score
[PASS] exactly round(n*pi) machine respondents  40 of 800
[PASS] theta is standardized on the drawn sample (mean 0, var 1)
[PASS] machine status is independent of theta (A1): |Cor(A, theta)| small
[PASS] machine respondents carry machine-pool text ids
[PASS] detector threshold hits the target specificity by construction  realized sp 0.9899, se 0.1711
[PASS] k_chunks=4 produces 4 pseudo-item columns
[PASS] k_chunks>1 without chunk scores fails loudly (lane 3 dependency)

--- test_loader_contract
[PASS] missing pool_measurements.json fails with a locatable message  lane 3 measurements not found at lane3-testbed/pool_measurements.json. This is e
[PASS] normalize_measurements accepts the documented shape
[PASS] an unrecognized shape raises PoolContractError naming the keys seen
[PASS] PersonaLLM filename tokens decode to trait labels

--- test_e7_layer_b
[PASS] E7 rho_obs = rho_H * Att matches the independently enumerated law  max |Att path - enumerated| 1.67e-16 over 18 (pi, p) cells
[PASS] that comparison is NOT vacuous: a 1% error in kappa or c breaks it  kappa 5.4e-05, c 4.1e-04 vs clean 1.7e-16 (tol 1e-13)
[PASS] the internal Att algebra is self-consistent (Den == Var(x))  max 2.78e-17 -- an identity, not a design check
[PASS] g is linear in p (E66 inherits E67)  g(0)=-0.0000 g(.5)=0.8090 g(1)=1.6181
[PASS] kappa and delta do not move with p  kappa=1.1184 delta=-0.0663
[PASS] pi = 0 recovers Att = 1 exactly

--- test_moments_match_simulation
[PASS] simulated rho_obs matches the exact Layer B prediction  sim 0.1740 vs exact 0.1843
[PASS] simulated kappa matches the exact prediction  sim 1.4452 vs exact 1.4423
[PASS] simulated coupling matches p * c_pool  sim 0.3150 vs exact 0.2989

--- test_c_pool_definitions
[PASS] on a BALANCED pool the design's c_pool equals lane 3's raw c-hat  0.460234 vs 0.460234
[PASS] on an UNBALANCED pool they DIFFER (INJECT.md says which goes in the paper)  reweighted 0.5740 vs raw 0.4888

41/41 checks passed
```

## 13. What runs next

1. Lane 3 lands `pool_measurements.json` + per-text score files.
2. Point `load_pool()` at them, run the Layer B **pilot cell** at one `(pool, trait, pi, p)`
   to confirm the realized `(c, kappa, delta, g)` match `layer_b_moments()` on real scores.
3. Sweep `p` and read the attenuation curve against (E7).
4. Resolve the chunk-scoring dependency (section 9) before anything needs `k >= 2`.

Blocking issues for lane 1: the Prop. 16 restatement (section 2) and the `delta` sign
reconciliation (section 7b).

INJECT-DONE
