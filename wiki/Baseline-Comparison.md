# Baseline Comparison

## Results (8-prompt heretic set)

| Method | exact_keep_pct | keep_rate | avg ms |
|--------|---------------|-----------|--------|
| **kompress-v8 (ours)** | **0.993** | 0.936 | 97.0 |
| Random eviction | 0.910 | 0.835 | 0.0 |
| LLMLingua-2 | 0.867 | 1.550† | 238.9 |
| TextRank | 0.599 | 0.543 | 23.1 |

† LLMLingua-2's keep_rate >1.0 reflects token expansion from special boundary markers — expected behavior.

## Analysis
- The gap between kompress-v8 (0.993) and random eviction (0.910) is the **learned component's contribution**: +0.083 over chance
- TextRank's 0.599 confirms that extractive summarization is unsuitable for must-keep preservation
- LLMLingua-2's 0.867 at 1.55 keep_rate shows that token-budget compression without must-keep awareness is insufficient

## How to reproduce
```bash
python baselines/run_baselines.py
```
Results save to `baselines/baseline_results.json`.

## Interactive comparison
https://peterlodri-sec.github.io/longrun-eval-kompress/baselines.html

## Missing baselines
AutoCompressors and Gisting require separate training on large corpora and are not runnable on a single M1 Pro. They are deferred to a revision with GPU resources.
