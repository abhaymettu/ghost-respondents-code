# Ownership walkthrough: source pointers and verification receipts

Companion to `notes/OWNERSHIP-E7-E39-P11.md` and `paper/ownership-walkthrough.html`.
Every equation taught in those two files is traced here to the line it was copied from, and
every number in them is traced to either a source line or a recomputation run in this session.

**Verdict: PASS.** All 22 display equations in section 1 match their source in notation.
All 21 numeric claims in section 2 reproduce. Six discrepancies between the paper's prose and the
derivations were found; all six are flagged in the deliverables rather than taught past, and
none of them invalidates (E7), (E39), or Prop. 11. No file in `paper/` other than the new
`ownership-walkthrough.html` was touched, and nothing was published.

Sources, as of commit `47eaf6c`:

| Short name | Path |
| --- | --- |
| ZERO | `derivations/lane1-zero-coupling.md` |
| PART | `derivations/lane1-partial-coupling.md` |
| PAPER | `paper/GHOST-RESPONDENTS-DRAFT.md` |

---

## 1. Equation-by-equation pointers

Every display equation reproduced in the walkthrough, with the line it came from. "Match"
means the ASCII form in the walkthrough is the source's ASCII form with no re-notation.

| Equation | Source | Line | Also stated in paper | Match |
| --- | --- | --- | --- | --- |
| (E0a) `N(pi, c) := (1 - pi) + pi * g` | ZERO | 45 | PAPER 214 (inline) | yes |
| (E0b) `Den(pi) := (1 - pi) + pi * kappa + pi (1 - pi) delta^2` | ZERO | 46 | PAPER 214 (inline) | yes |
| (E1) the two-process mixture | ZERO | 58 | PAPER 200-203 (prose form) | yes |
| (E3) `Var(x) = ... = V_H * Den(pi)` | ZERO | 76 | not displayed | yes |
| (E4) `Cov(x, w) = b s2_T * N(pi, c)` | ZERO | 80 | not displayed | yes |
| (E5) `rho_obs = rho_H * N / sqrt(Den)` | ZERO | 94 | PAPER 214 | yes |
| **(E7)** `Att(pi, c) = [...] / sqrt[...]` | ZERO | 102 | PAPER 214 (as `Att := N / sqrt(Den)`) | yes |
| (E10) `0 < Att_0(pi) <= sqrt(1 - pi) < 1` | ZERO | 116, equality case 118 | PAPER 216 (as "strictly between") | **mismatch, see D1** |
| (E17) `c*(pi) = sqrt(rel_H/kappa) [sqrt(Den) - (1-pi)] / pi` | ZERO | 173 | not displayed | yes |
| (E15)/(E16) `g_1, g_2, c_1, c_2` at `delta = 0` | ZERO | 158, 162 | superseded by Prop. 12 form | yes |
| (E30) `pi' = (1-se) pi / [(1-se) pi + sp (1-pi)]` | ZERO | 305 | PAPER 236 | yes |
| (E31) Lemma 1, the mean shift | ZERO | 319 | not displayed | yes |
| (E32) `E[theta | H, pass] = r_F sqrt(s2_T) lambda` | ZERO | 337 | not displayed | yes |
| (E33) `q := 1 - r_F^2 psi` | ZERO | 338 | PAPER 239 | yes |
| **(E34)** `rho_H,pass = rho_H * q / sqrt[...]` | ZERO | 346 | PAPER 242 | yes |
| **Prop. 11** statement and proof | ZERO | 350, proof 352 | PAPER 244-245 | yes |
| (E36) `Att` affine in `c` | PART | 49 | PAPER 219 (prose) | yes |
| (E37) `G(pi)` at general delta | PART | 65 | not displayed | yes |
| Prop. 12 `g_1(delta), g_2(delta), c_1(delta), c_2(delta)` | PART | 69-73 | PAPER 221-224 | yes |
| (E38) `pi_min` | PART | 75 | not displayed | yes |
| **(E39)** both halves | PART | 85 | PAPER 227 (**bias half only**) | yes, see D2 |
| (E76) `Att = 1 + pi (1/sqrt(rel_H) - 1) > 1` | PART | 271 | PAPER 230 | yes |

Notation decoder entries (theta, w, pi, rho_T, rel_H, rho_H, c, kappa, delta, g, se, sp_bar,
F, r_F, tau, lambda, psi, q) all come from ZERO section 0 (lines 9-53) and ZERO section 6.3
(lines 317-338); the inherited-symbol list in PART section 0 (line 11) confirms day 2 uses
each with the same meaning. `rho_H` as the headline estimand is decision N2, ZERO line 27 and
PART section 8, restated at PAPER 196-199.

