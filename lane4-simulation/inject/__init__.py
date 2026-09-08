"""Layer B injection: build contaminated samples from REAL machine text, zero generation.

The P1' design (derivations/design-pivot-memo.md section 3.2). Coupling c is not generated,
it is DIALED: a respondent's machine text is drawn from the label-matched pool cell with
probability p and from a reweighted random branch otherwise, giving c(p) = p * c_pool
exactly (E67) with kappa and delta held fixed.

    pools   -- lane 3 ingestion, Pool/PoolText, reference splits, chunk pseudo-items
    assign  -- the p-matched assignment rule and its exact moments
    build   -- bootstrap the human base, inject, emit a CONVENTIONS-conformant Sample
"""

from .assign import (
    AssignmentMoments,
    PoolCapacityError,
    assign_indices,
    assignment_moments,
    capacity_report,
    pool_coupling,
    random_branch_weights,
    raw_pool_coupling,
    realized_coupling,
)
from .build import (
    InjectedSample,
    bootstrap_base,
    build_injected_sample,
    detector_flags,
    exact_mixture_law,
    layer_b_moments,
)
from .pools import (
    Pool,
    PoolContractError,
    PoolText,
    Reference,
    chunk_pseudo_items,
    chunk_text,
    load_measurements,
    load_pool,
    normalize_measurements,
    personallm_label,
    pool_from_rows,
    split_reference,
    synthetic_pool,
    transfer_reference,
)

__all__ = [
    "AssignmentMoments", "InjectedSample", "Pool", "PoolCapacityError", "PoolContractError",
    "PoolText", "Reference", "assign_indices", "assignment_moments", "bootstrap_base",
    "build_injected_sample", "capacity_report", "chunk_pseudo_items", "chunk_text",
    "detector_flags", "exact_mixture_law", "layer_b_moments", "load_measurements", "load_pool",
    "normalize_measurements", "personallm_label", "pool_coupling", "pool_from_rows",
    "random_branch_weights", "raw_pool_coupling", "realized_coupling", "split_reference",
    "synthetic_pool", "transfer_reference",
]
