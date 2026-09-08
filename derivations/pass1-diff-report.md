# Pass 1 diff report: lane 1 (Fable 5.1) against Astra (GPT family)

Reviewer pass, 2026-09-07. Objects diffed:

- `derivations/lane1-zero-coupling.md` (day 1, 400 lines, equations E1-E34, Props. 1-11)
- `derivations/pass1-astra-rederivation.md` (608 lines, equations 01-39, blind re-derivation)

Method. Every equation in both files was mapped through the symbol crosswalk in section 1,
then each disagreement was re-derived from the SPEC 1.2 model by the reviewer rather than
adjudicated by inspection. Numeric receipts for the fourteen checks quoted below come from
`scratchpad/pass1check.py`, run in this session; every one passed. I did not take either
document's self-check log as evidence. Agreements were treated as suspect until re-derived:
section 5 lists what survived that hunt.

Two documents outside the diff object were read because they change classifications:
`derivations/lane1-open-questions.md` (notation decisions N1-N3, questions Q1-Q10, and the
day-2 revisions) and `lane4-simulation/CONVENTIONS.md` (which convention the simulation
already codes).

---

## 1. Symbol crosswalk

The files are not mechanically comparable. Nothing below is a disagreement; it is
translation, and getting it wrong manufactures fake discrepancies.

| object | lane 1 | Astra |
| --- | --- | --- |
| contamination fraction | `pi` | `π`, with `a = 1 - π` |
| coupling, `Cor(x, theta \| M)` | `c` | `c` |
| human reliability | `rel_H` | `λ` |
| machine-to-human variance ratio | `kappa = s2_M / V_H` | `k = vM / vH` |
| standardized score mean gap | `delta` | `d` |
| covariance multiplier | `g = c sqrt(kappa/rel_H)` | `γ = c sqrt(k/λ)` |
| numerator | `N = (1-pi) + pi g` | `N = a sqrt(λ) + π c sqrt(k)` |
| variance factor | `Den` | `D` |
| **`Cor(x, w \| H)`** | **`rho_H`** (primary) | **`rH`** (secondary) |
| **`Cor(theta, w)`** | **`rho_T`** (secondary) | **`ρ`** (primary) |

The two numerators differ by an absorbed `sqrt(rel_H)`, because the two files divide by
different baselines. Once that is carried, the core results are the same expression:

    lane1:  rho_obs = rho_H * N/sqrt(Den)          Astra:  rho_obs = ρ * N/sqrt(D)

CHECK (passed, 324 grid points spanning pi in {.05,.3,.7}, c in {-.8,0,.4,1},
rel_H in {.5,.7,.95}, kappa in {.2,1,2.5}, delta in {0,.5,2}):
`lane1.Att * sqrt(rel_H) == Astra.rho_obs/ρ` to 1e-12. The two closed forms are
algebraically identical, not merely consistent. `Den == D` term by term.

---

## 2. Discrepancy table

Seventeen items. "Discrepancy" includes items where the files agree but the agreement
needed adjudication, because SPEC 7 exists to catch correlated confidence.

