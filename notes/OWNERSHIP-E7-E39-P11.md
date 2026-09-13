# Owning (E7), (E39), and Prop. 11

A walkthrough of the three results you will be asked about first. Read time about 20 minutes.
Every equation below is copied from the derivation files, not restated from a summary. Sources:

- (E7), (E30) to (E34), Prop. 11: `derivations/lane1-zero-coupling.md` sections 3.1 and 6
- (E36) to (E39), Prop. 12: `derivations/lane1-partial-coupling.md` section 1
- Paper statements: `paper/GHOST-RESPONDENTS-DRAFT.md` sections 2.1 to 2.3

Six places where the paper's prose runs ahead of the derivation, or where an assumption is
doing work nobody has written down, are marked **FLAG n** at the point they bite and
collected in section 7. Equation-by-equation pointers and the verification receipts are in
`notes/OWNERSHIP-CHECK.md`.

---

## 0. The shared setup, once

All three results live in the same model, so learn the symbols once.

| Symbol | Is | Defined at |
| --- | --- | --- |
| `theta` | latent trait, mean 0, variance `s2_T` | zero-coupling s0 |
| `w = b theta + u` | the outcome you validate against, `u` independent of everything | zero-coupling s0 |
| `x` | the scored open-ended response | (E1) |
| `A in {H, M}` | authorship, unobserved | zero-coupling s0 |
| `pi = P(A = M)` | contamination fraction | zero-coupling s0 |
| `rho_T = Cor(theta, w)` | trait-level validity | zero-coupling s0 |
| `rel_H = s2_T / V_H` | human single-indicator reliability, `V_H = Var(x given H)` | zero-coupling s0 |
| `rho_H = Cor(x, w given H) = sqrt(rel_H) rho_T` | clean-sample observed validity. **This is the estimand.** | zero-coupling s0, N2 |
| `c = Cor(x, theta given M)` | coupling: how much trait signal the machine text carries | zero-coupling s0 |
| `kappa = s2_M / V_H` | machine-to-human observed variance ratio. `kappa < 1` is homogenization | zero-coupling s0 |
| `delta = (mu_H - mu_M) / sqrt(V_H)` | authorship mean gap in human-SD units | zero-coupling s0 |
| `g = c sqrt(kappa / rel_H)` | the machine slope on theta. `g = lambda_M`, same number | zero-coupling s0 |

Two shorthand polynomials that recur everywhere:

    N(pi, c) := (1 - pi) + pi * g                                   (E0a)
    Den(pi)  := (1 - pi) + pi * kappa + pi (1 - pi) delta^2         (E0b)

`N` is the covariance multiplier, `Den` the variance multiplier. `Den` does not depend on `c`.

Two assumptions carried throughout:

- **A1 (ignorable authorship).** `A` is independent of `(theta, u, e, v)`. Who gets ghosted
  does not depend on their trait.
- **A2.** The machine residual `v` is independent of the outcome noise `u`. The LLM does not
  see the outcome.

One notation decision you should be able to state on demand (N1): SPEC's prose says the
machine covariance is "c times the human-scale covariance". It is not. The exact factor is
`g = c sqrt(kappa / rel_H)`. They coincide only at `kappa = rel_H`. The files keep `c` as the
correlation and carry the scale factor explicitly in `g`.

---

## 1. (E7): the attenuation factor

### 1.1 The claim in one sentence

Contaminating a sample with machine-written responses multiplies the validity coefficient you
compute by a known factor `Att(pi, c)` that depends on only five numbers, and that factor can
sit below or above 1.

### 1.2 Notation decoder for this result

You need `pi, c, rel_H, kappa, delta` and the two polynomials `N` and `Den`. Nothing else.

### 1.3 The derivation, every move

Start from the mixture. The observed score is one of two processes depending on the unobserved
`A`:

    x = (1 - 1{A = M}) (mu_H + theta + e) + 1{A = M} (mu_M + lambda_M theta + v)      (E1)

with `theta, e, v, u` mutually independent and independent of `A` under A1 and A2.

*Intuition.* Nothing clever yet. This is just "some respondents wrote it, some had an LLM write
it", with the machine side written in a second-moment representation
`m = lambda_M theta + v` so that `Cor(x, theta given M) = c` and `Var(x given M) = s2_M` both
hold by construction. That representation is exact for correlations and needs no distributional
assumption.

**Step 1: the pooled variance.** Law of total variance over `A ~ Bernoulli(pi)`:

    E[Var(x | A)] = (1 - pi) V_H + pi s2_M

`Var(E[x | A])` is the variance of a two-point variable taking `mu_H` with probability `1 - pi`
and `mu_M` with probability `pi`, which is `pi (1 - pi) Delta^2` with `Delta = mu_H - mu_M`. So

    Var(x) = (1 - pi) V_H + pi s2_M + pi (1 - pi) Delta^2 = V_H * Den(pi)             (E3)

*Intuition.* Three sources of spread: within-human, within-machine, and the gap between the two
group means. The third is the one people forget. Two tight clusters with different centers look
like one wide distribution. Dividing through by `V_H` turns `s2_M` into `kappa` and `Delta^2`
into `delta^2`, which is where `Den` comes from.

**Step 2: the pooled covariance with the outcome.** Within-class first:

    Cov(x, w | H) = Cov(theta + e, b theta + u) = b s2_T
    Cov(x, w | M) = Cov(lambda_M theta + v, b theta + u) = lambda_M b s2_T

The second line uses A2 to kill `Cov(v, u)`. Between-class:
`Cov(E[x | A], E[w | A]) = 0`, because `E[w | A] = b E[theta | A] = 0` under A1. Adding the two
contributions with weights `1 - pi` and `pi`:

    Cov(x, w) = b s2_T [ (1 - pi) + pi g ] = b s2_T * N(pi, c)                        (E4)

*Intuition.* Each machine response replaces a unit of signal covariance with `g` units. If the
machine text carries no trait (`c = 0`, so `g = 0`), that respondent contributes nothing to the
covariance and `N` falls to `1 - pi`. The between-class term is zero precisely because A1 says
the two authorship groups have the same average trait, so their average outcomes match too.

**Step 3: the outcome variance is untouched.** `Var(w) = V_w`. Contamination is on the `x` side
only. (If the outcome is also machine-written, that is Q4 and Prop. 15, not this result.)

**Step 4: assemble the correlation.**

    rho_obs := Cor(x, w) = b s2_T N / sqrt(V_H Den V_w) = rho_H * N(pi, c) / sqrt(Den(pi))   (E5)

