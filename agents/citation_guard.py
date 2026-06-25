"""Citation guard — validates \\cite{} entries against CrossRef.

Checks every \\cite{key} in the manuscript against references.bib,
then hits the CrossRef API to verify DOIs exist and are resolvable.
"""

from __future__ import annotations

import json
import re
import subprocess
import urllib.request
from pathlib import Path

from agents import CIAgent, AgentResult, REPO_ROOT, register

PAPER_DIR = REPO_ROOT / "paper"
BIB_FILE = PAPER_DIR / "references.bib"
CROSSREF_API = "https://api.crossref.org/works"
USER_AGENT = "longrun-eval-kompress/1.0 (mailto:ci@peterlodri-sec.dev)"


def extract_cites(tex_dir: Path) -> set[str]:
    """Extract all \\cite{...} keys from .tex files."""
    keys = set()
    for f in tex_dir.glob("*.tex"):
        content = f.read_text()
        for m in re.finditer(r"\\cite[tp]?\{([^}]+)\}", content):
            for k in m.group(1).split(","):
                keys.add(k.strip())
    return keys


def extract_bib_keys(bib_path: Path) -> dict[str, dict]:
    """Parse .bib file, return {key: {doi, title, ...}}."""
    entries = {}
    if not bib_path.exists():
        return entries
    content = bib_path.read_text()
    for m in re.finditer(r"@\w+\{(\w+),\s*\n(.*?)\n\}", content, re.DOTALL):
        key = m.group(1)
        body = m.group(2)
        entry = {}
        for field_m in re.finditer(r"(\w+)\s*=\s*[{\"](.+?)[}\"]", body):
            entry[field_m.group(1).lower()] = field_m.group(2)
        entries[key] = entry
    return entries


def check_crossref(doi: str) -> tuple[bool, str]:
    """Query CrossRef for a DOI. Returns (ok, message)."""
    url = f"{CROSSREF_API}/{doi}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            title = data.get("message", {}).get("title", [""])[0]
            return True, f"OK — {title[:60]}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}"
    except Exception as e:
        return False, str(e)[:80]


class CitationGuard(CIAgent):
    name = "citation-guard"
    description = "Validate \\cite{} entries against CrossRef DOIs"

    def run(self, dry_run: bool = False) -> AgentResult:
        cites = extract_cites(PAPER_DIR)
        bib = extract_bib_keys(BIB_FILE)
        issues = []

        # Check for citations not in bib
        missing = cites - set(bib.keys())
        if missing:
            issues.append(f"Missing from .bib: {', '.join(sorted(missing))}")

        # Check for bib entries not cited
        orphan = set(bib.keys()) - cites
        if orphan:
            issues.append(f"Orphaned bib entries: {', '.join(sorted(orphan))}")

        # Check DOIs via CrossRef
        doi_results = {}
        for key, entry in bib.items():
            doi = entry.get("doi", "")
            if not doi:
                if key not in orphan:
                    issues.append(f"No DOI for cited entry: {key}")
                continue
            ok, msg = check_crossref(doi)
            doi_results[key] = msg
            if not ok:
                issues.append(f"DOI invalid ({key}): {msg}")

        if dry_run:
            return AgentResult(
                name=self.name, ok=len(issues) == 0,
                message=f"Would check {len(cites)} cites, {len(bib)} bib entries",
                details={"issues": issues, "doi_results": doi_results}
            )

        return AgentResult(
            name=self.name, ok=len(issues) == 0,
            message=f"{len(cites)} cites, {len(bib)} bib, {len(issues)} issues",
            details={"issues": issues, "doi_results": doi_results}
        )


register(CitationGuard())
