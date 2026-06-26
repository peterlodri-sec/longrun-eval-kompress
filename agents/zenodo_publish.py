"""Zenodo publish — creates a Zenodo deposition from a GitHub release.

Publishes the repo archive + paper PDF to Zenodo, mints a DOI,
and returns it for embedding in the release body, README, and CITATION.cff.

Requires ZENODO_ACCESS_TOKEN env var (deposit:write + deposit:actions scopes).
Triggered by GitHub release events or manually via CLI.

Usage:
    python tools/ci_agents.py run zenodo-publish
    python tools/ci_agents.py run zenodo-publish --dry-run
"""

from __future__ import annotations

import json
import os
import subprocess
import tarfile
import tempfile
from io import BytesIO
from pathlib import Path

from agents import CIAgent, AgentResult, REPO_ROOT, register

ZENODO_API = "https://zenodo.org/api"
CITATION_FILE = REPO_ROOT / "CITATION.cff"
README_FILE = REPO_ROOT / "README.md"
LINKS_FILE = REPO_ROOT / "LINKS.txt"

METADATA = {
    "upload_type": "publication",
    "publication_type": "article",
    "title": "Asymmetric Loss Modulation Resolves the Voting Ensemble Paradox in Learned Context-Pruning Ensembles",
    "creators": [{"name": "Lodri, Peter"}],
    "description": (
        "Multi-checkpoint voting ensembles with asymmetric training-data floors "
        "collapse to the per-stratum weakest voter under k-of-N drop voting. "
        "The 3.0× heavy false-eviction penalty on critical-syntactic tokens "
        "(signal names, file paths, exit codes) resolves this by lifting the "
        "collapse floor uniformly. Production model: kompress-v8, 149M-param "
        "dual-head ModernBERT trained via C3 self-distillation."
    ),
    "access_right": "open",
    "license": "apache-2.0",
    "keywords": [
        "context-pruning", "token-compression", "ensemble", "voting-paradox",
        "modernbert", "self-distillation", "loop-engineering", "open-science",
    ],
    "related_identifiers": [
        {
            "identifier": "https://github.com/peterlodri-sec/longrun-eval-kompress",
            "relation": "isSupplementTo",
            "resource_type": "software",
        },
        {
            "identifier": "https://huggingface.co/PeetPedro/kompress-v8",
            "relation": "isSupplementTo",
            "resource_type": "dataset",
        },
        {
            "identifier": "https://kompress.vaked.dev",
            "relation": "isSupplementTo",
            "resource_type": "software",
        },
    ],
}


def _get_tag() -> str:
    """Get the latest git tag, or fall back to HEAD short hash."""
    try:
        tag = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            text=True, stderr=subprocess.DEVNULL, cwd=str(REPO_ROOT)
        ).strip()
        return tag
    except subprocess.CalledProcessError:
        head = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            text=True, stderr=subprocess.DEVNULL, cwd=str(REPO_ROOT)
        ).strip()
        return f"v0.0.0+{head}"


def _create_deposition(token: str) -> dict:
    """Create an empty Zenodo deposition with metadata."""
    import urllib.request
    import urllib.error

    meta = {**METADATA, "version": _get_tag()}
    body = json.dumps({"metadata": meta}).encode()
    req = urllib.request.Request(
        f"{ZENODO_API}/deposit/depositions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def _upload_file(token: str, bucket_url: str, filename: str, data: bytes) -> dict:
    """Upload a file to the Zenodo bucket."""
    import urllib.request

    url = f"{bucket_url}/{filename}"
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/octet-stream",
        },
        method="PUT",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def _publish(token: str, deposition_id: int) -> dict:
    """Publish the deposition and return the record with DOI."""
    import urllib.request

    url = f"{ZENODO_API}/deposit/depositions/{deposition_id}/actions/publish"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def _make_archive() -> bytes:
    """Create a tar.gz of the repo (excluding .git, site, node_modules)."""
    buf = BytesIO()
    exclude = {".git", "site", "node_modules", "__pycache__", ".mypy_cache"}
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for item in sorted(REPO_ROOT.iterdir()):
            if item.name in exclude:
                continue
            if item.is_file():
                tar.add(item, arcname=item.name)
            elif item.is_dir():
                tar.add(item, arcname=item.name)
    return buf.getvalue()


