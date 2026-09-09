"""Labeled machine/human pools for the Layer B assignment-coupled injection design (P1').

Reads lane 3's per-text scores when they land and tolerates their absence: every function
here works on a `Pool` built either from lane 3's files or synthetically, so the assignment
rules and their tests do not wait on lane 3.

Notation follows derivations/design-pivot-memo.md section 3.2 and lane4-simulation/
CONVENTIONS.md. Layer B defines theta := L (the binary persona label), so `label` is the
trait and `score` is the measured trait score of the text.
"""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
LANE3_DIR = REPO_ROOT / "lane3-testbed"
LANE3_MEASUREMENTS = LANE3_DIR / "pool_measurements.json"

# PersonaLLM encodes the five binary persona labels in the file name, e.g.
# extr_agre_cons_emot_clos_p1.txt -> (E high, A high, C high, N low, O low).
# Token order is fixed by the release; the high-pole token maps to label 1.
PERSONALLM_TRAIT_TOKENS: dict[str, tuple[str, str]] = {
    "EXT": ("extr", "intr"),
    "AGR": ("agre", "anta"),
    "CON": ("cons", "unco"),
    "NEU": ("neur", "emot"),  # high pole is neurotic; "emot" = emotionally stable
    "OPE": ("open", "clos"),
}


class PoolContractError(RuntimeError):
    """Lane 3's output is missing or does not match the contract this module codes against."""


@dataclass(frozen=True)
class PoolText:
    """One scored text. `score` is the trait score; `label` is that text's persona label."""

    text_id: str
    label: int  # 0 / 1 on the target trait
    score: float
    detector: float | None = None  # detector score, higher = more machine-like
    chunk_scores: tuple[float, ...] = ()  # per-chunk scores, if lane 3 scored chunks
    n_words: int | None = None
    path: str | None = None


@dataclass
class Pool:
    """A labeled pool of texts on ONE trait, plus whatever lane 3 reported about it."""

    name: str
    trait: str
    texts: list[PoolText]
    kind: str = "machine"  # "machine" | "human"
    generator: str | None = None
    source: str = "synthetic"
    metrics: dict[str, Any] = field(default_factory=dict)  # lane 3's numbers, verbatim

    def __post_init__(self) -> None:
        if not self.texts:
            raise ValueError(f"pool {self.name!r} has no texts")
        bad = {t.label for t in self.texts} - {0, 1}
        if bad:
            raise ValueError(f"pool {self.name!r} has non-binary labels {sorted(bad)}")

    # ---- vectors -------------------------------------------------------------------
    @property
    def labels(self) -> np.ndarray:
        return np.array([t.label for t in self.texts], dtype=np.int64)

    @property
    def scores(self) -> np.ndarray:
        return np.array([t.score for t in self.texts], dtype=float)

    @property
    def detector(self) -> np.ndarray:
        vals = [np.nan if t.detector is None else t.detector for t in self.texts]
        return np.array(vals, dtype=float)

    def __len__(self) -> int:
        return len(self.texts)

    # ---- label structure -----------------------------------------------------------
    @property
    def cell_counts(self) -> tuple[int, int]:
        lab = self.labels
        return int(np.sum(lab == 0)), int(np.sum(lab == 1))

    @property
    def balance(self) -> float:
        """Fraction of texts with label 1. Prop. 16 as written assumes this is 0.5 (Q12)."""
        return float(np.mean(self.labels))

    def is_balanced(self, tol: float = 0.02) -> bool:
        return abs(self.balance - 0.5) <= tol

    def indices_by_label(self) -> dict[int, np.ndarray]:
        lab = self.labels
        return {l: np.flatnonzero(lab == l) for l in (0, 1)}

    def subset(self, idx: Sequence[int], name: str | None = None) -> "Pool":
        return Pool(
            name=name or f"{self.name}[{len(idx)}]",
            trait=self.trait,
            texts=[self.texts[i] for i in idx],
            kind=self.kind,
            generator=self.generator,
            source=self.source,
            metrics=dict(self.metrics),
        )

    def standardized(self, mu: float, sd: float, name: str | None = None) -> "Pool":
        """Rescale every score by a HUMAN-BASE (mu, sd). See INJECT.md 'Normalization'."""
        if sd <= 0:
            raise ValueError("sd must be positive")
        texts = [
            PoolText(
                text_id=t.text_id,
                label=t.label,
                score=(t.score - mu) / sd,
                detector=t.detector,
                chunk_scores=tuple((cs - mu) / sd for cs in t.chunk_scores),
                n_words=t.n_words,
                path=t.path,
            )
            for t in self.texts
        ]
        return Pool(name or self.name, self.trait, texts, self.kind, self.generator,
                    self.source, dict(self.metrics))


