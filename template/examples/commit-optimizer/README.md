# Loop Engineering E2E Example: Commit Message Optimizer

> Generate conventional commit messages from git diffs.
> A developer productivity use case -- zero LLM, pure regex archaeology.

## The problem

Your team writes inconsistent commit messages. Some use conventional commits,
some don't. You need a tool that analyzes a git diff and generates a proper
conventional commit message -- type, scope, description -- using only regex
and heuristics.

## Quick start

```bash
cd template/examples/commit-optimizer

# Analyze a sample diff
python loop.py "baseline: use first changed file as scope"

# Try a hypothesis
python loop.py "detect type from file paths and changed patterns"

# Check the state
cat STATE.md
```

## The clever parts

1. **Diff archaeology** -- parse `+`/`-` lines to detect added/removed patterns
2. **Type detection** -- `package.json` change = `chore`, `*.test.*` = `test`, new `*.py` = `feat`
3. **Scope extraction** -- directory name, file basename, or changed module
4. **Conventional commit grammar** -- `type(scope): description` with body and footer
5. **Breaking change detection** -- removed public API = `!` suffix
6. **Issue linking** -- extract `Fixes #123`, `Closes #456` from diff context

No LLM. No API calls. Just regex and heuristics. Surprisingly effective.

## What this example demonstrates

| Loop phase | File | What it does |
|-----------|------|-------------|
| **Plan** | `loop.py` -> `plan()` | Generates a commit strategy from a hypothesis |
| **Execute** | `experiment.py` | Analyzes diffs, generates messages, scores them |
| **Evaluate** | `evaluate.py` | Computes grammar compliance, scope accuracy, fitness |
| **Decide** | `loop.py` -> `decide()` | SHIP / RETRAIN / PIVOT based on metrics |
| **State** | `STATE.md` | Durable memory spine |
| **Genesis** | `genesis.md` | What we're reducing, when to stop, what never to sacrifice |

## Files

```
commit-optimizer/
├── loop.py              <- Four-phase runner
├── experiment.py        <- Diff analysis + message generation
├── evaluate.py          <- Metric computation
├── data.py              <- Sample diffs (30 realistic git diffs)
├── analyzer.py          <- Core diff analyzer (regex + heuristics)
├── STATE.md             <- Loop state
├── genesis.md           <- Genesis contract
├── SKILL.md             <- Project conventions
├── loop_run_log.jsonl   <- Iteration log
└── README.md            <- This file
```

## Adapt this example

1. Replace `data.py` with your real git diffs
2. Modify `analyzer.py` to add domain-specific type detection
3. Update `evaluate.py` with your commit quality metrics
4. Edit `genesis.md` with your convergence criteria
