# Round-3 spec fixes: frozen calibration split, and the distribution-match bin count

Both fixes come from `LAYERB-ROUND3.md` section 4 (points 6 and 8) and were approved for
implementation. Fix 1 is **applied**. Fix 2 is **staged, not applied**, because the Layer A
full grid was running while this was written; the staging and the reason are below.

---

## Fix 1 - one frozen calibration split, reused across waves and cells

### Evidence

`LAYERB-ROUND3.md` 1.2 (lines 88-135): across 400 splits per cell, **54% of the variance in
the per-cell EIV error is the split draw, not the cell**. The split explains more of the error
than the thing being measured. 2.3 (lines 268-308) is the operational consequence: with the
split re-drawn between waves the between-wave change detector carries an additive noise floor
of 0.06-0.27 and dies outright on weak-detector pools; with the split held fixed the same
change comes back with 18-40% relative error and the sign is never at risk. Source data:
`results/round3_splits.json`, produced by `round3_splits.py`.

### What was wrong, precisely

The arithmetic in `split_reference` was never the problem - the **seed** was. Every sweep did

```python
rng0 = np.random.default_rng(cell_seed)          # cell_seed = base + 1000 * cell_index
M_inj, M_ref = split_reference(M_all, rng0, frac=0.5)
H_base, H_ref = split_reference(H_all, rng0, frac=0.5)
```

which makes a cell's reference a function of **its position in a loop**. Insert a pool at the
top of `POOLS` and every later cell's reference silently moves; two scripts with different
seed bases hand the same cell different references; and the human split rides on an `rng0`
already partly consumed by the machine split, so it depends on which machine pool it was
paired with. None of that is a wave-invariant split.

### What changed

**`inject/pools.py`** - new block at lines 448-503, between `split_reference` and
`reference_detector` (`import hashlib` added at line 15). `split_reference` itself is
unchanged.

| line | added |
|---|---|
| 461 | `CALIBRATION_SEED = 20260908` - the frozen master seed |
| 466 | `calibration_stream(pool, seed=CALIBRATION_SEED)` -> `default_rng([seed, blake2s(pool.name)])` |
| 476 | `calibration_split(pool, frac=0.5, stratify=True, seed=CALIBRATION_SEED)` |
| 488 | `split_id(*refs)` - 16-hex blake2s over the sorted held-out `text_id`s |

The stream is keyed on `(master seed, pool.name)` and nothing else: not the cell index, not
the wave, not the rep. Two waves months apart, or two scripts with unrelated seed bases, land
on the identical held-out halves.

`split_id` hashes **what was actually held out**, not the seed that produced it, so a run
recorded under a different seed scheme is still comparable - equal ids mean the same texts.
That is what makes the split identity recoverable from the output, as the fix requires.

**`inject/__init__.py`** - `calibration_split`, `calibration_stream`, `split_id` added to the
`.pools` import block (lines 37-46) and to `__all__` (lines 55-59).

**Three call sites rewired**, each dropping `rng0` for `calibration_split` and recording the
split identity next to the seed in its output:

| file | split | recorded |
|---|---|---|
| `sweep_layerb.py` | 92-93 | `"split_id"` at 186 |
| `sweep_pin.py` | 60-61 (`cell_setup`) | `"split_id"` at 74 |
| `layerb_pilot.py` | 107-108 | `"split_id"` at 319 |

`cell_seed` / `SEED` are still used in all three for the Monte Carlo streams
(`sweep_layerb.py:138`, `layerb_pilot.py:200`, `sweep_pin.py:150-162`) and were not touched.

### Deliberately not changed

- **`round3_splits.py`** - varying the split *is* its experiment (`split_seeds` at 74-77, 400
  draws per cell). It keeps `split_reference` with a caller-supplied rng. The docstring of
  `calibration_split` names it as the exempt path so the next reader does not "fix" it.
- **`sweep_k4.py`** - it has no calibration split at all; its `_M_ref`/`_H_ref` are discarded
  and only the disjoint injection pool is used. Freezing it would move k4 results for nothing.
