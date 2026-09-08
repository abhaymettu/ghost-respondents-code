# Lane 1, day 2: partial coupling, the survivor-sample result, and extensions

Status: day-2 draft, self-checked by re-derivation, pending verification passes 1 to 3 (SPEC section 7). Nothing here ships until those pass. Companion to lane1-zero-coupling.md (day 1), which is not modified.

Conventions. As in day 1: ASCII math, numbered display equations, each re-derived once from scratch before being written. Equation numbers continue from the day-1 file, (E35) onward, and propositions from Prop. 12, so a cross-file reference is never ambiguous for the pass-1 diff. Every symbol from day-1 section 0 is used with the same meaning; new symbols are defined at first use and collected in section 0 below. "Prop." marks a claim with a proof in this file.

---

## 0. Inherited notation and new symbols

Inherited without change (day-1, from section 0 or the body equation cited): theta, s2_T, w = b theta + u, V_w, rho_T, A, pi, A1, A2, mu_H, e, s2_H, V_H, rel_H, rho_H, mu_M, m, s2_M, c, lambda_M, v, kappa, delta, Delta, g, phi, Phi, N(pi, c) (E0a), Den(pi) (E0b), Att (E7), Att_0 (E8), G (E13), g_1, g_2, c_1, c_2 (E15, E16), c*(pi) (E17), A1', Delta_theta, d_theta, Att' (E21), se, sp, pi' (E30), F, r_F, tau, lambda, psi, q (E31 to E33), rho_H,pass (E34), rho_v (Prop. 8). N(pi, c) with two arguments and no tilde is the day-1 numerator function; "~ N(m, s2)" after a random variable is the normal distribution, as in day 1.

New in this file:
- S := 1 + kappa + delta^2. The small-pi curvature constant; S = 2 at kappa = 1, delta = 0.
- pi_min: location of the interior minimum of Att in the U-shaped band (E38).
- q_H, q_M: within-class trait variance ratios, Var(theta | A) = s2_T q_A, reference s2_T = the day-1 human trait variance. a_H, a_M: within-class trait means in trait-SD units, E[theta | A] = sqrt(s2_T) a_A. d_theta = a_M - a_H as in day 1.
- m_H, m_M: within-class observed means E[x | A]. Delta_obs := m_H - m_M, delta_obs := Delta_obs / sqrt(V_H). Under A1 and A1', delta_obs = delta.
- N'', Den'', W'': the three moment multipliers of the unequal-variance mixture (E40 to E42); Att'' their ratio (E43).
- A3: detector error on machine text is independent of the respondent's theta (section 3).
- d': detector discriminability, the gap between the human and machine detector-score means in human-score SD units (section 3.3).
- Subscript "pass" on any symbol: its value in the survivor sample (D = pass).
- Section 2.4 only: g_struct, the structural machine slope on theta; kappa_eff, c_eff, g_eff, the realized within-class values under option B (E46).
- Section 5 only: y, the text-scored outcome item; mu_wH, mu_wM, s2_wM, c_w, lambda_w, v_w, kappa_w, delta_w, Delta_w, g_w, rho_vw, A4, N_2, N_w, R, Den_w, Att_2.

Operating points. SPEC 4.3 and the NORC range in SPEC section 2: "calibrated" is read as se = sp = 0.99 (in-domain), "degraded" as se = sp = 0.85 (out-of-domain), "oracle" as se = sp = 1. A fourth point, se = 1 with sp = 0.85, is used below to separate the two error channels; it is not on the SPEC grid.

---

## 1. Partial coupling: the final c parameterization and the general-c closed forms

### 1.1 The machine process, final form (N1)

The machine branch of (E1), restated as the equation lane 4 codes:

    x | M = mu_M + lambda_M theta + v,   lambda_M = c sqrt(s2_M / s2_T) = c sqrt(kappa / rel_H) = g,   Var(v) = (1 - c^2) s2_M,   v independent of (theta, u, e, A)     (E35)

Re-derivation of the two identities it must satisfy. Cor(x, theta | M) = lambda_M s2_T / sqrt(s2_M s2_T) = c sqrt(s2_M / s2_T) sqrt(s2_T / s2_M) = c. Var(x | M) = lambda_M^2 s2_T + (1 - c^2) s2_M = c^2 s2_M + (1 - c^2) s2_M = s2_M. The scale identity: sqrt(s2_M / s2_T) = sqrt(kappa V_H / (rel_H V_H)) = sqrt(kappa / rel_H). So c is the SPEC 1.2 correlation and g is the covariance multiplier of SPEC 1.4, and they coincide iff kappa = rel_H. This is final; N1 closes with this section and the handoff block (section 6) repeats (E35) with the parameter map.

Under A1' and in section 2 the machine branch is centered on its own class, x | M = mu_M + lambda_M (theta - E[theta | M]) + v, so that E[x | M] = mu_M always; under A1 the two forms agree.

### 1.2 What day 1 already proved at general c

(E5) to (E7): rho_obs = rho_H Att(pi, c), Att = N / sqrt(Den). (E13) to (E16), Prop. 4: at delta = 0 the sign of dAtt/dpi is the sign of a function G linear in pi, giving three regimes in c with thresholds c_1 < c_2. (E17), Prop. 5: the inflation boundary c*(pi) at general delta. Prop. 6: sign stability on c in [0, 1]. What is new below: the affine structure in c, the general-delta regimes, the location of the interior minimum, and the first-order bias.

### 1.3 Att is affine in c at fixed pi

From (E0a), N(pi, c) = (1 - pi) + pi c sqrt(kappa / rel_H), and Den does not depend on c, so

    Att(pi, c) = Att_0(pi) + c * pi sqrt(kappa / rel_H) / sqrt(Den(pi))                                          (E36)

with Att_0 from (E8). Two consequences. (a) At every pi the naive validity is smallest at c = 0 and largest at c = 1; the zero-coupling row of the grid is the worst case for attenuation and the c = 1 row the worst case for inflation. (b) The slope in c, pi sqrt(kappa / rel_H) / sqrt(Den), is increasing in kappa: coupling matters more when the machine scores are more dispersed, because the machine covariance with w scales with sqrt(s2_M) (day-1 section 1, remark on c = 1).

### 1.4 The three regimes at general delta

Re-derive G(pi) from (E13) with the full Den. Den(pi) = (1 - pi) + pi kappa + pi (1 - pi) delta^2 and Den'(pi) = kappa - 1 + (1 - 2 pi) delta^2. The delta-free part of G is (E14). The delta^2 part is

    2 (g - 1) pi (1 - pi) delta^2 - [ (1 - pi) + pi g ] (1 - 2 pi) delta^2
    = delta^2 { (1 - pi) [ 2 pi (g - 1) - (1 - 2 pi) ] - pi g (1 - 2 pi) }
    = delta^2 { (1 - pi)(2 pi g - 1) - pi g (1 - 2 pi) }
    = delta^2 { 2 pi g - 1 - 2 pi^2 g + pi - pi g + 2 pi^2 g }
    = delta^2 [ pi (1 + g) - 1 ].

The pi^2 terms cancel, so G stays linear in pi for every delta:

    G(pi) = (1 - pi) (2 g - 1 - kappa) + pi [ g (1 + kappa) - 2 kappa ] + delta^2 [ pi (1 + g) - 1 ]           (E37)

with endpoints G(0) = 2 g - S and G(1) = g S - 2 kappa, S = 1 + kappa + delta^2. Numerical check of (E37) against (E13) directly: kappa = 0.5, g = 0.7, delta = 1, pi = 0.3 gives Den = 1.06, Den' = -0.1, N = 0.91, so (E13) is 2(-0.3)(1.06) - 0.91(-0.1) = -0.545; (E37) is 0.7(-0.1) + 0.3(0.05) + (0.51 - 1) = -0.545.

Prop. 12 (regimes at general delta). Define

    g_1(delta) := 2 kappa / S,     g_2(delta) := S / 2,     c_1(delta) := 2 sqrt(kappa rel_H) / S,     c_2(delta) := S sqrt(rel_H) / (2 sqrt(kappa)).

