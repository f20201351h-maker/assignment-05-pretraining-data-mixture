# Pretraining data mixture and curriculum for a 4T-token run

A data-mixture specification written for ERA V5 Session 5. It is my proposed recipe for a hypothetical "V5" pretraining run: how much of each kind of data, in what order, what is protected from the selector, and what is held back for the anneal.

Status: this is a specification. No proxy run has been done, so every share below is a hypothesis, and section 10 says how I would try to break it.

Numbers come from different places and I try to keep them apart. **C** means the course material states it (its lessons and dataset inventory). "V4" below is the previous model in the course's case study; its numbers are C. **V** means I checked it against the dataset card or the paper ([SOURCES.md](SOURCES.md) has the links). **D** is my design choice, **E** is my estimate, **H** is a hypothesis for the proxy runs. Token figures are in billions (B) or trillions (T) and are approximate everywhere; different sources count with different tokenizers.

## 1. The model and the budget

The target model is strong at coding and multi-step agentic work, reasoning whose depth can be dialled, native Indic ability as the differentiator, and enough general knowledge that the specialised lanes do not hollow it out.

The budget is given as 2.4T to 4T tokens. I plan at **4T** (D), because that is where supply problems show up. A share that works at 4T works at 2.4T; the reverse is not true.

| Phase | Tokens | Share | Basis |
|---|---|---|---|
| Main pretraining run | 3,840B | 96% | C: about 95% |
| Anneal (learning rate decayed to zero) | 120B | 3% | C: 1 to 5% |
| Post-training ceiling (SFT, reasoning training, preference) | 40B | 1% | C: under 1% each |

## 2. The mixture

Shares are of tokens the model actually trains on. The main-run column is the average over four stages (section 8); no single batch looks like it.

| Lane | Main run avg | Main tokens | Anneal | Anneal tokens | Benchmarks it is there for |
|---|---|---|---|---|---|
| General web | 49.7% | 1,908B | 22% | 26.4B | MMLU |
| Code | 26.4% | 1,014B | 23% | 27.6B | LiveCodeBench, Aider Polyglot, and the base for SWE-bench |
| STEM and math | 9.0% | 346B | 12% | 14.4B | GPQA Diamond, AIME |
| Indic | 10.0% | 384B | 20% | 24.0B | MILU, IndicGenBench |
| Long-context | 3.6% | 138B | 10% | 12.0B | RULER, LongBench v2 |
| Reasoning traces | 0.85% | 33B | 8% | 9.6B | AIME, GPQA, the effort dial |
| Agentic trajectories | 0.45% | 17B | 5% | 6.0B | SWE-bench Verified, Terminal-Bench, tau-bench, BFCL |
| Total | 100% | 3,840B | 100% | 120B | |

`python check_mixture.py` recomputes these numbers from [mixture.yaml](mixture.yaml) and fails if a column does not sum. Token figures are rounded to the nearest billion.

This is more web-heavy than the course's mixture-composer preset (web 34, code 24, Indic 16, STEM 12, reasoning 6, long-context 6, agentic 2). That preset is described as the mix around 70 to 80% of the way through the run, and my stage 3 and 4 mixes are close to it on web and code. They stay lower on Indic and reasoning, and the run average stays web-heavy, for a reason I did not expect when I started: at 4T, every lane except web hits a ceiling.

- **Code** stops at about 26% because of evidence, not supply. Aryabumi et al. (V) found 25% code best for natural-language reasoning, with world knowledge falling as the code share rises beyond that. The lane peaks at 34% in stage 3, but I did not want the run average far above the one published optimum.
- **STEM** is at 2.6 passes over the roughly 146B in the inventory (C). I could push it to 4 passes and 14%, but I would rather buy that with newly mined math text than with a fourth reading of the same papers.
- **Indic** is at 3.9 passes over the verified native pool (section 4).
- **Reasoning and agentic** are small because almost none of that data exists (section 5). The preset's 6% reasoning would be 230B tokens against about 7B of open traces.

