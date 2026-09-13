# Voice fix: state the estimates, drop the ceremony

Pass of 2026-09-13. Rule applied: failed pre-registered claims are reported as the estimates
they produced and the text moves on. No announcement of honesty, withdrawal, or transparency;
no honesty-as-strength framing. Every number is unchanged. Swept: GHOST-RESPONDENTS-DRAFT.md,
QUEUE.md, README.md, FRAMING-DECISION.md, GAPS-CLOSURE-SPEC.md, REWRITE-NOTES.md,
FINAL-PASS-REPORT.md. QUEUE.md, README.md, and FRAMING-DECISION.md had no instances.

39 instances rewritten.

## GHOST-RESPONDENTS-DRAFT.md

### 1. front matter

Before:

```
The draft carries no unsourced claims marked for later. What is unresolved is listed under
Open items at the end, with its status.
```

After:

```
Unresolved items are listed under Open items at the end, with their status.
```

### 2. Abstract

Before:

```
Five times the replications sharpens the
failure instead of dissolving it: the best corrector meets the bias bar in 28.5% of resolvable
cells against a requirement of 100%, and EM turns out to be slightly harmful. The
anti-deletion argument I started with survives only conditionally: the deletion-selection bias
scales with the square of the fluency-trait correlation r_F, and at the measured r_F of 0.053
the detector destroys 0.1% of trait variance.
```

After:

```
At five times the
replications the best corrector meets the bias bar in 28.5% of resolvable cells against a
requirement of 100%, and EM is slightly harmful. The deletion-selection bias scales with the
square of the fluency-trait correlation r_F, and at the measured r_F of 0.053 the detector
destroys 0.1% of trait variance.
```

### 3. Abstract

Before:

```
One thing does work, and it is the one that declines to return a point estimate. Given the
prevalence,
```

After:

```
The partial-identification bound meets its target. Given the
prevalence,
```

### 4. 1.2

Before:

```
The pre-registered thresholds (SPEC 4.4) mostly fail, and the failure is the finding. On real
```

After:

```
Three of the four pre-registered thresholds (SPEC 4.4) fail outright and the fourth fails at
both realistic detector operating points (section 5.3). On real
```

### 5. 1.2

Before:

```
The naive estimator has the
lowest median RMSE in every detector group. Two adversarial reviews run blind to each other
reached the same conclusion about what is publishable here: the map of where each strategy
helps and where none does. That is what I report.

Four positive results survive.
```

After:

```
The naive estimator has the
lowest median RMSE in every detector group. The deliverable is the map of where each strategy
helps and where none does.

Four results follow.
```

### 6. 1.2

Before:

```
3. The deletion-selection bias, my original argument against detect-and-delete, is real but
   governed by r_F^2, and at the r_F I measure it is negligible. I report the sensitivity
   table instead of the kill claim (section 5.6).
4. The one estimator that meets its pre-registered target is the one that refuses to return a
   point estimate. Given pi,
```

After:

```
3. The deletion-selection bias is O(r_F^2), and at the measured r_F = 0.053 it is
   negligible; section 5.6 gives it as a sensitivity table over r_F.
4. The partial-identification bound meets its pre-registered target. Given pi,
```

### 7. 1.2

Before:

```
The fourth is the constructive half of the paper. At this validity level the honest output of
a contaminated open-ended item is a bracket, not a coefficient.
```

After:

```
The fourth is the constructive half of the paper. At this validity level the appropriate
output for a contaminated open-ended item is a bracket, not a coefficient.
```

### 8. 1.3

Before:

```
That assumption is stated in section 3 and named in Limitations as the most consequential one
the design makes, and the label-free failure reported here is its price, not a claim that
correction is impossible when labels exist.
```

After:

```
Section 3 states that assumption and section 7 discusses it; the label-free results here
apply to the no-label regime and say nothing about correction when labels exist.
```

### 9. 3

Before:

```
Every negative result in section 5
is a result about the no-label regime, and Limitations names this assumption as the most
consequential one the design makes.
```

After:

```
Every negative result in section 5
is a result about the no-label regime (section 7).
```

### 10. 4.3

Before:

```
Nothing was tuned to pass. The thresholds are evaluated as written on the cell set of 4.2.
```

After:

```
The thresholds were fixed before any grid run and are evaluated as written on the cell set
of 4.2.
```