# ------------------------------------------------------------------- lane 3 ingestion
def _first(d: dict, *keys: str, default: Any = None) -> Any:
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return default


def normalize_measurements(raw: Any) -> dict[str, dict[str, Any]]:
    """Accept the plausible shapes of lane 3's pool_measurements.json.

    Expected (documented in INJECT.md); anything close is accepted, anything else raises
    with the keys actually seen so the mismatch is one edit to fix, not a debugging session.
    """
    if isinstance(raw, dict) and "pools" in raw:
        pools = raw["pools"]
    elif isinstance(raw, dict):
        pools = raw
    elif isinstance(raw, list):
        pools = raw
    else:
        raise PoolContractError(f"top level is {type(raw).__name__}, expected dict or list")

    if isinstance(pools, list):
        items = []
        for entry in pools:
            if not isinstance(entry, dict):
                raise PoolContractError(f"pool entry is {type(entry).__name__}, expected dict")
            name = _first(entry, "name", "pool", "pool_name")
            if name is None:
                raise PoolContractError(f"pool entry has no name; keys={sorted(entry)}")
            items.append((str(name), entry))
    else:
        items = [(str(k), v) for k, v in pools.items() if isinstance(v, dict)]
    if not items:
        raise PoolContractError(
            "no pool entries found; top-level keys seen: "
            f"{sorted(pools) if isinstance(pools, dict) else type(pools).__name__}. "
            "Expected {'pools': {<pool name>: {'traits': {<TRAIT>: {...}}}}} -- see "
            "INJECT.md 'The pool_measurements.json contract'.")

    out: dict[str, dict[str, Any]] = {}
    for name, entry in items:
        traits = _first(entry, "traits", "by_trait", "per_trait", default=None)
        if traits is None:  # flat single-trait entry
            trait = _first(entry, "trait", default="UNKNOWN")
            traits = {str(trait): entry}
        if not isinstance(traits, dict):
            raise PoolContractError(f"pool {name!r}: 'traits' is {type(traits).__name__}")
        out[name] = {
            "name": name,
            "kind": _first(entry, "kind", "class", default="machine"),
            "generator": _first(entry, "generator", "model", default=None),
            "n_texts": _first(entry, "n_texts", "n", default=None),
            "scores_path": _first(entry, "scores_path", "scores_file", "per_text_scores",
                                  "per_text_path", default=None),
            "traits": {
                str(t): {
                    "g": _first(m, "g", "g_hat"),
                    "c_hat": _first(m, "c_hat", "c", "c_pool"),
                    "kappa": _first(m, "kappa"),
                    "delta": _first(m, "delta"),
                    "auc": _first(m, "auc", "detector_auc", "AUC"),
                    "r_H": _first(m, "r_H", "r_h", "rH"),
                    "scores_path": _first(m, "scores_path", "scores_file", default=None),
                }
                for t, m in traits.items()
                if isinstance(m, dict)
            },
        }
    return out


def load_measurements(path: Path | str | None = None) -> dict[str, dict[str, Any]]:
    """Read lane 3's pool_measurements.json. Raises PoolContractError if it has not landed."""
    p = Path(path) if path is not None else LANE3_MEASUREMENTS
    if not p.exists():
        raise PoolContractError(
            f"lane 3 measurements not found at {p}. This is expected until lane 3 step 1 "
            "lands (design-pivot-memo 8.2 step 1). Everything in inject/ except "
            "load_pool() runs on synthetic pools in the meantime; see INJECT.md."
        )
    try:
        raw = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        raise PoolContractError(f"{p} is not valid JSON: {e}") from e
    return normalize_measurements(raw)