Web takes what is left. That is exactly the pattern the course warns about, so I want to be plain about it: at 4T the extra budget beyond roughly 2.5T buys mostly more web. The alternative was to inflate the scarce lanes with repetition and synthetic text so the table looked more ambitious, and I think that is the worse failure.

The benchmark mapping follows the course's mixture composer, with two additions of mine. The course calls the long-context target only "long-eval"; I use RULER (synthetic retrieval and tracing tasks from 4K to 128K) and LongBench v2 (503 multiple-choice questions over real long documents) (V). And I add Terminal-Bench from the benchmark explainer, because working inside a real shell is the closest test of the tool-call-and-recover behaviour.

## 3. Supply

The repetition rule (C; Muennighoff et al., V) is that up to about 4 passes costs almost nothing and value is mostly gone by about 16. I treat 4 passes as a hard cap and the table shows how close each pool gets.

| Pool | Unique supply | Held back | Main-run demand | Passes | How the share is met |
|---|---|---|---|---|---|
| Web (DCLM-Baseline, FineWeb-Edu) | about 5T, overlapping (V) | 26B | 1,908B trained, 4.8T candidates at 40% keep | under 1 | Unique. The only lane with room for a selector |
| Code (Stack v2 train-full) | 775B (paper) or about 900B (card) (V) | 28B, plus 60B moved to long-context | 1,014B | 1.25 to 1.47 | Light repetition, no selector slack |
| STEM (peS2o, proof-pile-2, V4 D4) | 146B (C) | 14B | 346B | 2.6 | Repetition |
| Long-context | about 100B (C) | 12B | 138B | 1.6 | Repetition, or pack more |
| Indic A, verified native | 51.5B (V) | 10B | 160B | 3.9 | Repetition, at the cap |
| Indic B, unverified native | about 35B (E) | 0 | 88B | 2.5 | Repetition |
| Indic C, translated | 163B (V) | 0 | 116B | 0.7 | Exists; no new translation needed |
| Indic D, synthetic | 0.04B cleaned so far | 0 | 20B | n/a | **Generate about 5B** |
| Reasoning traces | about 7B (C) | 4B | 33B | n/a | **Generate about 5B**, then 4 passes |
| Agentic, multi-step | about 10B (E) | 0 | 17B | 1.7 | Open sets, mostly model-generated |
| Agentic, Tier A | 1 to 3B (E) | all of it | 0 | 0 | Reserved |

Four things in that table need saying out loud.

The selector only has room to work on web. V4 ran OPUS at about 40% keep (C). At that rate the web lane needs 4.8T of candidates, which is the whole of DCLM-Baseline plus FineWeb-Edu, so in practice candidates would also come from the wider FineWeb pool (18.5T, V). Code and STEM cannot afford to discard 60% of their candidates. For those lanes I rely on static cleaning (dedup, filtering, decontamination) and let the selector sit at keep 1.0.

Code supply has a dependency. The Stack v2 card holds file identifiers only; bulk content download needs an agreement with Software Heritage and INRIA (V). If that is not in place, the code share falls back to what V4's 199B code corpus (C) can carry.

The inventory's "AON (V4 corpus), 78B" row sits under Reasoning. The course describes the V4 always-on lane as Indic data plus benchmark training splits, so I do not count it as reasoning traces. Without it the reasoning lane's real supply is about 7B, not 85B.

Things I leave out: Samanantar (CC-BY-NC-4.0, V), Institutional Books (242B tokens, but non-commercial and no redistribution, V), NexusRaven (the only public data is a 1,070-row evaluation set, V), and every benchmark test split. IndicGenBench carries canary strings and asks never to be trained on (V).

## 4. The Indic lane

**10% of the main run, 384B tokens.** The split:

