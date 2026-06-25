#!/usr/bin/env python3
"""doc_sync.py — DevOps CI bot agent for documentation synchronization.

Runs locally or in GitHub Actions. Uses DeepSeek v4-flash to review the
latest diff and auto-fix drifted README.md / _AUTHOR.md.

Usage:
    DEEPSEEK_API_KEY=sk-... python tools/doc_sync.py
    python tools/doc_sync.py --dry-run   # show what would change
"""

import json
import os
import subprocess
import sys
import urllib.request

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"  # v4-flash
MAX_TOKENS = 4096
TEMPERATURE = 0.1

SYSTEM_PROMPT = """You are a documentation assistant. A research repo just had code/paper changes.
Review the diff and update README.md and _AUTHOR.md if needed to stay accurate.

RULES:
- Only fix factual inaccuracies, broken links, missing entries in tables
- Do NOT add marketing fluff or unnecessary explanations
- Keep the existing tone: concise, technical, honest
- If nothing needs changing, output NOTHING (empty response)
- If changes needed, output ONLY the changed files in this format:
  ===FILE: path/to/file===
  full file content
  ===END FILE==="""


def get_diff():
    """Get the latest commit diff stats and file list."""
    try:
        stats = subprocess.check_output(
            ["git", "diff", "HEAD~1", "--stat", "--",
             "*.tex", "*.py", "*.md", "Taskfile.yml", "flake.nix"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        files = subprocess.check_output(
            ["git", "diff", "HEAD~1", "--name-only", "--",
             "*.tex", "*.py", "*.md", "Taskfile.yml", "flake.nix"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        return stats, files
    except subprocess.CalledProcessError:
        return "", ""


def read_file(path):
    """Read a file, return empty string if missing."""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return ""


def call_deepseek(prompt, user_content, api_key):
    """Call DeepSeek chat completions API."""
    payload = json.dumps({
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_content},
        ],
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
    }).encode()

    req = urllib.request.Request(
        DEEPSEEK_API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"]


def parse_files(content):
    """Parse ===FILE: ...=== blocks from LLM response."""
    result = {}
    current_file = None
    lines = []

    for line in content.split("\n"):
        if line.startswith("===FILE: "):
            current_file = line[9:].strip()
            lines = []
        elif line.strip() == "===END FILE===":
            if current_file:
                result[current_file] = "\n".join(lines) + "\n"
            current_file = None
            lines = []
        elif current_file is not None:
            lines.append(line)

    return result


def main():
    dry_run = "--dry-run" in sys.argv

    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("No DEEPSEEK_API_KEY — skipping doc sync")
        sys.exit(0)

    stats, files = get_diff()
    if not files:
        print("No relevant changes — skipping")
        sys.exit(0)

    print(f"Changed files:\n{files}\n")

    user_content = (
        f"Changed files:\n{files}\n\n"
        f"Diff:\n{stats}\n\n"
        f"Current README.md:\n{read_file('README.md')}\n\n"
        f"Current _AUTHOR.md:\n{read_file('_AUTHOR.md')}"
    )

    print("Calling DeepSeek v4-flash...")
    response = call_deepseek(SYSTEM_PROMPT, user_content, api_key)

    if not response or not response.strip():
        print("No doc changes needed")
        sys.exit(0)

    updates = parse_files(response)
    if not updates:
        print("No doc changes needed")
        sys.exit(0)

    for path, content in updates.items():
        if dry_run:
            print(f"\n--- Would update {path} ---")
            print(content[:200] + "..." if len(content) > 200 else content)
        else:
            with open(path, "w") as f:
                f.write(content)
            print(f"Updated: {path}")

    if dry_run:
        print("\n(dry run — no files written)")
    else:
        print(f"\n{len(updates)} file(s) updated. Commit with:")
        print('  git add -A && git commit -m "docs: auto-sync [skip ci]" --no-verify')


if __name__ == "__main__":
    main()