The middle expression is just `Cov / sqrt(Var Var)` with (E3) and (E4) substituted in. The right
expression uses `rho_H = b s2_T / sqrt(V_H V_w)` from the notation table, so the `b s2_T` and
the `sqrt(V_H V_w)` cancel out of the ratio and leave `rho_H` times a pure function of the
standardized parameters. Define

    Att(pi, c) := rho_obs / rho_H = N / sqrt(Den)

and write it out in the five parameters:

    Att(pi, c) = [ (1 - pi) + pi c sqrt(kappa / rel_H) ]
                 / sqrt[ (1 - pi) + pi kappa + pi (1 - pi) delta^2 ]                  (E7)

*Intuition.* The whole result is a race between a numerator that falls (each machine response
donates `g < 1` units of covariance instead of 1) and a denominator that can fall faster
(homogenized machine text shrinks the pooled variance) or rise (a mean gap inflates it). The
correlation is the ratio, so whichever term moves more decides the sign of the bias. That is why
contamination is not automatically attenuation.

### 1.4 Boundary checks you should be able to run live

- `pi = 0` gives `Att = 1`. No contamination, no bias.
- `pi = 1` gives `Att = g / sqrt(kappa) = c / sqrt(rel_H)`. Check it against the direct
  computation: an all-machine sample has `Cor(x, w) = c rho_T = (c / sqrt(rel_H)) rho_H`. Match.
- `kappa = 1, delta = 0, c = 0` gives `Att = 1 - pi`. Pure dilution: machine noise at exactly
  human variance, carrying no signal.
- Against `rho_T` instead of `rho_H`: `rho_obs / rho_T = sqrt(rel_H) Att`. Classical attenuation
  and contamination multiply and are separable.

> **FLAG 1 (small).** Paper section 2.2 says "At `c = 0`, `Att_0 = (1 - pi) / sqrt(Den)` is
> strictly between 0 and `sqrt(1 - pi)`". The derivation writes (E10) as
> `0 < Att_0(pi) <= sqrt(1 - pi) < 1` and then names the attainment condition outright on the
> next line: "with equality ... iff `kappa = 0` and `delta = 0`". At that corner `Den = 1 - pi`
> and `Att_0 = sqrt(1 - pi)` exactly. The corner is degenerate (a machine that returns the same
> score every time) but admissible: Prop. 3 is stated "for every `kappa >= 0`". "Strictly
> between" overstates by one endpoint, against the paper's own source. Say `at most`
> `sqrt(1 - pi)`.

### 1.5 Assumptions doing real work, and what breaks

| Assumption | What it buys | What breaks without it |
| --- | --- | --- |
| **A1**, `A` independent of `theta` | The between-class covariance term in step 2 is exactly zero | You get (E19) to (E21) instead: `Att'` picks up `- pi (1 - pi) delta d_theta / sqrt(rel_H)` in the numerator and `Var(w)` gains `pi (1 - pi) b^2 Delta_theta^2`. The sign can now flip (Prop. 7). This is not hypothetical: the survivor sample after deletion is exactly this case. |
| **A2**, `v` independent of `u` | `Cov(x, w given M) = lambda_M b s2_T`, no extra term | `Cov(x, w)` gains `pi Cov(v, u)`. The machine can manufacture validity from nothing. Defensible here because the generator is conditioned on the prompt, not on the outcome, but it is an assumption about the data-generating pipeline, not about statistics. |
| Outcome not machine-written | `Var(w) = V_w` in step 3 | `Var(y) = V_w Den_w(pi)` and you need Prop. 15 (both endpoints). |
| One machine process, constant `(c, kappa, delta)` | `g` is a single number | A mixture of generators makes `g` a distribution; only its mean enters `N`, but `Den` picks up the between-generator variance. |
| Second moments only | No normality needed for (E7) | Nothing. This is the result's strongest point: (E7) is a second-moment identity, so the committee cannot attack it with a distributional objection. Say that out loud. |

### 1.6 A tiny numeric example

Take `pi = 1/2`, `c = 0` (machine text carries no trait), `delta = 0` (no mean gap). Then
`N = 1/2` and `Den = 1/2 + kappa/2`.

- `kappa = 1` (machine scores as dispersed as human scores): `Den = 1`, so `Att = 0.5`.
  Pure dilution, exactly `1 - pi`.
- `kappa = 0` (machine returns the same score every time): `Den = 1/2`, so
  `Att = 0.5 / sqrt(0.5) = 1/sqrt(2) = 0.707`.

Same amount of contamination, same zero signal, and the bias is 30 points different. The only
thing that changed is how much variance the machine responses add back. That is `Den` earning
its keep, and it is the fastest way to show a committee that `1 - pi` is the wrong default.

### 1.7 Three committee questions

**Q. "Isn't this just classical attenuation? Why not `1 - pi`?"**
`1 - pi` is one corner of (E7): `c = 0`, `kappa = 1`, `delta = 0`. Move off that corner in any
direction and the answer changes, because contamination perturbs the variance of `x` as well as
its covariance with `w`. Prop. 2 gives the exact crossover: `Att_0(pi) > 1 - pi` if and only if
`kappa + (1 - pi) delta^2 < 1`. Homogenization makes contamination less harmful than pure
dilution, a mean gap makes it more harmful, and the line between them is that inequality.

**Q. "`Att > 1` looks like an error. Correlations should attenuate."**
They should not, and the boundary check proves it. At `pi = 1` the formula returns
`c / sqrt(rel_H)`, which exceeds 1 whenever `c > sqrt(rel_H)`: a machine that copies the trait
more faithfully than your noisy human measurement does is a *better* indicator of `theta`, so
pooling it in raises the observed correlation. The exact boundary where `Att = 1` is
`c*(pi) = sqrt(rel_H / kappa) [ sqrt(Den(pi)) - (1 - pi) ] / pi` (E17). Below it contamination
hides validity, above it contamination manufactures validity, and the second is the more
dangerous failure because the naive researcher sees a stronger result.

**Q. "A2 says the LLM does not see the outcome. What if it does?"**
Then `Cov(x, w)` gains `pi Cov(v, u)` and every regime statement below is void. In this design
the outcome is a separate administered measure and the generator is prompted from the item text
alone, so A2 holds by construction of the pipeline. In a field application where the same LLM
drafts both the open-ended response and something correlated with the outcome, it does not, and
that is a design warning worth giving, not a limitation of the algebra.

### 1.8 Thirty seconds, out loud

