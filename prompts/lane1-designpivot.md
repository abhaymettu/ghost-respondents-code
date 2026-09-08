GHOST PROJECT - LANE 1 (lead) + LANE 2 (positioning) - DESIGN-PIVOT EVALUATION

User steering 6:30pm: "don't burn weeks or money on the 15k shape if a smarter design gets the same answer." The corpus-first audit (lane3-testbed/CORPUS-AUDIT.md, FALLBACK-AB, ~1,950-3,900 residual gens) found no existing corpus cleanly supplies the machine-text pool at the frozen design's conditioning levels. Evaluate the alternative: pivot the design to accommodate the data that actually exists.

lane1 owns the estimand math; lane2 owns novelty/positioning consequences. Coordinate; lane1 writes the memo.

Evaluate four pivot shapes, and for each state precisely: what it does to the primary estimand (rho_H correction + pi-hat), which SPEC results survive untouched (deletion-selection, prevalence, correction estimator), which die or weaken (the c-grid map, homogenization signature, boundary results), and identifiability cost:

P1. COUPLING AS ESTIMAND, NOT DESIGN FACTOR. Drop controlled generation entirely; take machine text from observational corpora and ESTIMATE per-item realized coupling from a trait-recovery model, with uncertainty propagated (errors-in-variables on c). lane3's audit3 shows realized c-hat is recoverable but noisy (r 0.11-0.24 against labels, trait model capped at AUC 0.53-0.64 on binary labels). Questions: does the mixture still identify rho_H and pi when c enters as a measured-with-error covariate per item instead of an experimental factor? What does the attenuation-on-c itself do to the correction? Does the c-grid "map" survive as a posterior over realized coupling rather than a designed grid?
P2. GENRE-MATCHED TRANSFORMS. Use confounded corpora but close the genre gap by transforming the HUMAN side (length-matching, truncation, style-normalization of PK essays to the machine pool's register) instead of generating genre-matched machine text. What does truncating/flattening the human base do to the trait signal (trait-from-text needs length) and to the validity story? Probably fatal - prove it or clear it.
P3. HYBRID MINIMUM. Corpus c=0 (best candidate from the wide hunt, if any clears) + the smallest possible conditioned batch (600-essay subsample, single family, 1,200 gens). The fallback shape, properly costed against P1.
P4. REFRAME THE PAPER. If controlled coupling is unaffordable at any price, what is the strongest paper that needs NO generation: prevalence + correction + deletion-selection on observational corpora, with the coupling story demoted from experimental factor to measured moderator? What is lost from the headline, honestly?

lane2's piece inside the same memo: does P1/P4 collide with or dodge the persona-conditioning literature (PersonaLLM, Big5-persona prompting work, Argyle-style silicon samples), and does the pivot strengthen or weaken the novelty position from your day-1 memo?

DELIVERABLE: derivations/design-pivot-memo.md with a recommendation matrix (estimand preserved / claims lost / cost / time-to-Layer-B) and a single recommended path. End with DONE-PIVOT-MEMO. This is analysis only - no generation, no code runs beyond what exists.