| # | item | lane 1 | Astra | class | verdict |
| --- | --- | --- | --- | --- | --- |
| D1 | which correlation is `rho_H` | `Cor(x,w\|H)` | `Cor(theta,w\|H)` | SPEC-AMBIGUITY | both internally consistent; crosswalk exact; needs Abhay's N2 decree |
| D2 | is `c = 1` harmless | harmless iff `kappa = rel_H`, `delta = 0` (line 62) | that machine *removes* human noise (line 229) | **LANE1-ERROR** | **Astra right.** That cell inflates. Day-1 file must be edited |
| D3 | "the homogenized amanuensis attenuates" (line 169) | unqualified | n/a | **LANE1-ERROR** (minor) | true only for `pi` below ~0.6 at `kappa=.2`; contradicts lane 1's own Prop. 4 |
| D4 | SPEC 1.5 "unbiased only if detector errors independent of theta" | formalized, not challenged | refuted, two counterexamples | SPEC-AMBIGUITY (SPEC is wrong) | **Astra right**, both counterexamples verified; SPEC sentence must change |
| D5 | collider vs reweighting in deletion | `D` is a collider between `A` and `F` | theta-side selection needs no collider | BOTH-VALID | different objects; both correct; presentation risk |
| D6 | homogenization condition | `kappa < 1 - rel_H` | `k < 1 - λ` | SPEC-AMBIGUITY | identical literal reading, both flagged it; needs a decree |
| D7 | four parameters or five | adds `kappa` (N3) | adds `k` | SPEC-AMBIGUITY | identical correction; SPEC 1.4 undercounts |
| D8 | SPEC 1.4 "c times the human covariance" | `g = c sqrt(kappa/rel_H)` (N1) | `γ = c sqrt(k/λ)` (14) | SPEC-AMBIGUITY | identical correction, *not* an Astra-only find |
| D9 | SPEC 1.4 "net direction depends on the mean gap" | Prop. 2 / Q1, Q2 | line 156 | SPEC-AMBIGUITY | identical correction; gap changes magnitude, not sign |
| D10 | sign-flip threshold under A1 | E18 | (26), (27) | CONVENTION-ONLY | same expression; verified identical |
| D11 | sign-flip boundary under non-ignorable authorship | E23 | (29) | CONVENTION-ONLY | same expression once `Δw = -b Δθ` is carried; verified |
| D12 | `Cov(Z_M, U_M)` | assumed zero (A2) | derived, bounded (12) | BOTH-VALID | Astra more explicit about what A2 buys; lane 3 should test it |
| D13 | ceiling on inflation | absent | `\|rho_obs\| <= \|ρ\|` (15) | BOTH-VALID | Astra-only, correct, lane 1 should adopt it |
| D14 | monotonicity regimes `c_1`, `c_2` | Prop. 4 | absent | BOTH-VALID | lane-1-only, verified by brute force |
| D15 | Gaussian-threshold deletion magnitudes | E32-E34 + table | absent | BOTH-VALID | lane-1-only, all three rows reproduce |
| D16 | Prop. 1 equality case `kappa = 0` | stated plainly | notes `c` undefined at `vM = 0` | CONVENTION-ONLY | limit only; footnote it |
| D17 | Prop. 11 strictness | "`q < 1` and `rel_H < 1`" | n/a | **LANE1-ERROR** (trivial) | correct condition is `q < 1` and (`rel_H < 1` **or** `rho_T^2 < 1`) |

Symbol collisions for the merged manuscript (CONVENTION-ONLY, but a live error source):
`g` is lane 1's slope and Astra's `Var(G)`; `k` is lane 1's item count and Astra's variance
ratio; `lambda` is lane 1's inverse Mills ratio *and* machine slope and Astra's reliability;
`kappa` is lane 1's variance ratio and Astra's residual covariance; `b` is lane 1's outcome
slope and Astra's item loading. Five collisions across two files.

---

## 3. The three items Astra's summary claims as corrections

The user flagged these for special attention. Two of the three are not lane-1 corrections.

**3.1 Covariance scaling under coupling (D8). Not an Astra-only correction.**
Astra's (14) gives `γ = c sqrt(k/λ)`, equal to `c` only when `vM = t`. Lane 1 line 50 and
notation decision N1 state `g = c sqrt(s2_M/s2_T) = c sqrt(kappa/rel_H)`, equal to `c` only
when `s2_M = s2_T`. These are the same expression, and both were reached before either saw
the other. Re-derived: `Cov(x,w|M) = Cov(c sqrt(vM/t)(theta-mu) + Z_M, nu + b(theta-mu) + U)
= c sqrt(vM/t) * b * t`, while `Cov(x,w|H) = b t`, so the ratio is `c sqrt(vM/t)`. Both
correct. This is a **SPEC 1.4 error that two independent derivations caught identically**,
which is the strongest possible signal that the SPEC sentence is wrong. It is not evidence
about lane 1.

**3.2 Sign-flip conditions (D10, D11). The formulas are identical, not different.**

    lane 1 (E18):   c_flip = -(1-pi)/pi * sqrt(rel_H/kappa)
    Astra   (26):   c_flip = -(1-π) sqrt(λ) / (π sqrt(k))