| Tier | Tokens | Share of Indic | Share of main run | Unique supply | Passes |
|---|---|---|---|---|---|
| A, verified native | 160B | 41.7% | 4.17% | 41.5B after the 10B reserve | 3.9 |
| B, unverified native | 88B | 22.9% | 2.29% | about 35B (E) | 2.5 |
| C, translated | 116B | 30.2% | 3.02% | 163B | under 1 |
| D, synthetic | 20B | 5.2% | 0.52% | must be generated | 4 over 5B |
| Total | 384B | 100% | 10.00% | | |

I sized this lane from the bottom up. The headline came last.

**Tier A** is Sangraha Verified. The inventory lists it as 64B, but the card's table shows that 12.8B of that is English, so the Indic-only figure is 51.5B (V). "Verified" means volunteers vetted the websites, not each document. I hold back the best 10B for the anneal and read the remaining 41.5B just under four times. That gives 160B, and it is the ceiling on trustworthy Indic text. Every other number in the lane follows from it.

**Tier B** is Sangraha Unverified (24.3B, perplexity-filtered documents from CulturaX and MADLAD-400) plus IndicCorp v2 (20.9B, CC0). I could not find a statement of how much these overlap, so 35B unique after deduplication is my estimate and the weakest number in this section. The risks are quality and a known filter bias: an English-tuned filter deletes Indic-script text first. This tier needs script-aware cleaning before it earns its 2.5 passes.

**Tier C** is what Sangraha calls "Synthetic", and the name is misleading. It is English Wikimedia machine-translated into 14 languages with IndicTrans2 (about 90B) and then transliterated into Roman script (about 72B) (V). I use the translated set once and about 26B of the romanised text, because people do type Indian languages in Roman script. The risk is translationese: one register, Wikipedia's, with English sentence structure underneath. A billion of these tokens is not worth a billion from Tier A, which is why the tier is capped at 30% even though its supply is the largest.

**Tier D** is model-written Indic text for shapes that do not exist natively: instruction following, short reasoning, tool use in Hindi or Telugu. My separate chat-data cleaning project produced 35.9M cleaned tokens of Anudesh (crowd-written prompts, Llama-2 responses). The lane needs about 5B unique. I kept it at 5% because generated text carries the generator's errors, and synthetic data helps at moderate doses.

Native text (A plus B) is 64.6% of the lane. That ratio is the thing I am protecting. I considered the composer's 16%. At 4T that is 614B, and with Tier A already at the cap the extra 230B could only be translated or generated, which would put native text below 45%. I do not think a model fed mostly IndicTrans2 output learns to write like a native speaker. The same 384B is 16.7% of a 2.4T run, so the preset is reasonable at the low end of the budget range. My rule is that Indic is fixed in tokens by the verified pool, and the percentage is whatever that comes to.

The aggregate split hides the per-language picture. Hindi has 12.6B verified tokens and Odia 1.2B (V). At the same pass count Odia gets about 4B native tokens, and nearly everything else it sees is translated. For the low-resource languages the lane is mostly Tier C, and the 41.7% headline is really a Hindi and Bengali number.

## 5. Agentic, reasoning and long-context

### Agentic

The behaviour is the one in the course's grant-search example: plan, call a tool, read the result, recover when a call fails, and keep the thread across many steps. The data shape that teaches it is a full trajectory with loss on the assistant's turns only. Tool observations are context. I count the lane in seen tokens, since that is what costs compute, but the supervised fraction is much smaller. The masking has one consequence for the main run: ordinary pretraining puts loss on every token, so this lane needs a per-token loss mask from the dataloader. If the data pipeline cannot carry one, the trajectories stay out of pretraining and wait for SFT.

Supply splits into two kinds, and the two-currency point (samples vs tokens) applies.

*One-shot function calling* is many samples and few tokens: Glaive v2 (113K samples, Apache-2.0), xLAM (60K, execution-verified, CC-BY-4.0, gated), ToolACE (11.3K; the inventory says 110K), Hermes (11.6K), ToolBench (126K instances over real APIs, with known stability problems) (V). Together that is about 0.25B tokens (E). It teaches the call format and nothing about recovery. After cleaning Glaive myself I trust it less: 38K of 112K conversations were exact or near duplicates.