"Take a survey where some share of the open-ended answers were written by an LLM. You correlate
the scored answer with an outcome. What you get is the clean correlation times one factor. The
numerator of that factor is how much trait covariance survives, which falls as contamination
rises. The denominator is how much the pooled variance moved, which can go either way: machine
text is usually less dispersed, which shrinks the denominator, but if the machine scores sit at
a different average than the human ones, that gap inflates it. So the correlation is a race
between those two. Most people assume you just lose a fraction `1 - pi` of your signal. That is
one corner of the formula, and off that corner you can get less bias than that, or you can get
bias in the other direction."

---

## 2. (E39): the first-order bias

### 2.1 The claim in one sentence

For small contamination, the bias in the naive validity coefficient is linear in `pi` with a
sign given by `c - c_2(delta)`, so one threshold on the coupling tells you whether contamination
hides your effect or manufactures it.

### 2.2 Notation decoder for this result

Everything from (E7), plus:

    S := 1 + kappa + delta^2
    g_2(delta) := S / 2                           the slope threshold
    c_2(delta) := S sqrt(rel_H) / (2 sqrt(kappa)) the same threshold in c units

`c_2` is `g_2` converted with `c = g sqrt(rel_H / kappa)`. There is a companion threshold
`c_1(delta) = 2 sqrt(kappa rel_H) / S`, and `c_1 <= c_2` always, by AM-GM
(`S^2 >= (1 + kappa)^2 >= 4 kappa`). The pair define the three regimes of Prop. 12: `Att`
decreases in `pi` below `c_1`, increases above `c_2`, and is U-shaped between.

### 2.3 The derivation, every move

**Step 1: expand the numerator.** `N(pi, c) = (1 - pi) + pi g = 1 + pi (g - 1)`. Exact, not an
approximation. `N` is affine in `pi` to begin with.

**Step 2: expand the denominator.** Write `Den` out and collect powers of `pi`:

    Den(pi) = (1 - pi) + pi kappa + pi (1 - pi) delta^2
            = 1 + pi (kappa - 1 + delta^2) - pi^2 delta^2

Take the square root with `sqrt(1 + z) = 1 + z/2 + O(z^2)`. Here `z = pi (kappa - 1 + delta^2) -
pi^2 delta^2`, which is `O(pi)`, so `z^2 = O(pi^2)` and the `pi^2 delta^2` term is `O(pi^2)`
too. Both go into the remainder:

    sqrt(Den(pi)) = 1 + (pi / 2)(kappa - 1 + delta^2) + O(pi^2)

*Intuition.* Near `pi = 0` the pooled variance moves linearly, and a square root halves a small
relative change. The `pi (1 - pi) delta^2` term contributes `pi delta^2` at first order because
`(1 - pi) -> 1`; the mean gap's second-order correction is not visible yet.

**Step 3: divide.** `1 / (1 + a pi + O(pi^2)) = 1 - a pi + O(pi^2)`, so

    Att(pi, c) = [1 + pi (g - 1)] [1 - (pi / 2)(kappa - 1 + delta^2)] + O(pi^2)
               = 1 + pi [ (g - 1) - (kappa - 1 + delta^2) / 2 ] + O(pi^2)

**Step 4: collect the bracket.** This is the only step where anything cancels, so do it slowly:

    (g - 1) - (kappa - 1 + delta^2) / 2
      = g - 1 - kappa/2 + 1/2 - delta^2/2
      = g - 1/2 - kappa/2 - delta^2/2
      = g - (1 + kappa + delta^2) / 2
      = g - S / 2
      = g - g_2(delta)

Hence

    Att(pi, c) = 1 + pi [ g - g_2(delta) ] + O(pi^2),
    bias(rho_obs) = pi rho_H sqrt(kappa / rel_H) [ c - c_2(delta) ] + O(pi^2)          (E39)

The second form follows from the first by `bias = rho_H (Att - 1)` and substituting
`g = c sqrt(kappa / rel_H)`, then factoring `sqrt(kappa / rel_H)` out of the bracket:

    g - S/2 = c sqrt(kappa/rel_H) - S/2
            = sqrt(kappa/rel_H) [ c - (S/2) sqrt(rel_H/kappa) ]
            = sqrt(kappa/rel_H) [ c - c_2(delta) ]

*Intuition.* One sentence covers the whole `(pi, c)` map: the naive validity moves in the
direction of `c - c_2(delta)`, at a rate `pi sqrt(kappa / rel_H)`. Everything the map does
qualitatively is in the sign of one subtraction.

> **FLAG 2 (real, and the most likely place a committee catches you).** The paper's section 2.2
> says, after printing the bias half of (E39): "so the sign of the contamination bias is the
> sign of `c - c_2`." That sentence is true to first order only, and the prose drops the hedge
> the display carries. Globally the zero of the bias is `c*(pi)` from (E17), and
> `c*(0+) = c_2(delta)` is a limit, not an identity. On the derivation's own numbers
> (`kappa = 0.2, rel_H = 0.7, delta = 0`, so `c_2 = 1.122`): at `c = 1 < c_2`, `Att` is
> 0.994 at `pi = 0.1` and 0.987 at `pi = 0.3`, as the sign rule predicts, but 1.016 at
> `pi = 0.7` and 1.098 at `pi = 0.9`. The bias changed sign while `c - c_2` did not. The
> crossing is at `c*(0.6) = 1.0012`, just past `pi = 0.60`, which is what
> `lane1-zero-coupling.md` Prop. 4 already states. Nothing in the result is wrong; the
> paper sentence is. If asked, say: the sign rule is the `pi -> 0` statement, the global
> boundary is (E17), and the grid tops out at `pi = 0.30` where they agree. Do not defend the
> sentence as written.

> **FLAG 3 (small, worth knowing before someone else finds it).** (E39) in `c` units divides by
> `sqrt(kappa)`, so `c_2(delta) -> infinity` as `kappa -> 0` and the product
> `sqrt(kappa/rel_H) [c - c_2]` is a `0 * infinity` form. The `g` form
> `Att = 1 + pi [g - g_2(delta)]` has no such problem: at `kappa = 0`, `g = 0` and the slope is
> just `-S/2`. Use the `g` form if anyone pushes on the constant-machine corner.

> **FLAG 4 (bookkeeping).** The derivation's own check sentence in section 1.5 reads "at
> `pi = 0.10` the exact table value below is 1.020 because `Den = 1` makes (E36) exactly linear
> there." (E36) is the statement that `Att` is affine in `c`. What `Den = 1` delivers is exact
> linearity in `pi`. Wrong pointer, right arithmetic. Do not repeat the citation.

### 2.4 Assumptions doing real work, and what breaks