`sqrt(rel_H/kappa) = sqrt(λ)/sqrt(k)`. Same expression; CHECK passed. Astra's extra
threshold (27), "reversal reachable for some admissible `c < 0` iff `π > sqrt(λ)/(sqrt(λ)+
sqrt(k))`", is the same fact as lane 1's "impossible on the SPEC grid unless
`kappa/rel_H > 5.4`": at `pi = 0.30`, `(0.7/0.3)^2 = 5.444`. CHECK passed as an
if-and-only-if across a `pi` x `rel_H` x `kappa` grid.

The non-ignorable-authorship boundaries also coincide. Lane 1's E23 is
`c = (1-pi) sqrt(rel_H/kappa) [delta*d_theta/sqrt(rel_H) - 1/pi]`; Astra's (29) is
`c = -(1-π)(1+πB)/(πL)` with `B = ΔxΔw/h` and `L = m/h`. Substituting `Δw = -b Δθ` gives
`B = -delta*d_theta/sqrt(rel_H)` and `L = sqrt(kappa/rel_H)`, and the two collapse to the
same curve. CHECK passed over `pi` x `rel_H` x `kappa` x `delta` x `d_theta` including
negative `d_theta`. Astra's `c = 0` special case `B < -1/π` is lane 1's nonemptiness
condition `delta*d_theta > sqrt(rel_H)/pi` rearranged.

Astra does add one mechanism lane 1 does not have: reversal at `c > 0` through `L < 0`,
i.e. machine-class and human-class trait-outcome associations of opposite sign. That is
coverage, not correction. Lane 1 adds the SPEC-grid feasibility numbers Astra does not have.

**3.3 The deletion "only if" claim (D4). Real, and Astra is right.**
SPEC 1.5 asserts "deletion is unbiased only if detector errors are independent of theta".
Astra refutes it in both directions. I reproduced both counterexamples.

*Not necessary* (Astra 38): `theta = +1` w.p. 1/4, `-1` w.p. 3/4; pass w.p. 1 and 1/9.
Then `sp = 1/3` and the trait mean moves from `-0.500` to `+0.500`, yet `t_H = t_S = 0.7500`
exactly. Since the residual laws are untouched by a selection that depends only on theta and
independent detector noise, every correlation in the section-5.3 model is a function of the
trait variance alone, so both correlations are preserved despite strongly theta-dependent
detection. CHECK passed.

*Not sufficient* (Astra 39): `theta = ±1`, `U` uniform on `{-2,-1,1,2}`, `w = theta + U`,
pass iff `|U| = 1`, which is independent of theta. Simulated at n = 4e6:
`Cor(theta,w) = 0.5347` against the exact `sqrt(2/7) = 0.5345`, moving to `0.7068` among
passers against the exact `1/sqrt(2) = 0.7071`. CHECK passed.

Verdict. The SPEC sentence is false as a universal necessity claim. The correct statement is
Astra's: preserving the entire human joint law requires `S` independent of `(theta, w, x)`
given `H`; for a *particular* correlation, trait-independent detection is neither necessary
nor sufficient. Lane 1 did not commit this error, but also did not catch it.

This does **not** gut lane 1's Prop. 11, and the report should not be read that way.
Astra's counterexample (38) needs a two-point trait distribution whose variance happens to
survive selection. Under lane 1's stated model, bivariate normal `(theta, F)` with a
monotone pass function, `q = 1 - r_F^2 psi < 1` strictly and the attenuation is strict. I
re-derived E32-E34 in full and they are correct, including the ratio formula. What must
change is the paper's *headline*: state the parametric conditions, not the false universal.

---

## 4. The lane-1 error (D2), in full

Lane 1, line 62: "SPEC 1.2 calls this regime 'nearly harmless'. Props. 4 and 5 below show
that is true only when additionally `kappa = rel_H` (same scale as the human measurement)
and `delta = 0`."

Astra, line 229: "A machine that reports theta exactly has `c = 1`, `k = λ`, and `d = 0`;
it removes human measurement noise as π rises. Conversely, if `k = 1`, `d = 0`, and
`c = sqrt(λ)`, the observable correlation equals `rH` for every π."

Direct contradiction. Re-derived: `kappa = rel_H` means `s2_M = s2_T`, so at `c = 1` the
machine score is `mu_M + theta` exactly, with **no measurement error at all**, while the
human score is `theta + e`. The machine is then a strictly better measurement, so the
pooled correlation must rise above `rho_H`. Setting `k = λ`, `c = 1`, `d = 0`:

    N = (1-pi) sqrt(λ) + pi sqrt(λ) = sqrt(λ),   D = (1-pi) + pi λ
    Att = 1 / sqrt(1 - pi(1 - rel_H))  >  1  for every pi > 0 unless rel_H = 1

CHECK passed, closed form matching the general formula to 1e-12 at six
`(rel_H, pi)` points: at `rel_H = 0.7`, `Att = 1.015` at `pi = 0.1` and `1.048` at
`pi = 0.3`. That is inflation, not harmlessness.

Solving `Att(pi) = 1` for all `pi` gives the unique answer `kappa = 1`, `delta = 0`,
`c = sqrt(rel_H)` (the human-replica machine). CHECK passed, and a scan over
`kappa in [0.1, 3.0] x c in [0, 1]` at `rel_H = 0.7` found no other solution.

Source of the slip: lane 1 line 84 correctly verifies that the *covariance* ratio is 1 at
`c = 1`, `s2_M = s2_T`, then reads matched covariance as harmlessness. Matched covariance
with smaller variance is precisely what raises a correlation.

Two independent corroborations. Astra reached the correct condition blind. Lane 1 itself
reached it on day 2: open-questions Q3, day-2 revision, records "Exactly harmless is only
the human-replica machine (`kappa = 1`, `delta = 0`, `c = sqrt(rel_H)`; (E54))". Lane 1's
own Prop. 5 machinery is right; only the section-1 Remark is wrong. At `k = λ`, `d = 0`,
`rel_H = 0.7`, `pi = 0.1`, `c*(pi) = 0.849 < 1`, so `c = 1` sits above the inflation
boundary, contradicting line 62 from inside lane 1's own file.

**Action: edit `lane1-zero-coupling.md` line 62.** The day-1 file is what pass 2 and the
writeup read; the day-2 correction is in a different file and will not be seen.

D3 is the same slip's shadow. Line 169's "The homogenized amanuensis attenuates" is true on
the SPEC grid but not in general. At `c = 1`, `kappa = 0.2`, `rel_H = 0.7`, computed
`Att`: 0.994 at `pi = 0.1`, 0.987 at 0.3, 0.990 at 0.5, **1.016 at 0.7, 1.098 at 0.9**.
Lane 1's own Prop. 4 predicts exactly this (`g = 0.534` sits between `g_1 = 0.333` and
`g_2 = 0.600`, hence U-shaped), so the prose over-generalizes the proposition above it.
Add "on the SPEC grid".

---

## 5. Contamination check

Question: did Astra see lane 1's file, or a description of it? Conclusion: **no evidence of
contamination, and positive evidence of independence.**

Tells looked for and not found. Lane 1's idiosyncratic markers are `kappa` for the variance
ratio, `Den` for the denominator, the `g = c sqrt(kappa/rel_H)` slope form, the `c_1`/`c_2`
threshold pair, the `A1`/`A1'` assumption labels, and `rel_H`. None appears in Astra's file.
Astra writes `k`, `D`, `γ`, `c_H(π)`/`c_flip(π)`, "the principal model", and `λ`.

