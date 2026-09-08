GHOST PROJECT - LANE 4 - LOADER FIX + FULL POOL x TRAIT SWEEP (P1' GO'd; LAYERB-PILOT.md section 8.4)

Two tasks, in order. Grid and dgp.py stay untouched.

1. LOADER FIX. lane3's chunk-scoring pass (POOL-MEASUREMENTS.md "Chunk scoring" section) confirmed a structural mismatch: pools.py expects one row per text (list-of-dicts or CSV) with per-trait columns, but lane3's data/scores/*.json are dict-of-arrays keyed by ids/trait_scores/detector_p_machine/chunk_1..4, one file per pool with all 5 traits together, and pool_measurements.json sets no scores_path. INJECT.md section 8 promised "one edit to _pick(), not a debugging session" - make pools.py parse lane3's ACTUAL shape (dict-of-arrays per pool, all traits, chunk_j dicts per trait). Add tests for the real files.

2. FULL SWEEP (after lane3's FIXES-DONE lands - it adds pk_human detector scores and the g correction; check for the FIXES-DONE marker in POOL-MEASUREMENTS.md before starting, and if it has not landed within a reasonable work session, do the loader fix and the sweep for everything EXCEPT the adjusted-count branch, then rerun that branch when it lands). Extend the pilot to all 4 labeled pools x all 5 traits at the same cell (pi=0.10, n=1000, p in {0,0.5,1}, 400 reps, rho_T=0.5, k_chunks=1, plus the adjusted-count prevalence branch once detector scores exist). Same PASS discipline and honest-power arithmetic per cell (per-cell r_H differs; report each cell's own numbers).

DELIVERABLE: lane4-simulation/LAYERB-SWEEP.md with the 20-cell table (g, kappa, delta, Att per arm, EIV recovery, pi-hat bias, detector route where scored) + LAYERB-PILOT.md updated or appended with the adjusted-count result; end with SWEEP-DONE.
