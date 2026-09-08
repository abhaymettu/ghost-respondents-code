# Lane 3 follow-on: out-of-fold chunk scores (highest-value dependency from lane 4 sweep 2)

Lane 4's LAYERB-SWEEP2.md Part III FAIL 1: your chunk scores are IN-SAMPLE. POOL-MEASUREMENTS.md ~line 225 records the five RidgeClassifiers behind chunk_1..chunk_k were "a refit, not a reload", refit on all texts then applied to chunks of their own training texts, while the whole-text scores are 5-fold cross-fitted. ~line 241 describes the chunk baseline as sitting on "a cross-fitted trait score", which line 225 rules out. The memo contradicts itself.

Task:
1. Re-derive ALL chunk scores (every pool with chunk_1..chunk_k, incl. pk_human) OUT-OF-FOLD, same 5-fold scheme as the whole-text scores. Export alongside the old ones (do not overwrite; suffix _oof).
2. Recompute the between-chunk correlations (rbar) and chunk-vs-whole correlations on the OOF scores; compare against the in-sample numbers lane 4 measured (chunk1/whole validity ratio 1.98-2.77x, mean-chunk vs whole 0.5908/0.5620/0.6766 EXT/AGR/OPE).
3. Fix the memo contradiction (~225 vs ~241) and record both score versions with their provenance.
4. Deliverable: lane3-testbed/CHUNK-REFIT.md with the before/after numbers and a verdict: does weak-H2 still fail on OOF scores, and by how much. End with marker line REFIT-DONE.
Constraints: local CPU, nice the compute, do not touch lane 4's files, no git pushes (repo just initialized; commit locally is fine, no co-author trailers).
