GHOST PROJECT - LANE 1 - PASS-1 CONDITION EDITS

The pass-1 diff (derivations/pass1-diff-report.md) came back CLEAN conditional on three edits. Apply all three now, exactly as specified there:

1. derivations/lane1-zero-coupling.md line 62 (item D2 in the diff report): the c = 1 harmlessness condition is wrong; the correct condition is kappa = 1, delta = 0, c = sqrt(rel_H). Your day-2 file already has this as E54 - port it back and note the correction inline (dated correction note, do not silently rewrite history).
2. Same file, line 169 (D3): qualify "the homogenized amanuensis attenuates" to the SPEC grid. Also fix Prop. 11's strictness condition (D17) to q < 1 and (rel_H < 1 or rho_T^2 < 1).
3. SPEC.md section 1.5 (D4): "unbiased only if detector errors are independent of theta" is false in both directions. Replace with the exact condition from the diff report (independence of S from (theta, w, x) given H for the whole law) and state your Prop. 11 under its parametric assumptions. Keep the edit minimal and dated.

Also: confirm your day-2 status - derivations/lane1-partial-coupling.md exists (42KB) but has no DONE-LANE1-DAY2 marker. If day-2 work is complete, append the marker plus the one-paragraph summary. If items are still open, finish them or log them in lane1-open-questions.md first.

Read derivations/pass1-diff-report.md sections 3 and 4 before editing so the context is exact. When done, reply with the list of edits applied (file + line) and end with DONE-LANE1-PASS1EDITS.
