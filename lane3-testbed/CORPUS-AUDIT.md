# Corpus-first audit — Day 2, evening pass

Approved 2026-09-07 18:06 CDT: replace the shelved 15k-generation batch (`generate_counterparts.py`, `GEN-CONFIG.md`) with existing corpora wherever they hold up. No API keys, no cost, no generation ran tonight — three audits only. Code: `audit2_genre_confound.py`, `audit3_trait_recoverability.py`; raw results in `audit2_results.json`, `audit3_results.json`; downloaded data under `data/big5_personality_essays/`, `data/argugpt/`, `data/ghostbuster/`, `data/student_llm/`.

**Scope note**: M4 benchmark's essay-domain subset was checked and does not exist — see the Audit 2 addendum below. M4's 12 domains are academic/encyclopedic/news/forum/peer-review text, none of them an essay or free-writing genre.

## Audit 1 — Big5PersonalityEssays viability

Source: `github.com/stnflri/Big5PersonalityEssays`, file `Brief-State-of-Consciousness-Essays.xlsx`, downloaded and parsed with openpyxl into `data/big5_personality_essays/essays.xlsx`.

| property | value |
|---|---|
| usable rows (text + all 5 labels populated) | **399** |
| generator | GPT-4-turbo (per repo description) |
| label format | binary (0.0/1.0) per FFM trait — same encoding as the local PK mirror |
| unconditioned/c=0 arm | not located — repo page and arXiv abstract (2407.17586) don't describe one, all 399 rows carry full label sets with no null/baseline rows visible. Treat as "not found," not "confirmed absent" — the arXiv PDF itself couldn't be parsed (binary fetch failure) |
| license | CC BY 4.0, per the arXiv abstract page's license badge. No standalone LICENSE file was found in the repo itself |
| length vs PK | Big5-machine: mean 100.4 words, median 92, sd 36.8, range 50–318 (n=399). PK: mean 652.1, median 626, sd 253.9, range 33–2500 (n=2,467). **Big5 essays are ~6.5x shorter than PK.** |

**Verdict: fails viability on two independent grounds** — 399 < the 700-usable-essay threshold, and even a row-count fix wouldn't close the 6.5x length gap, which is itself a confound for anything downstream (detector features, trait signal) that's sensitive to text length. → **fallback A** condition triggered.

## Audit 2 — genre confound on c=0 candidates

Detector: `openai-community/roberta-base-openai-detector`, zero-shot, same scoring path as Day 2's `detector/calibration.py` (`run_roberta_scores`). Each pairing: 500 PK-human vs up to 500 machine texts from the pool (or the full pool if smaller), AUC via `sklearn.metrics.roc_curve`/`auc`.

| pool | n in pool | n used | AUC | Δ from benchmark |
|---|---|---|---|---|
| Big5PersonalityEssays-machine vs PK-human (**same-genre benchmark**) | 399 | 399 | **0.472** | — |
| ArguGPT machine (argumentative exam essays) | 3,338 | 500 | **0.982** | +0.509 |
| Ghostbuster `gpt_writing` split (student-essay prompts) | 694 | 500 | **0.644** | +0.171 |
| `knarasi1/student_and_llm_essays`, LLM-labeled | 2,078 | 500 | **0.601** | +0.129 |
| M4 essay domain | **does not exist** — see addendum below | — | — | — |

Benchmark AUC of 0.472 is effectively chance — the detector barely separates PK-human from Big5-machine text on this genre, which is the expected result for a genuinely same-genre pairing. All three tested candidates sit far above that: **AUC rises with how differently the source task is framed relative to PK's free stream-of-consciousness prompt** — ArguGPT (structured argumentative-exam essays) is worst, Ghostbuster's `gpt_writing` split (structured student-essay prompts) next, `student_llm_essays` least bad but still clearly separable above the benchmark.

**Ranking by distance from benchmark (worst confound first)**: ArguGPT (+0.509) > Ghostbuster gpt_writing (+0.171) > student_llm_essays (+0.129).

**Verdict: all three tested candidates carry a genre confound** — none is usable as-is for a clean c=0 baseline; the detector is picking up genre/task-framing differences, not (or not only) machine-vs-human authorship. → **fallback B** condition triggered for all three. M4 remains unscored and shouldn't be assumed to fail the same way without checking it.

## Audit 2 addendum — M4

**Checked whether M4 has an essay-genre domain. It does not.**

