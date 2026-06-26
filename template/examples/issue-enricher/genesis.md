# Genesis Contract -- issue-enricher

## What are you reducing?
Missing context in issue trackers. Issues lack cross-references, code
links, and related-issue connections. We want to enrich them automatically
using only open-source, legally-compliant tools.

## What makes an iteration valid?
- The experiment produces precision + coverage metrics
- The metric is comparable to the previous iteration
- The result is logged to loop_run_log.jsonl

## When do you stop?
- Both convergence criteria are met (precision >= 0.60, coverage >= 0.50), OR
- The correctable loop invariant fires (3 iterations, no improvement), OR
- The budget is exhausted

## What must never be sacrificed?
- Never fabricate numbers -- all metrics come from the experiment
- Never skip the evaluation phase
- Never remove the genesis contract
- Never add paid APIs or LLM calls beyond the optional summary
- Always respect robots.txt and rate limits