| Assumption | What it buys | What breaks without it |
| --- | --- | --- |
| Everything (E7) needs | The object being expanded | See 1.5 |
| `pi` small | The `O(pi^2)` remainder is negligible | The linear rule stops predicting the sign, as FLAG 2 shows. Measured error on the derivation's own table: at `pi = 0.10, kappa = 0.5, c = 0.9` the exact `Att` is 1.0014 against a linear 1.0011 (gap 0.0004); at `pi = 0.30` the same cell is 1.0068 against 1.0032 (gap 0.0036); at `pi = 0.9, kappa = 0.2, c = 1` it is 1.0981 against 0.9411 (gap 0.157). The grid's ceiling is `pi = 0.30`, so the expansion is safe where the paper uses it, and only there. |
| `kappa > 0` | `c_2` is finite | See FLAG 3. Use the `g` form. |
| A1 | `delta` enters only through `delta^2` in `S` | Under A1' the mean gap gets a first-order sign effect through `delta d_theta` in the numerator of (E21). Under A1 the gap is pure variance inflation and cannot change the direction of the covariance. |

### 2.5 A tiny numeric example

The cleanest cell is `c = 1`, `kappa = 1`, `delta = 0`, `rel_H = 0.7` (a faithful amanuensis at
human scale).

    g = 1 * sqrt(1 / 0.7) = 1 / 0.8367 = 1.195
    g_2 = S / 2 = (1 + 1 + 0) / 2 = 1
    slope = g - g_2 = 0.195

So `Att ~ 1 + 0.195 pi`. At `pi = 0.10` that is 1.0195. The exact table value in
`lane1-partial-coupling.md` section 1.6 is 1.020, and here the expansion is not an
approximation at all: `kappa = 1` and `delta = 0` make `Den = 1` exactly, so `Att = N` is
exactly linear in `pi`.

The reading to carry: a machine that reproduces the trait perfectly, at human scale, with no
mean gap, still biases the coefficient, and biases it *upward* by about two percent at ten
percent contamination. That is (E76) in the paper, `Att = 1 + pi (1 / sqrt(rel_H) - 1) > 1`, and
it is the fastest counterexample to "a good ghostwriter is harmless".

### 2.6 Three committee questions

**Q. "First order in `pi`. Over what range is that any good?"**
Over the grid, which tops out at `pi = 0.30`. The measured gaps are in the table in 2.4: four
ten-thousandths at `pi = 0.10`, four thousandths at `pi = 0.30`, and it falls apart by
`pi = 0.9`. (E39) is the sentence-length summary of the map; the exact statements are (E7) for
values, Prop. 12 for shape, and (E17) for the sign boundary. Never quote (E39) as the exact
result.

**Q. "Why is the sign threshold `c_2` and not `c_1`? You defined both."**
They answer different questions. `c_1` and `c_2` bracket the regimes of *monotonicity in `pi`*,
that is, the sign of `dAtt/dpi`: decreasing below `c_1`, increasing above `c_2`, U-shaped
between (Prop. 12). `c_2` shows up again in (E39) because it is also the `pi -> 0` limit of the
*level* boundary `c*(pi)` where `Att = 1` (Prop. 5). Two different derivatives, one coincident
boundary at the origin. `c_1` has no role in the sign of the bias.

**Q. "The mean gap enters only as `delta^2`. So the direction of the gap does not matter?"**
Correct, under A1, and that is a substantive claim rather than an algebraic accident. Under A1
the mean gap touches `Var(x)` only, through `pi (1 - pi) Delta^2` in (E3), and `Var` cannot see
a sign. It never reaches `Cov(x, w)`, because `E[w | A] = 0` for both classes when authorship is
ignorable. The gap's direction becomes visible only once authorship is non-ignorable, where
`delta d_theta` appears in the numerator of (E21) and can flip the sign of the whole
coefficient. That is the bridge to Prop. 11: the detector manufactures exactly that
non-ignorability.

### 2.7 Thirty seconds, out loud

"If contamination is light, you can skip the whole map. The bias is linear in the contamination
rate, and its direction is one comparison: the coupling `c` against a threshold `c_2` built from
the variance ratio, the mean gap and the reliability. Below the threshold, contamination hides
your effect. Above it, contamination manufactures one. The rate is set by how much variance the
machine adds. The one thing I will not let that sentence do is run to high contamination, since
it is a small-`pi` expansion and the exact sign boundary moves with `pi`."

---

## 3. Prop. 11: the deletion-selection bias

### 3.1 The claim in one sentence

Running a clean human sample through an AI-text detector and deleting the flagged cases lowers
the validity coefficient among the survivors, even with zero machine responses in the data and
even with a perfect-sensitivity detector, because the detector throws away trait variance along
with the fluency it was actually measuring.

### 3.2 Notation decoder for this result

| Symbol | Is |
| --- | --- |
| `se = P(flag given M)` | sensitivity |
| `sp_bar = P(pass given H)` | marginal specificity. The paper writes this as `sp` |
| `pi'` | residual contamination after deletion, (E30) |
| `F` | the fluency score (or whatever text feature) the detector thresholds on |
| `r_F = Cor(theta, F)` | the fluency-trait correlation. The whole result scales with `r_F^2` |
| `tau = Phi^{-1}(1 - sp_bar)` | the pass threshold on standardized `F` |
| `lambda = phi(tau) / sp_bar` | truncated-normal mean, the inverse Mills ratio at `tau` |
| `psi = lambda (lambda - tau)` | the fraction of `F`'s variance that truncation removes, in `(0, 1)` |
| `q = 1 - r_F^2 psi` | the survivors' trait-variance retention factor, (E33) |
| `rho_H,pass` | `Cor(x, w given H, pass)` |

### 3.3 The derivation, every move

**Step 0: why residual contamination is not the story.** By Bayes,

    pi' := P(M | pass) = (1 - se) pi / [ (1 - se) pi + sp (1 - pi) ]                  (E30)

At `se = sp = 0.85` and `pi = 0.10`: `pi' = 0.015 / (0.015 + 0.765) = 0.019`. That looks small,
and if residual contamination were the only channel, deletion would work. The rest of the
section is the argument that it is not the only channel.

**Step 1: name the collider.** The detector's human error rate depends on `F`, which correlates
with `theta`. The graph is

    theta -> F -> D <- A,      theta -> x,   theta -> w

`D` is a collider between `A` and `F`. Under A1, `A` and `theta` are independent. Conditioning
on `D = pass` opens the path `A - D - F - theta`, so among survivors `A` and `theta` are
dependent. The survivor population satisfies A1', not A1.

