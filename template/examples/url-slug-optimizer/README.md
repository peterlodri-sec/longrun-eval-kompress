# Loop Engineering E2E Example: URL Slug Optimizer

> Find the optimal URL slug generation strategy balancing readability and brevity.
> A web engineering use case for the Loop Engineering paradigm.

## The problem

Your URL shortener generates slugs from page titles. You need slugs that are
short enough to share but readable enough to be memorable. The loop explores
slug generation strategies and measures the readability-brevity tradeoff.

## Quick start

```bash
cd template/examples/url-slug-optimizer

# Run the full loop
python loop.py "baseline: full title slug"

# Try a hypothesis
python loop.py "remove vowels from long words"

# Check the state
cat STATE.md
```

## What this example demonstrates

| Loop phase | File | What it does |
|-----------|------|-------------|
| **Plan** | `loop.py` -> `plan()` | Generates a slug strategy from a hypothesis |
| **Execute** | `experiment.py` | Generates slugs, measures readability + brevity |
| **Evaluate** | `evaluate.py` | Computes readability score, length, fitness |
| **Decide** | `loop.py` -> `decide()` | SHIP / RETRAIN / PIVOT based on metrics |
| **State** | `STATE.md` | Durable memory spine |
| **Genesis** | `genesis.md` | What we're reducing, when to stop, what never to sacrifice |

## Files

```
url-slug-optimizer/
├── loop.py              <- Four-phase runner
├── experiment.py        <- Slug generation experiment
├── evaluate.py          <- Metric computation
├── data.py              <- Sample page titles (60 entries)
├── STATE.md             <- Loop state
├── genesis.md           <- Genesis contract
├── SKILL.md             <- Project conventions
├── loop_run_log.jsonl   <- Iteration log
└── README.md            <- This file
```

## Adapt this example

1. Replace `data.py` with your real page titles/URLs
2. Modify `experiment.py` with your slug generation strategy
3. Update `evaluate.py` with your readability metrics
4. Edit `genesis.md` with your convergence criteria
