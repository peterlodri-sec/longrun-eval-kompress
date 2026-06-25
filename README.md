# longrun-eval-kompress

> **ICLR 2027 manuscript** — Asymmetric Loss Modulation Resolves the Voting Ensemble Paradox in Learned Context-Pruning Ensembles.
>
> Open-source LaTeX paper + baseline scripts + marimo notebook + MCP server. Total research cost: **$38.95** ($37.19 DeepSeek + $1.76 GPU).

---

## ELI5 (Explain Like I'm 5)

Imagine you have a group of friends helping you decide which words to keep when you're shrinking a long text. Each friend is good at some things and bad at others. You think: "If I ask ALL my friends and only keep a word if they ALL agree, I'll make fewer mistakes."

**Wrong.** The friend who's worst at spotting important numbers will veto every number, even when all the other friends correctly say "keep that!" Your group ends up worse than your best friend working alone.

That's the **Voting Ensemble Paradox**. This paper proves it mathematically and shows how to fix it: penalize the friends 3x harder when they throw away important things like error codes and file paths. After the fix, everyone gets better, and the group finally works.

The fix is called **kompress-v8**. It's a small AI model (149M parameters) that decides which words to keep when compressing text for other AI agents. It preserves 99.3% of critical tokens (numbers, error names, file paths) while removing filler. The whole project cost $38.95 — less than a conference ticket.

---

## What's in this repo

