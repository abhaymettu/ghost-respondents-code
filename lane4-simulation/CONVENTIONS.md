# Lane 4 shared contract (binding on every module)

Frozen by the lane-4 orchestrator before any code was written. Every module below
must match this file exactly. If a subagent thinks the contract is wrong, it says so
in its report and does NOT unilaterally change it.

Notation follows `derivations/lane1-zero-coupling.md` section 0 and the binding
decisions N1, N2, N3, Q7 in `derivations/lane1-open-questions.md`.

## Scale normalization (fixed, never a free parameter)

    s2_T = Var(theta)     = 1
    V_w  = Var(w)         = 1
    mu_H = 0

Everything else is derived from the five standardized parameters plus rho_T:

    V_H     = s2_T / rel_H = 1 / rel_H          # human observed-score variance
    s2_H    = V_H - s2_T   = (1 - rel_H)/rel_H  # human measurement-error variance
    s2_M    = kappa * V_H                       # machine observed-score variance
    Delta   = delta * sqrt(V_H)                 # unstandardized mean gap mu_H - mu_M
    mu_M    = mu_H - Delta = -Delta
    b       = rho_T                             # since s2_T = V_w = 1
    s2_u    = 1 - rho_T^2
    lam_M   = c * sqrt(s2_M / s2_T) = c * sqrt(s2_M)     # N1: g in lane 1's notation
    s2_v    = (1 - c^2) * s2_M

Truth values every metric is scored against:

    rho_H = sqrt(rel_H) * rho_T      # PRIMARY estimand (N2 DECIDED 2026-09-07)
    rho_T = rho_T                    # SECONDARY, disattenuated
    true parallel-item standardized loading = sqrt(rel_H)

## Cell (the grid unit)

```python
@dataclass(frozen=True)
class Cell:
    pi: float          # contamination fraction
    c: float           # coupling = Cor(x, theta | M)   (N1: the CORRELATION, not the slope)
    n: int
    detector: str      # "none" | "calibrated" | "degraded" | "oracle"
    kappa: float       # s2_M / V_H            (N3)
    rho_v: float = 0.0 # shared machine residual correlation across items (Q7 default arm)
    rel_H: float = 0.7
    delta: float = 0.0 # (mu_H - mu_M) / sqrt(V_H)
    rho_T: float = 0.5
    k: int = 4         # number of parallel indicators
    r_F: float = 0.3   # fluency-trait correlation (drives deletion-selection)
    d_theta: float = 0.0   # A1' trait mean shift of machine users, in trait SD; 0 = ignorable (A1)
    arm: str = "base"
```

## DGP (SPEC 4.1 with lane 1's N1 form)

