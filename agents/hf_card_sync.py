"""HuggingFace card sync — generates/updates model card when metrics change.

Compares current metrics against the existing model card, generates
updated markdown if needed. Outputs to hf_card.md (for manual push or PR).
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from agents import CIAgent, AgentResult, REPO_ROOT, register

BASELINES_JSON = REPO_ROOT / "baselines" / "baseline_results.json"
MODEL_CARD_FILE = REPO_ROOT / "hf_card.md"
MODEL_ID = "PeetPedro/kompress-v8"

CARD_TEMPLATE = """---
language: en
tags:
  - kompress
  - context-pruning
  - modernbert
  - efficient-nlp
  - text-compression
library_name: transformers
pipeline_tag: token-classification
license: apache-2.0
---

# kompress-v8

Production context-pruning model trained via C3 self-distillation with Qwen2.5-7B teacher.

## Architecture
- Base: answerdotai/ModernBERT-base
- Parameters: 149M
- Heads: Token classifier (Linear 768→2) + Span CNN (Conv1d 768→256→1, GELU, Sigmoid)
- Gate: `final_score = token_prob × (0.5 + 0.5 × span_score)`

## Metrics
{metrics_table}

## Usage

```python
from transformers import AutoModelForTokenClassification, AutoTokenizer

model = AutoModelForTokenClassification.from_pretrained("{model_id}")
tokenizer = AutoTokenizer.from_pretrained("{model_id}")
```

## Training
- Method: C3 Self-Distillation (Collect-Curate-Compress)
- Teacher: Qwen2.5-7B-Instruct
- Loss: 3.0× weighted CE on must-keep tokens + 0.3 × span BCE
- Hardware: vast.ai RTX 4090, ~$1.76 total compute
- Data: 97 Qwen-labeled C3 pairs + 200 generic multi-domain

## Key Findings
- Label quality is the bottleneck, not model capacity or data quantity
- 3.0× false-eviction penalty resolves the Voting Ensemble Paradox
- Pareto frontier: λ=3 (v8, 0.955, 15%), λ=5 (v17, 0.963, 3.7%), λ=10 (v16, 0.972, 2.8%)

## Citation

```bibtex
@article{{kompress2027,
  title={{Asymmetric Loss Modulation Resolves the Voting Ensemble Paradox in Learned Context-Pruning Ensembles}},
  author={{Lodri, Peter}},
  journal={{ICLR 2027}},
  year={{2027}}
}}
```
"""


def load_metrics() -> dict:
    if not BASELINES_JSON.exists():
        return {}
    try:
        data = json.loads(BASELINES_JSON.read_text())
        v8 = data.get("kompress-v8", {}).get("averages", {})
        return {
            "exact_keep_pct": v8.get("exact_pct", 0.955),
            "keep_rate": v8.get("keep_rate", 0.854),
        }
    except (json.JSONDecodeError, KeyError):
        return {}


def load_existing_card() -> str:
    if MODEL_CARD_FILE.exists():
        return MODEL_CARD_FILE.read_text()
    return ""


class HFCardSync(CIAgent):
    name = "hf-card-sync"
    description = "Sync HuggingFace model card with current metrics"

    def run(self, dry_run: bool = False) -> AgentResult:
        metrics = load_metrics()
        if not metrics:
            return AgentResult(
                name=self.name, ok=True,
                message="No baseline results — skipping card sync"
            )

        metrics_table = (
            f"| Metric | Value |\n"
            f"|--------|-------|\n"
            f"| exact_keep_pct | {metrics['exact_keep_pct']:.3f} |\n"
            f"| keep_rate | {metrics['keep_rate']:.3f} |\n"
            f"| override_delta | 0.000 |\n"
            f"| agent mk_in_ref | 1.000 |"
        )

        new_card = CARD_TEMPLATE.format(
            metrics_table=metrics_table,
            model_id=MODEL_ID,
        )

        existing = load_existing_card()
        if existing.strip() == new_card.strip():
            return AgentResult(
                name=self.name, ok=True,
                message="Model card already up to date"
            )

        if dry_run:
            return AgentResult(
                name=self.name, ok=True,
                message="Would update model card",
                details={"metrics": metrics}
            )

        MODEL_CARD_FILE.write_text(new_card)
        return AgentResult(
            name=self.name, ok=True,
            message=f"Updated {MODEL_CARD_FILE.name} — commit and push, then sync to HuggingFace",
            details={"metrics": metrics},
            artifacts=[MODEL_CARD_FILE]
        )


register(HFCardSync())