| Path | What |
|------|------|
| `paper/` | LaTeX manuscript (9 files, ~1600 lines) — the actual paper |
| `baselines/` | Baseline comparison scripts + results (TextRank, LLMLingua-2, random, kompress-v8) |
| `notebook.py` | [marimo](https://marimo.io) interactive notebook — explore the paradox, mechanisms, baselines |
| `mcp_server/` | MCP server for agent interaction (7 tools) |
| `AGENTS.md` | Operating instructions for AI agents working in this repo |

## Interactive notebook (marimo)

This repo ships with a [marimo](https://marimo.io) notebook (`notebook.py`)
that turns the paper into an interactive experience:

- **Paradox simulator** — adjust k (voting threshold) and N (voters) to watch
  the ensemble collapse in real time
- **Mechanism toggle** — filter the version lineage by which mechanisms (A/B/C)
  are active
- **Baseline comparison** — live results from `baseline_results.json`
- **Silver-label table** — per-domain `mk_in_ref` showing why label quality
  is the bottleneck
- **Compute costs** — the $38.95 breakdown

```bash
# Edit mode (interactive, you can modify cells)
pip install marimo
marimo edit notebook.py

# Run mode (read-only, shareable as a web app)
marimo run notebook.py

# Export as standalone HTML (WebAssembly, no server needed)
marimo export html notebook.py -o notebook.html
```

> marimo notebooks are pure Python, Git-friendly, and reproducible — no hidden
> state. Learn more at [marimo.io](https://marimo.io) or browse the
> [gallery](https://marimo.io/gallery/).

## Quick start

```bash
# Clone
git clone https://github.com/peterlodri-sec/longrun-eval-kompress.git
cd longrun-eval-kompress

# Run baselines (takes ~30s-2min depending on model downloads)
python baselines/run_baselines.py

# Open interactive notebook (https://marimo.io)
pip install marimo
marimo edit notebook.py

# Start MCP server (for agent interaction)
python mcp_server/server.py
```

## Key results

| Method | exact_keep_pct | keep_rate | Note |
|--------|---------------|-----------|------|
| **kompress-v8 (ours)** | **0.993** | 0.936 | Production model |
| Random eviction | 0.910 | 0.835 | Floor (no learning) |
| LLMLingua-2 | 0.867 | 1.550 | keep_rate >1 (token expansion) |
| TextRank | 0.599 | 0.543 | Extractive, not token-level |

| Ensemble config | exact_keep_pct | Note |
|-----------------|---------------|------|
| v4 alone (best single) | 0.967 | — |
| Ensemble (majority 2/3) | 0.931 | **-0.031 paradox collapse** |

## Pareto frontier: loss-weight ablation

The must-keep loss weight $\lambda$ controls the precision--compression tradeoff.
v8 data held constant; only $\lambda$ varies. The frontier is monotonic and clean.

| λ | Model | Heretic exact | Compression | keep_rate | Status |
|---|-------|--------------|-------------|-----------|--------|
| **3.0** | **v8** | **0.955** | **15.0%** | **0.854** | **Production (sweet spot)** |
| 5.0 | v17 | 0.963 | 3.7% | 0.963 | Pareto middle |
| 10.0 | v16 | 0.972 | 2.8% | 0.972 | Best precision, near-zero compression |

Each +1.0 in λ buys ~0.01 heretic precision at the cost of ~10% compression.
At λ=10 the model keeps 97.2% of tokens — useless as a compressor despite
the best precision score. λ=3 (v8) is the knee of the curve.

## The three mechanisms

| Mechanism | Where | What it does |
|-----------|-------|-------------|
| **A: 3.0x penalty** | training | 3x weighted cross-entropy on must-keep tokens |
| **B: regex override** | inference | Force-keep tokens matching MUST_KEEP_RE |
| **C: self-labeling** | training | Use A+B as oracle to relabel → retrain |

## Version lineage (v2-v17, loop still running)

| Ver | Method | Heretic | Status |
|-----|--------|---------|--------|
| v2 | base | 0.975 | precision ceiling |
| v4 | self-label | 0.967 | breakthrough |
| **v8** | **Qwen2.5 C3 (λ=3)** | **0.955** | **production (15% compression)** |
| v15 | mixed (983 pairs) | 0.878 | data-scale regression |
| v16 | Qwen2.5 C3 (λ=10) | 0.972 | best precision, 2.8% compression |
| v17 | Qwen2.5 C3 (λ=5) | 0.963 | Pareto middle, 3.7% compression |

17 models trained, 8 teachers, 4 architectures, $1.76 total compute.
Key finding: **label quality is the bottleneck, not model capacity or data quantity.**

Full table in `paper/experimental_evaluation.tex` §4.9.

## External artifacts

- **Model:** [PeetPedro/kompress-v8](https://huggingface.co/PeetPedro/kompress-v8) (HuggingFace)
- **Engine:** [peterlodri-sec/loopkit](https://github.com/peterlodri-sec/loopkit) (GitHub)
- **Dataset:** [PeetPedro/ultrawhale-dogfood](https://huggingface.co/datasets/PeetPedro/ultrawhale-dogfood) (HuggingFace)
- **Outer loop:** [peterlodri-sec/ultrawhale](https://github.com/peterlodri-sec/ultrawhale) (GitHub)
- **Logs:** [pocoo.vaked.dev](https://pocoo.vaked.dev)

## Loop Engineering

This project follows the [Loop Engineering paradigm](https://addyosmani.com/blog/loop-engineering/):
- **State:** the manuscript is the state; git is the durable memory
- **Skills:** `AGENTS.md` encodes project conventions once
- **Maker/checker:** baseline script (maker) vs manuscript (checker)
- **Correctable loop:** if the metric doesn't improve in 3 iterations, stop
- **Hill climbing:** v9-v14 explored post-production; none surpassed v8

See also:
- [Cobus Greyling's reference implementation](https://github.com/cobusgreyling/loop-engineering)
- [LangChain's four-tier loop taxonomy](https://www.langchain.com/blog/the-art-of-loop-engineering)
- [LoopKit docs](https://peterlodri-sec.github.io/loopkit/)

## Wiki

For extended documentation, architectural deep-dives, and the full experiment
log, see the [pocoo.vaked.dev blog](https://pocoo.vaked.dev) — the chronological
log registry and replication vault for every experiment in this project.

Key posts:
- [Fine-tuning Kompress: the Sapir-Whorf case](https://pocoo.vaked.dev/posts/2026-06-25-fine-tuning-kompress-sapir-whorf.html)
- [Iterative self-labeling](https://pocoo.vaked.dev/posts/2026-06-25-iterative-self-labeling.html)
- [Heretic adversarial eval](https://pocoo.vaked.dev/posts/2026-06-25-kompress-heretic-eval.html)
- [The silver label problem](https://pocoo.vaked.dev/posts/2026-06-25-the-silver-label-problem.html)
- [LoopKit starter kit](https://pocoo.vaked.dev/posts/2026-06-25-loopkit.html)

## License

Apache License 2.0 — see [LICENSE](LICENSE).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). PRs welcome.

## Security

See [SECURITY.md](SECURITY.md).

## Funding

This project follows a **decentralized open-source funding model**. No
institutional grants. Community council guides donations for infrastructure
costs. If you'd like to support this work:

**GitHub Sponsors:** https://github.com/sponsors/peterlodri-sec

---

<p align="center">
  <sub>Built with the <a href="https://addyosmani.com/blog/loop-engineering/">Loop Engineering</a> paradigm.<br>
  Research cost: $37.19 (DeepSeek API) + $1.76 (GPU compute) = <strong>$38.95</strong>.<br>
  Support this project on <a href="https://github.com/sponsors/peterlodri-sec">GitHub Sponsors</a>.</sub>
</p>