Per respondent i:

    theta_i ~ N(0, 1)                     [under A1' add d_theta to the M class, see below]
    A_i     ~ Bernoulli(pi)               1 = machine
    u_i     ~ N(0, s2_u)
    w_i     = b * theta_i + u_i

    human  items:  x_ij = mu_H + theta_i + e_ij,           e_ij ~ N(0, s2_H) iid over j
    machine items: x_ij = mu_M + lam_M * (theta_i - d_theta) + v_ij

with v_i ~ N_k(0, s2_v * [(1 - rho_v) I + rho_v J]), i.e. equicorrelated with
correlation rho_v and variance s2_v on each item.

Non-ignorable arm (A1', lane 1 section 4b): theta | M ~ N(d_theta, 1),
theta | H ~ N(0, 1). Implement by drawing theta ~ N(0,1) and adding d_theta where
A = 1. The machine mean is re-centred by subtracting d_theta inside lam_M(...) so
that E[x | M] = mu_M regardless of d_theta, exactly as lane 1 writes it.
Default d_theta = 0 recovers A1.

Checks the DGP must satisfy in-sample at large n (these are unit tests):
- Cor(x_j, theta | M) = c
- Var(x_j | M)        = s2_M
- Var(x_j | H)        = V_H
- Cor(x_j, x_l | M)   = c^2 + rho_v (1 - c^2)      (E24)
- Cor(x_j, w | H)     = rho_H

## Detector

Human side is lane 1's Gaussian threshold on fluency (section 6.3):

    F_i  = r_F * theta_i + sqrt(1 - r_F^2) * eta_i,   eta_i ~ N(0,1) independent
    human passes iff F_i > tau,   tau = Phi^{-1}(1 - sp)

Machine side: flagged ~ Bernoulli(se), independent of theta (lane 1 section 6.4
assumption; automatic at c = 0).

Operating points (se = P(flag | M), sp = P(pass | H)):

| name       | se   | sp   | note |
| ---------- | ---- | ---- | ---- |
| none       | 0.00 | 1.00 | no deletion; naive only |
| calibrated | 0.95 | 0.99 | NORC in-domain end |
| degraded   | 0.85 | 0.85 | NORC out-of-domain end |
| oracle     | 1.00 | 1.00 | perfect; concede it wins (SPEC 4.4) |

sp = 1 means tau = -inf, every human passes. se = 0 means nothing is flagged.

## Sample object

`simulate(cell, rng) -> Sample` with numpy arrays:

    theta (n,)   w (n,)   X (n, k)   A (n,) uint8 1=machine   F (n,)   flag (n,) bool

The headline indicator is `X[:, 0]` (a SINGLE indicator), because every lane-1
closed form (E5)-(E9), (E34) is a single-indicator statement. The remaining k-1
items exist for the between-item metrics (E26), the loading metric, and the
mixture/label-free estimators. Do not silently switch the headline to a composite.

## Estimator return contract

```python
@dataclass
class Fit:
    name: str
    rho_H_hat: float             # estimate of rho_H = Cor(x_1, w | H)
    rho_T_hat: float             # estimate of rho_T = Cor(theta, w)
    pi_hat: float | None
    rel_hat: float | None        # that estimator's own reliability estimate
    ci_H: tuple[float, float] | None   # nominal 95% CI for rho_H
    ci_T: tuple[float, float] | None   # nominal 95% CI for rho_T
    loading_hat: float | None    # implied standardized human loading (truth sqrt(rel_H))
    seconds: float
    converged: bool = True
    note: str = ""
    seconds_resample: float | None = None   # see below
```

`seconds_resample` (added 2026-09-07, additive with a default, so existing callers
are unaffected) is the share of `seconds` spent resampling rather than computing the
point estimate: EM's parametric bootstrap and SIMEX's remeasurement Monte Carlo. It is
`None` for estimators that do no resampling, so "does not resample" stays
distinguishable from "resamples, but immeasurably fast". It exists because resampling
is the part of grid cost that can be traded against interval quality by lowering
`B`/`B_boot`, and the grid needs to see that split to make the trade. `run_cell`
aggregates it into `timing[name]["mean_seconds_resample"]` and `["resample_share"]`.

Every estimator reports BOTH rho_H_hat and rho_T_hat so that Abhay's pending N2
call costs no rework. The relation is rho_T_hat = rho_H_hat / sqrt(rel_hat) using
that estimator's OWN rel_hat (what a researcher running that estimator would
actually report), not the true rel_H. For parallel items the standardized loading
and reliability are linked by rel = loading^2, so rel_hat = mean between-item
correlation and loading_hat = sqrt(max(rel_hat, 0)).

A fit that fails returns the dataclass with NaNs, `converged=False` and a note.
It never raises.

## Seeds

Master seed per run. Per (cell, rep) stream via
`np.random.SeedSequence(master).spawn()` indexed by a deterministic
`(cell_id, rep)` hash, so a rep's draw does not depend on shard boundaries or
on execution order. Cell id is a stable hash of the sorted Cell field values.

## Style

numpy + scipy + scikit-learn only. No pandas, no config framework, no plotting.
Files stay flat in `lane4-simulation/`. Type hints on public functions.

## Scoped exception to "files stay flat" (added 2026-09-07, Layer B)

Layer A stays flat in `lane4-simulation/`. Layer B lives in the package
`lane4-simulation/inject/` (`pools.py`, `assign.py`, `build.py`, `test_inject.py`), because
the P1' injection design is a coherent unit with its own contract with lane 3 and its own
test suite. This is the ONLY package exception; no other module may take it without the same
declaration. Rationale and the rest of Layer B's contract deviations: `INJECT.md` section 10.
