# Skill: url-slug-optimizer

## What this loop does
Generates URL slugs from page titles while balancing readability and brevity.
Explores slug strategies (stopword removal, vowel stripping, truncation)
and measures the readability-length tradeoff.

## Decision rules
1. Never fabricate numbers -- all metrics come from the experiment.
2. The manuscript is the state; git is the durable memory.
3. Maker/checker: the experiment script (maker) vs the manuscript (checker).
4. If the metric doesn't improve in 3 iterations, stop (correctable loop invariant).
5. Halt when budget is exhausted or convergence criteria are met.

## Benchmark
- Dataset: 60 technical blog post titles
- Metrics: readability (word overlap with title), average slug length
- Target: readability >= 0.40 AND avg length <= 45 chars

## Architecture
- Regex-based slug generation (word extraction, filtering, joining)
- Configurable slug spec (stopwords, vowels, truncation, word limit)
- Evaluation: readability + length + fitness score

## Training
- No training -- this is a feature engineering / text transformation loop
- Each iteration tests a different slug generation strategy
- The loop explores the Pareto frontier of readability vs brevity
