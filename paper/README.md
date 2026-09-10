# paper/

The working-paper draft and everything that regenerates its numbers.

| path | what |
|---|---|
| `GHOST-RESPONDENTS-DRAFT.md` | the draft (Psychological Methods shape); `TODO` marks unsourced claims |
| `scripts/make_tables.py` | reads the saved grids and closed forms, writes `tables/*.md` and `tables/numbers.json` |
| `scripts/make_figures.py` | draws `figures/*.png` and `.svg` from the same inputs |
| `scripts/check_numbers.py` | self-check: every numeric token in the draft against `numbers.json`, the tables, and a whitelist of document-sourced constants |
| `tables/` | 14 generated tables (do not edit by hand) |
| `figures/` | 8 generated figures |

Regenerate everything:

```
lane4-simulation/.venv/bin/python paper/scripts/make_tables.py
cd lane4-simulation && uv run --python .venv/bin/python --with matplotlib python ../paper/scripts/make_figures.py && cd ..
lane4-simulation/.venv/bin/python paper/scripts/check_numbers.py
```

Inputs are read-only: `lane4-simulation/results/{grid,grid-labelfree-nbins8,layerb-grid,layerb-grid-500rep}/grid.jsonl`,
`lane4-simulation/population.py`, `lane3-testbed/analysis/fluency_r_f_results.json`.
