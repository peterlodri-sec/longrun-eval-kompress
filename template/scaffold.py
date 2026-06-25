#!/usr/bin/env python3
"""Scaffold a new loop-experiment-researcher project from this template.

Usage:
    # From a fresh clone of this template:
    python template/scaffold.py --name "my-research-idea"

    # Or with a description:
    python template/scaffold.py --name "my-research-idea" --description "Studying X via loop Y"

This script:
1. Creates a new directory with your project name
2. Copies the template structure (paper/, baselines/, mcp_server/, notebook.py)
3. Renames placeholder content to your project name
4. Initializes git
5. Prints next steps

The template follows the Loop Engineering paradigm:
- paper/         → LaTeX manuscript (the durable state)
- baselines/     → Baseline comparison scripts
- mcp_server/    → MCP server for agent interaction
- notebook.py    → Marimo interactive notebook
- AGENTS.md      → Agent operating instructions (the skill file)
- .devcontainer/ → Full dev environment
- .github/       → CI workflow
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

TEMPLATE_DIR = Path(__file__).parent
REPO_ROOT = TEMPLATE_DIR.parent


def scaffold(name: str, description: str, target: Path | None = None) -> Path:
    """Create a new project from the template."""
    project_dir = target or (REPO_ROOT.parent / name)
    if project_dir.exists():
        print(f"Error: {project_dir} already exists")
        sys.exit(1)

    project_dir.mkdir(parents=True)
    print(f"Creating {project_dir}/")

    # 1. Copy the template structure
    dirs_to_copy = ["paper", "baselines", "mcp_server", "site", ".github", ".devcontainer"]
    files_to_copy = [
        "notebook.py", "AGENTS.md", "README.md", "LINKS.txt",
        "LICENSE", "CONTRIBUTING.md", "SECURITY.md", "llms.txt",
        "robots.txt", ".gitignore",
    ]

    for d in dirs_to_copy:
        src = REPO_ROOT / d
        if src.exists():
            shutil.copytree(src, project_dir / d, dirs_exist_ok=True)
            print(f"  ✓ {d}/")

    for f in files_to_copy:
        src = REPO_ROOT / f
        if src.exists():
            shutil.copy2(src, project_dir / f)
            print(f"  ✓ {f}")

    # 2. Create the loop scaffold files
    create_loop_scaffold(project_dir, name, description)

    # 3. Rename in key files
    rename_placeholders(project_dir, name, description)

    # 4. Initialize git
    subprocess.run(["git", "init"], cwd=project_dir, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=project_dir, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", f"Initial scaffold: {name}"],
        cwd=project_dir, capture_output=True
    )
    print(f"  ✓ git initialized with initial commit")

    # 5. Print next steps
    print_next_steps(project_dir, name)
    return project_dir


def create_loop_scaffold(project_dir: Path, name: str, description: str):
    """Create the loop-specific scaffold files."""
    scaffold_dir = project_dir / "loop"
    scaffold_dir.mkdir(exist_ok=True)

    # loop/STATE.md — the durable memory spine
    (scaffold_dir / "STATE.md").write_text(dedent(f"""\
        # Loop State — {name}

        > {description}

        ## Current Iteration
        - Iteration: 0
        - Hypothesis: (your first hypothesis here)
        - Status: not started

        ## History
        (empty — first run pending)

        ## Budget
        - Compute: $0.00 / $XX.XX allocated
        - Tokens: 0 / XX,XXX allocated

        ## Convergence Criteria
        - (define when the loop should stop)

        ## Correctable Loop Invariant
        If the metric does not improve in 3 iterations, stop and pivot.
        """))

    # loop/SKILL.md — the skill file (project conventions)
    (scaffold_dir / "SKILL.md").write_text(dedent(f"""\
        # Skill: {name}

        ## What this loop does
        {description}

        ## Decision rules
        1. Never fabricate numbers — all metrics must be sourced.
        2. The manuscript is the state; git is the durable memory.
        3. Maker/checker: the experiment script (maker) vs the manuscript (checker).
        4. If the metric doesn't improve in 3 iterations, stop (correctable loop invariant).
        5. Halt when budget is exhausted or convergence criteria are met.

        ## Benchmark
        - (define your evaluation metric and benchmark here)

        ## Architecture
        - (describe your model/system architecture here)

        ## Training
        - (describe your training procedure here)
        """))

    # loop/loop.py — the minimal loop runner
    (scaffold_dir / "loop.py").write_text(dedent("""\
        #!/usr/bin/env python3
        \"\"\"Minimal loop runner: Plan → Execute → Evaluate → Decide.

        This is the four-phase state machine from LoopKit.
        Each iteration runs one cycle and updates STATE.md.
        \"\"\"
        from __future__ import annotations
        import json
        from pathlib import Path
        from datetime import datetime, timezone

        STATE_FILE = Path(__file__).parent / "STATE.md"
        LOG_FILE = Path(__file__).parent / "loop_run_log.jsonl"

        def read_state() -> dict:
            \"\"\"Read the current loop state.\"\"\"
            # In a real loop, parse STATE.md or read from SQLite.
            return {"iteration": 0, "status": "not started"}

        def plan(hypothesis: str) -> dict:
            \"\"\"Phase 1: derive an experiment spec from a hypothesis.\"\"\"
            return {"hypothesis": hypothesis, "spec": "TODO: define experiment"}

        def execute(spec: dict) -> dict:
            \"\"\"Phase 2: run the experiment.\"\"\"
            print(f"  Executing: {spec['hypothesis']}")
            return {"result": "TODO: run experiment", "metrics": {}}

        def evaluate(result: dict) -> dict:
            \"\"\"Phase 3: evaluate the result against the benchmark.\"\"\"
            metrics = result.get("metrics", {})
            return {"metric": metrics.get("target", 0.0), "passed": False}

        def decide(evaluation: dict, state: dict) -> str:
            \"\"\"Phase 4: decide what to do next (SHIP / RETRAIN / PIVOT).\"\"\"
            if evaluation["passed"]:
                return "SHIP"
            if state["iteration"] >= 3:
                return "PIVOT"
            return "RETRAIN"

        def run_iteration(hypothesis: str):
            \"\"\"Run one full four-phase cycle.\"\"\"
            state = read_state()
            print(f"\\n=== Iteration {state['iteration'] + 1} ===")

            # Phase 1: Plan
            spec = plan(hypothesis)
            print(f"  Plan: {spec['hypothesis']}")

            # Phase 2: Execute
            result = execute(spec)

            # Phase 3: Evaluate
            evaluation = evaluate(result)
            print(f"  Evaluate: metric={evaluation['metric']:.3f}")

            # Phase 4: Decide
            decision = decide(evaluation, state)
            print(f"  Decide: {decision}")

            # Log
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "iteration": state["iteration"] + 1,
                "hypothesis": hypothesis,
                "metric": evaluation["metric"],
                "decision": decision,
            }
            with LOG_FILE.open("a") as f:
                f.write(json.dumps(log_entry) + "\\n")

            return decision

        if __name__ == "__main__":
            import sys
            hypothesis = sys.argv[1] if len(sys.argv) > 1 else "baseline: establish initial metric"
            decision = run_iteration(hypothesis)
            print(f"\\nLoop decision: {decision}")
            if decision == "SHIP":
                print("✓ Convergence reached. Update STATE.md and write up results.")
            elif decision == "PIVOT":
                print("→ Metric not improving. Pivot to a new hypothesis.")
            else:
                print("→ Retrain with refined hypothesis.")
        """))

    # loop/genesis.md — the genesis contract
    (scaffold_dir / "genesis.md").write_text(dedent(f"""\
        # Genesis Contract — {name}

        ## What are you reducing?
        {description}

        ## What makes an iteration valid?
        - The experiment produces a measurable metric
        - The metric is comparable to the previous iteration
        - The result is logged to loop_run_log.jsonl

        ## When do you stop?
        - The convergence criteria in STATE.md are met, OR
        - The correctable loop invariant fires (3 iterations, no improvement), OR
        - The budget is exhausted

        ## What must never be sacrificed?
        - Never fabricate numbers
        - Never skip the evaluation phase
        - Never commit secrets or API keys
        - Never remove the genesis contract
        """))

    print(f"  ✓ loop/ (STATE.md, SKILL.md, loop.py, genesis.md)")


def rename_placeholders(project_dir: Path, name: str, description: str):
    """Rename placeholder content in copied files."""
    replacements = {
        "longrun-eval-kompress": name,
        "Asymmetric Loss Modulation Resolves the Voting Ensemble Paradox in Learned Context-Pruning Ensembles": description,
        "ICLR 2027 manuscript": "Research manuscript",
    }

    files_to_update = [
        "README.md", "AGENTS.md", "CONTRIBUTING.md", "llms.txt",
        "paper/main.tex", "paper/introduction.tex",
    ]

    for fpath in files_to_update:
        full = project_dir / fpath
        if not full.exists():
            continue
        content = full.read_text()
        for old, new in replacements.items():
            content = content.replace(old, new)
        full.write_text(content)

    # Clear the baseline results (fresh project)
    baselines_json = project_dir / "baselines" / "baseline_results.json"
    if baselines_json.exists():
        baselines_json.write_text("{}\n")

    # Reset the paper to a minimal skeleton
    main_tex = project_dir / "paper" / "main.tex"
    if main_tex.exists():
        content = main_tex.read_text()
        # Keep the preamble but replace the title
        content = content.replace(
            "Asymmetric Loss Modulation Resolves the Voting Ensemble Paradox\\\\\n       in Learned Context-Pruning Ensembles",
            description.replace("\n", "\\\\") if "\n" in description else description
        )
        main_tex.write_text(content)


def print_next_steps(project_dir: Path, name: str):
    print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║  Scaffold complete: {name:<48s} ║
╚══════════════════════════════════════════════════════════════════════╝

Next steps:

  1. Enter the project:
     cd {project_dir}

  2. Edit the genesis contract:
     # Define what you're reducing, when to stop, what never to sacrifice
     vim loop/genesis.md

  3. Edit the skill file:
     # Define your benchmark, architecture, and training procedure
     vim loop/SKILL.md

  4. Run your first loop iteration:
     python loop/loop.py "baseline: establish initial metric"

  5. Open the interactive notebook:
     marimo edit notebook.py

  6. Start the MCP server (for agent interaction):
     python mcp_server/server.py

  7. Write up results in the LaTeX manuscript:
     cd paper && latexmk -pdf main.tex

  8. Create a GitHub repo and push:
     gh repo create {name} --public --source=. --push

Loop Engineering paradigm:
  • STATE.md  → the durable memory spine (loop state)
  • SKILL.md  → project conventions encoded once
  • genesis.md → what you're reducing, when to stop, what never to sacrifice
  • loop.py   → Plan → Execute → Evaluate → Decide
  • paper/    → the manuscript is the state; git is the durable memory

The correctable loop invariant: if the metric doesn't improve in 3
iterations, stop and pivot. Not slow down — stop.

Happy looping. — peterlodri-sec
""")


def main():
    ap = argparse.ArgumentParser(
        description="Scaffold a new loop-experiment-researcher project from this template."
    )
    ap.add_argument("--name", required=True, help="Project name (kebab-case, e.g. 'my-research-idea')")
    ap.add_argument("--description", default="A loop-engineering research experiment", help="One-line description")
    ap.add_argument("--target", default=None, help="Target directory (default: ../<name>)")
    args = ap.parse_args()

    # Validate name
    if not args.name.replace("-", "").replace("_", "").isalnum():
        print("Error: name must be alphanumeric with - or _ only")
        sys.exit(1)

    scaffold(args.name, args.description, Path(args.target) if args.target else None)


if __name__ == "__main__":
    main()
