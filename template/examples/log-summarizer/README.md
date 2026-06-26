# Loop Engineering E2E Example: Log Summarizer

> Compress verbose application logs into concise, actionable summaries.
> A DevOps/SRE use case for the Loop Engineering paradigm.

## The problem

Your application produces thousands of log lines per minute. You need to
summarize them into actionable alerts without losing critical information.
The loop explores summarization strategies and measures information retention.

## Quick start

```bash
cd template/examples/log-summarizer

# Run the full loop
python loop.py "baseline: first 50 chars of each line"

# Try a hypothesis
python loop.py "extract error codes and timestamps only"

# Check the state
cat STATE.md
```

## What this example demonstrates

| Loop phase | File | What it does |
|-----------|------|-------------|
| **Plan** | `loop.py` -> `plan()` | Generates a summarization strategy from a hypothesis |
| **Execute** | `experiment.py` | Summarizes logs, measures info retention |
| **Evaluate** | `evaluate.py` | Computes retention score, compression, fitness |
| **Decide** | `loop.py` -> `decide()` | SHIP / RETRAIN / PIVOT based on metrics |
| **State** | `STATE.md` | Durable memory spine |
| **Genesis** | `genesis.md` | What we're reducing, when to stop, what never to sacrifice |

## Files

```
log-summarizer/
├── loop.py              <- Four-phase runner
├── experiment.py        <- Log summarization experiment
├── evaluate.py          <- Metric computation
├── data.py              <- Sample logs (80 lines)
├── STATE.md             <- Loop state
├── genesis.md           <- Genesis contract
├── SKILL.md             <- Project conventions
├── loop_run_log.jsonl   <- Iteration log
└── README.md            <- This file
```

## Adapt this example

1. Replace `data.py` with your real log data
2. Modify `experiment.py` with your summarization strategy
3. Update `evaluate.py` with your retention metrics
4. Edit `genesis.md` with your convergence criteria
