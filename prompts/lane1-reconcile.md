GHOST PROJECT - LANE 1 - TWO BLOCKERS FROM THE INJECTION MODULE (P1' GO'd 7:19pm)

lane4 finished step 2 (lane4-simulation/INJECT.md, 41/41 tests, INJECT-DONE). Two items are explicitly blocking on you:

1. PROP 16 RESTATEMENT (INJECT.md section 2). The reweighting hook: random branch draws text t with probability u_t = q_{L_t}/N_{L_t} (respondent label marginal over pool cell size). This makes c(p) = p*c_pool EXACT for any pool balance AND any respondent balance - the memo as written silently assumed respondent balance (the PK base is NOT balanced on any trait; table E shows the memo-as-written branch bending c(p) off the line by 1.4e-2 and kappa drifting 0.981->0.791 across the p sweep). Restate Prop 16 in derivations/lane1-partial-coupling.md (or a dated addendum in the design-pivot memo) with the hook and both balance assumptions dropped; note the consequence in INJECT.md section 4 (reweighted c_pool vs raw c-hat are different numbers on unbalanced pools; the paper reports the reweighted one at the realized q1; do not conflate in captions).

2. DELTA SIGN (INJECT.md 7b). CONVENTIONS.md line 46: delta = (mu_H - mu_M)/sqrt(V_H). design-pivot-memo.md section 1: delta = (mu_M - mu_H)/sqrt(V_H). Att depends on delta^2 only so no number moves, but reconcile the two documents and state which convention is binding before the notation table is written.

DELIVERABLE: dated addendum covering both, in the appropriate derivations file(s), ending with DONE-RECONCILE.
