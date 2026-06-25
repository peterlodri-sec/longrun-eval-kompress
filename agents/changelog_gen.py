"""Changelog generator — auto-generates CHANGELOG.md from git log.

Reads commits since the last tag (or all commits if no tags),
groups them by type (feat/fix/docs/...), and writes CHANGELOG.md.
"""

from __future__ import annotations

import re
import subprocess
from datetime import datetime
from pathlib import Path

from agents import CIAgent, AgentResult, REPO_ROOT, register

CHANGELOG_FILE = REPO_ROOT / "CHANGELOG.md"
CATEGORIES = {
    "feat": "Added",
    "fix": "Fixed",
    "docs": "Documentation",
    "ci": "CI/CD",
    "refactor": "Changed",
    "test": "Testing",
    "chore": "Maintenance",
    "perf": "Performance",
}


def get_last_tag() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            text=True, stderr=subprocess.DEVNULL, cwd=str(REPO_ROOT)
        ).strip()
    except subprocess.CalledProcessError:
        return None


def get_commits(since: str | None = None) -> list[dict]:
    """Get commits since tag (or all)."""
    range_spec = f"{since}..HEAD" if since else "HEAD"
    try:
        log = subprocess.check_output(
            ["git", "log", range_spec, "--pretty=format:%h|%s|%ad",
             "--date=short", "--no-merges"],
            text=True, stderr=subprocess.DEVNULL, cwd=str(REPO_ROOT)
        )
    except subprocess.CalledProcessError:
        return []

    commits = []
    for line in log.strip().splitlines():
        parts = line.split("|", 2)
        if len(parts) == 3:
            commits.append({"hash": parts[0], "message": parts[1], "date": parts[2]})
    return commits


def categorize(commits: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {v: [] for v in CATEGORIES.values()}
    groups.setdefault("Other", [])
    for c in commits:
        m = re.match(r"^(\w+):", c["message"])
        prefix = m.group(1) if m else ""
        category = CATEGORIES.get(prefix, "Other")
        groups[category].append(c)
    return groups


class ChangelogGen(CIAgent):
    name = "changelog-gen"
    description = "Generate CHANGELOG.md from git log"

    def run(self, dry_run: bool = False) -> AgentResult:
        last_tag = get_last_tag()
        commits = get_commits(last_tag)
        if not commits:
            return AgentResult(
                name=self.name, ok=True,
                message="No commits since last tag — nothing to generate"
            )

        groups = categorize(commits)
        today = datetime.now().strftime("%Y-%m-%d")
        header = f"## [{today}] — {last_tag or 'initial'}\n\n"

        sections = []
        for category, items in groups.items():
            if not items:
                continue
            lines = [f"### {category}\n"]
            for c in items:
                lines.append(f"- {c['message']} (`{c['hash']}`)")
            sections.append("\n".join(lines))

        content = f"# Changelog\n\n{header}" + "\n\n".join(sections) + "\n"

        if dry_run:
            return AgentResult(
                name=self.name, ok=True,
                message=f"Would generate changelog: {len(commits)} commits, {len(sections)} sections",
                details={"content_preview": content[:500]}
            )

        # Prepend to existing changelog if present
        existing = ""
        if CHANGELOG_FILE.exists():
            existing = CHANGELOG_FILE.read_text()
            # Remove existing header if present
            existing = re.sub(r"^# Changelog\n\n", "", existing)

        CHANGELOG_FILE.write_text(content + "\n" + existing)

        return AgentResult(
            name=self.name, ok=True,
            message=f"Generated changelog: {len(commits)} commits → {len(sections)} sections",
            details={"commits": len(commits), "sections": len(sections)},
            artifacts=[CHANGELOG_FILE]
        )


register(ChangelogGen())
