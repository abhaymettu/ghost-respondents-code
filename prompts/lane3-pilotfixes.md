GHOST PROJECT - LANE 3 - TWO FIXES FROM THE LAYER B PILOT (LAYERB-PILOT.md sections 1 and 5)

1. PK-HUMAN DETECTOR SCORES (pilot section 5). pool_measurement.py:253 ran roberta over pk_this_texts + pool texts but kept only the pool half. Save detector_p_machine for the PK humans too: add it to lane3-testbed/data/scores/pk_human.json (same key name the pool files use, aligned to ids). ~2,467 roberta CPU forward passes, 500 already cached if you kept them. This unblocks the adjusted-count prevalence branch (sp is a quantile of HUMAN detector scores).

2. g RECOMPUTE (pilot section 1). Your g column is chat_r / r_H, a ratio of correlations. (E66) is g = Cov(x_M, theta)/Cov(x_H, theta) = c * sqrt(kappa) / r_H - yours is high by exactly 1/sqrt(kappa) (2.7725 vs 2.5163 for personallm_gpt-4 EXT whole-pool). Recompute the g column in POOL-MEASUREMENTS.md and pool_measurements.json with the covariance form, add a one-line method note saying which form is reported. The label-mean-difference form (m1-m0)/(h1-h0) agrees with the covariance form to 6 digits (pilot verified), use either.

DELIVERABLE: update POOL-MEASUREMENTS.md (append a short "Pilot fixes" section noting both) and the JSON/score files; end with FIXES-DONE.