---

## 2. Numeric receipts

Recomputed this session in `python3` from the closed forms, not copied from a table. Command
form: `Att(p,c,k,rel,d) = ((1-p)+p*c*sqrt(k/rel)) / sqrt((1-p)+p*k+p*(1-p)*d*d)`; the
Prop. 11 ratio from `tau = NormalDist().inv_cdf(1-sp_bar)`, `lam = pdf(tau)/sp_bar`,
`psi = lam*(lam-tau)`, `q = 1-r_F^2 psi`.

### (E7)

| Claim in the walkthrough | Recomputed | Source it must match | Status |
| --- | --- | --- | --- |
| `pi=.5, c=0, kappa=1, delta=0` gives `Att = 0.5` | 0.500000 | (E7) boundary check, ZERO 104 | PASS |
| `pi=.5, c=0, kappa=0, delta=0` gives `0.707` | 0.7071068 = `1/sqrt(2)` | (E10) bound attained | PASS |
| `pi=.10, c=0, kappa=0.2` gives `Att = 0.938` | 0.9383149 | PART 1.6 table (0.938); PAPER 438, 851 (0.9383) | PASS |
| `pi=1` gives `c / sqrt(rel_H)` | identity check | ZERO 104 | PASS |

### (E39)

| Claim | Recomputed | Source | Status |
| --- | --- | --- | --- |
| `c=1, kappa=1, delta=0, rel_H=0.7`: `g = 1.195` | 1.1952286 | PART 87 ("+0.195 pi rho_H") | PASS |
| slope `g - g_2 = 0.195` | 0.1952286 | PART 87 | PASS |
| linear `Att` at `pi=0.10` is 1.0195; exact table 1.020 | linear 1.0195229, exact 1.0195229 (identical, `Den = 1`) | PART 1.6 table row `0.10 / 1.0 / c=1` = 1.020 | PASS |
| `c_2 = 1.122` at `kappa=0.2, rel_H=0.7, delta=0` | 1.1224972 | PART 91 | PASS |
| `c_1 = 0.624` at the same cell | 0.6236096 | PART 91 | PASS |
| Flag 2 counterexample: `Att(0.1)=0.994, Att(0.3)=0.987, Att(0.9)=1.098` at `c=1, kappa=0.2` | 0.9938, 0.9869, 1.0981 | ZERO 169 (0.994, 0.987, 0.991, 1.016, 1.098) | PASS |
| Flag 2 crossing `c*(0.6) = 1.0012` | 1.0012 | ZERO 169 ("crosses 1 at pi = 0.60") | PASS |
| first-order gaps 0.0004 / 0.0036 / 0.157 | 0.00036, 0.00360, 0.15698 | derived here, no source claim | PASS (own computation, labelled as such) |

### Prop. 11

| Claim | Recomputed | Source | Status |
| --- | --- | --- | --- |
| `sp_bar=0.85`: `tau = -1.036, lambda = 0.274, psi = 0.360` | -1.03643, 0.27440, 0.35956 | ZERO 358 | PASS |
| `r_F=0.5`: `q = 0.910` | 0.91011 | ZERO 359 | PASS |
| `rho_H,pass / rho_H = 0.951` at `rel_H=0.7, rho_T=0.5` | 0.95093 | ZERO 359 (0.951) | PASS |
| `r_F=0.3`: `q = 0.968`, ratio `0.983` | 0.96764, 0.98280 | ZERO 358 (0.968, 0.983) | PASS |
| `sp_bar=0.99, r_F=0.5`: `q = 0.984`, ratio `0.992` | 0.98416, 0.99157 | ZERO 360 (0.984, 0.992) | PASS |
| `r_F=0.053`: `q = 0.99899`, ratio `0.9995` | 0.998990, 0.99947 | PAPER 859 (`q = 0.99910` at r_F=0.05; 0.10% of trait variance destroyed at 0.053, PAPER 860-863) | PASS |
| `pi' = 0.019` at `se=sp=0.85, pi=0.10` | 0.0192308 | ZERO 307 | PASS |
| measured `r_F`: 0.045 detector score, 0.053 surface proxy | not recomputed | PAPER 45-46, 828, 846; `paper/tables/tab_rF_sensitivity.md` line 17 | PASS (quoted, both stated as lower bounds) |
| deletion at the `pi=0.10, kappa=0.2, c=0` cell moves 0.938 to 0.988 | not recomputed | PAPER 864 ("from 0.938 to 0.988"), PAPER 851 | PASS (quoted) |

---

## 3. Discrepancies found

Six. All six appear in both deliverables, numbered identically, at the point they bite and in
a collected table. None blocks the three results.