def _read_rows(path: Path) -> list[dict[str, str]]:
    if path.suffix == ".json":
        raw = json.loads(path.read_text())
        rows = raw["rows"] if isinstance(raw, dict) and "rows" in raw else raw
        if not isinstance(rows, list):
            raise PoolContractError(f"{path}: expected a list of per-text rows")
        return [{str(k): ("" if v is None else str(v)) for k, v in r.items()} for r in rows]
    if path.suffix == ".jsonl":
        return [
            {str(k): ("" if v is None else str(v)) for k, v in json.loads(line).items()}
            for line in path.read_text().splitlines()
            if line.strip()
        ]
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _pick(row: dict[str, str], *names: str) -> str | None:
    lower = {k.lower(): k for k in row}
    for n in names:
        k = lower.get(n.lower())
        if k is not None and row[k] != "":
            return row[k]
    return None


def personallm_label(text_id: str, trait: str) -> int:
    """Persona label from a PersonaLLM file name. Raises if the trait token is absent."""
    try:
        hi, lo = PERSONALLM_TRAIT_TOKENS[trait]
    except KeyError:
        raise ValueError(f"unknown trait {trait!r}; known: {sorted(PERSONALLM_TRAIT_TOKENS)}")
    tokens = set(Path(text_id).stem.split("_"))
    if hi in tokens:
        return 1
    if lo in tokens:
        return 0
    raise PoolContractError(
        f"{text_id!r} carries neither {hi!r} nor {lo!r}; not a PersonaLLM file name"
    )


def pool_from_rows(
    rows: Iterable[dict[str, str]],
    name: str,
    trait: str,
    kind: str = "machine",
    generator: str | None = None,
    source: str = "lane3",
    metrics: dict[str, Any] | None = None,
    label_from_filename: bool = False,
) -> Pool:
    """Build a Pool from per-text score rows, tolerating lane 3's column naming."""
    texts: list[PoolText] = []
    for i, row in enumerate(rows):
        tid = _pick(row, "text_id", "id", "file", "filename", "path", "name")
        if tid is None:
            raise PoolContractError(f"row {i}: no text id column; columns={sorted(row)}")
        raw_score = _pick(row, f"score_{trait}", f"{trait}_score", trait, "score", "x")
        if raw_score is None:
            raise PoolContractError(
                f"row {i}: no score column for trait {trait!r}; columns={sorted(row)}"
            )
        if label_from_filename:
            label = personallm_label(tid, trait)
        else:
            raw_label = _pick(row, f"label_{trait}", f"{trait}_label", "label", "L")
            if raw_label is None:
                raise PoolContractError(
                    f"row {i}: no label column for trait {trait!r}; columns={sorted(row)}"
                )
            label = int(float(raw_label))
        det = _pick(row, "detector", "detector_score", "roberta", "p_machine")
        words = _pick(row, "n_words", "words", "word_count")
        chunks: list[float] = []
        j = 1
        while (cv := _pick(row, f"chunk_{j}", f"chunk{j}", f"chunk_{j}_{trait}")) is not None:
            chunks.append(float(cv))
            j += 1
        texts.append(
            PoolText(
                text_id=str(tid),
                label=label,
                score=float(raw_score),
                detector=None if det is None else float(det),
                chunk_scores=tuple(chunks),
                n_words=None if words is None else int(float(words)),
                path=_pick(row, "path", "file", "filename"),
            )
        )
    return Pool(name, trait, texts, kind, generator, source, metrics or {})


def load_pool(
    name: str,
    trait: str,
    measurements: dict[str, dict[str, Any]] | None = None,
    root: Path | None = None,
) -> Pool:
    """Load one labeled pool for one trait from lane 3's saved per-text scores."""
    meas = measurements if measurements is not None else load_measurements()
    if name not in meas:
        raise PoolContractError(f"pool {name!r} not in measurements; have {sorted(meas)}")
    entry = meas[name]
    tmetrics = entry["traits"].get(trait)
    if tmetrics is None:
        raise PoolContractError(
            f"pool {name!r} has no trait {trait!r}; have {sorted(entry['traits'])}"
        )
    rel = tmetrics.get("scores_path") or entry.get("scores_path")
    if rel is None:
        raise PoolContractError(
            f"pool {name!r} trait {trait!r}: no per-text scores path. The injection module "
            "needs per-text scores, not just pool summaries (lane 3 brief, step 1)."
        )
    base = root if root is not None else LANE3_DIR
    path = Path(rel)
    if not path.is_absolute():
        path = base / path
    if not path.exists():
        raise PoolContractError(f"pool {name!r}: per-text scores not found at {path}")
    rows = _read_rows(path)
    label_from_filename = not any(
        _pick(r, f"label_{trait}", f"{trait}_label", "label", "L") is not None for r in rows[:1]
    )
    return pool_from_rows(
        rows, name=name, trait=trait, kind=str(entry.get("kind") or "machine"),
        generator=entry.get("generator"), source=f"lane3:{path}",
        metrics=tmetrics, label_from_filename=label_from_filename,
    )