- **`estimators.py`, `grid.py`, `dgp.py`, `metrics.py`** - nothing in the Layer A grid's import
  graph imports `inject`, so fix 1 could not reach the live run (see grid safety, below).

### Side effect worth knowing

The human calibration split is now identical across all four machine pools for a given trait,
because it is derived from the human pool's own name rather than from a shared `rng0` that the
machine split had already advanced. That removes a nuisance source and makes "one shared split"
literally true on the human side. The split still differs per trait, because `split_reference`
stratifies on `pool.indices_by_label()` and only the labels differ between traits - `pool.name`
does not encode the trait.

### Consequence for published numbers

Re-running `sweep_layerb.py` now returns **different numbers from the split-0 tables in
`LAYERB-SWEEP2.md`**. They are not wrong; the old ones were one nuisance draw, which is exactly
what round 3 established. Nothing was re-run here: that would write under `results/`, which was
off limits during the grid.

### Tests

`inject/test_inject.py`, `test_frozen_calibration_split` (registered in `main()`), 8 checks:

- deterministic across repeated calls (held-out ids and injection ids both);
- unaffected by caller RNG state, by cell ordering, and by which pools were split first;
- **the old per-cell pattern really did move the reference** (198 of the human ids differ
  between sweep cell 0 and cell 1) - so the fix is not asserting something already true;
- the master seed is live (changing it re-draws);
- the stream is a function of `pool.name` and the seed alone;
- the held-out reference is still disjoint from the injection pool;
- `split_id` is equal iff the held-out ids are equal, order- and argument-position aware.

`.venv/bin/python -m inject.test_inject` -> **69/69 checks passed** (was 61).

---

## Fix 2 - `n_bins` default: 60 -> 8

### The value, and why 8

`LAYERB-ROUND3.md` 3.4 (lines 407-432) rejects 60 and puts the usable range at 8-15 but names
no single winner, so per the brief the choice is made here on the evidence. 3.4's own table is
a **7-cell subset** and reads 15 (3 wins) over 8 (2). Recomputed over **all 40 cell x split
rows** in `results/round3_dm.json` (20 lane-3 cells x 2 splits, ladder 8/15/30/60/120 from
`round3_dm.py:43`), it reverses:

| n_bins | mean slope | mean \|slope-1\| | median \|slope-1\| | frac slope>0.8 | closest-to-1 wins | mean intercept | MAE | RMSE | mean bias |
|---|---|---|---|---|---|---|---|---|---|
| **8** | **0.748** | **0.279** | **0.251** | **0.40** | **21/40** | **+0.0465** | 0.0643 | 0.0911 | +0.0128 |
| 15 | 0.688 | 0.329 | 0.335 | 0.33 | 11/40 | +0.0507 | 0.0647 | 0.0905 | +0.0089 |
| 30 | 0.584 | 0.422 | 0.430 | 0.23 | 3/40 | +0.0595 | 0.0631 | 0.0888 | +0.0037 |
| 60 | 0.494 | 0.508 | 0.588 | 0.23 | 4/40 | +0.0664 | 0.0639 | 0.0885 | -0.0014 |
| 120 | 0.386 | 0.614 | 0.708 | 0.15 | 1/40 | +0.0741 | 0.0666 | 0.0890 | -0.0082 |

8 wins every slope aggregate and the intercept. **Slope, not level, is the argument** - and the
argument is honest only if the rest is said too:

- **Level accuracy is flat across the whole ladder.** MAE 0.0631-0.0666 and RMSE 0.0885-0.0911
  end to end. Anyone reporting this fix as "the prevalence estimate got more accurate" is
  overselling it.
- **Mean bias actually worsens** at 8 (+0.0128) versus 60 (-0.0014). The bin count trades
  intercept against slope.
- **It is not uniform in pi.** At pi=0.10 finer bins win (MAE 0.0411 at 120 vs 0.0630 at 8); at
  pi=0.30 coarser wins (0.0779 at 8 vs 0.1118 at 120). 8 is the right default because it is
  right where the estimator is used, not everywhere.
