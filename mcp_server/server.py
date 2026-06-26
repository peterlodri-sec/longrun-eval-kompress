#!/usr/bin/env python3
"""MCP server for the longrun-eval-kompress repository.

Provides tools for agents to:
- Read manuscript sections
- Run baseline comparisons
- Query experiment results
- Get model/dataset metadata

Usage:
    python mcp_server/server.py          # stdio transport
    python mcp_server/server.py --http   # HTTP transport (port 8765)

Configure in opencode.json / .mcp.json:
    {
      "mcpServers": {
        "kompress-research": {
          "command": "python",
          "args": ["mcp_server/server.py"],
          "cwd": "/path/to/longrun-eval-kompress"
        }
      }
    }
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

REPO_ROOT = Path(__file__).parent.parent
PAPER_DIR = REPO_ROOT / "paper"
BASELINES_DIR = REPO_ROOT / "baselines"

# Import CI agents
sys.path.insert(0, str(REPO_ROOT))
import agents.citation_guard  # noqa: F401
import agents.metric_watchdog  # noqa: F401
import agents.changelog_gen  # noqa: F401
import agents.hf_card_sync  # noqa: F401
import agents.latex_guard  # noqa: F401
import agents.linker  # noqa: F401
import agents.todo_scanner  # noqa: F401
import agents.secret_scanner  # noqa: F401
import agents.zenodo_publish  # noqa: F401
from agents import list_agents, get_agent

server = Server("kompress-research")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="read_manifest",
            description="Read the manuscript structure: list all LaTeX files, their line counts, and section titles.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="read_section",
            description="Read a specific manuscript section by filename (e.g. 'methodology', 'experimental_evaluation'). Returns the full LaTeX content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "section": {
                        "type": "string",
                        "description": "Section filename without .tex (e.g. 'introduction', 'methodology', 'related_work', 'experimental_evaluation', 'loopkit_implementation', 'data_availability', 'disclaimer_legal_privacy')",
                    }
                },
                "required": ["section"],
            },
        ),
        Tool(
            name="get_baselines",
            description="Get the baseline comparison results (TextRank, LLMLingua-2, random eviction, kompress-v8) from the JSON results file.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="run_baselines",
            description="Run the baseline comparison script. This takes ~30s-2min depending on model downloads. Returns the summary table.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_model_info",
            description="Get kompress-v8 model metadata: architecture, training data, metrics, version lineage v2-v14.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="search_paper",
            description="Search the manuscript for a keyword or phrase. Returns matching lines with file and line number.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term (regex supported)"},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_repo_status",
            description="Get repository status: git log, file tree, and TODO/placeholder markers in the manuscript.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="run_ci_agent",
            description="Run a CI agent (citation-guard, metric-watchdog, changelog-gen, hf-card-sync, latex-guard, linker, todo-scanner, secret-scanner, zenodo-publish). Returns pass/fail with details.",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "description": "Agent name (citation-guard, metric-watchdog, changelog-gen, hf-card-sync, latex-guard, linker, todo-scanner, secret-scanner, zenodo-publish)",
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "If true, show what would happen without making changes",
                        "default": False,
                    },
                },
                "required": ["agent"],
            },
        ),
        Tool(
            name="list_ci_agents",
            description="List all available CI agents and their descriptions.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "read_manifest":
        return _read_manifest()
    elif name == "read_section":
        return _read_section(arguments["section"])
    elif name == "get_baselines":
        return _get_baselines()
    elif name == "run_baselines":
        return _run_baselines()
    elif name == "get_model_info":
        return _get_model_info()
    elif name == "search_paper":
        return _search_paper(arguments["query"])
    elif name == "get_repo_status":
        return _get_repo_status()
    elif name == "run_ci_agent":
        return _run_ci_agent(arguments["agent"], arguments.get("dry_run", False))
    elif name == "list_ci_agents":
        return _list_ci_agents()
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


def _read_manifest() -> list[TextContent]:
    files = sorted(PAPER_DIR.glob("*.tex"))
    lines = ["# Manuscript Structure\n"]
    for f in files:
        content = f.read_text()
        lc = len(content.splitlines())
        sections = [
            l.strip()
            for l in content.splitlines()
            if l.strip().startswith("\\section{") or l.strip().startswith("\\subsection{")
        ]
        lines.append(f"## {f.name} ({lc} lines)")
        for s in sections:
            lines.append(f"  - {s}")
        lines.append("")
    return [TextContent(type="text", text="\n".join(lines))]


def _read_section(section: str) -> list[TextContent]:
    path = PAPER_DIR / f"{section}.tex"
    if not path.exists():
        available = [f.stem for f in PAPER_DIR.glob("*.tex")]
        return [TextContent(type="text", text=f"Section '{section}' not found. Available: {available}")]
    return [TextContent(type="text", text=path.read_text())]


def _get_baselines() -> list[TextContent]:
    path = BASELINES_DIR / "baseline_results.json"
    if not path.exists():
        return [TextContent(type="text", text="No baseline results yet. Run 'run_baselines' tool first.")]
    data = json.loads(path.read_text())
    lines = ["# Baseline Results\n"]
    lines.append("| Method | exact_keep_pct | keep_rate | avg_ms |")
    lines.append("|--------|---------------|-----------|--------|")
    for name, d in data.items():
        avg = d.get("averages", {})
        if avg:
            lines.append(f"| {name} | {avg['exact_pct']:.3f} | {avg['keep_rate']:.3f} | {avg['avg_ms']:.1f} |")
    return [TextContent(type="text", text="\n".join(lines))]


def _run_baselines() -> list[TextContent]:
    script = BASELINES_DIR / "run_baselines.py"
    if not script.exists():
        return [TextContent(type="text", text="run_baselines.py not found.")]
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True, text=True, timeout=300, cwd=str(REPO_ROOT)
    )
    output = result.stdout
    if result.returncode != 0:
        output += f"\n\nSTDERR:\n{result.stderr}"
    return [TextContent(type="text", text=output[-4000:])]


def _get_model_info() -> list[TextContent]:
    info = """# kompress-v8 Model Metadata

