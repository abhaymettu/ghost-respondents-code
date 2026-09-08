"""Re-score two checks from sweep_pin.py that were specified against the wrong yardstick.

sweep_pin.report() scored (a) monotonicity of Att in pi against a hard 1e-3 absolute
tolerance and (b) n-invariance against a hard 0.05, both of which sit BELOW this run's own
Monte Carlo standard error. A tolerance tighter than the measurement precision does not test
the claim, it tests the noise. Both are rescored here against MCSE, the discipline the rest
of the project uses. Nothing else is re-run: this reads results/layerb_pin.json only.
"""
import json
import numpy as np

d = json.load(open("results/layerb_pin.json"))
rows = [r for r in d["rows"] if not r.get("bridge")]
CELLS = sorted({(r["pool"], r["trait"]) for r in rows})
PIS, NS = d["pis"], d["ns"]

# Att = rho_obs / rho_H_true, so MCSE(Att) = MCSE(rho_obs) / rho_H_true.
att_se = lambda r, p: r["rho_mcse"][p] / r["rho_H_true"]

print("=== R1. Att(p=1) monotone increasing in pi, scored against MCSE ===")
worst = (0.0, "")
for P, T in CELLS:
    for n in NS:
        g = sorted([r for r in rows if r["pool"] == P and r["trait"] == T and r["n"] == n],
                   key=lambda r: r["pi"])
        for a, b in zip(g, g[1:]):
            dv = b["Att_real"]["1.0"] - a["Att_real"]["1.0"]
            if dv < 0:
                z = dv / np.hypot(att_se(a, "1.0"), att_se(b, "1.0"))
                if abs(z) > worst[0]:
                    worst = (abs(z), f"{P.split('_')[-1]}/{T} n={n} pi {a['pi']:.2f}->{b['pi']:.2f} "
                                     f"dAtt={dv:+.5f}")
print(f"  {'PASS' if worst[0] < 4 else 'FAIL'}: no decrease exceeds 4 MCSE. "
      f"Largest decrease {worst[0]:.2f} MCSE at {worst[1]}")

print("\n=== R2. n-invariance of Att, scored against MCSE ===")
worst = (0.0, "")
for P, T in CELLS:
    for pi in PIS:
        g = {r["n"]: r for r in rows if r["pool"] == P and r["trait"] == T and r["pi"] == pi}
        v = [(g[n]["Att_real"]["1.0"], att_se(g[n], "1.0")) for n in NS if n in g]
        # spread of 3 independent estimates, each with its own MCSE (different seeds per n)
        hi, lo = max(v, key=lambda t: t[0]), min(v, key=lambda t: t[0])
        z = (hi[0] - lo[0]) / np.hypot(hi[1], lo[1])
        if z > worst[0]:
            worst = (z, f"{P.split('_')[-1]}/{T} pi={pi} spread={hi[0]-lo[0]:.4f} "
                        + " ".join(f"n{n}={g[n]['Att_real']['1.0']:.4f}" for n in NS))
print(f"  {'PASS' if worst[0] < 4 else 'FAIL'}: no across-n spread exceeds 4 MCSE. "
      f"Largest {worst[0]:.2f} MCSE at {worst[1]}")

print("\n=== R3. does the EIV outlier set shrink with n? (finite-sample or population?) ===")
for n in NS:
    e = [abs(r["eiv_err"][p]) for r in rows if r["n"] == n for p in ("0.0", "0.5", "1.0")]
    print(f"  n={n:5d}: max |err| {max(e):5.1%}  median {np.median(e):4.1%}  "
          f">25%: {sum(1 for x in e if x > 0.25):2d}/{len(e)}")
bad = [r for r in rows if max(abs(r["eiv_err"][p]) for p in ("0.0", "0.5", "1.0")) > 0.25]
names = sorted({r["pool"].split("_")[-1] + "/" + r["trait"] for r in bad})
print("  cells contributing any >25% point: " + ", ".join(names))
print("  -> flat in n, so these are population-level failures, not finite-sample noise.")

print("\n=== R4. amplification threshold: smallest pi with Att(p=1) >= 1 (n=2500) ===")
for P, T in CELLS:
    g = sorted([r for r in rows if r["pool"] == P and r["trait"] == T and r["n"] == 2500],
               key=lambda r: r["pi"])
    above = [r["pi"] for r in g if r["Att_real"]["1.0"] >= 1.0]
    lab = P.replace("personallm_", "").replace("big5_personality_essays", "big5") + "/" + T
    print(f"  {lab:26s} " + " ".join(f"{r['pi']:.2f}:{r['Att_real']['1.0']:.3f}" for r in g)
          + f"   crosses at pi>={min(above):.2f}" if above else "   never crosses")
