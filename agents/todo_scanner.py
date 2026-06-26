"""Todo scanner — reports all TODO/FIXME/HACK/XXX/TBD comments.

Scans all source files for task markers and reports:
- Total count per marker type
- File locations with line numbers
- Whether any reference GitHub issues (e.g., TODO(#123))

Zero API calls, pure regex. Runs in <1s.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from agents import CIAgent, AgentResult, REPO_ROOT, register

MARKERS = {"TODO", "FIXME", "HACK", "XXX", "TBD"}

SCAN_EXTENSIONS = {".py", ".tex", ".md", ".yml", ".yaml", ".toml", ".cfg", ".sh", ".js", ".css", ".html", ".json", ".txt", ".bib"}

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv"}
SKIP_PREFIXES = ("site/",)

# Matches TODO(#123), TODO: message, TODO username: message, etc.
MARKER_RE = re.compile(
    r"\b(TODO|FIXME|HACK|XXX|TBD)\b"
    r"(?:\s*\(#(\d+)\))?"  # optional issue ref
    r"[:\s]*(.*?)"         # message (rest of line)
    r"$",
    re.IGNORECASE,
)

# GitHub issue ref pattern
ISSUE_RE = re.compile(r"#(\d+)")


def scan_todos(root: Path) -> list[dict]:
    """Scan all files for TODO markers, return list of hits."""
    hits = []
    for ext in SCAN_EXTENSIONS:
        for f in root.rglob(f"*{ext}"):
            rel = f.relative_to(root)
            if any(d in rel.parts for d in SKIP_DIRS):
                continue
            if any(str(rel).startswith(p) for p in SKIP_PREFIXES):
                continue
            try:
                lines = f.read_text(errors="replace").splitlines()
            except Exception:
                continue
            for i, line in enumerate(lines, 1):
                m = MARKER_RE.search(line)
                if m:
                    marker = m.group(1).upper()
                    issue = m.group(2)
                    msg = m.group(3).strip()
                    hits.append({
                        "file": str(rel),
                        "line": i,
                        "marker": marker,
                        "issue": f"#{issue}" if issue else None,
                        "message": msg[:80],
                    })
    return hits


class TodoScannerAgent(CIAgent):
    name = "todo-scanner"
    description = "Scans for TODO/FIXME/HACK/XXX/TBD comments across all files"

    def run(self, dry_run: bool = False) -> AgentResult:
        hits = scan_todos(REPO_ROOT)

        # Count by marker type
        by_marker = Counter(h["marker"] for h in hits)
        # Count by file
        by_file = Counter(h["file"] for h in hits)
        # Find issue refs
        issue_refs = [h for h in hits if h["issue"]]

        details = {
            "total": len(hits),
            "by_marker": dict(by_marker),
            "top_files": dict(by_file.most_common(10)),
        }
        if issue_refs:
            details["issue_refs"] = [f"{h['file']}:{h['line']} {h['issue']}" for h in issue_refs[:10]]

        if len(hits) == 0:
            msg = "No TODO/FIXME/HACK/XXX/TBD markers found"
            ok = True
        else:
            msg = f"{len(hits)} markers found ({', '.join(f'{k}={v}' for k, v in sorted(by_marker.items()))})"
            ok = True  # advisory, never fails

        return AgentResult(
            name=self.name,
            ok=ok,
            message=msg,
            details=details,
        )


register(TodoScannerAgent())
