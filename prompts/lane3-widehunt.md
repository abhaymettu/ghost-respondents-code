GHOST PROJECT - LANE 3 - WIDE CORPUS HUNT (after the M4 addendum)

User steering 6:30pm: widen the hunt beyond the three c=0 candidates that flunked the genre audit. Finish the M4 addendum first (already in your queue), then run a systematic sweep for genre-matched machine-text corpora.

TARGET PROFILE: machine-written personal-narrative / stream-of-consciousness / diary / journal / self-reflection text (the Pennebaker-King genre). Trait-labeled is a bonus, not a requirement (c=0 does not need labels). Minimum usable pool ~700 texts. Public license. Any generator.

LEADS TO CHECK (score each, add your own): HuggingFace dataset search for LLM/GPT + diary/journal/personal-narrative/reflection/memoir; PersonaLLM project outputs; humanlab/psychadapter artifacts; OUTFOX, MGTD, DeepfakeTextDetect, HART, LLM-DetectAIve and other detection corpora - enumerate their DOMAINS and score only the personal-narrative ones (skip news/wiki/reviews/QA outright, we know those fail); Reddit-style first-person narrative subsets (note: HC3 ELI5 is QA-framed, likely fails, but check whether any subset is diary-style); LLM-generated college-admissions/personal-statement corpora (qsardor/viorra-admissions-essays and kin); any synthetic-diary or synthetic-journal sets.

SCORING (same machinery as audit2): for each candidate with a downloadably public pool, run PK-human vs machine-pool separability on your detector path and report AUC against the 0.472 same-genre benchmark. Candidates you cannot download get desk-rejected with the reason (paywalled, key-gated, gone).

DELIVERABLE: append "Wide hunt" section to lane3-testbed/CORPUS-AUDIT.md: a scored table (pool, n, genre description, AUC, delta vs benchmark, license, verdict), the best candidate(s) named explicitly, and a bottom line: does any existing corpus clear the genre bar for c=0 (and/or supply a bigger conditioned pool), yes/no + which. End with HUNT-DONE. No generation, no cost, no API keys.
