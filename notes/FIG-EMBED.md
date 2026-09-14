# Figure embedding and PDF render

Lane `ghostfigs`, 2026-09-13. The draft referenced eight figures in prose and embedded none.
All eight are now embedded at their first major prose reference and the preprint PDF is
rendered and pixel-verified. No prose and no numbers were changed: the draft diff is
`40 insertions(+), 0 deletions(-)` and `git diff paper/tables/` is empty.

## 1. Reference map

Every `Figure N` mention in the draft, the file it maps to, and where the image was placed.
"First reference" is the line number in the pre-embed file.

| Fig | File | First prose reference | Section | Embedded |
|---|---|---|---|---|
| 1 | `paper/figures/fig1_contamination_bias_map.png` | L474 "Figure 1 and Table 3 give the naive bias in the core box at n = 1000 with no detector." | 5.2 | after that sentence, before Table 3 |
| 2 | `paper/figures/fig2_boundary_map.png` | L619 "Table 7 and Figure 2 give the naive relative bias in the core box at n = 1000 against its own Monte Carlo standard error" | 5.4 | after Table 7, before "Reading it:" |
| 3 | `paper/figures/fig3_rmse_by_estimator.png` | L603 "naive ... the lowest cellwise RMSE in 274 of 336 cells (Figure 3)" | 5.3 | after that paragraph |
| 4 | `paper/figures/fig4_t1_by_prevalence.png` | L522 "0/6, 0/6, 2/13, 8/29, 20/41 at pi = 0.01 ... (Figure 4)" | 5.3 | after that paragraph |
| 5 | `paper/figures/fig5_layerA_regimes.png` | L442 "exactly as the table reads (Figure 5)" | 5.1 | after that paragraph |
| 6 | `paper/figures/fig6_rF_sensitivity.png` | L837 "Figure 6 gives the r_F at which it would matter" | 5.6 | after that paragraph |
| 7 | `paper/figures/fig7_detector_sensitivity.png` | L379 "Detectability is a generator property, not a constant (Figure 7)" | 4.2 | after that paragraph |
| 8 | `paper/figures/fig8_em_vs_naive_500rep.png` | L761 "\|em bias\| exceeds \|naive bias\| in 157 of 280 cells (56%; Figure 8)" | 5.5 | after that paragraph |

Later mentions were left as cross-references: Figure 8 is named again at L966 (Discussion
recommendation 6). No other figure is referenced twice.

PNG was used over SVG in every case: Chrome headless rasterises the base64-inlined PNGs
reliably, and the PNGs are written at `savefig.dpi = 200`, which is 340-390 effective dpi at
the widths used, so nothing is resolution-limited on the page.

Captions were written from the figure's own title plus the sentence that introduces it. Two
places where the surrounding prose and the figure had to be reconciled rather than copied:

- Figure 5's caption says "attenuation at c = 0 and c = 0.4 and inflation at c = 0.9",
  matching the draft at L440-442 ("c = 0.9 sits in the inflation regime and c in {0, 0.4} in
  the attenuation regime"). The three regimes of section 2.2 are not one-per-curve here.
- Figure 6's caption says the vertical line marks "r_F = 0.053" without calling it measured.
  See the known mismatch in section 4.

## 2. fig2 provenance check

The instruction was to confirm the embedded fig2 is the regenerated resolvability map, not a
stale winner-labeled version. It is. Checked three ways:

- The file on disk renders with the title `Resolvability map: naive relative bias (relative
  MCSE); bold where |bias| > 2 MCSE (core box, n = 1000, 100 reps)`, read off the image, not
  off the filename or mtime.
- `paper/scripts/make_figures.py:107` emits exactly that suptitle; the `ABBR` winner-label
  table is gone from `make_tables.py` (`notes/ITER-AF.md` round D, "Boundary map becomes a
  resolvability map").
- Regenerating from the frozen grid reproduced the same PNG byte-for-byte, so the artifact on
  disk is the round-D output and nothing later diverged from it.

The values in the figure match Table 7 cell by cell, including the worst cell
(p = 1, pi = 0.30, calibrated, +0.597) and the 8 cells above 0.30.

## 3. One figure was regenerated: fig3

`fig3_rmse_by_estimator.png` as shipped had its top half blank, with a stray "truth rho_H"
label floating above both panels. Cause, at `make_figures.py:129`:

    ax.text(23.5, truth, " truth rho_H", ...)

x = 23.5 and y = truth are data coordinates outside the axes. On the right panel truth is
0.418 against a y-limit of 0.16, so `bbox_inches="tight"` expanded the canvas to about 2.6x
the axes height to include a label that was never inside the plot. The label was also drawn
before `set_ylim`, so it could not know it was out of range.

Fix, three lines, in the same place: compute the limit first, then draw the label only when
the truth line is actually visible, anchored with `ax.get_yaxis_transform()` so x is an axes
fraction and y stays in data units.

    ax.set_ylim(0, ymax)
    if truth < ymax:
        ax.text(0.99, truth, "truth rho_H ", transform=ax.get_yaxis_transform(), ...)

Re-ran `make_figures.py` over the frozen grids. Effect on the repo:

- `fig3_rmse_by_estimator.png` changed: blank band gone, label sits on the truth line inside
  the Layer B panel, the Layer A panel drops a label for a line that was never on screen.
- The other seven PNGs are byte-identical to what was committed.
- The eight SVGs differ only in their embedded creation date.
- `git diff paper/tables/` is empty: all 14 tables and all 452 numbers are unchanged.

This is a rendering fix to a plotting call, not a change to any plotted value.

## 4. Per-figure check in the PDF

Every figure page was rasterised at 130 dpi and inspected. "Ink" is the share of pixels below
200/255 on the whole page, as a blank-page guard.

| Fig | PDF page | Renders | Ink | Caption adjacent | Clipping | Legibility |
|---|---|---|---|---|---|---|
| 7 | 8 | yes | 10.1% | yes, directly below | none; bar labels 0.27/0.69/0.62/0.94 all read | good |
| 5 | 10 | yes | 7.6% | yes | none; legend, both axes, all six series read | good |
| 1 | 11 | yes | 6.8% | yes | none; all 18 cell values and the colorbar read | good |
| 4 | 13 | yes | 7.6% | yes | none; all ten n/N annotations read | good |
| 3 | 15 | yes | 5.9% | yes | none; both panels, legend, "101 points above 0.16 not shown" read | good, after the section 3 fix |
| 2 | 16 | yes | 13.5% | yes | none; all four detector panels and the colorbar read | small but legible; see note |
| 8 | 19 | yes | 6.1% | yes | none; diagonal, both axes and the title read | good |
| 6 | 21 | yes | 8.0% | yes | none; four-entry legend and both dotted references read | good |

No figure page is blank, none is cropped at a page edge, and no figure is split across pages.
Every caption sits on the same page as its image. Sweeping all 32 pages, none falls below 3%
ink, so there is no accidental blank page anywhere in the document.

Figure 2 note: at 3.34:1 across the full text width the per-cell numbers are the smallest
type in the document. They are legible on screen at 100% and sharp when zoomed, because the
source is 2325 px into 6.4 in. The figure is the shading view of the map; Table 7 sits
immediately above it with the same numbers at body-table size, so nothing is readable only
in the figure.

## 5. The PDF

    pandoc paper/GHOST-RESPONDENTS-DRAFT.md \
      --from=markdown-yaml_metadata_block --to=html5 --standalone --embed-resources \
      --resource-path=paper --css=paper/print.css \
      --metadata pagetitle="Ghost respondents: a boundary map for covert AI authorship in open-ended survey data" \
      -o ghost.html

    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
      --no-pdf-header-footer --print-to-pdf=/tmp/ghost-preprint-final.pdf file://$PWD/ghost.html

On the YAML strip: the draft has no front matter, but the bare `---` rule before
`## References` (L1199) was being read as the opening of a YAML metadata block, and pandoc
died on the colon inside "`docs/LIT-SCAN.md`: **V**" seven lines later. Disabling the
extension with `--from=markdown-yaml_metadata_block` leaves that `---` as the horizontal
rule it was meant to be and needs no edit to the source. `--embed-resources` inlines the
eight PNGs as base64, so Chrome does not depend on the HTML's location to find them.

**Correction, 2026-09-13 (see `paper/CITATION-UPDATE.md`).** Disabling `yaml_metadata_block`
alone was not enough. That same bare `---` was then read by `multiline_tables` as a table
dashline, and the whole References section - heading included - was swallowed into a
one-column table 6% of the text width, which is how it renders in the 32-page PDF above. The
build now also disables that extension:

    --from=markdown-yaml_metadata_block-multiline_tables

The paper's own 15 tables are pipe tables and are unaffected; the only `<table>` the flag
removes is the bogus one. With it the references set as a normal full-width list and the
document is 31 pages.

`paper/print.css` is committed so the PDF is rebuildable from the repo. It is print CSS only:
letter at 0.85 x 0.8 in margins, a serif body at 10.5 pt, 8.1 pt bordered tables set to avoid
breaking across pages, and figures centred with their caption paragraph pinned to the image.

Output, both copies byte-identical at 1,338,249 bytes:

- `/tmp/ghost-preprint-final.pdf`
- `paper/paper-preprint.pdf`

**32 pages**, letter (612 x 792 pt). All eight "Figure N." captions are present in the
extracted text, on eight distinct pages.

## 6. Known mismatch, not fixed here

Figure 6's in-plot annotation still reads "measured r_F = 0.053 (lower bound)". Since
`notes/ITER-AF.md` round C, the draft calls 0.053 a surface proxy and names 0.045 from the
detector's own score as the direct anchor (section 5.6, Table 11). The figure's wording
predates that change. Fixing it means editing a figure label about a number, which is outside
this lane's remit, so it is recorded rather than changed. The caption added here says only
that the line marks r_F = 0.053, so nothing in the embedded text repeats the stale framing.

Nothing was published. The OSF upload is handled separately.