# ------------------------------------------------------------------- synthetic pools
def synthetic_pool(
    rng: np.random.Generator,
    n: int,
    c_pool: float,
    name: str = "synthetic",
    trait: str = "EXT",
    balance: float = 0.5,
    mean: float = 0.0,
    sd: float = 1.0,
    kind: str = "machine",
) -> Pool:
    """A labeled pool with a known population coupling, for tests and for the E67 proof.

    Scores are drawn so that the REALIZED (finite-pool) coupling is close to `c_pool`; the
    exact realized value is whatever `assignment_moments` computes from the finite pool, and
    that -- not the target -- is what E67 is checked against.
    """
    if not 0 < balance < 1:
        raise ValueError("balance must be in (0, 1)")
    n1 = int(round(n * balance))
    labels = np.zeros(n, dtype=np.int64)
    labels[:n1] = 1
    rng.shuffle(labels)
    sd_l = np.sqrt(balance * (1 - balance))
    lstar = (labels - balance) / sd_l  # standardized label, Var = 1
    resid = rng.standard_normal(n)
    resid = (resid - resid.mean()) / resid.std()
    scores = mean + sd * (c_pool * lstar + np.sqrt(max(1.0 - c_pool**2, 0.0)) * resid)
    texts = [
        PoolText(text_id=f"{name}_{i:05d}", label=int(labels[i]), score=float(scores[i]))
        for i in range(n)
    ]
    return Pool(name, trait, texts, kind=kind, source="synthetic")


# ------------------------------------------------------------------- reference splits
@dataclass(frozen=True)
class Reference:
    """A machine reference distribution for the SPEC 3.2 label-free prevalence estimator."""

    name: str
    kind: str  # "held_out" | "transfer"
    scores: np.ndarray
    provenance: str
    text_ids: tuple[str, ...] = ()  # so disjointness from the injection pool is checkable

    def __len__(self) -> int:
        return int(self.scores.size)


def split_reference(
    pool: Pool, rng: np.random.Generator, frac: float = 0.5, stratify: bool = True
) -> tuple[Pool, Reference]:
    """Disjoint split: texts for injection, texts for the 3.2 reference.

    SPEC 3.2 generates its reference on demand; with no generation the reference is a
    held-out split of the injected pool. The split is what removes the circularity, so the
    two index sets are disjoint by construction and that is asserted here, not assumed.
    """
    if not 0 < frac < 1:
        raise ValueError("frac must be in (0, 1)")
    n = len(pool)
    if stratify:
        keep: list[int] = []
        for _, idx in sorted(pool.indices_by_label().items()):
            perm = rng.permutation(idx)
            keep.extend(perm[: int(round(len(perm) * frac))].tolist())
        keep_idx = np.array(sorted(keep), dtype=int)
    else:
        perm = rng.permutation(n)
        keep_idx = np.array(sorted(perm[: int(round(n * frac))].tolist()), dtype=int)
    ref_idx = np.array(sorted(set(range(n)) - set(keep_idx.tolist())), dtype=int)
    if keep_idx.size == 0 or ref_idx.size == 0:
        raise ValueError(f"split left an empty side: {keep_idx.size} / {ref_idx.size}")
    inject = pool.subset(keep_idx, name=f"{pool.name}:inject")
    reference = Reference(
        name=f"{pool.name}:reference",
        kind="held_out",
        scores=pool.subset(ref_idx).scores,
        provenance=f"held-out {ref_idx.size}/{n} of {pool.name} (disjoint from injection)",
        text_ids=tuple(pool.texts[i].text_id for i in ref_idx),
    )
    return inject, reference


