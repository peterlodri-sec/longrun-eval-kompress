#!/usr/bin/env python3
"""Loop runner: Plan -> Execute -> Evaluate -> Decide.

Usage:
    python loop.py "baseline: full title slug"
    python loop.py "remove vowels from long words"
    python loop.py "remove stopwords, keep first 6 words"

Each iteration:
1. Plan    -- generate a slug spec from the hypothesis
2. Execute -- run the experiment (generate slugs + measure)
3. Evaluate -- measure readability, length, fitness
4. Decide  -- SHIP / RETRAIN / PIVOT
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from experiment import SlugSpec, run_experiment
from evaluate import evaluate

STATE_FILE = Path(__file__).parent / "STATE.md"
LOG_FILE = Path(__file__).parent / "loop_run_log.jsonl"


def plan(hypothesis: str) -> SlugSpec:
    """Phase 1: derive a slug spec from the hypothesis."""
    h = hypothesis.lower()

    if "baseline" in h or "full" in h:
        return SlugSpec(name="baseline: full title slug")

    if "vowel" in h:
        return SlugSpec(
            name="remove vowels from long words",
            remove_vowels=True,
        )

    if "stopword" in h and "first" in h:
        return SlugSpec(
            name="remove stopwords, keep first 6",
            remove_stopwords=True,
            keep_first_n=6,
        )

    if "stopword" in h:
        return SlugSpec(
            name="remove stopwords",
            remove_stopwords=True,
        )

    if "first" in h or "short" in h:
        return SlugSpec(
            name="keep first 5 words only",
            keep_first_n=5,
        )

    if "truncate" in h:
        return SlugSpec(
            name="truncate title to 30 chars",
            truncate_title=30,
        )

    # Default: stopword removal + first 6 words
    return SlugSpec(
        name="stopwords + first 6 words (default)",
        remove_stopwords=True,
        keep_first_n=6,
    )


def decide(evaluation: dict, iteration: int) -> str:
    """Phase 4: decide what to do next (SHIP / RETRAIN / PIVOT)."""
    if evaluation["passed"]:
        return "SHIP"
    if iteration >= 3:
        return "PIVOT"
    return "RETRAIN"


def read_iteration() -> int:
    """Read current iteration from STATE.md."""
    if not STATE_FILE.exists():
        return 0
    content = STATE_FILE.read_text()
    m = re.search(r"Iteration:\s*(\d+)", content)
    return int(m.group(1)) if m else 0


def update_state(iteration: int, hypothesis: str, evaluation: dict, decision: str):
    """Update STATE.md with the latest iteration."""
    content = STATE_FILE.read_text() if STATE_FILE.exists() else ""
    content = re.sub(r"Iteration:\s*\d+", f"Iteration: {iteration}", content)
    content = re.sub(r"Hypothesis:.*", f"Hypothesis: {hypothesis}", content)
    content = re.sub(r"Status:.*", f"Status: {decision.lower()}", content)
    STATE_FILE.write_text(content)


def run_iteration(hypothesis: str):
    """Run one full four-phase cycle."""
    iteration = read_iteration() + 1
    print(f"\n=== Iteration {iteration} ===")

    # Phase 1: Plan
    spec = plan(hypothesis)
    print(f"  Plan: {spec.name}")

    # Phase 2: Execute
    result = run_experiment(spec)

    # Phase 3: Evaluate
    evaluation = evaluate(result)
    print(f"  Evaluate: readability={evaluation['readability']:.3f}, "
          f"avg_length={evaluation['avg_length']:.1f}, "
          f"fitness={evaluation['fitness']:.3f}")

    # Phase 4: Decide
    decision = decide(evaluation, iteration)
    print(f"  Decide: {decision}")

    # Update state
    update_state(iteration, hypothesis, evaluation, decision)

    # Log
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "iteration": iteration,
        "hypothesis": hypothesis,
        "spec": spec.name,
        "readability": evaluation["readability"],
        "avg_length": evaluation["avg_length"],
        "fitness": evaluation["fitness"],
        "decision": decision,
    }
    with LOG_FILE.open("a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return decision


if __name__ == "__main__":
    import sys
    hypothesis = sys.argv[1] if len(sys.argv) > 1 else "baseline: full title slug"
    decision = run_iteration(hypothesis)
    print(f"\nLoop decision: {decision}")
    if decision == "SHIP":
        print("Convergence reached. Update STATE.md and write up results.")
    elif decision == "PIVOT":
        print("Metric not improving. Pivot to a new hypothesis.")
    else:
        print("Retrain with refined hypothesis.")
