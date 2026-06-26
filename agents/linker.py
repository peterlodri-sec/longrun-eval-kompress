"""Linker — syncs link references across the repository.

Scans all markdown/tex/py/html/txt/yml files for URLs, compares against
LINKS.txt as the canonical registry, and reports drift:

1. Link used in files but NOT in LINKS.txt → report missing
2. Link in LINKS.txt but NOT used anywhere → report orphaned
3. If dry_run=False, auto-appends missing links to LINKS.txt

Does NOT touch LINKS.txt in dry_run mode (advisory only).
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

from agents import CIAgent, AgentResult, REPO_ROOT, register

LINKS_FILE = REPO_ROOT / "LINKS.txt"

SCAN_EXTENSIONS = {".md", ".tex", ".py", ".html", ".txt", ".yml", ".yaml", ".json", ".bib", ".css", ".toml", ".cfg", ".sh"}

SKIP_PREFIXES = ("site/",)
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv"}

# URLs to never report as "missing" — API endpoints, internal refs, badges
SKIP_URLS = {
    "http://example.com",
    "http://localhost",
    "https://api.crossref.org",
    "https://api.deepseek.com",
    "https://img.shields.io",
    "https://arxiv.org/submit",
    "https://github.com/peterlodri-sec/longrun-eval-kompress.git",
    "https://github.com/peterlodri-sec/longrun-eval-kompress/actions",
    "https://github.com/peterlodri-sec/longrun-eval-kompress/blob/main/template",
    "https://github.com/peterlodri-sec/longrun-eval-kompress/issues",
    "https://github.com/peterlodri-sec/longrun-eval-kompress/security",
}

# Reference-only URLs in LINKS.txt that are NOT cited in code files
# (upstream repos, ecosystem links, dependency references)
REFERENCE_URLS = {
    "https://addyo.substack.com/p/loop-engineering",
    "https://cobusgreyling.github.io/loop-engineering/",
    "https://cobusgreyling.substack.com/p/loop-engineering",
    "https://github.com/Green-PT/honey-for-devs",
    "https://github.com/headroomlabs-ai/headroom",
    "https://github.com/headroomlabs-ai/headroom/pull/1363",
    "https://github.com/headroomlabs-ai/headroom/pull/1400",
    "https://github.com/headroomlabs-ai/headroom/pull/1418",
    "https://github.com/headroomlabs-ai/headroom/pull/1419",
    "https://github.com/peterlodri-sec",
    "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct",
    "https://huggingface.co/answerdotai/ModernBERT-base",
    "https://huggingface.co/chopratejas/kompress-v2-base",
    "https://music.vaked.dev",
    "https://vaked.dev/ultrawhale",
    "https://vaked.dev/ultrawhale/book",
    "https://vaked.dev/ultrawhale/docs",
    "https://x.com/0xp3t3rl",
}

URL_RE = re.compile(
    r"https?://[^\s\)\]\"'>\}\`\$\\]+"
)


def scan_urls(root: Path) -> dict[str, set[Path]]:
    """Scan all files for URLs, return {url: {file, ...}}."""
    urls: dict[str, set[Path]] = {}
    for ext in SCAN_EXTENSIONS:
        for f in root.rglob(f"*{ext}"):
            rel = f.relative_to(root)
            if any(d in rel.parts for d in SKIP_DIRS):
                continue
            if any(str(rel).startswith(p) for p in SKIP_PREFIXES):
                continue
            if f.name == "LINKS.txt":
                continue
            try:
                content = f.read_text(errors="replace")
            except Exception:
                continue
            for m in URL_RE.finditer(content):
                url = m.group(0).rstrip(".,;:)")
                if _should_skip_url(url):
                    continue
                urls.setdefault(url, set()).add(rel)
    return urls


def parse_links_txt(path: Path) -> dict[str, str]:
    """Parse LINKS.txt (format: 'URL — description'), return {url: description}."""
    links = {}
    if not path.exists():
        return links
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(" — ", 1)
        if len(parts) == 2:
            url = parts[0].strip()
            desc = parts[1].strip()
            if url.startswith("http"):
                links[url] = desc
    return links


def normalize_url(url: str) -> str:
    """Normalize URL for comparison (strip trailing slash). Returns empty string if invalid."""
    try:
        urlparse(url)
    except ValueError:
        return ""
    return url.rstrip("/")


def _should_skip_url(url: str) -> bool:
    """Check if URL should be skipped entirely."""
    for skip in SKIP_URLS:
        if url.startswith(skip):
            return True
    # Skip git clone URLs
    if url.endswith(".git"):
        return True
    return False


class LinkerAgent(CIAgent):
    name = "linker"
    description = "Ensures link consistency: LINKS.txt <-> file references"

    def run(self, dry_run: bool = False) -> AgentResult:
        links_txt = parse_links_txt(LINKS_FILE)
        file_urls = scan_urls(REPO_ROOT)

        registry_normalized = {}
        for u in links_txt:
            n = normalize_url(u)
            if n:
                registry_normalized[n] = u

        files_normalized = {}
        for u in file_urls:
            n = normalize_url(u)
            if n:
                files_normalized[n] = u

        # 1. Links used in files but NOT in LINKS.txt
        missing = []
        for norm, original in sorted(files_normalized.items()):
            if norm not in registry_normalized:
                files = sorted(str(p) for p in file_urls[original])
                missing.append((original, files))

        # 2. Links in LINKS.txt but NOT used anywhere (skip reference-only)
        orphaned = []
        for norm, original in sorted(registry_normalized.items()):
            if norm not in files_normalized and original not in REFERENCE_URLS:
                orphaned.append(original)

        # 3. Auto-append missing links (non-dry-run only)
        appended = []
        if not dry_run and missing:
            with open(LINKS_FILE, "a") as f:
                f.write("\n# --- auto-detected by linker agent ---\n")
                for url, _files in missing:
                    desc = _guess_desc(url)
                    f.write(f"{url} — {desc}\n")
                    appended.append(url)

        details = {
            "missing_from_links_txt": len(missing),
            "orphaned_in_links_txt": len(orphaned),
            "appended": len(appended),
        }
        if missing:
            details["missing_urls"] = [u for u, _ in missing[:15]]
        if orphaned:
            details["orphaned_urls"] = orphaned[:15]

        ok = len(missing) == 0 and len(orphaned) == 0
        msg = f"{len(missing)} missing, {len(orphaned)} orphaned"
        if appended:
            msg += f", {len(appended)} appended"
        if ok:
            msg = "All links consistent between files and LINKS.txt"

        return AgentResult(
            name=self.name,
            ok=ok,
            message=msg,
            details=details,
        )


def _guess_desc(url: str) -> str:
    """Infer a short description from a URL."""
    try:
        p = urlparse(url)
    except ValueError:
        return "unknown"
    path = p.path.rstrip("/")
    if "github.com" in url:
        parts = path.strip("/").split("/")
        if len(parts) >= 2:
            return f"{parts[-2]}/{parts[-1]}"
    if "huggingface.co" in url:
        parts = path.strip("/").split("/")
        if "datasets" in parts:
            idx = parts.index("datasets")
            return "/".join(parts[idx + 1:]) if len(parts) > idx + 1 else p.netloc
        return "/".join(parts[-2:]) if len(parts) >= 2 else p.netloc
    if path:
        return path.split("/")[-1] or p.netloc
    return p.netloc


register(LinkerAgent())
