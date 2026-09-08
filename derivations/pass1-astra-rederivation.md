# Verification pass 1 — Astra independent re-derivation

Source scope: SPEC.md §§1.1–1.5 and §7 only. Method: symbolic derivation, without simulation or analysis code. Equation identifiers are local to this document. “Bias” below is a population estimand discrepancy, not the finite-sample expectation of a sample Pearson correlation.

## 1. Two-process mixture: notation, assumptions, and ambiguity resolutions

### 1.1 Notation and estimands

Let authorship be A ∈ {H, M}, with P(A = M) = π and a = 1 − π. For each class A, write μθ,A = E(θ | A), μx,A = E(x | A), νA = E(w | A), tA = Var(θ | A), vA = Var(x | A), and qA = Var(w | A). Write KA = Cov(x, w | A), ρA = Cor(θ, w | A), and rH = Cor(x, w | H). All relevant second moments are finite. Assume tA, qA, and vA are positive; otherwise the corresponding Pearson correlations are undefined. Endpoint mixture weights refer to the same specified component laws even when one component has zero population weight.

**Primary target resolution:** interpret SPEC §1.3's ρH as Cor(θ, w | H), consistent with the latent-trait validity coefficient in §1.1. Also carry the alternative observable human target rH. The unconditional target explicitly written in §1.1 is denoted ρall = Cor(θ, w); it need not equal ρH when authorship selects different respondents. Its formula is given in (18).

The naive population estimate is ρobs = Cor(x, w) in the unfiltered mixture. Raw score validity and latent-trait validity differ even in a completely human sample when human measurement error is nonzero.

### 1.2 Measurement and outcome assumptions

“Clean outcome w” means the outcome is not replaced or corrupted by machine authorship. It does **not**, on its own, imply equal outcome distributions across authorship groups, or rule out association between x and outcome residuals. I make the needed additional assumptions explicitly.

Use the within-class linear projection of w on θ:

\[
\begin{aligned}
w &= \nu_A+\beta_A(\theta-\mu_{\theta,A})+U_A,\\
\beta_A &= \rho_A\sqrt{q_A/t_A},\qquad
E(U_A\mid A)=0,\qquad \operatorname{Cov}(\theta,U_A\mid A)=0,\\
\operatorname{Var}(U_A\mid A)&=q_A(1-\rho_A^2).
\end{aligned}
\tag{01}
\]

This projection requires no Gaussian distribution and no causal interpretation of βA. It also does not require the conditional mean E(w | θ, A) to be exactly linear. Stronger residual assumptions needed for the deletion example are stated there.

For humans, use the classical additive process, with E(e | H) = 0, Cov(e, θ | H) = 0, and the additional outcome exclusion Cov(e, UH | H) = 0:

\[
x=\theta+e\quad(A=H),\qquad
\mu_{x,H}=\mu_{\theta,H},\qquad
v_H=t_H+s_H^2,\qquad
\lambda_H:=\operatorname{rel}_H=\frac{t_H}{t_H+s_H^2}.
\tag{02}
\]

Here sH² is the SPEC's `s2_H`: **human error variance**. In contrast, vM = sM² is the SPEC's `s2_M`: **total machine-score variance**. These are not corresponding variance components. I retain their literal definitions. Thus the literal homogenization condition is vM < sH², which is stronger than vM < vH. I do not silently redefine sH² as total human-score variance.

For machines, retain the actual correlation definition c = Cor(x, θ | M). A convenient projection representation is

\[
\begin{aligned}
x&=\mu_{x,M}+c\sqrt{v_M/t_M}(\theta-\mu_{\theta,M})+Z_M\quad(A=M),\\
E(Z_M\mid M)&=0,\qquad \operatorname{Cov}(Z_M,\theta\mid M)=0,\\
\operatorname{Var}(Z_M\mid M)&=v_M(1-c^2),\qquad -1\le c\le1.
\end{aligned}
\tag{03}
\]

At c = 0, impose the SPEC's stronger statement x ⟂ θ | M, not merely zero correlation. For the main derivation, also impose the **outcome-residual exclusion** Cov(ZM, UM | M) = 0. Without this exclusion, independence of x and θ does not imply zero covariance of x and w. Equation (12) records the omitted term if this assumption is relaxed. Independent machine residuals from (θ, UM) give one sufficient construction, but independence is stronger than the moment calculations need.

The SPEC's intended coupling grid is 0 ≤ c ≤ 1. I extend the sign map to −1 ≤ c < 0 explicitly to identify where negative coupling could reverse a sign.

### 1.3 What is held fixed

For the principal, closed-form grid, assume the joint respondent distribution (θ, w) is the same in both authorship classes: A ⟂ (θ, w). Thus tH = tM = t, qH = qM = q, νH = νM = ν, and ρH = ρM = ρall = ρ. Authorship changes the measurement process; it does not select a different respondent population in this principal model.

Hold t, q, ρ, the common trait and outcome means, sH², vM, μx,H, and μx,M fixed while varying π and c. Accordingly, λ = λH is fixed. Varying c at fixed vM changes Var(ZM | M) as in (03). Section 2.4 drops respondent-distribution invariance, while holding each component's parameters fixed across its grid.

Set k = vM/vH > 0, Δx = μx,H − μx,M, and d = Δx/√vH. The literal SPEC homogenization assumption is k < 1 − λ; the weaker total-variance comparison is k < 1. In particular, literal strict homogenization with positive vM is impossible if λ = 1.

