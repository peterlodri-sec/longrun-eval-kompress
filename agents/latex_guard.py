"""LaTeX guard — compiles the manuscript and gates on errors.

Runs latexmk, parses the log for errors/warnings, and returns
a structured result. Never blocks CI (always succeeds with report).
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from agents import CIAgent, AgentResult, REPO_ROOT, register

PAPER_DIR = REPO_ROOT / "paper"
MAIN_TEX = PAPER_DIR / "main.tex"


class LatexGuard(CIAgent):
    name = "latex-guard"
    description = "Compile LaTeX manuscript and report errors/warnings"

    def run(self, dry_run: bool = False) -> AgentResult:
        if not MAIN_TEX.exists():
            return AgentResult(
                name=self.name, ok=False,
                message="main.tex not found"
            )

        if dry_run:
            return AgentResult(
                name=self.name, ok=True,
                message="Would compile paper/main.tex"
            )

        # Clean build artifacts
        subprocess.run(
            ["rm", "-f", "*.aux", "*.bbl", "*.blg", "*.log", "*.out"],
            cwd=str(PAPER_DIR), capture_output=True
        )

        # Compile
        result = subprocess.run(
            ["latexmk", "-pdf", "-interaction=nonstopmode", "main.tex"],
            capture_output=True, text=True, timeout=120, cwd=str(PAPER_DIR)
        )

        log_file = PAPER_DIR / "main.log"
        log_content = log_file.read_text() if log_file.exists() else ""

        # Parse errors and warnings
        errors = re.findall(r"^!\s+(.+)$", log_content, re.MULTILINE)
        warnings = re.findall(r"Warning", log_content, re.IGNORECASE)
        overfull = re.findall(r"Overfull", log_content)
        underfull = re.findall(r"Underfull", log_content)

        ok = result.returncode == 0 and len(errors) == 0

        details = {
            "returncode": result.returncode,
            "errors": errors[:10],
            "warnings": len(warnings),
            "overfull_hboxes": len(overfull),
            "underfull_hboxes": len(underfull),
        }

        if ok:
            msg = f"PDF compiled successfully ({len(warnings)} warnings)"
        else:
            msg = f"Compilation failed: {len(errors)} error(s), {len(warnings)} warning(s)"

        return AgentResult(
            name=self.name, ok=ok,
            message=msg,
            details=details,
            artifacts=[PAPER_DIR / "main.pdf"] if ok else []
        )


register(LatexGuard())
