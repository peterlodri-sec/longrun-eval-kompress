"""Issue enricher -- regex archaeology + keyword graph.

Extracts structured context from issues using only regex and heuristics:
- Cross-references: fixes #123, closes #456, related to #789
- Code references: src/foo.py:42, function_name(), class.method()
- Labels, milestones, assignees from API response
- Time-to-first-response, time-to-close (velocity metrics)
- Keyword-based related issue detection (no embeddings needed)
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field


# --- Regex patterns ---

# Cross-references: fixes #123, closes #456, related to #789, see also #012
CROSS_REF_RE = re.compile(
    r"(?:fix(?:es|ed)?|close[sd]?|resolve[sd]?|related\s+to|see\s+also|duplicate\s+of|ref(?:erence[sd]?)?)\s*#(\d+)",
    re.IGNORECASE,
)

# Code references: src/foo.py:42, foo.py:10, app/models.py:100
FILE_REF_RE = re.compile(
    r"[\w/\\.-]+\.(?:py|js|ts|jsx|tsx|go|rs|java|rb|c|cpp|h|hpp|css|html|yaml|yml|json|toml|md):\d+"
)

# Function/method references: function_name(), Class.method(), self.foo()
FUNC_REF_RE = re.compile(
    r"\b([A-Z][a-zA-Z0-9_]*\.[a-z][a-zA-Z0-9_]*|[a-z][a-zA-Z0-9_]*(?:\.[a-z][a-zA-Z0-9_]*)*)\(\)"
)

# URLs
URL_RE = re.compile(r"https?://[^\s\)>]+")

# Error codes: E001, ERR-123, error_code_42
ERROR_CODE_RE = re.compile(r"\b(?:E\d{3}|ERR-\d+|error[_-]?\w+\d+)\b", re.IGNORECASE)

# Version references: v1.2.3, version 2.0, since v3.1
VERSION_RE = re.compile(r"\bv?\d+\.\d+(?:\.\d+)?\b")

# Stopwords for keyword extraction
STOPWORDS = {
    "the", "a", "an", "is", "it", "in", "on", "at", "to", "for", "of",
    "and", "or", "but", "not", "with", "this", "that", "was", "are", "be",
    "has", "had", "have", "do", "does", "did", "will", "would", "could",
    "should", "can", "may", "might", "i", "my", "me", "we", "our", "you",
    "your", "he", "she", "they", "them", "their", "if", "then", "else",
    "when", "where", "how", "what", "which", "who", "whom", "why",
    "just", "also", "very", "too", "so", "now", "here", "there", "than",
    "been", "being", "from", "up", "out", "about", "into", "over", "after",
    "before", "between", "under", "again", "once", "only", "same",
}


@dataclass
class EnrichedIssue:
    """Structured context extracted from an issue."""
    number: int
    title: str
    body: str
    state: str
    labels: list[str] = field(default_factory=list)
    assignees: list[str] = field(default_factory=list)
    milestone: str | None = None
    created_at: str | None = None
    closed_at: str | None = None
    comments_count: int = 0

    # Enriched fields
    cross_references: list[int] = field(default_factory=list)
    code_references: list[str] = field(default_factory=list)
    function_references: list[str] = field(default_factory=list)
    error_codes: list[str] = field(default_factory=list)
    urls: list[str] = field(default_factory=list)
    versions: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    related_issues: list[int] = field(default_factory=list)
    velocity: dict = field(default_factory=dict)


def extract_cross_references(text: str) -> list[int]:
    """Extract issue cross-references (fixes #123, closes #456, etc.)."""
    return list(set(int(m.group(1)) for m in CROSS_REF_RE.finditer(text)))


def extract_code_references(text: str) -> list[str]:
    """Extract file path references (src/foo.py:42)."""
    return list(set(m.group(0) for m in FILE_REF_RE.finditer(text)))


def extract_function_references(text: str) -> list[str]:
    """Extract function/method references (function_name(), Class.method())."""
    return list(set(m.group(1) for m in FUNC_REF_RE.finditer(text)))


def extract_error_codes(text: str) -> list[str]:
    """Extract error codes (E001, ERR-123, etc.)."""
    return list(set(m.group(0) for m in ERROR_CODE_RE.finditer(text)))


def extract_urls(text: str) -> list[str]:
    """Extract URLs from text."""
    return list(set(m.group(0) for m in URL_RE.finditer(text)))


def extract_versions(text: str) -> list[str]:
    """Extract version references."""
    return list(set(m.group(0) for m in VERSION_RE.finditer(text)))


def extract_keywords(text: str, top_n: int = 15) -> list[str]:
    """Extract top keywords by frequency (no TF-IDF needed -- simple but effective)."""
    words = re.findall(r"\b[a-z]{3,}\b", text.lower())
    words = [w for w in words if w not in STOPWORDS]
    return [word for word, _ in Counter(words).most_common(top_n)]


def compute_keyword_overlap(kw1: list[str], kw2: list[str]) -> float:
    """Compute Jaccard similarity between two keyword lists."""
    s1, s2 = set(kw1), set(kw2)
    if not s1 or not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)


