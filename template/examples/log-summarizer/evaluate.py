"""Evaluate: compute retention, compression, and fitness.

The fitness score balances information retention and compression:
    fitness = retention * (1 + compression_bonus)

Retention is weighted much more heavily than compression — losing
error codes or timestamps is unacceptable.
"""


def evaluate(results: dict) -> dict:
    """Compute evaluation metrics from experiment results."""
    retention = results["retention"]
    compression = results["compression"]

    # Compression bonus: 0 at full size, 0.5 at full compression
    compression_bonus = max(0, 1 - compression) * 0.5

    # Fitness: retention-weighted with compression bonus
    fitness = retention * (1 + compression_bonus)

    # Thresholds
    retention_threshold = 0.90  # must retain 90% of critical fields
    compression_threshold = 0.60  # at most 60% of original size

    passed = (
        retention >= retention_threshold
        and compression <= compression_threshold
    )

    return {
        "retention": retention,
        "compression": compression,
        "fitness": round(fitness, 4),
        "passed": passed,
        "retention_threshold": retention_threshold,
        "compression_threshold": compression_threshold,
    }