Then g_1(delta) <= g_2(delta) for every delta (S^2 >= (1 + kappa)^2 >= 4 kappa), and Prop. 4 holds verbatim with c_1, c_2 replaced by c_1(delta), c_2(delta): Att is decreasing in pi on [0, 1] for c <= c_1(delta), increasing for c >= c_2(delta), and U-shaped between. The mean gap widens the U-shaped band on both sides: c_1(delta) decreases and c_2(delta) increases in delta^2. In the band the minimum is at

    pi_min = (S - 2 g) / [ S (1 + g) - 2 (g + kappa) ]                                                             (E38)

Proof. G is linear (E37), so G(pi) = (1 - pi) G(0) + pi G(1), and its sign pattern on [0, 1] is set by the signs of G(0) = 2 g - S and G(1) = g S - 2 kappa: both nonpositive iff g <= min(S/2, 2 kappa / S) = 2 kappa / S (the smaller of the two by the AM-GM step); both nonnegative iff g >= S / 2; otherwise G(0) < 0 < G(1) and the root is pi_min = G(0) / (G(0) - G(1)) = (2 g - S) / (2 g - S - g S + 2 kappa), which is (E38) after multiplying numerator and denominator by -1. Convert to c with c = g sqrt(rel_H / kappa). QED.

Check of (E38): kappa = 0.2, delta = 0, rel_H = 0.7, c = 1 (g = 0.5345, S = 1.2, inside the band since c_1 = 0.624 < 1 < c_2 = 1.122) gives pi_min = (1.2 - 1.0690) / (1.2 * 1.5345 - 2 * 0.7345) = 0.1310 / 0.3724 = 0.352. Direct evaluation of (E7): Att(0.30, 1) = 0.9869, Att(0.35, 1) = 0.9865, Att(0.40, 1) = 0.9869. The minimum sits between the grid's pi = 0.30 and the next value, so on the SPEC grid this cell reads as monotone attenuation even though it is in the U-shaped band; lane 4 should not read a monotone grid column as evidence for regime I.

### 1.5 First-order bias in pi

Expand (E7) at small pi: N = 1 + pi (g - 1) and sqrt(Den) = 1 + (pi / 2)(kappa - 1 + delta^2) + O(pi^2), so

    Att(pi, c) = 1 + pi [ g - g_2(delta) ] + O(pi^2),     bias(rho_obs) = pi rho_H sqrt(kappa / rel_H) [ c - c_2(delta) ] + O(pi^2)              (E39)

Re-derivation: the pi coefficient is (g - 1) from N minus (kappa - 1 + delta^2) / 2 from sqrt(Den), and (g - 1) - (kappa - 1 + delta^2) / 2 = g - (1 + kappa + delta^2) / 2 = g - S / 2. Checks: c = 0, kappa = 1, delta = 0 gives -pi rho_H (pure dilution); c = 1, kappa = 1, delta = 0, rel_H = 0.7 gives +0.195 pi rho_H, and at pi = 0.10 the exact table value below is 1.020 because Den = 1 makes (E36) exactly linear there. (E39) is the single sentence version of the whole (pi, c) map: to first order the naive validity moves in the direction of c - c_2(delta), at a rate set by pi sqrt(kappa / rel_H).

### 1.6 Hand-computed values for lane 4 (rel_H = 0.7, delta = 0; Att from (E7))

Thresholds at delta = 0: c_1 = 0.624, 0.789, 0.837 and c_2 = 1.122, 0.887, 0.837 for kappa = 0.2, 0.5, 1.0.

| pi | kappa | c = 0 | c = 0.5 | c = 0.9 | c = 1 |
| --- | --- | --- | --- | --- | --- |
| 0.10 | 0.2 | 0.938 | 0.966 | 0.988 | 0.994 |
| 0.10 | 0.5 | 0.923 | 0.967 | 1.001 | 1.010 |
| 0.10 | 1.0 | 0.900 | 0.960 | 1.008 | 1.020 |
| 0.30 | 0.2 | 0.803 | 0.895 | 0.969 | 0.987 |
| 0.30 | 0.5 | 0.759 | 0.897 | 1.007 | 1.034 |
| 0.30 | 1.0 | 0.700 | 0.879 | 1.023 | 1.059 |

Reading: at kappa = 0.2 no column reaches 1 (c_2 = 1.12 > 1, the Q3 point); at kappa = 0.5 and 1.0 the c = 0.9 column inflates at both pi because 0.9 > c_2. The c = 0.5 column is below c_1 in every row and decreases from pi = 0.10 to 0.30 as Prop. 12 requires.

---

## 2. The unequal-variance mixture (Q8): general selection on theta

Section 4b derived the between-mean term under A1' (a location shift of theta across classes, equal within-class variances). The survivor sample of section 3 has unequal within-class trait variances, so the general form is derived once here and A1' and the survivor sample are read off as special cases.

### 2.1 Assumption A1'' (general selection on theta)

theta | H has mean sqrt(s2_T) a_H and variance s2_T q_H; theta | M has mean sqrt(s2_T) a_M and variance s2_T q_M, with q_H, q_M > 0 and d_theta := a_M - a_H. s2_T is the day-1 reference variance (the human trait variance in the unselected population, so that rho_H and rel_H keep their day-1 values as reference quantities). The measurement error e, the outcome noise u, and the machine residual v are independent of (theta, A) as in A1 and A2. The machine branch is centered on its class:

    x | M = mu_M + lambda_M (theta - E[theta | M]) + v,     lambda_M = c sqrt(s2_M / (s2_T q_M)) = g / sqrt(q_M),     Var(v) = (1 - c^2) s2_M      (option A)

so that Cor(x, theta | M) = c and Var(x | M) = s2_M hold within class M as it stands (SPEC 1.2 defines c on the machine subsample, which is what an empirical estimate of c would be). Under A1' (q_M = 1) this is (E35) centered. The alternative reading, option B, holds the structural slope g and residual variance fixed and lets c and kappa move with q_M; the conversion is (E46) below and the choice is logged as Q10.

Observed class means. E[x | H] = mu_H + sqrt(s2_T) a_H =: m_H and E[x | M] = mu_M =: m_M, so the observed gap is

    Delta_obs := m_H - m_M = Delta + sqrt(s2_T) a_H,     delta_obs := Delta_obs / sqrt(V_H) = delta + a_H sqrt(rel_H).

Under A1 and A1' (a_H = 0) delta_obs = delta; in the survivor sample a_H != 0 and the observed human mean moves even though mu_H and e do not.

### 2.2 Moments

Within-class covariances with w = b theta + u:

    Cov(x, w | H) = b Var(theta | H) = b s2_T q_H,
    Cov(x, w | M) = lambda_M b Var(theta | M) = (g / sqrt(q_M)) b s2_T q_M = b s2_T g sqrt(q_M).

Between-class: E[w | A] = b sqrt(s2_T) a_A, so Cov(E[x | A], E[w | A]) = pi (1 - pi) (m_H - m_M) b sqrt(s2_T) (a_H - a_M) = -pi (1 - pi) b sqrt(s2_T) Delta_obs d_theta. Divide the total covariance by the reference b s2_T and use Delta_obs / sqrt(s2_T) = delta_obs sqrt(V_H) / sqrt(rel_H V_H):

    N''(pi) := Cov(x, w) / (b s2_T) = (1 - pi) q_H + pi g sqrt(q_M) - pi (1 - pi) delta_obs d_theta / sqrt(rel_H)                     (E40)

Variances. Var(x | H) = s2_T q_H + s2_H = V_H - s2_T (1 - q_H) = V_H [1 - rel_H (1 - q_H)]; Var(x | M) = s2_M = kappa V_H; between, pi (1 - pi) Delta_obs^2 = V_H pi (1 - pi) delta_obs^2. Var(w | A) = b^2 s2_T q_A + s2_u = V_w [1 - rho_T^2 (1 - q_A)]; between, pi (1 - pi) b^2 s2_T d_theta^2 = V_w pi (1 - pi) rho_T^2 d_theta^2. Hence

    Den''(pi) := Var(x) / V_H = (1 - pi) [1 - rel_H (1 - q_H)] + pi kappa + pi (1 - pi) delta_obs^2                                        (E41)
    W''(pi)   := Var(w) / V_w = 1 - rho_T^2 [ (1 - pi)(1 - q_H) + pi (1 - q_M) ] + pi (1 - pi) rho_T^2 d_theta^2                        (E42)

