# Genesis Contract — log-summarizer

## What are you reducing?
Verbose application log lines. Each line costs storage and parsing time.
We want to compress them into concise summaries while retaining critical
information (level, timestamp, error codes, component).

## What makes an iteration valid?
- The experiment produces retention + compression metrics
- The metric is comparable to the previous iteration
- The result is logged to loop_run_log.jsonl

## When do you stop?
- Both convergence criteria are met (retention >= 0.90, compression <= 0.60), OR
- The correctable loop invariant fires (3 iterations, no improvement), OR
- The budget is exhausted

## What must never be sacrificed?
- Never fabricate numbers -- all metrics come from the experiment
- Never skip the evaluation phase
- Never remove the genesis contract
- Never compress so aggressively that error codes or timestamps are lost