*Multi-step trajectories* are where the tokens are. SWE-Gym has 2,438 tasks but only 491 trajectories that solved their task, at a mean of about 18.6K tokens each, so roughly 9M tokens (V). SWE-smith has 50K tasks and about 5K successful trajectories; its Hugging Face repo shows 76K rows because the same trajectories appear in three formats (V). Nebius released 80K SWE-agent trajectories of which 13.4K resolved the issue (V). Toucan has 1.5M tool-use trajectories run against real MCP servers (V). None of these cards states a token count. My estimate is 1 to 3B tokens that are both executed and outcome-checked, which I call Tier A, and on the order of 10B of unchecked or mixed-outcome multi-step data. Almost all of it was generated by another model, so the provenance is synthetic even when the execution is real.

Timing: nothing in stages 1 and 2, 0.5% in stage 3, 1.5% in stage 4, 5% of the anneal, then SFT. The main run uses the unchecked pool with known-failed trajectories removed. All of Tier A is held back for the anneal and reused in SFT. Synthetic generation is required for everything outside software engineering: browsing, the policy-following dialogues tau-bench tests, and anything in an Indian language. Benchmarks are SWE-bench Verified (500 human-validated issues, scored on hidden tests), Terminal-Bench, tau-bench and BFCL. SWE-Gym and SWE-smith were built from repositories outside SWE-bench, and that separation has to survive our own cleaning.

### Reasoning

The behaviour is a trace whose length follows the requested effort. The data shape is problem, trace, answer, and in pretraining it is an ordinary document with loss everywhere. Pretraining is not where a reasoning model gets made. The traces are taught after the base model exists, and the dial is finished later with verifiable-reward training. So the pretraining share is small on purpose. Its job is to make the format familiar.

Sources: OpenMathReasoning (3.2M chain-of-thought solutions to AoPS problems, CC-BY-4.0), OpenThoughts2 and 3 (about 1M and 1.2M traces across math, code and science, Apache-2.0), NuminaMath-CoT (860K, Apache-2.0), OpenR1-Math (225K, answers checked with Math-Verify, Apache-2.0) (V). The inventory puts these at about 7B tokens. The rows overlap, since OpenThoughts2 was built partly from OpenR1-Math. Every trace is model-written, and the pool is mostly math.

Demand is 33B in the main run and 9.6B in the anneal. With 4B held back, that needs about 5B of new unique traces at 4 passes, and those should be the code and general-reasoning traces the open sets lack, each with a checked answer. Section 9 gives the length bands. The held-back 4B is the long, verified end. Benchmarks are AIME and GPQA Diamond for the reasoning itself. The dial cannot be tested until post-training.

### Long-context

This lane is defined by format. A long-context sample is one coherent document trained in one piece. The point is that a 100K-token document cut into 4K windows is not long-context training. Batches have a single length, so the lane runs in its own 32,768-token batches, with about a tenth of its tokens in a 65K to 131K tail (D). Tokens in this lane are counted here only. The 60B of repo-packed code is subtracted from the code pool.

Supply is about 100B (C): repositories packed whole, and public-domain books. The book figure matches what I could verify: the book sources in Common Pile sum to about 40B (V).

It comes last in the main run. A model that cannot yet read gains nothing from a 32K window, and long sequences are the most expensive tokens in the run. Qwen3 is the one published staged recipe I checked, and it does the same: a final stage at sequence length 32,768 with 75% of the text between 16K and 32K tokens (V). There is a second reason for the timing. The agentic trajectories average about 18.6K tokens and run up to 81K in SWE-Gym (V), so they do not fit in an 8K window. The agentic share rises in the same stage. Held back: 12B of the best complete documents for the anneal. I would claim only the context length we trained at, plus whatever RULER shows beyond it.

## 6. The protected floor