*Intuition.* You did not select on the trait, and you did not select on authorship. You selected
on something downstream of both. That is enough. This is the formal content of "deletion selects
on theta", and it is the reason the result survives at `pi = 0`.

**Step 2: the mean shift, distribution-free.** Let `s(theta) := P(pass | H, theta) =
E[sp(F) | theta, H]` and `sp_bar := E[sp(F) | H]`.

    E[theta | H, pass] - E[theta | H] = Cov(theta, sp(F) | H) / sp_bar                (E31)

*Proof, each equality:* `E[theta | H, pass] = E[theta 1{pass} | H] / P(pass | H)` is the
definition of conditional expectation. The numerator is `E[theta s(theta) | H]` by the tower
property over `theta`. Write that as `E[theta | H] sp_bar + Cov(theta, s(theta) | H)`, which is
just the definition of covariance rearranged. Divide by `sp_bar`. Finally
`Cov(theta, s(theta)) = Cov(theta, E[sp(F) | theta]) = Cov(theta, sp(F))`, again by the tower
property.

For `(theta, F)` bivariate normal with correlation `r_F`, and `sp` nondecreasing and
nonconstant, `Cov(theta, sp(F)) = r_F sqrt(s2_T) Cov(F, sp(F))` and `Cov(F, sp(F)) > 0` by
Chebyshev's association inequality. So the shift has the sign of `r_F` and vanishes only when
fluency carries no trait information. (E31) is Lemma 1 and is worth knowing separately: it needs
no normality and no threshold rule.

**Step 3: the variance shrink, under a Gaussian threshold detector.** Model

    F = r_F theta / sqrt(s2_T) + sqrt(1 - r_F^2) eta,    eta ~ N(0, 1) independent,
    pass iff F > tau,     sp_bar = 1 - Phi(tau)

Standard truncated-normal facts with `lambda := phi(tau) / (1 - Phi(tau)) = phi(tau) / sp_bar`:

    E[F | F > tau] = lambda,    Var(F | F > tau) = 1 - psi,    psi := lambda (lambda - tau)

Now decompose `theta` on `F`. Because `(theta, F)` is bivariate normal and `F` is standardized,
`theta = r_F sqrt(s2_T) F + sqrt(s2_T (1 - r_F^2)) eta'` with `eta'` independent of `F`.
Selection touches `F` and nothing else, so take the variance of that decomposition conditionally
on `F > tau`:

    Var(theta | H, pass) = r_F^2 s2_T Var(F | F > tau) + s2_T (1 - r_F^2)
                         = r_F^2 s2_T (1 - psi) + s2_T (1 - r_F^2)
                         = s2_T [ r_F^2 - r_F^2 psi + 1 - r_F^2 ]
                         = s2_T [ 1 - r_F^2 psi ] = s2_T q                            (E33)

and likewise `E[theta | H, pass] = r_F sqrt(s2_T) lambda` (E32), which is Lemma 1 specialized.

*Intuition.* Only the part of `theta` that runs through `F` is exposed to the truncation. That
part is `r_F^2` of the variance, and truncation removes the fraction `psi` of it. So you lose
`r_F^2 psi` of the trait variance and keep `q`. Everything downstream is `O(r_F^2)`, and that is
the single most important fact about this result.

**Step 4: what selection does *not* touch.** The measurement error `e` and the outcome noise `u`
are independent of `(theta, F)`, so truncating on `F` leaves their variances alone:

    Cov(x, w | H, pass) = b s2_T q,
    Var(x | H, pass)    = s2_T q + s2_H,
    Var(w | H, pass)    = b^2 s2_T q + s2_u

*Intuition.* This asymmetry is the entire result. The numerator of the correlation is all true
score, so it loses the full factor `q`. Each denominator is part true score and part noise, so
it loses only the true-score share. A ratio whose top shrinks more than its bottom falls.

**Step 5: divide by the unrestricted quantities.**

    Var(x | H, pass) / V_H = (s2_T q + s2_H) / V_H = q rel_H + (1 - rel_H) = 1 - rel_H (1 - q)
    Var(w | H, pass) / V_w = (b^2 s2_T q + s2_u) / V_w = 1 - rho_T^2 (1 - q)

using `rel_H = s2_T / V_H` and `rho_T^2 = b^2 s2_T / V_w`. So

    rho_H,pass := Cor(x, w | H, pass)
                = rho_H * q / sqrt[ (1 - rel_H (1 - q)) (1 - rho_T^2 (1 - q)) ]        (E34)

**Step 6: Prop. 11, the sign.**

> **Prop. 11 (deletion bias at `pi' = 0`).** `rho_H,pass < rho_H` whenever `r_F != 0`,
> `sp_bar < 1`, and (`rel_H < 1` or `rho_T^2 < 1`).

*Proof, every move.* Each denominator factor is a convex combination of `q` and 1:

    1 - rel_H (1 - q) = rel_H * q + (1 - rel_H) * 1

Since `q <= 1` and `0 <= rel_H <= 1`, that combination is `>= q`, with equality exactly when
`rel_H = 1` or `q = 1`. The same argument applies verbatim to `1 - rho_T^2 (1 - q)`. So the
product of the two factors is `>= q^2` and its square root is `>= q`, which makes the whole
ratio `q / sqrt(...) <= 1`. It is strict as soon as `q < 1` and at least one of the two factors
is strictly above `q`, which is one of `rel_H < 1` or `rho_T^2 < 1`. Finally,
`q < 1` needs `r_F != 0` and `psi > 0`; and `psi = lambda (lambda - tau) > 0` for every finite
`tau`, because `lambda > max(tau, 0)`, and `tau` is finite exactly when `sp_bar < 1`. QED.

*Intuition for the degenerate case.* If `rel_H = 1` and `rho_T^2 = 1` then `rho_H = 1` already,
and a correlation of 1 survives any range restriction: both variances shrink by the same factor
and the ratio is unchanged. That is why the third condition exists, and it was added on
2026-09-07 as pass-1 item D17. Before that the proposition said "`q < 1` and `rel_H < 1`", which
misses strictness through the `rho_T^2` factor. Know that history; it is the kind of thing a
careful reader will reconstruct.

This is indirect range restriction, Thorndike case III. The detector is the third variable and
fluency-correlated trait variance is what gets discarded.

