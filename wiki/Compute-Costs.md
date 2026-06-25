# Compute Costs

## Breakdown

| Layer | Cost | What |
|-------|------|------|
| Outer loop (ultrawhale v1→v100) | $37.19 | DeepSeek API — the coding agent that built itself, generated the dataset |
| Inner loop (kompress v3→v17) | $1.76 | vast.ai RTX 4090 — 17 models, 8 teachers, 4 architectures |
| **Total** | **$38.95** | Less than a single conference registration |

## Per-model cost
- v3 training: ~$0.09 (15 min RTX 4090)
- v4 self-label + train: ~$0.15 (25 min)
- v5 self-label + train: ~$0.15 (25 min)
- v8 C3 distillation: ~$0.20
- Average per model: ~$0.10

## The economics
- $0.24 per release across 150 blocks (ultrawhale)
- $0.10 per model across 17 models (kompress)
- The entire research program cost less than a single industry conference registration
- No institutional grants, no corporate sponsorship — personal expenditure + decentralized open-source funding