# ------------------------------------------------------------------ frozen calibration split
# LAYERB-ROUND3.md 1.2: 54% of the variance in the per-cell EIV error is the calibration split
# draw, not the cell. 2.3: with the split re-drawn between waves the between-wave change
# detector picks up an additive noise floor of 0.06-0.27 and dies for weak-detector pools;
# with it frozen the same change carries an 18-40% relative error and the sign is never at
# risk. The operational rule is therefore: draw the split once, reuse it at every wave.
#
# The mechanism is the seed, not the arithmetic. A per-cell `default_rng(cell_seed)` with
# `cell_seed = base + 1000 * cell_index` (what the sweeps used) makes the split a function of
# a cell's POSITION in a loop: insert a pool and every later cell's reference moves, and two
# scripts with different bases give the same cell different references. Keying the stream on
# the pool's identity instead makes the split a function of the pool alone, so it is stable
# across waves, across cell orderings, and across scripts.
CALIBRATION_SEED = 20260908
"""Frozen master seed for the wave-invariant calibration split. Changing it re-draws every
reference in the pipeline and breaks comparability with every recorded `split_id`."""


def calibration_stream(pool: Pool, seed: int = CALIBRATION_SEED) -> np.random.Generator:
    """The RNG for `pool`'s calibration split: a function of (seed, pool.name) and nothing else.

    Not the cell index, not the wave, not the rep. Two waves months apart, or two scripts with
    unrelated seed bases, land on the identical held-out halves.
    """
    key = int.from_bytes(hashlib.blake2s(pool.name.encode("utf-8"), digest_size=8).digest(), "big")
    return np.random.default_rng([int(seed), key])


def calibration_split(
    pool: Pool, frac: float = 0.5, stratify: bool = True, seed: int = CALIBRATION_SEED
) -> tuple[Pool, Reference]:
    """`split_reference` on the frozen stream: the same pool always yields the same reference.

    Use this everywhere a calibration/reference split feeds an estimate. `split_reference` with
    a caller-supplied rng remains the right call only when varying the split IS the experiment
    (round3_splits.py), which is why that path is left alone.
    """
    return split_reference(pool, calibration_stream(pool, seed), frac=frac, stratify=stratify)


def split_id(*refs: Reference) -> str:
    """Content hash of the held-out ids: the split's identity, recoverable from the output.

    Derived from what was actually held out rather than from the seed, so a run recorded under
    a different seed scheme is still comparable -- equal ids mean the same texts, whatever
    produced them.
    """
    h = hashlib.blake2s(digest_size=8)
    for ref in refs:
        h.update(ref.name.encode("utf-8"))
        h.update(b"\x00")
        for tid in sorted(ref.text_ids):
            h.update(tid.encode("utf-8"))
            h.update(b"\x00")
        h.update(b"\x01")
    return h.hexdigest()


def reference_detector(pool: Pool, ref: Reference) -> np.ndarray:
    """Detector scores for a held-out Reference, looked up by text id against `pool`.

    A Reference carries the trait scores and the ids, not the detector column -- SPEC 3.2's
    distribution-match branch needs only the scores. The adjusted_count branch needs the
    detector on the HUMAN reference (for sp) and the machine reference (for se), which is
    what this returns. Raises rather than filling NaN if the reference is not from `pool`.
    """
    by_id = {t.text_id: t.detector for t in pool.texts}
    missing = [i for i in ref.text_ids if i not in by_id]
    if missing:
        raise PoolContractError(
            f"reference {ref.name!r} has {len(missing)} ids not in pool {pool.name!r} "
            f"(first: {missing[0]!r}); it was not split from this pool"
        )
    return np.array([by_id[i] for i in ref.text_ids], dtype=float)


def transfer_reference(pool: Pool, injected_from: Pool) -> Reference:
    """A reference from a DIFFERENT pool (the realistic case; free from the multi-pool corpora)."""
    if pool.name == injected_from.name:
        raise ValueError(
            f"transfer reference must differ from the injected pool (both {pool.name!r}); "
            "use split_reference for the held-out case"
        )
    return Reference(
        name=f"{pool.name}:transfer",
        kind="transfer",
        scores=pool.scores,
        provenance=f"transfer: reference={pool.name}, injected={injected_from.name}",
        text_ids=tuple(t.text_id for t in pool.texts),
    )


