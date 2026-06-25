# AGENTS.md — longrun-eval-kompress

## Project Overview

This repository contains the ICLR 2027 manuscript for "Asymmetric Loss Modulation
Resolves the Voting Ensemble Paradox in Learned Context-Pruning Ensembles" —
a formal academic LaTeX paper about the Voting Ensemble Paradox in multi-checkpoint
compression ensembles, the 3.0× asymmetric loss modulation fix, and the kompress-v8
production model trained via C3 self-distillation.

The research was produced by the Loop Engineering paradigm (Addy Osmani, Boris Cherny,
Cobus Greyling, LangChain) using the LoopKit orchestration framework, at a total cost
of $37.19 (DeepSeek API) + $0.55 (GPU compute) = under $38.

## Repository Structure

```
longrun-eval-kompress/
├── AGENTS.md                  ← You are here (agent operating instructions)
├── notebook.py                ← Marimo interactive research paper notebook
├── paper/                     ← LaTeX manuscript (9 files, ~1600 lines)
│   ├── main.tex               ← Master file (preamble, metadata, abstract, \include)
│   ├── introduction.tex       ← §1: Sapir-Whorf framing, Loop Engineering, paradox
│   ├── related_work.tex       ← §2: 5 subsections (compression, loops, ensembles, C3)
│   ├── methodology.tex        ← §3: Paradox proof (Thm 1 + Cor 1 + Remark 1), mechanisms A/B/C
│   ├── experimental_evaluation.tex ← §4: Real data, v2-v14 lineage, baselines, threats
│   ├── loopkit_implementation.tex  ← §5: Four-phase algorithm, four-tier loop mapping
│   ├── data_availability.tex  ← §6: Artifacts, compute costs, acknowledgments
│   ├── disclaimer_legal_privacy.tex ← Appendix A: AI authorship, PII, genesis, safety
│   └── references.bib         ← Bibliography (verified + flagged entries)
├── baselines/                 ← External baseline comparison scripts
│   ├── run_baselines.py       ← Runs TextRank, LLMLingua-2, random, kompress-v8
│   └── baseline_results.json  ← Latest baseline run results
└── mcp_server/
    └── server.py              ← MCP server for agent interaction (7 tools)
```

## Key Facts

### The Thesis
Multi-checkpoint voting ensembles with asymmetric training-data floors collapse to
the per-stratum weakest voter under k-of-N drop voting. The 3.0× heavy false-eviction
penalty on critical-syntactic tokens (signal names, file paths, exit codes) resolves
this by lifting the collapse floor uniformly.

### Three Mechanisms
- **A (training-time):** 3.0× weighted cross-entropy on must-keep tokens (Sapir-Whorf term)
- **B (inference-time):** Post-inference regex override force-keeping MUST_KEEP_RE matches
- **C (training-time):** Self-labeling loop using A+B as oracle → relabel → retrain

### kompress-v8 (Production Model)
- 149M-param dual-head ModernBERT (token classifier + Span CNN)
- Trained via C3 self-distillation (Collect-Curate-Compress) with Qwen2.5-7B teacher
- Heretic exact: 0.955, keep_rate: 0.854, override_delta: 0.000, agent mk_in_ref: 1.000
- HuggingFace: PeetPedro/kompress-v8
- Pareto frontier: lambda=3 (v8, 0.955, 15%), lambda=5 (v17, 0.963, 3.7%), lambda=10 (v16, 0.972, 2.8%)
- 17 models trained (v3-v17), 8 teachers, 4 architectures, $1.76 total compute
- Key finding: label quality is the bottleneck, not model capacity or data quantity

### External Artifacts
- Model: https://huggingface.co/PeetPedro/kompress-v8
- Training engine: https://github.com/peterlodri-sec/loopkit
- Dataset: https://huggingface.co/datasets/PeetPedro/ultrawhale-dogfood
- Outer loop: https://github.com/peterlodri-sec/ultrawhale
- Experiment logs: https://pocoo.vaked.dev

