# Lane 1, day 1: mixture formalization and zero-coupling closed forms

Status: day-1 draft, self-checked by re-derivation, pending verification passes 1 to 3 (SPEC section 7). Nothing here ships until those pass.

Conventions. ASCII math throughout so Astra's line-by-line diff (pass 1) is mechanical. Display equations are numbered (E1), (E2), ... and each was re-derived once from scratch before being written. Every symbol is defined in section 0 before use. "Prop." marks a claim with a proof in this file; "Claim (day 2)" marks a statement whose proof is deferred.

---

## 0. Notation

Population: respondents i = 1..n, index suppressed. Everything below is a population (n = infinity) statement; sampling error is lane 4's business.

Latent and outcome:
- theta: latent trait, E[theta] = 0 (location is immaterial for correlations), Var(theta) = s2_T.
- w = b * theta + u: outcome. u is independent of everything else, Var(u) = s2_u. V_w := Var(w) = b^2 s2_T + s2_u.
- rho_T := Cor(theta, w) = b sqrt(s2_T / V_w). The trait-level validity coefficient.

Authorship:
- A in {H, M}, unobserved. pi := P(A = M).
- Assumption A1 (ignorable authorship): A is independent of (theta, u, e, v). Section 4b relaxes this.

Human process (A = H):
- x = mu_H + theta + e, e independent of (theta, u, A), Var(e) = s2_H. SPEC 1.2 writes x = theta + e with no intercept; mu_H is added so the mean gap mu_H - mu_M of SPEC 1.4 has a definition. Setting mu_H = 0 recovers SPEC's form.
- V_H := Var(x | H) = s2_T + s2_H.
- rel_H := s2_T / V_H, the single-indicator human reliability.
- rho_H := Cor(x, w | H) = b s2_T / sqrt(V_H V_w) = sqrt(rel_H) * rho_T. This is the clean-sample observed validity: what the naive estimator targets in an uncontaminated sample, and the primary estimand in SPEC 1.3. Bias is measured against rho_H; results against rho_T follow by dividing by sqrt(rel_H).

Machine process (A = M):
- x = mu_M + m, Var(m) = s2_M, and the coupling c := Cor(x, theta | M) = Cor(m, theta).
- Second-moment representation (exact for correlations, no distributional assumption needed): m = lambda_M * theta + v, where lambda_M := c * sqrt(s2_M / s2_T), v independent of (theta, u, e, A), Var(v) = (1 - c^2) s2_M. Check: Cov(m, theta) = lambda_M s2_T = c sqrt(s2_M s2_T), so Cor(m, theta) = c; Var(m) = lambda_M^2 s2_T + (1 - c^2) s2_M = c^2 s2_M + (1 - c^2) s2_M = s2_M.
- Assumption A2: the machine residual v is independent of the outcome noise u (the LLM does not see the outcome).

Standardized parameters (everything downstream is a function of these five plus rho_T where Var(w) matters):
- pi: contamination fraction.
- c: coupling.
- rel_H: human reliability.
- kappa := s2_M / V_H, the machine-to-human observed-variance ratio. Homogenization in SPEC's sense (s2_M < s2_H) is kappa < 1 - rel_H; the weaker condition kappa < 1 (machine scores less dispersed than human scores) is what most results below actually need, and both are stated where they differ.
- delta := (mu_H - mu_M) / sqrt(V_H), the mean gap in human observed-score SD units. Delta := mu_H - mu_M is the unstandardized gap.
- g := lambda_M = c * sqrt(kappa / rel_H). The machine slope on theta. Derivation: sqrt(s2_M / s2_T) = sqrt(kappa V_H / (rel_H V_H)) = sqrt(kappa / rel_H).

Standard normal density and distribution function: phi, Phi (section 6 only).

Two shorthand polynomials in pi that recur everywhere:

    N(pi, c) := (1 - pi) + pi * g                                   (E0a)
    Den(pi)    := (1 - pi) + pi * kappa + pi (1 - pi) delta^2          (E0b)

N is the covariance multiplier, Den the variance multiplier. Den does not depend on c.

Note on SPEC 1.4 wording. SPEC says the machine covariance term is "c times the human-scale covariance". Under SPEC's own definition c = Cor(x, theta | M), the exact factor is g = c sqrt(s2_M / s2_T), not c. The two coincide only when s2_M = s2_T (kappa = rel_H). This file keeps c as the correlation (SPEC 1.2 definition) and carries the scale factor explicitly in g. Logged in lane1-open-questions.md as notation decision N1; lane 4 must use the same convention.

---

## 1. The two-process mixture (SPEC 1.1 to 1.2)

The observed score is a two-component mixture:

    x = (1 - 1{A = M}) (mu_H + theta + e) + 1{A = M} (mu_M + lambda_M theta + v)      (E1)

