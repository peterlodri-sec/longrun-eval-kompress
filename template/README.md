# loop-experiment-researcher template

> Scaffold a Loop Engineering research project from an idea to a published manuscript.
> Based on the [longrun-eval-kompress](https://github.com/peterlodri-sec/longrun-eval-kompress) project.

## Quick start

```bash
# Clone this template
git clone https://github.com/peterlodri-sec/longrun-eval-kompress.git my-research-idea
cd my-research-idea

# Scaffold your project
python template/scaffold.py --name "my-research-idea" \
  --description "Studying X via loop Y"
```

Or use GitHub's "Use this template" button, then run the scaffold script.

## What you get

```
my-research-idea/
├── loop/                   ← The loop scaffold (created by scaffold.py)
│   ├── STATE.md            ← Durable memory spine (loop state)
│   ├── SKILL.md            ← Project conventions (the skill file)
│   ├── genesis.md          ← Genesis contract (what/when/never)
│   └── loop.py             ← Four-phase runner: Plan → Execute → Evaluate → Decide
├── paper/                  ← LaTeX manuscript (the durable state)
├── baselines/              ← Baseline comparison scripts
├── mcp_server/             ← MCP server for agent interaction (7 tools)
├── notebook.py             ← Marimo interactive notebook
├── site/                   ← Single-page HTML sites (matching vaked theme)
├── .github/workflows/      ← CI: LaTeX balance, syntax, agent readiness
├── .devcontainer/          ← Full dev environment (Python, LaTeX, marimo, MCP)
├── AGENTS.md               ← Agent operating instructions
├── README.md               ← Project README (auto-renamed)
├── LINKS.txt               ← All public URLs
├── LICENSE                 ← Apache 2.0
├── CONTRIBUTING.md         ← Contribution guide
├── SECURITY.md             ← Security policy
└── llms.txt                ← LLM-optimized summary
```

## The Loop Engineering workflow

1. **Write the genesis contract** (`loop/genesis.md`): what are you reducing? when do you stop? what must never be sacrificed?
2. **Write the skill file** (`loop/SKILL.md`): define your benchmark, architecture, and training procedure.
3. **Run the loop**: `python loop/loop.py "your hypothesis"`
4. **Each iteration**: Plan → Execute → Evaluate → Decide (SHIP / RETRAIN / PIVOT)
5. **The correctable loop invariant**: if the metric doesn't improve in 3 iterations, stop and pivot.
6. **Write up**: the LaTeX manuscript in `paper/` is the durable state; git is the memory.

## What the scaffold script does

`python template/scaffold.py --name "my-idea" --description "..."`:

1. Creates a new directory with your project name
2. Copies the full template structure (paper, baselines, mcp_server, notebook, CI, devcontainer)
3. Creates `loop/` with STATE.md, SKILL.md, loop.py, genesis.md
4. Renames placeholders in README, AGENTS.md, paper/main.tex
5. Initializes git with an initial commit
6. Prints next steps

## Dev container

Open in VS Code with Dev Containers extension, or use GitHub Codespaces:

```bash
# The devcontainer includes:
# - Python 3.12 + marimo + mcp + torch + transformers + headroom
# - LaTeX (texlive) for manuscript compilation
# - VS Code extensions: Python, LaTeX Workshop, marimo, Copilot
# - Forwarded ports: 8765 (MCP), 2718 (marimo)
```

## CI workflow

The included GitHub Actions workflow checks:
- LaTeX environment balance (every `\begin{X}` has `\end{X}`)
- No TODOs or TBD placeholders in the manuscript
- Python syntax for baselines, MCP server, and notebook
- Agent readiness (AGENTS.md, MCP server, notebook, README all present)

## Based on

This template was extracted from [longrun-eval-kompress](https://github.com/peterlodri-sec/longrun-eval-kompress), an ICLR 2027 manuscript produced by the Loop Engineering paradigm for $38.95 total. The project that produced it followed exactly this workflow: genesis contract → skill file → loop iterations → manuscript → baselines → notebook → MCP server → HTML sites.

## License

Apache 2.0 — see [LICENSE](../LICENSE).
