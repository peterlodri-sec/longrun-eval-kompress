"""Experiment: enrich issues, measure enrichment depth.

Each enrichment strategy extracts different context from issues.
The evaluation measures: cross-reference detection, code reference
extraction, related-issue linking, and velocity computation.
"""
from __future__ import annotations

from dataclasses import dataclass

from data import SAMPLE_ISSUES
from enricher import (
    EnrichedIssue,
    enrich_issue,
    find_related_issues,
)


@dataclass
class EnrichmentSpec:
    """Defines what context to extract from issues."""
    name: str
    extract_cross_refs: bool = True
    extract_code_refs: bool = True
    extract_functions: bool = True
    extract_error_codes: bool = True
    extract_keywords: bool = True
    find_related: bool = False
    related_threshold: float = 0.15
    extract_velocity: bool = True


def run_experiment(spec: EnrichmentSpec) -> dict:
    """Run the full experiment: enrich issues -> measure coverage."""
    enriched = []
    for issue in SAMPLE_ISSUES:
        e = enrich_issue(issue, comments=[])
        enriched.append(e)

    # Find related issues if enabled
    if spec.find_related:
        for e in enriched:
            e.related_issues = find_related_issues(
                e, enriched, threshold=spec.related_threshold
            )

    # Measure enrichment depth
    total = len(enriched)
    has_cross_refs = sum(1 for e in enriched if e.cross_references)
    has_code_refs = sum(1 for e in enriched if e.code_references)
    has_functions = sum(1 for e in enriched if e.function_references)
    has_error_codes = sum(1 for e in enriched if e.error_codes)
    has_keywords = sum(1 for e in enriched if e.keywords)
    has_related = sum(1 for e in enriched if e.related_issues)
    has_velocity = sum(1 for e in enriched if e.velocity.get("comments_count", 0) > 0)

    total_refs = sum(len(e.cross_references) for e in enriched)
    total_code = sum(len(e.code_references) for e in enriched)
    total_functions = sum(len(e.function_references) for e in enriched)
    total_related = sum(len(e.related_issues) for e in enriched)

    # Cross-reference coverage: how many of the extracted refs are real?
    # (In this sample data, we know the ground truth)
    known_refs = {1: [15], 3: [8, 12], 6: [11], 10: [13], 12: [3], 13: [10]}
    true_positives = 0
    false_positives = 0
    for e in enriched:
        if e.number in known_refs:
            expected = set(known_refs[e.number])
            found = set(e.cross_references)
            true_positives += len(expected & found)
            false_positives += len(found - expected)

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0

    # Coverage: % of issues with at least one enrichment signal
    signals_per_issue = []
    for e in enriched:
        signals = 0
        if e.cross_references:
            signals += 1
        if e.code_references:
            signals += 1
        if e.function_references:
            signals += 1
        if e.error_codes:
            signals += 1
        if e.keywords:
            signals += 1
        if e.related_issues:
            signals += 1
        signals_per_issue.append(signals)

    avg_signals = sum(signals_per_issue) / len(signals_per_issue) if signals_per_issue else 0
    coverage = sum(1 for s in signals_per_issue if s >= 2) / len(signals_per_issue) if signals_per_issue else 0

    return {
        "total_issues": total,
        "cross_ref_coverage": round(has_cross_refs / total, 4),
        "code_ref_coverage": round(has_code_refs / total, 4),
        "function_coverage": round(has_functions / total, 4),
        "error_code_coverage": round(has_error_codes / total, 4),
        "keyword_coverage": round(has_keywords / total, 4),
        "related_coverage": round(has_related / total, 4),
        "total_cross_refs": total_refs,
        "total_code_refs": total_code,
        "total_functions": total_functions,
        "total_related": total_related,
        "cross_ref_precision": round(precision, 4),
        "avg_signals_per_issue": round(avg_signals, 2),
        "multi_signal_coverage": round(coverage, 4),
    }