OPUS scores a batch by how much its update helps a proxy built from benchmark material, and in V4 it looked at only the first 512 tokens of each sample (C). An English-heavy proxy undervalues Indic text. The first 512 tokens of an agent trajectory look like a log. V4 answered with an 8% always-on lane for Indic data and benchmark training splits. The course's V5 plan extends protection to Indic, agentic and reasoning, and I follow that.

Protected lanes go through the always-on channel and the selector never scores them, so for these lanes the share and the floor are the same number. The selector chooses within the rest.

| Stage | Indic | Reasoning | Agentic | Floor per batch |
|---|---|---|---|---|
| S1 | 10 | 0 | 0 | 10% |
| S2 | 10 | 0.5 | 0 | 10.5% |
| S3 | 10 | 1 | 0.5 | 11.5% |
| S4 | 10 | 2 | 1.5 | 13.5% |

Why 10 to 13.5% and not V4's 8%: V4's 8% covered one capability and V5 protects three. Why not the composer's 12% Indic floor: section 4. The floor only counts tokens in these three lanes, so nothing is counted twice. The long-context lane also bypasses the selector, for a mechanical reason: a 512-token prefix says little about a 32K document. I schedule it and do not count it in the floor. The anneal runs without the selector, since everything in it was chosen by hand.

The cost of the floor is that protected lanes get no dynamic quality filtering at all. Tier B Indic is the place that worries me.

## 7. The anneal reserve

120B tokens at the end, with the learning rate decayed to zero. OLMo 2 is the evidence that this is worth planning: mid-training on 50B-token mixes after a 3.9T main stage moved the 7B model's GSM8K score from 24.1 to 67.5 (V).

What is held out of the main run and first seen in the anneal:

| Reserve | Unique tokens | What it is | Why late |
|---|---|---|---|
| Indic Tier A | 10B | Best verified native text, balanced across languages more evenly than the pool | The last thing the model reads should be native text, not translation |
| Agentic Tier A | all, 1 to 3B (E) | Executed, outcome-checked trajectories | Scarce, and wasted on a model that cannot yet read code |
| Reasoning | 4B | Long traces with verified answers | The main run only needs the format |
| Code | 28B | Repositories with tests, commit and diff pairs | Edit-shaped code is what SWE-bench scores |
| Web | 26B | Top slice by quality score | Keeps general knowledge in the final mix |
| STEM | 14B | Textbook-grade and proof text | |
| Long-context | 12B | Complete books and whole repositories | |

The accounting rule: a reserved token is removed from the main-run pool before pass counts are computed, which is why section 4 uses 41.5B for Tier A and not 51.5B. Two exceptions are explicit. The anneal's 24B of Indic is 10B fresh Tier A, 10B replay of the best main-run Tier A, and 4B of Tier D replayed from the checked part of the generated pool. The 4B reasoning reserve is read about 2.4 times to fill 9.6B. Agentic Tier A is read about three times inside the anneal if the pool is 2B. If it turns out to be 1B, I would cut the anneal's agentic share to 3% and give the difference to code, not loop the same trajectories six times.

My anneal keeps 22% web where the composer's anneal preset has 8%. OLMo 2's mid-training mix was roughly half high-quality web (V), and I did not want to end the run on a mix that is four-fifths specialised without evidence that it is safe. Proxy H4 tests this.

## 8. Curriculum

| Stage | Main-run span | Seq. length | Web | Code | STEM | Indic | Reasoning | Agentic | Long-ctx |
|---|---|---|---|---|---|---|---|---|---|
| S1 Foundation | 0 to 20% | 4K | 70 | 14 | 6 | 10 | 0 | 0 | 0 |
| S2 Broaden | 20 to 50% | 4K | 55.5 | 26 | 8 | 10 | 0.5 | 0 | 0 |
| S3 Code and reasoning | 50 to 80% | 8K | 42.5 | 34 | 12 | 10 | 1 | 0.5 | 0 |
| S4 Long-context | 80 to 100% | 8K, plus 32K+ batches | 31.5 | 28 | 9 | 10 | 2 | 1.5 | 18 |
| Anneal | final 120B | same as S4 | 22 | 23 | 12 | 20 | 8 | 5 | 10 |