with theta, e, v, u mutually independent and independent of A under A1 and A2. The three c regimes of SPEC 1.2 are: c = 0 (lambda_M = 0, x | M = mu_M + v carries no trait signal), 0 < c < 1 (diluted signal, lambda_M in (0, sqrt(s2_M / s2_T))), c = 1 (v degenerate, x | M = mu_M + sqrt(s2_M / s2_T) theta, a rescaled trait).

Remark on c = 1. SPEC 1.2 calls this regime "nearly harmless". Props. 4 and 5 below show it is not: when rel_H < 1, c = 1 is exactly harmless for no (kappa, delta). The pooled correlation equals rho_H at every pi only for the human-replica machine, kappa = 1, delta = 0, c = sqrt(rel_H) (day-2 (E54)). At c = 1, kappa = rel_H, delta = 0 the machine score is mu_M + theta with no measurement error, and Att = 1 / sqrt(1 - pi (1 - rel_H)) > 1 for every pi > 0 (1.015 at pi = 0.1 and 1.048 at pi = 0.3 with rel_H = 0.7). A faithful amanuensis biases the pooled correlation on every scale. Logged as Q3. [Correction 2026-09-07, pass 1 item D2: this remark originally read "true only when additionally kappa = rel_H (same scale as the human measurement) and delta = 0", which took the matched covariance ratio of the SPEC 1.4 verification below (g = 1 at c = 1, s2_M = s2_T) for harmlessness; a matched covariance with a smaller variance raises the correlation. Caught by Astra's blind rederivation and by lane 1 on day 2.]

---

## 2. Observed moments under A1

All three follow from (E1) by the law of total expectation, variance, and covariance over A ~ Bernoulli(pi).

Mean:

    E[x] = (1 - pi) mu_H + pi mu_M = mu_H - pi Delta                                   (E2)

Variance. E[Var(x | A)] = (1 - pi) V_H + pi s2_M. Var(E[x | A]) is the variance of a two-point variable taking mu_H w.p. 1 - pi and mu_M w.p. pi, which is pi (1 - pi) Delta^2. So

    Var(x) = (1 - pi) V_H + pi s2_M + pi (1 - pi) Delta^2 = V_H * Den(pi)                (E3)

Covariance with the outcome. Within-class: Cov(x, w | H) = Cov(theta + e, b theta + u) = b s2_T. Cov(x, w | M) = Cov(lambda_M theta + v, b theta + u) = lambda_M b s2_T (A2 kills Cov(v, u)). Between-class: Cov(E[x | A], E[w | A]) = 0 because E[w | A] = b E[theta | A] = 0 under A1. So

    Cov(x, w) = b s2_T [ (1 - pi) + pi g ] = b s2_T * N(pi, c)                          (E4)

Outcome variance: Var(w) = V_w, unchanged by contamination under A1 (the outcome is not machine-written; if it is, see Q4).

Verification of the SPEC 1.4 factor: Cov(x, w | M) / Cov(x, w | H) = lambda_M = g. At c = 1 and s2_M = s2_T this is 1, as it should be for a perfect same-scale copy of theta.

---

## 3. The naive validity coefficient and its bias

### 3.1 General c

Reminder: g and lambda_M are the same number (section 0); structural equations use lambda_M, standardized formulas use g.

    rho_obs := Cor(x, w) = b s2_T N / sqrt(V_H Den V_w) = rho_H * N(pi, c) / sqrt(Den(pi))    (E5)

Define the attenuation factor Att(pi, c) := rho_obs / rho_H = N / sqrt(Den). Then

    bias(rho_obs) := rho_obs - rho_H = rho_H * [ N(pi, c) / sqrt(Den(pi)) - 1 ]           (E6)

with N and Den from (E0). Written out in the five standardized parameters:

    Att(pi, c) = [ (1 - pi) + pi c sqrt(kappa / rel_H) ] / sqrt[ (1 - pi) + pi kappa + pi (1 - pi) delta^2 ]     (E7)

Boundary checks (all re-derived): pi = 0 gives A = 1. pi = 1 gives A = g / sqrt(kappa) = c / sqrt(rel_H), which matches the direct computation Cor(x, w | M) = c rho_T = (c / sqrt(rel_H)) rho_H. kappa = 1, delta = 0, c = 0 gives A = 1 - pi (pure dilution: machine noise with the same variance as human scores).

Relative to rho_T instead of rho_H: rho_obs / rho_T = sqrt(rel_H) Att(pi, c). The classical attenuation sqrt(rel_H) and the contamination factor Att multiply; they are separable, which matters for the correction (day 3).

### 3.2 Exact result at c = 0 (the day-1 target)

    Att_0(pi) := Att(pi, 0) = (1 - pi) / sqrt[ (1 - pi) + pi kappa + pi (1 - pi) delta^2 ]                  (E8)

    bias_0(rho_obs) = rho_H [ Att_0(pi) - 1 ]                                                                (E9)

Prop. 1 (sign and bounds at c = 0). For pi in (0, 1), rho_H > 0:

    0 < Att_0(pi) <= sqrt(1 - pi) < 1,                                                                       (E10)

with equality on the left inequality of the bound iff kappa = 0 and delta = 0. Hence contamination with zero coupling always attenuates and never flips sign, whatever the mean gap and whatever the homogenization.

Proof. Att_0^2 = (1 - pi)^2 / Den. Since Den = (1 - pi) + pi kappa + pi (1 - pi) delta^2 >= (1 - pi), Att_0^2 <= (1 - pi)^2 / (1 - pi) = 1 - pi, with equality iff pi kappa + pi (1 - pi) delta^2 = 0. Positivity: N = 1 - pi > 0 and Den > 0. QED.

Prop. 2 (direction relative to pure dilution). Compare with the pure-dilution benchmark 1 - pi (the answer one would guess from "pi of the covariance is gone"):

    Att_0(pi) > 1 - pi   iff   Den(pi) < 1   iff   kappa + (1 - pi) delta^2 < 1                              (E11)

Proof. Att_0 > 1 - pi iff (1 - pi) / sqrt(Den) > 1 - pi iff Den < 1 iff pi kappa + pi (1 - pi) delta^2 < pi. Divide by pi. QED.

This is the precise form of SPEC 1.4's sentence "reliability compression partially offsets dilution; net direction depends on the mean gap". The offset is relative to 1 - pi, not relative to zero: homogenization (kappa < 1) makes contamination less harmful than pure dilution, a mean gap makes it more harmful, and the crossover is the line kappa + (1 - pi) delta^2 = 1. The sign of the bias itself is always negative (Prop. 1). Logged as Q2 because the SPEC sentence can be misread as a sign claim.

Prop. 3 (monotonicity at c = 0, SPEC H1). Att_0(pi) is strictly decreasing on [0, 1) for every kappa >= 0, delta.

Proof. d/dpi log Att_0^2 = -2 / (1 - pi) - Den'(pi) / Den(pi), where Den'(pi) = kappa - 1 + (1 - 2 pi) delta^2. Put over the common denominator (1 - pi) Den > 0; the numerator is

    -2 Den - (1 - pi) Den'
    = -2 (1 - pi) - 2 pi kappa - 2 pi (1 - pi) delta^2 - (1 - pi)(kappa - 1) - (1 - pi)(1 - 2 pi) delta^2
    = -(1 - pi) - (1 + pi) kappa - (1 - pi) delta^2                                                        (E12)

(the delta^2 terms: -2 pi (1 - pi) - (1 - pi)(1 - 2 pi) = -(1 - pi)(2 pi + 1 - 2 pi) = -(1 - pi)). Every term in (E12) is <= 0 and the first is < 0. QED.

So H1 holds exactly at c = 0 with no restriction on the mean gap: the "small-mean-gap regime" qualifier in SPEC H1 is unnecessary at c = 0 under A1 (it becomes necessary once A1 is dropped, section 4b).

### 3.3 General c: monotonicity, inflation, and the amanuensis regime

The sign of dAtt/dpi is the sign of

    G(pi) := 2 (g - 1) Den(pi) - N(pi, c) Den'(pi)                                                             (E13)

(from d/dpi log Att = N'/N - Den'/(2D) with N' = g - 1, common denominator 2 N Den > 0 for c >= 0).

At delta = 0 this factorizes cleanly. With Den = (1 - pi) + pi kappa and Den' = kappa - 1:

    G(pi) = (1 - pi) (2 g - 1 - kappa) + pi [ g (1 + kappa) - 2 kappa ]                                    (E14)

Derivation: 2(g - 1)[(1 - pi) + pi kappa] - [(1 - pi) + pi g](kappa - 1) = (1 - pi)[2 g - 2 - kappa + 1] + pi [2 g kappa - 2 kappa - g kappa + g], and 2 g kappa - g kappa + g = g (1 + kappa).

Define the two slope thresholds

    g_1 := 2 kappa / (1 + kappa),      g_2 := (1 + kappa) / 2,      g_1 <= g_2 (AM-GM: (1 + kappa)^2 >= 4 kappa),     (E15)

and in c units, using c = g sqrt(rel_H / kappa):

    c_1 := 2 sqrt(kappa rel_H) / (1 + kappa),      c_2 := (1 + kappa) sqrt(rel_H) / (2 sqrt(kappa)).                (E16)

Prop. 4 (shape in pi at delta = 0). G is linear in pi with G(0) = 2 g - 1 - kappa and G(1) = g (1 + kappa) - 2 kappa. Therefore:
- c <= c_1 (g <= g_1): Att(pi, c) is decreasing in pi on [0, 1]. Naive validity attenuates monotonically. This contains the whole c = 0 case.
- c >= c_2 (g >= g_2): Att(pi, c) is increasing in pi on [0, 1]. Contamination inflates the naive validity above rho_H at every pi. This is the amanuensis regime: the machine score is a better measurement of theta than the human one.
- c_1 < c < c_2: A first decreases then increases (G changes sign once, from negative to positive), so the bias is non-monotone in pi with an interior minimum. H1's monotonicity claim fails in this band.

Consistency checks: at kappa = 1, c_1 = c_2 = sqrt(rel_H), i.e. c^2 = rel_H: the machine is exactly as reliable as the human measurement and Att(pi, c) = 1 for all pi (N = 1, Den = 1). At kappa < 1, c_1 < sqrt(rel_H) < c_2. Under SPEC's homogenization (kappa < 1 - rel_H) and rel_H = 0.7, kappa = 0.2 gives c_2 = 1.2 * 0.8367 / (2 * 0.4472) = 1.12 > 1: no coupling on [0, 1] inflates at small pi. On the SPEC grid (pi <= 0.30) the homogenized amanuensis attenuates because its covariance with w is scaled by sqrt(s2_M), not s2_T (see Remark on c = 1 in section 1); by Prop. 4 the band is U-shaped in pi at this cell (c = 1 < c_2 = 1.12 at kappa = 0.2, rel_H = 0.7), so Att crosses 1 at pi = 0.60 and inflates beyond it: 0.994, 0.987, 0.991, 1.016, 1.098 at pi = 0.1, 0.3, 0.5, 0.7, 0.9. [Qualified 2026-09-07, pass 1 item D3: the sentence originally carried no prevalence restriction.]

Prop. 5 (the inflation boundary, general delta). Att(pi, c) = 1 on the curve

    c*(pi) = sqrt(rel_H / kappa) * [ sqrt(Den(pi)) - (1 - pi) ] / pi                                        (E17)

with Att > 1 above it and Att < 1 below it (Att is increasing in c at fixed pi since N is). Limits: c*(0+) = sqrt(rel_H / kappa) (1 + kappa + delta^2) / 2, which reduces to c_2 at delta = 0; c*(1) = sqrt(rel_H) for every delta (pure machine sample matches rho_H iff c / sqrt(rel_H) = 1). The mean gap raises the boundary at small pi (the delta^2 term) and has no effect at pi = 1 (the pi (1 - pi) factor vanishes).

Proof of the limit at 0: sqrt(Den) = sqrt(1 + pi (kappa - 1 + delta^2) - pi^2 delta^2) = 1 + (pi / 2)(kappa - 1 + delta^2) + O(pi^2), so [sqrt(Den) - 1 + pi] / pi -> (kappa - 1 + delta^2) / 2 + 1 = (1 + kappa + delta^2) / 2.

Interpretation for the paper. Below c*(pi): contamination hides validity. Above it: contamination manufactures validity, which is the more insidious failure because the naive researcher sees a stronger result. Both are biases against rho_H.

---

## 4. Sign stability on the (pi, c) grid

### 4a. Under ignorable authorship (A1): sign-stable everywhere on c in [0, 1]

Prop. 6. Under A1 and A2, for every pi in [0, 1) and every c in [0, 1], sign(rho_obs) = sign(rho_H).

Proof. rho_obs = rho_H N / sqrt(Den) by (E5); Den > 0; N = (1 - pi) + pi g with g = c sqrt(kappa / rel_H) >= 0 for c >= 0, so N >= 1 - pi > 0. QED.

Sign flip under A1 needs c < 0 (anti-coupling: the LLM output moves against the respondent's trait), and then exactly when

    c < c_flip(pi) := -(1 - pi) / pi * sqrt(rel_H / kappa)                                                (E18)

which for the SPEC grid (pi <= 0.30) requires c < -2.33 sqrt(rel_H / kappa), impossible for a correlation unless kappa / rel_H > 5.4, i.e. s2_M > 5.4 s2_T, the opposite of homogenization. Conclusion: with SPEC's c grid {0, partial, high} and ignorable authorship, every cell is sign-stable. The grid map for naive rho_obs under A1 is a three-region map, not a two-region map:

| region on the (pi, c) plane | condition | naive estimate |
| --- | --- | --- |
| attenuation | 0 <= c < c*(pi) | same sign, too small |
| inflation | c*(pi) < c <= 1 | same sign, too large |
| sign flip | c < c_flip(pi) < 0 | impossible on the SPEC grid |

with c*(pi) from (E17) and c_flip from (E18). The attenuation region contains the entire c = 0 row (Prop. 1).

### 4b. The between-mean term: sign flips under non-ignorable authorship

SPEC section 8, failure mode 3, names a "between-mean term" among the mixture-specific results. Under A1 there is none in Cov(x, w), because E[w | A] does not vary with A. It appears as soon as authorship is associated with the trait, which is the realistic case (whoever pastes into an LLM is not a random draw on conscientiousness, anxiety, or language proficiency). This subsection derives it under the simplest non-ignorable model; it is the sign-flip mechanism the grid should contain.

Assumption A1' (location-shift selection): theta | H has mean 0 and variance s2_T; theta | M has mean Delta_theta and variance s2_T. All other independences as in A1 and A2. Write d_theta := Delta_theta / sqrt(s2_T). The machine process is centered on its own class: x | M = mu_M + lambda_M (theta - Delta_theta) + v, so mu_M is still E[x | M] and Delta = mu_H - mu_M is still the observed-score gap.

Moments. Within-class covariances are unchanged. E[w | H] = 0, E[w | M] = b Delta_theta. The between-class covariance is now nonzero:

    Cov(E[x | A], E[w | A]) = pi (1 - pi) (mu_M - mu_H)(b Delta_theta - 0) = -pi (1 - pi) b Delta Delta_theta

    Cov(x, w) = b s2_T N(pi, c) - pi (1 - pi) b Delta Delta_theta                                         (E19)
    Var(x)    = V_H Den(pi)                              (unchanged: class means and within-class variances unchanged)
    Var(w)    = V_w + pi (1 - pi) b^2 Delta_theta^2                                                       (E20)

Standardize: Delta Delta_theta / s2_T = delta sqrt(V_H) d_theta sqrt(s2_T) / s2_T = delta d_theta / sqrt(rel_H); b^2 Delta_theta^2 / V_w = rho_T^2 d_theta^2. Then

    Att'(pi, c) := rho_obs / rho_H = [ N(pi, c) - pi (1 - pi) delta d_theta / sqrt(rel_H) ] / sqrt[ Den(pi) (1 + pi (1 - pi) rho_T^2 d_theta^2) ]     (E21)

where rho_H is still the human-subpopulation validity (unchanged under A1' by construction). Setting d_theta = 0 recovers (E7).

Prop. 7 (sign-flip region under A1'). rho_obs has the opposite sign to rho_H iff

    (1 - pi) + pi c sqrt(kappa / rel_H) < pi (1 - pi) delta d_theta / sqrt(rel_H)                        (E22)

equivalently, for c >= 0, iff c < c_flip'(pi) with

    c_flip'(pi) = (1 - pi) sqrt(rel_H / kappa) [ delta d_theta / sqrt(rel_H) - 1 / pi ]                   (E23)

The region is nonempty on c >= 0 iff delta d_theta > sqrt(rel_H) / pi. On the SPEC grid the smallest requirement is at pi = 0.30: delta d_theta > 3.33 sqrt(rel_H) (about 2.8 at rel_H = 0.7), for example a 2-SD machine mean gap combined with LLM users sitting 1.4 trait-SD from non-users. At pi = 0.05 the requirement is delta d_theta > 20 sqrt(rel_H), which is not a realistic cell.

Proof. Sign of rho_obs is the sign of the numerator of (E21); the denominator is positive. Rearrange (E22) for c using g = c sqrt(kappa / rel_H). QED.

Mechanism. Machine answers are displaced on x (by -Delta) and the respondents who submit them are displaced on theta, hence on w (by b Delta_theta). If the two displacements have the same sign (machine scores run high and LLM users run high on the trait), the between-class term adds to the covariance; if opposite, it subtracts, and at high enough pi it dominates the within-class signal. This is Simpson's structure: both within-class correlations positive, pooled correlation negative. Coupling protects against it (larger c raises N).

Whether Layer A gets a non-ignorable arm is Q5 in lane1-open-questions.md. Section 6 shows that detect-and-delete manufactures exactly this A1' structure out of an A1 population, which is why 4b belongs in the paper even if the field disputes that LLM users differ on theta a priori.

---

## 5. Homogenization and between-item correlations (SPEC 1.4, H2)

Now k parallel indicators. The parallel-item restriction is for a clean statement; the general-loading covariance matrix is (E29).

Human: x_j = mu_H + theta + e_j, e_j iid with variance s2_H, j = 1..k. Cov(x_j, x_l | H) = s2_T and Cor(x_j, x_l | H) = rel_H for j != l.

Machine: x_j = mu_M + lambda_M theta + v_j, Var(v_j) = (1 - c^2) s2_M, Cor(v_j, v_l) = rho_v for j != l. rho_v is the shared machine-residual correlation (same session, same prompt style, same model voice across items). Then

    Cov(x_j, x_l | M) = lambda_M^2 s2_T + rho_v (1 - c^2) s2_M = s2_M [ c^2 + rho_v (1 - c^2) ] =: s2_M r_M      (E24)

and r_M = Cor(x_j, x_l | M) = c^2 + rho_v (1 - c^2).

### 5.1 Within machine cases

Prop. 8. Cor(x_j, x_l | M) > Cor(x_j, x_l | H) iff rho_v > (rel_H - c^2) / (1 - c^2); at c = 0, iff rho_v > rel_H. Homogenization (kappa) does not enter: within-class correlations are scale-free, so low machine variance by itself does not inflate the between-item correlation among machine cases. Inflation within M requires a shared machine residual.

Proof. Compare r_M with rel_H and solve for rho_v. QED.

### 5.2 Pooled (what the naive researcher computes)

By the same total-covariance argument as (E3), the between-class term for two items is pi (1 - pi) (mu_M - mu_H)^2 = pi (1 - pi) Delta^2:

    Cov(x_j, x_l) = (1 - pi) s2_T + pi s2_M r_M + pi (1 - pi) Delta^2                                     (E25)

    r_obs := Cor(x_j, x_l) = [ (1 - pi) rel_H + pi kappa r_M + pi (1 - pi) delta^2 ] / Den(pi)               (E26)

(E26) is a weighted average of three correlations: rel_H with weight (1 - pi), r_M with weight pi kappa, and 1 with weight pi (1 - pi) delta^2. The last is the point: the between-mean displacement acts on the item covariance matrix like a perfectly reliable common factor.

    r_obs - rel_H = pi [ kappa (r_M - rel_H) + (1 - pi) delta^2 (1 - rel_H) ] / Den(pi)                      (E27)

(Check: multiply rel_H by Den and subtract from the numerator of (E26): the (1 - pi) rel_H terms cancel, leaving pi kappa (r_M - rel_H) + pi (1 - pi) delta^2 (1 - rel_H).)

Prop. 9 (H2, the homogenization signature). Under A1 and A2 at c = 0:
(i) the trait-outcome correlation is strictly attenuated for every pi in (0, 1) (Prop. 1), and
(ii) the pooled between-item correlation exceeds the human one iff

    delta^2 > kappa rel_H / [ (1 - pi)(1 - rel_H) ]        (independent machine residuals, rho_v = 0)     (E28a)

    kappa (r_M - rel_H) + (1 - pi) delta^2 (1 - rel_H) > 0   (general rho_v)                              (E28b)

Both (i) and (ii) hold simultaneously exactly when (E28) holds. Homogenization enters through kappa: a smaller machine variance lowers the mean gap needed for inflation, because the machine cases then contribute almost nothing to within-class variance and their whole contribution to the item covariance is the between-mean term.

Proof. (i) is Prop. 1. (ii) is (E27) with the sign of the bracket, Den > 0. At rho_v = 0 and c = 0, r_M = 0 and the bracket is (1 - pi) delta^2 (1 - rel_H) - kappa rel_H. QED.

Worked scale (illustrative, for lane 4 to reproduce): with rel_H = 0.7, pi = 0.10, rho_v = 0, c = 0, the threshold gap is delta > sqrt(kappa * 0.7 / 0.27) = 1.61 sqrt(kappa) SD. At kappa = 1 (no homogenization) that is 1.61 SD; at kappa = 0.2 it is 0.72 SD.

Corollary (the reliability paradox). For parallel items, Cronbach's alpha is k r / (1 + (k - 1) r), increasing in r, so alpha_obs > alpha_H exactly under (E28) while the validity coefficient falls. A contaminated scale can look more reliable and less valid at the same time, and the gap widens with homogenization.

Prop. 10 (the asymmetry an estimator can use). Under A1, the between-mean term pi (1 - pi) Delta_vec Delta_vec^T enters every indicator covariance but not Cov(x_j, w) (E4), because the clean outcome has no authorship mean gap. For general loadings lambda_j (human), with Sigma_H and Sigma_M the k x k within-class item covariance matrices and Sigma_obs the pooled one,

    Sigma_obs = (1 - pi) Sigma_H + pi Sigma_M + pi (1 - pi) Delta_vec Delta_vec^T,      Cov(x, w) = b s2_T [ (1 - pi) lambda + pi lambda_M ]     (E29)

with Delta_vec the k-vector of item mean gaps (entries Delta_j = mu_Hj - mu_Mj), lambda the human loading vector, lambda_M the machine slope vector. The rank-one term is a spurious "authorship factor" with loadings sqrt(pi (1 - pi)) Delta_j. A one-factor fit to Sigma_obs absorbs it into the loadings (factor-loading bias, SPEC 1.3 secondary estimand; day 3), and the trait-outcome moments do not carry it. This asymmetry is what the label-free estimator (SPEC 3.2) has to exploit; it is noted here, not developed.

---

## 6. Deletion-selection (SPEC 1.5), day-1 portion

### 6.1 Residual contamination

Detector D in {flag, pass}. se := P(flag | M), sp := P(pass | H). By Bayes,

    pi' := P(M | pass) = (1 - se) pi / [ (1 - se) pi + sp (1 - pi) ]                                       (E30)

Check: se = 1 gives pi' = 0; se = 0, sp = 1 gives pi' = pi. At SPEC's out-of-domain operating point (se = sp = 0.85) and pi = 0.10: pi' = 0.015 / (0.015 + 0.765) = 0.019. It looks small. The survivor-sample attenuation from section 3 with pi replaced by pi' is then also small. That is the argument the rest of this section defeats.

### 6.2 The collider

Let F be writing fluency (or any text feature the detector uses), correlated with theta. The detector's human error rate depends on F: sp(f) := P(pass | H, F = f), increasing in f (non-native and low-fluency human text is flagged more). Structure:

    theta -> F -> D <- A,      theta -> x,  theta -> w

D is a collider between A and F. Under A1, A is independent of theta. Conditioning on D = pass opens the path A - D - F - theta, so among survivors A and theta are dependent: the survivor population satisfies A1' with Delta_theta != 0, not A1. That is the formal content of "deletion selects on theta".

Lemma 1 (selection on theta, distribution-free). Write s(theta) := P(pass | H, theta) = E[sp(F) | theta, H] and sp_bar := E[sp(F) | H] = P(pass | H), the marginal specificity (the same number as sp in 6.1; the bar marks it as the average of sp(f)). Then

    E[theta | H, pass] - E[theta | H] = Cov(theta, sp(F) | H) / sp_bar                                    (E31)

Proof. E[theta | H, pass] = E[theta 1{pass} | H] / P(pass | H) = E[theta s(theta) | H] / sp_bar = { E[theta | H] sp_bar + Cov(theta, s(theta) | H) } / sp_bar. Cov(theta, s(theta)) = Cov(theta, E[sp(F) | theta]) = Cov(theta, sp(F)) by the tower property. QED.

So passed humans have a shifted trait mean iff Cov(theta, sp(F) | H) != 0. If (theta, F) is bivariate normal with correlation r_F (the fluency-trait correlation, used again in 6.3) and sp is nondecreasing and nonconstant on the support of F, then Cov(theta, sp(F)) = Cov(E[theta | F], sp(F)) = r_F sqrt(s2_T) Cov(F, sp(F)) (F standardized), and Cov(F, sp(F)) > 0 for a nondecreasing nonconstant function of F (Chebyshev's association inequality). Hence the shift has the sign of r_F and vanishes only when fluency carries no trait information.

Lemma 1 concerns the mean. The bias in the validity coefficient comes from the variance, next.

### 6.3 Closed form under a Gaussian threshold detector

Model the detector as a threshold on standardized fluency: F = r_F theta / sqrt(s2_T) + sqrt(1 - r_F^2) eta, eta ~ N(0, 1) independent of everything, and pass iff F > tau. (A probit detector sp(f) = Phi((f - tau) / sigma), sigma > 0 the detector's own noise scale, is the same model with eta absorbing the detector's own noise and r_F rescaled; this loses no generality within the Gaussian family.) Marginal specificity sp_bar = 1 - Phi(tau), so tau = Phi^{-1}(1 - sp_bar).

Standard truncated-normal facts: with lambda := phi(tau) / (1 - Phi(tau)) = phi(tau) / sp_bar,

    E[F | F > tau] = lambda,      Var(F | F > tau) = 1 - psi,      psi := lambda (lambda - tau) in (0, 1).

Because theta = r_F sqrt(s2_T) F + sqrt(s2_T (1 - r_F^2)) eta' with eta' independent of F,

    E[theta | H, pass] = r_F sqrt(s2_T) lambda                                                            (E32)
    Var(theta | H, pass) = s2_T [ r_F^2 (1 - psi) + (1 - r_F^2) ] = s2_T q,      q := 1 - r_F^2 psi        (E33)

(E32) is Lemma 1 specialized. The measurement error e and the outcome noise u are independent of (theta, F), so they are untouched by selection, and among passed humans

    Cov(x, w | H, pass) = b s2_T q,   Var(x | H, pass) = s2_T q + s2_H,   Var(w | H, pass) = b^2 s2_T q + s2_u.

Dividing by the unrestricted quantities:

    rho_H,pass := Cor(x, w | H, pass) = rho_H * q / sqrt[ (1 - rel_H (1 - q)) (1 - rho_T^2 (1 - q)) ]      (E34)

Derivation of the denominator: (s2_T q + s2_H) / V_H = q rel_H + 1 - rel_H = 1 - rel_H (1 - q); (b^2 s2_T q + s2_u) / V_w = 1 - rho_T^2 (1 - q).

Prop. 11 (deletion bias at pi' = 0). rho_H,pass < rho_H whenever r_F != 0, sp_bar < 1, and (rel_H < 1 or rho_T^2 < 1), i.e. whenever fluency carries trait information, the detector deletes any humans at all, and the human measurement is not simultaneously perfectly reliable and perfectly valid (in that degenerate case rho_H,pass = rho_H = 1). [Third condition added 2026-09-07, pass 1 item D17.] The bias does not depend on pi, se, or the machine process: it is present at pi = 0 (a clean sample run through a detector) and at se = 1 (oracle sensitivity, pi' = 0).

Proof. Since 0 <= rel_H <= 1, 1 - rel_H (1 - q) >= q with equality iff rel_H = 1 or q = 1; likewise for rho_T^2. So the denominator of (E34) is >= q, hence the ratio is <= 1, strictly when q < 1 and (rel_H < 1 or rho_T^2 < 1), one strict factor being enough [corrected 2026-09-07, pass 1 item D17: the clause read "q < 1 and rel_H < 1", which misses strictness through the rho_T^2 factor]. q < 1 iff r_F != 0 and psi > 0; psi = lambda (lambda - tau) > 0 for every finite tau (lambda > max(tau, 0)), and tau is finite iff sp_bar < 1. QED.

This is indirect range restriction (Thorndike case III) induced by the detector: the detector is the third variable, fluency-correlated trait variance is what gets thrown away. The magnitude is governed by two numbers the field can measure, the human false-positive rate 1 - sp_bar and the fluency-trait correlation r_F:

| sp_bar | tau | lambda | psi | r_F | q | rho_H,pass / rho_H at rel_H = 0.7, rho_T = 0.5 |
| --- | --- | --- | --- | --- | --- | --- |
| 0.85 | -1.036 | 0.274 | 0.360 | 0.3 | 0.968 | 0.983 |
| 0.85 | -1.036 | 0.274 | 0.360 | 0.5 | 0.910 | 0.951 |
| 0.99 | -2.326 | 0.027 | 0.063 | 0.5 | 0.984 | 0.992 |

Hand-computed from (E34); lane 4 reproduces these before they appear in prose. Two readings: at the in-domain operating point (sp_bar = 0.99) the bias is under one percent; at the out-of-domain point the field actually faces it is 2 to 5 percent relative, comparable to the residual-contamination attenuation it was meant to remove. Whether that magnitude "kills detect-and-delete" on its own is Q6 in the open-questions file; the combination with 6.4 is where the larger effect is expected.

### 6.4 What the survivor sample looks like (structure only; proof day 2)

Open points for this subsection are Q8 (unequal within-class variances under general selection) and Q9 (non-Gaussian detectors) in lane1-open-questions.md.

Among survivors (D = pass):
- machine share pi' from (E30);
- human survivors: theta mean r_F sqrt(s2_T) lambda, variance s2_T q, from (E32) to (E33);
- machine survivors: if the detector's error on machine text does not depend on the respondent's theta (automatic at c = 0, where the machine text carries no theta; an assumption at c > 0), theta | M, pass has mean 0 and variance s2_T.

So the survivor population is an A1'-type mixture with an induced authorship-trait gap d_theta,pass = -r_F lambda (in trait-SD units) and, new relative to section 4b, unequal within-class trait variances (s2_T q for humans, s2_T for machines). The detector has manufactured the between-mean term of (E19) out of an ignorable population.

Claim (day 2). The survivor validity coefficient is

    rho_obs,pass = rho_H * Att''(pi', c; q, d_theta,pass)

where Att'' generalizes (E21) to unequal within-class trait variances. The sign-flip condition (E22) then applies with pi -> pi', d_theta -> -r_F lambda, delta -> the survivor mean gap, and the range-restricted human term q multiplying the human within-class covariance. Day 2 derives Att'' and shows that the combined bias (i) does not vanish as se -> 1, (ii) is not monotone in detector quality when sp_bar and se trade off along a ROC curve, and (iii) is exactly the section 4b sign-flip mechanism at high pi. The pieces still to be written: the unequal-variance generalization of (E19) to (E21), the survivor mean gap delta_pass (the machine mean is unaffected under the assumption above; the human mean is unaffected because e is independent of F), and the ROC trade-off statement.

---

## 7. Summary of what this file proves and what it hands off

Proven (population level, A1 and A2 unless stated):
- (E1): the mixture itself.
- (E2) to (E4): pooled mean, variance, and outcome covariance of the mixture.
- (E5) to (E7): naive validity as rho_H N / sqrt(Den); closed-form bias in (pi, c, rel_H, kappa, delta).
- (E8) to (E12), Props. 1 to 3: at c = 0, bias is negative for every pi in (0, 1), bounded by sqrt(1 - pi), never sign-flipping, monotone decreasing in pi, and better or worse than pure dilution according to kappa + (1 - pi) delta^2 versus 1.
- (E13) to (E17), Props. 4 and 5: at general c, three regimes in c (monotone attenuation, U-shaped, monotone inflation) with thresholds c_1, c_2, and the inflation boundary c*(pi).
- Prop. 6: sign-stable everywhere on the SPEC grid under A1.
- (E19) to (E23), Prop. 7: the between-mean term and the sign-flip region under non-ignorable authorship.
- (E24) to (E29), Props. 8 to 10: within-M and pooled between-item correlations; the homogenization signature (H2) as an exact condition; the reliability paradox; the rank-one authorship factor and its absence from the outcome covariance.
- (E30) to (E34), Lemma 1, Prop. 11: residual contamination; conditioning on D = pass selects on theta; closed-form deletion bias at pi' = 0 under a Gaussian threshold detector.

Handed to day 2: section 6.4's survivor-sample validity coefficient Att'' and the three claims under it.

Handed to lane 4 (pass 2 targets): every equation numbered above is a population moment Layer A can compute empirically. The three hand-computed rows in the section 6.3 table and the section 5.2 worked scale are the first numbers to reproduce.

Handed to lane1-open-questions.md: notation decisions N1 to N3 (c versus g, estimand, five inputs), questions Q1 to Q9. Q5 is raised in section 4b; Q8 and Q9 belong to the day-2 work in section 6.4.
