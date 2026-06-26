---
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
| Metric | Value |
|--------|-------|
| exact_keep_pct | 0.955 |
| keep_rate | 0.854 |
| override_delta | 0.000 |
| agent mk_in_ref | 1.000 |

## Usage

```python
from transformers import AutoModelForTokenClassification, AutoTokenizer

model = AutoModelForTokenClassification.from_pretrained("PeetPedro/kompress-v8")
tokenizer = AutoTokenizer.from_pretrained("PeetPedro/kompress-v8")
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
@article{kompress2027,
  title={Asymmetric Loss Modulation Resolves the Voting Ensemble Paradox in Learned Context-Pruning Ensembles},
  author={Lodri, Peter},
  journal={ICLR 2027},
  year={2027}
}
```
