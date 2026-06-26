"""Evaluate: compute enrichment quality and fitness.

The fitness score balances enrichment depth (how much context we extract)
and precision (how accurate the cross-references are). Precision is
weighted more heavily -- false cross-references are worse than missing them.
"""


def evaluate(results: dict) -> dict:
    """Compute evaluation metrics from experiment results."""
    precision = results["cross_ref_precision"]
    coverage = results["multi_signal_coverage"]
    avg_signals = results["avg_signals_per_issue"]

    # Depth bonus: more signals per issue = better
    depth_bonus = min(avg_signals / 4, 0.5)  # cap at 0.5

    # Fitness: precision-weighted with depth bonus
    fitness = precision * (1 + depth_bonus) + coverage * 0.3

    # Thresholds
    precision_threshold = 0.60  # cross-ref precision >= 60%
    coverage_threshold = 0.50  # 50% of issues have 2+ signals

    passed = (
        precision >= precision_threshold
        and coverage >= coverage_threshold
    )

    return {
        "precision": precision,
        "coverage": coverage,
        "avg_signals": avg_signals,
        "fitness": round(fitness, 4),
        "passed": passed,
        "precision_threshold": precision_threshold,
        "coverage_threshold": coverage_threshold,
    }
