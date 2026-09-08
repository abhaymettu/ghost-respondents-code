# Layer A full grid - progress

_Updated 2026-09-08 00:17:05 (local)._

**Status: RUNNING - 74 / 372 cells done (19.9%).**

| field | value |
|---|---|
| config fingerprint | `080e38c51239da1a` |
| cells done / total | 74 / 372 |
| cells resumed (already done at launch) | 0 |
| workers | 10 (nice 10) |
| elapsed | 7:47:38 |
| remaining (cost-weighted) | 1 day, 9:25:19 |
| **ETA** | **2026-09-09 09:42:24** |
| core-seconds consumed | 260,518 |

ETA is cost-weighted, not cell-count-weighted: n=5000 cells cost ~6x an n=500 cell, so a raw cells-done percentage would badly misreport the remaining time.

## Measured vs. projected per-rep cost

| n | projected s/rep | measured s/rep | cells measured | divergence |
|---|---|---|---|---|
| 500 | 1.051 | 3.651 | 20 | +247.4% |
| 1000 | 1.323 | 5.556 | 41 | +320.0% |
| 5000 | 6.360 | 16.938 | 13 | +166.3% |

**Per-fit runtime diverged more than 25% from the pilot extrapolation.** Per the launch brief this is recorded and the run continues; it changes no config and invalidates no result. It affects the ETA and the core-hour accounting only.

- n=500: measured 3.294 s/rep vs projected 1.051 s/rep (+213.4%) over 3 cells. Run continues per the launch brief.
- n=1000: measured 5.021 s/rep vs projected 1.323 s/rep (+279.5%) over 3 cells. Run continues per the launch brief.
- n=5000: measured 21.808 s/rep vs projected 6.360 s/rep (+242.9%) over 3 cells. Run continues per the launch brief.

## Failures

No cell raised. (Per-estimator non-convergence within a cell is a RESULT, recorded in each cell's `failure_rate`, not a failure here.)

## Outputs

- `results/grid/grid.jsonl` - one line per completed cell (resume index)
- `results/grid/cells/<cell_id>.json` - per-cell manifest
- `GRID-CONFIG.md` - frozen configuration
