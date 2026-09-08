GHOST PROJECT - LANE 3 (TESTBED) - DAY 2

Continue in this workspace. Day 1 (TESTBED-REPORT.md, loaders, data) is done. Today, per SPEC day-by-day:

1. Detector calibration: calibrate a published open-weights AI-text classifier plus a simple feature baseline on the HC3 pairs, then re-calibrate on the essays testbed. Record operating points (se, sp) at calibrated, degraded, and oracle settings per SPEC 2.4; compare against the NORC PACT honest range (roughly 99% in-domain to mid-80s out-of-domain).
2. r_F estimate for lane 1's Q6: fluency proxies against trait scores in the essays data, so the deletion-selection magnitude has an empirical anchor. IMPORTANT CONSTRAINT: the local essays mirror has binary labels only; continuous BFI needs the IEEE DataPort login which is Abhay's call. Use whatever trait information the local data actually has, say exactly what you used, and flag in the report if the continuous-BFI version is blocked on that login.
3. rho_v measurement plan for Q7: write the concrete procedure (and code, but do not run generation) for measuring shared machine residual across items once counterpart generation exists: same-session versus independent-calls arms.
4. Freeze the testbed: summary stats file with verified counts, license notes, operating points, and the exact dataset fingerprints (hashes) lane 4 will code against.

Deliverable: lane3-testbed/CALIBRATION-REPORT.md plus any code under lane3-testbed/. No LLM counterpart generation yet - that batch is gated on a burn report to Abhay. End with DONE-LANE3-DAY2 and a one-paragraph summary.