# ------------------------------------------------------------------ chunk pseudo-items
def chunk_text(text: str, k: int) -> list[str]:
    """Split into k contiguous chunks of near-equal word count, losing no words.

    The weak-H2 rescue (memo 3.4): between-chunk correlation is the within-text
    consistency form of the homogenization signature, not the same-session form.
    """
    if k < 1:
        raise ValueError("k must be >= 1")
    words = text.split()
    if len(words) < k:
        raise ValueError(f"text has {len(words)} words, cannot make {k} chunks")
    bounds = np.linspace(0, len(words), k + 1).round().astype(int)
    return [" ".join(words[bounds[j]:bounds[j + 1]]) for j in range(k)]


def chunk_pseudo_items(
    texts: Sequence[str], k: int, scorer: Callable[[Sequence[str]], np.ndarray]
) -> np.ndarray:
    """Score k chunks per text -> (len(texts), k) pseudo-item matrix.

    `scorer` is injected because the fitted trait model lives in lane 3, not here. Lane 3's
    step-1 brief does not include chunk-level scoring: see INJECT.md 'Open dependency'.
    """
    chunks: list[str] = []
    for t in texts:
        chunks.extend(chunk_text(t, k))
    scores = np.asarray(scorer(chunks), dtype=float)
    if scores.shape != (len(texts) * k,):
        raise ValueError(f"scorer returned {scores.shape}, expected {(len(texts) * k,)}")
    return scores.reshape(len(texts), k)


# ------------------------------------------- lane 3 as it actually shipped (2026-09-07)
# The schema above (`pools -> traits -> scores_path`, row-shaped score files) is the one
# this module was written against BEFORE lane 3 landed. What lane 3 actually shipped is
# different in three ways, so the real reader lives here rather than contorting the one
# above: top-level `pk_human` / `labeled_pools` / `unlabeled_pools` instead of `pools`;
# traits keyed `cEXT` not `EXT`; and score files that are column-shaped dicts of parallel
# lists, not rows. INJECT.md section 8 documents both and says which is live.
# Lane 3 keys traits cEXT / cNEU / cAGR / cCON / cOPN. Note cOPN, not cOPE: the openness
# key does NOT follow the c + PERSONALLM_TRAIT_TOKENS pattern, so the map is written out
# rather than derived. Both spellings and the bare lane-3 key resolve.
LANE3_TRAIT_KEY = {
    "EXT": "cEXT", "NEU": "cNEU", "AGR": "cAGR", "CON": "cCON",
    "OPE": "cOPN", "OPN": "cOPN",
}
LANE3_TRAITS: tuple[str, ...] = ("EXT", "NEU", "AGR", "CON", "OPE")


def lane3_trait_key(trait: str, available: Iterable[str] = ()) -> str:
    """Resolve a trait name to lane 3's key, accepting 'EXT', 'OPN', 'cOPN', ..."""
    if trait in LANE3_TRAIT_KEY:
        return LANE3_TRAIT_KEY[trait]
    avail = set(available)
    if trait in avail:
        return trait
    raise PoolContractError(
        f"unknown trait {trait!r}; known {sorted(LANE3_TRAIT_KEY)}"
        + (f", file has {sorted(avail)}" if avail else "")
    )


def load_lane3(path: Path | str | None = None) -> dict[str, Any]:
    """Lane 3's pool_measurements.json, verbatim."""
    p = Path(path) if path is not None else LANE3_MEASUREMENTS
    if not p.exists():
        raise PoolContractError(f"lane 3 measurements not found at {p}")
    with p.open() as fh:
        return json.load(fh)


def lane3_scores_path(
    name: str, raw: dict[str, Any] | None = None, root: Path | None = None
) -> Path:
    """Resolve `score_files[name]`. Lane 3 files these paths RELATIVE to lane3-testbed/."""
    raw = load_lane3() if raw is None else raw
    files = raw.get("score_files", {})
    if name not in files:
        raise PoolContractError(f"pool {name!r} not in score_files; have {sorted(files)}")
    path = Path(files[name])
    if not path.is_absolute():
        path = (root if root is not None else LANE3_DIR) / path
    if not path.exists():
        raise PoolContractError(f"pool {name!r}: per-text scores not found at {path}")
    return path