**S1** starts close to where V4 started (web about 70, code 13, protected 8; C), because that is the only run we have first-hand evidence from. The job is language and basic facts.

**S1 to S2, at 20%.** Code nearly doubles and the first short reasoning traces appear. By now the model can read; code adds exact structure and long dependencies, which is reported to help tasks that contain no code.

**S2 to S3, at 50%.** Code and STEM peak, the window goes to 8K, and agentic trajectories enter at 0.5%. This is the stage aimed at LiveCodeBench, GPQA and AIME. The window and the mixture should not change at the same step; I would move the window first.

**S3 to S4, at 80%.** The long-context lane switches on at 18% and agentic triples. Web, code and STEM all give up share to pay for it.

**S4 to anneal.** The reserve is released, Indic doubles to 20%, and the learning rate starts its decay.

Indic stays at 10% through the whole main run. That is deliberate. V4's 150x gradient-norm spike came from a sharp change in the Hindi share against frozen embeddings (C). Holding the lane flat means the only Indic step is the one into the anneal, where the learning rate is falling anyway.

No transition is a hard step. Each is a linear ramp centred on the boundary. V4 used a blend of about 3B tokens at each seam on a run of roughly 0.5T (C). Scaled to this run that is about 23B. I start from 30B, and the largest single move here (long-context from 0 to 18%) probably wants more. Both the 20/50/80 boundaries and the ramp width are hypotheses. The proxy can tune the ramp by watching gradient norm across a seam. It cannot tell me whether 50% is better than 45%, and I would not pretend otherwise.

## 9. Difficulty and reasoning-length bands

### Difficulty

I use the course's B0 to B5 difficulty ladder. What separates the bands is how much the reader must already hold and how many steps depend on each other. Length is not the criterion: a long recipe is B1 and a three-line proof can be B4.

| Band | What a document assumes | Math example | Code example |
|---|---|---|---|
| B0 Nursery | Nothing. Single clauses, concrete words | "Two apples and one apple make three apples." | `print("hello")` |
| B1 Grade school | Basic vocabulary, one-step inference | "Ravi has 12 mangoes and gives 5 to Meena. How many are left?" | Sum a list with a loop |
| B2 High school | Symbols, two or three chained steps | Solve x² − 5x + 6 = 0 | Binary search with the empty-list case handled |
| B3 Undergraduate | Definitions from a first course | Prove that √2 is irrational | Implement an LRU cache with O(1) operations |
| B4 Graduate | A specialist's working toolkit | Show that a continuous function on a compact set is uniformly continuous | Fix a race condition that spans two modules of a real repository |
| B5 Research | The current literature | A lemma from a recent arXiv paper, proof included | A merged pull request that changes a scheduler's invariants, with its review thread |

The same ladder applies in Indic text. A B0 Hindi line is "यह मेरा घर है।" (this is my house); a Class 8 science textbook chapter is B2.

Banding uses the usual recipe: a strong model labels a sample, a cheap classifier scores the rest, and source metadata (textbook grade, arXiv category, single file or whole repository) does most of the work for STEM and code.

The schedule shifts weight between bands; it never removes one. The question is how deep to go at each point, not which topics to withhold.

| Share of stage tokens (H) | B0 to B1 | B2 to B3 | B4 to B5 |
|---|---|---|---|
| S1 | 50 | 40 | 10 |
| S2 | 30 | 50 | 20 |
| S3 | 15 | 50 | 35 |
| S4 | 10 | 45 | 45 |
| Anneal | 0 | 40 | 60 |

In web, the selector already acts as a difficulty schedule, because a batch the model has mastered stops moving its weights. The explicit bands matter most in the protected lanes, where nothing else does the sorting.

### Reasoning length

