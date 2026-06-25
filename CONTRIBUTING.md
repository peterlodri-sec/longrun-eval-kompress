# Contributing to longrun-eval-kompress

Thank you for your interest in contributing. This is an open-source academic
research project following the Loop Engineering paradigm. Contributions are
welcome in several forms.

## How to contribute

### 1. Manuscript corrections

If you find an error in the LaTeX manuscript (`paper/`):

1. Check `AGENTS.md` for the project's editing rules.
2. **Never fabricate numbers.** All metrics come from
   [pocoo.vaked.dev](https://pocoo.vaked.dev) logs or
   `baselines/baseline_results.json`.
3. Open a PR with the fix. Include the source of the corrected number.
4. Verify LaTeX environment balance before submitting:
   ```bash
   cd paper && for env in theorem proof corollary definition remark; do
     b=$(grep -c "\\\\begin{$env}" *.tex | awk -F: '{s+=$2} END{print s}')
     e=$(grep -c "\\\\end{$env}" *.tex | awk -F: '{s+=$2} END{print s}')
     echo "$env: begin=$b end=$e $([ "$b" = "$e" ] && echo OK || echo MISMATCH)"
   done
   ```

### 2. Baseline improvements

If you want to add a baseline or improve the comparison:

1. Add your baseline adapter to `baselines/run_baselines.py`.
2. Run `python baselines/run_baselines.py` from the repo root.
3. Results save to `baselines/baseline_results.json`.
4. Update the baseline table in `paper/experimental_evaluation.tex` with real numbers.
5. Open a PR with both the script change and the table update.

### 3. Notebook / MCP improvements

- **Marimo notebook:** `marimo edit notebook.py` to open the editor. Keep cells
  modular — each cell is a self-contained section.
- **MCP server:** Add tools to `mcp_server/server.py`. Test with `python mcp_server/server.py`.

### 4. New model versions (v15+)

When new kompress versions are trained:

1. Add the version to the lineage table in `paper/experimental_evaluation.tex`.
2. Update `AGENTS.md` and `mcp_server/server.py` model info if it surpasses v8.
3. Add the HuggingFace link to `LINKS.txt`.

## Git conventions

- **Commit messages:** imperative mood (e.g., "Add v15 to lineage table"), no
  AI attribution in the commit body.
- **Branch:** work on a feature branch, PR into `main`.
- **Never commit** secrets, API keys, or `.env` files.
- **The repo is PUBLIC** — all content is visible.

## Code style

- Python: follow existing style in `baselines/` and `mcp_server/`.
- LaTeX: follow existing style in `paper/`. Use `\textbf{}` for emphasis,
  `\texttt{}` for code/identifiers, `$$` for display math.
- No comments unless the code is non-obvious.

## Verification checklist before PR

- [ ] LaTeX environments balanced (see command above)
- [ ] No `\tbd` placeholders introduced (unless data is genuinely pending)
- [ ] No fabricated numbers — every metric is sourced
- [ ] `python baselines/run_baselines.py` runs without errors (if baselines changed)
- [ ] `python -c "import ast; ast.parse(open('mcp_server/server.py').read())"` passes
- [ ] No secrets, API keys, or `.env` files committed

## Disclaimer

This project uses AI-assisted authorship (Claude, GLM, Qwen2.5, DeepSeek) for
prose synthesis, code generation, and literature verification. The research
direction, experimental design, evaluation criteria, and all scientific claims
were conceived and verified by the human author. See
`paper/disclaimer_legal_privacy.tex` for the full AI authorship, privacy, and
legal policy.

Contributions that use AI assistance are welcome. Please disclose AI
assistance in your PR description (e.g., "Drafted with Claude, reviewed and
verified by me").

## Funding

This project follows a decentralized open-source funding model. No
institutional grants. If you'd like to support the project:

**GitHub Sponsors:** https://github.com/sponsors/peterlodri-sec

The community council guides donations for infrastructure costs (compute,
hosting). No editorial control over research direction or claims.

## License

By contributing, you agree that your contributions will be licensed under the
Apache License 2.0 (see `LICENSE`).
