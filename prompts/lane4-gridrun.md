GHOST PROJECT - LANE 4 - LAYER A FULL GRID LAUNCH

Pass 1 diff verdict is CLEAN (conditional edits are lane 1's, they do not touch your DGP). Pass 2 (numerical check of every closed-form moment against Layer A) is cleared to proceed, with two carried flags from the diff report: (BW1) use population moments rather than averaged sample correlations when checking the closed forms; (BW3) note the regime story assumes rho_vw = 0.

Launch the full Layer A grid now, in the background, sharded by cell across the machine's cores per SPEC 4.3 extended by lane 1's N3 (kappa in {0.2, 0.5, 1.0}) and Q7 (rho_v default arm 0, independent-calls). Constraints:
- Seeds frozen, config written to lane4-simulation/GRID-CONFIG.md before the first cell starts. No config change after start; any post-start change means a logged rerun.
- 500 reps per cell per SPEC 4.3. Leave at least 2 cores free (he uses this machine); nice the workers.
- Results land under lane4-simulation/results/ with per-cell manifests; a GRID-PROGRESS.md updated every ~30 min (cells done / total, ETA).
- If per-fit runtime in the real grid diverges >25% from the pilot extrapolation, note it in GRID-PROGRESS.md and keep going.
- This is CPU only. No LLM calls, no API keys, nothing spent.

When the grid is COMPLETE, run the pass-2 numerical check (every closed-form moment from derivations/lane1-zero-coupling.md and lane1-partial-coupling.md against grid output within Monte Carlo error, population moments per BW1) and write derivations/pass2-numerical-check.md ending DONE-PASS2 with a per-moment table. Do not start pass 2 on a partial grid. Reply progress only via the files; end your turn with GRID-LAUNCHED and the config path.