Stronger than absence: **five symbol collisions in the wrong direction.** Astra uses `g` for
`Var(G)`, the shared machine style factor, while lane 1 uses `g` for the slope. Astra uses
`κ_M` for a residual covariance, while lane 1 uses `kappa` for the variance ratio. Astra
uses `λ` for reliability, while lane 1 uses `lambda` for the inverse Mills ratio and
`lambda_M` for the machine slope. A contaminated derivation reuses the source's symbols for
the source's objects; it does not systematically reassign them to different objects.

Where the two do converge, convergence is forced. `N` and `Den`/`D` are the obvious names
for a numerator and a denominator, and their *definitions* differ (Astra's `N` absorbs
`sqrt(λ)`, lane 1's does not), so the shared letter is not a shared derivation. The one
genuinely striking convergence is that Astra's `c_H(π)` is algebraically identical to lane
1's `c*(π)`; but that curve is the unique solution of `Att = 1`, so any correct derivation
produces it. Equation numbering differs (`E1`-`E34` vs `01`-`39`), format differs (lane 1 is
deliberately ASCII, Astra is LaTeX plus Unicode), and Astra carries a 39-entry per-equation
self-check log with no lane-1 analogue.

Divergent coverage is itself evidence. Astra derives things lane 1 lacks (the `κ_M` bound,
the `D - N^2` decomposition, the unconditional latent target, the two deletion
counterexamples) and misses things lane 1 has (the `c_1`/`c_2` regime map, the Gaussian
threshold closed form, the Cronbach's alpha corollary, the rank-one authorship factor). A
contaminated re-derivation tracks its source's outline.

The shared corrections to the SPEC (D6, D7, D8, D9) are all forced by the SPEC's own text
and are the four most obvious things a careful reader hits in section 1.4. They are not
tells.

---

## 6. Both-wrong agreements, and joint gaps

Agreement is not proof, so these were hunted specifically. Three candidates; none is a
shared error, two are shared blind spots that will bite downstream.

**BW1 (cleared, but a pass-2 trap).** Both files compute population correlations, and both
flag it (lane 1 line 11, Astra line 3). Neither states the consequence for pass 2: the
sample Pearson correlation is biased for `rho`, so lane 4 must not check the closed forms by
averaging `r-hat` at moderate `n`. Compare against population moments, or use large `n`, or
average on the Fisher-z scale. **Flag for lane 4.**

**BW2 (cleared).** Both read `s2_M` as total machine variance and `s2_H` as human *error*
variance, making SPEC's "`s2_M < s2_H`" strictly stronger than "machine answers are less
dispersed than human answers". That is the literal reading of SPEC 1.2, both flagged it, and
both carried both conditions. Correct, not a shared error. It still needs a decree, since
`kappa < 1 - rel_H` is 0.3 at `rel_H = 0.7` while `kappa < 1` is the dispersion reading.
Lane 4's `kappa in {0.2, 0.5, 1.0}` straddles both, so no rework either way.

**BW3 (real shared limit, honestly declared by both).** Both take the machine residual as
independent of the outcome noise (lane 1's A2; Astra's `κ_M = 0` after deriving the general
form). Both therefore present the three-regime story as driven by `c` alone. Lane 1's day-2
(E60) shows a shared machine residual `rho_vw` inflates validity at `c = 0`, i.e. the
regime story is not exhaustive. Neither day-1 document says so. **Flag for the writeup;
lane 3 should measure it** on same-session machine text.

Nothing else in the overlap survived as a candidate. The core mixture moments, `Den`, the
`c = 0` attenuation bound, the inflation boundary, both sign-flip boundaries, and the
between-item structure were each re-derived independently here and are correct in both files.

---

## 7. Coverage asymmetry (not discrepancies)

Lane 1 only: the `c_1`/`c_2` monotonicity regime map (Prop. 4, verified against brute-force
scans over `rel_H` x `kappa` x `c`); the Gaussian threshold deletion closed form E32-E34 and
its numeric table (all three rows reproduce: `q = 0.968/0.910/0.984`, ratios
`0.983/0.951/0.992`); the Cronbach's alpha reliability paradox; the rank-one authorship
factor; the `pi'` post-deletion contamination fraction with the SPEC operating point
(`pi' = 0.0192`, reproduced); the E28a between-item crossover
(`delta > 1.610 sqrt(kappa) = 0.720` at `kappa = 0.2`, reproduced and bracketed numerically).

Astra only: the `D - N^2` decomposition (15) and the resulting ceiling `|rho_obs| <= |ρ|`
across the full `c in [-1,1]` grid (identity verified exact to 1e-12, ceiling verified on
324 points); the `κ_M` Cauchy-Schwarz bound; general authorship selection (17)-(18) with
class-specific `rho_M`, `t_M`; the `L < 0` sign-reversal mechanism at `c > 0`; the exact
numeric between-item existence example (24), which reproduces; the deletion counterexamples.

D13 deserves promotion, not just recording. Astra's ceiling bounds the amanuensis regime
from above: contamination can beat the *observed* human validity `rho_H` but can never beat
the *latent* validity `rho_T`. That is the sentence that makes lane 1's inflation region
publishable rather than alarming, and it also makes D1 concrete, because the two estimands
sit on opposite sides of it.

---

## 8. Verdict

**CLEAN, conditional on three edits and one decision.** No unresolved substantive
discrepancy remains: every disagreement between the two documents was re-derived here and
adjudicated, and one side is right in each case. Per SPEC 7 nothing blocks the preprint on
grounds of a standing lane-1/Astra conflict.

The conditions are not open discrepancies; they are known fixes that must land.

1. **Edit `lane1-zero-coupling.md` line 62** (D2). The `c = 1` harmlessness condition is
   wrong; the correct one is `kappa = 1`, `delta = 0`, `c = sqrt(rel_H)`. Lane 1's day-2
   file already has this as E54, but pass 2 and the writeup read the day-1 file.
2. **Edit line 169** (D3): qualify "the homogenized amanuensis attenuates" to the SPEC grid.
   Also fix Prop. 11's strictness condition (D17) to `q < 1` and (`rel_H < 1` or
   `rho_T^2 < 1`).
3. **Edit SPEC 1.5** (D4). "Unbiased only if detector errors are independent of theta" is
   false in both directions. Replace with the exact condition (independence of `S` from
   `(theta, w, x)` given `H` for the whole law) and state lane 1's Prop. 11 under its
   parametric assumptions.
4. **Abhay's N2 decision** (D1): is the headline estimand `Cor(x, w | H)` or
   `Cor(theta, w)`? This is a decree, not a derivation question, and it costs no rework:
   the crosswalk is exact, and `lane4-simulation/CONVENTIONS.md` already computes both
   (`rho_H = sqrt(rel_H) * rho_T` as primary, `rho_T` as secondary, with every estimator
   returning both). It does flip the sign of a headline sentence, since the same cell
   inflates against `rho_H` and partially disattenuates against `rho_T`.

Pass 2 (lane 4 numerical) is cleared to proceed, with two carried flags: use population
moments rather than averaged sample correlations when checking the closed forms (BW1), and
note that the regime story assumes `rho_vw = 0` (BW3). Lane 4's DGP already implements N1
correctly (`lam_M = c * sqrt(s2_M / s2_T)`), which was the single highest-risk convention.

DONE-PASS1-DIFF

---

Summary. The two derivations agree on every core result once the symbol crosswalk is
applied, and the agreement is convergent rather than correlated: Astra reassigns five of
lane 1's symbols to different objects, numbers equations differently, and covers a
substantially different set of results, so there is no evidence it saw lane 1's work. Of the
three points Astra's summary claims as corrections, two (covariance scaling under coupling,
the sign-flip conditions) turn out to be things lane 1 already had, identically, and are
better described as two independent derivations catching the same two SPEC 1.4 errors; the
third, the deletion "only if" claim, is a genuine and correct refutation of SPEC 1.5 that
lane 1 missed, though it constrains the paper's wording rather than lane 1's Prop. 11. The
one substantive lane-1 error the diff surfaced is in neither of those places: lane 1's day-1
Remark on `c = 1` calls the perfect same-scale amanuensis harmless when it in fact inflates
the pooled correlation by `1/sqrt(1 - pi(1 - rel_H))`, a slip lane 1 caught itself on day 2
and Astra caught blind. Pass 1 is clean; the preprint gate is three edits and Abhay's
pending estimand call.
