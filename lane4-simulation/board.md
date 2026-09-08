
## lane 4 - full Layer A grid LAUNCHED 2026-09-07 16:31
- Config frozen at `lane4-simulation/GRID-CONFIG.md`, fingerprint `080e38c51239da1a`, written before the first cell started. Launcher refuses to start against a config with a different fingerprint, so a post-start change forces a logged rerun rather than a silent mix.
- 372 cells = base 216 + kappa 144 + rho_v 12. `nonignorable` excluded, gated on Abhay's Q5. 500 reps/cell, master seed 20260907, 930,000 estimator-fits.
- 10 workers (12 cores minus 2 left free), nice 10, one BLAS thread per worker. Projected 116.0 core-hours / ~11.6 h wall.
- **Cost is ~2x SPEC 6's ~60 core-hour budget, known at launch.** The pilot measured n=1000 only (1.323 s/rep); n=5000 costs 6.360 s/rep and there are 72 such cells. EM's parametric bootstrap is the driver. Lowering `B_boot` would be a config change and therefore a logged rerun; not done.
- Live state in `lane4-simulation/GRID-PROGRESS.md` (~30 min refresh: cells done/total, cost-weighted ETA, measured vs projected s/rep per n, divergence notes, failures). Per-cell manifests in `results/grid/cells/<cell_id>.json`; resume index `results/grid/grid.jsonl`.
- Pass 2 is gated on the grid reading COMPLETE in GRID-PROGRESS.md. Both `derivations/lane1-zero-coupling.md` and `derivations/lane1-partial-coupling.md`; population moments per BW1 (verified: every cell row carries the full `population_moments(cell)` dict, exact to 1e-12 against recomputation); rho_vw = 0 assumption noted per BW3.