**Further specification resolutions:** the correlation definition of c takes precedence over §1.4's proposed covariance shortcut. The covariance shortcut is valid only under an additional scale restriction, derived in (14). Also, (π, c, relH, mean gap) alone do not determine the answer: the machine-to-human variance ratio k is needed, unless a separate restriction fixes it. A raw mean gap must be accompanied by a score scale; d supplies that scale.

## 2. Observed moments and closed-form bias

### 2.1 Mixture identities before imposing c = 0

Define Δw = νH − νM. Total expectation gives

\[
E(x)=a\mu_{x,H}+\pi\mu_{x,M},\qquad
E(w)=a\nu_H+\pi\nu_M.
\tag{04}
\]

Total variance gives

\[
V_x:=\operatorname{Var}(x)=a v_H+\pi v_M+\pi a\Delta_x^2,\qquad
V_w:=\operatorname{Var}(w)=a q_H+\pi q_M+\pi a\Delta_w^2.
\tag{05}
\]

Total covariance gives

\[
C_{xw}:=\operatorname{Cov}(x,w)
=aK_H+\pi K_M+\pi a\Delta_x\Delta_w.
\tag{06}
\]

The last term is missing from the SPEC's §1.4 identity unless ΔxΔw = 0. Equal outcome means, as in the principal model, are sufficient; equal score means are not required.

Define the estimand discrepancies precisely:

\[
\rho_{\mathrm{obs}}=\frac{C_{xw}}{\sqrt{V_xV_w}},\qquad
B_H=\rho_{\mathrm{obs}}-\rho_H,\qquad
B_{x,H}=\rho_{\mathrm{obs}}-r_H,\qquad
B_{\mathrm{all}}=\rho_{\mathrm{obs}}-\rho_{\mathrm{all}}.
\tag{07}
\]

### 2.2 Exact zero-coupling result under the principal model

First derive the human covariance from x = θ + e and the exclusions in §1.2:

\[
K_H=\operatorname{Cov}(\theta,w\mid H)
=\rho\sqrt{tq},\qquad
r_H=\frac{K_H}{\sqrt{v_Hq}}=\rho\sqrt{\lambda}.
\tag{08}
\]

Define D = a + πk + πa d². At c = 0, independence from θ and the outcome-residual exclusion eliminate both machine covariance terms:

\[
K_M=0,\qquad
C_{xw}=a\rho\sqrt{tq},\qquad
V_x=v_HD,\qquad V_w=q.
\tag{09}
\]

Consequently the requested zero-coupling closed forms are

\[
\begin{aligned}
\rho_{\mathrm{obs}}(\pi,0)
&=\rho\sqrt{\lambda}\,\frac{a}{\sqrt D}
=r_H\frac{a}{\sqrt D},\\
B_H(\pi,0)=B_{\mathrm{all}}(\pi,0)
&=\rho\left(\sqrt{\lambda}\frac{a}{\sqrt D}-1\right),\\
B_{x,H}(\pi,0)
&=r_H\left(\frac{a}{\sqrt D}-1\right).
\end{aligned}
\tag{10}
\]

At π = 0, the latent-target discrepancy is already ρ(√λ − 1), whereas the observable-human discrepancy is zero. This separates ordinary human measurement error from the added contamination effect.

For any 0 < π ≤ 1 and k > 0,

\[
D-a^2=\pi\bigl[k+a(1+d^2)\bigr]>0.
\tag{11}
\]

Thus, if rH ≠ 0, zero coupling strictly reduces |ρobs| below |rH|, and therefore below or equal to |ρ|. For 0 < π < 1 the sign is preserved; at π = 1 the correlation is zero. “Attenuation” means movement toward zero: its signed bias is negative for positive targets and positive for negative targets.

A smaller k shrinks the denominator and partially offsets dilution at fixed π, λ, and d. It cannot overcome dilution at c = 0. A larger |d| increases attenuation. With d = 0 and k = 1 the multiplier relative to rH is a; as k tends to zero with π < 1 it tends to √a. The zero-variance machine limit is only a limit, since c itself is undefined at vM = 0. Accordingly, the SPEC's suggestion that the mean gap determines the net direction is not correct for this zero-coupling model: it changes the amount of attenuation, not its direction.

### 2.3 General coupling

Before imposing the outcome-residual exclusion, expanding (01) and (03) yields

\[
\begin{aligned}
K_M&=c\rho_M\sqrt{v_Mq_M}+\kappa_M,
\qquad \kappa_M:=\operatorname{Cov}(Z_M,U_M\mid M),\\
|\kappa_M|&\le
\sqrt{v_Mq_M(1-c^2)(1-\rho_M^2)}.
\end{aligned}
\tag{12}
\]

The bound is Cauchy–Schwarz applied to the two projection residuals. Thus c alone cannot determine the machine–outcome covariance. The following results set κM = 0 as explicitly assumed; they do not follow from “clean outcome” alone.

In the principal model, define N = a√λ + πc√k. Then

\[
\begin{aligned}
C_{xw}&=\rho\sqrt{v_Hq}\,N,\\
\rho_{\mathrm{obs}}(\pi,c)&=\rho\frac{N}{\sqrt D},\\
B_H(\pi,c)=B_{\mathrm{all}}(\pi,c)&=
\rho\left(\frac{N}{\sqrt D}-1\right),\\
B_{x,H}(\pi,c)&=
\rho\left(\frac{N}{\sqrt D}-\sqrt\lambda\right).
\end{aligned}
\tag{13}
\]

