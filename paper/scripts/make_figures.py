"""Regenerate every figure in the working paper from the saved grids and paper/tables/numbers.json.

Run (matplotlib is not in the lane-4 venv; uv supplies it ephemerally):
  cd lane4-simulation && uv run --python .venv/bin/python --with matplotlib python ../paper/scripts/make_figures.py

Colour rules: Okabe-Ito hues that also differ in lightness, values printed on every heatmap cell,
markers differ by shape as well as colour, so nothing is carried by colour alone.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
L4 = ROOT / "lane4-simulation"
sys.path.insert(0, str(L4))
sys.path.insert(0, str(ROOT / "paper" / "scripts"))
import population as pop  # noqa: E402

OUT = ROOT / "paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
NUM = json.loads((ROOT / "paper" / "tables" / "numbers.json").read_text())

OKABE = {"black": "#000000", "orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73",
         "yellow": "#F0E442", "blue": "#0072B2", "vermilion": "#D55E00", "purple": "#CC79A7"}
EST_STYLE = {  # colour + marker + lightness-distinct
    "naive": (OKABE["black"], "o"), "delete": (OKABE["blue"], "s"), "simex": (OKABE["orange"], "^"),
    "labelfree": (OKABE["green"], "D"), "em": (OKABE["vermilion"], "v"),
}
PIS = (0.01, 0.02, 0.05, 0.10, 0.20, 0.30)
DETS = ("none", "calibrated", "degraded", "oracle")
PS = (0.0, 0.5, 1.0)
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 200})


def load(path):
    with open(path) as fh:
        return [json.loads(line) for line in fh if line.strip()]


LB = load(L4 / "results" / "layerb-grid" / "grid.jsonl")
LB5 = load(L4 / "results" / "layerb-grid-500rep" / "grid.jsonl")
LA = load(L4 / "results" / "grid" / "grid.jsonl")
core = [r for r in LB if r["cell"]["arm"] == "box"]
RHO_H = NUM["lb_rho_H_ext"]


def savefig(fig, name):
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight")
    fig.savefig(OUT / f"{name}.svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


# ---------------------------------------------------------------- fig 1: contamination bias map
fig, ax = plt.subplots(figsize=(6.2, 2.6))
M = np.array([[100 * NUM[f"lb_cb_relbias_p{p}_pi{pi}"] for pi in PIS] for p in PS])
lim = max(abs(M.min()), abs(M.max()))
im = ax.imshow(M, cmap="PuOr_r", vmin=-lim, vmax=lim, aspect="auto")
for i, p in enumerate(PS):
    for j, pi in enumerate(PIS):
        v = M[i, j]
        ax.text(j, i, f"{v:+.0f}%", ha="center", va="center", fontsize=9,
                color="white" if abs(v) > 0.6 * lim else "black")
ax.set_xticks(range(len(PIS)), [f"{pi:.2f}" for pi in PIS])
ax.set_yticks(range(len(PS)), [f"p = {p:.1f}\n(c = {0.379 * p:.2f})" for p in PS])
ax.set_xlabel("contamination fraction pi")
ax.set_ylabel("assignment coupling")
ax.set_title("Naive bias in rho_H, relative to the truth 0.068 (real text, n = 1000, no detector)", fontsize=9)
cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
cb.set_label("relative bias (%)")
savefig(fig, "fig1_contamination_bias_map")

# ---------------------------------------------------------------- fig 2: resolvability map
# Shaded by |naive bias| / MCSE: is there a contamination bias here large enough to see at
# 100 replications? Cells at or under 2 are unresolved, not shown to be zero.
fig, axes = plt.subplots(1, 4, figsize=(13.5, 3.2), sharey=True)
vmax = 14.0
for ax, d in zip(axes, DETS):
    G = np.zeros((3, 6))
    T = [["" for _ in PIS] for _ in PS]
    for i, p in enumerate(PS):
        for j, pi in enumerate(PIS):
            r = next(r for r in core if r["cell"]["n"] == 1000 and r["cell"]["detector"] == d and r["cell"]["p"] == p and r["cell"]["pi"] == pi)
            nv = r["estimators"]["naive"]["rho_H"]
            G[i, j] = abs(nv["bias"]) / nv["mcse"]
            rb = nv["rel_bias"]
            T[i][j] = f"{rb if abs(rb) >= 5e-3 else 0.0:+.2f}\n({nv['mcse'] / r['truth']['rho_H']:.3f})"
    im = ax.imshow(G, cmap="viridis_r", vmin=0, vmax=vmax, aspect="auto")
    for i in range(3):
        for j in range(6):
            ax.text(j, i, T[i][j], ha="center", va="center", fontsize=5.5, linespacing=1.4,
                    color="white" if G[i, j] > 0.5 * vmax else "black",
                    fontweight="bold" if G[i, j] > 2.0 else "normal")
    ax.set_xticks(range(6), [f"{pi:.2f}" for pi in PIS], fontsize=7)
    ax.set_title(f"detector: {d}", fontsize=9)
    ax.set_xlabel("pi")
axes[0].set_yticks(range(3), [f"p = {p:.1f}" for p in PS])
cb = fig.colorbar(im, ax=axes, fraction=0.015, pad=0.01)
cb.set_label("|naive bias| / MCSE")
fig.suptitle("Resolvability map: naive relative bias (relative MCSE); bold where |bias| > 2 MCSE "
             "(core box, n = 1000, 100 reps)", fontsize=9, y=1.02)
savefig(fig, "fig2_boundary_map")

# ---------------------------------------------------------------- fig 3: RMSE by estimator and detector (Layer B vs Layer A)
fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.2))
for ax, (title, rows, get, truth) in zip(axes, [
    ("Layer B, real text (rho_H = 0.068), 336 cells", LB, lambda r, e: r["estimators"][e]["rho_H"]["rmse"], RHO_H),
    ("Layer A, parametric (rho_H = 0.418), 372 cells", LA, lambda r, e: r["summary"]["estimators"][e]["rho_H"]["rmse"], NUM["la_rho_H"]),
]):
    rng = np.random.default_rng(0)
    for di, d in enumerate(DETS):
        rs = [r for r in rows if r["cell"]["detector"] == d]
        for ei, e in enumerate(EST_STYLE):
            col, mk = EST_STYLE[e]
            x0 = di * 6 + ei
            ys = np.array([get(r, e) for r in rs])
            ax.scatter(x0 + rng.uniform(-0.25, 0.25, len(ys)), ys, s=6, marker=mk, color=col, alpha=0.35, linewidths=0)
            ax.plot([x0 - 0.35, x0 + 0.35], [np.median(ys)] * 2, color=col, lw=2)
    ax.set_xticks([di * 6 + 2 for di in range(4)], DETS)
    ax.set_ylabel("rho_H RMSE")
    ax.set_title(title, fontsize=9)
    ax.axhline(truth, color="grey", lw=0.8, ls=":")
    ax.text(23.5, truth, " truth rho_H", va="bottom", fontsize=7, color="grey")
    ymax = 0.11 if truth < 0.1 else 0.16
    n_clip = sum(get(r, e) > ymax for r in rows for e in EST_STYLE)
    ax.set_ylim(0, ymax)
    if n_clip:
        ax.text(0.99, 0.98, f"{n_clip} points above {ymax} not shown\n(labelfree, n_bins = 60 column)", transform=ax.transAxes,
                ha="right", va="top", fontsize=7, color="grey")
handles = [plt.Line2D([], [], color=c, marker=m, ls="", label=e) for e, (c, m) in EST_STYLE.items()]
axes[0].legend(handles=handles, fontsize=7, ncol=5, loc="upper left", frameon=False)
fig.suptitle("Per-cell RMSE by estimator; bars are medians. On real text, naive is lowest in 274 of 336 cells", fontsize=9, y=1.02)
savefig(fig, "fig3_rmse_by_estimator")

# ---------------------------------------------------------------- fig 4: T1 by prevalence, 100 vs 500 reps
fig, ax = plt.subplots(figsize=(5, 2.8))
pis = (0.01, 0.02, 0.05, 0.10, 0.20)
for tag, col, mk in (("100", OKABE["sky"], "o"), ("500", OKABE["blue"], "s")):
    fr = [NUM[f"lb_t1_b3_pass_pi{pi}_{tag}"] / NUM[f"lb_t1_b3_n_pi{pi}_{tag}"] for pi in pis]
    ax.plot(range(5), fr, marker=mk, color=col, label=f"{tag} reps")
    for x, pi in enumerate(pis):
        ax.annotate(f"{NUM[f'lb_t1_b3_pass_pi{pi}_{tag}']}/{NUM[f'lb_t1_b3_n_pi{pi}_{tag}']}", (x, fr[x]),
                    textcoords="offset points", xytext=(0, 6 if tag == "500" else -11), ha="center", fontsize=7, color=col)
ax.axhline(1.0, color="grey", ls=":", lw=0.8)
ax.text(0.05, 1.0, "SPEC T1 requires every cell", va="bottom", fontsize=7, color="grey")
ax.set_xticks(range(5), [f"{pi:.2f}" for pi in pis])
ax.set_ylim(0, 1.08)
ax.set_xlabel("pi")
ax.set_ylabel("share of resolvable cells where\nbest corrector meets the 20% bar")
ax.legend(frameon=False, fontsize=8, loc="center left")
savefig(fig, "fig4_t1_by_prevalence")

# ---------------------------------------------------------------- fig 5: Layer A three regimes, closed form vs MC
fig, ax = plt.subplots(figsize=(5, 3))
pi_grid = np.linspace(0, 0.32, 200)
for c, col, mk in ((0.0, OKABE["blue"], "o"), (0.4, OKABE["orange"], "^"), (0.9, OKABE["vermilion"], "s")):
    ax.plot(pi_grid, [pop.att(p, c, 0.7, 0.5, 0.0) for p in pi_grid], color=col, lw=1.5, label=f"c = {c} closed form (E7)")
    xs, ys, es = [], [], []
    for r in LA:
        cl = r["cell"]
        if cl["c"] == c and cl["kappa"] == 0.5 and cl["n"] == 1000 and cl["detector"] == "none" and cl["rho_v"] == 0.0:
            e = r["summary"]["estimators"]["naive"]["rho_H"]
            xs.append(cl["pi"]); ys.append(1 + e["bias"] / NUM["la_rho_H"]); es.append(e["mcse"] / NUM["la_rho_H"])
    ax.errorbar(xs, ys, yerr=es, fmt=mk, color=col, ms=5, capsize=2, lw=0.8, label=f"c = {c} Monte Carlo")
ax.axhline(1, color="grey", ls=":", lw=0.8)
ax.set_xlabel("pi")
ax.set_ylabel("Att = rho_obs / rho_H")
ax.set_title("Layer A: three coupling regimes (kappa = 0.5, rel_H = 0.7, delta = 0)", fontsize=9)
ax.legend(fontsize=7, frameon=False, ncol=2)
savefig(fig, "fig5_layerA_regimes")

# ---------------------------------------------------------------- fig 6: r_F sensitivity
from make_tables import att_pass  # noqa: E402  (closed forms E48 to E51)

fig, ax = plt.subplots(figsize=(5.2, 3.2))
rf_grid = np.linspace(0.0, 0.6, 121)
for (kappa, c), col, ls in (((0.2, 0.0), OKABE["blue"], "-"), ((0.2, 0.9), OKABE["orange"], "--"), ((1.0, 0.0), OKABE["vermilion"], "-.")):
    ys = [att_pass(0.10, c, kappa, 0.0, 0.7, 0.5, rf, 0.85, 0.85) for rf in rf_grid]
    ax.plot(rf_grid, ys, color=col, ls=ls, lw=1.6, label=f"after deletion, kappa = {kappa}, c = {c}")
    ax.axhline(pop.att(0.10, c, 0.7, kappa, 0.0), color=col, ls=":", lw=0.9)
ax.axvline(NUM["rF_measured"], color="grey", lw=1)
ax.text(NUM["rF_measured"] + 0.01, 0.9995, f"measured r_F = {NUM['rF_measured']:.3f} (lower bound)", fontsize=7, color="grey", va="top")
ax.set_xlabel("fluency-trait correlation r_F")
ax.set_ylabel("Att_pass = rho_obs,pass / rho_H")
ax.set_title("Detect-and-delete at the degraded point (se = sp = 0.85), pi = 0.10", fontsize=9)
ax.plot([], [], color="grey", ls=":", label="no detector (same kappa, c)")
ax.legend(fontsize=7, frameon=False, loc="lower left")
savefig(fig, "fig6_rF_sensitivity")

# ---------------------------------------------------------------- fig 7: realized detector sensitivity
fig, ax = plt.subplots(figsize=(4.6, 2.6))
labels, vals, cols = [], [], []
for pool, pl in (("gpt4", "gpt-4-0613"), ("llama2", "llama-2")):
    for lvl, col in (("calibrated", OKABE["blue"]), ("degraded", OKABE["orange"])):
        labels.append(f"{pl}\n{lvl}\n(sp = {NUM[f'lb_sp_{pool}_{lvl}']:.2f})")
        vals.append(NUM[f"lb_se_{pool}_{lvl}"])
        cols.append(col)
bars = ax.bar(range(4), vals, color=cols, edgecolor="black", lw=0.5)
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.02, f"{v:.2f}", ha="center", fontsize=8)
ax.set_xticks(range(4), labels, fontsize=7)
ax.set_ylim(0, 1.05)
ax.set_ylabel("realized sensitivity (share of machine text caught)")
ax.set_title("Detectability is a generator property, not a constant", fontsize=9)
savefig(fig, "fig7_detector_sensitivity")

# ---------------------------------------------------------------- fig 8: em vs naive bias at 500 reps
fig, ax = plt.subplots(figsize=(3.6, 3.4))
xs = [abs(r["estimators"]["naive"]["rho_H"]["bias"]) for r in LB5]
ys = [abs(r["estimators"]["em"]["rho_H"]["bias"]) for r in LB5]
ax.scatter(xs, ys, s=8, color=OKABE["vermilion"], alpha=0.6, linewidths=0)
m = max(max(xs), max(ys))
ax.plot([0, m], [0, m], color="grey", lw=0.8, ls=":")
ax.set_xlabel("|naive bias|")
ax.set_ylabel("|EM bias|")
ax.set_title(f"500 reps, pi <= 0.20: EM worse than naive in {NUM['lb5_em_worse_than_naive']} of 280 cells", fontsize=8)
ax.set_aspect("equal")
savefig(fig, "fig8_em_vs_naive_500rep")