## Agent Operating Instructions

### When editing the manuscript
1. **Never fabricate numbers.** All metrics come from pocoo.vaked.dev blog posts or
   the baseline_results.json file. If a number is not sourced, mark it `\tbd`.
2. **Maintain LaTeX environment balance.** Every `\begin{X}` must have `\end{X}`.
   Verify with: `grep -c '\\begin{X}' *.tex` vs `grep -c '\\end{X}' *.tex`.
3. **The proof in methodology.tex is the spine.** Theorem 1 (Voting Ensemble Paradox),
   Corollary 1 (Pareto collapse), and Remark 1 (k-of-N generalization) must remain
   mathematically consistent. If you change the assumptions, re-derive the proof.
4. **Three mechanisms must stay separated.** A (training penalty), B (inference override),
   C (self-labeling). Do not conflate them — the 0.911→0.965 table measures B, not A.
5. **v8 uses C3 self-distillation with a Qwen2.5-7B teacher**, NOT the same self-labeling
   as v3→v4. The v3-v5 chain is the paradox evidence; v8 is the production deployment.

### When running baselines
1. Run `python baselines/run_baselines.py` from the repo root.
2. The script runs TextRank, LLMLingua-2, random eviction, and kompress-v8.
3. Results save to `baselines/baseline_results.json`.
4. LLMLingua-2 may show keep_rate > 1.0 (it expands tokens with special markers) —
   this is expected behavior, document it honestly.
5. kompress-v8 loads via headroom's KompressCompressor, not AutoModelForTokenClassification.

### When using the MCP server
1. Start: `python mcp_server/server.py` (stdio) or configure in opencode.json.
2. Tools: read_manifest, read_section, get_baselines, run_baselines, get_model_info,
   search_paper, get_repo_status.
3. The server reads from the repo root; ensure you're in the right directory.

### When updating the marimo notebook
1. Run: `marimo edit notebook.py` to open the interactive editor.
2. Run: `marimo run notebook.py` for read-only sharing.
3. The notebook pulls baseline data from `baselines/baseline_results.json`.
4. Keep cells modular — each cell is a self-contained section of the paper.

### Git conventions
- Commit messages: imperative mood, no AI attribution in the commit body.
- Never commit secrets, API keys, or .env files.
- The repo is PUBLIC — all content is visible.

### Verification commands
```bash
# Check LaTeX environment balance
cd paper && for env in theorem proof corollary definition remark abstract document itemize table algorithm; do
  b=$(grep -c "\\\\begin{$env}" *.tex | awk -F: '{s+=$2} END{print s}')
  e=$(grep -c "\\\\end{$env}" *.tex | awk -F: '{s+=$2} END{print s}')
  echo "$env: begin=$b end=$e $([ "$b" = "$e" ] && echo OK || echo MISMATCH)"
done

# Check for remaining TODOs
grep -rn "TODO" paper/*.tex

# Check for unverified citations
grep -rn "VERIFY" paper/references.bib

# Run baselines
python baselines/run_baselines.py

# Start MCP server
python mcp_server/server.py

# Open marimo notebook
marimo edit notebook.py
```

## Loop Engineering Alignment

This repo follows the Loop Engineering paradigm:
- **STATE.md equivalent:** The manuscript itself is the state; git is the durable memory.
- **Skills:** This AGENTS.md is the skill file — project conventions encoded once.
- **Maker/checker:** The baseline script (maker) vs the LaTeX manuscript (checker).
- **Correctable loop invariant:** If the eval metric doesn't improve in 3 iterations, stop.
- **Hill climbing:** v9-v14 are the post-production hill-climbing loop; none surpassed v8.

## Funding

Decentralized open-source funding model. No institutional grants. Community council
guides donations for infrastructure costs. See paper/disclaimer_legal_privacy.tex §A.6.
