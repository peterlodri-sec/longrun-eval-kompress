# Loop Engineering E2E Example: Prompt Compression

> A complete, runnable example of the Loop Engineering paradigm.
> Compresses prompts for a sentiment classifier while preserving accuracy.

## The problem

You have a sentiment classifier that works great on full prompts, but you need to
compress the prompts to save tokens. The loop explores compression strategies and
measures whether accuracy is preserved.

## Quick start

```bash
cd template/examples/prompt-compression

# Run the full loop (3 iterations)
python loop.py "baseline: no compression"

# Run with a hypothesis
python loop.py "keyword extraction preserves sentiment signal"

# Check the state
cat STATE.md
```

## What this example demonstrates

| Loop phase | File | What it does |
|-----------|------|-------------|
| **Plan** | `loop.py` → `plan()` | Generates a compression spec from a hypothesis |
| **Execute** | `experiment.py` | Compresses prompts, runs classifier, logs results |
| **Evaluate** | `evaluate.py` | Measures accuracy, compression ratio, F1 |
| **Decide** | `loop.py` → `decide()` | SHIP / RETRAIN / PIVOT based on metrics |
| **State** | `STATE.md` | Durable memory spine — iteration history, budget, convergence |
| **Genesis** | `genesis.md` | What we're reducing, when to stop, what never to sacrifice |

## The loop in action

```
$ python loop.py "baseline: no compression"

=== Iteration 1 ===
  Plan: baseline: no compression
  Executing: no compression (full prompts)
  Evaluate: accuracy=0.870, compression=1.000, f1=0.856
  Decide: RETRAIN

$ python loop.py "keyword extraction preserves sentiment signal"

=== Iteration 2 ===
  Plan: keyword extraction preserves sentiment signal
  Executing: extract top-10 keywords per prompt
  Evaluate: accuracy=0.845, compression=0.320, f1=0.830
  Decide: RETRAIN

$ python loop.py "stopword removal only"

=== Iteration 3 ===
  Plan: stopword removal only
  Executing: remove stopwords, keep all other tokens
  Evaluate: accuracy=0.862, compression=0.680, f1=0.848
  Decide: PIVOT (correctable invariant: 3 iterations, no improvement)
```

## Files

```
prompt-compression/
├── loop.py              ← Four-phase runner (Plan → Execute → Evaluate → Decide)
├── experiment.py        ← Compression + classification experiment
├── evaluate.py          ← Metric computation (accuracy, compression, F1)
├── data.py              ← Sample dataset (100 sentiment prompts)
├── STATE.md             ← Loop state (durable memory)
├── genesis.md           ← Genesis contract
├── SKILL.md             ← Project conventions
├── loop_run_log.jsonl   ← Iteration log (append-only)
└── README.md            ← This file
```

## Adapt this example

1. Replace `data.py` with your real dataset
2. Modify `experiment.py` to implement your compression strategy
3. Update `evaluate.py` to compute your target metric
4. Edit `genesis.md` with your convergence criteria
5. Run the loop: `python loop.py "your hypothesis"`
