# Template Guide

This repo is a **loop-experiment-researcher** template. Scaffold a new research project from an idea to a published manuscript.

## Quick start
```bash
git clone https://github.com/peterlodri-sec/longrun-eval-kompress.git my-research
cd my-research
python template/scaffold.py --name "my-research" --description "Studying X via loop Y"
```

Or click **"Use this template"** on GitHub.

## What you get
```
my-research/
├── loop/                   ← The loop scaffold
│   ├── STATE.md            ← Durable memory spine
│   ├── SKILL.md            ← Project conventions
│   ├── genesis.md          ← Genesis contract
│   └── loop.py             ← Four-phase runner: Plan → Execute → Evaluate → Decide
├── paper/                  ← LaTeX manuscript
├── baselines/              ← Baseline comparison scripts
├── mcp_server/             ← MCP server for agent interaction
├── notebook.py             ← Marimo interactive notebook
├── site/                   ← HTML sites
├── .github/                ← CI workflows
├── .devcontainer/          ← Full dev environment
└── ... (AGENTS.md, README, LICENSE, etc.)
```

## The workflow
1. Write the genesis contract (`loop/genesis.md`)
2. Write the skill file (`loop/SKILL.md`)
3. Run the loop: `python loop/loop.py "your hypothesis"`
4. Each iteration: Plan → Execute → Evaluate → Decide
5. The correctable loop invariant: 3 iterations, no improvement → stop
6. Write up in `paper/`

See [template/README.md](https://github.com/peterlodri-sec/longrun-eval-kompress/blob/main/template/README.md) for the full guide.
