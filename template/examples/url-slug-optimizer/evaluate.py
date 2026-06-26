"""Evaluate: compute readability, length, and fitness.

The fitness score balances readability (slug contains recognizable words)
and brevity (short URLs). Readability is weighted more heavily -- a slug
nobody can read is useless regardless of how short it is.
"""


def evaluate(results: dict) -> dict:
    """Compute evaluation metrics from experiment results."""
    readability = results["avg_readability"]
    avg_length = results["avg_slug_length"]
    compression = results["compression"]

    # Brevity bonus: 0 at 50+ chars, 0.5 at 10 chars
    brevity_bonus = max(0, (50 - avg_length) / 80) * 0.5

    # Fitness: readability-weighted with brevity bonus
    fitness = readability * (1 + brevity_bonus)

    # Thresholds
    readability_threshold = 0.40  # slug should contain 40% of title words
    max_length_threshold = 45  # avg slug <= 45 chars

    passed = (
        readability >= readability_threshold
        and avg_length <= max_length_threshold
    )

    return {
        "readability": readability,
        "avg_length": avg_length,
        "compression": compression,
        "fitness": round(fitness, 4),
        "passed": passed,
        "readability_threshold": readability_threshold,
        "max_length_threshold": max_length_threshold,
    }