These expressions remain valid at ρ = 0, yielding zero observed correlation under the specified exclusions. No division by ρ is needed.

When KH ≠ 0, the covariance multiplier corresponding to the actual coupling correlation is

\[
\gamma:=\frac{K_M}{K_H}
=c\sqrt{\frac{v_M}{t}}
=c\sqrt{\frac{k}{\lambda}},\qquad
K_M=cK_H\ \text{for every }c\ \Longleftrightarrow\ v_M=t
\ \Longleftrightarrow\ k=\lambda.
\tag{14}
\]

For c = 0 the equality is trivially true without the scale restriction. Otherwise, replacing γ with c generally changes the model. Under the additional restriction k = λ, (13) becomes ρobs = rH(a + πc)/√D, which is the covariance-dilution form suggested in §1.4.

An explicit variance decomposition checks the achievable magnitude:

\[
D-N^2=
 a(1-\lambda)+\pi k(1-c^2)
 +\pi a\left[(\sqrt\lambda-c\sqrt k)^2+d^2\right]
\ \ge 0.
\tag{15}
\]

The three contributions are human residual variance, machine residual variance, and between-process differences in signal slope and intercept, each divided by vH. Hence |ρobs| ≤ |ρ| for the full −1 ≤ c ≤ 1 grid in the principal model. For nonnegative c, the mixture may improve on the noisy human observable correlation rH, but cannot exceed the latent validity magnitude |ρ|.

For 0 < π ≤ 1 and ρ ≠ 0, the exact boundary between attenuation and inflation **relative to |rH|**, restricted to c ≥ 0, is

\[
 c_H(\pi)=\frac{\sqrt\lambda(\sqrt D-a)}{\pi\sqrt k},\qquad
 |\rho_{\mathrm{obs}}|\begin{cases}
 <|r_H|,&0\le c<c_H(\pi),\\
 =|r_H|,&c=c_H(\pi),\\
 >|r_H|,&c>c_H(\pi).
 \end{cases}
\tag{16}
\]

Only boundaries inside [0, 1] are reachable. A sufficiently large mean gap can push the threshold above 1. At π = 1 this threshold is √λ, as expected from ρobs = cρ. At fixed c > 0, changing k affects the numerator as well as the denominator; the zero-coupling denominator-only argument does not apply.

The SPEC's “c near 1 is nearly harmless” statement also needs scale and mean qualifications. Even c = 1 can lower validity through differing score scales or means across authorship groups, as the last term of (15) shows. Conversely, if k = 1, d = 0, and c = √λ, the observable correlation equals rH for every π. A machine that reports θ exactly has c = 1, k = λ, and d = 0; it removes human measurement noise as π rises. High coupling alone does not specify which of these situations applies.

### 2.4 General authorship selection and the unconditional latent target

Drop A ⟂ (θ, w), retaining the classwise human model and κM = 0. The exact covariance is now

\[
C_{xw}=
 a\rho_H\sqrt{t_Hq_H}
 +\pi c\rho_M\sqrt{v_Mq_M}
 +\pi a\Delta_x\Delta_w.
\tag{17}
\]

Equations (05), (07), and (17) give a closed form for every bias definition without equal class means, trait variances, outcome variances, or trait–outcome correlations. At c = 0, delete only the second term in (17); the between-class term remains. If residual exclusion is relaxed, add πκM. The extra parameters cannot be recovered from π, c, λH, and Δx alone.

For the unconditional latent target in SPEC §1.1, set Δθ = μθ,H − μθ,M. Then

\[
\rho_{\mathrm{all}}=
\frac{
 a\rho_H\sqrt{t_Hq_H}
 +\pi\rho_M\sqrt{t_Mq_M}
 +\pi a\Delta_\theta\Delta_w
}{
 \sqrt{\left(a t_H+\pi t_M+\pi a\Delta_\theta^2\right)V_w}
}.
\tag{18}
\]

This target itself changes with π when the respondent distributions differ. In the principal model it reduces to ρH, so the two latent-target interpretations coincide there.

## 3. Homogenization, between-item correlations, and outcome attenuation

### 3.1 What the single-indicator specification does not determine

The scalar mixture does not specify Cov(xj, xk | M). Smaller marginal variances therefore do not, by themselves, imply higher machine between-item correlations. A joint multi-item model is an additional assumption.

Here is a sufficient construction at c = 0. Let T be the centered respondent trait, with Var(T) = t. For humans, use a one-factor extension of the classical measurement model, with positive loadings ℓj and mutually uncorrelated item errors independent of the trait and outcome residual. The unit-loading special case is exactly the scalar model:

\[
\begin{aligned}
x_j\mid H&=\mu_{j,H}+\ell_j T+\varepsilon_j,\qquad
\operatorname{Var}(\varepsilon_j\mid H)=h_j,\\
v_{j,H}&=\ell_j^2t+h_j,\qquad
K_{jk,H}:=\operatorname{Cov}(x_j,x_k\mid H)=\ell_j\ell_k t
\quad(j\ne k).
\end{aligned}
\tag{19}
\]

