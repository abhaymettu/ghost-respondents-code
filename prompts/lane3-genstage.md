GHOST PROJECT - LANE 3 - COUNTERPART GENERATION: STAGE, DO NOT FIRE

The ~15k-generation counterpart batch (SPEC 2.3) is approved in principle; the burn report went to Abhay at 2:55pm (Sonnet-class frontier ~$105, API-served open-weight <$10, full 14,874 generations). It fires tonight unless he objects. Your job now is staging only:

1. Write lane3-testbed/generate_counterparts.py: for each essay prompt, three coupling levels (c = 0: prompt only; c partial: prompt + coarse persona trait-band sketch, NOT exact scores; c high: prompt + actual trait scores), two model families (frontier proprietary: claude API, Sonnet-class; open-weight: an API-served open model, e.g. Llama-class via a cheap provider). Frozen generation parameters + seeds in lane3-testbed/GEN-CONFIG.md. Output layout: one JSONL per family x coupling with essay id, prompt hash, response, model, seed, timestamp.
2. A --dry-run mode that runs 10 generations per family x coupling (60 total, under $1) and writes GEN-DRYRUN.md with measured tokens in/out, cost extrapolation against the 14,874 total, and quality eyeball notes.
3. DO NOT run anything but the dry run. The full batch fires on my explicit go, tonight, after the dry-run cost check and Abhay's no-objection window.
4. If the essays trait data blocks c-high conditioning (binary labels only, IEEE login pending), say exactly what c-high can and cannot be with local data in GEN-CONFIG.md and flag it - do not invent scores.

API keys: use whatever claude/anthropic key setup already exists on this machine (check env and ~/.config first; never print a key, never write one into the repo). If no key exists for either family, stop and report which is missing. End with GEN-STAGED when scripts + config + dry run are in place, or GEN-BLOCKED with the reason.
