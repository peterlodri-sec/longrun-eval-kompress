#!/usr/bin/env python3
"""Loop runner: Plan -> Execute -> Evaluate -> Decide.

Usage:
    python loop.py "baseline: parse issue body only"
    python loop.py "find related issues by keyword overlap"
    python loop.py "full enrichment with related issues"

Each iteration:
1. Plan    -- generate an enrichment strategy from the hypothesis
2. Execute -- enrich issues, measure coverage + precision
3. Evaluate -- measure precision, coverage, fitness
4. Decide  -- SHIP / RETRAIN / PIVOT
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from experiment import EnrichmentSpec, run_experiment
from evaluate import evaluate

STATE_FILE = Path(__file__).parent / "STATE.md"
LOG_FILE = Path(__file__).parent / "loop_run_log.jsonl"


def plan(hypothesis: str) -> EnrichmentSpec:
    """Phase 1: derive an enrichment spec from the hypothesis."""
    h = hypothesis.lower()

    if "baseline" in h or "body only" in h:
        return EnrichmentSpec(
            name="baseline: body parsing only",
            extract_cross_refs=True,
            extract_code_refs=False,
            extract_functions=False,
            extract_error_codes=False,
            find_related=False,
        )

    if "related" in h and "keyword" in h:
        return EnrichmentSpec(
            name="related issues via keyword overlap",
            extract_cross_refs=True,
            extract_code_refs=True,
            extract_functions=False,
            find_related=True,
            related_threshold=0.15,
        )

    if "full" in h or "all" in h:
        return EnrichmentSpec(
            name="full enrichment with related issues",
            extract_cross_refs=True,
            extract_code_refs=True,
            extract_functions=True,
            extract_error_codes=True,
            find_related=True,
            related_threshold=0.12,
        )

    if "velocity" in h:
        return EnrichmentSpec(
            name="velocity-focused (time metrics)",
            extract_cross_refs=True,
            extract_velocity=True,
            extract_code_refs=False,
            find_related=False,
        )

    if "code" in h:
        return EnrichmentSpec(
            name="code-focused (file + function refs)",
            extract_cross_refs=True,
            extract_code_refs=True,
            extract_functions=True,
            find_related=False,
        )

    # Default: cross-refs + keywords
    return EnrichmentSpec(
        name="cross-refs + keywords (default)",
        extract_cross_refs=True,
        extract_keywords=True,
        find_related=False,
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
    print(f"  Evaluate: precision={evaluation['precision']:.3f}, "
          f"coverage={evaluation['coverage']:.3f}, "
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
        "precision": evaluation["precision"],
        "coverage": evaluation["coverage"],
        "fitness": evaluation["fitness"],
        "decision": decision,
    }
    with LOG_FILE.open("a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return decision


if __name__ == "__main__":
    import sys
    hypothesis = sys.argv[1] if len(sys.argv) > 1 else "baseline: parse issue body only"
    decision = run_iteration(hypothesis)
    print(f"\nLoop decision: {decision}")
    if decision == "SHIP":
        print("Convergence reached. Update STATE.md and write up results.")
    elif decision == "PIVOT":
        print("Metric not improving. Pivot to a new hypothesis.")
    else:
        print("Retrain with refined hypothesis.")