- **8 is the floor of the tested ladder.** Nothing below it was measured, so 8 is the best value
  *available inside the evidence*, not a proven interior optimum. If someone extends the ladder
  down, this default is the first thing to re-check.

Why slope is the quantity to buy: fix 1's whole purpose is the between-wave change detector of
2.3. A fixed intercept cancels in a wave-to-wave difference; slope attenuation does not. The
two fixes are the same fix seen twice - freeze the split so a change is measurable, then stop
attenuating the change once it is.

### What is staged, and why

**`estimators.py` is not edited.** `staged/estimators-n_bins.patch` holds the one-line change
(`estimators.py:330`, `n_bins: int = 60` -> `8`, plus a three-line rationale comment), verified
with `git apply --check` to apply cleanly.

The reason is the live grid. `grid.py:188` does a **deferred** `from estimators import
ESTIMATORS` *inside* `run_cell`, so every worker imports `estimators.py` at runtime;
`labelfree` is one of the five live estimators and `estimators.py:400` calls
`_distribution_match_pi(x, machine_ref, human_ref_eff)` with **no explicit `n_bins`**, taking
the signature default. `run_grid_full.py:372` runs `multiprocessing.Pool(n_workers)` with
`imap_unordered(chunksize=1)` and no `maxtasksperchild`; Pool repopulates a dead worker and
macOS spawn re-imports from disk. A default changed mid-run could therefore apply to some of
the 372 cells and not others. That is precisely the brief's staging trigger.

`staged/README.md` carries the apply command and the caveat that applying it invalidates
comparability with every `distribution_match` number produced before it, the completed grid
included.

### Test

`test_estimators.py` section 6 (3 checks). Behavioural, not signature-based, so it passes both
before and after the patch lands: both slope checks pass `n_bins` explicitly, on a ~160-a-side
reference that mirrors the lane-3 geometry.

- `n_bins=8` tracks a change in prevalence better than 60: slope +0.812 vs +0.632;
- attenuation is monotone in the bin count over the 3.4 ladder:
  8:+0.812 > 15:+0.758 > 30:+0.713 > 60:+0.632 > 120:+0.427 - the same ordering the lane-3
  data shows, reproduced from scratch on synthetic references;
- the shipped default is one of the two states this document accounts for (60 pre-patch,
  8 post-patch), so applying the patch shows up in the test output rather than silently.

`.venv/bin/python test_estimators.py` -> **23/23 checks passed** (was 20).

---

## Grid safety

The Layer A full grid ran throughout. **No grid process was signalled, niced, paused or
restarted, and nothing under `results/` was written** - it was read only for liveness and for
the round-3 aggregates above.

Import-graph check, done before any edit: `run_grid_full -> dgp, grid`; `grid -> dgp, metrics`
plus the deferred `estimators`; `metrics -> population`; `estimators -> dgp, population`. Every
`import` line in those files, including indented and lazy ones, was grepped. **Nothing in the
grid's import graph imports `inject`**, which is why fix 1 was safe to apply live and fix 2 was
not.

Liveness at the end of this work (checked 2026-09-08 22:36:52): `results/grid/grid.jsonl` at
333 cells, last line written 22:21:07, and all **10 worker processes under pid 12744 above 50%
CPU** (93-95% at the 22:32 check). The 15-minute gap in the jsonl is the shape of the tail, not
a stall: at 500 reps per cell (`GRID-CONFIG.md`) and ~13.3 s/rep measured at n=5000, a tail cell
runs tens of minutes, so completions arrive in widely spaced bursts. Worker CPU is the liveness
evidence here, not the file mtime alone.

## Full suite after both changes

| suite | result |
|---|---|
| `python -m inject.test_inject` | 69/69 |
| `python test_estimators.py` | 23/23 |
| `python test_dgp.py` | all checks passed |
| `python test_population.py` | all checks passed |
