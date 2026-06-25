#!/usr/bin/env python3
"""CLI for CI agents.

Usage:
    python tools/ci_agents.py list                # list all agents
    python tools/ci_agents.py run citation-guard   # run one agent
    python tools/ci_agents.py run-all              # run all agents
    python tools/ci_agents.py run --dry-run latex-guard  # dry run
"""

import sys
import argparse

# Ensure agents package is importable
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))

# Import all agents to trigger registration
import agents.citation_guard  # noqa: F401
import agents.metric_watchdog  # noqa: F401
import agents.changelog_gen  # noqa: F401
import agents.hf_card_sync  # noqa: F401
import agents.latex_guard  # noqa: F401

from agents import list_agents, get_agent


def cmd_list():
    for name, desc in sorted(list_agents().items()):
        print(f"  {name:20s} {desc}")


def cmd_run(name: str, dry_run: bool = False):
    agent = get_agent(name)
    if not agent:
        print(f"Unknown agent: {name}")
        print(f"Available: {', '.join(sorted(list_agents().keys()))}")
        sys.exit(1)
    result = agent.run(dry_run=dry_run)
    print(result.to_text())
    if not result.ok:
        sys.exit(1)


def cmd_run_all(dry_run: bool = False):
    failed = 0
    for name in sorted(list_agents().keys()):
        agent = get_agent(name)
        result = agent.run(dry_run=dry_run)
        print(result.to_text())
        if not result.ok:
            failed += 1
    if failed:
        print(f"\n{failed} agent(s) failed")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="CI agent runner")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List all agents")

    run_p = sub.add_parser("run", help="Run a specific agent")
    run_p.add_argument("agent", help="Agent name")
    run_p.add_argument("--dry-run", action="store_true")

    run_all_p = sub.add_parser("run-all", help="Run all agents")
    run_all_p.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if args.command == "list":
        cmd_list()
    elif args.command == "run":
        cmd_run(args.agent, args.dry_run)
    elif args.command == "run-all":
        cmd_run_all(args.dry_run)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
