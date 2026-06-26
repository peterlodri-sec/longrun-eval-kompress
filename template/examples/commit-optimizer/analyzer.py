"""Diff analyzer -- regex archaeology for commit message generation.

Parses git diffs to extract:
- Changed files and their types (feature, fix, test, docs, etc.)
- Added/removed lines (detect patterns like new functions, removed APIs)
- Scope (directory, module, component)
- Breaking changes (removed public functions/classes)
- Issue references (Fixes #123, Closes #456)

All regex, no LLM. Surprisingly effective.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


# --- File type detection ---

FEAT_PATTERNS = [
    re.compile(r"\.(py|js|ts|jsx|tsx|go|rs|java|rb)$"),  # source files
]
FIX_PATTERNS = [
    re.compile(r"test[s]?/"),  # test files
    re.compile(r"\.(test|spec)\.(py|js|ts)$"),
]
DOCS_PATTERNS = [
    re.compile(r"\.(md|rst|txt)$"),
    re.compile(r"docs?/"),
    re.compile(r"README"),
]
CONFIG_PATTERNS = [
    re.compile(r"(package\.json|Cargo\.toml|setup\.py|pyproject\.toml|Makefile|Dockerfile)$"),
    re.compile(r"\.(yml|yaml|toml|cfg|ini|env)$"),
    re.compile(r"\.github/"),
]
STYLE_PATTERNS = [
    re.compile(r"\.(css|scss|less|styl)$"),
    re.compile(r"\.(svg|png|jpg|ico)$"),
]

# --- Pattern detection in diff content ---

NEW_FUNCTION_RE = re.compile(
    r"^\+.*(def|function|func|fn|pub fn|async fn)\s+(\w+)",
    re.MULTILINE,
)
REMOVED_FUNCTION_RE = re.compile(
    r"^-.*(def|function|func|fn|pub fn|async fn)\s+(\w+)",
    re.MULTILINE,
)
NEW_CLASS_RE = re.compile(
    r"^\+.*(class|struct|interface|type)\s+(\w+)",
    re.MULTILINE,
)
REMOVED_CLASS_RE = re.compile(
    r"^-.*(class|struct|interface|type)\s+(\w+)",
    re.MULTILINE,
)
NEW_EXPORT_RE = re.compile(
    r"^\+.*(export|pub|public)\s+",
    re.MULTILINE,
)
ISSUE_REF_RE = re.compile(
    r"(?:fix(?:es|ed)?|close[sd]?|resolve[sd]?)\s*#(\d+)",
    re.IGNORECASE,
)
BREAKING_RE = re.compile(
    r"(?:BREAKING[- ]CHANGE|!!!|major|deprecated|removed|deleted)",
    re.IGNORECASE,
)

# Conventional commit types
TYPE_KEYWORDS = {
    "feat": ["add", "new", "create", "implement", "introduce", "support", "enable"],
    "fix": ["fix", "bug", "issue", "error", "crash", "resolve", "patch"],
    "docs": ["doc", "readme", "comment", "typo", "spelling", "grammar"],
    "style": ["format", "indent", "whitespace", "lint", "prettier", "style"],
    "refactor": ["refactor", "reorganize", "restructure", "clean", "simplify", "extract"],
    "test": ["test", "spec", "assert", "mock", "coverage", "pytest", "jest"],
    "chore": ["bump", "version", "dependabot", "renovate", "ci", "cd", "deploy"],
    "perf": ["perf", "optimize", "speed", "fast", "cache", "benchmark"],
    "revert": ["revert", "undo", "rollback", "backout"],
}


@dataclass
class DiffAnalysis:
    """Structured analysis of a git diff."""
    files_changed: list[str] = field(default_factory=list)
    file_types: dict[str, str] = field(default_factory=dict)  # file -> type
    added_lines: int = 0
    removed_lines: int = 0
    new_functions: list[str] = field(default_factory=list)
    removed_functions: list[str] = field(default_factory=list)
    new_classes: list[str] = field(default_factory=list)
    removed_classes: list[str] = field(default_factory=list)
    issue_refs: list[int] = field(default_factory=list)
    is_breaking: bool = False
    primary_type: str = "chore"
    scope: str = ""
    description: str = ""


def classify_file(filepath: str) -> str:
    """Classify a file path into a commit type."""
    for pattern in FIX_PATTERNS:
        if pattern.search(filepath):
            return "test"
    for pattern in DOCS_PATTERNS:
        if pattern.search(filepath):
            return "docs"
    for pattern in CONFIG_PATTERNS:
        if pattern.search(filepath):
            return "chore"
    for pattern in STYLE_PATTERNS:
        if pattern.search(filepath):
            return "style"
    for pattern in FEAT_PATTERNS:
        if pattern.search(filepath):
            return "feat"
    return "chore"


def extract_scope(files: list[str]) -> str:
    """Extract scope from file paths (common directory prefix)."""
    if not files:
        return ""
    if len(files) == 1:
        parts = files[0].split("/")
        if len(parts) > 1:
            return parts[-2] if parts[-1].endswith((".py", ".js", ".ts")) else parts[-1]
        return ""
    # Find common prefix
    prefix = files[0]
    for f in files[1:]:
        while not f.startswith(prefix):
            prefix = prefix[:-1]
    # Clean up to directory name
    prefix = prefix.rsplit("/", 1)[0] if "/" in prefix else ""
    return prefix.split("/")[-1] if prefix else ""


def detect_type_from_keywords(description: str) -> str:
    """Detect commit type from description keywords."""
    desc_lower = description.lower()
    scores = {}
    for commit_type, keywords in TYPE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in desc_lower)
        if score > 0:
            scores[commit_type] = score
    if scores:
        return max(scores, key=scores.get)
    return "chore"


def analyze_diff(diff_text: str) -> DiffAnalysis:
    """Full analysis of a git diff."""
    files_changed = []
    added_lines = 0
    removed_lines = 0
    all_added = []
    all_removed = []

    for line in diff_text.splitlines():
        # Detect file changes
        if line.startswith("diff --git"):
            parts = line.split(" b/", 1)
            if len(parts) > 1:
                files_changed.append(parts[1])

        # Count lines
        if line.startswith("+") and not line.startswith("+++"):
            added_lines += 1
            all_added.append(line[1:])
        elif line.startswith("-") and not line.startswith("---"):
            removed_lines += 1
            all_removed.append(line[1:])

    added_text = "\n".join(all_added)
    removed_text = "\n".join(all_removed)

    # Extract patterns
    new_functions = [m.group(2) for m in NEW_FUNCTION_RE.finditer(added_text)]
    removed_functions = [m.group(2) for m in REMOVED_FUNCTION_RE.finditer(removed_text)]
    new_classes = [m.group(2) for m in NEW_CLASS_RE.finditer(added_text)]
    removed_classes = [m.group(2) for m in REMOVED_CLASS_RE.finditer(removed_text)]
    issue_refs = [int(m.group(1)) for m in ISSUE_REF_RE.finditer(diff_text)]

    # Breaking change detection
    is_breaking = bool(BREAKING_RE.search(diff_text))
    if removed_functions or removed_classes:
        is_breaking = True

    # Classify files
    file_types = {f: classify_file(f) for f in files_changed}

    # Determine primary type
    type_counts = {}
    for ft in file_types.values():
        type_counts[ft] = type_counts.get(ft, 0) + 1
    primary_type = max(type_counts, key=type_counts.get) if type_counts else "chore"

    # Override: if functions/classes were removed, it's a fix or refactor
    if removed_functions or removed_classes:
        primary_type = "fix" if not is_breaking else "refactor"

    # Extract scope
    scope = extract_scope(files_changed)

    # Generate description from new functions/classes
    description_parts = []
    if new_functions:
        description_parts.append(f"add {', '.join(new_functions[:3])}")
    if new_classes:
        description_parts.append(f"add {', '.join(new_classes[:3])}")
    if removed_functions:
        description_parts.append(f"remove {', '.join(removed_functions[:3])}")
    if not description_parts:
        # Fallback: use first file name
        if files_changed:
            fname = files_changed[0].split("/")[-1].rsplit(".", 1)[0]
            description_parts.append(f"update {fname}")

    description = " ".join(description_parts)

    return DiffAnalysis(
        files_changed=files_changed,
        file_types=file_types,
        added_lines=added_lines,
        removed_lines=removed_lines,
        new_functions=new_functions,
        removed_functions=removed_functions,
        new_classes=new_classes,
        removed_classes=removed_classes,
        issue_refs=issue_refs,
        is_breaking=is_breaking,
        primary_type=primary_type,
        scope=scope,
        description=description,
    )


def generate_commit_message(analysis: DiffAnalysis) -> str:
    """Generate a conventional commit message from analysis."""
    type_prefix = analysis.primary_type
    if analysis.is_breaking:
        type_prefix += "!"

    scope = f"({analysis.scope})" if analysis.scope else ""
    header = f"{type_prefix}{scope}: {analysis.description}"

    # Build body
    body_parts = []
    if analysis.new_functions:
        body_parts.append(f"New functions: {', '.join(analysis.new_functions)}")
    if analysis.removed_functions:
        body_parts.append(f"Removed: {', '.join(analysis.removed_functions)}")
    if analysis.new_classes:
        body_parts.append(f"New classes: {', '.join(analysis.new_classes)}")
    if analysis.removed_classes:
        body_parts.append(f"Removed classes: {', '.join(analysis.removed_classes)}")

    body = "\n".join(body_parts) if body_parts else ""

    # Build footer
    footer = ""
    if analysis.issue_refs:
        refs = " ".join(f"#{r}" for r in analysis.issue_refs)
        footer = f"Closes {refs}"

    # Assemble
    parts = [header]
    if body:
        parts.append("")
        parts.append(body)
    if footer:
        parts.append("")
        parts.append(footer)

    return "\n".join(parts)