### 11. 5.1

Before:

```
Every one of those is a move from catastrophic to merely failing. The simex column
```

After:

```
Each remains outside its threshold. The simex column
```

### 12. 5.3 T3

Before:

```
The quantification literature predicts this miss, and it is worth naming which assumption
breaks rather than reporting the number alone. Distribution-matching
```

After:

```
The quantification literature predicts this miss. Distribution-matching
```

### 13. 5.3 T4

Before:

```
The statement the data support is stronger and
less flattering than the concession: at this signal level, doing nothing beats both.
```

After:

```
At this signal level, doing nothing beats both.
```

### 14. 5.4

Before:

```
- **The partial-identification bound SPEC asks for is the one thing in this paper that meets
  its target, and getting there required finding out why the obvious version of it is wrong.**
```

After:

```
- **The partial-identification bound SPEC asks for meets its target once sampling
  uncertainty is included.**
```

### 15. 5.4

Before:

```
A bound that narrow is narrow because it is wrong. It
  states the identification uncertainty from unknown c and silently treats `rho_obs_hat`, a
  Monte Carlo point estimate carrying naive's own MCSE, as exact.
```

After:

```
That width is understated: the bound
  carries the identification uncertainty from unknown c and treats `rho_obs_hat`, a Monte
  Carlo point estimate carrying naive's own MCSE, as exact.
```

### 16. 5.6

Before:

```
The honest form of the claim is the one the derivation always carried
(`lane1-partial-coupling.md` 3.5): deletion-selection is a real bias whose size is governed
by the out-of-domain false-positive rate and r_F, and here is the r_F you would need for it
to matter (Figure 6). SPEC 1.5's unconditional "kills detect-and-delete" is withdrawn.
```

After:

```
The claim the derivation supports (`lane1-partial-coupling.md` 3.5) is that
deletion-selection is a bias whose size is governed by the out-of-domain false-positive rate
and r_F; Figure 6 gives the r_F at which it would matter. SPEC 1.5's unconditional "kills
detect-and-delete" does not hold at the measured r_F.
```

### 17. 6 rec 2

Before:

```
The one estimator
   in this study that meets its pre-registered target is the partial-identification bound of
   section 5.4, and it meets it by declining to produce a number: coverage no lower than
```

After:

```
The partial-identification
   bound of section 5.4 meets its pre-registered target: coverage no lower than
```

### 18. 6 closing

Before:

```
It is withdrawn from this paper's deliverables and named as future
work (section 7); the whole-text validity numbers above are the only evidence offered, and
they are suggestive of the direction, not confirmatory of what a document-pooled Layer B run
would find.
```

After:

```
It is left as future work (section 7). The whole-text validity numbers
above indicate the direction; they do not show what a document-pooled Layer B run would find.
```

### 19. References header

Before:

```
Provenance, stated so a reader knows what "checked" covers. Entries carried from the
```

After:

```
Verification status per entry. Entries carried from the
```

### 20. References header

Before:

```
Anything still unconfirmed is marked `unverified` and stays that way.
```

After:

```
Anything still unconfirmed is marked `unverified`.
```

### 21. Open items 1

Before:

```
Section 1.1 now states what each of the three actually does
   rather than gesturing at them.
```

After:

```
Section 1.1 states what each of the three does.
```

### 22. Open items 2

Before:

```
Full
   texts were not read, and the References entries say so.
```

After:

```
Full
   texts were not read.
```

### 23. Open items 5

Before:

```
5. **WITHDRAWN-honestly 2026-09-10.** Document-pooled Layer B is named as future work
   (section 6, Limitations), not implied as imminent.
```

After:

```
5. **WITHDRAWN 2026-09-10.** Document-pooled Layer B is future work (section 6, Limitations).
```

### 24. Open items 7

Before:

```
the front
   matter carries an explicit placeholder rather than an invented line.
```

After:

```
the front
   matter carries a placeholder.
```

## GAPS-CLOSURE-SPEC.md

### 25. title

Before:

```
# Honest-gaps closure spec
```

After:

```
# Gaps closure spec
```

### 26. scope

Before:

```
Scope: close or honestly
withdraw the 7 items
```

After:

```
Scope: close or
withdraw the 7 items
```

### 27. item 1

Before:

```
sourced numbers; WITHDRAWN-honestly (drop the
```

After:

```
sourced numbers; WITHDRAWN (drop the
```

### 28. item 2

Before:

```
so it is the honest
upper bound to use
```

After:

```
so it is the
upper bound to use
```

### 29. item 2

Before:

```
Scope limit, stated honestly rather than smoothed: this
```

After:

```
Scope limit: this
```

### 30. item 3

Before:

```
Closed as: WITHDRAWN-honestly.
```

After:

```
Closed as: WITHDRAWN.
```

### 31. item 4

Before:

```
audit-and-flag step; WITHDRAWN-honestly
on the specific
```

After:

```
audit-and-flag step; WITHDRAWN
on the specific
```

### 32. definitions

Before:

```
- WITHDRAWN-honestly: the claim is removed or downgraded to what the evidence actually
  supports, with the reason stated in place of the removed claim.
```

After:

```
- WITHDRAWN: the claim is removed or downgraded to what the evidence supports, with the
  reason stated in place of the removed claim.
```

## REWRITE-NOTES.md

### 33. Section 1

Before:

```
it now states the
threshold failures as the finding in the first sentence, not as a caveat after a positive
result.
```

After:

```
it now states the
threshold results in the first sentence.
```

### 34. Career framing

Before:

```
One-page comparison, honest, no inflation.
```

After:

```
One-page comparison.
```

### 35. Career framing

Before:

```
a three-pass verification discipline (independent re-derivation, numerical
certification against simulation, adversarial review with a mandate to find the error) that
caught its own headline claim being wrong before it shipped; a pre-registered analysis plan
whose failures are reported as failures, with the magnitude of the miss stated (82-98%, not
"mostly"); and a negative result that is mechanistically explained rather than shrugged at
(the estimators fail because the box is variance-dominated at this validity level, not because
the correction machinery is broken in some unspecified way).
```

After:

```
a three-pass verification discipline (independent re-derivation, numerical
certification against simulation, adversarial review) that revised the headline claim before
submission; a pre-registered analysis plan with the threshold results stated at their
magnitude (82-98% miss); and a negative result with a mechanism (the box is
variance-dominated at this validity level).
```

### 36. Career framing

Before:

```
A committee that skims for "what did you
discover" rather than "how did you handle discovering you were wrong" will get less out of it.
```

After:

```
A committee that skims for "what did you
discover" rather than reading the methods will get less out of it.
```

### 37. Career framing

Before:

```
and the honest failure of the label-free prevalence
estimator and the EM mixture is the kind of finding that saves someone else from shipping a
broken correction.
```

After:

```
and the label-free prevalence and EM mixture
results are the kind of finding that saves someone else from shipping a broken correction.
```

## FINAL-PASS-REPORT.md

### 38. 1.2

Before:

```
- New closing line, which is the one-sentence stress test the brief asked for: at this
  validity level the honest output of a contaminated open-ended item is a bracket, not a
  coefficient.
```

After:

```
- New closing line: at this validity level the appropriate output for a contaminated
  open-ended item is a bracket, not a coefficient.
```

### 39. closing

Before:

```
The
spine it lost when the kill claim failed has been replaced rather than papered over: the
boundary map is the descriptive deliverable, and the partial-identification bound is the
prescriptive one, and the bound is the first thing in the project that meets a pre-registered
target without qualification beyond a condition the paper states plainly. The paper's
strongest feature is still that it reports its own failures at full magnitude - 0/372 nominal
coverage for the pre-registered primary, the withdrawn kill claim, EM getting worse with more
resolution, the naive estimator winning 274 of 336 cells - and this pass added failures rather
than removing any, including one internal contradiction in the section 5.7 restatement of
Prop. 14 and three new limitations that a reviewer would otherwise have found first. What it
cannot do yet is claim a working correction, and it does not try to.
```

After:

```
The
boundary map is the descriptive deliverable and the partial-identification bound is the
prescriptive one; the bound meets its pre-registered target conditional on a known pi. The
negative results stand as stated: 0/372 nominal coverage for the pre-registered primary, the
r_F-conditional deletion-selection result, EM getting worse with more resolution, the naive
estimator winning 274 of 336 cells. This pass also fixed one internal contradiction in the
section 5.7 restatement of Prop. 14 and added three limitations. There is no working
correction.
```