SCORE_VERSIONS = ("oof", "insample")
"""Which lane-3 scoring columns a Pool reads.

"oof"      chunk_1_oof..chunk_k_oof. On pk_human each chunk is scored by the fold model that
           excluded its parent text, so the chunk score carries no information about its own
           text's label. This is the confirmatory version and the default.
"insample" chunk_1..chunk_k, the historical columns. On pk_human the chunk scorer saw the
           parent text, so any chunk-consuming quantity (rel_hat, the k>1 loading, every
           rho_T-scale number) is inflated by leakage. Kept only to reproduce runs made
           before 2026-09-09; a confirmatory run must not use it.

Whole-text scores are NOT switched by this flag, because no leaky whole-text column exists:
pk_human ships `cross_fitted_scores` (5-fold OOF) and the machine pools ship `trait_scores`
from a full-PK refit whose training set never contained their texts. `lane3_pool` records
which column it read in `Pool.metrics["whole_text_scoring"]` so the provenance is explicit
rather than assumed.
"""


def _chunk_meta(blob: dict[str, Any], suffix: str) -> dict[str, Any]:
    """The chunk_meta block for this scoring version, falling back to the unsuffixed one."""
    return blob.get(f"chunk_meta{suffix}") or blob.get("chunk_meta") or {}


def _lane3_chunks(
    blob: dict[str, Any], tkey: str, n: int, score_version: str = "oof"
) -> tuple[list[tuple[float, ...]], int]:
    """Per-text chunk scores for ONE trait out of lane 3's chunk columns.

    Each column is a list aligned to `ids` whose entries are either null (the text had
    too few sentences to split into k non-trivial chunks -- lane 3 skips rather than pads)
    or a dict of that chunk's five trait scores. A text is chunked only if EVERY chunk is
    present; otherwise it gets an empty tuple, which is what `build._chunks_or_none` reads
    to refuse a k > 1 run rather than silently short a row.

    `score_version` selects `chunk_j_oof` ("oof") or `chunk_j` ("insample"); see
    SCORE_VERSIONS. Lane 3's pass-3 review finding B3 is that reading the in-sample columns
    makes every chunk-consuming quantity non-confirmatory.
    """
    if score_version not in SCORE_VERSIONS:
        raise PoolContractError(f"score_version must be one of {SCORE_VERSIONS}, got {score_version!r}")
    suffix = "_oof" if score_version == "oof" else ""
    meta = _chunk_meta(blob, suffix)
    k = int(meta.get("k", 0)) or sum(1 for j in range(1, 65) if f"chunk_{j}{suffix}" in blob)
    if k <= 1:
        return [() for _ in range(n)], 0
    cols = []
    for j in range(1, k + 1):
        col = blob.get(f"chunk_{j}{suffix}")
        if col is None:
            raise PoolContractError(
                f"chunk_meta says k={k} but chunk_{j}{suffix} is missing (score_version="
                f"{score_version!r}); have {sorted(c for c in blob if c.startswith('chunk_'))}"
            )
        if len(col) != n:
            raise PoolContractError(f"chunk_{j}{suffix} has {len(col)} entries, ids has {n}")
        cols.append(col)
    out: list[tuple[float, ...]] = []
    n_missing = 0
    for i in range(n):
        vals = []
        for col in cols:
            cell = col[i]
            v = None if cell is None else cell.get(tkey)
            if v is None:
                vals = []
                break
            vals.append(float(v))
        if not vals:
            n_missing += 1
        out.append(tuple(vals))
    return out, n_missing


