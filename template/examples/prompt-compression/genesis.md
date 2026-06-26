# Genesis Contract — prompt-compression

## What are you reducing?
Prompt length for a sentiment classifier. Each word costs tokens. We want to
compress prompts while preserving the sentiment signal so accuracy doesn't drop.

## What makes an iteration valid?
- The experiment produces accuracy + compression ratio
- The metric is comparable to the previous iteration
- The result is logged to loop_run_log.jsonl

## When do you stop?
- Both convergence criteria are met (accuracy >= 0.85, compression <= 0.70), OR
- The correctable loop invariant fires (3 iterations, no improvement), OR
- The budget is exhausted

## What must never be sacrificed?
- Never fabricate numbers — all metrics come from the experiment
- Never skip the evaluation phase
- Never remove the genesis contract
- Never compress so aggressively that the classifier becomes random
