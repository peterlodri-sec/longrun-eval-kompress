#!/usr/bin/env python3
"""Metric watchdog — validates baseline_results.json against expected thresholds.

CI gate: fails if any baseline metric regresses below the threshold.
"""
import json, sys
from pathlib import Path

RESULTS = Path("baselines/baseline_results.json")
THRESHOLDS = {
    "kompress-v8": {"avg_exact_keep_pct": 0.90},
    "textrank": {"avg_exact_keep_pct": 0.50},
    "llmlingua2": {"avg_exact_keep_pct": 0.80},
}

if not RESULTS.exists():
    print("No results file — skipping metric watchdog.")
    sys.exit(0)

data = json.loads(RESULTS.read_text())
failures = []

for key, r in data.items():
    thresholds = THRESHOLDS.get(key, {})
    for metric, min_val in thresholds.items():
        actual = r.get(metric, 0)
        if actual < min_val:
            failures.append(f"{key}.{metric}: {actual:.3f} < {min_val:.3f}")

if failures:
    print(f"❌ {len(failures)} regressions:")
    for f in failures:
        print(f"   {f}")
    sys.exit(1)
else:
    print(f"✅ All {len(data)} baselines within thresholds")
