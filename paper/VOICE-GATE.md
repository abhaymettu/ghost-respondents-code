# Voice gate: PASS

Gate run 2026-09-13 on the A-through-F iteration of `GHOST-RESPONDENTS-DRAFT.md` (rounds A, B,
C, D from `notes/PUBLISH-BAR.md`). Supersedes the 2026-09-13 gate on c5136ad. Working tree
under `paper/` was clean of unrelated edits at gate time. No rewrites were made by this gate.

## Receipts

### 1. Register grep across the draft

Pattern set: honest, we report / I report, we withdraw, transparen, candor, candid, failed
hypothes, failure is the finding, at full magnitude, worth naming, flatter, papered over,
smoothed, own failure, stated plainly, nothing was tuned, declines to, refuses to, I admit, to
be fair, it is worth noting, delve, crucial, robustly, comprehensive, nuanced, leverage,
underscore, testament, landscape, realm, tapestry, "not only ... but also".

Zero hits.

The three surviving `concede` / `conceded` / `concession` hits (draft 407, 591, 609) are the
T4 status label for the oracle arm, allowed by the previous gate for the same reason: a status
word, not a virtue claim.

Em dashes: zero.

### 2. Two register defects introduced by this round, both removed before the gate

- 6.2 draft carried "Used honestly it is a sensitivity analysis". Replaced with "The use it
  supports is a sensitivity analysis". Announcing honesty is the banned move.
- 5.4 draft carried "which bounds it near 0.09" with no artifact behind 0.09. Replaced with
  "at roughly a tenth of the estimand", which the MCSE column supports and which quotes no
  unsourced number.

### 3. Numbers

`paper/scripts/check_numbers.py`, run on the result:

| | baseline (draft 2 at 9e90bc6) | after A-F |
|---|---|---|
| pass 1: numbers.json keys appearing in the draft | 427 of 430 | 448 of 452 |
| pass 2: distinct unsourced numeric tokens | 156 | 135 |

The four pass-1 misses are non-numeric metadata values (`None`, `False`, and two label
strings), not numbers the draft fails to quote. The set of unsourced tokens shrank by 21 and
gained nothing: a set-difference of the two token lists is empty in the new-only direction.

Numeric-token diff on the draft (removed-only vs added-only multisets, `git diff`):

- Removed-only numbers are the old Table 7 best-of-five values and winner counts (17, 11), the
  three old boundary values 0.335 / 0.398 / 0.316, the old "61 of 72 under 0.10" and "8.0%",
  the three "78%" restatements of the bound's target, `0.073` in its 5.6 sentence, and `2024`
  from the cut Zhang and Tong reference. Every one is a deliberate deletion under D, A, or B.
- Added-only numbers are the new Table 7 cells and their MCSEs, the five detector-score
  correlations, 0.161, 0.172, 0.472, 1.28, 2467, and the resolvability counts 33 / 39 / 8.
  Each traces to `paper/tables/numbers.json`.

Facts the previous gate required to survive, re-checked live: 34% self-reported prevalence
(1.1), three of four thresholds fail outright (abstract, 1.2, Table 4), 274 of 336 cells
(abstract, 5.3, 6), 27% frontier sensitivity (Table 1, 5.4, 6), 78.1% of n = 1000 cells under
the width bar (5.4), 1116 moments (abstract, 5.1), EM slightly harmful (abstract, 5.5), SPEC
1.5's unconditional claim does not hold (5.6). All present.

### 4. Coherence read

Read end to end: abstract, 1.1, 1.2, 1.3, 4.3, 5.4, 5.6, 6, and the appendix.

Two claims written in this round were wrong on the read and were corrected before the gate:

- "Two thirds of the box has no visible contamination bias" against 39 of 72. Now "More than
  half".
- "the same estimator with the same draws in every row", asserting naive is identical across
  detector levels. It is not: 5.7 measures the per-detector seed spread. Now "naive ignores
  the detector by construction, and what varies down its column is per-detector seed noise
  (section 5.7 measures that spread)".

The bound's framing is consistent at all four sites it appears (abstract, 1.2 item 4, 5.4
bullet, 6.2): a conditional sensitivity band taking pi, kappa, delta and rel_H as known, with
coverage following from the construction, never "meets its target".

"Pre-registered" appears nowhere except the one sentence in 4.3 that says the work is not
pre-registered.
