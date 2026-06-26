# Announcements

> Copy-paste these when ready to publish. Adapt tone per platform.

---

## X / Twitter (thread)

**Tweet 1:**
We just open-sourced an ICLR 2027 manuscript: "Asymmetric Loss Modulation Resolves the Voting Ensemble Paradox in Learned Context-Pruning Ensembles."

17 models. 8 teachers. 4 architectures. $38.95 total cost.

The paradox: adding voters to a compression ensemble makes it WORSE. We prove it and fix it. 🧵

**Tweet 2:**
The Voting Ensemble Paradox:

When checkpoints with asymmetric training-data floors vote under k-of-N drop voting, the ensemble collapses to the per-stratum weakest voter. Adding stronger voters cannot help.

We formalize this with indicator functions and conditional probabilities.

**Tweet 3:**
The fix: 3.0× asymmetric loss modulation.

3× weighted cross-entropy on critical-syntactic tokens (signal names, file paths, exit codes) — the Sapir-Whorf term. Lifts the collapse floor uniformly.

Pareto frontier: λ=3 (0.955, 15% compression) → λ=10 (0.972, 2.8%). λ=3 is the sweet spot.

**Tweet 4:**
Key finding across 17 models: label quality is the bottleneck, not model capacity or data quantity.

v15 (983 pairs, largest dataset): 0.878 (worst)
v11 (larger encoder): keep_rate collapsed to 0.517
v8 (C3 self-distillation, Qwen2.5 teacher): 0.955 ← production

**Tweet 5:**
Baselines (8-prompt heretic set):
- kompress-v8: 0.993 exact_keep_pct
- Random eviction: 0.910
- LLMLingua-2: 0.867
- TextRank: 0.599

The learned component contributes +0.083 over chance. TextRank confirms extractive summarization is unsuitable for must-keep preservation.

**Tweet 6:**
Everything is open-source:
- Paper: github.com/peterlodri-sec/longrun-eval-kompress
- Model: huggingface.co/PeetPedro/kompress-v8
- Engine: github.com/peterlodri-sec/loopkit
- Dataset: huggingface.co/datasets/PeetPedro/ultrawhale-dogfood
- Logs: pocoo.vaked.dev
- ENTHEA visualizer: kompress.vaked.dev
- Interactive paper: kompress.vaked.dev/notebook/

**Tweet 7:**
Built with the Loop Engineering paradigm (@addyosmani @cobusgreyling @LangChainAI).

The repo is also a template: `python template/scaffold.py --name "my-idea"` gives you a full research project scaffold — manuscript, loop runner, MCP server, notebook, CI, devcontainer.

Be the example you want to see in the world. 🔄

---

## HuggingFace model card (PeetPedro/kompress-v8 — update)

Add to the existing model card:

```
## Citation

If you use kompress-v8, please cite:

@software{lodri2026kompress,
  author = {Peter Lodri},
  title = {Asymmetric Loss Modulation Resolves the Voting Ensemble Paradox in Learned Context-Pruning Ensembles},
  url = {https://github.com/peterlodri-sec/longrun-eval-kompress},
  year = {2026},
  license = {Apache-2.0}
}

## Interactive demo

Try the Voting Ensemble Paradox simulator: https://kompress.vaked.dev/notebook/

Explore the full research: https://kompress.vaked.dev
```

---

## Blog post (pocoo.vaked.dev)

```html
# The loop shipped. Here's what it produced.

We closed the loop. 17 models, 8 teachers, 4 architectures, $38.95 total. The manuscript is written, the baselines are run, the paradox is proven, the fix works.

## What we built

- An ICLR 2027 manuscript proving the Voting Ensemble Paradox
- kompress-v8: a production compression model (0.993 exact_keep_pct)
- A loop-experiment-researcher template so anyone can scaffold from here
- Interactive HTML sites, a marimo notebook, an MCP server
- A genesis seal that cryptographically binds the repo state to the research contract

## What we learned

Label quality is the bottleneck. Not model capacity (v11 collapsed). Not data quantity (v15 regressed with 3x more data). Only label-quality interventions worked: self-labeling (v3→v4), C3 distillation with a Qwen teacher (v8), and the λ-ablation (v8→v17→v16).

The dead ends are the research. 11 of 17 models were dead ends. We published them all.

## What's next

The loop has stopped improving. v8 is the production model. The paradox is proven. The paper is written.

Until the next loop starts.

— peter
```

---

## Reddit (r/MachineLearning)

**Title:** [R] Asymmetric Loss Modulation Resolves the Voting Ensemble Paradox in Learned Context-Pruning Ensembles

**Body:**
We prove that multi-checkpoint voting ensembles with asymmetric training-data floors collapse to the per-stratum weakest voter under k-of-N drop voting — adding stronger voters cannot help. We formalize this via indicator functions and conditional probabilities, and introduce a 3.0× weighted cross-entropy penalty on critical-syntactic tokens as a corrective.

**Key results:**
- kompress-v8: 0.993 exact_keep_pct (vs TextRank 0.599, LLMLingua-2 0.867)
- Voting ensemble paradox: majority 2/3 collapses to 0.931 (−0.031 below best single)
- Pareto frontier: λ=3 (0.955, 15% compression) → λ=10 (0.972, 2.8%)
- 17 models, 8 teachers, 4 architectures, $38.95 total cost

**Key finding:** Label quality is the bottleneck, not model capacity or data quantity.

**Everything is open-source:**
- Paper + code: https://github.com/peterlodri-sec/longrun-eval-kompress
- Model: https://huggingface.co/PeetPedro/kompress-v8
- ENTHEA visualizer: https://kompress.vaked.dev
- Interactive paper: https://kompress.vaked.dev/notebook/

Built with the Loop Engineering paradigm (Addy Osmani, Cobus Greyling, LangChain). The repo is also a reusable template for loop-experiment-researcher projects.