For machines, posit a centered shared response-style factor G, independent of (θ, w), with Var(G) = g > 0. Let the item residuals ηj be mutually uncorrelated and independent of G, θ, and w, with positive loadings bj:

\[
\begin{aligned}
x_j\mid M&=\mu_{j,M}+b_jG+\eta_j,\qquad
\operatorname{Var}(\eta_j\mid M)=m_j,\\
v_{j,M}&=b_j^2g+m_j,\qquad
K_{jk,M}:=\operatorname{Cov}(x_j,x_k\mid M)=b_jb_k g,\\
\operatorname{Cov}(x_j,\theta\mid M)&=0,\qquad
\operatorname{Cov}(x_j,w\mid M)=0.
\end{aligned}
\tag{20}
\]

All residual variances are nonnegative. Positive loadings fix a common item orientation; with mixed loading signs, comparisons must instead specify signed correlations or their magnitudes. Under the stated orientation,

\[
\begin{aligned}
r_{jk,H}&=
\frac{1}{\sqrt{\left(1+h_j/(\ell_j^2t)\right)
                         \left(1+h_k/(\ell_k^2t)\right)}},\\
r_{jk,M}&=
\frac{1}{\sqrt{\left(1+m_j/(b_j^2g)\right)
                         \left(1+m_k/(b_k^2g)\right)}}.
\end{aligned}
\tag{21}
\]

The exact condition for larger positive machine correlations in this model is

\[
r_{jk,M}>r_{jk,H}
\ \Longleftrightarrow\
\left(1+\frac{m_j}{b_j^2g}\right)
\left(1+\frac{m_k}{b_k^2g}\right)
<
\left(1+\frac{h_j}{\ell_j^2t}\right)
\left(1+\frac{h_k}{\ell_k^2t}\right).
\tag{22}
\]

A sufficient condition is a weakly smaller machine residual-to-common-factor variance ratio for each item, with at least one strict inequality. This can coexist with vj,M < vj,H for both items, or with the stronger literal SPEC condition vj,M < hj. Homogenization must preserve shared item variation while reducing item-specific variation enough to satisfy (22).

Under the principal respondent-distribution assumptions, every such item also has zero machine outcome covariance and hence obeys the zero-coupling attenuation result (10), with that item's parameters. The latent coefficient Cor(θ, w) itself stays fixed. What attenuates is the correlation using x as its proxy. High internal consistency can therefore coexist with zero validity for the respondent trait among machine cases.

Scaling every machine item by a positive constant changes its variance but leaves all its correlations unchanged. Alternatively, low-variance independent machine items have zero between-item correlations. Both observations refute an implication from homogenization alone. If all machine scores are constant, their Pearson correlations are undefined, not automatically one.

For completeness, the pooled item covariance has another source of apparent consistency. With Δj = μj,H − μj,M,

\[
\operatorname{Cov}(x_j,x_k)
=aK_{jk,H}+\pi K_{jk,M}+\pi a\Delta_j\Delta_k.
\tag{23}
\]

Same-direction class mean gaps can increase pooled covariance. This is distinct from correlations calculated within machine cases; pooled correlations also depend on the corresponding marginal variances.

### 3.2 Exact existence example, without simulation

Take centered θ and U independent with variance 1, and w = θ + U. Human items are xj = θ + εj, with independent errors of variance 1. Machine items are xj = G + ηj, with Var(G) = 1/4 and mutually independent residuals of variance 1/16. All machine variables are independent of (θ, U); all class score means are zero. For distinct items,

\[
\begin{aligned}
v_{j,H}&=2, & r_{jk,H}&=\tfrac12, & r_H&=\tfrac12,\\
v_{j,M}&=\tfrac{5}{16}<s_{H,j}^2=1,
& r_{jk,M}&=\tfrac45,
& \operatorname{Cor}(x_j,w\mid M)&=0,\\
\rho&=\tfrac{1}{\sqrt2}, &
\rho_{\mathrm{obs}}(\pi,0)&=
\frac{1-\pi}{\sqrt{\,2\left[2(1-\pi)+5\pi/16\right],}}.
\end{aligned}
\tag{24}
\]

Thus the SPEC's literal homogenization inequality, inflated machine item correlations, and attenuated observed outcome validity can all hold simultaneously. The shared machine factor supplies the extra assumption that makes this possible.

## 4. Sign-stable and sign-flipped regions of the (π, c) grid

### 4.1 Principal model

Assume ρ ≠ 0 and positive variances. Since D > 0, both latent target ρ and observable human target rH have the same sign. Equation (13) gives the complete sign classification:

\[
\begin{array}{lll}
\text{same sign as the human target}&\Longleftrightarrow&
N=(1-\pi)\sqrt\lambda+\pi c\sqrt k>0,\\
\text{zero observed correlation}&\Longleftrightarrow&N=0,\\
\text{opposite sign to the human target}&\Longleftrightarrow&N<0.
\end{array}
\tag{25}
\]

On the SPEC's grid 0 ≤ c ≤ 1, every point with π < 1 is sign-stable. At π = 1, c > 0 is sign-stable and c = 0 gives zero. There is **no sign-flipped region on this grid** under these assumptions. If ρ = 0, all observed correlations are zero and a relative sign classification is inapplicable.

On the extended negative-coupling grid, the zero boundary can be written in either coordinate:

\[
 c_{\mathrm{flip}}(\pi)=
 -\frac{(1-\pi)\sqrt\lambda}{\pi\sqrt k}
 \quad(0<\pi\le1),\qquad
 \pi_{\mathrm{flip}}(c)=
 \frac{\sqrt\lambda}{\sqrt\lambda-c\sqrt k}
 \quad(-1\le c<0).
\tag{26}
\]

For fixed π > 0, c above the boundary preserves the sign and c below it reverses the sign. For fixed c < 0, π below the boundary preserves the sign and π above it reverses the sign. Equality gives zero. At π = 0 the sign is always the human sign. A reversal is possible for at least one admissible negative coupling precisely when

\[
\pi>\frac{\sqrt\lambda}{\sqrt\lambda+\sqrt k}.
\tag{27}
\]

At equality, c = −1 gives zero but not reversal. The score mean gap d has no effect on these sign boundaries because it occurs only in a positive denominator.

### 4.2 Authorship selection or differing outcome means

A universal grid cannot be given without fixing the additional parameters in (17). For an exact conditional grid, suppose ρH ≠ 0 and set h = ρH√(tHqH), m = ρM√(vMqM), b = ΔxΔw, L = m/h, and B = b/h. Then

\[
\frac{C_{xw}}{h}
=(1-\pi)+\pi cL+\pi(1-\pi)B
=1+\pi(cL-1+B)-B\pi^2.
\tag{28}
\]

The region where this expression is positive is sign-stable relative to ρH or rH; the negative region is sign-flipped; zero is the boundary. For π > 0 and L ≠ 0, the boundary is

\[
 c=-\frac{(1-\pi)(1+\pi B)}{\pi L}.
\tag{29}
\]

If L > 0, points above this boundary preserve the sign; if L < 0, the inequality reverses. If L = 0, the sign is independent of c. At π = 0 it is the human sign regardless of L or B.

Even at c = 0, for 0 < π < 1,

\[
\text{sign reversal relative to }\rho_H
\ \Longleftrightarrow\ 1+\pi B<0
\ \Longleftrightarrow\ B<-\frac1\pi.
\tag{30}
\]

For example, when h > 0, a sufficiently negative product ΔxΔw can reverse the pooled association. This is a between-class mean effect, not homogenization. Opposite classwise trait–outcome associations can also cause a reversal at c > 0 through L < 0. If κM is allowed, (28) acquires the additional term πκM/h. Neither that term nor the other selection terms is determined by c.

The sign of the unconditional latent target ρall can also differ from the human sign in this general setting. To compare against that target, use Cxwρall > 0 for stability and Cxwρall < 0 for reversal, with ρall given by (18); the human-target map cannot automatically be reused.

## 5. Deletion-selection and the surviving human population

### 5.1 Residual contamination

Let S = 1 mean the detector passes a response and the response survives deletion. Define se = P(S = 0 | M) and sp = P(S = 1 | H). These are population-average classwise rates, not assumptions of trait-independent detection. Total probability and Bayes' rule give

\[
\begin{aligned}
P(S=1)&=(1-\mathrm{se})\pi+\mathrm{sp}(1-\pi),\\
\pi':=P(M\mid S=1)&=
\frac{(1-\mathrm{se})\pi}
     {(1-\mathrm{se})\pi+\mathrm{sp}(1-\pi)}.
\end{aligned}
\tag{31}
\]

The denominator must be positive. The expression does not depend on errors being independent of θ. For 0 < π < 1 and a positive pass probability,

\[
\pi'<\pi\quad\Longleftrightarrow\quad \mathrm{se}+\mathrm{sp}>1.
\tag{32}
\]

Thus residual contamination is not automatically small. When se = 1, sp > 0, and π < 1, it is exactly zero, yet selection among humans can remain.

### 5.2 Conditioning on detection changes the trait distribution

Assume sp > 0 and define qH(t) = P(S = 1 | θ = t, H). Bayes' rule for the conditional law, followed by taking any integrable function g of the trait, gives

\[
\begin{aligned}
 dP(\theta\mid H,S=1)&=
 \frac{q_H(\theta)}{\mathrm{sp}}\,dP(\theta\mid H),\\
 E[g(\theta)\mid H,S=1]-E[g(\theta)\mid H]
 &=\frac{\operatorname{Cov}(g(\theta),q_H(\theta)\mid H)}{\mathrm{sp}}.
\end{aligned}
\tag{33}
\]

This formula applies to continuous, discrete, and mixed trait distributions. The entire trait distribution is unchanged if and only if qH(θ) = sp almost surely, equivalently S ⟂ θ | H. A nonconstant pass probability changes the distribution, although some individual moments can remain unchanged.

Let F denote fluency. As a sufficient model of the SPEC's fluency mechanism, suppose the detector's human pass probability depends on θ through F, so that S ⟂ θ | F, H, and set s(f) = P(S = 1 | F = f, H). Then

\[
 q_H(t)=\int s(f)\,dP(F=f\mid\theta=t,H)
       =E[s(F)\mid\theta=t,H].
\tag{34}
\]

If lower fluency receives lower pass probabilities and the conditional fluency distribution varies with θ in a way that makes this expectation nonconstant, surviving humans are reweighted by trait. Merely asserting a correlation between F and θ is not a mathematical guarantee for every possible detector function; the required condition is a nonconstant qH(t). An increasing pass function combined with an ordered shift in fluency distributions is one sufficient route, provided it changes the expectation.

