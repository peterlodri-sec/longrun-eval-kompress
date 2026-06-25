# Version Lineage

17 models trained, 8 teachers, 4 architectures, $1.76 total compute.

| Ver | Teacher / Method | Heretic | keep_rate | Status |
|-----|-----------------|---------|-----------|--------|
| v2 | — (base) | 0.975 | 0.897 | precision ceiling |
| v3 | self-label, Q&A | 0.942 | 0.728 | first self-label |
| v4 | self-label, domain | 0.967 | 0.823 | override internalized |
| v5 | self-label, domain | 0.961 | — | converged |
| v6 | generator, agent-dist | 0.962 | 0.854 | dead end |
| v7 | sliding-window | 0.956 | 0.868 | dead end |
| **v8** | **Qwen2.5-7B C3 (λ=3)** | **0.955** | **0.854** | **PRODUCTION** |
| v9 | Qwen2.5-7B, C3-only | 0.921 | — | overfit |
| v10 | Qwen2.5-7B, scaled C3 | 0.947 | 0.891 | diminishing |
| v11 | Qwen2.5-7B, large enc | 0.917 | 0.517 | capacity ≠ precision |
| v12 | Qwen3-Coder | 0.949 | 0.949 | too conservative |
| v13 | regex, GLM | 0.951 | 0.951 | too conservative |
| v14 | council, v8+GLM | 0.882 | — | proof-of-concept |
| v15 | mixed (983 pairs) | 0.878 | — | data-scale regression |
| v16 | Qwen2.5 C3 (λ=10) | 0.972 | 0.972 | best precision, 2.8% compression |
| v17 | Qwen2.5 C3 (λ=5) | 0.963 | 0.963 | Pareto middle |

## Key finding
**Label quality is the bottleneck, not model capacity or data quantity.**
- v15 (983 pairs, largest dataset) → 0.878 (worst)
- v11 (larger encoder) → keep_rate collapsed to 0.517
- Only label-quality interventions improved the heretic metric

## All models on HuggingFace
- https://huggingface.co/PeetPedro/kompress-v8
- https://huggingface.co/PeetPedro/kompress-v17
- https://huggingface.co/PeetPedro/kompress-v16
- https://huggingface.co/PeetPedro/kompress-v15
- https://huggingface.co/PeetPedro/kompress-v7
- https://huggingface.co/PeetPedro/kompress-v6
- https://huggingface.co/PeetPedro/kompress-v4
- https://huggingface.co/PeetPedro/kompress-v3
- Full list: https://huggingface.co/PeetPedro (18 models)
