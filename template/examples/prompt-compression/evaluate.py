"""Evaluate: compute accuracy, compression ratio, and F1 score.

Called by the loop's Evaluate phase. Takes experiment results and
produces a single fitness score for the Decide phase.
"""
from __future__ import annotations


def evaluate(results: dict) -> dict:
    """Compute evaluation metrics from experiment results.

    The fitness score balances accuracy and compression:
        fitness = accuracy * (1 + compression_bonus)

    Where compression_bonus = max(0, 1 - compression_ratio) * 0.5

    This rewards high accuracy AND high compression, with accuracy
    weighted more heavily.
    """
    accuracy = results["accuracy"]
    compression_ratio = results["compression_ratio"]

    # Compression bonus: 0 at full size, 0.5 at full compression
    compression_bonus = max(0, 1 - compression_ratio) * 0.5

    # Fitness: accuracy-weighted with compression bonus
    fitness = accuracy * (1 + compression_bonus)

    # F1 approximation (since we only have accuracy, approximate precision=recall)
    # In a real project, you'd compute this from the confusion matrix
    f1 = accuracy  # simplified: assume balanced classes

    # Thresholds
    accuracy_threshold = 0.85
    compression_threshold = 0.70  # at most 70% of original size

    passed = (
        accuracy >= accuracy_threshold
        and compression_ratio <= compression_threshold
    )

    return {
        "accuracy": accuracy,
        "compression_ratio": compression_ratio,
        "fitness": round(fitness, 4),
        "f1": round(f1, 4),
        "passed": passed,
        "accuracy_threshold": accuracy_threshold,
        "compression_threshold": compression_threshold,
    }
