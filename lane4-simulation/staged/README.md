# Staged, not applied

Edits that are correct but that could not land while the Layer A full grid was in flight.
The grid's workers import `estimators.py` at runtime (`grid.py:188` does the import inside
`run_cell`), `run_grid_full.py:372` runs a `multiprocessing.Pool` with no `maxtasksperchild`,
and a respawned worker on macOS re-imports from disk. So a default changed here mid-run would
apply to some cells and not others.

## estimators-n_bins.patch

`_distribution_match_pi`'s `n_bins` default, 60 -> 8. Rationale, evidence and the honest
caveats are in `../SPEC-FIXES-ROUND3.md` (fix 2).

Apply once `results/grid/grid.jsonl` has all 372 cells and the run has exited:

    git apply lane4-simulation/staged/estimators-n_bins.patch   # from the repo root
    lane4-simulation/.venv/bin/python lane4-simulation/test_estimators.py

`test_estimators.py` section 6 passes in both states: its two behavioural checks pass
`n_bins` explicitly, and the third accepts a shipped default of either 60 (pre-patch) or 8
(post-patch), so applying the patch is visible in the test output rather than silent.

Applying it invalidates comparability with any `labelfree`/`distribution_match` number
produced before it, the completed grid included. Re-run, or label the two eras.