> **FLAG 5 (an assumption doing real work that neither file discusses).** Step 4 needs
> `e` independent of `(theta, F)`. In the model that is stipulated. In an application it is a
> claim about the world, and a doubtful one: the detector scores the same text a human rater
> scores, so surface polish plausibly drives both the detector's `F` and the rater's error `e`.
> If `Cov(F, e | H) != 0`, then `Var(x | H, pass) != s2_T q + s2_H`, step 5's first line fails,
> and the clean `q / sqrt(...)` form of (E34) is not the right object. The sign of the bias is
> then no longer guaranteed by the convexity argument. Neither `lane1-zero-coupling.md` section
> 6.3 nor paper section 2.3 raises this. If a committee member raises it, concede it as a scope
> condition on the measurement model, not on the algebra, and note that `Var(w | H, pass)` is
> safe under the weaker and much more defensible claim that the outcome noise `u` is independent
> of the text.

> **FLAG 6 (notation, not an error).** The derivation writes `sp_bar` for marginal specificity
> and explicitly says it is "the same number as `sp` in 6.1; the bar marks it as the average of
> `sp(f)`". Paper section 2.3 drops the bar. Consistent, but if you write `sp` on a board and
> then say "average specificity", say which one you mean.

### 3.4 Assumptions doing real work, and what breaks

| Assumption | What it buys | What breaks without it |
| --- | --- | --- |
| `(theta, F)` bivariate normal | The closed form `q = 1 - r_F^2 psi` | The *direction* survives (Lemma 1 and Chebyshev need no normality), but the magnitude does not. Non-Gaussian detectors are logged as Q9 in `lane1-open-questions.md`, still open. |
| Pass rule is a monotone threshold on `F` | `Cov(F, sp(F)) > 0`, so the mean shift is signed | A non-monotone rule (flag both the most fluent and the least fluent text) can zero the covariance or reverse it. Real detectors are monotone in their own score, so this is safe, but it is an assumption. |
| `e`, `u` independent of `(theta, F)` | Step 4 | See FLAG 5. |
| Detection depends on the text only through `F` | The whole one-dimensional treatment | Multidimensional detection means `q` becomes a matrix contraction; the sign argument still runs if selection is on any scalar monotone index. |
| `r_F != 0` | Nonzero effect | At `r_F = 0` the result is exactly nil. That is not hypothetical: paper section 5.7's watermark case builds `r_F = 0` by construction, and the collider terms vanish identically. |
| `sp_bar < 1` | `tau` finite, so `psi > 0` | A detector that never flags a human deletes nobody and induces nothing. This is why sensitivity is irrelevant and specificity is everything. |

### 3.5 A tiny numeric example

At the degraded operating point `sp_bar = 0.85`:

    tau = Phi^{-1}(0.15) = -1.036
    lambda = phi(-1.036) / 0.85 = 0.2333 / 0.85 = 0.274
    psi = 0.274 * (0.274 + 1.036) = 0.274 * 1.310 = 0.360

Take `r_F = 0.5`, `rel_H = 0.7`, `rho_T = 0.5`:

    q = 1 - 0.25 * 0.360 = 0.910
    1 - rel_H (1 - q) = 1 - 0.7 * 0.09 = 0.937
    1 - rho_T^2 (1 - q) = 1 - 0.25 * 0.09 = 0.9775
    rho_H,pass / rho_H = 0.910 / sqrt(0.937 * 0.9775) = 0.910 / 0.957 = 0.951

A 5% relative hit with zero machine responses in the sample. Now put in the number actually
measured on the essays testbed, `r_F = 0.053`: `q = 1 - 0.0028 * 0.36 = 0.99899`, and the ratio
is 0.9995. Five hundredths of a percent.

Carry both. The first says the mechanism is real and non-trivial at a plausible-sounding `r_F`.
The second says the paper does not claim it bites at the `r_F` this project measured. Volunteer
the second before anyone asks for it.

### 3.6 Three committee questions

**Q. "Surely a better detector fixes this."**
Only along one axis. Note that neither `pi` nor `se` appears anywhere in (E32) to (E34). Prop. 14(i)
makes it formal: as `se -> 1`, `pi' -> 0` and `Att_pass` converges to the (E34) ratio, which is
strictly below 1 by Prop. 11 and does not depend on `pi` or `c`. The only route to zero is
`sp_bar -> 1`, which sends `tau -> -infinity`, `psi -> 0`, `q -> 1`. Perfect sensitivity does not
help because the bias lives entirely on the human side of the sample. The oracle (`se = sp = 1`)
is the only point where `Att_pass = 1`.

**Q. "How big is it really?"**
`O(r_F^2)`, which is the whole answer. The measured `r_F` on this project's testbed is 0.045 from
the detector's own score and 0.053 from surface proxies, both reported as lower bounds. At those
values the detector destroys about 0.1% of trait variance, and deletion still nets roughly five
points of recovered contamination attenuation. The paper ships this as a sensitivity table over
`r_F` (section 5.6, Table 11), not as a kill claim. SPEC 1.5's original unconditional
"detect-and-delete is dead" was retracted on 2026-09-10 for exactly this reason. Saying that
first is stronger than being walked to it.

**Q. "Where does the inequality actually come from? Range restriction usually shrinks everything."**
It does, but not by the same factor. The numerator of the correlation is pure true-score
covariance, so it takes the full factor `q`. Each denominator is a mix of true score and noise,
and only the true-score share is exposed to the selection, so each denominator falls by less:
`1 - rel_H (1 - q)` is `rel_H q + (1 - rel_H)`, a convex combination of `q` and 1. Top shrinks
more than bottom, ratio falls. And that is also why the degenerate case exists: when
`rel_H = rho_T = 1` there is no noise to protect the denominator, everything shrinks by `q`, and
the correlation is unchanged at 1.

### 3.7 Thirty seconds, out loud

"The obvious fix for ghostwritten survey responses is to run a detector and delete what it
flags. The problem is what the detector is actually thresholding on. It is fluency, or something
like it, and fluency correlates with the trait you are measuring. So when you delete flagged
cases, you are not removing a random slice of your humans, you are shaving off the low-fluency
tail, and that tail carries trait variance. The correlation you compute afterward is lower than
the clean one, and it stays lower no matter how good your sensitivity gets, because the whole
problem is on the human side. Only specificity helps. The size scales with the square of the
fluency-trait correlation, and on my testbed that correlation is about 0.05, so the cost is
about a tenth of a percent of trait variance. The mechanism is real. At my measured numbers it
is small, and I report it as a sensitivity band rather than a headline."

---

## 4. The three together

Read this page last, and read it again before you walk in.

**They are one chain, and the chain is the paper's argument.**

(E7) is the diagnosis. Contamination is not dilution. It moves the numerator of a correlation
(less trait covariance per contaminated response) and the denominator (machine text is usually
less dispersed, but a mean gap between the groups inflates the pooled variance). Which term
moves more decides everything, so the bias has no fixed sign. That is the claim you have to
land first, because every intuition in the room will be "you lose a fraction of your signal".