Confirmed two independent ways: (1) `gh api repos/mbzuai-nlp/M4/contents/data` — raw file listing of the actual repo, not a summarized description — returns 12 domain-named JSONL files (`<domain>_<generator>.jsonl`): `arabic`, `arxiv`, `bulgarian_true_and_fake_news`, `germanwikipedia`, `id-newspaper` (Indonesian), `peerread`, `qazh` (Kazakh), `reddit`, `russian`, `urdu`, `wikihow`, `wikipedia`. No file or subdirectory is named `essay` or matches an essay/free-writing genre. (2) The repo's own README (`gh api repos/mbzuai-nlp/M4/contents/README.md`) describes the dataset's scope directly: domains are academic (arXiv), encyclopedic (Wikipedia), instructional (WikiHow), forum-QA (Reddit-ELI5), peer-review (PeerRead), and news (several languages) — the paper's own framing never mentions essays or personal/reflective writing as a covered domain. M4 was built for cross-domain/cross-generator/cross-lingual *detector* generalization studies, not to include a stream-of-consciousness or argumentative-essay genre.

Nearest domains by surface resemblance — `peerread` (structured academic peer-review prose) and `reddit` (ELI5-style forum Q&A, same source HC3 already draws from) — are both genre mismatches at least as large as ArguGPT/Ghostbuster/student_llm_essays already tested in Audit 2, and `reddit` specifically overlaps with data already used for detector calibration (HC3), which would make any AUC there uninformative as a fresh test. **Not scoring either as a stand-in c=0 candidate**: doing so and reporting an AUC number under the heading "M4 essay domain" would misrepresent what was measured — these domains aren't essays, and a large AUC gap for a domain that's structurally nothing like PK's writing task doesn't test the same hypothesis as the other three candidates (which are at least essay/writing-prompt genres). No genre-confound AUC was run for M4.

**Generator-axis note (informational, not scored)**: M4's generators — `chatGPT`/`chatgpt`, `davinci`, `bloomz`, `cohere`, `dolly`/`dolly2`, `flant5`, and `llama` (the last only on `peerread`) — span a wider range of model families (Cohere, BLOOM-Z, Dolly, FLAN-T5, LLaMA, in addition to OpenAI's ChatGPT/davinci) than the three already-tested c=0 candidates. Audit 2's original three candidates weren't checked per-candidate for exact generator identity, so this is a directional note only, not a quantified "M4 adds N new generators" claim — flagging as unverified rather than asserting a specific count.

**Effect on ranking and verdict**: none. The c=0 candidate ranking (student_llm_essays best of tested, ArguGPT worst) is unchanged — M4 was never entered into it, not scored as a fourth ranked entry. **Fallback B is not cleared or reduced by this addendum** — no candidate has come in within ~0.05 of the 0.472 benchmark, and M4 contributes no new evidence either way since it wasn't a same-genre test.

## Wide hunt — genre-matched machine-text corpora beyond the original three

Steered 2026-09-07 18:30 CDT: widen the search past ArguGPT/Ghostbuster/student_llm_essays/M4, specifically hunting for machine-generated **personal-narrative / stream-of-consciousness / diary / journal / self-reflection** text — PK's actual genre — rather than any structured-essay or QA/news/wiki genre already known to fail.

