#!/usr/bin/env python3
"""Loop runner: Plan -> Execute -> Evaluate -> Decide.

Usage:
    python loop.py "baseline: use first changed file as scope"
    python loop.py "detect type from file paths and changed patterns"
    python loop.py "full analysis with breaking change detection"
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from experiment import CommitStrategy, run_experiment
from evaluate import evaluate

STATE_FILE = Path(__file__).parent / "STATE.md"
LOG_FILE = Path(__file__).parent / "loop_run_log.jsonl"


def plan(hypothesis: str) -> CommitStrategy:
    """Phase 1: derive a commit strategy from the hypothesis."""
    h = hypothesis.lower()

    if "baseline" in h or "first" in h:
        return CommitStrategy(
            name="baseline: first file as scope",
            use_file_type=True,
            use_function_names=False,
            use_scope=True,
            use_issue_refs=False,
        )

    if "file path" in h or "path" in h:
        return CommitStrategy(
            name="file path type detection",
            use_file_type=True,
            use_function_names=True,
            use_scope=True,
            use_issue_refs=True,
        )

    if "full" in h or "all" in h or "breaking" in h:
        return CommitStrategy(
            name="full analysis with breaking detection",
            use_file_type=True,
            use_function_names=True,
            use_scope=True,
            use_issue_refs=True,
            detect_breaking=True,
        )

    if "keyword" in h:
        return CommitStrategy(
            name="keyword-based type detection",
            use_file_type=True,
            use_function_names=True,
            keyword_type_detection=True,
        )

    # Default: file type + function names
    return CommitStrategy(
        name="file type + function names (default)",
        use_file_type=True,
        use_function_names=True,
        use_scope=True,
    )


def decide(evaluation: dict, iteration: int) -> str:
    """Phase 4: decide what to do next."""
    if evaluation["passed"]:
        return "SHIP"
    if iteration >= 3:
        return "PIVOT"
    return "RETRAIN"


def read_iteration() -> int:
    if not STATE_FILE.exists():
        return 0
    content = STATE_FILE.read_text()
    m = re.search(r"Iteration:\s*(\d+)", content)
    return int(m.group(1)) if m else 0


def update_state(iteration: int, hypothesis: str, evaluation: dict, decision: str):
    content = STATE_FILE.read_text() if STATE_FILE.exists() else ""
    content = re.sub(r"Iteration:\s*\d+", f"Iteration: {iteration}", content)
    content = re.sub(r"Hypothesis:.*", f"Hypothesis: {hypothesis}", content)
    content = re.sub(r"Status:.*", f"Status: {decision.lower()}", content)
    STATE_FILE.write_text(content)


def run_iteration(hypothesis: str):
    iteration = read_iteration() + 1
    print(f"\n=== Iteration {iteration} ===")

    spec = plan(hypothesis)
    print(f"  Plan: {spec.name}")

    result = run_experiment(spec)

    evaluation = evaluate(result)
    print(f"  Evaluate: score={evaluation['avg_score']:.1f}, "
          f"grammar={evaluation['grammar']:.3f}, "
          f"fitness={evaluation['fitness']:.3f}")

    decision = decide(evaluation, iteration)
    print(f"  Decide: {decision}")

    update_state(iteration, hypothesis, evaluation, decision)

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "iteration": iteration,
        "hypothesis": hypothesis,
        "spec": spec.name,
        "avg_score": evaluation["avg_score"],
        "grammar": evaluation["grammar"],
        "fitness": evaluation["fitness"],
        "decision": decision,
    }
    with LOG_FILE.open("a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return decision


if __name__ == "__main__":
    import sys
    hypothesis = sys.argv[1] if len(sys.argv) > 1 else "baseline: use first changed file as scope"
    decision = run_iteration(hypothesis)
    print(f"\nLoop decision: {decision}")
    if decision == "SHIP":
        print("Convergence reached.")
    elif decision == "PIVOT":
        print("Metric not improving. Pivot.")
    else:
        print("Retrain with refined hypothesis.")