| # | Location | Finding | Kind |
| --- | --- | --- | --- |
| D1 | PAPER 216 vs ZERO 116-118 | Paper: `Att_0` is "strictly between 0 and `sqrt(1 - pi)`". (E10): `0 < Att_0(pi) <= sqrt(1 - pi)`. ZERO 118 names the attainment condition outright: "with equality ... iff kappa = 0 and delta = 0", where `Den = 1 - pi` and `Att_0 = sqrt(1 - pi)` exactly. Prop. 3 (ZERO 130) is stated "for every `kappa >= 0`", so the corner is in scope. The paper overstates by one endpoint, against its own source. | paper prose |
| D2 | PAPER 229 vs (E17)/Prop. 4 | Paper: "so the sign of the contamination bias is the sign of `c - c_2`". (E39) is `+ O(pi^2)`; the global zero is `c*(pi)` (E17), and `c*(0+) = c_2` is a limit (ZERO 177). Counterexample from ZERO 169: at `kappa=0.2, rel_H=0.7, delta=0, c=1 < c_2=1.122`, `Att(0.9) = 1.098 > 1`. Harmless on a grid capped at `pi = 0.30`; wrong as a general sentence. | paper prose |
| D3 | (E39) `c` form | Undefined at `kappa = 0`: `c_2 -> infinity`, product is `0 * infinity`. The `g` form at PART 85 is well defined there. Defensive note, not an error in either file. | scope |
| D4 | PART 87 | Check sentence cites (E36) ("`Att` affine in `c`") for exact linearity in `pi` at `Den = 1`. Wrong equation pointer; the arithmetic it defends is correct (verified: linear and exact both 1.0195229). | bookkeeping |
| D5 | ZERO 340-344, PAPER 236-245 | (E34) step 4 requires `e` independent of `(theta, F)`. A real detector scores the same text a human rater scores, so `Cov(F, e | H) != 0` is plausible; that would break `Var(x | H, pass) = s2_T q + s2_H` and with it the convexity argument for the sign. Stipulated in the model, discussed in neither file. `Var(w | H, pass)` survives under the weaker claim that outcome noise is independent of the text. | unflagged assumption |
| D6 | ZERO 317 vs PAPER 236-237 | Derivation writes `sp_bar` (marginal specificity), paper writes `sp`. ZERO 317 states they are the same number. Consistent; noted so the two spellings are not read as two quantities. | notation |

D2 and D5 are the two a careful reader finds first. Both are called out in the walkthrough as
things to volunteer rather than defend.

---

## 4. Render receipt

`paper/ownership-walkthrough.html` was rendered and visually inspected in Chromium
(Chrome/153.0.8010.12, headless, via CDP), served from `127.0.0.1:8777`, at device scale 2.

| Check | Result |
| --- | --- |
| Console errors | 1, a `favicon.ico` 404 from the throwaway local server. No page errors. |
| Screens inspected | header + contents; (E7) derivation; (E39) flags 2-4 and assumption table; five flash checks with all reveals open; refresh card; Prop. 11 tables. Light and dark. |
| Defect found and fixed | Equation blocks were clipped at the prose measure: (E1), (E3), (E5) and others ran past the right edge with no visible affordance. Fixed by bleeding `.eq`, `.tbl` and `.card` to `min(100vw - 2.5rem, 50rem)` centred on the measure. |
| Clipped equation blocks after fix | 0 of 31 at 1440, 1180 and 900 px |
| Page-level horizontal scroll | none at 1440 / 1180 / 900 / 760 / 420 px (`documentElement.scrollWidth == innerWidth` at each) |
| Narrow widths | at 760 px 3 of 31 equations scroll inside their own container, at 420 px 28 of 31; by design, `overflow-x: auto` per block, body never scrolls. Mono size drops a step below 640 px. |
| Themes | light and dark both rendered and read; tokens defined on bare `:root` with a `prefers-color-scheme` override |
| Reduced motion | `@media (prefers-reduced-motion: reduce)` collapses transition durations and drops the reveal transform |
| Print | print stylesheet drops the bleed and hides the contents nav. Flash-check answers print only if opened first: a closed `<details>` hides its content in the UA sheet and no print rule can override that cross-engine. Noted rather than worked around. |
| Dependencies | none. No external font, script, stylesheet or image; the file is self-contained. |
| Published | no. Rendered locally only; the local server and browser were stopped afterward. |

---

## 5. Scope

- `paper/GHOST-RESPONDENTS-DRAFT.md` was read, not modified. `git status` shows no change to it.
- The only new file under `paper/` is `ownership-walkthrough.html`.
- Nothing was published to any external surface.
