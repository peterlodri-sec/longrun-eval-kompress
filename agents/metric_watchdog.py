"""Metric watchdog — detects baseline regression across commits.

Compares the current baseline_results.json against the previous version.
Opens a GitHub issue if any metric regresses beyond a threshold.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from agents import CIAgent, AgentResult, REPO_ROOT, register

BASELINES_JSON = REPO_ROOT / "baselines" / "baseline_results.json"
REGRESSION_THRESHOLD = 0.005  # 0.5% regression triggers alert


def get_previous_baselines() -> dict | None:
    """Get baseline_results.json from HEAD~1."""
    try:
        content = subprocess.check_output(
            ["git", "show", "HEAD~1:baselines/baseline_results.json"],
            text=True, stderr=subprocess.DEVNULL, cwd=str(REPO_ROOT)
        )
        return json.loads(content)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None


def load_current_baselines() -> dict | None:
    if not BASELINES_JSON.exists():
        return None
    try:
        return json.loads(BASELINES_JSON.read_text())
    except json.JSONDecodeError:
        return None


def compare_baselines(prev: dict, curr: dict) -> list[str]:
    """Compare two baseline snapshots. Returns list of regression messages."""
    issues = []
    for method in curr:
        if method not in prev:
            continue
        for metric in ("exact_pct", "keep_rate"):
            old_val = prev[method].get("averages", {}).get(metric)
            new_val = curr[method].get("averages", {}).get(metric)
            if old_val is None or new_val is None:
                continue
            delta = new_val - old_val
            if delta < -REGRESSION_THRESHOLD:
                issues.append(
                    f"{method}.{metric}: {old_val:.3f} → {new_val:.3f} "
                    f"(regression {delta:+.3f})"
                )
    return issues


class MetricWatchdog(CIAgent):
    name = "metric-watchdog"
    description = "Detect baseline metric regressions between commits"

    def run(self, dry_run: bool = False) -> AgentResult:
        prev = get_previous_baselines()
        curr = load_current_baselines()

        if curr is None:
            return AgentResult(
                name=self.name, ok=True,
                message="No baseline_results.json found — skipping"
            )
        if prev is None:
            return AgentResult(
                name=self.name, ok=True,
                message="No previous baseline to compare against — first run"
            )

        issues = compare_baselines(prev, curr)

        if dry_run:
            return AgentResult(
                name=self.name, ok=len(issues) == 0,
                message=f"Would compare baselines, {len(issues)} regressions",
                details={"regressions": issues}
            )

        return AgentResult(
            name=self.name, ok=len(issues) == 0,
            message=f"{len(issues)} regression(s) detected" if issues else "All metrics stable",
            details={"regressions": issues}
        )


register(MetricWatchdog())
