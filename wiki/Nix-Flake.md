# Nix Flake

A reproducible dev environment via [Nix flakes](https://nixos.wiki/wiki/Flakes).

## Quick start

```bash
nix develop          # enter dev shell
task --list          # see available commands
```

## What's included

- **Python 3.12** — marimo, numpy, matplotlib, sumy, nltk (+ mcp, llmlingua via pip)
- **LaTeX** — texlive with all paper deps (amsmath, natbib, hyperref, etc.)
- **task** — Taskfile runner (16 commands)
- **treefmt** — auto-formatting (nix, python, json, yaml, markdown)
- **pre-commit hooks** — ruff, trailing whitespace, private key detection
- **git, gh, curl, jq**

## Flake outputs

| Output | What |
|--------|------|
| `nix develop` | Dev shell with all tools |
| `nix run .#nb-edit` | Open marimo editor |
| `nix run .#nb-run` | Run marimo as web app |
| `nix run .#paper` | Compile LaTeX |
| `nix flake check` | Run formatting + pre-commit checks |

## Formatting

```bash
# Inside dev shell
treefmt                    # format all files
pre-commit run -a          # run all hooks manually
```

Formatters: nixpkgs-fmt, black, jsonfmt, yamlfmt, mdformat.

Excludes: `site/assets/*`, `flake.lock`, `*.lock`.

## Pre-commit hooks

Auto-activated when entering `nix develop`. Runs on `git commit`:

- treefmt (formatting)
- trailing-whitespace
- end-of-file-fixer
- check-merge-conflict
- detect-private-keys
- ruff (Python linting with --fix)

## Updating

```bash
nix flake update          # update all inputs
nix flake lock --update-input nixpkgs   # update just nixpkgs
```