Four bands, matching the low, medium, high, ultra effort tiers. The token thresholds are my choice. The upper bound of ultra is set by the data: the open trace sets cap generation at 16K to 32K tokens (V).

| Band | Trace length | What belongs here | Example |
|---|---|---|---|
| Low | under 64 tokens | One or two steps, answer almost direct | "What is 43 ÷ 17?" 17 × 2 = 34, 9 left over, about half of 17. About 2.5. |
| Medium | 64 to 512 | A few steps, each stated | "How many integers from 1 to 1000 are divisible by 3 or 5?" Count 333 and 200, subtract the 66 multiples of 15: 467. |
| High | 512 to 4K | Derive, then check a second way | The same count, verified in blocks of 15 and by complement. Or: a unit test fails on an empty input; trace the loop bounds, propose a fix, check it against three cases. |
| Ultra | 4K to 32K | Several approaches, at least one abandoned | An olympiad inequality where the first substitution fails. Or a bug whose first diagnosis is wrong and the trace has to back out of it. |

Both examples come from the course material.

Across the whole trace pool, reserve included, I want low 40%, medium 35%, high 20%, ultra 5% by sample count (D). By tokens that is about 1%, 9%, 36% and 54%: the two currencies again. A lane that is 5% ultra by samples spends more than half its tokens there.

Low and medium traces appear from S2. High joins in S3 and S4. Ultra traces never enter the main run. They sit in the 4B reserve with the verified high traces: the anneal reads mostly the high ones plus a small ultra share, and the rest of the ultra traces wait for post-training, since they are the raw material for the verifiable-reward stage and the open supply of them is thin.

One more requirement follows. If hard problems always come with long traces, the model learns that difficulty sets length and the dial does nothing. Part of the generated 5B therefore has to be the same problem solved at all four lengths, across math, code and general problems.

## 10. Proxy validation

Not yet run. I list what each experiment could prove wrong.

**Setup.** A 1B-parameter model on 20B tokens (20 tokens per parameter, the Chinchilla point), then a 3B model on 30B tokens for the decisions that are still contested. Architecture, tokenizer, optimiser schedule, total tokens and evaluation set stay fixed. Only the data recipe changes. The curriculum is compressed proportionally, so stage boundaries stay at 20, 50 and 80%.

Scarce pools have to shrink with the budget. At 20B tokens the Indic lane is 2B, and the full verified pool would cover it without a single repeat, so the proxy would never see the repetition the real run depends on. I subsample each pool so that pass counts match the full-scale plan.

The baseline runs with three seeds first. The spread across seeds is the noise floor. A difference counts only if it is larger than twice that spread.

**Metrics.** Primary: held-out loss per lane, on text from each lane that no arm trains on. Secondary, by log-likelihood or pass rate: MILU by language, MMLU, HumanEval, GSM8K, and RULER at 8K to 32K for the long-context arm. A model this size will score low on all of them, and that is acceptable. A proxy only has to rank recipes.

| | Question | Arms | I am wrong if |
|---|---|---|---|
| H1 | Is 10% Indic the right size? | 6%, 10%, 16%, with the 16% arm filled by Tier C | 16% beats 10% on MILU and held-out native loss while MMLU and HumanEval stay within noise (raise it). Or 6% matches 10% (lower it) |
| H2 | Are translated tokens worth less than native ones? | At a fixed 10%: native-heavy (65/35, mine) vs translated-heavy (35/65) | Translated-heavy matches on held-out native loss and on the MILU questions that are not translated from English (about three quarters of MILU, V). Then the tier cap is unnecessary |
| H3 | Does staging help? | My four stages vs the same lane totals as one flat mix | Flat is within noise everywhere. Then I keep only the long-context stage and the anneal |
| H4 | Does the reserve earn its place? | Reserve spent in the anneal vs the same data shuffled into the main run, with the same learning-rate decay on the ordinary mix | No gain on the scarce-lane metrics, or a loss on MMLU |
| H5 | Is 26% code right? | 18%, 26%, 35%, traded against web | 35% lifts HumanEval without MMLU falling (go higher). Or 18% matches 26% on code (give the tokens back) |
| H6 | Should long-context come late? | Last 20% vs spread evenly | Even spread matches on RULER and short-context loss |

