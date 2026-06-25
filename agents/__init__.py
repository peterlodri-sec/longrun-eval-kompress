"""CI agent base class and registry.

All agents inherit from CIAgent and implement run(). The registry
allows CLI and MCP to discover and invoke agents by name.

Usage:
    from agents import get_agent, list_agents
    agent = get_agent("citation-guard")
    result = agent.run()
"""

from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).parent.parent


@dataclass
class AgentResult:
    """Standardized output from every CI agent."""
    name: str
    ok: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    artifacts: list[Path] = field(default_factory=list)

    def to_text(self) -> str:
        status = "PASS" if self.ok else "FAIL"
        lines = [f"[{status}] {self.name}: {self.message}"]
        for k, v in self.details.items():
            lines.append(f"  {k}: {v}")
        if self.artifacts:
            lines.append(f"  artifacts: {', '.join(str(a) for a in self.artifacts)}")
        return "\n".join(lines)


class CIAgent(ABC):
    """Base class for all CI agents."""
    name: str = "unnamed"
    description: str = ""

    @abstractmethod
    def run(self, dry_run: bool = False) -> AgentResult:
        ...

    def _git_diff(self, ref: str = "HEAD~1", *args: str) -> str:
        """Run git diff, return stdout."""
        import subprocess
        try:
            return subprocess.check_output(
                ["git", "diff", ref, *args],
                text=True, stderr=subprocess.DEVNULL, cwd=str(REPO_ROOT)
            )
        except subprocess.CalledProcessError:
            return ""

    def _git_log(self, n: int = 20) -> str:
        import subprocess
        try:
            return subprocess.check_output(
                ["git", "log", "--oneline", f"-{n}"],
                text=True, stderr=subprocess.DEVNULL, cwd=str(REPO_ROOT)
            )
        except subprocess.CalledProcessError:
            return ""


_REGISTRY: dict[str, CIAgent] = {}


def register(agent: CIAgent) -> CIAgent:
    _REGISTRY[agent.name] = agent
    return agent


def get_agent(name: str) -> CIAgent | None:
    return _REGISTRY.get(name)


def list_agents() -> dict[str, str]:
    return {k: v.description for k, v in _REGISTRY.items()}
