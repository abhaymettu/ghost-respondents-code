# Layer A full grid - progress

_Updated 2026-09-09 01:39:32 (local)._

**Status: COMPLETE - 372 / 372 cells done (100.0%).**

| field | value |
|---|---|
| config fingerprint | `080e38c51239da1a` |
| cells done / total | 372 / 372 |
| cells resumed (already done at launch) | 344 |
| workers | 10 (nice 10) |
| elapsed | 1:53:15 |
| remaining (cost-weighted) | 0:00:00 |
| **ETA** | **2026-09-09 01:39:32** |
| core-seconds consumed | 48,763 |

ETA is cost-weighted, not cell-count-weighted: n=5000 cells cost ~6x an n=500 cell, so a raw cells-done percentage would badly misreport the remaining time.

## Measured vs. projected per-rep cost

| n | projected s/rep | measured s/rep | cells measured | divergence |
|---|---|---|---|---|
| 500 | 1.051 | 1.362 | 5 | +29.6% |
| 1000 | 1.323 | 2.096 | 14 | +58.4% |
| 5000 | 6.360 | 6.819 | 9 | +7.2% |

**Per-fit runtime diverged more than 25% from the pilot extrapolation.** Per the launch brief this is recorded and the run continues; it changes no config and invalidates no result. It affects the ETA and the core-hour accounting only.

- n=1000: measured 2.340 s/rep vs projected 1.323 s/rep (+76.9%) over 3 cells. Run continues per the launch brief.
- n=500: measured 1.367 s/rep vs projected 1.051 s/rep (+30.1%) over 3 cells. Run continues per the launch brief.

## Failures

No cell raised. (Per-estimator non-convergence within a cell is a RESULT, recorded in each cell's `failure_rate`, not a failure here.)

## Outputs

- `results/grid/grid.jsonl` - one line per completed cell (resume index)
- `results/grid/cells/<cell_id>.json` - per-cell manifest
- `GRID-CONFIG.md` - frozen configuration


**Grid complete.** Pass 2 (numerical check of every closed-form moment against this output) may now run; it must not be started on a partial grid.

## Derived single-column re-run grids

Post-freeze re-runs of a single estimator column across the same 372-cell set (`run_grid_column.py`), used by `ESTIMATOR-FIX-REPORT.md`. Tracked here per grid since they resume/complete independently of the frozen grid above.

| grid | column | cells done / total | run log |
|---|---|---|---|
| `results/grid-labelfree-nbins8/` | labelfree @ n_bins=8 | 372/372 | `labelfree-nbins8-run.log` |
| `results/grid-bounds-c/` | bounds_c (H5) | 372/372 | n/a (~34s, no log kept) |
| `results/grid-simex-boot50/` | simex @ B_boot=50 | **372/372 -- COMPLETE** | `simex_boot50_run.log` ("col: COMPLETE 372/372 in 36376s") |
