GHOST PROJECT - LANE 4 (SIMULATION HARNESS) - DAY 1 KICKOFF

Read SPEC.md sections 4, 5, and 7 in this workspace first, plus derivations/lane1-open-questions.md items N1, N2, N3, Q7 (binding notation decisions). You are lane 4, the simulation harness lane. Fable orchestrator with Sonnet subagents writing the code; Fable itself (not a subagent) reviews the estimator code line by line before any grid run.

Deliverable today: lane4-simulation/ with the Layer A parametric Monte Carlo engine, NOT yet run at grid scale:
1. DGP per SPEC 4.1 with lane 1's N1 form: x | M = mu_M + c sqrt(s2_M / s2_T) theta + v, Var(v) = (1 - c^2) s2_M, so c means Cor(x, theta | M) exactly.
2. Grid machinery per SPEC 4.3, extended per N3 (kappa in {0.2, 0.5, 1.0}) and Q7 (rho_v as a grid parameter, default arm independent-calls rho_v = 0).
3. Metrics per SPEC 4.4 computed for BOTH rho_H (clean-sample observed validity, headline per N2 recommendation) and rho_T (disattenuated), so Abhay's pending N2 call costs no rework.
4. Estimators: naive, detect-and-delete at the three detector operating points, SIMEX (3.1), label-free prevalence + errors-in-variables (3.2). EM multi-start with parametric bootstrap intervals for the mixture model (3.3) is the cheap alternative the SPEC flags - implement that, not Stan.
5. One pilot cell (pi = 0.10, c = 0, n = 1000, kappa = 0.5, detector = oracle) run end-to-end with seeds frozen, output written to lane4-simulation/PILOT.md including runtime per fit so the overnight-grid core-hour estimate can be checked.

Sharding: fits are embarrassingly parallel, shard by cell, single-machine cores only. Do NOT run the full grid today - the pilot plus a Fable line-by-line review of estimator code comes first, and lane 1's day-2 handoff block may adjust the DGP. End with DONE-LANE4-DAY1 and a one-paragraph summary.
