# 17 Models, $38.95, and One Paradox: What We Learned Training Compression Models in Public

**Peter Lodri · June 26, 2026**

---

We just published a paper proving that multi-checkpoint voting ensembles *collapse to their weakest voter*. We trained 17 kompress models on HuggingFace to fix it. Total cost: $38.95. Here's the full story — the dead ends, the breakthrough, and the open-source toolkit we built along the way.

## The Problem

[kompress](https://huggingface.co/chopratejas/kompress-v2-base) is a 149M-param ModernBERT token classifier that decides which tokens to keep when compressing LLM context. It's used by the [headroom proxy](https://github.com/headroomlabs-ai/headroom) to reduce token costs for coding agents.

The problem: it drops critical tokens — compiler flags (`-O2`), hex addresses (`0xDEAD`), file paths (`/var/log`), error names (`TokenExpiredError`). These get split across subword tokens by the ModernBERT tokenizer, and the single-token classifier misses them.

## The Paradox

We tried building an ensemble of models from different checkpoints. The ensemble should be *better* than any single model, right?

It was worse. Much worse.

Under k-of-N drop voting, the ensemble eviction indicator equals the k-th order statistic of the per-voter indicators. **The ensemble collapses to its weakest member on every stratum.** We proved this formally (Theorem 1 + Corollary 1 + Remark 1) and validated it empirically: an ensemble of v3, v3.1, and v3.2 scored 0.931 heretic-exact — worse than v4 alone at 0.967.

## The Fix: 3.0× Asymmetric Loss Modulation

Three mechanisms resolve the paradox:

1. **Training (λ=3.0):** Weighted cross-entropy penalty on critical-syntactic tokens — 3x more important than regular tokens
2. **Inference overrides:** Post-inference regex safety net catches what the tokenizer splits ([PR #1419](https://github.com/headroomlabs-ai/headroom/pull/1419))
3. **C3 Self-Distillation:** Qwen2.5-7B teacher labels must-keep spans on real tool outputs, student model learns to match

## The 17-Model Journey

All models on HuggingFace: [PeetPedro](https://huggingface.co/PeetPedro)

| Version | What We Tried | Heretic | Keep Rate | Lesson |
|---|---|---|---|---|
| v2-base | Baseline | 0.975 | 0.897 | Precision ceiling |
| v4 | Self-labels | 0.943 | 0.823 | Override internalized |
| v6 | Agent-distribution | 0.962 | — | Dead end |
| **v8** | **Qwen2.5 teacher** | **0.955** | **0.854** | **Production ★** |
| v9 | C3-only | 0.921 | — | Overfit |
| v11 | Large encoder (352M) | 0.906 | 0.517 | Capacity ≠ precision |
| v12 | Qwen3-Coder teacher | 0.949 | — | Too conservative |
| v14 | Council-controlled | 0.882 | — | Concept proven |
| v15 | Everything bagel | 0.878 | — | Diluted signal |
| v16 | 10× weight | 0.972 | 0.972 | Pareto endpoint |
| v17 | 5× weight | 0.963 | 0.963 | Tradeoff |

11 of 17 models were dead ends. **We published them all.** The dead ends are the research.

## The Weight Tradeoff (Pareto Frontier)

We mapped the full Pareto curve by varying the must-keep loss weight:

| Weight | Heretic | Compression | Status |
|---|---|---|---|
| 3× (v8) | 0.955 | 15% | **Optimal** |
| 5× (v17) | 0.963 | 3.7% | Too conservative |
| 10× (v16) | 0.972 | 2.8% | Useless compression |

The tradeoff is fundamental. λ=3.0 is the Pareto-optimal point.

## Open Science

Everything is public:

- **Paper:** [kompress.vaked.dev](https://kompress.vaked.dev) — interactive paper with live paradox simulation
- **Models:** [huggingface.co/PeetPedro](https://huggingface.co/PeetPedro) — 18 models with full cards
- **Eval Space:** [PeetPedro/headroom-eval](https://huggingface.co/spaces/PeetPedro/headroom-eval) — Level 4 Hill Climbing Loop
- **LoopKit:** [github.com/peterlodri-sec/loopkit](https://github.com/peterlodri-sec/loopkit) — loop engineering starter kit
- **Blog:** [pocoo.vaked.dev](https://pocoo.vaked.dev) — full experiment log

## What We Learned

1. **Label quality is the bottleneck** — not model capacity (v11 collapsed), not data quantity (v15 regressed with 3× more data)
2. **Small, calibrated datasets win** — v8's 97 carefully labeled pairs outperformed models trained on 983 pairs
3. **Regex in production beats training the model** — post-inference safety nets are surgical; training is blunt
4. **The Pareto frontier is real** — you cannot have perfect precision and aggressive compression simultaneously
5. **Dead ends are the research** — 11 of 17 models were dead ends, and we published every one

## Community

This project is part of the broader loop engineering ecosystem with [Addy Osmani](https://addyosmani.com/blog/loop-engineering/), [LangChain](https://www.langchain.com/blog/the-art-of-loop-engineering), and [Cobus Greyling](https://github.com/cobusgreyling/loop-engineering).

We're applying for an HF GPU Community Grant to run the Eval Space on a T4 — if you'd like to support this, check out the [Space](https://huggingface.co/spaces/PeetPedro/headroom-eval) and give it a like!

---

*"The agent forgets. The repo does not." — Addy Osmani*
