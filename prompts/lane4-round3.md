# Lane 4 follow-on round (all $0, local CPU, nice -15; grid PID 8258 stays untouched)

From your own Part VI in LAYERB-SWEEP2.md. Three items, one deliverable:

1. EIV FAILURE ISOLATION: targeted run over the full 20 cells at pi in {0.10, 0.30}, scoring EIV error against g, c_pool, kappa, delta (and products). You estimated ~20 min. Identify what separates the 2 failing cells (gpt-4/EXT, gpt-3.5/AGR) from llama-2/OPE. If nothing separates them, say so plainly and narrow the candidates.
2. CALIBRATION-SPLIT SPREAD: characterize the adjusted-count offset across many random calibration splits (open from LAYERB-SWEEP.md s9 item 2). Part IV showed the offset is stable in pi; measure the split-to-split spread and state whether a usable between-wave change detector survives it.
3. DM-SLOPE DIAGNOSIS: the distribution-match estimator's slope runs 0.31-0.48 in 5 of 6 cells but 0.935 on llama-2/OPE. Find what makes OPE special and whether the slope is diagnosable/derivable.
Deliverable: lane4-simulation/LAYERB-ROUND3.md with numbers per item, end with marker line ROUND3-DONE. Run tests after any estimator edits. Repo is now git-initialized - commit your work locally with plain messages, no co-author trailers, no pushes.
