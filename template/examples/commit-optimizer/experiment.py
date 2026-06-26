"""Experiment: analyze diffs, generate messages, score them.

Each strategy extracts different context from diffs.
The evaluation measures grammar compliance, scope accuracy,
and description quality.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from data import SAMPLE_DIFFS
from analyzer import analyze_diff, generate_commit_message, DiffAnalysis


@dataclass
class CommitStrategy:
    """Defines how to generate commit messages from diffs."""
    name: str
    use_file_type: bool = True
    use_function_names: bool = True
    use_scope: bool = True
    use_issue_refs: bool = True
    detect_breaking: bool = True
    keyword_type_detection: bool = False


CONVENTIONAL_RE = re.compile(
    r"^(feat|fix|docs|style|refactor|test|chore|perf|revert|ci|build)(\(.+\))?(!)?:\s+.+"
)


def score_message(message: str, diff: str) -> dict:
    """Score a generated commit message against conventional commit rules."""
    lines = message.strip().splitlines()
    header = lines[0] if lines else ""

    # Check conventional commit grammar
    grammar_match = bool(CONVENTIONAL_RE.match(header))

    # Check header length (max 72 chars)
    header_ok = len(header) <= 72

    # Check if scope is present
    has_scope = "(" in header and ")" in header

    # Check if body is present (good practice)
    has_body = len(lines) >= 3 and lines[1].strip() == ""

    # Check if issue refs are present
    has_refs = bool(re.search(r"#\d+", message))

    # Check if header starts with lowercase
    starts_lower = header.split(":")[0].split("(")[0].islower() if ":" in header else False

    # Score: 100 = perfect conventional commit
    score = 0
    if grammar_match:
        score += 40
    if header_ok:
        score += 20
    if has_scope:
        score += 15
    if has_body:
        score += 15
    if has_refs:
        score += 10

    return {
        "score": score,
        "grammar": grammar_match,
        "header_ok": header_ok,
        "has_scope": has_scope,
        "has_body": has_body,
        "has_refs": has_refs,
    }


def run_experiment(spec: CommitStrategy) -> dict:
    """Run the full experiment: analyze diffs -> generate messages -> score."""
    scores = []
    grammar_compliant = 0
    total = len(SAMPLE_DIFFS)

    for diff_entry in SAMPLE_DIFFS:
        if isinstance(diff_entry, tuple):
            diff_text, context = diff_entry
        else:
            diff_text = diff_entry
            context = ""

        analysis = analyze_diff(diff_text)
        message = generate_commit_message(analysis)
        result = score_message(message, diff_text)
        scores.append(result)
        if result["grammar"]:
            grammar_compliant += 1

    avg_score = sum(s["score"] for s in scores) / len(scores) if scores else 0
    avg_has_scope = sum(1 for s in scores if s["has_scope"]) / len(scores) if scores else 0
    avg_has_body = sum(1 for s in scores if s["has_body"]) / len(scores) if scores else 0

    return {
        "total_diffs": total,
        "avg_score": round(avg_score, 1),
        "grammar_compliance": round(grammar_compliant / total, 4),
        "scope_coverage": round(avg_has_scope, 4),
        "body_coverage": round(avg_has_body, 4),
    }
