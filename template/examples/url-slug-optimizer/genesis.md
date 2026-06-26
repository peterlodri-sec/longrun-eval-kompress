# Genesis Contract — url-slug-optimizer

## What are you reducing?
URL slug length for page titles. Longer slugs cost more characters and are
harder to share. But slugs that are too short lose readability. We want to
find the optimal tradeoff.

## What makes an iteration valid?
- The experiment produces readability + length metrics
- The metric is comparable to the previous iteration
- The result is logged to loop_run_log.jsonl

## When do you stop?
- Both convergence criteria are met (readability >= 0.40, length <= 45), OR
- The correctable loop invariant fires (3 iterations, no improvement), OR
- The budget is exhausted

## What must never be sacrificed?
- Never fabricate numbers -- all metrics come from the experiment
- Never skip the evaluation phase
- Never remove the genesis contract
- Never optimize so aggressively that slugs become unreadable