def _read_pdf() -> bytes | None:
    """Read paper/main.pdf if it exists."""
    pdf = REPO_ROOT / "paper" / "main.pdf"
    if pdf.exists():
        return pdf.read_bytes()
    return None


def _update_citation(doi: str) -> bool:
    """Add DOI to CITATION.cff if not already present."""
    if not CITATION_FILE.exists():
        return False
    content = CITATION_FILE.read_text()
    if doi in content:
        return False
    # Add doi field after version or date-released line
    if "doi:" in content:
        return False  # already has a DOI field
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line.strip().startswith("date-released:"):
            lines.insert(i + 1, f'doi: "{doi}"')
            break
    else:
        # Append before last ---
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() == "---":
                lines.insert(i, f'doi: "{doi}"')
                break
    CITATION_FILE.write_text("\n".join(lines))
    return True


def _update_readme(doi: str) -> bool:
    """Add Zenodo badge to README.md if not already present."""
    if not README_FILE.exists():
        return False
    content = README_FILE.read_text()
    badge = f"https://zenodo.org/badge/DOI/{doi}.svg"
    if badge in content or doi in content:
        return False
    # Add after the first --- or after the title
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line.strip() == "---":
            lines.insert(i, f"[![DOI](https://zenodo.org/badge/DOI/{doi}.svg)](https://doi.org/{doi})")
            lines.insert(i + 1, "")
            break
    README_FILE.write_text("\n".join(lines))
    return True


def _update_links(doi: str) -> bool:
    """Add Zenodo DOI to LINKS.txt if not already present."""
    if not LINKS_FILE.exists():
        return False
    content = LINKS_FILE.read_text()
    doi_url = f"https://doi.org/{doi}"
    if doi_url in content:
        return False
    with open(LINKS_FILE, "a") as f:
        f.write(f"\n{doi_url}")
    return True


class ZenodoPublish(CIAgent):
    name = "zenodo-publish"
    description = "Publish GitHub release to Zenodo, mint DOI, update CITATION.cff + README"

    def run(self, dry_run: bool = False) -> AgentResult:
        token = os.environ.get("ZENODO_ACCESS_TOKEN")
        if not token:
            return AgentResult(
                name=self.name, ok=False,
                message="ZENODO_ACCESS_TOKEN not set — create at https://zenodo.org/account/settings/applications/tokens/new/"
            )

        tag = _get_tag()

        if dry_run:
            return AgentResult(
                name=self.name, ok=True,
                message=f"Would publish to Zenodo as {tag}",
                details={
                    "tag": tag,
                    "metadata_title": METADATA["title"][:60] + "...",
                    "files": "repo tar.gz + paper/main.pdf",
                }
            )

        # Create deposition
        dep = _create_deposition(token)
        dep_id = dep["id"]
        bucket = dep["links"]["bucket"]

        # Upload repo archive
        archive = _make_archive()
        _upload_file(token, bucket, f"longrun-eval-kompress-{tag}.tar.gz", archive)

        # Upload paper PDF if available
        pdf = _read_pdf()
        if pdf:
            _upload_file(token, bucket, "paper.pdf", pdf)

        # Publish
        record = _publish(token, dep_id)
        doi = record.get("doi", "")
        record_id = record.get("record_id", dep_id)
        record_url = record.get("record_url", f"https://zenodo.org/record/{record_id}")

        # Update local files
        citation_updated = _update_citation(doi)
        readme_updated = _update_readme(doi)
        links_updated = _update_links(doi)

        return AgentResult(
            name=self.name, ok=True,
            message=f"Published to Zenodo: {doi}",
            details={
                "doi": doi,
                "record_url": record_url,
                "deposition_id": dep_id,
                "tag": tag,
                "citation_updated": citation_updated,
                "readme_updated": readme_updated,
                "links_updated": links_updated,
            },
            artifacts=[
                p for p, u in [
                    (CITATION_FILE, citation_updated),
                    (README_FILE, readme_updated),
                    (LINKS_FILE, links_updated),
                ] if u
            ],
        )


register(ZenodoPublish())
