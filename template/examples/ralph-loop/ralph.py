#!/usr/bin/env python3
"""ralph-loop. one file. no fancy. just loop.

ralph tries to find the best compression ratio for a list of numbers.
he doesn't know what "best" means. he just keeps trying.

usage:
    python ralph.py

that's it. no arguments. no config. no options. just ralph.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

# --- the data (ralph doesn't do separate files) ---

NUMBERS = [
    42, 17, 93, 8, 56, 31, 74, 12, 89, 45,
    63, 28, 91, 5, 67, 34, 82, 19, 58, 76,
    3, 41, 95, 14, 62, 27, 88, 46, 71, 22,
    53, 9, 78, 36, 84, 11, 69, 38, 92, 25,
    61, 16, 87, 43, 73, 7, 55, 32, 96, 20,
]

# --- the experiment (ralph doesn't do separation of concerns) ---

def compress(numbers: list[int], ratio: float) -> list[int]:
    """keep only `ratio` fraction of numbers (the ones closest to median)."""
    if ratio >= 1.0:
        return numbers[:]
    if ratio <= 0.0:
        return []

    median = sorted(numbers)[len(numbers) // 2]
    # score each number by distance from median (closer = better)
    scored = [(abs(n - median), n) for n in numbers]
    scored.sort()
    keep = max(1, int(len(numbers) * ratio))
    return [n for _, n in scored[:keep]]


def score(original: list[int], compressed: list[int], ratio: float) -> float:
    """score: how well did we preserve the signal?

    ralph's scoring formula:
    - mean preservation: how close is the mean?
    - range preservation: how close is the min/max?
    - compression bonus: smaller is better (but not too small)

    ralph doesn't know statistics. he just added numbers until
    the score felt right.
    """
    if not compressed:
        return 0.0

    orig_mean = sum(original) / len(original)
    comp_mean = sum(compressed) / len(compressed)
    mean_error = abs(orig_mean - comp_mean) / orig_mean

    orig_range = max(original) - min(original)
    comp_range = max(compressed) - min(compressed)
    range_error = abs(orig_range - comp_range) / orig_range if orig_range > 0 else 0

    # compression bonus: 0 at full size, 0.3 at 50%
    compression_bonus = (1 - ratio) * 0.3

    # penalty for over-compression (keeping < 20% is too aggressive)
    over_penalty = 0.3 if ratio < 0.2 else 0.0

    fitness = (1 - mean_error) * 0.5 + (1 - range_error) * 0.3 + compression_bonus - over_penalty
    return round(max(0, fitness), 4)


# --- the loop (ralph does everything inline) ---

STATE_FILE = Path(__file__).parent / "STATE.md"
LOG_FILE = Path(__file__).parent / "loop_run_log.jsonl"

STATE = {
    "iteration": 0,
    "best_ratio": 1.0,
    "best_score": 0.0,
    "history": [],
}


def plan() -> float:
    """ralph picks a ratio. how? vibes.

    if this is the first try, start at 0.5.
    if the last try was good, try a little more compression.
    if the last try was bad, try a little less.
    """
    if STATE["iteration"] == 0:
        return 0.5

    last = STATE["history"][-1] if STATE["history"] else None
    if not last:
        return 0.5

    if last["score"] > STATE["best_score"]:
        # good direction, push harder
        return max(0.1, last["ratio"] - 0.05)
    else:
        # bad direction, pull back
        return min(1.0, last["ratio"] + 0.1)


def execute(ratio: float) -> list[int]:
    """compress the numbers."""
    return compress(NUMBERS, ratio)


def evaluate(compressed: list[int], ratio: float) -> float:
    """score it."""
    return score(NUMBERS, compressed, ratio)


def decide(score: float) -> str:
    """ralph's decision engine.

    - if score > 0.7: "good enough!"
    - if iteration >= 5: "ok fine, stopping"
    - if score improved: "try harder"
    - otherwise: "try something else"
    """
    if score > 0.7:
        return "good enough"
    if STATE["iteration"] >= 5:
        return "ok fine"
    if score > STATE["best_score"]:
        return "try harder"
    return "try something else"


def update_state(ratio: float, score_val: float, decision: str):
    """update STATE.md (ralph remembers things sometimes)."""
    STATE["iteration"] += 1
    STATE["history"].append({"ratio": ratio, "score": score_val, "decision": decision})

    if score_val > STATE["best_score"]:
        STATE["best_score"] = score_val
        STATE["best_ratio"] = ratio

    # write STATE.md
    lines = [
        "# ralph's state",
        "",
        f"iteration: {STATE['iteration']}",
        f"best ratio: {STATE['best_ratio']:.2f}",
        f"best score: {STATE['best_score']:.4f}",
        f"last decision: {decision}",
        "",
        "## history",
    ]
    for h in STATE["history"]:
        lines.append(f"- ratio={h['ratio']:.2f} score={h['score']:.4f} -> {h['decision']}")
    lines.append("")
    STATE_FILE.write_text("\n".join(lines))

    # log
    log_entry = {
        "iteration": STATE["iteration"],
        "ratio": ratio,
        "score": score_val,
        "decision": decision,
    }
    with LOG_FILE.open("a") as f:
        f.write(json.dumps(log_entry) + "\n")


def run_loop():
    """ralph runs the loop. he doesn't know it's a loop. he just keeps going."""
    print("ralph-loop: ultra cavemanified loop engineering")
    print("=" * 50)

    while True:
        iteration = STATE["iteration"] + 1
        print(f"\n--- iteration {iteration} ---")

        # phase 1: plan (ralph picks a ratio)
        ratio = plan()
        print(f"  plan: ratio={ratio:.2f}")

        # phase 2: execute (ralph compresses)
        compressed = execute(ratio)
        print(f"  execute: {len(NUMBERS)} -> {len(compressed)} numbers")

        # phase 3: evaluate (ralph scores)
        score_val = evaluate(compressed, ratio)
        print(f"  evaluate: score={score_val:.4f}")

        # phase 4: decide (ralph decides)
        decision = decide(score_val)
        print(f"  decide: {decision}")

        # update state
        update_state(ratio, score_val, decision)

        if decision in ("good enough", "ok fine"):
            break

    print("\n" + "=" * 50)
    print(f"ralph is done. best ratio: {STATE['best_ratio']:.2f}, best score: {STATE['best_score']:.4f}")
    print("ralph says: 'i did my best.'")


if __name__ == "__main__":
    run_loop()
