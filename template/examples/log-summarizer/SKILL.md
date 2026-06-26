# Skill: log-summarizer

## What this loop does
Compresses verbose application logs into concise summaries while retaining
critical information. Explores summarization strategies (field extraction,
truncation, structured filtering) and measures the retention-compression tradeoff.

## Decision rules
1. Never fabricate numbers -- all metrics come from the experiment.
2. The manuscript is the state; git is the durable memory.
3. Maker/checker: the experiment script (maker) vs the manuscript (checker).
4. If the metric doesn't improve in 3 iterations, stop (correctable loop invariant).
5. Halt when budget is exhausted or convergence criteria are met.

## Benchmark
- Dataset: 80 application log lines (INFO/WARN/ERROR, 4 components)
- Metrics: retention (critical field preservation), compression (size reduction)
- Target: retention >= 0.90 AND compression <= 0.60

## Architecture
- Regex-based field extraction (timestamp, level, component, error codes)
- Configurable summarization spec (keep/drop each field, truncate messages)
- Evaluation: retention + compression + fitness score

## Training
- No training -- this is a feature engineering / summarization strategy loop
- Each iteration tests a different summarization strategy
- The loop explores the Pareto frontier of retention vs compression
