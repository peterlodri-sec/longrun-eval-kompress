# longrun-eval-kompress

> "ah and just one more this you know then I think we can close this loop [deepseek] xd"

> **ICLR 2027 manuscript** — Asymmetric Loss Modulation Resolves the Voting Ensemble Paradox in Learned Context-Pruning Ensembles.
>
> Open-source LaTeX paper + baseline scripts + marimo notebook + MCP server. Total research cost: **$38.95** ($37.19 DeepSeek + $1.76 GPU).

[![CI](https://github.com/peterlodri-sec/longrun-eval-kompress/actions/workflows/ci.yml/badge.svg)](https://github.com/peterlodri-sec/longrun-eval-kompress/actions/workflows/ci.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Built with marimo](https://img.shields.io/badge/built%20with-marimo-00d4ff.svg)](https://marimo.io)
[![Sponsor](https://img.shields.io/badge/sponsor-peterlodri--sec-ff69b4.svg)](https://github.com/sponsors/peterlodri-sec)

**[Download paper PDF](https://peterlodri-sec.github.io/longrun-eval-kompress/paper/main.pdf)** | **[Interactive notebook](https://peterlodri-sec.github.io/longrun-eval-kompress/)** | **[Experiment logs](https://pocoo.vaked.dev)**

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
| `agents/` | CI agent suite — 6 agents (citation, metrics, changelog, HF card, LaTeX, doc-sync) |
| `notebook.py` | [marimo](https://marimo.io) interactive notebook — explore the paradox, mechanisms, baselines |
| `site/` | marimo WASM export — interactive notebook running in-browser (no server) |
| `mcp_server/` | MCP server for agent interaction (7 tools + 2 CI agent tools) |
| `Taskfile.yml` | Task runner — 20+ commands for paper, site, baselines, CI, agents |
| `flake.nix` | Nix flake — reproducible dev shell with Python, LaTeX, treefmt, pre-commit hooks |
| `AGENTS.md` | Operating instructions for AI agents working in this repo |

## Interactive notebook (marimo)

This repo ships with a [marimo](https://marimo.io) notebook (`notebook.py`)
that turns the paper into an interactive experience. It's also deployed as a
standalone WASM site — no server needed:

**Live:** [peterlodri-sec.github.io/longrun-eval-kompress](https://peterlodri-sec.github.io/longrun-eval-kompress/)

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
marimo export html-wasm notebook.py -o site --no-execute
```

> marimo notebooks are pure Python, Git-friendly, and reproducible — no hidden
> state. Learn more at [marimo.io](https://marimo.io) or browse the
> [gallery](https://marimo.io/gallery/).

## Quick start

```bash
# Clone
git clone https://github.com/peterlodri-sec/longrun-eval-kompress.git
cd longrun-eval-kompress

# Option A: Nix (reproducible, all deps included)
nix develop          # enter dev shell with Python, LaTeX, task, treefmt
task paper:build     # compile PDF
task site:build      # export marimo → WASM
task ci              # run all checks

# Option B: pip + system LaTeX
pip install marimo
task paper:build     # or: cd paper && latexmk -pdf main.tex
task nb:edit         # open marimo editor

# Run baselines (takes ~30s-2min depending on model downloads)
python baselines/run_baselines.py

# Start MCP server (for agent interaction)
python mcp_server/server.py
```

See [Taskfile.yml](Taskfile.yml) for all 16 commands (`task --list`).

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
- **CI agent suite:** 6 agents (citation-guard, metric-watchdog, changelog-gen, hf-card-sync, latex-guard, doc-sync) — all advisory, never blocking
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
- [Fine-tuning Kompress: the Sapir-Whorf case](https://pocoo.vaked.dev/posts/2026-06-25-fine-tuning-kompress-sapir-whorf.html) — 3.0× penalty motivation
- [Iterative self-labeling](https://pocoo.vaked.dev/posts/2026-06-25-iterative-self-labeling.html) — v3→v4 self-labeling loop
- [Heretic adversarial eval](https://pocoo.vaked.dev/posts/2026-06-25-kompress-heretic-eval.html) — override lift 0.942→0.969
- [The silver label problem](https://pocoo.vaked.dev/posts/2026-06-25-the-silver-label-problem.html) — 28% noise floor diagnostic
- [LoopKit starter kit](https://pocoo.vaked.dev/posts/2026-06-25-loopkit.html) — open-source release
- [The loop shipped](https://pocoo.vaked.dev/posts/2026-06-25-the-loop-shipped.html) — 17 models, $38.95 total
- [Loop engineering applied](https://pocoo.vaked.dev/posts/2026-06-25-loop-engineering-applied.html) — Osmani + Anthropic patterns mapped

## License

Apache License 2.0 — see [LICENSE](LICENSE).

## Security

See [SECURITY.md](SECURITY.md).

## Genesis seal (honesty loop)

This repo carries a cryptographic genesis seal that binds the current state
to the genesis contract. Any change to the manuscript, baselines, or contract
invalidates the seal.

```bash
python tools/genesis_seal.py --verify   # check seal
python tools/genesis_seal.py            # regenerate after intentional changes
```

The seal is verified automatically in CI on every push and weekly via a
scheduled DNS link check. See [paper/disclaimer\_legal\_privacy.tex](paper/disclaimer_legal_privacy.tex) §A.3.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Citing

If you use this work, cite the repository and the paper. Click "Cite this repository" on GitHub or use the BibTeX in [CITATION.cff](CITATION.cff).

## Funding

This project follows a **decentralized open-source funding model**. No
institutional grants. Community council guides donations for infrastructure
costs. If you'd like to support this work:

**GitHub Sponsors:** https://github.com/sponsors/peterlodri-sec

## Use this as a template

This repo is a **loop-experiment-researcher** template. Scaffold a new research
project from an idea to a published manuscript:

```bash
git clone https://github.com/peterlodri-sec/longrun-eval-kompress.git my-research
cd my-research
python template/scaffold.py --name "my-research" --description "Studying X via loop Y"
```

You get: loop scaffold (STATE.md, SKILL.md, genesis.md, loop.py), LaTeX
manuscript skeleton, baseline scripts, MCP server, marimo notebook, CI
workflow, and a full devcontainer. See [template/README.md](template/README.md)
for the full guide.

Or click **"Use this template"** on GitHub to create a new repo from this one.

---

## Be the example you want to see in the world

This project is built on a simple motto: **be the example you want to see in
the world.** Every choice — open-source artifacts, real baseline numbers,
honest documentation of dead ends, $38.95 total cost, a template anyone can
clone — was made to show what's possible when you don't wait for permission,
institutional grants, or a "proper" research lab.

The kompress line has 17 models. 11 of them were dead ends. We published
them anyway. v15 had the largest dataset (983 pairs) and the worst result
(0.878). We documented it honestly. v11 had a bigger encoder and collapsed
to keep_rate 0.517. We wrote about it. The dead ends are the research — they
show what doesn't work, which is as valuable as what does, if you're honest
about it.

This repo is the example. The manuscript, the baselines, the notebook, the
MCP server, the template, the CI, the devcontainer — all of it exists so that
the next person who has an idea and a $40 budget can start from here instead
of from zero.

## Closing the loop

The loop is the goal, not the destination. This project started as an inner
loop of [ultrawhale](https://github.com/peterlodri-sec/ultrawhale), which is
an inner loop of [vaked](https://protocol.vaked.dev). The compression model
makes the outer loops cheaper to run; the outer loops produce the data that
trains the compression model. Each loop feeds the one above it and the one
below it. That's the infinite goal — not a paper, not a product, but a
self-reinforcing cycle that gets better every iteration.

The correctable loop invariant says: if the metric doesn't improve in 3
iterations, stop. The loop has stopped improving for now. v8 is the production
model. The paradox is proven. The fix works. The paper is written.

Until the next loop starts.

---

<p align="center">
  <sub>Built with the <a href="https://addyosmani.com/blog/loop-engineering/">Loop Engineering</a> paradigm.<br>
  <em>Be the example you want to see in the world.</em><br>
  Research cost: $37.19 (DeepSeek API) + $1.76 (GPU compute) = <strong>$38.95</strong>.<br>
  Support this project on <a href="https://github.com/sponsors/peterlodri-sec">GitHub Sponsors</a>.</sub>
</p>
