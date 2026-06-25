# Pareto Frontier

The must-keep loss weight λ controls the precision–compression tradeoff. v8's training data held constant; only λ varies.

## The frontier

| λ | Model | Heretic exact | Compression | keep_rate | Status |
|---|-------|--------------|-------------|-----------|--------|
| **3.0** | **v8** | **0.955** | **15.0%** | **0.854** | **Production (sweet spot)** |
| 5.0 | v17 | 0.963 | 3.7% | 0.963 | Pareto middle |
| 10.0 | v16 | 0.972 | 2.8% | 0.972 | Best precision, near-zero compression |

## Interpretation
- Each +1.0 in λ buys ~0.01 heretic precision at ~10% compression cost
- At λ=10, the model keeps 97.2% of tokens — useless as a compressor despite the best precision
- λ=3 (v8) is the knee of the curve: 0.955 heretic with 15% compression

## Why λ=3 is the production choice
In headroom (the production compression infrastructure), compression aggressiveness matters for context-window savings. λ=3 gives the best tradeoff: meaningful compression (15%) with high must-keep survival (0.955 heretic, 1.000 agent mk_in_ref with override).