Prop. 13 (validity under A1''). With rho_H the reference human validity b s2_T / sqrt(V_H V_w),

    rho_obs = rho_H Att''(pi, c),     Att'' := N'' / sqrt(Den'' W'')                                                                     (E43)

Proof. rho_obs = Cov(x, w) / sqrt(Var(x) Var(w)) = b s2_T N'' / sqrt(V_H Den'' V_w W''), and b s2_T / sqrt(V_H V_w) = rho_H. QED.

Special cases, each checked by substitution. (a) q_H = q_M = 1, a_H = 0: N'' = N - pi (1 - pi) delta d_theta / sqrt(rel_H), Den'' = Den, W'' = 1 + pi (1 - pi) rho_T^2 d_theta^2, which is (E21). (b) Additionally d_theta = 0: (E7). (c) pi = 0 with q_H = q: N'' = q, Den'' = 1 - rel_H (1 - q), W'' = 1 - rho_T^2 (1 - q), which is the ratio in (E34) exactly. (d) A1 with q_H = q_M = 1 but a_H = a_M = a != 0 (both classes shifted together): d_theta = 0, delta_obs = delta + a sqrt(rel_H), so a common trait shift only relabels the observed gap.

What q_H < 1 does on its own (a_H = a_M = 0, q_M = 1): N'' = (1 - pi) q_H + pi g, Den'' = (1 - pi)[1 - rel_H (1 - q_H)] + pi kappa + pi (1 - pi) delta^2. The human within-class signal is scaled by q_H while the machine signal pi g is not, so range restriction on humans makes the machine share of the covariance relatively larger: at c = 0 that is extra attenuation, at c > c_2 extra inflation.

### 2.3 Sign flip under A1''

Prop. 13 (continued). rho_obs has the opposite sign to rho_H iff N'' < 0, i.e.

    (1 - pi) q_H + pi g sqrt(q_M) < pi (1 - pi) delta_obs d_theta / sqrt(rel_H)                                                          (E44)

equivalently, for c >= 0, iff c < c_flip''(pi) with

    c_flip''(pi) = (1 - pi) sqrt(rel_H / kappa) [ delta_obs d_theta / sqrt(rel_H) - q_H / pi ] / sqrt(q_M)                                (E45)

The region is nonempty on c >= 0 iff delta_obs d_theta > q_H sqrt(rel_H) / pi. Re-derivation of (E45) from (E44): pi g sqrt(q_M) < pi (1 - pi) delta_obs d_theta / sqrt(rel_H) - (1 - pi) q_H, divide by pi sqrt(q_M) and substitute g = c sqrt(kappa / rel_H). At q_H = q_M = 1 this is (E23). Relative to A1', human range restriction (q_H < 1) lowers the requirement by the factor q_H, and machine range restriction (q_M < 1) scales the whole threshold up by 1 / sqrt(q_M) without changing whether it is positive.

### 2.4 Option B conversion (for lane 4, if it holds the structural slope fixed)

If a DGP generates x | M = mu_M + g_struct (theta - E[theta | M]) + v with g_struct = c sqrt(kappa / rel_H) and Var(v) = (1 - c^2) kappa V_H fixed while Var(theta | M) = s2_T q_M, then within class M the realized quantities are

    Var(x | M) = kappa V_H [ 1 - c^2 (1 - q_M) ],     kappa_eff = kappa [ 1 - c^2 (1 - q_M) ],     c_eff = c sqrt(q_M) / sqrt( 1 - c^2 (1 - q_M) )        (E46)

Re-derivation: Var(x | M) = g_struct^2 s2_T q_M + (1 - c^2) kappa V_H = c^2 kappa V_H q_M + (1 - c^2) kappa V_H = kappa V_H [q_M c^2 + 1 - c^2]. Cor(x, theta | M) = g_struct s2_T q_M / sqrt(Var(x | M) s2_T q_M) = c sqrt(kappa V_H) sqrt(q_M) / sqrt(kappa V_H [1 - c^2 (1 - q_M)]). Consistency check: with g_eff := c_eff sqrt(kappa_eff / rel_H), g_eff sqrt(q_M) = c_eff sqrt(kappa_eff / rel_H) sqrt(q_M) = c sqrt(q_M) sqrt(kappa / rel_H) sqrt(q_M) = g q_M, and directly Cov(x, w | M) / (b s2_T) = g_struct q_M = g q_M. So (E40) to (E43) hold for either reading once (c, kappa) are the realized within-class values; only the labels on the grid axes differ. Lane 4 should state which it codes (Q10).

---

## 3. The survivor sample: what detect-and-delete leaves behind (proof of day-1 section 6.4)

### 3.1 Assumption A3 and the survivor parameters

Assumption A3 (detector error on machine text is trait-blind): P(pass | M, theta) = 1 - se does not depend on theta. At c = 0 this is automatic, since machine text carries no theta; at c > 0 it is an assumption about the detector, not about the machine process, and pass 3 should attack it (a detector that flags bland text more, when blandness tracks c theta, violates it). Under A3, theta | M, pass = theta | M in distribution.

Under A1 in the full population, the Gaussian threshold detector of 6.3, and A3, the survivor population (D = pass) satisfies A1'' with

    pi -> pi' (E30),   q_H = q = 1 - r_F^2 psi (E33),   q_M = 1,   a_H = r_F lambda (E32),   a_M = 0,   d_theta = -r_F lambda,
    delta_obs = delta_pass := delta + r_F lambda sqrt(rel_H)                                                                            (E47)

with kappa, c, g unchanged (q_M = 1 makes options A and B of section 2 coincide, so Q10 does not touch this section). Re-derivation of delta_pass: E[x | H, pass] = mu_H + E[theta | H, pass] = mu_H + r_F lambda sqrt(s2_T), because e is independent of (theta, F); E[x | M, pass] = mu_M by A3; the gap is Delta + r_F lambda sqrt(s2_T), and sqrt(s2_T / V_H) = sqrt(rel_H). Note for the day-1 file: the parenthetical in 6.4, "the human mean is unaffected because e is independent of F", is true of mu_H and of e but not of the observed human mean, which moves by r_F lambda sqrt(s2_T); logged as a wording fix for pass 1.

### 3.2 The survivor validity coefficient

