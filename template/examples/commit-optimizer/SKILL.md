# Skill: commit-optimizer

## What this loop does
Generates conventional commit messages from git diffs using only regex and
heuristics. Analyzes file types, function/class changes, and issue references
to produce type(scope): description messages.

## Decision rules
1. Never fabricate numbers -- all metrics come from the experiment.
2. The manuscript is the state; git is the durable memory.
3. Maker/checker: the experiment script (maker) vs the manuscript (checker).
4. If the metric doesn't improve in 3 iterations, stop (correctable loop invariant).
5. Halt when budget is exhausted or convergence criteria are met.

## Benchmark
- Dataset: 30 realistic git diffs (features, fixes, refactors, docs, config)
- Metrics: avg score (0-100), grammar compliance (type(scope): desc)
- Target: score >= 60 AND compliance >= 0.70

## Architecture
- Regex-based diff parsing (file paths, function/class changes, issue refs)
- Conventional commit grammar detection
- Scoring: grammar (40) + header length (20) + scope (15) + body (15) + refs (10)
- Evaluation: score + compliance + fitness

## Training
- No training -- this is a feature engineering / text generation loop
- Each iteration tests a different analysis strategy
- The loop explores the quality-coverage tradeoff
