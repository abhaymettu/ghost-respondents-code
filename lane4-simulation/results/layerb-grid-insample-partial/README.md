SUPERSEDED. In-sample chunk scores, halted 176/336 cells.

Orchestrator decision D1 (2026-09-09 06:28), from lane3-testbed/pass3-nlp-review.md finding
B3: `inject/pools.py::_lane3_chunks` read the in-sample `chunk_1..chunk_4` columns, so every
chunk-consuming quantity in this partial run is non-confirmatory. Kept for reproduction and
for the in-sample vs OOF comparison only. The confirmatory run is `results/layerb-grid/`
with `score_version = "oof"`. Do not cite numbers from here.
