GHOST PROJECT - VERIFICATION PASS 1 (INDEPENDENT RE-DERIVATION) - ASTRA

You are Astra running verification pass 1 from SPEC section 7. Your job is an INDEPENDENT derivation of the zero-coupling mixture results, from the problem statement alone. The point of using a different model family is independence: correlated reasoning errors are the failure mode this pass exists to catch.

HARD RULES:
1. Read ONLY SPEC.md sections 1.1 through 1.5 and section 7 in this workspace. Do NOT open, read, list, or search the derivations/ directory, the lane1 tab, or any file whose name contains "lane1". Do NOT read lane1-open-questions.md. If any tool call would touch those, skip it.
2. Derive everything yourself. If you find a ambiguity in the SPEC, resolve it yourself and record the resolution explicitly in your deliverable.
3. Write no simulation or analysis code.

Deliverable: derivations/pass1-astra-rederivation.md, structured so it can be diffed line by line against another derivation of the same five items:
1. The two-process mixture formalization from SPEC 1.1-1.2, including coupling c = Cor(x, theta | M). State your notation and every assumption (e.g. what "clean outcome w" means, what is held fixed).
2. Observed-moment derivations and a closed form for bias(rho_obs) as a function of the mixture parameters. Exact result at c = 0 first, then general c. Define rho_obs and the target estimand precisely; if SPEC 1.1 (rho = Cor(theta, w)) and 1.3 (rho_H) conflict, pick one, say which, and carry both if cheap.
3. Conditions under which homogenization (s2_M < s2_H) inflates between-item correlations among machine cases while attenuating trait-outcome correlation.
4. The region of the (pi, c) grid where naive estimates are sign-stable versus sign-flipped.
5. Deletion-selection (SPEC 1.5): the residual-contamination expression for pi' and the conditioning argument for why detection-correlated-with-fluency biases the surviving human sample.

Self-check every display equation by re-deriving it once from scratch before writing it down. End the file with a section "Self-check log" listing each equation and how it was verified, and a final line DONE-PASS1-ASTRA.