This argument already explains selection without a collider. The path θ → F → S weights the sample when conditioning on S. A collider mechanism additionally arises if S is a common effect of fluency and another variable associated with the outcome or measurement error, for example F → S ← Q. That mechanism can induce residual associations as well. The exact conditioning equations do not require a particular causal graph.

To express the broader issue, let Z = (θ, w, x) within humans and qZ(z) = P(S = 1 | Z = z, H). For any integrable g(Z),

\[
\begin{aligned}
 dP(Z\mid H,S=1)&=\frac{q_Z(Z)}{\mathrm{sp}}\,dP(Z\mid H),\\
 E[g(Z)\mid H,S=1]-E[g(Z)\mid H]
 &=\frac{\operatorname{Cov}(g(Z),q_Z(Z)\mid H)}{\mathrm{sp}}.
\end{aligned}
\tag{35}
\]

Taking g to be θ, w, x, their squares, and their cross-products identifies the changes that enter the two validity correlations. Independence of detection from θ alone does not constrain all these moments.

### 5.3 Explicit correlation distortion under selection only on the trait

For a sufficient example, strengthen the human model to w = α + βθ + U and x = θ + e, with e and U centered, mutually independent, independent of θ, and with fixed variances sH² and u². Suppose S depends only on θ and independent detector randomness, so the residual distributions remain unchanged after selection. Write tS = Var(θ | H, S = 1) > 0. Then

\[
\begin{aligned}
\operatorname{Cor}(\theta,w\mid H,S=1)
 &=\frac{\beta\sqrt{t_S}}{\sqrt{\beta^2t_S+u^2}},\\
\operatorname{Cor}(x,w\mid H,S=1)
 &=\frac{\beta t_S}
 {\sqrt{(t_S+s_H^2)(\beta^2t_S+u^2)}}.
\end{aligned}
\tag{36}
\]

The corresponding original human correlations replace tS by tH. If selection reduces trait variance, β ≠ 0, and u² > 0, the latent correlation strictly decreases in magnitude. The observable correlation likewise strictly decreases when at least one of u² or sH² is positive. Selection can instead increase trait variance and increase these magnitudes. The direction is not universal.

The unstandardized regression slope of w on θ stays β in this particular selection-only-on-θ model. A changed correlation does not imply a changed slope. Even a correct measurement-error adjustment in the surviving sample recovers its selected latent correlation, not necessarily the original population's ρH.

### 5.4 Why substituting π′ into the original mixture is insufficient

Define KA,S = Cov(x, w | A, S = 1), and define Δx,S and Δw,S as differences between the surviving class means. The actual surviving covariance is

\[
\operatorname{Cov}(x,w\mid S=1)
=(1-\pi')K_{H,S}+\pi'K_{M,S}
 +\pi'(1-\pi')\Delta_{x,S}\Delta_{w,S}.
\tag{37}
\]

The analogous selected variances use the selected class variances and selected mean gaps. Selection can also change within-machine coupling and the residual exclusions. Replacing π with π′ while retaining the original class moments is justified only if selection preserves those moments. When π′ = 0, (37) becomes KH,S, not necessarily KH. Equations (33)–(36) exhibit the bias that can survive complete removal of machines.

### 5.5 Resolution of the SPEC's “unbiased only if” claim

For preservation of the **entire human trait distribution**, S ⟂ θ | H is both necessary and sufficient, as (33) proves. For preservation of the **entire human joint law** of (θ, w, x), S ⟂ (θ, w, x) | H is both necessary and sufficient, by (35). The latter condition is a sufficient protection for both human validity correlations.

For preservation of one particular correlation, however, trait-independent detection is neither generally necessary nor generally sufficient. Two exact counterexamples distinguish these claims.

**Not necessary for a particular correlation.** Let human θ take +1 with probability 1/4 and −1 with probability 3/4. Pass +1 cases with probability 1 and −1 cases with probability 1/9. Use the independent residual model of §5.3, with positive residual variances. Then

\[
\begin{aligned}
\mathrm{sp}&=\tfrac14+\tfrac34\cdot\tfrac19=\tfrac13,\\
P(\theta=+1\mid H,S=1)&=\tfrac34,\\
E(\theta\mid H)&=-\tfrac12,\qquad E(\theta\mid H,S=1)=\tfrac12,\\
 t_H&=1-(-\tfrac12)^2=\tfrac34
     =1-(\tfrac12)^2=t_S.
\end{aligned}
\tag{38}
\]

Detection depends strongly on θ, and its distribution and mean change, but its variance does not. Both correlations in (36) therefore equal their original human values. Thus “only if” is false as a universal necessity claim for the specified correlation targets.

**Not sufficient without restrictions on other variables.** Let human θ be equally likely ±1, and independently let U be equally likely −2, −1, +1, or +2. Set w = θ + U, and pass exactly when |U| = 1. This detector is independent of θ, but selects outcome residuals. Its implications are

\[
\begin{aligned}
\mathrm{sp}&=\tfrac12,\qquad S\perp\theta\mid H,\\
\operatorname{Var}(U\mid H)&=\tfrac52,\qquad
\operatorname{Var}(U\mid H,S=1)=1,\\
\rho_H&=\frac{1}{\sqrt{1+5/2}}=\sqrt{\tfrac27},\qquad
\operatorname{Cor}(\theta,w\mid H,S=1)=\frac1{\sqrt2}.
\end{aligned}
\tag{39}
\]

