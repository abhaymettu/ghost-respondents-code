# Lane 4: Layer A simulation harness

Parametric Monte Carlo engine for SPEC section 4.1 to 4.4. Built day 1, **not yet run at grid
scale**: the pilot cell plus the orchestrator's line-by-line estimator review comes first, and
lane 1's day-2 handoff (section 6.4, Att'') may still adjust the DGP.

## Files

| file | what it is |
| --- | --- |
| `CONVENTIONS.md` | the binding contract: scale normalization, DGP form, detector, `Fit` shape, seeding. Frozen before any code was written. |
| `dgp.py` | `Cell`, `Sample`, `simulate`, `rep_rng`. Lane 1's N1 form, N3's kappa, Q7's rho_v. |
| `population.py` | every lane-1 closed form (E0 to E34) as a pure function, for verification pass 2. |
| `estimators.py` | naive, detect-and-delete, MC-SIMEX, label-free prevalence + EIV, EM mixture. |
| `metrics.py` | SPEC 4.4 metrics for **both** rho_H and rho_T, plus the pre-registered success flags. |
| `grid.py` | grid construction, cost estimation, sharded multiprocessing runner. |
| `run_pilot.py` | the one frozen pilot cell, end to end, writing `PILOT.md`. |
| `test_dgp.py`, `test_population.py`, `test_estimators.py` | plain-assert self-checks, no pytest. |

## Environment

```
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python numpy scipy scikit-learn
```

Everything runs as `.venv/bin/python <file>`. No pandas, no plotting, no config framework.

## Notation, and the three decisions it rests on

Lane 1's binding decisions, implemented literally:

- **N1**: `c` is the *correlation* `Cor(x, theta | M)`, not the slope. The DGP uses
  `x | M = mu_M + c sqrt(s2_M / s2_T) theta + v` with `Var(v) = (1 - c^2) s2_M`, so `c` means
  exactly what SPEC 1.2 says it means. Lane 1's `g = c sqrt(kappa / rel_H)` is the slope and it
  is carried explicitly everywhere the algebra needs it.
- **N2**: **decided 2026-09-07.** The headline estimand is the observed-score
  `rho_H = Cor(x, w | H)`, the clean-sample observed validity, so "bias" means contamination
  bias and excludes classical attenuation. The latent `rho_T = rho_H / sqrt(rel_H)` is retained
  as the robustness estimand. **Every metric is computed for both**, unchanged: the decision
  fixes which one is the headline, not what is computed. (SPEC 1.1/1.3 wording is Abhay's
  call, Q3, and is untouched here.)
- **N3**: `kappa = s2_M / V_H` is a grid parameter in its own right, `{0.2, 0.5, 1.0}`, covering
  SPEC's homogenized case and the no-homogenization control.
- **Q7**: `rho_v`, the shared machine residual across items, is a grid parameter. The default arm
  is `rho_v = 0` (independent calls per item); lane 3 measures the real value on the generated
  counterparts and the grid picks it up from there.

## Running it

```
.venv/bin/python run_pilot.py                     # the frozen pilot cell -> PILOT.md
.venv/bin/python grid.py --dry-run --arms base    # cell count and core-hour estimate, runs nothing
.venv/bin/python grid.py --arms base --reps 500 --workers 12 --out results/
.venv/bin/python grid.py --arms base --shard 0/4  # shard by cell across processes or reruns
```

The runner shards by cell (fits are embarrassingly parallel, SPEC section 6) and is resumable:
a cell whose `cell_id` already has a line in the output directory is skipped.

## Reproducibility

Seeds are per `(cell_id, rep)` via `SeedSequence`, so a replication's draw does not depend on
shard boundaries or execution order. The pilot's master seed is frozen at `20260907` and
recorded in `PILOT.md` along with the exact reproducing command and package versions.

## What this harness is for

Layer A's purpose is proof, not realism (SPEC 4.1). Every closed form in
`derivations/lane1-zero-coupling.md` is a population moment this engine computes empirically;
a mismatch invalidates the derivation, not the simulation. `population.py` and the population
columns in every results row exist so that verification pass 2 is mechanical.