(E39) is the diagnosis compressed to a sentence you can use. Expand (E7) at small `pi` and the
whole two-dimensional map collapses to a single comparison: `c` against `c_2(delta)`, at a rate
`pi sqrt(kappa / rel_H)`. That is how you say the result without a blackboard. The cost of the
compression is that the sign rule is a `pi -> 0` statement and the true boundary `c*(pi)` drifts
away from `c_2` as `pi` grows (FLAG 2). On this paper's grid, which stops at `pi = 0.30`, they
agree; say so with the number rather than leaving it implicit.

Prop. 11 is why the obvious fix fails, and it is the piece that is structurally different from
the other two. (E7) and (E39) describe what contamination does to you. Prop. 11 describes what
your *response* to contamination does to you. It runs on a mechanism the first two do not have:
a collider. Under A1, authorship and trait are independent. Deletion conditions on the detector,
the detector is a common effect of authorship and of fluency, and fluency is downstream of the
trait. Conditioning on a collider manufactures the dependence A1 ruled out. Formally the
survivor sample is an A1' mixture with an induced trait gap `d_theta = -r_F lambda` and unequal
within-class trait variances, which is exactly the structure section 4b built for a different
reason, and which the day-2 file then evaluates as (E48) to (E51).

**The joint through-line, in one sentence each.**

1. Contamination biases validity by a known factor with no fixed sign (E7).
2. To first order the sign is one comparison, `c` against `c_2(delta)` (E39).
3. Deleting the contamination introduces a second, independent bias that no amount of
   sensitivity removes (Prop. 11).
4. So the honest output is not a correction, it is a sensitivity band: fix `pi, kappa, delta,
   rel_H`, treat `c` as unidentified in `[0, 1]`, and invert (E7) at both endpoints. That is the
   `bounds_c` estimator, and (E36) (`Att` affine and increasing in `c`) is what makes
   "invert at both endpoints" valid rather than a guess.

**How the pieces reuse each other.** `bounds_c` inverts (E7), and needs (E36) for monotonicity.
Prop. 14 evaluates the survivor sample using (E40) to (E43), whose special case (c) at `pi' = 0`
is exactly (E34), which is Prop. 11. So Prop. 11 is not a side result; it is the `pi' = 0`
boundary condition of the survivor formula, which is why Prop. 14(i) can say the bias does not
vanish as `se -> 1` just by taking a limit into Prop. 11.

**The three magnitudes to have memorized.**

- Contamination at `pi = 0.10`, `c = 0`, `kappa = 0.2`, `rel_H = 0.7`: `Att = 0.938`. Six points.
- The same cell after deletion at the degraded detector: 0.988. Deletion recovers five of them.
- The selection channel's own cost at the measured `r_F = 0.053`: 0.05% of the coefficient.

That ordering is the paper's honest headline. Deletion mostly works at the `r_F` this project
measured. What survives the measurement is the conditional claim: deletion-selection is a real
bias governed by `r_F` and by the out-of-domain false-positive rate, reported as a sensitivity
table, plus two things from Prop. 14 that do not depend on `r_F`'s size at all (the bias does
not vanish as `se -> 1`, and it is not monotone along a ROC curve).

---

## 5. Five flash checks

Cover the answer, say yours out loud, then look.

**1. In (E7), which of the five parameters does `Den(pi)` not depend on, and why does that
matter?**

<details><summary>answer</summary>

`c`. `Den` is the variance multiplier, and the coupling only affects how much *trait* signal the
machine text carries, not how dispersed it is. `Var(x | M) = s2_M = kappa V_H` holds for every
`c`, by construction of the second-moment representation. It matters because it is what makes
`Att` affine in `c` at fixed `pi` (E36), which is what lets `bounds_c` invert (E7) at the two
endpoints of a range for `c` and be certain it has bracketed the interior.
</details>

**2. A colleague says: "`Att > 1` must be a coding error, correlations attenuate under
contamination." Give the one-line refutation and the one-line boundary.**


<details><summary>answer</summary>

Refutation: at `pi = 1` the formula gives `Att = c / sqrt(rel_H)`, which exceeds 1 whenever
`c > sqrt(rel_H)`, and that matches the direct computation `Cor(x, w | M) = c rho_T`. A machine
that tracks the trait more faithfully than a noisy human measurement is a better indicator of
`theta`, so pooling it in raises the observed correlation.
Boundary: `Att = 1` exactly on `c*(pi) = sqrt(rel_H / kappa) [sqrt(Den(pi)) - (1 - pi)] / pi`
(E17), with `Att > 1` above it.
</details>

**3. State the sign rule of (E39), then state the one qualification you must attach to it.**

<details><summary>answer</summary>

Rule: `bias(rho_obs) = pi rho_H sqrt(kappa / rel_H) [c - c_2(delta)] + O(pi^2)`, so to first
order the bias has the sign of `c - c_2(delta)` with
`c_2(delta) = S sqrt(rel_H) / (2 sqrt(kappa))`, `S = 1 + kappa + delta^2`.
Qualification: it is a `pi -> 0` statement. The exact zero of the bias is `c*(pi)` from (E17),
and `c*(0+) = c_2` is a limit. At `kappa = 0.2, rel_H = 0.7, delta = 0, c = 1` the rule says
attenuation (`c < c_2 = 1.122`) and it is right at `pi = 0.1` and `pi = 0.3` (0.994, 0.987) and
wrong at `pi = 0.9` (1.098). The grid stops at `pi = 0.30`, where the rule holds.
</details>

**4. Prop. 11 says the deletion bias does not depend on `se`. Why not, in one sentence, and what
does that imply about which detector metric you should care about?**

<details><summary>answer</summary>

Because the bias lives entirely on the human side of the sample: (E32) to (E34) describe
`Cor(x, w | H, pass)`, and `se` only governs how many *machine* cases survive. Implication:
specificity is the metric, not sensitivity or AUC. `sp_bar -> 1` sends `tau -> -infinity`,
`psi -> 0`, `q -> 1`, and the bias to zero; `se -> 1` sends `pi' -> 0` and leaves the (E34)
ratio exactly where it was (Prop. 14(i)).
</details>

**5. In (E34) the numerator carries the factor `q` and the denominator does not. Say precisely
why, and name the case where the argument gives equality.**

<details><summary>answer</summary>

