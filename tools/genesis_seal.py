#!/usr/bin/env python3
"""Genesis seal: cryptographically bind the repo state to the genesis contract.

The genesis contract (paper/disclaimer_legal_privacy.tex §A.3, template/loop/genesis.md)
declares what the project reduces, when it stops, and what must never be sacrificed.
The seal binds that declaration to the current repo state via a SHA-256 hash of:
  1. The genesis contract text
  2. The manuscript line count + table count
  3. The baseline results JSON
  4. The git HEAD commit hash

This makes the research artifacts auditable: any change to the manuscript,
baselines, or genesis contract invalidates the seal. The seal is written to
.genesis_seal.json and can be verified by re-running this script.

Usage:
    python tools/genesis_seal.py            # generate/update seal
    python tools/genesis_seal.py --verify   # verify seal matches current state
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SEAL_FILE = REPO_ROOT / ".genesis_seal.json"


def git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, cwd=str(REPO_ROOT)
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else "missing"


def manuscript_stats() -> dict:
    paper = REPO_ROOT / "paper"
    tex_files = sorted(paper.glob("*.tex"))
    total_lines = sum(len(f.read_text().splitlines()) for f in tex_files)
    table_count = 0
    for f in tex_files:
        table_count += f.read_text().count("\\begin{table}")
    env_ok = True
    for env in ["theorem", "proof", "corollary", "definition", "remark",
                 "abstract", "document", "itemize", "table", "algorithm"]:
        b = sum(f.read_text().count(f"\\begin{{{env}}}") for f in tex_files)
        e = sum(f.read_text().count(f"\\end{{{env}}}") for f in tex_files)
        if b != e:
            env_ok = False
    return {
        "total_lines": total_lines,
        "table_count": table_count,
        "tex_file_count": len(tex_files),
        "environments_balanced": env_ok,
    }


def baseline_hash() -> str:
    return file_hash(REPO_ROOT / "baselines" / "baseline_results.json")


def genesis_contract_hash() -> str:
    """Hash the genesis contract content from the disclaimer appendix."""
    disclaimer = REPO_ROOT / "paper" / "disclaimer_legal_privacy.tex"
    if not disclaimer.exists():
        return "missing"
    content = disclaimer.read_text()
    start = content.find("\\subsection{Genesis contract")
    end = content.find("\\subsection{Adversarial evaluation")
    if start == -1 or end == -1:
        return "missing"
    contract_text = content[start:end].strip()
    return hashlib.sha256(contract_text.encode()).hexdigest()


def generate_seal() -> dict:
    stats = manuscript_stats()
    return {
        "sealed_at": datetime.now(timezone.utc).isoformat(),
        "git_head": git_head(),
        "manuscript": stats,
        "baseline_results_sha256": baseline_hash(),
        "genesis_contract_sha256": genesis_contract_hash(),
        "agents_md_sha256": file_hash(REPO_ROOT / "AGENTS.md"),
        "seal_version": "1.0.0",
    }


def compute_seal_hash(seal: dict) -> str:
    """The seal itself has a hash — bind all fields into one digest."""
    # Exclude sealed_at and seal_version from the hash (metadata, not content)
    content = {k: v for k, v in seal.items() if k not in ("sealed_at", "seal_version")}
    return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()


def verify_seal() -> bool:
    if not SEAL_FILE.exists():
        print("FAIL: No seal file found. Run `python tools/genesis_seal.py` to create one.")
        return False

    old_seal = json.loads(SEAL_FILE.read_text())
    old_hash = old_seal.pop("seal_hash", None)

    current = generate_seal()
    current_hash = compute_seal_hash(current)

    if old_hash != current_hash:
        print(f"FAIL: Seal mismatch.")
        print(f"  Sealed at:    {old_seal.get('sealed_at', 'unknown')}")
        print(f"  Sealed hash:  {old_hash}")
        print(f"  Current hash: {current_hash}")
        print(f"  Git head:     {current['git_head']}")

        # Show what changed
        for key in current:
            if key in ("sealed_at", "seal_version"):
                continue
            old_val = old_seal.get(key)
            new_val = current[key]
            if old_val != new_val:
                print(f"  CHANGED: {key}")
                print(f"    was: {json.dumps(old_val)[:100]}")
                print(f"    now: {json.dumps(new_val)[:100]}")
        return False

    print(f"OK: Seal valid. State unchanged since {old_seal.get('sealed_at', 'unknown')}.")
    print(f"  Git head: {current['git_head']}")
    print(f"  Manuscript: {current['manuscript']['total_lines']} lines, "
          f"{current['manuscript']['table_count']} tables, "
          f"envs balanced: {current['manuscript']['environments_balanced']}")
    return True


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Genesis seal: bind repo state to genesis contract.")
    ap.add_argument("--verify", action="store_true", help="Verify seal matches current state")
    args = ap.parse_args()

    if args.verify:
        ok = verify_seal()
        sys.exit(0 if ok else 1)
    else:
        seal = generate_seal()
        seal["seal_hash"] = compute_seal_hash(seal)
        SEAL_FILE.write_text(json.dumps(seal, indent=2) + "\n")
        print(f"Seal written to {SEAL_FILE}")
        print(f"  seal_hash: {seal['seal_hash']}")
        print(f"  git_head:  {seal['git_head']}")
        print(f"  manuscript: {seal['manuscript']['total_lines']} lines, "
              f"{seal['manuscript']['table_count']} tables")
        print(f"  genesis_contract_sha256: {seal['genesis_contract_sha256'][:16]}...")
        print(f"  baseline_results_sha256: {seal['baseline_results_sha256'][:16]}...")
        print(f"\nTo verify: python tools/genesis_seal.py --verify")


if __name__ == "__main__":
    main()
