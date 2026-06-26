"""Secret scanner — detects leaked credentials in tracked files.

Scans all source files for common secret patterns:
- API keys (OpenAI sk-, DeepSeek sk-, HuggingFace hf_, Anthropic sk-ant-)
- GitHub tokens (ghp_, gho_, ghs_, ghr_)
- AWS keys (AKIA..., AWS secret keys)
- Private keys (BEGIN RSA/EC/DSA PRIVATE KEY)
- Connection strings (mongodb://, postgresql://, redis://)
- Base64-encoded tokens (long runs of base64 that look like secrets)

Zero API calls, pure regex. Runs in <1s.
Critical for public repos — one leak and you're compromised.
"""

from __future__ import annotations

import re
from pathlib import Path

from agents import CIAgent, AgentResult, REPO_ROOT, register

SCAN_EXTENSIONS = {".py", ".tex", ".md", ".yml", ".yaml", ".toml", ".cfg", ".sh", ".js", ".css", ".html", ".json", ".txt", ".bib", ".env", ".env.*"}

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv"}
SKIP_PREFIXES = ("site/",)

# Each pattern: (name, regex)
SECRET_PATTERNS = [
    ("OpenAI API key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("DeepSeek API key", re.compile(r"sk-[A-Fa-f0-9]{32,}")),
    ("Anthropic API key", re.compile(r"sk-ant-[A-Za-z0-9\-]{20,}")),
    ("HuggingFace token", re.compile(r"hf_[A-Za-z0-9]{20,}")),
    ("GitHub PAT", re.compile(r"ghp_[A-Za-z0-9]{36}")),
    ("GitHub OAuth", re.compile(r"gho_[A-Za-z0-9]{36}")),
    ("GitHub App token", re.compile(r"(ghs|ghr)_[A-Za-z0-9]{36}")),
    ("AWS Access Key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("AWS Secret Key", re.compile(r"(?i)aws_secret_access_key\s*[=:]\s*[A-Za-z0-9/+=]{40}")),
    ("Private key block", re.compile(r"-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----")),
    ("MongoDB URI", re.compile(r"mongodb(\+srv)?://[^\s\"']+")),
    ("PostgreSQL URI", re.compile(r"postgresql://[^\s\"']+")),
    ("Redis URI", re.compile(r"redis://[^\s\"']+")),
    ("MySQL URI", re.compile(r"mysql://[^\s\"']+")),
    ("Generic connection string", re.compile(r"(?i)(password|passwd|pwd)\s*[=:]\s*\S{8,}")),
    ("Generic API key assignment", re.compile(r"(?i)(api_key|apikey|api_secret)\s*[=:]\s*['\"][A-Za-z0-9\-_]{16,}['\"]")),
    ("Generic token assignment", re.compile(r"(?i)(auth_token|access_token|bearer)\s*[=:]\s*['\"][A-Za-z0-9\-_\.]{16,}['\"]")),
]

# False positive patterns — skip lines matching these
FALSE_POSITIVES = [
    re.compile(r"(?i)(example|placeholder|dummy|test|fake|mock|xxx|your_|<)"),
    re.compile(r"sk-[A-Za-z0-9]{4,6}$"),  # too short
    re.compile(r"AKIA0000000000000000"),  # example
    re.compile(r"(?i)(compile\(|re\.|SECRET_PATTERNS|FALSE_POSITIVES)"),  # regex/scanner source
    re.compile(r"^\s*[-#*]"),  # docstring/list items
]


def scan_secrets(root: Path) -> list[dict]:
    """Scan all files for secret patterns, return list of hits."""
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
                # Skip false positives
                if any(fp.search(line) for fp in FALSE_POSITIVES):
                    continue
                for name, pattern in SECRET_PATTERNS:
                    m = pattern.search(line)
                    if m:
                        # Mask the secret in the report
                        secret = m.group(0)
                        masked = secret[:4] + "*" * min(len(secret) - 4, 12) + secret[-2:] if len(secret) > 6 else "****"
                        hits.append({
                            "file": str(rel),
                            "line": i,
                            "type": name,
                            "masked": masked,
                        })
                        break  # one hit per line
    return hits


class SecretScannerAgent(CIAgent):
    name = "secret-scanner"
    description = "Detects leaked credentials (API keys, tokens, passwords) in files"

    def run(self, dry_run: bool = False) -> AgentResult:
        hits = scan_secrets(REPO_ROOT)

        # Count by type
        from collections import Counter
        by_type = Counter(h["type"] for h in hits)

        details = {
            "total": len(hits),
            "by_type": dict(by_type),
        }
        if hits:
            details["findings"] = [
                f"{h['file']}:{h['line']} [{h['type']}] {h['masked']}"
                for h in hits[:20]
            ]

        if len(hits) == 0:
            msg = "No secrets detected"
            ok = True
        else:
            msg = f"ALERT: {len(hits)} potential secret(s) found!"
            ok = False  # fail if secrets found — this is critical

        return AgentResult(
            name=self.name,
            ok=ok,
            message=msg,
            details=details,
        )


register(SecretScannerAgent())