Substituting (E47) into (E40) to (E43):

    N_pass   = (1 - pi') q + pi' g + pi' (1 - pi') r_F lambda [ r_F lambda + delta / sqrt(rel_H) ]                                       (E48)
    Den_pass = (1 - pi') [1 - rel_H (1 - q)] + pi' kappa + pi' (1 - pi') delta_pass^2                                                   (E49)
    W_pass   = 1 - rho_T^2 (1 - pi') (1 - q) + pi' (1 - pi') rho_T^2 r_F^2 lambda^2                                                      (E50)
    rho_obs,pass = rho_H Att_pass,     Att_pass := N_pass / sqrt(Den_pass W_pass)                                                        (E51)

Re-derivation of the between term in (E48): -pi' (1 - pi') delta_pass d_theta / sqrt(rel_H) = +pi' (1 - pi') [delta + r_F lambda sqrt(rel_H)] r_F lambda / sqrt(rel_H) = pi' (1 - pi') r_F lambda [delta / sqrt(rel_H) + r_F lambda]. The three named pieces of the day-1 claim are visible: residual contamination (pi' terms with g and kappa), range restriction (q in the human terms of all three multipliers), and the manufactured between-mean term (the r_F lambda products). For r_F > 0 the manufactured term has the sign of delta_pass: it is positive whenever delta >= 0, so it slightly helps, and turns negative only when delta < -r_F lambda sqrt(rel_H), i.e. when machine scores run above the surviving humans' scores (for r_F < 0 its sign is that of -delta_pass).

Checks. tau -> -inf with se -> 0 (no deletion; automatic in the ROC family of 3.3, where se = Phi(tau + d')): pi' = pi, lambda = 0, q = 1, and (E51) is (E7). pi = 0: pi' = 0 and (E51) is (E34). c = 0, r_F = 0: q = 1, lambda drops out, and (E51) is Att_0(pi') with the survivor mean gap delta, the naive "residual contamination only" formula of 6.1.

### 3.3 The ROC family

To move along a receiver operating curve, model the detector score on machine text as F | M ~ N(-d', 1), independent of theta (so A3 holds), with the same threshold: pass iff F > tau. Then

    sp_bar = 1 - Phi(tau),     se = Phi(tau + d'),     tau = -Phi^{-1}(sp),     d' = Phi^{-1}(se) + Phi^{-1}(sp).

d' = 2.073 reproduces the degraded point (0.85, 0.85) and d' = 4.653 the calibrated point (0.99, 0.99). Fixed d' and moving tau is one ROC curve; fixed tau and growing d' raises se at constant sp_bar.

Limits at fixed d' > 0. As tau -> -inf, pi' -> pi, q -> 1, lambda -> 0, and Att_pass -> Att(pi, c). As tau -> +inf, (1 - se) / sp_bar = [1 - Phi(tau + d')] / [1 - Phi(tau)] ~ exp(-d' tau - d'^2 / 2) tau / (tau + d') -> 0 by the Mills ratio, so pi' -> 0 faster than any power of tau while lambda ~ tau; hence every pi' lambda^2 term vanishes, psi -> 1, q -> 1 - r_F^2, and

    lim_{tau -> +inf} Att_pass = (1 - r_F^2) / sqrt[ (1 - rel_H r_F^2) (1 - rho_T^2 r_F^2) ]                                                (E52)

which is (E34) at the most aggressive threshold: what survives is the fluent tail of the humans only.

### 3.4 Prop. 14 (the three day-1 claims)

(i) The combined bias does not vanish as se -> 1. At fixed sp_bar < 1 and r_F != 0, as se -> 1 (d' -> inf at fixed tau) pi' -> 0 and Att_pass -> the (E34) ratio, which is strictly below 1 by Prop. 11 and does not depend on pi or c. Proof: (E48) to (E50) are continuous in pi' and reduce to case (c) of section 2.2 at pi' = 0. QED. So no improvement in sensitivity removes the deletion bias; only sp_bar -> 1 does, and the oracle (se = sp = 1) is the only point at which Att_pass = 1.

(ii) Along a ROC curve the bias is not monotone in the threshold. Existence is shown by evaluation of (E51) at pi = 0.10, c = 0, kappa = 0.2, delta = 0, rel_H = 0.7, rho_T = 0.5, r_F = 0.5, d' = 2.073 (hand-computed; lane 4 reproduces):

| tau | sp_bar | se | pi' | q | Att_pass |
| --- | --- | --- | --- | --- | --- |
| -inf | 1 | 0 | 0.100 | 1 | 0.938 |
| -2.326 | 0.99 | 0.400 | 0.0631 | 0.984 | 0.953 |
| -1.036 | 0.85 | 0.850 | 0.0192 | 0.910 | 0.940 |
| 0 | 0.50 | 0.981 | 0.0042 | 0.841 | 0.908 |
| +inf | 0 | 1 | 0 | 0.750 | 0.853 |

The bias falls, then rises past its no-deletion value, then reaches the (E52) floor. Mechanism: raising tau removes machines, an effect that saturates once pi' is small, and removes fluent-selected humans, an effect that grows without bound in tau; the optimum threshold is interior and, on this ROC, near the in-domain specificity, where the detector catches only 40 percent of machine text. "A better detector" in the sense of a higher threshold is therefore not "less bias".

(iii) The survivor sample has exactly the section 4b structure, and the flip region is empty on the SPEC grid. From (E45) with (E47),

    c_flip,pass(pi') = -(1 - pi') sqrt(rel_H / kappa) [ r_F lambda ( delta / sqrt(rel_H) + r_F lambda ) + q / pi' ]                             (E53)

which, for r_F > 0, is nonempty on c >= 0 iff delta < -sqrt(rel_H) [ r_F lambda + q / (pi' r_F lambda) ] (for r_F < 0 the same condition holds with (r_F, delta) replaced by (|r_F|, -delta)). At the degraded point with pi = 0.30, r_F = 0.5: pi' = 0.0703, r_F lambda = 0.137, q = 0.910, so the requirement is delta < -79 observed SD. The most favourable cell in the ROC family at se = 0.85 is sp_bar = 0.50 (tau = 0, lambda = 0.798), where pi' = 0.114, r_F lambda = 0.399, q = 0.841 and the requirement is delta < -15.8 SD. The manufactured gap |d_theta| = r_F lambda is bounded by r_F times the truncated-normal mean, which never reaches the size that Prop. 7 needs. Day-1 6.4's phrase "is exactly the section 4b sign-flip mechanism at high pi" is corrected to: the same mechanism, but with a gap too small to flip the sign on any realistic cell; the manufactured between-mean term matters for magnitude, not sign, which is the same conclusion as Q5 for the population version.

### 3.5 Magnitudes (Q6)

Att_pass from (E51) at pi = 0.10, rel_H = 0.7, rho_T = 0.5, delta = 0; "none" is Att(pi, c) from (E7); the fourth column separates the two error channels; oracle is se = sp = 1.

| kappa | c | r_F | none | degraded (0.85, 0.85) | calibrated (0.99, 0.99) | se = 1, sp = 0.85 | oracle |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.2 | 0 | 0.3 | 0.938 | 0.971 | 0.996 | 0.983 | 1 |
| 0.2 | 0 | 0.5 | 0.938 | 0.940 | 0.991 | 0.951 | 1 |
| 0.2 | 0.9 | 0.5 | 0.988 | 0.949 | 0.992 | 0.951 | 1 |
| 1.0 | 0 | 0.5 | 0.900 | 0.932 | 0.991 | 0.951 | 1 |

Reading for the writeup. At the calibrated point deletion works: every row ends within 1 percent of rho_H, consistent with SPEC's in-domain framing. At the degraded point the answer depends on r_F and c. With r_F = 0.3 deletion helps (row 1); with r_F = 0.5 it swaps a 6 percent contamination bias for a 6 percent deletion bias at c = 0 (row 2), and worsens the bias from 1 to 5 percent when the machine text is trait-informative (row 3), because deleting trait-carrying machine rows removes signal while deleting fluent humans removes variance. The se = 1 column is the floor of (i): with the human false-positive rate at 15 percent and r_F = 0.5, no sensitivity gets above 0.951. The paper's claim against detect-and-delete is therefore conditional on two measurable numbers, the out-of-domain false-positive rate and r_F; lane 3's r_F estimate on the essays testbed decides how hard the claim can be stated (Q6, lane 3 owner).

---

## 4. Q3: the qualified three-regime story

SPEC 1.2 (line 20): "c near 1: the LLM is a faithful amanuensis. Contamination is nearly harmless; the paper should say so and move on." What the closed forms support is narrower, in three statements.

### 4.1 Exactly harmless is one machine, not a regime

Att(pi, c) = 1 at a single pi iff c = c*(pi) from (E17). Att(pi, c) = 1 for every pi iff N(pi)^2 = Den(pi) identically in pi. Matching coefficients: the pi^1 terms give 2 (g - 1) = kappa - 1 + delta^2, i.e. g = S / 2; the pi = 1 values give g^2 = kappa; together (1 - sqrt(kappa))^2 + delta^2 = 0, so

    harmless for all pi  iff  kappa = 1, delta = 0, g = 1, i.e. c = sqrt(rel_H)                                                          (E54)

(the pi^2 coefficient (1 - g)^2 = -delta^2 is then also satisfied). Re-derivation of the pi^1 step: N^2 = 1 + 2 pi (g - 1) + pi^2 (g - 1)^2 and Den = 1 + pi (kappa - 1) + pi delta^2 - pi^2 delta^2. The uniquely harmless machine is a replica of the human measurement: same mean, same variance, and Cor(x, theta | M) = sqrt(rel_H) = Cor(x, theta | H). A perfect trait copy (c = 1) is not harmless at any kappa unless pi is also on the curve (E17).

### 4.2 Nearly harmless at c = 1 pins kappa to a window

By (E39), at c = 1 the first-order bias in pi is pi rho_H [ sqrt(kappa / rel_H) - S / 2 ]. At delta = 0 it vanishes iff s = sqrt(kappa) solves s^2 - (2 / sqrt(rel_H)) s + 1 = 0:

    s = [ 1 -+ sqrt(1 - rel_H) ] / sqrt(rel_H),     kappa_lo kappa_hi = 1                                                                (E55)

At rel_H = 0.7: kappa_lo = 0.292, kappa_hi = 3.42. So a perfect amanuensis with no mean gap attenuates (to first order) when kappa < 0.292, inflates when 0.292 < kappa < 3.42, and attenuates again above. Table 1.6 confirms the pattern exactly: at c = 1 the kappa = 0.2 rows sit below 1 (0.994, 0.987) and the kappa = 0.5 and 1.0 rows above (1.010, 1.034; 1.020, 1.059). The SPEC's homogenized case (SPEC line 18, machine answers "samey"; kappa = 0.2 on the N3 grid) is on the attenuating side of the window, and the no-homogenization control (kappa = 1) is inside it. A mean gap moves the window: at delta = 1 and kappa = 0.5, c_2(1) = S sqrt(rel_H) / (2 sqrt(kappa)) = 2.5 * 0.837 / 1.414 = 1.48 > 1, so with a 1-SD mean gap no c in [0, 1] avoids attenuation at that kappa.

### 4.3 The estimand decides the sign in the amanuensis cell

Against rho_T instead of rho_H (N2), rho_obs / rho_T = sqrt(rel_H) Att. At c = 1, kappa = 1, delta = 0 this is (1 - pi) sqrt(rel_H) + pi, which lies between sqrt(rel_H) (the clean sample) and 1: a perfect trait copy with human-scale variance is a better indicator of theta than the human measurement, so contamination moves the naive coefficient toward the latent target. Under N2's rho_H headline the same cell reads as inflation (+2 percent at pi = 0.10, +6 percent at pi = 0.30, table 1.6). [N2 decided 2026-09-07 20:58: the headline is the observed-score rho_H := Cor(x, w | H) (E75), section 8.] Under the headline the amanuensis regime is not harmless: it inflates the naive validity above the clean-sample value, Att = 1 + pi (1 / sqrt(rel_H) - 1) > 1 (E76). The rho_T reading, under which the same cell is partial disattenuation that never reaches the target (Prop. 17), is the robustness note of 8.2, not the headline.

Recommended wording for the three regimes (replacing SPEC 1.2's third bullet): "c near 1 is harmless only when the machine output also matches the human scale and mean (kappa near 1, delta near 0); at SPEC's own homogenized setting (kappa = 0.2, rel_H = 0.7) the harmless coupling c_2 = 1.12 is unreachable, so on SPEC's prevalence grid (pi <= 0.30) a perfect amanuensis still attenuates, and outside the homogenized setting it inflates the validity coefficient above what a clean human sample delivers." [Restated 2026-09-07 20:58 under the N2 decree, with the pi <= 0.30 qualifier day-1 section 3.3 already carries, since that cell sits in the U-shaped band and recrosses Att = 1 near pi = 0.60, off the grid; the earlier closing clause "while moving the estimate toward the latent validity" is now the robustness note of 8.2.] Whether SPEC 1.2 changes is Abhay's call (Q3 owner).

---

## 5. Q4: both endpoints machine-written (extension; ships only if Layer B's target stays clean)

SPEC 4.2 (line 87) sets the Layer B validity target as a held-out trait or a simulated outcome, both clean, so the main derivation keeps w clean. If the outcome is itself an open-ended item scored the same way (text-to-text validity, the realistic case for a trait score against another text-scored construct), it is a second mixture. This section derives that case under ignorable authorship and shows the between-mean term appears without any selection on theta.

### 5.1 Setup

Let y be the outcome item. Same authorship for both items (one respondent pastes the whole survey into one session), so A is common. Under A1:

    y | H = mu_wH + b theta + u,     Var(y | H) = V_w,     Cor(y, theta | H) = rho_T,
    y | M = mu_wM + lambda_w theta + v_w,     lambda_w = c_w sqrt(s2_wM / s2_T),     Var(v_w) = (1 - c_w^2) s2_wM,

with c_w := Cor(y, theta | M), kappa_w := s2_wM / V_w, Delta_w := mu_wH - mu_wM, delta_w := Delta_w / sqrt(V_w), and

    g_w := lambda_w / b = c_w sqrt(kappa_w) / rho_T

the outcome-side mirror of g (rel_H replaced by rho_T^2 = Cor(y, theta | H)^2). Assumption A4: Cor(v, v_w) = rho_vw, the shared machine residual across the two items (the same object as rho_v in Prop. 8 when x and y are two items of one session), with (v, v_w) independent of (theta, e, u, A). A2 is not needed: no term below pairs v with u.

### 5.2 Moments

Within H: Cov(x, y | H) = b s2_T. Within M: Cov(g theta + v, lambda_w theta + v_w) = g lambda_w s2_T + rho_vw sqrt((1 - c^2) s2_M (1 - c_w^2) s2_wM). Between: pi (1 - pi) Delta Delta_w, present under A1 because both class means shift. Divide by b s2_T, using lambda_w / b = g_w, sqrt(s2_M s2_wM) / (b s2_T) = sqrt(kappa kappa_w) sqrt(V_H V_w) / (b s2_T) = sqrt(kappa kappa_w) / rho_H, and Delta Delta_w / (b s2_T) = delta delta_w / rho_H:

    N_2(pi) = (1 - pi) + pi g g_w + [ pi rho_vw sqrt((1 - c^2)(1 - c_w^2) kappa kappa_w) + pi (1 - pi) delta delta_w ] / rho_H                (E56)
    Den_w(pi) = Var(y) / V_w = (1 - pi) + pi kappa_w + pi (1 - pi) delta_w^2                                                              (E57)

Prop. 15 (both endpoints). rho_obs = rho_H Att_2 with

    Att_2 := N_2 / sqrt( Den Den_w )                                                                                                    (E58)

Proof. As for Prop. 13 with Var(x) = V_H Den(pi) unchanged and Var(y) = V_w Den_w(pi) by the same law-of-total-variance step. QED.

General joint authorship. If P(A_x = M, A_y = M) = pi_xy with marginals pi, the four (A_x, A_y) cells have weights 1 - 2 pi + pi_xy, pi - pi_xy, pi - pi_xy, pi_xy and within-cell covariances b s2_T times 1, g_w, g, g g_w + R with R := rho_vw sqrt((1 - c^2)(1 - c_w^2) kappa kappa_w) / rho_H; the between term is Delta Delta_w Cov(1{A_x = M}, 1{A_y = M}) = Delta Delta_w (pi_xy - pi^2). So

    N_2 = (1 - 2 pi + pi_xy) + (pi - pi_xy)(g + g_w) + pi_xy (g g_w + R) + (pi_xy - pi^2) delta delta_w / rho_H                             (E59)

Same session, pi_xy = pi, gives (E56). Independent authorship, pi_xy = pi^2, gives N_2 = N(pi, c) N_w(pi, c_w) + pi^2 R with N_w := (1 - pi) + pi g_w and no between term: two single-mixture attenuations multiplied, sign-stable for c, c_w >= 0 and rho_vw >= 0. A negative shared residual is a second flip channel: N_2 < 0 iff rho_vw < -N N_w rho_H / [ pi^2 sqrt((1 - c^2)(1 - c_w^2) kappa kappa_w) ]. The threshold magnitude is smallest at c = c_w = 0, where it is (1 - pi)^2 rho_H / (pi^2 sqrt(kappa kappa_w)); at pi = 0.30, kappa = kappa_w = 1 that is 5.44 rho_H, above 1 for every rho_H > 0.184, so no admissible rho_vw reaches it on the SPEC grid. The between-mean term under A1 needs pi_xy > pi^2, i.e. respondents who machine-write one item tend to machine-write the other, which is the realistic case.

### 5.3 What is new relative to a clean outcome

(a) The between-mean term is present under A1, with the sign of delta delta_w, and enters relative to rho_H rather than relative to the trait signal, so it is largest when the true validity is small. (b) The shared residual rho_vw is a second inflation source under A1 even at delta = delta_w = 0: at c = c_w = 0, kappa = kappa_w = 0.2, rho_H = 0.3, pi = 0.1, rho_vw = 0.5 gives N_2 = 0.9 + 0.0333 = 0.933, Den = Den_w = 0.92, Att_2 = 1.014; a same-session residual masquerades as validity, which is the between-item face of H2. (c) Sign flip under A1. At c = c_w = rho_vw = 0, N_2 = (1 - pi)[1 + pi delta delta_w / rho_H] < 0 iff

    pi delta delta_w < -rho_H                                                                                                          (E60)

reachable on the SPEC grid: pi = 0.30, rho_H = 0.3 needs opposite-sign gaps with |delta delta_w| > 1, for instance 1-SD gaps in opposite directions on the two items. Magnitudes at pi = 0.1, kappa = kappa_w = 0.2, rho_H = 0.3, c = c_w = rho_vw = 0: delta = delta_w = 1 gives N_2 = 1.2, Den = Den_w = 1.01, Att_2 = 1.19; delta = 1, delta_w = -1 gives N_2 = 0.6, Att_2 = 0.594. The same two 1-SD gaps that produce a 6 percent attenuation with a clean outcome (table 1.6, kappa 0.2, c = 0: 0.938 at delta = 0) produce a 19 percent inflation or a 41 percent attenuation here.

Ship condition. This section ships as an extension iff Layer B's target stays clean (Q4 owner: Abhay). If the target becomes a text-scored construct, this section replaces day-1 section 3 as the main model and (E60) becomes a headline result, because it is a sign flip under ignorable authorship, which Q5 says the clean-outcome model cannot produce.

---

## 6. Day-2 handoff block for lane 4

### 6.1 Canonical DGP (N1 final), unit human variances

Correlations are scale-free, so set V_H = V_w = 1. All noise terms Gaussian, mutually independent, independent of theta and A.

    theta ~ N(0, rel_H)                                                  [s2_T = rel_H]
    A ~ Bernoulli(pi), independent of theta                               [A1; see 6.4 for the non-ignorable arm]
    x | H = delta + theta + e,          e ~ N(0, 1 - rel_H)               [mu_H = delta, so Delta = delta]
    x | M = 0 + c sqrt(kappa / rel_H) theta + v,   v ~ N(0, (1 - c^2) kappa)     [mu_M = 0, s2_M = kappa; this is (E35)]
    w = b theta + u,   b = rho_T / sqrt(rel_H),   u ~ N(0, 1 - rho_T^2)                                                     (E61)

Implied: Var(w) = rho_T^2 + 1 - rho_T^2 = 1; Cor(theta, w) = rho_T; rho_H = Cor(x, w | H) = b rel_H = rho_T sqrt(rel_H); Cor(x, theta | M) = c; Var(x | M) = kappa. Both estimands come out of the same draw: report bias and RMSE against rho_H = rho_T sqrt(rel_H) (headline, N2 recommendation) and against rho_T (disattenuated table). Base values used in every hand table here: rel_H = 0.7, rho_T = 0.5, so rho_H = 0.418.

Multi-item (Q7). For items j = 1..J with a common trait: x_j | H = delta + theta + e_j, e_j iid N(0, 1 - rel_H); x_j | M = c sqrt(kappa / rel_H) theta + v_j with

    v_j = sqrt((1 - c^2) kappa) [ sqrt(rho_v) z + sqrt(1 - rho_v) z_j ],   z, z_1, ..., z_J iid N(0, 1)                                    (E62)

so that Var(v_j) = (1 - c^2) kappa and Cor(v_j, v_k) = rho_v. rho_v is a grid parameter with default 0 (independent calls); 0.5 as the same-session arm. Under Q4's both-endpoints model, rho_vw in section 5 is this rho_v with y as one of the items.

Grid. pi and c per SPEC 4.3; kappa in {0.2, 0.5, 1.0} (N3); delta per SPEC's mean-gap values; rho_v in {0, 0.5}; r_F in {0, 0.3, 0.5}. rel_H and rho_T fixed at the base values unless a sensitivity arm is wanted.

### 6.2 Detector DGP

    F | H = r_F theta / sqrt(rel_H) + sqrt(1 - r_F^2) eta,     F | M = -d' + eta',     eta, eta' iid N(0, 1)
    pass iff F > tau,     tau = -Phi^{-1}(sp),     d' = Phi^{-1}(se) + Phi^{-1}(sp)                                                        (E63)

Operating points: calibrated (se = sp = 0.99): tau = -2.326, d' = 4.653; degraded (0.85, 0.85): tau = -1.036, d' = 2.073; oracle (1, 1): pass iff A = H, implemented on A directly (it is the tau -> -inf, d' -> inf corner and is not a finite member of (E63)); none: pass everyone. Optional ROC arm for table 3.4: d' = 2.073 fixed, sp in {0.99, 0.85, 0.50}. Detect-and-delete estimators compute the naive correlation on the pass subsample; the r_F = 0 arm isolates residual contamination from deletion selection.

### 6.3 Numbers lane 4 reproduces before any of them appears in prose (SPEC section 7, check 2)

Population moments, not estimator output, so evaluate them from the DGP's implied covariance matrix or from a single draw large enough that the Monte Carlo error is below the third decimal (n = 10^6 gives a correlation SE near 0.001; compare at two decimals or use the exact moment route):

1. Table 1.6: 24 values of Att(pi, c) at rel_H = 0.7, delta = 0; the thresholds c_1, c_2 at each kappa; and pi_min = 0.352 with Att(0.35, 1) = 0.9865 at kappa = 0.2.
2. Table 3.4: Att_pass along the ROC at d' = 2.073, including the intermediate pi', q, se values.
3. Table 3.5: 16 values of Att_pass by operating point, plus the day-1 6.3 table (which is the se = 1 column).
4. Section 4.2: the harmless window kappa_lo = 0.292, kappa_hi = 3.42 at c = 1, rel_H = 0.7 (Att crosses 1 there to first order in pi; check at pi = 0.01).
5. Section 5.3: Att_2 = 1.19, 0.594, 1.014 at the stated parameters (needs the two-item DGP with a machine-written y).

### 6.4 Non-ignorable authorship arm (only if Abhay answers Q5 yes)

Replace the A line of (E61) with theta | A ~ N(sqrt(rel_H) a_A, rel_H q_A) and center the machine branch on its class, x | M = c sqrt(kappa / (rel_H q_M)) (theta - sqrt(rel_H) a_M) + v. The recommended minimal arm is the location shift (q_H = q_M = 1, a_H = 0, a_M = d_theta in {0, 0.5, 1.0}), whose closed form is (E21); the general form is (E43) and the flip boundary (E45). If lane 4 prefers to hold the structural slope fixed instead, apply (E46) before comparing with the closed forms and say so in the grid metadata (Q10).

Three things not to do: do not code x | M = mu_M + c theta + v (N1: that c is g); do not read a grid column that decreases from pi = 0.10 to 0.30 as regime I (section 1.4, the minimum can sit past 0.30); do not report a bias without naming its estimand (N2).

---

## 7. Summary: proven versus open after day 2

Proven in this file (subject to passes 1 to 3):
- Att is affine in c at fixed pi (E36); the three regimes hold at every mean gap with thresholds c_1(delta), c_2(delta) (Prop. 12, E37) and an explicit interior minimum (E38); first-order bias pi rho_H sqrt(kappa / rel_H) [c - c_2(delta)] (E39).
- The unequal-variance mixture closed form (E40) to (E43) with A1', A1 and the pi = 0 range-restriction formula as special cases, and its flip boundary (E45) (Prop. 13).
- The survivor-sample validity coefficient (E48) to (E51) under A3, with the three day-1 claims: the bias does not vanish as se -> 1 (floor = (E34)); it is non-monotone along a ROC (table 3.4); it has the 4b structure but the flip region is empty on the SPEC grid (Prop. 14).
- Exactly harmless is the human-replica machine only (E54); the amanuensis is first-order harmless at c = 1 only inside a kappa window (E55) that excludes SPEC's homogenized case; the amanuensis story is signed under the N2 decree of 2026-09-07 20:58: inflation of the observed-score headline, partial disattenuation against rho_T (sections 4.3 and 8).
- Both endpoints machine-written: between-mean term under A1, a sign flip reachable on the SPEC grid under same-session authorship (E56) to (E60), none under independent authorship (Prop. 15).

Open, logged in lane1-open-questions.md: Q10 (option A versus B for c and kappa under non-ignorable arms); A3 as a pass-3 attack target; Q9 (non-Gaussian detectors: the ROC family of 3.3 is Gaussian, so Prop. 14 (ii) is an existence claim inside that family); the day-1 6.4 wording fix; Q6 now hinges on lane 3's r_F; Q3 and Q4 ship conditions are Abhay's calls. Not done: the pass-1 diff against derivations/pass1-astra-rederivation.md (Astra's notation differs, including its reading of rho_H, so the diff needs a symbol map first).

Verification status: self-checked by re-derivation of every display equation once. Sonnet pass, 2026-09-07, 14 agents (10 re-derivation refuters, one symbolic and one numeric moment-builder per section for sections 1 to 5; 3 arithmetic checkers over tables 1.6, 3.4, 3.5 and every number quoted in prose; 1 notation audit): every numbered equation (E35) to (E63) and every proof step of Props. 12 to 15 reproduced; 101 of 101 numeric cells reproduced; equation and proposition numbering and ASCII check clean. Eight exposition findings applied in this file: the (E39) algebra chain; the q_H remark now states a_H = a_M = 0; the tau -> -inf check now says se -> 0; the survivor between-term sign remark and the (E53) nonemptiness condition now carry r_F > 0 with the r_F < 0 mirror; the independent-authorship sign-stability claim in 5.2 now requires rho_vw >= 0, with the negative-rho_vw flip threshold shown to exceed 1 on the SPEC grid; g_eff defined; section 0 catalog completed (g_struct, kappa_eff, c_eff, g_eff, N_w, R, rho_v); Q9 carried forward. Passes 1 to 3 pending.

---

DONE-LANE1-DAY2 (2026-09-07, marker appended after the Sonnet pass). Summary. Proven in this file, subject to passes 1 to 3: attenuation is affine in c at fixed prevalence, so the three coupling regimes hold at every mean gap with explicit thresholds c_1(delta), c_2(delta) and an interior minimum pi_min (E36 to E39, Prop. 12); the unequal-variance mixture closed form and its flip boundary, with A1', A1, and the pure range-restriction formula as special cases (E40 to E45, Prop. 13); the survivor-sample coefficient under A3 with the three day-1 claims settled, namely the bias does not vanish as se -> 1, it is non-monotone along the ROC, and the manufactured between-mean term changes magnitude but never sign on the SPEC grid (E48 to E53, Prop. 14); exact harmlessness holds only for the human-replica machine, and the amanuensis is first-order harmless at c = 1 only inside a kappa window that excludes the homogenized case (E54, E55); and the both-endpoints mixture, where a sign flip is reachable under same-session authorship but not under independent authorship with rho_vw >= 0 (E56 to E60, Prop. 15). Open, logged in lane1-open-questions.md: Q10 (realized versus structural c and kappa under non-ignorable arms, lane 4 to state which it codes); A3 and Q9 as pass-3 attack targets; the D1-fix wording in day-1 section 6.4; Q6's strength against detect-and-delete hinges on lane 3's r_F; the Q3 SPEC wording and the Q4 ship decision are Abhay's calls; the pass-1 diff needs a symbol map before it is mechanical.

---

## 8. Addendum (2026-09-07, 20:58): N2 decided, the observed-score headline

N2 is closed by Abhay's delegated call, relayed 20:58 and on disk at prompts/lane1-n2.md. The headline estimand is the observed-score validity in the human subpopulation,

    rho_H := Cor(x, w | H),   x the observed trait score, w the criterion,                                                              (E75)

and the latent-trait validity rho_T := Cor(theta, w) is carried as a robustness note, not as the headline. The crosswalk is exact and unchanged, rho_H = sqrt(rel_H) rho_T (section 0, 6.1, CONVENTIONS.md line 30), so no number in this file, in day 1, in the pivot memo or in lane 4's outputs moves; what the decree fixes is which ratio the word "bias" refers to. Under (E75) the clean sample (pi = 0) is unbiased by construction, so bias means contamination bias and nothing else, which was the argument of the N2 entry in lane1-open-questions.md. Equation numbers continue the lane-1 sequence from the pivot memo's (E74); propositions continue from the memo's Prop. 16.

### 8.1 The amanuensis sentence, signed

Under (E75) the amanuensis cell (c = 1, kappa = 1, delta = 0) is not harmless: it inflates. From (E7) with g = 1 / sqrt(rel_H) and Den = 1,

    Att(pi; c = 1, kappa = 1, delta = 0) = 1 + pi [ 1 / sqrt(rel_H) - 1 ] > 1   for every 0 < pi <= 1 when rel_H < 1,               (E76)

exactly linear in pi, and at rel_H = 0.7 equal to 1.020 at pi = 0.10 and 1.059 at pi = 0.30 (table 1.6). The 4.3 sentence therefore reads: a perfect trait copy at human scale and mean pushes the naive validity above the value the human sample alone delivers, by 2 percent at pi = 0.10 and 6 percent at pi = 0.30; the only exactly harmless machine is the human replica (E54), and the amanuensis is harmless to first order only inside the kappa window (E55), which excludes SPEC's homogenized kappa = 0.2.

The general statement behind the sentence is already proven and only re-read under (E75). At fixed pi, Att is affine and increasing in c (E36) and equals 1 on the curve c*(pi) of (E17), so contamination inflates the headline iff c > c*(pi) and attenuates iff c < c*(pi). To first order in pi the boundary is g_2(delta) = S / 2 = (1 + kappa + delta^2) / 2 in coupling-ratio units (E39), a scale-free statement that holds unchanged under Layer B's normalization, where r_H takes the role of sqrt(rel_H) in N (memo (E66), LAYERB-PILOT.md section 4). At kappa = 1, delta = 0 the threshold is g_2 = 1, the human-replica point: coupling above the human-replica point amplifies the observed correlation and coupling below it attenuates, and the amplification holds at every pi, not only to first order, because g >= S / 2 makes Att increasing in pi from Att(0) = 1 (day-1 Prop. 4 at delta = 0, Prop. 12 in general). At other (kappa, delta) the threshold sits at S / 2, above 1 when kappa + delta^2 > 1 and below 1 otherwise.

Lane 4's Layer B pilot (lane4-simulation/LAYERB-PILOT.md, marker PILOTB-DONE, 2026-09-07) realized this on real text: PersonaLLM gpt-4-0613 stories injected into the PK essays, EXT, pi = 0.10, with the assignment fraction p as the only dial. Its section 1 closed form and section 2 Monte Carlo (400 replicates per arm), on the injection-half values r_H = 0.1828 and c_pool = 0.4760 (not lane 3's whole-pool 0.1596 and 0.4420):

| p | c | kappa | delta | g | Att, closed form | Att, MC mean (MCSE) |
|---|---|---|---|---|---|---|
| 0 | 0 | 0.864 | 0.536 | 0 | 0.895 | 0.868 (0.018) |
| 0.5 | 0.238 | 0.864 | 0.536 | 1.210 | 1.015 | 0.982 (0.017) |
| 1 | 0.476 | 0.864 | 0.536 | 2.419 | 1.135 | 1.138 (0.016) |

At the pilot's kappa and delta the first-order threshold is g_2 = S / 2 = 2.151 / 2 = 1.076; g runs 0, 1.21, 2.42, so the p = 0 arm sits below the threshold and attenuates, and the p = 0.5 and p = 1 arms sit above it and inflate, at pi = 0.10 by the closed-form column and at every pi by Prop. 12. The exact crossing at pi = 0.10 from (E17), N = sqrt(Den) with Den = 1.01225, is g* = 1.061, c* = g* r_H / sqrt(kappa) = 0.209, p* = c* / c_pool = 0.44 (g*, c* and p* computed here from the pilot's inputs; the pilot reports Den but not the crossing). Two caveats on quoting the pilot as the amanuensis cell. It is not that cell: kappa = 0.864 and delta = 0.536 rather than 1 and 0, and g = 2.42 rather than 1.195, so it sits well past the threshold rather than at the SPEC point c = 1. And the p = 0.5 arm's sign rests on the closed form alone: its MC mean 0.982 lies 1.9 MCSE below the predicted 1.015 and on the other side of 1, inside the pilot's 4 MCSE pass bar, and the pilot records a seed-noise check on that arm (its section 2); the p = 0 and p = 1 arms agree with the closed form on which side of 1 they fall. What the pilot establishes is the mechanism: the same machine pool, the same kappa and delta, moved from Att = 0.895 to Att = 1.135 by assignment alone, which under (E75) is attenuation turned into inflation, the g > g_2 side of (E39) on real text.

### 8.2 Robustness: the latent-trait reading

Against rho_T the same estimate reads through rho_obs / rho_T = sqrt(rel_H) Att (6.1). What flips is the zero of the bias and with it the verbal sign of every cell that inflates under (E75).

Prop. 17 (the latent reading never inflates). Under A1 with 0 <= c <= 1, kappa >= 0, any delta, rel_H < 1, 0 < pi < 1 and rho_T != 0: 0 <= sqrt(rel_H) Att(pi, c) < 1, hence |rho_obs| < |rho_T|.

Proof. sqrt(rel_H) N = sqrt(rel_H) (1 - pi) + pi c sqrt(kappa) is nonnegative, and it is < (1 - pi) + pi sqrt(kappa) because rel_H < 1, pi < 1 and c <= 1. By concavity of the square root, (1 - pi) sqrt(1) + pi sqrt(kappa) <= sqrt((1 - pi) + pi kappa) <= sqrt(Den(pi)), the last step because pi (1 - pi) delta^2 >= 0. So sqrt(rel_H) N < sqrt(Den), i.e. sqrt(rel_H) Att < 1, and rho_obs = rho_T sqrt(rel_H) Att gives the modulus claim. QED.

So under rho_T the (pi, c) sign map of section 1 collapses to one region: every cell attenuates, the inflation region c > c*(pi) included, and the latent zero N = sqrt(Den / rel_H) is never reached with c <= 1 (at kappa = 1, delta = 0 it would need c = 2.47 at pi = 0.10 and c = 1.38 at pi = 0.30). The amanuensis cell reads as partial disattenuation that never completes: sqrt(rel_H) Att is 0.853 at pi = 0.10 and 0.886 at pi = 0.30 against 0.837 for the clean sample. Under rho_T no machine is harmless at any interior prevalence: Att(0) = 1 for every machine, so sqrt(rel_H) Att = 1 cannot hold for all pi, and by Prop. 17 it fails at every 0 < pi < 1; the one equality is the all-machine sample pi = 1 with c = 1, where Att(1) = c / sqrt(rel_H) (day-1 boundary check, line 104), off both Prop. 17's domain and the SPEC grid. The clean sample itself carries the classical bias rho_T (sqrt(rel_H) - 1), which is -0.082 at rho_T = 0.5, rel_H = 0.7. On the pilot, rho_obs / rho_T = r_H Att runs 0.164, 0.186, 0.208 across p = 0, 0.5, 1 (rho_T = 0.5 and rho_H = 0.0914 there): the same three arms read as 84, 81 and 79 percent short of the latent target.

What does not flip: Att itself and every statement made in Att terms, the three regimes and their thresholds c_1 and c_2 (E15, E16, E37), the curve c*(pi) (E17), the interior minimum pi_min (E38), the monotonicity results (day-1 Prop. 4, Prop. 12), exact harmlessness (E54) and the kappa window (E55) read as statements about Att = 1 and about the first-order coefficient, the unequal-variance flip boundary (E45), the survivor floor (E34) and Prop. 14, the both-endpoints flip (E56) to (E60) and Prop. 15, all of which are ratios or their sign patterns and rescale by the constant sqrt(rel_H); and the memo's Prop. 16 with (E73), (E74), which concern c and g and do not involve the estimand. Lane 4's H1 to H3 metrics need no rework because CONVENTIONS.md line 142 already reports both estimands. The estimator chain recovers rho_H first and reaches rho_T by dividing by sqrt(rel_hat), which adds the sampling variance of rel_hat to every rho_T-scale metric, so an estimator ranking read on the rho_T scale can differ from the rho_H ranking through that term alone; the grid reports both and the difference is read off it, not derived. At k_chunks = 1, rel_H is not identified and the rho_T version cannot be reported at all (the pilot's section 4), so on Layer B the robustness note waits on chunk-level scores (Q14, memo 8.2 step 1).

### 8.3 Propagation

- This file: 4.3 tagged and its sentence signed as in 8.1, the recommended SPEC 1.2 wording restated under (E75); the section 7 bullet no longer calls the sign open.
- board.md: line 7's N2 clause moved from open to decided 2026-09-07 with a pointer here; line 10's lane-4 clause that waited on the call tagged.
- lane1-open-questions.md: the N2 entry tagged and a closure entry appended with a pointer here.
- derivations/design-pivot-memo.md line 247, which said the call was still open, tagged.
- Not edited, other lanes' files, listed for their owners: CONVENTIONS.md line 30 still calls rho_H the "N2 recommendation" and README.md lines 37 to 40 still say "Abhay's call on this is still open" (lane 4); LAYERB-PILOT.md's disclosures still call the delta sign unresolved, ruled in memo 9.2 (lane 4); SPEC.md 1.1 defines rho as Cor(theta, w) and 1.3 names rho_H "the validity coefficient in the human subpopulation", so under the decree 1.3 is (E75) and 1.1's rho is rho_T, a SPEC edit that is Abhay's (Q3 owner).

Verification status: self-checked by re-derivation of (E76), Prop. 17 and every number above once. Sonnet pass, 2026-09-07 evening, 4 agents (2 refuters on 8.1 and 8.2, 1 arithmetic checker over every number against (E7), table 1.6 and LAYERB-PILOT.md, 1 notation and cross-reference audit over the four edited files): 83 checks, (E76) and Prop. 17 reproduced, every pilot number reproduced, numbering and ASCII clean. Seven findings applied: the restated SPEC 1.2 wording regained day-1's pi <= 0.30 qualifier (the kappa = 0.2 cell recrosses Att = 1 near pi = 0.60); Prop. 17 now states rho_T != 0; the "no harmless machine" sentence is restricted to interior pi, with the pi = 1, c = 1 equality named; Den printed as the pilot's 1.01225; the crossing parenthetical says which quantities are computed here; and the README citation in 8.3 and in lane1-open-questions.md now quotes what the README says.

---

DONE-N2 (2026-09-07, decree relayed 20:58, addendum the same evening). Summary. The headline estimand is rho_H := Cor(x, w | H) with x the observed trait score (E75); rho_T = rho_H / sqrt(rel_H) is a robustness note. Under the headline the amanuensis cell inflates, Att = 1 + pi (1 / sqrt(rel_H) - 1) (E76), 2 percent at pi = 0.10 and 6 percent at pi = 0.30; in general coupling above g_2(delta) = S / 2 amplifies the observed correlation and below it attenuates, with g_2 = 1 at the human-replica point; the Layer B pilot realized the crossing on real text, Att 0.895 at p = 0 to 1.135 at p = 1 with the crossing near p = 0.44, at kappa = 0.864 and delta = 0.536, not the amanuensis cell itself. Under rho_T nothing inflates (Prop. 17), the amanuensis cell is partial disattenuation that never completes, and no machine is harmless; Att, its thresholds, its monotonicity results and lane 4's metrics are unchanged. board.md, lane1-open-questions.md and the pivot memo's line 247 carry the decision; lane 4's CONVENTIONS.md and README.md wording that still calls N2 open, and SPEC 1.1 and 1.3, are listed for their owners.
