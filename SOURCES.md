# Sources

Where the external numbers in the README come from. Course numbers (lessons, dataset inventory and mixture composer) are not repeated here.

The dataset cards and papers were opened in October 2026. Most were read through a fetch tool that summarises the page, so a figure quoted here is the figure the page gave at that time, to the precision shown. Where two sources disagree, both are listed.

## Indic

| Claim | Source |
|---|---|
| Sangraha: Verified 64.3B, Unverified 24.3B, Synthetic 162.7B, total 251.3B tokens; CC-BY-4.0 | https://huggingface.co/datasets/ai4bharat/sangraha |
| Verified includes 12.8B English tokens, so Indic-only verified is about 51.5B | Same card, per-language table; the subtraction is mine |
| Per-language verified tokens: Hindi 12.6B, Bengali 10.6B, Tamil 4.0B, Telugu 3.7B, Marathi 2.8B, Odia 1.2B | Same card |
| "Verified" is site-level vetting by volunteers; Unverified is perplexity-filtered CulturaX and MADLAD-400; Synthetic is IndicTrans2 translation of English Wikimedia into 14 languages (about 90B) plus romanisation (about 72B); counts use the authors' own tokenizer | IndicLLMSuite paper, https://arxiv.org/abs/2403.06350 |
| IndicCorp v2: 20.9B tokens, 24 languages, CC0 | https://arxiv.org/abs/2212.05409 , https://huggingface.co/datasets/ai4bharat/IndicCorpV2 |
| Samanantar is CC-BY-NC-4.0 | https://huggingface.co/datasets/ai4bharat/samanantar |
| MILU: about 80K multiple-choice questions, 11 languages (10 Indic plus English), about a quarter translated from English, gated | https://arxiv.org/abs/2411.02538 , https://huggingface.co/datasets/ai4bharat/MILU |
| IndicGenBench: 29 languages; repository carries canary strings | https://arxiv.org/abs/2404.16816 , https://github.com/google-research-datasets/indic-gen-bench |
| Anudesh: crowd-sourced prompts with Llama-2-70B responses | https://huggingface.co/datasets/ai4bharat/indic-align |

Not found: any statement of how much Sangraha overlaps IndicCorp v2. The 35B unique figure for Tier B is my estimate.

## Web, code, STEM, long documents

| Claim | Source |
|---|---|
| DCLM-Baseline: 4T tokens (card), 3.8T (paper), 3.71T as counted by OLMo 2; CC-BY-4.0 | https://huggingface.co/datasets/mlfoundations/dclm-baseline-1.0 , https://arxiv.org/abs/2406.11794 |
| FineWeb-Edu 1.3T tokens; FineWeb now more than 18.5T (15T at release); ODC-By | https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu , https://huggingface.co/datasets/HuggingFaceFW/fineweb |
| The Stack v2: card gives about 900B tokens for train-full; the StarCoder2 paper gives 775B for train-full alone, and its 900B+ figure is the whole StarCoder2 training set including extras such as pull requests and notebooks. No single licence (permissive or unlicensed files). Card holds identifiers only; bulk download needs an agreement with Software Heritage and INRIA | https://huggingface.co/datasets/bigcode/the-stack-v2 , https://arxiv.org/abs/2402.19173 |
| peS2o v2: 39M papers, 42B whitespace tokens, ODC-By | https://huggingface.co/datasets/allenai/peS2o |
| Proof-Pile-2: 55B tokens (arXiv 29B, OpenWebMath 15B, AlgebraicStack 11B); component licences apply | https://huggingface.co/datasets/EleutherAI/proof-pile-2 |
| Common Pile book sources: pre-1929 books 12.4B, Library of Congress 9.5B, Biodiversity Heritage Library 9.8B, Project Gutenberg 5.7B, DOAB 3.0B | https://huggingface.co/datasets/common-pile/comma_v0.1_training_dataset , https://arxiv.org/abs/2506.05209 |
| Institutional Books 1.0: 242B tokens; non-commercial, no redistribution | https://huggingface.co/datasets/institutional/institutional-books-1.0 |

## Agentic