This mechanism is permitted unless an additional exclusion prevents detector dependence on outcome residuals. The outcome is still clean; its distribution changes through selection. Independent classical score error can be added without changing the counterexample for the latent target.

Both examples can coexist with perfect machine sensitivity and positive human specificity, so that π′ = 0. Remaining machine contamination is not the reason for either conclusion. With π′ > 0, preserving the human distribution also does not by itself remove mixture bias. With π′ = 0, a raw human score correlation still requires a reliability adjustment to estimate latent ρH.

The supported deletion result is therefore: detect-and-delete can reduce contamination while changing the human population being analyzed; complete removal of machine cases does not guarantee valid estimation of the original human target. Fluency-dependent selection produces this problem when its pass probabilities change the relevant trait or joint moments. A universal necessity theorem for one correlation does not follow from the SPEC's premises.

## Self-check log

- **(01):** Recomputed the projection coefficient directly as Cov(θ, w | A)/tA. Subtracting that projection gives a zero-mean residual orthogonal to θ. Expanding its variance gives qA − Cov(θ, w | A)²/tA = qA(1 − ρA²), checking every projection identity.
- **(02):** Took the expectation and expanded Var(θ + e | H) directly. The centered, orthogonal error leaves the trait mean unchanged and adds only sH² to variance. Dividing true-score variance by the resulting total variance gives λH. This also checks that the SPEC's two variance labels refer to different components.
- **(03):** Started instead with the projection of x on θ within M. Its slope is Cov(x, θ | M)/tM = c√(vM/tM). Subtracting it gives the displayed zero-mean, orthogonal residual with variance vM − c²vM. Reconstructing x recovers total variance vM and correlation c. Independence at c = 0 remains a separately stated assumption, not an implication of projection.
- **(04):** Recomputed both means by partitioning the expectation into H and M contributions. The weights sum to one, and each endpoint returns its component mean.
- **(05):** Expanded E(x²) − E(x)² using the component raw second moments. The remaining mean terms reduce to πaΔx². Repeated the same calculation for w, obtaining πaΔw² and the displayed within-class terms.
- **(06):** Expanded E(xw) − E(x)E(w) from component raw cross-moments. The mean contribution is πa(μx,H − μx,M)(νH − νM), confirming both its coefficient and sign.
- **(07):** Reconstructed the population Pearson coefficient from centered covariance and marginal standard deviations. Subtracted each explicitly defined target separately; no finite-sample expectation or implicit reliability correction enters these definitions.
- **(08):** Expanded Cov(θ + e, βH(θ − μθ,H) + UH | H). Only βHt survives. Dividing first by √(tq) and then by √(vHq) gives ρ and ρ√λ respectively.
- **(09):** At c = 0, directly evaluated the covariance of the machine residual with β(θ − μθ) + U; both terms vanish under the stated exclusions. Weighting the remaining human covariance gives aρ√(tq). Independently normalized the score variance in (05) by vH, yielding D, and used the common outcome law to obtain q.
- **(10):** Directly divided aρ√(tq) by √(vHDq), then subtracted ρ and ρ√λ separately. Checked π = 0, which gives human measurement attenuation only, and π = 1, which gives zero observed correlation at c = 0.
- **(11):** Expanded D − (1 − π)² without using a previous attenuation result. The remaining terms are πk + πa + πad², all nonnegative and with πk strictly positive on the stated domain. This checks the strict attenuation claim independently of intuition about denominator compression.
- **(12):** Multiplied the centered machine and outcome projections directly. The signal–signal term is cρM√(vMqM); the two signal–residual terms vanish by orthogonality; the residual–residual term is κM. Applied Cauchy–Schwarz using the two residual variances to verify the bound, including its zero value if either residual variance vanishes.
- **(13):** Standardized x by √vH and w by √q before mixing. Their classwise covariances become ρ√λ and cρ√k, so the mixture covariance is ρN on that scale. Its score variance is D and outcome variance is one. Dividing and subtracting the two human targets reproduces all four lines. Setting c = 0 reproduces (10).
- **(14):** Independently divided the machine signal covariance cβ√(vMt) by the human covariance βt. This gives c√(vM/t), or c√(k/λ). Equality with c for all couplings requires vM = t when KH is nonzero; the single point c = 0 is the explicit exception.
- **(15):** Re-derived the result as a residual-variance decomposition after projecting normalized x on the common standardized trait. Human and machine residual variances contribute a(1 − λ) and πk(1 − c²); variance of the two class slopes contributes πa(√λ − c√k)²; class intercept differences contribute πad². A separate expansion cancels to D − [a√λ + πc√k]², checking each term and its coefficient.
- **(16):** Solved a√λ + πc√k = √λ√D directly for c. Division by π√k is valid and positive on the stated domain, preserving the inequality direction. Checked that the comparison is of magnitudes with c ≥ 0, and that π = 1 reduces the threshold to √λ.
- **(17):** Recomputed each class covariance with its own trait variance, outcome variance, and trait validity. Added the mean cross-term from a direct raw-moment expansion. This confirms that the machine scale is √(vMqM), whereas the human signal scale is √(tHqH); equal respondent distributions were not used.
- **(18):** Repeated the mixture raw-moment calculation with θ in place of x. Its covariance with w includes πaΔθΔw, and its variance includes πaΔθ². Dividing by its standard deviation and √Vw yields the display. Equal respondent laws reduce it to the common ρ.
- **(19):** Expanded both the single-item variance and the cross-item product. The factor contributes ℓj²t or ℓjℓkt, and only a single-item variance receives hj. The item residuals are centered, as required by the use of μj,H as the item mean; their cross-covariances and trait covariances are zero by assumption.
- **(20):** Repeated the expansion for the independent shared machine factor. It gives bj²g + mj and bjbkg. The machine item residuals are centered, as required by μj,M being the item mean. Independence from θ and w eliminates both validity covariances, while allowing nonzero covariance between different machine items.
- **(21):** Divided each cross-item covariance by the product of its item standard deviations. Factoring out the positive loadings and factor variance yields the two reciprocal square-root expressions; positivity prevents an omitted sign factor.
- **(22):** Compared the positive reciprocal square roots in (21), inverted the comparison, and squared the positive denominators. This gives the displayed product inequality with the correct direction. It depends on residual-to-shared variance ratios, not on marginal variance alone.
- **(23):** Expanded pooled E(xjxk) − E(xj)E(xk) independently. The class-mean terms reduce to πaΔjΔk, and the remaining terms are the weighted within-class covariances.
- **(24):** Hand-computed Var(w) = 2; human item variance 2, cross-item covariance 1, and outcome covariance 1; machine item variance 1/4 + 1/16 = 5/16 and cross-item covariance 1/4. These give human correlations 1/2, machine item correlation 4/5, and latent validity 1/√2. Directly mixing gives score variance 2a + 5π/16 and outcome covariance a, reproducing the final expression. No random samples or analysis code were used.
- **(25):** Factored the principal observed correlation as ρ times N/√D. Since √D and √λ are positive, the sign of N alone distinguishes preservation, zero, and reversal relative to either nonzero human target.
- **(26):** Solved N = 0 first for c and separately for π. Substitution of either solution into a√λ + πc√k returns zero. For c < 0, the π-boundary lies strictly between zero and one; the formula for c at π = 1 returns zero.
- **(27):** Minimized N over the allowed coupling interval at c = −1. Solving (1 − π)√λ − π√k < 0 gives the strict threshold. Equality yields a zero at c = −1, verifying the distinction between cancellation and reversal.
- **(28):** Divided the independently derived covariance (17) by nonzero h, then expanded (1 − π) + πcL + π(1 − π)B. The constant, linear, and quadratic terms are 1, π(cL − 1 + B), and −Bπ² respectively.
- **(29):** Set the unexpanded expression in (28) to zero and isolated πcL. Dividing by πL gives the boundary, and the sign of L supplies the stated direction of the stable half-plane. The L = 0 exception does not require dividing by zero.
- **(30):** Set c = 0 before simplifying: the normalized covariance becomes (1 − π)(1 + πB). For 0 < π < 1 its first factor is positive, so reversal is exactly 1 + πB < 0, equivalently B < −1/π.
- **(31):** Counted surviving probability mass separately: machine mass π(1 − se), human mass (1 − π)sp. Their sum gives the pass probability; normalizing the machine mass gives π′. This calculation uses only averaged rates, not trait independence.
- **(32):** Multiplied π′ < π by its positive denominator, canceled the positive π, and collected the remaining terms as (1 − π)(sp − [1 − se]) > 0. This is equivalent to se + sp > 1 on the stated interior domain.
- **(33):** Applied Bayes' rule to an arbitrary trait event, obtaining its reweighting by qH/sp. Integrating g yields E[gqH]/sp; subtracting E[g] and using E[qH] = sp gives the covariance expression. Equality of the full trait laws requires this weight to be one almost surely.
- **(34):** Used iterated conditional expectation of the pass indicator given θ and F. The stated conditional-independence assumption replaces its inner expectation with s(F), leaving the conditional fluency average in the display.
- **(35):** Repeated the event-level Bayes calculation for the entire human vector Z. Normalization again gives E[qZ] = sp. Integrating g and subtracting its original mean produces the displayed covariance difference, without assuming independence from any component of Z.
- **(36):** Centered θ, x, and w at their selected means. Independence of the residuals from selection gives selected covariances Cov(θ, w) = Cov(x, w) = βtS, and variances tS, tS + sH², and β²tS + u². Dividing separately gives both displayed correlations, including the sign of β.
- **(37):** Treated the conditional population S = 1 as its own two-component mixture, with weights 1 − π′ and π′. Expanding its raw cross-moment minus its mean product produces the selected class covariances and the selected mean cross-term. At π′ = 0 it reduces to KH,S.
- **(38):** Computed surviving masses 1/4 and 1/12, with total 1/3. Their normalized probabilities are 3/4 and 1/4. Since θ² is identically one, subtracting the squared means gives variance 3/4 both before and after selection. Substitution into (36) confirms preservation of both correlations despite trait-dependent detection.
- **(39):** Enumerated the four equally weighted residual values by hand. Their mean is zero and second moment is 10/4; the two surviving values have mean zero and variance one. Independence of θ from U makes selection independent of θ and leaves its variance and its covariance with w equal to one. Outcome variances are 7/2 before selection and 2 after, giving √(2/7) and 1/√2.

DONE-PASS1-ASTRA