## Architecture
- Base: answerdotai/ModernBERT-base → chopratejas/kompress-v2-base → PeetPedro/kompress-v8
- Parameters: 149M
- Heads: Token classifier (Linear 768→2) + Span CNN (Conv1d 768→256→1, GELU, Sigmoid)
- Gate: final_score = token_prob × (0.5 + 0.5 × span_score)
- Threshold: 0.5

## Training (v8)
- Method: C3 Self-Distillation (Collect-Curate-Compress)
- Teacher: Qwen2.5-7B-Instruct
- Data: 97 Qwen-labeled C3 pairs + 200 generic multi-domain (33% C3 ratio)
- Base: fine-tuned from kompress-v2-base
- Epochs: 3, Loss: 0.490 → 0.431
- Hardware: vast.ai RTX 4090
- LoRA: r=16, alpha=32, last 4/22 attention layers
- Loss: 3.0x weighted CE on must-keep tokens + 0.3 * span BCE

## Results
- Heretic exact (32p): 0.955
- keep_rate: 0.854
- override_delta: 0.000 (internalized)
- agent mk_in_ref (with override): 1.000
- Compression: 15%

## Version Lineage (v2-v14)
| Ver | Teacher | Heretic | keep_rate | Status |
|-----|---------|---------|-----------|--------|
| v2 | --- | 0.975 | 0.897 | precision ceiling |
| v3 | self-label | 0.942 | 0.728 | first self-label |
| v4 | self-label | 0.967 | 0.823 | override internalized |
| v5 | self-label | 0.961 | --- | converged |
| v6 | generator | 0.962 | 0.854 | dead end |
| v7 | sliding-window | 0.956 | 0.868 | dead end |
| v8 | Qwen2.5-7B | 0.955 | 0.854 | PRODUCTION |
| v9 | Qwen2.5-7B | 0.921 | --- | overfit |
| v10 | Qwen2.5-7B | 0.947 | 0.891 | diminishing |
| v11 | Qwen2.5-7B | 0.917 | 0.517 | capacity≠precision |
| v12 | Qwen3-Coder | 0.949 | 0.949 | too conservative |
| v13 | regex GLM | 0.951 | 0.951 | too conservative |
| v14 | council v8+GLM | 0.882 | --- | proof-of-concept |
"""
    return [TextContent(type="text", text=info)]


def _search_paper(query: str) -> list[TextContent]:
    import re
    pattern = re.compile(query, re.IGNORECASE)
    results = []
    for f in sorted(PAPER_DIR.glob("*.tex")):
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if pattern.search(line):
                results.append(f"{f.name}:{i}: {line.strip()[:120]}")
    if not results:
        return [TextContent(type="text", text=f"No matches for '{query}' in manuscript.")]
    return [TextContent(type="text", text="\n".join(results[:50]))]


def _get_repo_status() -> list[TextContent]:
    # Git log
    git_result = subprocess.run(
        ["git", "log", "--oneline", "-10"],
        capture_output=True, text=True, cwd=str(REPO_ROOT)
    )
    # File tree
    tree = []
    for f in sorted(REPO_ROOT.rglob("*")):
        if ".git" in f.parts:
            continue
        if f.is_file():
            rel = f.relative_to(REPO_ROOT)
            tree.append(str(rel))

    # Check for TODOs
    todos = []
    for f in sorted(PAPER_DIR.glob("*.tex")):
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if "TODO" in line or "\\tbd" in line:
                todos.append(f"{f.name}:{i}: {line.strip()[:100]}")

    lines = ["# Repository Status\n"]
    lines.append("## Git Log")
    lines.append(git_result.stdout or "(no commits)")
    lines.append("\n## Files")
    lines.append("\n".join(tree[:40]))
    if todos:
        lines.append("\n## TODOs/Placeholders")
        lines.append("\n".join(todos))
    else:
        lines.append("\n## TODOs/Placeholders: None")
    return [TextContent(type="text", text="\n".join(lines))]


def _run_ci_agent(agent_name: str, dry_run: bool) -> list[TextContent]:
    agent = get_agent(agent_name)
    if not agent:
        available = ", ".join(sorted(list_agents().keys()))
        return [TextContent(type="text", text=f"Unknown agent: {agent_name}\nAvailable: {available}")]
    result = agent.run(dry_run=dry_run)
    return [TextContent(type="text", text=result.to_text())]


def _list_ci_agents() -> list[TextContent]:
    agents = list_agents()
    lines = ["# CI Agents\n"]
    for name, desc in sorted(agents.items()):
        lines.append(f"- **{name}**: {desc}")
    lines.append(f"\nRun with: `run_ci_agent(agent=\"{list(agents.keys())[0]}\")`")
    return [TextContent(type="text", text="\n".join(lines))]
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
