# Skill: issue-enricher

## What this loop does
Enriches open-source issue trackers with structured context: cross-references,
code references, related issues, and velocity metrics. Uses only regex heuristics
and keyword overlap -- no LLM, no paid APIs, fully OS-legal.

## Decision rules
1. Never fabricate numbers -- all metrics come from the experiment.
2. The manuscript is the state; git is the durable memory.
3. Maker/checker: the experiment script (maker) vs the manuscript (checker).
4. If the metric doesn't improve in 3 iterations, stop (correctable loop invariant).
5. Halt when budget is exhausted or convergence criteria are met.

## Benchmark
- Dataset: 20 synthetic issues from a web framework repo
- Metrics: cross-ref precision, multi-signal coverage
- Target: precision >= 0.60 AND coverage >= 0.50

## Architecture
- Regex-based extraction (cross-refs, code refs, functions, error codes)
- Keyword overlap for related-issue detection (Jaccard similarity)
- GitHub REST API for crawling (60 req/hour unauthenticated)
- Evaluation: precision + coverage + fitness score

## Training
- No training -- this is a feature engineering / information extraction loop
- Each iteration tests a different enrichment strategy
- The loop explores the precision-coverage tradeoff
