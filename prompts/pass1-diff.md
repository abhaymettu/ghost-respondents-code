GHOST PROJECT - VERIFICATION PASS 1 - LINE-BY-LINE DIFF (REVIEW LANE)

Read SPEC.md section 7 first. Two independent derivations of the zero-coupling mixture results now exist:
- derivations/lane1-zero-coupling.md (lane 1, Fable 5.1)
- derivations/pass1-astra-rederivation.md (Astra, GPT family, derived without seeing lane 1)

Your job: the line-by-line diff SPEC section 7 requires. This is the human-pace element. Do not skim. You are a reviewer, not an advocate for either side; correlated-confirmation is the failure mode, so check every disagreement by re-deriving it yourself from the definitions before ruling.

For EVERY place the two derivations disagree (equations, conditions, constants, sign claims, regime boundaries, deletion-selection claims):
1. Quote both versions.
2. Re-derive the point yourself from first principles and state which is right, or whether both are right under different conventions, or whether the SPEC is ambiguous at that point.
3. Classify: LANE1-ERROR / ASTRA-ERROR / CONVENTION-ONLY / SPEC-AMBIGUITY / BOTH-VALID.
Also check for contamination tells: if Astra reproduces lane1's idiosyncratic notation choices (the g = c sqrt(kappa/rel_H) form, the name kappa, c_2, A1/A1' labels) verbatim, that suggests it saw lane1's work despite instructions - flag any such tell in a CONTAMINATION CHECK section.
Also note places where they AGREE but you find both wrong (re-derive; agreement is not proof).

Pay specific attention to (Astra's own summary claims corrections on): covariance scaling under coupling c, the sign-flip conditions, and the deletion "only if" claim.

Deliverable: derivations/pass1-diff-report.md with: a table of every discrepancy with its classification and your re-derived verdict; the contamination check; a list of any both-wrong agreements; and a final verdict section: CLEAN (no unresolved substantive discrepancy) or BLOCKED (list each unresolved item). End with DONE-PASS1-DIFF and a one-paragraph summary. Unresolved substantive discrepancies block the preprint per SPEC 7 - say so explicitly if any exist.