| Claim | Source |
|---|---|
| Glaive function-calling v2: 112,960 rows, Apache-2.0 | https://huggingface.co/datasets/glaiveai/glaive-function-calling-v2 |
| xLAM function-calling 60K: execution-verified, CC-BY-4.0, gated | https://huggingface.co/datasets/Salesforce/xlam-function-calling-60k |
| ToolACE: 11,300 rows (the course inventory lists 110K), Apache-2.0 | https://huggingface.co/datasets/Team-ACE/ToolACE |
| Hermes function-calling v1: about 11.6K rows, Apache-2.0 | https://huggingface.co/datasets/NousResearch/hermes-function-calling-v1 |
| ToolBench: 126,486 instances over 16,464 real APIs; stability problems reported by StableToolBench | https://github.com/OpenBMB/ToolBench , https://arxiv.org/abs/2403.07714 |
| NexusRaven: no training set released; the public data is a 1,070-row evaluation set, CC-BY-NC-4.0 | https://huggingface.co/datasets/Nexusflow/NexusRaven_API_evaluation |
| SWE-Gym: 2,438 task instances; 491 successful trajectories used for training; mean 18,578 tokens per trajectory, range 2,560 to 81,245 | https://arxiv.org/abs/2412.21139 |
| SWE-smith: about 50K task instances from 128 repositories; about 5K successful trajectories used for training; the trajectories repository has 76K rows across three formats; MIT | https://arxiv.org/abs/2504.21798 , https://huggingface.co/datasets/SWE-bench/SWE-smith-trajectories |
| Nebius SWE-agent trajectories: 80,036 trajectories, 13,389 resolved; CC-BY-4.0 | https://huggingface.co/datasets/nebius/SWE-agent-trajectories |
| Toucan: about 1.5M trajectories from 495 real MCP servers. Licence differs between paper (CC-BY-4.0) and card (Apache-2.0) | https://arxiv.org/abs/2510.01179 , https://huggingface.co/datasets/Agent-Ark/Toucan-1.5M |

None of these cards states a token count. The 9M figure for SWE-Gym is 491 × 18,578. The Tier A range of 1 to 3B and the 10B multi-step figure are my estimates from row counts and file sizes.

## Reasoning

| Claim | Source |
|---|---|
| OpenMathReasoning: 3.2M chain-of-thought solutions, AoPS problems, CC-BY-4.0; 16,384-token generation cap | https://huggingface.co/datasets/nvidia/OpenMathReasoning |
| OpenThoughts2-1M and OpenThoughts3-1.2M: Apache-2.0; OpenThoughts3 generated with a 32,768-token cap; OpenThoughts2 draws on OpenR1-Math | https://huggingface.co/datasets/open-thoughts/OpenThoughts2-1M , https://huggingface.co/datasets/open-thoughts/OpenThoughts3-1.2M |
| NuminaMath-CoT: 859,594 rows, Apache-2.0 | https://huggingface.co/datasets/AI-MO/NuminaMath-CoT |
| OpenR1-Math-220k: about 225K problems, DeepSeek-R1 traces checked with Math-Verify, 16K-token cap, Apache-2.0 | https://huggingface.co/datasets/open-r1/OpenR1-Math-220k |

## Methods

| Claim | Source |
|---|---|
| Up to 4 epochs of repeated data changes loss negligibly; returns diminish fast beyond about 16 | Muennighoff et al., https://arxiv.org/abs/2305.16264 |
| 25% code is best for natural-language reasoning; world knowledge falls as the code share rises | Aryabumi et al., https://arxiv.org/abs/2408.10914 |
| OLMo 2: 3.9T stage 1; mid-training mixes of 50B to 300B with the learning rate decayed linearly to zero; about half of each mix is high-quality web; GSM8K 24.1 to 67.5 for the 7B model | https://arxiv.org/abs/2501.00656 , https://huggingface.co/datasets/allenai/dolmino-mix-1124 |
| Qwen3: general stage at sequence length 4,096, a reasoning stage, then a long-context stage at 32,768 with 75% of text between 16,384 and 32,768 tokens | https://arxiv.org/abs/2505.09388 |
| OPUS: 4.7% compute overhead; the paper's own selection ratio is 50%. The 40% keep and sixfold figures in the README are the course's V4 numbers | https://arxiv.org/abs/2602.05400 |
| Results at small scale correlate with 7B results across data recipes: Pearson r = 0.838 from 400M runs, 0.956 from 1B, 0.982 from 3B | DCLM, https://arxiv.org/abs/2406.11794 |

## Benchmarks

| Claim | Source |
|---|---|
| SWE-bench Verified: 500 human-validated instances | https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified |
| Terminal-Bench 2.0: 89 tasks | https://arxiv.org/abs/2601.11868 |
| tau-bench: retail and airline domains, scored on final database state, pass^k | https://arxiv.org/abs/2406.12045 |
| Aider Polyglot: 225 Exercism exercises in six languages | https://aider.chat/docs/leaderboards/ |
| GPQA Diamond: 198 questions | https://arxiv.org/abs/2311.12022 |
| RULER: 13 synthetic tasks from 4K to 128K | https://arxiv.org/abs/2404.06654 |
| LongBench v2: 503 multiple-choice questions, 8K to 2M words | https://arxiv.org/abs/2412.15204 |

## My earlier cleaning work

Cleaning figures (Glaive 55.9M tokens in and 40.6M out; Anudesh 35.9M out; 9,173 exact and 29,067 near duplicates removed from Glaive) are from the `artifacts/metrics.json` of my chat-data cleaning project.