def compute_velocity(issue: dict, comments: list[dict]) -> dict:
    """Compute time-to-first-response and time-to-close."""
    from datetime import datetime

    created = issue.get("created_at")
    closed = issue.get("closed_at")
    velocity = {}

    if created:
        created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))

        # Time to first response
        if comments:
            first_comment = min(
                (c.get("created_at", "") for c in comments if c.get("created_at")),
                default=None,
            )
            if first_comment:
                first_dt = datetime.fromisoformat(first_comment.replace("Z", "+00:00"))
                velocity["time_to_first_response_hours"] = round(
                    (first_dt - created_dt).total_seconds() / 3600, 1
                )

        # Time to close
        if closed:
            closed_dt = datetime.fromisoformat(closed.replace("Z", "+00:00"))
            velocity["time_to_close_hours"] = round(
                (closed_dt - created_dt).total_seconds() / 3600, 1
            )

    velocity["comments_count"] = len(comments)
    return velocity


def enrich_issue(issue: dict, comments: list[dict] | None = None) -> EnrichedIssue:
    """Enrich a single issue with all extracted context."""
    comments = comments or []
    body = issue.get("body", "") or ""
    title = issue.get("title", "")
    full_text = f"{title}\n{body}"

    # Extract all comment text for cross-references
    comment_text = "\n".join(c.get("body", "") or "" for c in comments)
    all_text = f"{full_text}\n{comment_text}"

    return EnrichedIssue(
        number=issue["number"],
        title=title,
        body=body[:500],  # truncate for display
        state=issue.get("state", "unknown"),
        labels=[l["name"] for l in issue.get("labels", [])],
        assignees=[a["login"] for a in issue.get("assignees", [])],
        milestone=issue.get("milestone", {}).get("title") if issue.get("milestone") else None,
        created_at=issue.get("created_at"),
        closed_at=issue.get("closed_at"),
        comments_count=len(comments),
        cross_references=extract_cross_references(all_text),
        code_references=extract_code_references(all_text),
        function_references=extract_function_references(all_text),
        error_codes=extract_error_codes(all_text),
        urls=extract_urls(all_text),
        versions=extract_versions(all_text),
        keywords=extract_keywords(full_text),
        velocity=compute_velocity(issue, comments),
    )


def find_related_issues(
    target: EnrichedIssue,
    candidates: list[EnrichedIssue],
    threshold: float = 0.15,
) -> list[int]:
    """Find related issues by keyword overlap (Jaccard similarity).

    This is the clever part: no embeddings, no LLM, just word overlap.
    Surprisingly effective for issue deduplication and linking.
    """
    related = []
    for candidate in candidates:
        if candidate.number == target.number:
            continue
        overlap = compute_keyword_overlap(target.keywords, candidate.keywords)
        if overlap >= threshold:
            related.append(candidate.number)
    return related