def lane3_pool(
    name: str,
    trait: str,
    raw: dict[str, Any] | None = None,
    root: Path | None = None,
    chunks: bool = True,
    score_version: str = "oof",
    allow_insample: bool = False,
) -> Pool:
    """Build a Pool from lane 3's per-text score file. `name` is a key of `score_files`.

    Lane 3 ships ONE file per pool holding all five traits as dict-of-arrays, with no
    `scores_path` in pool_measurements.json, so this reads `score_files[name]` and slices
    the requested trait out. It does not go through `_read_rows` / `pool_from_rows`, which
    parse the row-shaped files the pre-lane-3 contract assumed.

    `score_version` defaults to "oof" (SCORE_VERSIONS). Passing "insample" additionally
    requires `allow_insample=True`: the leaky columns are reachable only by a caller that
    says in writing it is reproducing a pre-2026-09-09 run, never by a default or a typo.
    """
    if score_version not in SCORE_VERSIONS:
        raise PoolContractError(f"score_version must be one of {SCORE_VERSIONS}, got {score_version!r}")
    if score_version == "insample" and not allow_insample:
        raise PoolContractError(
            "score_version='insample' reads lane 3's leaky chunk columns (pass-3 review finding "
            "B3: on pk_human the chunk scorer saw the parent text). A confirmatory run must use "
            "'oof'. Pass allow_insample=True only to reproduce a run made before 2026-09-09."
        )
    raw = load_lane3() if raw is None else raw
    path = lane3_scores_path(name, raw, root)
    with path.open() as fh:
        blob = json.load(fh)

    if name == "pk_human":
        kind, entry = "human", raw.get("pk_human", {})
    else:
        kind = "machine"
        entry = (raw.get("labeled_pools", {}).get(name)
                 or raw.get("unlabeled_pools", {}).get(name, {}))
    scores_key = "cross_fitted_scores" if "cross_fitted_scores" in blob else "trait_scores"
    if scores_key not in blob:
        raise PoolContractError(
            f"pool {name!r}: no cross_fitted_scores or trait_scores; have {sorted(blob)}"
        )
    tkey = lane3_trait_key(trait, blob[scores_key])
    if tkey not in blob[scores_key]:
        raise PoolContractError(
            f"pool {name!r}: no trait {tkey!r} in {scores_key}; have {sorted(blob[scores_key])}"
        )
    scores = blob[scores_key][tkey]
    labels = (blob.get("labels") or {}).get(tkey)
    if labels is None:
        raise PoolContractError(
            f"pool {name!r} is unlabeled on {tkey!r}; Layer B needs a per-text label "
            "(theta := L). Unlabeled pools carry kappa and delta only."
        )
    det = blob.get("detector_p_machine")
    ids = blob.get("ids") or [f"{name}:{i}" for i in range(len(scores))]
    if not len(ids) == len(scores) == len(labels):
        raise PoolContractError(
            f"pool {name!r}: ragged columns ids={len(ids)} scores={len(scores)} "
            f"labels={len(labels)}"
        )
    if det is not None and len(det) != len(ids):
        raise PoolContractError(
            f"pool {name!r}: detector_p_machine has {len(det)} entries, ids has {len(ids)}"
        )
    n = len(scores)
    chunk_rows, n_unchunked = (
        _lane3_chunks(blob, tkey, n, score_version) if chunks else ([() for _ in range(n)], 0)
    )
    texts = [
        PoolText(
            text_id=str(ids[i]),
            label=int(round(float(labels[i]))),
            score=float(scores[i]),
            detector=None if det is None else float(det[i]),
            chunk_scores=chunk_rows[i],
        )
        for i in range(n)
    ]
    if kind == "machine":
        metrics = dict((entry.get("trait_stats") or {}).get(tkey, {}))
    else:
        # pk_human reports r_H as {"r": ..., "p": ...}; flatten to the scalar the design uses.
        metrics = {}
        for key in ("r_H", "mu_H", "V_H"):
            v = (entry.get(key) or {}).get(tkey)
            metrics[key] = v.get("r", v.get("value")) if isinstance(v, dict) else v
    metrics["lane3_trait_key"] = tkey
    metrics["n_unchunked"] = n_unchunked
    suffix = "_oof" if score_version == "oof" else ""
    metrics["k_chunks_available"] = int(_chunk_meta(blob, suffix).get("k", 0))
    metrics["has_detector"] = det is not None
    # Provenance, so a downstream manifest never has to guess which scoring it consumed.
    metrics["score_version"] = score_version
    metrics["chunk_scoring"] = _chunk_meta(blob, suffix).get(
        "scoring_rule", "chunk_meta carries no scoring_rule (pre-refit file)")
    metrics["whole_text_scoring"] = (
        "pk_human cross_fitted_scores: 5-fold OOF" if scores_key == "cross_fitted_scores"
        else "trait_scores: full-PK refit; this pool's texts were never in the training set")
    return Pool(
        name=name, trait=trait, texts=texts, kind=kind,
        generator=None if kind == "human" else name,
        source=f"lane3:{path}", metrics=metrics,
    )


def lane3_labeled_pools(raw: dict[str, Any] | None = None) -> list[str]:
    """The labeled pool names, in lane 3's order."""
    raw = load_lane3() if raw is None else raw
    return list(raw.get("labeled_pools", {}))
