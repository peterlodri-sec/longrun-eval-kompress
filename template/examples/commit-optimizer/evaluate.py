"""Evaluate: compute commit message quality and fitness."""


def evaluate(results: dict) -> dict:
    """Compute evaluation metrics from experiment results."""
    avg_score = results["avg_score"]
    grammar = results["grammar_compliance"]
    scope = results["scope_coverage"]

    # Fitness: weighted average of score and compliance
    fitness = (avg_score / 100) * 0.5 + grammar * 0.3 + scope * 0.2

    # Thresholds
    score_threshold = 60  # avg score >= 60/100
    grammar_threshold = 0.70  # 70% grammar compliance

    passed = (
        avg_score >= score_threshold
        and grammar >= grammar_threshold
    )

    return {
        "avg_score": avg_score,
        "grammar": grammar,
        "scope": scope,
        "fitness": round(fitness, 4),
        "passed": passed,
        "score_threshold": score_threshold,
        "grammar_threshold": grammar_threshold,
    }