**Search process**: HuggingFace dataset search (`diary`, `journal LLM`, `synthetic diary`, `personal statement`, `admissions essay`, `stream of consciousness`, etc. — no hits for most multi-word queries, HF's search is exact-ish rather than semantic), GitHub repo search for named detection-corpus suites (OUTFOX, MGTBench, LLM-DetectAIve, DeepfakeTextDetection), and the two named leads (PersonaLLM, `humanlab/psychadapter`). Every "domain list" claim below is from a raw `gh api contents/` file listing or the repo's own README fetched directly — same standard as the M4 addendum, not a summarized description.

**Desk-rejected without scoring** (genre mismatch or no downloadable corpus):

| candidate | why rejected |
|---|---|
| `did3m/darcy_diary_10000` (HF, 10,000 rows, no license listed) | Templated pseudo-1811 diary snippets, mean 22.7 words/entry (30x shorter than PK's 652), same short verbatim phrases recur across entries ("I find myself tortured by sentiments I dare not speak aloud") — degenerate/templated generation, not comparable prose even setting genre aside |
| `qsardor/viorra-admissions-essays` (128 rows), `Atharva1244/college_essays` (85 rows), `Ayesha490/personalstatement` (48 rows, instruction-tuning Q&A format, not essays) | All three are **human-authored** admissions essays (sourced from real published examples, e.g. Johns Hopkins Admissions Blog) or a mentor-advice chat dataset, not LLM-generated text at all; also all far below the 700-usable threshold |
| OUTFOX (`ryuryukke/OUTFOX`, 15,400 LLM-generated essays, ChatGPT/GPT-3.5/FLAN-T5-XXL, MIT-adjacent license per repo) | Confirmed via repo README: built on Kaggle Feedback Prize, argumentative/persuasive essays responding to essay problem statements, grades 6-12 — same structured-argumentative genre as ArguGPT, which already scored AUC 0.982. Large and clean, but not personal-narrative; skipped rather than scored to avoid restating a known failure mode under a new name |
| MGTBench `Essay` domain (`xinleihe/MGTBench`) | Confirmed via README: sourced from Verma et al. (Ghostbuster) — the same underlying student-essay domain already scored in Audit 2 (AUC 0.644) under `polsci/ghostbuster-essay-cleaned`. MGTBench's `WP` domain is Ghostbuster's creative-writing (WritingPrompts-style fiction) split, `Reuters` is news — neither is personal-narrative. No new data here |
| LLM-DetectAIve (`mbzuai-nlp/LLM-DetectAIve`) | Same MBZUAI group as M4; repo is pipeline/code only (no `data/` folder in the GitHub repo), and the paper's own abstract frames its scope as "education, academia" domains — no personal-narrative subset indicated, and no dataset artifact found on HF under a matching name |
| `humanlab/psychadapter` | Code-only repo (train/inference scripts for a GPT-2 persona adapter) — no released generated-text corpus to download |
| HC3 subsets (all 5, including `reddit_eli5`) | Verified directly: every HC3 record is `{question, human_answers, chatgpt_answers}` — strictly QA-framed, including the Reddit-ELI5 subset. No diary/personal-narrative-style subset exists inside HC3 |
| M4GT-Bench / SemEval2024-task8 | Not investigated further this pass — these are extensions of M4 itself (same MBZUAI authors, explicitly named in M4's README as "further extended" for SemEval 2024 shared task 8); given M4's own domain list has no essay/personal-narrative genre and these are described as adding "surprising generators, domains and languages" on the same base, treated as low-probability for a genre M4 never had, not chased down given the leads that did pan out |

**Scored**: one genuinely new, genre-relevant candidate surfaced — **PersonaLLM** (`hjian42/PersonaLLM`, MIT license, EACL/NAACL-Findings 2024, MIT Media Lab / MIT CCC / Stanford). It generates first-person narrative text from BFI-persona-conditioned LLMs (32 persona types × 10 samples each, 320 stories per model) across three model families (GPT-4-0613, GPT-3.5-turbo-0613, Llama-2). Sample text confirmed by direct read: first-person, reflective-toned narrative prose (a workplace-mentorship story), structurally closer to PK's free-writing register than any structured-essay/QA/news genre tested so far — worth an actual AUC check rather than a desk-reject.

Scored with `audit_widehunt.py` (same `run_roberta_scores`/`roc_curve`/`auc` path as Audit 2), PK-human sampled fresh per pool at matched n, same 500-cap convention:

| pool | n in pool | n used | genre description | AUC | Δ from 0.472 benchmark | license | verdict |
|---|---|---|---|---|---|---|---|
| PersonaLLM — GPT-4-0613 | 320 | 320 | BFI-persona-conditioned first-person narrative story | **0.836** | +0.364 | MIT | genre-confound |
| PersonaLLM — GPT-3.5-turbo-0613 | 320 | 320 | same | **0.777** | +0.305 | MIT | genre-confound |
| PersonaLLM — Llama-2 | 320 | 320 | same | **0.945** | +0.473 | MIT | genre-confound |
| PersonaLLM — combined (all 3 models) | 960 | 500 | same | **0.859** | +0.387 | MIT | genre-confound |

**Best candidate(s)**: none of the wide-hunt leads clears or approaches the benchmark. PersonaLLM's own genre resemblance to PK (first-person, reflective) did not translate into a lower confound — its AUCs (0.78–0.95) sit *worse* than two of the three original candidates (student_llm_essays 0.601, Ghostbuster gpt_writing 0.644) and close to ArguGPT's 0.982. Plausible reason, not confirmed by further testing here: PersonaLLM's prompt was explicit creative-writing ("write a story"), producing plotted, resolution-arc narrative fiction (workplace conflict, dialogue, a tidy ending) rather than PK's unstructured, unedited stream-of-consciousness — so despite sharing a first-person voice, it's a different writing task, and the detector separates on that. **`knarasi1/student_and_llm_essays` (AUC 0.601, tested in Audit 2) remains the best candidate found across both audits**, and it does not supply a genre-matched or larger conditioned-arm pool either (2,078 pool, essay genre, not personal-narrative, and unlabeled for traits).

**Bottom line: no.** No existing public corpus found in this hunt clears the genre bar for c=0 (all AUCs land between +0.13 and +0.51 above the 0.472 benchmark), and none supplies a bigger *usable* conditioned-arm pool than Big5PersonalityEssays' 399 (PersonaLLM's 960 combined is bigger by count but isn't a conditioned-arm candidate in the trait-recoverability sense used in Audit 3 — it's persona-conditioned generation for a different research question, and its per-file naming encodes coarse trait bands rather than exact scores, but more importantly its extreme genre confound as measured here means the same-genre assumption Audit 1/3 relied on for Big5PersonalityEssays doesn't hold for it). Fallback B's 750–1,500-generation residual stands as the final number — the wide hunt does not change it.

## Audit 3 — trait recoverability / realized coupling c-hat

Ran despite Audit 1's nonviability for direct reuse — 399 essays is still a usable diagnostic sample for measuring realized coupling, just not enough to serve as the actual conditioned-arm corpus.

**Method**: `sentence-transformers/all-MiniLM-L6-v2` embeddings (384-d) → `RidgeClassifier(alpha=1.0)`, one model per FFM dimension, trained on PK's binary median-split labels (only trait data the local mirror has — see `CALIBRATION-REPORT.md`; continuous BFI scores remain blocked behind the IEEE DataPort login). 75/25 PK train/held-out split for a sanity check, then refit on 100% of PK (n=2,467) for the actual Big5 application. c-hat = point-biserial r between the ridge decision score on Big5-machine essays (n=399) and Big5's own stated binary label, per dimension.

| trait | PK held-out sanity AUC | c-hat (r) | p |
|---|---|---|---|
| cEXT | 0.639 | **0.241** | <0.0001 |
| cAGR | 0.572 | 0.142 | 0.0046 |
| cCON | 0.528 | 0.123 | 0.0139 |
| cNEU | 0.551 | 0.106 | 0.0342 |
| cOPN | 0.629 | −0.029 | 0.557 (n.s.) |

PK held-out sanity AUCs (0.53–0.64) are weak-but-above-chance across the board — trait-from-text prediction is hard even in-domain, which caps how strong c-hat could plausibly look regardless of the corpus. Realized c-hat on Big5PersonalityEssays is modest for 4/5 traits (r ≈ 0.11–0.24) and statistically indistinguishable from zero for openness. **Even setting aside Audit 1's size/length problems, this corpus's realized conditioning is far from "high" coupling** — a c-high label in this dataset does not currently buy strong recoverable trait signal by this measure.

## c=0 candidate ranking (summary)

1. `knarasi1/student_and_llm_essays` — least-bad genre confound (AUC 0.601, +0.129 over benchmark), largest usable pool (2,078)
2. `polsci/ghostbuster-essay-cleaned` (`gpt_writing` split) — moderate confound (AUC 0.644, +0.171), pool 694
3. `ArguGPT` — worst confound by far (AUC 0.982, +0.509), pool 3,338 but task-framing mismatch dominates
4. M4 essay domain — **does not exist** (checked, not skipped); not a candidate

## VERDICT: FALLBACK-AB

Both arms need generation. Residual counts, using the ranges from the corpus-first design brief:

- **Conditioned cells (partial + high) — fallback A**: Big5PersonalityEssays is undersized (399 vs 700 threshold) and length-mismatched (6.5x shorter than PK) for direct reuse, and even its usable subset shows only modest realized coupling (Audit 3). Generate the planned 600-essay conditioned cells × 2 coupling levels (partial, high) = **1,200 generations at 1 model family, 2,400 at 2 model families**.
- **Unconditioned cells (c=0) — fallback B**: all three tested candidate pools carry a genre confound relative to the same-genre benchmark; none is usable as-is. Generate **750–1,500 genre-matched c=0 essays** (single coupling level, so no partial/high multiplier; family-count multiplier still applies if both frontier and open-weight families are wanted at c=0).

**Combined residual generation range: ~1,950–3,900 generations** (1,200–2,400 conditioned + 750–1,500 unconditioned), against the shelved batch's 14,874 — roughly a **74–87% reduction** in generation volume from the corpus-first approach, even though neither arm reached GO-ZERO. Before firing fallback A: revisit whether Big5PersonalityEssays' 399 essays are worth using as a *supplementary* conditioned-arm source rather than a replacement, given the modest-but-nonzero c-hat signal — that could shrink fallback A's count below 600 if partial credit is acceptable to lane 1. Fallback B's count is now final as far as corpus audits go — M4 was the last untested c=0 candidate, it has no essay domain, and no further public-corpus search is planned before firing fallback B's 750–1,500 generations.

AUDIT-DONE

AUDIT-M4-DONE

HUNT-DONE
