GHOST PROJECT - LANE 1 (DERIVATION) - DAY 1 KICKOFF

Read SPEC.md in this workspace first (sections 1 and 7 especially). You are lane 1, the derivation lane and the project critical path. Fable 5.1 Ultra effort; use Sonnet subagents (never Fable subagents) for algebra expansion passes and the notation audit. Do the derivation structure yourself.

Deliverable today: derivations/lane1-zero-coupling.md with full algebra and clean notation:
1. The two-process mixture formalization from SPEC sections 1.1-1.2, including the coupling parameter c = Cor(x, theta | M).
2. Observed-moment derivations and a closed form for bias(rho_obs) as a function of (pi, c, rel_H, mean gap). Exact result at c = 0 first, then the general-c expression.
3. The conditions under which homogenization (s2_M < s2_H) inflates between-item correlations among machine cases while attenuating trait-outcome correlation.
4. The region of the (pi, c) grid where naive estimates are sign-stable versus sign-flipped.
5. Start section 1.5 (deletion-selection): the residual-contamination expression for pi-prime and the collider setup showing conditioning on D = pass selects on theta when detector errors correlate with fluency. The full proof can carry into day 2.

Rules: self-check every display equation by re-deriving it once from scratch before writing it down. Do NOT write simulation or analysis code; the numerical check is lane 4 reproducing your moments (SPEC section 7 pass 2), and lane 4 does not exist yet. Log anything unresolved in derivations/lane1-open-questions.md. When the file is in place and self-checked, end your turn with DONE-LANE1-DAY1 and a one-paragraph summary of what is proven versus still open.
