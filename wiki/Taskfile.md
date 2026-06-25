# Taskfile

This repo uses [Task](https://taskfile.dev) as a Make alternative. All commands are defined in `Taskfile.yml`.

## Available tasks

| Task | What |
|------|------|
| `task paper:build` | Compile LaTeX → PDF |
| `task paper:clean` | Remove LaTeX build artifacts |
| `task paper:check` | Verify environments balanced, TODOs, citations |
| `task site:build` | Export marimo → WASM HTML |
| `task site:serve` | Local preview server |
| `task nb:edit` | Open marimo editor |
| `task nb:run` | Marimo read-only app |
| `task nb:check` | Lint notebook |
| `task baselines:run` | Run all baseline comparisons |
| `task mcp` | Start MCP server (stdio) |
| `task ci` | All CI checks locally |
| `task seal:verify` | Verify genesis seal |
| `task seal:update` | Regenerate genesis seal |
| `task all` | Build paper + site + verify |
| `task publish` | Commit, push, deploy |

## Quick reference

```bash
task --list              # see all commands
task paper:build         # compile PDF
task site:build          # export marimo → WASM
task ci                  # run all checks
task all                 # full rebuild
```

## Installation

```bash
# macOS
brew install go-task

# Linux (curl)
curl -sSfL https://taskfile.dev/install.sh | sh

# Nix
nix develop   # task is included in the dev shell
```

## Zsh note

The `paper:clean` task uses `2>/dev/null || true` to avoid zsh "no matches found" errors when globs don't match.
