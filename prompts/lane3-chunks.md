GHOST PROJECT - LANE 3 - CHUNK-LEVEL SCORING PASS (P1' dependency, INJECT.md section 9)

lane4's injection module needs per-chunk trait scores for the weak-H2 rescue (parallel pseudo-items, k>=2). Your step-1 brief did not include chunk scoring. Add it now using the SAME fitted trait models and the same pools as pool_measurement.py: split each text into k chunks (k=4 default; sentence-boundary split per the memo's P2 verdict), score each chunk with the PK-trained full-refit RidgeClassifier per trait, and save chunk_1..chunk_k columns alongside the existing per-text files in lane3-testbed/data/scores/ (same file names, added columns; keep the existing columns untouched - lane4's loader reads them).

Also export the fitted trait models (the 5 RidgeClassifiers + the sentence-transformer reference) to lane3-testbed/data/models/ so lane4 can score chunks itself later if needed (INJECT.md section 9 allows either resolution; doing both is belt and suspenders since the export is cheap).

DELIVERABLE: append a "Chunk scoring" section to lane3-testbed/POOL-MEASUREMENTS.md (k, split rule, file paths, spot-check numbers: between-chunk correlation for PK-human on EXT as the human baseline), ending with CHUNKS-DONE.
