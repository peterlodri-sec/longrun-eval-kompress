# Skill: prompt-compression

## What this loop does
Compresses sentiment analysis prompts while preserving classification accuracy.
Explores compression strategies (truncation, stopword removal, keyword extraction)
and measures the accuracy-compression tradeoff.

## Decision rules
1. Never fabricate numbers — all metrics come from the experiment.
2. The manuscript is the state; git is the durable memory.
3. Maker/checker: the experiment script (maker) vs the manuscript (checker).
4. If the metric doesn't improve in 3 iterations, stop (correctable loop invariant).
5. Halt when budget is exhausted or convergence criteria are met.

## Benchmark
- Dataset: 100 product review prompts (50 positive, 50 negative)
- Classifier: lexicon-based sentiment scorer
- Metric: accuracy >= 0.85 AND compression ratio <= 0.70

## Architecture
- Lexicon-based classifier (no ML model)
- Compression spec: keyword extraction, stopword removal, truncation, positive-only
- Evaluation: accuracy + compression ratio + fitness score

## Training
- No training — this is a feature engineering / prompt engineering loop
- Each iteration tests a different compression strategy
- The loop explores the Pareto frontier of accuracy vs compression