**Guard rule.** A recipe that wins on its own lane is rejected if any other lane's held-out loss, or MMLU, gets worse by more than the noise floor. This is the check that a specialised gain did not come out of another capability.

**From 1B to 3B.** The baseline and the two closest calls go to 3B. If a ranking flips between sizes, I treat that decision as unresolved and do not let either proxy settle it. DCLM reports that results at small scale track results at 7B across data recipes, with a correlation of 0.84 from 400M-parameter runs and above 0.95 from 1B and 3B runs (V). That is good enough to trust clear wins. It is not good enough for narrow ones.

**Cost (E).** Using FLOPs ≈ 6 × parameters × tokens, a 1B run is about 1.2 × 10²⁰ FLOPs, or 75 to 96 H100-hours at 35 to 45% utilisation. A 3B run is 340 to 430. Eleven 1B runs and three 3B runs come to roughly 1,800 to 2,400 GPU-hours.

**What the proxies cannot test.** Agentic ability and long reasoning are post-training behaviours. A 1B pretraining proxy can show that the lanes lower held-out loss on trajectories and traces, and nothing more. The floor needs a working selector to test, and the selector is taught later. Until then the floor rests on V4's experience.

## 11. Cleaning, pointed at the starved lanes

The mixture shows three lanes with less clean supply than they need, and that is where cleaning effort should go next.

1. **Verified Indic, low-resource languages first.** Deduplicate Sangraha Unverified against IndicCorp v2 and against Sangraha Verified, so the Tier B estimate becomes a measurement. Use script-aware filters. Decontaminate against MILU and IndicGenBench.
2. **Multi-step agentic trajectories.** Collapse the SWE-smith formats to one copy, keep the resolved flag on Nebius and SWE-Gym, drop known-failed runs, and record which model generated each trajectory. That gives a real Tier A token count, the number I am least able to defend today.
3. **Reasoning traces.** Deduplicate across the OpenThoughts and OpenR1 sets, tag each trace with its length band, and keep answer-verified traces separate.

So far my chat-data cleaning pipeline has cleaned two shards: Glaive function-calling (55.9M tokens in, 40.6M out) and Anudesh (35.9M out). Both land in the low tiers of their lanes, one-shot agentic and Indic Tier D. That is 76.5M tokens, a small step towards the cumulative target. The course material does not state the gating threshold as a number, so I am not claiming it is met.

## 12. What I am least sure of

- **The Tier A agentic token count.** 1 to 3B is an estimate from row counts. The anneal's agentic share depends on it.
- **Tier B Indic overlap.** 35B unique could be 25B or 45B.
- **Tokenizer units.** Sangraha counts with its own tokenizer, peS2o in whitespace tokens, the Stack v2 with StarCoder2's. Our tokenizer will move every one of these, Indic most.
- **The stage boundaries.** 20, 50 and 80% are reasoned, not measured.
- **Whether 4T is the right budget for this supply.** The specialised lanes do not grow with the budget. In a 2.4T run, keeping the same tokens for Indic, STEM, long-context, reasoning and agentic, and holding code at 26%, gives web about 34% and Indic about 17%. That is close to the composer preset, so the preset is roughly this plan at the low end of the range. If the proxies show web past roughly 1T adding little, the honest recommendation is the smaller run.

## Files

- [mixture.yaml](mixture.yaml): the recipe in machine-readable form.
- [check_mixture.py](check_mixture.py): reconciles the shares, tier split, reserve and pass counts, and prints the tables above. Needs Python with PyYAML.
- [SOURCES.md](SOURCES.md): where each external number comes from, and where sources disagree.

Every number can be traced through the files above.
