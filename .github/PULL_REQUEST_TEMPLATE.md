## Pull Request

### Description
<!-- What does this PR change? -->

### Type
- [ ] Bug fix
- [ ] New baseline
- [ ] Manuscript update
- [ ] Notebook / MCP / site improvement
- [ ] Template / CI / devcontainer
- [ ] Documentation

### Verification checklist
- [ ] No fabricated numbers — all metrics sourced from pocoo.vaked.dev or baseline_results.json
- [ ] LaTeX environments balanced (if paper/ changed): `cd paper && for env in theorem proof corollary definition remark; do b=$(grep -c "\\\\begin{$env}" *.tex | awk -F: '{s+=$2} END{print s}'); e=$(grep -c "\\\\end{$env}" *.tex | awk -F: '{s+=$2} END{print s}'); echo "$env: $b/$e"; done`
- [ ] Python syntax valid (if code changed): `python -c "import ast; ast.parse(open('file').read())"`
- [ ] No `\tbd` placeholders introduced (unless data is genuinely pending)
- [ ] No TODOs introduced in paper/*.tex
- [ ] No secrets, API keys, or .env files committed
- [ ] AI assistance disclosed below (if applicable)

### AI assistance
<!-- If you used AI assistance (Claude, GLM, etc.), disclose here. Example: "Drafted with Claude, reviewed and verified by me." -->

### Related issues
<!-- Link any related issues: #123 -->
