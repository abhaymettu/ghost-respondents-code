GHOST PROJECT - LANE 4 - POST-SWEEP ROUND (all $0, local compute; grid and dgp.py untouched)

Three stale notes in LAYERB-SWEEP.md to correct, then the next compute round.

STALE 1 (section 7): pk_human chunk scores EXIST. Verified just now: lane3-testbed/data/scores/pk_human.json carries chunk_1..chunk_4 with 2,421 non-null entries plus chunk_meta (lane3's CHUNKS-DONE pass). The "blocked on lane 3" claim is wrong - the multi-item dependency is RESOLVED. Correct the note and proceed.

STALE 2 (section 7): the delta sign is RULED. lane1's memo 9.2 (DONE-RECONCILE): day-1 orientation delta := (mu_H - mu_M)/sqrt(V_H) is binding and matches CONVENTIONS.md; the memo is corrected. No numbers move (Att uses delta^2). Close the note.

STALE 3 (N2): the estimand call is DECIDED (2026-09-07): observed-score headline rho_H := Cor(x, w | H), latent as robustness. lane1's addendum (lane1-partial-coupling.md section 8, DONE-N2) lists two lane-4-owned wording updates: CONVENTIONS.md line 30 still calls rho_H the "N2 recommendation" and README.md lines 37-40 still say the call is open. Update both to the decided state with today's date. SPEC.md 1.1/1.3 edits are explicitly Abhay's call (Q3) - do NOT touch SPEC.md.

COMPUTE ROUND:
1. estimators.py guard: _adjusted_count_pi must guard denom <= tol (not abs(denom) < tol) and return (nan, False) when the detector does not separate. One comparison. The running grid (PID 8258) imported estimators.py into memory long ago, so the file edit cannot perturb it - verify that reasoning holds (process start time vs edit time) and note it in the commit message. Do not change any other behavior.
2. Multi-item arms UNBLOCKED: rerun the sweep's headline cells (or a representative subset - your call, justify it) at k_chunks=4 using the chunk scores: rel_H now identified, rho_T recoverable. Report rho_T recovery per cell-arm and the chunk-based between-item consistency vs the human baseline (r = 0.2083 on PK EXT) as the weak-H2 read.
3. (pi, n) expansion: sweep pi in {0.02, 0.05, 0.10, 0.20, 0.30} x n in {500, 1000, 2500} on the 4 machine-pool EXT cells plus the gpt-3.5/AGR and llama-2/OPE extremes (the largest swings), same PASS discipline. Minutes-scale per your own section 9 estimate.

DELIVERABLE: lane4-simulation/LAYERB-SWEEP2.md with the corrections noted and the new results, ending with SWEEP2-DONE.
