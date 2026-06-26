# Genesis Contract -- commit-optimizer

## What are you reducing?
Commit message inconsistency. Some follow conventional commits, some don't.
We want to generate proper messages from diffs using only regex and heuristics.

## What makes an iteration valid?
- The experiment produces score + compliance metrics
- The metric is comparable to the previous iteration
- The result is logged to loop_run_log.jsonl

## When do you stop?
- Both convergence criteria are met (score >= 60, compliance >= 0.70), OR
- The correctable loop invariant fires (3 iterations, no improvement), OR
- The budget is exhausted

## What must never be sacrificed?
- Never fabricate numbers -- all metrics come from the experiment
- Never skip the evaluation phase
- Never remove the genesis contract
- Never use an LLM -- this must stay pure regex
