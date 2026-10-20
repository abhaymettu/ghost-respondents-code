# Ghost respondents

Replication material for *Ghost respondents: a boundary map for covert AI authorship in
open-ended survey data* (working paper). The paper is
[`paper/GHOST-RESPONDENTS-DRAFT.md`](paper/GHOST-RESPONDENTS-DRAFT.md).

The study asks what happens to a validity coefficient when some fraction of open-ended survey
responses were written by a language model, and whether any label-free correction recovers the
human coefficient. The answer on this testbed is that none of the four tested corrections
beats doing nothing, and section 6 says where that conclusion does and does not apply.

## Paper section to file

| paper section | what it reports | files |
|---|---|---|
| 2. The mixture model | closed forms for the contamination bias and the survivor sample | `derivations/lane1-zero-coupling.md`, `derivations/lane1-partial-coupling.md`; the same forms as code in `lane4-simulation/population.py` |
| 3. Estimators | naive, delete, simex, labelfree, em, bounds_c | `lane4-simulation/estimators.py`, tests in `lane4-simulation/test_estimators.py` |
| 4.1 Layer A design | parametric Monte Carlo, 372 cells | `lane4-simulation/grid.py`, `lane4-simulation/GRID-CONFIG.md` |
| 4.2 Layer B design | real essays, real machine pools, injection | `lane3-testbed/` (corpora, scoring, detector), `lane4-simulation/inject/`, `lane4-simulation/INJECT.md` |
| 4.2 Table 1, detector | realized operating points | `lane3-testbed/detector/`, `lane3-testbed/CALIBRATION-REPORT.md` |
| 4.3 Thresholds | T1 to T4 as written | `SPEC.md` section 4.4 |
| 5.1 Layer A results | the algebra check and the Layer A thresholds | `lane4-simulation/results/grid/grid.jsonl`, `lane4-simulation/pass2-numerical-check.md` |
| 5.2 to 5.4 Layer B results | contamination map, four thresholds, resolvability map | `lane4-simulation/results/layerb-grid/grid.jsonl`, `lane4-simulation/LAYERB-GRID.md` |
| 5.4 the sensitivity band | `bounds_c` across all Layer A cells | `lane4-simulation/results/grid-bounds-c/grid.jsonl`, `lane4-simulation/ESTIMATOR-FIX-REPORT.md` |
| 5.5 500-replication slice | the same 280 cells at five times the replications | `lane4-simulation/results/layerb-grid-500rep/grid.jsonl` |
| 5.6 r_F | the detector score against the trait labels, and surface proxies | `lane3-testbed/analysis/detector_r_f.py` (anchor), `lane3-testbed/analysis/fluency_anchor.py` (proxies) |
| 5.7 follow-on arms | robust estimators, trait-independent detection | `lane4-simulation/ROBUST-ARM.md`, `lane4-simulation/WATERMARK.md`, `lane4-simulation/results/robust-arm/`, `lane4-simulation/results/watermark/` |
| 8. Reproducibility appendix | environment, seeds, artifacts of record, verification passes | this README plus `lane4-simulation/GRID-CONFIG.md` and `derivations/pass1-diff-report.md`, `derivations/pass3-methods-review.md`, `lane3-testbed/PASS3-FIXES.md` |

Every table and figure in the paper is generated, not typed. `paper/README.md` gives the
regeneration commands and the read-only inputs they use.

## Layout

```
paper/            the draft, its generated tables and figures, and the scripts that write them
derivations/      the closed-form derivations and the three verification passes
lane2-novelty/    the novelty check against the closest prior work
lane3-testbed/    corpora, out-of-fold scoring, detector calibration, pool measurement
lane4-simulation/ the simulation engine, the estimators, and the saved grids
docs/             the follow-up experiment designs and the literature scan
SPEC.md           the analysis plan the thresholds and design come from
```

`SPEC.md` is a repository file frozen at commit `db7c171`. It is an analysis plan, not an
external pre-registration; the paper says so wherever it cites it.

The history was rewritten once, on 2026-10-20, to take the third-party corpora out of it, so
every commit hash changed. The paper and notes cite the old hashes; `docs/commit-map.tsv` maps
each old hash to its new one. `db7c171` is now `13b7a21` (tag `spec-frozen`), and `SPEC.md` is
byte-identical at both.

## Reproducing

The grids are saved, so nothing here needs to be re-run to check the paper. To regenerate the
tables, figures, and the number check from the saved grids:

```
lane4-simulation/.venv/bin/python paper/scripts/make_tables.py
cd lane4-simulation && uv run --python .venv/bin/python --with matplotlib python ../paper/scripts/make_figures.py && cd ..
lane4-simulation/.venv/bin/python paper/scripts/check_numbers.py
```

Environment: Python 3.12.13, numpy 2.5.3, scipy 1.18.1, scikit-learn 1.9.0, macOS arm64.
Re-running the grids themselves is an overnight job on 10 workers; `lane4-simulation/README.md`
has the runner commands and costs.

## Data

The Pennebaker-King essays and the PersonaLLM pools are third-party corpora under their own
terms; `lane3-testbed/TESTBED-REPORT.md` records provenance and what is and is not
redistributable here. The essay labels are binary median splits, which is the form the
available mirror carries.

The corpora are downloaded, not committed. `lane3-testbed/data/` is ignored by git; fetch the
corpora into it with

```
python3 scripts/download_data.py
```

The script uses only the standard library and lists each source and its licence at the top.
`data/scores/` and `data/models/` are derived outputs; `lane3-testbed/pool_measurement.py` and
`lane3-testbed/pk_human_detector_scores.py` regenerate them from the downloaded corpora.

## Release tree

The published tree is what `git archive` produces. Development material that the paper does
not cite (lane prompts, run logs, working boards, day-by-day review notes, and the halted
in-sample grid) is marked `export-ignore` in `.gitattributes` and excluded from it:

```
git archive --format=tar --prefix=ghost-respondents/ HEAD | tar -x -C /tmp
```

Check that tree against this README before publishing.

## Generative AI use

This study was built and written with large language models, including the derivations, the
code, and the manuscript. The paper's Reproducibility appendix states this in full and names
the verification passes. The author is responsible for the content.
