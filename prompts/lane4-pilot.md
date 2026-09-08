GHOST PROJECT - LANE 4 - LAYER B PILOT CELL (P1' GO'd 7:19pm; both dependencies landed)

lane3's POOL-MEASUREMENTS.md + pool_measurements.json + per-text scores are on disk (MEASURE-DONE). Your module is done (INJECT-DONE). Run the pilot cell from design-pivot-memo.md 8.2 step 3 NOW. Do NOT touch the Layer A grid or dgp.py.

CELL: trait EXT, pool personallm_gpt-4-0613, pi = 0.10, n = 1000, p in {0, 1} (plus p = 0.5 midpoint if cheap), human base = PK bootstrap. Use lane3's realized measurements (r_H 0.1596, c-hat 0.4426, kappa 0.823, delta -0.492 - note these differ from the memo's conditional kappa=0.5/delta=0 assumption; the pilot runs at REALIZED values). k_chunks=1 only (chunk dependency unresolved).

CHECK (same PASS discipline as PILOT.md): closed form (E7) at realized (g, kappa, delta) via layer_b_moments() vs the injected mixture over 100 replicates: rho_obs path, Att recovered per arm, the random-vs-matched contrast, estimator recovery for the 3.2 label-free prevalence estimator (held-out reference) and the EIV correction. Report realized (c, kappa, delta, g) vs predicted, the Att contrast vs (E7), and whether the contrast is resolvable at 100 reps given the MEASURED r_H (0.1596, lower than the memo's stale 0.245 - recompute the resolvability arithmetic honestly; if the EXT contrast is underpowered at n=1000, report the n or rep count that resolves it rather than claiming a pass).

DELIVERABLE: lane4-simulation/LAYERB-PILOT.md with the numbers and PASS/FAIL per the pilot discipline, ending with PILOTB-DONE.
