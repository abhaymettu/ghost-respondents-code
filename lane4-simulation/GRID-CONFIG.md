# Layer A full grid - frozen run configuration

**Config fingerprint: `080e38c51239da1a`**. Written before the first cell started. 
This file is the authority for the run; `run_grid_full.py` recomputes the fingerprint at every launch and refuses to start if it disagrees with the value recorded here.

## Reading of the launch brief

SPEC 4.3's cross, extended by lane 1's N3 (kappa in {0.2, 0.5, 1.0}) and Q7. Q7 is read as fixing rho_v = 0 (independent calls) as the DEFAULT level, and the run additionally carries the 12-cell rho_v = 0.5 sensitivity slice so Q7 is answered empirically rather than assumed. Those 12 cells cost ~2.2 core-hours out of ~116; omitting them and later wanting them would force a full logged rerun, which is the more expensive mistake.

The `nonignorable` arm (d_theta, A1' trait-mean shift) is EXCLUDED: it is gated on Abhay's Q5 call and was not named in the launch brief.

## Carried flags from the pass-1 diff report

- **(BW1)** The pass-2 numerical check compares closed forms against **population moments**, not against averaged sample correlations. `population.py` computes each moment as a pure function of the cell, and `metrics.summarize` inlines the full `population_moments(cell)` dict into every cell's row, so the check reads the population value directly rather than reconstructing it from replicate means. Where an empirical Monte Carlo mean is used, it is used only as the thing being TESTED, never as the reference.
- **(BW3)** The regime story assumes rho_vw = 0 (the machine-noise term is uncorrelated with the outcome w). Layer A's DGP imposes this: nothing in `dgp.py` induces a v-w covariance. The rho_v arm varies the between-ITEM correlation of the machine noise, which is a different parameter and does not relax rho_vw = 0. So every regime claim from this grid inherits the assumption; it is not tested here.

## Frozen parameters

| field | value |
|---|---|
| master_seed | 20260907 |
| reps per cell | 500 (SPEC 4.3) |
| arms | base, kappa, rho_v |
| cells (deduplicated) | 372 |
| cells by arm | base=216, kappa=144, rho_v=12 |
| cells by n | 500=72, 1000=228, 5000=72 |
| pi levels | 0.01, 0.02, 0.05, 0.10, 0.20, 0.30 |
| c levels | 0.0, 0.4, 0.9 |
| n levels | 500, 1000, 5000 |
| detector levels | none, calibrated, degraded, oracle |
| kappa levels | 0.2, 0.5, 1.0 (N3; reference 0.5) |
| rho_v levels | 0.0 default (Q7, independent calls), 0.5 sensitivity slice |
| estimators | naive, delete, simex, labelfree, em |
| total estimator-fits | 930,000 |

## Seeding

Per-(cell, rep) streams via `dgp.rep_rng(master_seed, cell, rep)`, which hashes `f"{cell.cell_id}:{rep}"` with SHA-256. `cell_id` is a hash of the full `Cell` dataclass including `arm`, so no two grid cells share a stream, and re-running any single cell reproduces it exactly. Estimator-internal RNGs (SIMEX's remeasurement draws, EM's bootstrap and multi-start) are spawned from that per-rep stream inside `grid.run_cell`, so they are frozen by the same seed.

## Execution

| field | value |
|---|---|
| workers | 10 (cpu_count 12 minus 2 left free) |
| nice level | 10 |
| BLAS threads per worker | 1 (OMP/OPENBLAS/MKL/NUMEXPR/VECLIB pinned) |
| shard unit | one cell (SPEC 6: fits are embarrassingly parallel) |
| resumable | yes, by cell_id present in results/grid/grid.jsonl |
| python | 3.12.13 |
| numpy / scipy / scikit-learn | 2.5.3 / 1.18.1 / 1.9.0 |
| platform | macOS-26.5.2-arm64-arm-64bit |
| started (local) | 2026-09-07 16:29:26 |

## Cost projection

Per-rep cost measured on this machine at 2 reps per n, (pi=0.10, c=0.4, detector=calibrated, kappa=0.5):

| n | measured s/rep | cells at this n | projected core-hours |
|---|---|---|---|
| 500 | 1.051 | 72 | 10.5 |
| 1000 | 1.323 | 228 | 41.9 |
| 5000 | 6.360 | 72 | 63.6 |
| **total** | | **372** | **116.0** |

Projected wall clock at 10 workers: **11.6 h**.

**This exceeds SPEC 6's ~60 core-hour budget (~116 vs ~60), and that is known at launch rather than discovered mid-run.** The pilot extrapolation in PILOT.md section (e) measured n=1000 only and projected 87 core-hours for the full arm set; the n=5000 cells cost 6.36 s/rep against that 1.32 s/rep anchor, which is where the extra ~29 core-hours come from. EM is the driver (~66% of its own cost is the parametric bootstrap, and EM is ~95% of grid cost). The run proceeds as briefed; the lever if it needs to come down later is EM's `B_boot`, which would be a config change and therefore a logged rerun.

## Rerun policy

No config change after the first cell starts. If any frozen parameter above changes -- seed, reps, arms, cell set, estimator list -- the fingerprint changes, this script refuses to launch against the old results directory, and the run must be restarted into a fresh directory with the change logged here. Resuming an interrupted run with an UNCHANGED fingerprint is not a config change and is expected: completed cells are skipped by cell_id.
