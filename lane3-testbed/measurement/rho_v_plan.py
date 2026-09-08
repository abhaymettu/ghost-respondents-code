"""Day 2 part 3: measurement plan + code for rho_v (Q7) -- the shared
machine residual across items.

## What rho_v is

SPEC 1.4/H2 predicts homogenization: machine-authored item responses
correlate with each other beyond what the shared true trait theta
explains, because they were produced by a model with its own tendencies
(topic anchoring, verbosity, phrasing habits) layered on top of the
theta-driven signal. rho_v is the average residual correlation between
items, among machine-authored (A_i = M) cases, after partialling out the
fitted trait signal. It is the empirical target for the "between-item
correlations inflate among machine cases" part of H2.

## The confound this plan isolates

There are two different mechanisms that could produce a nonzero rho_v,
and the simulation grid (lane 4) needs to know which one it's modeling:

  1. Coupling-driven correlation: at partial/high coupling c, the model
     sees the same respondent-level signal (persona sketch or actual
     trait scores) for every item, so its per-item outputs share that
     signal even after the true-theta component is removed -- a
     genuine property of the measurement process being studied.
  2. Session-state artifact: if all of one respondent's item responses
     are generated inside a single LLM call/conversation, the model's
     own generation state (recent tokens, sampled persona drift,
     stylistic momentum) is shared across items regardless of coupling
     level. This would inflate rho_v even at c = 0 and would be an
     artifact of *how the counterparts were generated*, not a property
     of the measurement process itself.

Two experimental arms separate these:

  - same_session: generate all k item responses for one respondent
    inside a single LLM call (one context/conversation), then extract
    per-item scores.
  - independent_calls: generate each item response via its own
    stateless call (fresh context, no memory of the respondent's other
    item responses), varying only the item prompt and the coupling
    condition.

Everything else (model, coupling level c, decoding temperature, seed
policy) is held fixed between arms. rho_v measured in independent_calls
at c = 0 should be ~0 (no shared signal at all, no shared session);
rho_v in same_session at c = 0 that is > 0 is the pure session-state
artifact size, which lane 4's simulation must either avoid (by using
independent_calls for the frozen generation batch) or explicitly model.

## Procedure once counterpart generation exists

1. For each (respondent, coupling level, model family, arm) cell,
   generate k item responses per the schema in `GenerationRecord` below.
2. Score each response into a numeric item indicator x_ij (same scoring
   pipeline used for human responses -- SPEC 1.1's x_i).
3. Fit the trait-signal baseline per item: regress x_ij on the known
   generation-time trait input (persona-band or actual score, per
   coupling level) pooled across respondents. Residual e_ij = x_ij -
   fitted value. (At c = 0 there is no trait input to regress on, so
   e_ij = x_ij - mean(x_.j); rho_v there is just the raw between-item
   correlation.)
4. For each arm, compute the k x k Pearson correlation matrix of
   {e_ij} across respondents, and rho_v = mean of the off-diagonal
   entries (upper triangle).
5. Bootstrap over respondents (resample respondent id with replacement,
   recompute rho_v) for a CI on each arm's rho_v, then report
   rho_v_same_session - rho_v_independent_calls with its own bootstrap
   CI to test whether the session-state artifact is distinguishable
   from zero at the planned sample size.

This module is self-contained and unit-tested against synthetic data
(see `_self_test`) so the pipeline is verified correct before real
generations exist. No generation is run here.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@dataclass
class GenerationRecord:
    """One machine-authored item response. This is the schema the
    (not-yet-run) generation batch must produce for rho_v to be
    computable."""

    respondent_id: str
    item_id: str
    arm: str  # "same_session" | "independent_calls"
    coupling_level: str  # "c0" | "partial" | "high"
    model_family: str  # e.g. "frontier" | "open"
    response_text: str
    score: float | None = None  # filled by the scoring pipeline (x_ij)
    trait_input: float | None = None  # the theta-band or exact score the generator saw, if any


def score_records(records: list[GenerationRecord], scorer) -> None:
    """In-place: fill .score via a scoring callable text -> float."""
    for r in records:
        if r.score is None:
            r.score = scorer(r.response_text)


def _residual_matrix(records: list[GenerationRecord], arm: str) -> tuple[np.ndarray, list[str], list[str]]:
    """Build the respondent x item score matrix for one arm, fit a
    per-item baseline against trait_input (linear regression if any
    trait_input is present, else item mean), and return the residual
    matrix along with the respondent and item id orderings."""
    sub = [r for r in records if r.arm == arm]
    if not sub:
        raise ValueError(f"no records for arm={arm!r}")

    respondents = sorted({r.respondent_id for r in sub})
    items = sorted({r.item_id for r in sub})
    r_index = {r: i for i, r in enumerate(respondents)}
    i_index = {i: j for j, i in enumerate(items)}

    scores = np.full((len(respondents), len(items)), np.nan)
    trait_inputs = np.full((len(respondents), len(items)), np.nan)
    for rec in sub:
        if rec.score is None:
            raise ValueError(f"record {rec.respondent_id}/{rec.item_id} has no score; call score_records first")
        scores[r_index[rec.respondent_id], i_index[rec.item_id]] = rec.score
        if rec.trait_input is not None:
            trait_inputs[r_index[rec.respondent_id], i_index[rec.item_id]] = rec.trait_input

    residuals = np.full_like(scores, np.nan)
    for j, item in enumerate(items):
        y = scores[:, j]
        valid = ~np.isnan(y)
        x = trait_inputs[:, j]
        if np.isnan(x).all():
            # c=0 case: no trait input, baseline is the item mean
            residuals[valid, j] = y[valid] - y[valid].mean()
        else:
            xv = x[valid]
            yv = y[valid]
            ok = ~np.isnan(xv)
            if ok.sum() >= 2 and np.std(xv[ok]) > 0:
                slope, intercept = np.polyfit(xv[ok], yv[ok], 1)
                fitted = intercept + slope * xv
                fitted[~ok] = yv[~ok].mean()
            else:
                fitted = np.full_like(yv, yv.mean())
            residuals[valid, j] = yv - fitted

    return residuals, respondents, items


def compute_rho_v(records: list[GenerationRecord], arm: str) -> float:
    """Mean off-diagonal pairwise Pearson correlation of item residuals, for one arm."""
    residuals, _, items = _residual_matrix(records, arm)
    k = len(items)
    if k < 2:
        raise ValueError("need at least 2 items to compute between-item correlation")

    # pairwise-complete correlation (respondents can have missing items)
    corr = np.full((k, k), np.nan)
    for a in range(k):
        for b in range(k):
            if a == b:
                continue
            xa, xb = residuals[:, a], residuals[:, b]
            valid = ~np.isnan(xa) & ~np.isnan(xb)
            if valid.sum() >= 3 and np.std(xa[valid]) > 0 and np.std(xb[valid]) > 0:
                corr[a, b] = np.corrcoef(xa[valid], xb[valid])[0, 1]

    off_diag = corr[~np.eye(k, dtype=bool)]
    off_diag = off_diag[~np.isnan(off_diag)]
    if len(off_diag) == 0:
        raise ValueError("no valid item pairs to correlate")
    return float(off_diag.mean())


def bootstrap_rho_v(records: list[GenerationRecord], arm: str, n_boot: int = 1000, seed: int = 0) -> dict:
    """Bootstrap over respondents for a CI on rho_v within one arm."""
    sub = [r for r in records if r.arm == arm]
    respondents = sorted({r.respondent_id for r in sub})
    rng = np.random.default_rng(seed)
    by_resp: dict[str, list[GenerationRecord]] = {}
    for r in sub:
        by_resp.setdefault(r.respondent_id, []).append(r)

    point = compute_rho_v(records, arm)
    boots = []
    for _ in range(n_boot):
        sampled_ids = rng.choice(respondents, size=len(respondents), replace=True)
        resampled = []
        for k, rid in enumerate(sampled_ids):
            for rec in by_resp[rid]:
                # relabel respondent_id so resampled duplicates don't collide in the matrix build
                resampled.append(
                    GenerationRecord(
                        respondent_id=f"{rid}__boot{k}",
                        item_id=rec.item_id,
                        arm=rec.arm,
                        coupling_level=rec.coupling_level,
                        model_family=rec.model_family,
                        response_text=rec.response_text,
                        score=rec.score,
                        trait_input=rec.trait_input,
                    )
                )
        try:
            boots.append(compute_rho_v(resampled, arm))
        except ValueError:
            continue

    boots = np.array(boots)
    return {
        "point": point,
        "ci_lo": float(np.percentile(boots, 2.5)),
        "ci_hi": float(np.percentile(boots, 97.5)),
        "n_boot_used": len(boots),
    }


def compare_arms(records: list[GenerationRecord], n_boot: int = 1000, seed: int = 0) -> dict:
    same = bootstrap_rho_v(records, "same_session", n_boot=n_boot, seed=seed)
    indep = bootstrap_rho_v(records, "independent_calls", n_boot=n_boot, seed=seed)
    diff_point = same["point"] - indep["point"]
    return {
        "same_session": same,
        "independent_calls": indep,
        "session_artifact_estimate": diff_point,
        "interpretation": (
            "session_artifact_estimate > 0 and its CI excludes 0 means part of the "
            "between-item correlation in same-session generation is a session-state "
            "artifact, not a coupling-c effect -- the frozen generation batch should "
            "use independent_calls, or lane 4's simulation must model the artifact explicitly."
        ),
    }


# ---------------------------------------------------------------------------
# Self-test on synthetic data (no real generation). Verifies the pipeline is
# correct: constructs data with a KNOWN injected session-state correlation
# and checks compute_rho_v recovers it.
# ---------------------------------------------------------------------------


def _make_synthetic(n_respondents=200, n_items=5, session_extra_corr=0.3, seed=0) -> list[GenerationRecord]:
    rng = np.random.default_rng(seed)
    records: list[GenerationRecord] = []
    for arm, extra in [("independent_calls", 0.0), ("same_session", session_extra_corr)]:
        # shared "session" noise per respondent, added to every item's score in that arm
        session_noise = rng.normal(0, np.sqrt(extra), size=n_respondents) if extra > 0 else np.zeros(n_respondents)
        for i in range(n_respondents):
            rid = f"r{i}"
            for j in range(n_items):
                base = rng.normal(0, 1)
                score = base + session_noise[i]
                records.append(
                    GenerationRecord(
                        respondent_id=rid,
                        item_id=f"item{j}",
                        arm=arm,
                        coupling_level="c0",
                        model_family="synthetic",
                        response_text="<synthetic>",
                        score=float(score),
                        trait_input=None,
                    )
                )
    return records


def _self_test():
    records = _make_synthetic(session_extra_corr=0.4, seed=1)
    result = compare_arms(records, n_boot=300, seed=1)
    print("Self-test (synthetic data, no real generation):")
    print(f"  independent_calls rho_v ~ {result['independent_calls']['point']:.3f} (expect ~0)")
    print(f"  same_session rho_v      ~ {result['same_session']['point']:.3f} (expect > 0, injected artifact)")
    print(f"  session_artifact_estimate = {result['session_artifact_estimate']:.3f}")
    assert abs(result["independent_calls"]["point"]) < 0.15, "independent_calls rho_v should be near 0"
    assert result["same_session"]["point"] > 0.15, "same_session rho_v should show the injected artifact"
    print("Self-test passed.")


if __name__ == "__main__":
    _self_test()
