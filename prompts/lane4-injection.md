GHOST PROJECT - LANE 4 - P1' STEP 2: INJECTION MODULE (user GO 7:19pm, design pivot approved)

The user approved P1' (assignment-coupled injection, zero generation). Read derivations/design-pivot-memo.md sections 1, 3.2, 8.2 first. The Layer A grid keeps running - do NOT disturb it; this build is code+tests only, no new grid load.

BUILD (memo 8.2 step 2): the Layer B injection module in lane4-simulation/ (new subdirectory inject/ or as fits CONVENTIONS.md):
1. Pool loader for the labeled machine pools (PersonaLLM 3 generators, Big5PersonalityEssays) reading lane3's saved per-text scores when they land (lane3 is producing pool_measurements.json + per-text score files now; code against that contract, tolerate its absence).
2. Assignment rules per Prop 16: random, matched (text label == respondent label), p-matched (match with probability p). Balanced-label assumption; reweighting hook for unbalanced pools (Q12).
3. Bootstrap of the PK base at SPEC n and pi cells; held-out and transfer references for the 3.2 estimator; chunk pseudo-items for the weak H2 rescue.
4. Unit tests on synthetic data proving c(p) = p*c_pool (E67) numerically, kappa/delta invariant to p.

Fable review after your pass (per memo: one round plus Fable review).

DELIVERABLE: lane4-simulation/inject/ module + INJECT.md (design notes, test results, the E67 numerical proof) ending with INJECT-DONE. Do not run the pilot cell yet - that waits for lane3's measurements.
