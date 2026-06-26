#!/usr/bin/env python3
"""Loop runner: Plan -> Execute -> Evaluate -> Decide.

Usage:
    python loop.py "baseline: first 50 chars of each line"
    python loop.py "extract error codes and timestamps only"
    python loop.py "keep level + component + error codes, truncate message"

Each iteration:
1. Plan    -- generate a summarization spec from the hypothesis
2. Execute -- run the experiment (summarize + measure retention)
3. Evaluate -- measure retention, compression, fitness
4. Decide  -- SHIP / RETRAIN / PIVOT
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from experiment import SummarySpec, run_experiment
from evaluate import evaluate

STATE_FILE = Path(__file__).parent / "STATE.md"
LOG_FILE = Path(__file__).parent / "loop_run_log.jsonl"


def plan(hypothesis: str) -> SummarySpec:
    """Phase 1: derive a summarization spec from a hypothesis."""
    h = hypothesis.lower()

    if "baseline" in h or "truncate" in h or "first" in h:
        return SummarySpec(
            name="baseline: truncate to 50 chars",
            keep_message=True,
            message_max_chars=50,
        )

    if "error code" in h and "timestamp" in h:
        return SummarySpec(
            name="error codes + timestamps only",
            keep_timestamp=True,
            keep_level=True,
            keep_component=False,
            keep_error_codes=True,
            keep_message=False,
        )

    if "level" in h and "component" in h and "error" in h:
        return SummarySpec(
            name="level + component + error codes",
            keep_timestamp=False,
            keep_level=True,
            keep_component=True,
            keep_error_codes=True,
            keep_message=False,
        )

    if "user_id" in h or "field" in h:
        return SummarySpec(
            name="extract user_id fields",
            keep_timestamp=True,
            keep_level=True,
            keep_component=True,
            keep_error_codes=True,
            keep_message=False,
            extract_fields=["user_id", "error"],
        )

    if "short" in h:
        return SummarySpec(
            name="short: level + first 5 words",
            keep_timestamp=False,
            keep_level=True,
            keep_component=False,
            keep_error_codes=False,
            keep_message=True,
            first_n_words=5,
        )

    # Default: level + component + error codes + truncated message
    return SummarySpec(
        name="level + component + error + truncated message",
        keep_timestamp=True,
        keep_level=True,
        keep_component=True,
        keep_error_codes=True,
        keep_message=True,
        message_max_chars=40,
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
    print(f"  Evaluate: retention={evaluation['retention']:.3f}, "
          f"compression={evaluation['compression']:.3f}, "
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
        "retention": evaluation["retention"],
        "compression": evaluation["compression"],
        "fitness": evaluation["fitness"],
        "decision": decision,
    }
    with LOG_FILE.open("a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return decision


if __name__ == "__main__":
    import sys
    hypothesis = sys.argv[1] if len(sys.argv) > 1 else "baseline: first 50 chars of each line"
    decision = run_iteration(hypothesis)
    print(f"\nLoop decision: {decision}")
    if decision == "SHIP":
        print("Convergence reached. Update STATE.md and write up results.")
    elif decision == "PIVOT":
        print("Metric not improving. Pivot to a new hypothesis.")
    else:
        print("Retrain with refined hypothesis.")
