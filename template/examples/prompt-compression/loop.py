#!/usr/bin/env python3
"""Loop runner: Plan -> Execute -> Evaluate -> Decide.

Usage:
    python loop.py "baseline: no compression"
    python loop.py "keyword extraction preserves sentiment signal"
    python loop.py "stopword removal only"

Each iteration:
1. Plan    — generate a compression spec from the hypothesis
2. Execute — run the experiment (compress + classify)
3. Evaluate — measure accuracy, compression, fitness
4. Decide  — SHIP / RETRAIN / PIVOT
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from experiment import CompressionSpec, run_experiment
from evaluate import evaluate

STATE_FILE = Path(__file__).parent / "STATE.md"
LOG_FILE = Path(__file__).parent / "loop_run_log.jsonl"


def plan(hypothesis: str) -> CompressionSpec:
    """Phase 1: derive a compression spec from a hypothesis."""
    h = hypothesis.lower()

    if "baseline" in h or "no compression" in h:
        return CompressionSpec(name="baseline (no compression)")

    if "keyword" in h:
        return CompressionSpec(
            name="keyword extraction",
            extract_keywords=True,
            keyword_top_n=10,
        )

    if "stopword" in h:
        return CompressionSpec(
            name="stopword removal",
            remove_stopwords=True,
        )

    if "short" in h or "truncate" in h or "first" in h:
        return CompressionSpec(
            name="truncation (first 8 words)",
            max_words=8,
        )

    if "positive" in h:
        return CompressionSpec(
            name="positive words only",
            keep_positive_only=True,
        )

    # Default: try keyword extraction
    return CompressionSpec(
        name="keyword extraction (default)",
        extract_keywords=True,
        keyword_top_n=8,
    )


def evaluate_phase(result: dict) -> dict:
    """Phase 3: evaluate the result against the benchmark."""
    return evaluate(result)


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
    # Read existing state
    content = STATE_FILE.read_text() if STATE_FILE.exists() else ""

    # Update iteration count
    content = re.sub(r"Iteration:\s*\d+", f"Iteration: {iteration}", content)

    # Update hypothesis
    content = re.sub(
        r"Hypothesis:.*",
        f"Hypothesis: {hypothesis}",
        content
    )

    # Update status
    content = re.sub(
        r"Status:.*",
        f"Status: {decision.lower()}",
        content
    )

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
    evaluation = evaluate_phase(result)
    print(f"  Evaluate: accuracy={evaluation['accuracy']:.3f}, "
          f"compression={evaluation['compression_ratio']:.3f}, "
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
        "accuracy": evaluation["accuracy"],
        "compression_ratio": evaluation["compression_ratio"],
        "fitness": evaluation["fitness"],
        "decision": decision,
    }
    with LOG_FILE.open("a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return decision


if __name__ == "__main__":
    import sys
    hypothesis = sys.argv[1] if len(sys.argv) > 1 else "baseline: no compression"
    decision = run_iteration(hypothesis)
    print(f"\nLoop decision: {decision}")
    if decision == "SHIP":
        print("Convergence reached. Update STATE.md and write up results.")
    elif decision == "PIVOT":
        print("Metric not improving. Pivot to a new hypothesis.")
    else:
        print("Retrain with refined hypothesis.")