Selection on `F` shrinks only the trait variance, by the factor `q = 1 - r_F^2 psi`. The
covariance `Cov(x, w | H, pass) = b s2_T q` is pure true score, so it takes the full factor.
Each variance is part true score and part noise that selection never touched, so
`Var(x | H, pass) / V_H = rel_H q + (1 - rel_H)`, a convex combination of `q` and 1, which is at
least `q`. Same for the outcome with `rho_T^2`. Top falls more than bottom.
Equality case: `rel_H = 1` and `rho_T^2 = 1`, where there is no noise to protect the
denominators, every term scales by `q`, and `rho_H,pass = rho_H = 1`. That is the third
condition of Prop. 11, added as pass-1 item D17.
</details>

---

## 6. Three-minute refresh card

Read this in the corridor.

**The estimand.** `rho_H = Cor(x, w | H) = sqrt(rel_H) rho_T`. Observed-score validity in a
clean sample, decision N2. "Bias" means contamination bias and excludes classical attenuation.

**The five parameters.** `pi` prevalence, `c` coupling, `rel_H` reliability, `kappa` variance
ratio, `delta` mean gap. Plus `rho_T` wherever `Var(w)` matters.

**(E7).**

    Att = [ (1 - pi) + pi c sqrt(kappa/rel_H) ] / sqrt[ (1 - pi) + pi kappa + pi(1-pi) delta^2 ]

Numerator is signal covariance, denominator is pooled variance, bias is the race between them,
sign is not fixed. Checks: `pi = 0` gives 1; `pi = 1` gives `c / sqrt(rel_H)`;
`kappa = 1, delta = 0, c = 0` gives `1 - pi`.

**(E39).**

    bias = pi rho_H sqrt(kappa/rel_H) [ c - c_2(delta) ] + O(pi^2),
    c_2(delta) = S sqrt(rel_H) / (2 sqrt(kappa)),   S = 1 + kappa + delta^2

Below `c_2` contamination hides validity, above it manufactures it. Small-`pi` statement only;
the exact boundary is `c*(pi)` (E17). Amanuensis cell `c = kappa = 1, delta = 0`: slope
`1/sqrt(rel_H) - 1 = 0.195`, so `Att = 1.020` at `pi = 0.10`. A perfect ghostwriter is not
harmless.

**Prop. 11.**

    rho_H,pass / rho_H = q / sqrt[ (1 - rel_H(1-q)) (1 - rho_T^2(1-q)) ] < 1,
    q = 1 - r_F^2 psi,   psi = lambda(lambda - tau),   tau = Phi^-1(1 - sp_bar)

Conditions: `r_F != 0`, `sp_bar < 1`, not (`rel_H = 1` and `rho_T^2 = 1`). Collider: deletion
conditions on `D`, a common effect of `A` and `F`, and `F` is downstream of `theta`. Does not
involve `pi` or `se`. Only specificity removes it.

**Four numbers.**

| | |
| --- | --- |
| `Att` at `pi = 0.10, c = 0, kappa = 0.2, rel_H = 0.7` | 0.938 |
| the same cell after deletion, degraded detector | 0.988 |
| `rho_H,pass / rho_H` at `sp_bar = 0.85, r_F = 0.5` | 0.951 |
| the same at the measured `r_F = 0.053` | 0.9995 |

**The honest headline, in the order to say it.** The algebra is exact and reproduces on real
text. The deletion-selection bias is `O(r_F^2)` and at the measured `r_F` (0.045 detector score,
0.053 surface proxy, both lower bounds) it is negligible, so detect-and-delete is not killed;
SPEC 1.5's unconditional version was retracted on 2026-09-10. What survives measurement: the
mechanism is real and reported as a sensitivity table over `r_F`, plus two `r_F`-free facts from
Prop. 14 (the bias does not vanish as `se -> 1`, and it is not monotone along a ROC curve). The
shipped output is a sensitivity band from `bounds_c`, not a correction.

**Three sentences you should not say.** "Contamination attenuates" (not always, E17). "The sign
of the bias is the sign of `c - c_2`" without "to first order" (FLAG 2). "A better detector fixes
it" (only specificity, Prop. 14(i)).

---

## 7. Flags, collected

Six items. Four are in the paper or the derivation and you should raise them before a reader
does; two are notation.

| # | Where | What | Severity |
| --- | --- | --- | --- |
| 1 | `paper/GHOST-RESPONDENTS-DRAFT.md` s2.2 | "At `c = 0`, `Att_0` is strictly between 0 and `sqrt(1 - pi)`". (E10) writes `0 < Att_0(pi) <= sqrt(1 - pi) < 1` and states the equality case ("iff `kappa = 0` and `delta = 0`") on the next line, a degenerate but admissible corner (Prop. 3 is stated "for every `kappa >= 0`"). "Strictly between" overstates by one endpoint. | small |
| 2 | `paper/GHOST-RESPONDENTS-DRAFT.md` s2.2, the sentence after (E39) | "so the sign of the contamination bias is the sign of `c - c_2`" drops the first-order hedge the display carries. The global boundary is `c*(pi)` (E17); `c_2` is its `pi -> 0` limit. Counterexample on the project's own numbers: `kappa = 0.2, rel_H = 0.7, delta = 0, c = 1 < c_2 = 1.122`, yet `Att(0.9) = 1.098 > 1`. Harmless on a grid that stops at `pi = 0.30`, wrong as stated. | **real, prose** |
| 3 | (E39), `c` form | Undefined at `kappa = 0`: `c_2 -> infinity` and the product is `0 * infinity`. The `g` form `Att = 1 + pi[g - g_2(delta)]` is fine there. Use the `g` form for the constant-machine corner. | small, defensive |
| 4 | `derivations/lane1-partial-coupling.md` s1.5, the check sentence | Cites (E36) ("`Att` is affine in `c`") for exact linearity in `pi` at `Den = 1`. Wrong pointer, arithmetic correct. | bookkeeping |
| 5 | (E34) step 4, neither file | Needs `e` independent of `(theta, F)`. In an application the detector scores the same text a human rater scores, so `Cov(F, e | H) != 0` is plausible and would break `Var(x | H, pass) = s2_T q + s2_H`, hence (E34)'s clean form and the convexity argument for the sign. Stipulated in the model, undiscussed anywhere. Concede as a scope condition on the measurement model, not on the algebra. `Var(w | H, pass)` survives under the weaker claim that outcome noise is independent of the text. | **real, unflagged assumption** |
| 6 | `sp` vs `sp_bar` | The derivation writes `sp_bar` for marginal specificity and states it is the same number as `sp`; the paper drops the bar. Consistent, but be explicit if you write it on a board. | notation |

Nothing here blocks the three results. Items 2 and 5 are the two a careful reader will find, so
volunteer both.
