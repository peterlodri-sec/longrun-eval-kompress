# Researcher Loop Prompt — GPU-Equipped Collaborator

> **For:** Researchers with GPU access (A100, H100, or multi-GPU RTX 4090)
> **Goal:** Extend the kompress experiment loop, close deferred baselines, and strengthen the paper for ICLR 2027
> **Cost estimate:** $5–$20 depending on experiments chosen

---

## Context

You are joining an ongoing Loop Engineering research project. The paper is
titled "Asymmetric Loss Modulation Resolves the Voting Ensemble Paradox in
Learned Context-Pruning Ensembles." The core contribution ( Voting Ensemble
Paradox proof + 3.0× fix + kompress-v8 production model) is complete. Your
job is to run the experiments we deferred due to lack of GPU infrastructure.

## What's already done

- 17 models trained (v3-v17), $38.95 total cost
- Paradox proven (Theorem 1 + Corollary 1 + Remark 1)
- Three mechanisms (A/B/C) validated
- Baselines: TextRank (0.599), LLMLingua-2 (0.867), random (0.910), kompress-v8 (0.993)
- Paper written (1688 lines, 14 tables, 2 figures)
- CI agent suite running (6 agents)

## What's deferred (your tasks)

### Task 1: AutoCompressors baseline (priority: HIGH)

AutoCompressors \citep{chevalier2023autocompressors} recurrently summarize
context into summary tokens. We cited it but couldn't run it on M1 Pro.

```bash
# Setup
pip install transformers torch
git clone https://github.com/compressa-ai/AutoCompressors.git
cd AutoCompressors

# Run on the 8-prompt heretic set
python evaluate.py \
  --model "compressa-ai/auto-compressor-llama-2-7b" \
  --prompts /path/to/heretic_prompts.jsonl \
  --output /path/to/autocompressor_results.json

# Metrics to report
# - exact_keep_pct (must-keep survival)
# - keep_rate (compression ratio)
# - avg_ms (inference latency)
```

Report results in the format of Table 10 in `paper/experimental_evaluation.tex`.

### Task 2: Gisting baseline (priority: HIGH)

Gisting \citep{mu2023gisting} trains a model to compress prompts into gist
tokens via cross-attention.

```bash
# Setup
pip install transformers torch
git clone https://github.com/Hellisothermen/Gisting.git
cd Gisting

# Run on the 8-prompt heretic set
python evaluate.py \
  --model "Naman-nitc/Gist-7B" \
  --prompts /path/to/heretic_prompts.jsonl \
  --output /path/to/gisting_results.json
```

### Task 3: v18+ experiment loop (priority: MEDIUM)

If the paradox fix generalizes, try:

1. **Different architectures:** Try DeBERTa-v3 or Longformer as backbone
2. **Different λ values:** λ=1, λ=2, λ=4, λ=7 to fill the Pareto curve
3. **Larger teacher:** Try Qwen2.5-14B or Qwen3-Coder as C3 teacher
4. **More data:** Generate 500+ C3 pairs from ultrawhale loop

For each experiment:
```bash
# Use LoopKit
cd /path/to/loopkit
python -m loop.kompress.run \
  --teacher "qwen2.5-14b" \
  --lambda 4.0 \
  --pairs 300 \
  --output /path/to/v18_results/
```

### Task 4: Adversarial stress test (priority: LOW)

Run kompress-v8 on harder prompts:
- Legal contracts (dense clause references)
- Medical records (dosage numbers, ICD codes)
- Financial statements (account numbers, percentages)
- Source code (function names, line numbers, error codes)

Report per-domain exact_keep_pct.

## How to report results

1. Add results to `baselines/baseline_results.json`
2. Update `paper/experimental_evaluation.tex` tables
3. Update `paper/references.bib` if new citations needed
4. Commit with conventional format: `feat(eval): add AutoCompressors baseline`
5. The CI agent suite will auto-validate (citation-guard, metric-watchdog)

## Constraints

- **Never fabricate numbers.** All metrics must come from actual runs.
- **Honest documentation.** If an experiment fails, document why.
- **Cost tracking.** Log GPU hours in `paper/data_availability.tex`.
- **The paradox is the star.** Don't let baseline数量 dilute the core claim.

## Getting started

```bash
git clone https://github.com/peterlodri-sec/longrun-eval-kompress.git
cd longrun-eval-kompress
pip install -r baselines/requirements.txt  # if exists
python baselines/run_baselines.py          # verify current state
```

## Contact

Open a GitHub issue: https://github.com/peterlodri-sec/longrun-eval-kompress/issues
Title: "GPU experiments: [your name]"

---

*"Be the example you want to see in the world."*
