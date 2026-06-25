# Changelog

All notable changes to this project are documented in this file.
Format based on [Keep a Changelog](https://keepachangelog.com/),
this project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0] — 2026-06-25

### Added
- ICLR 2027 manuscript: "Asymmetric Loss Modulation Resolves the Voting
  Ensemble Paradox in Learned Context-Pruning Ensembles"
- Full LaTeX manuscript (9 files, ~1700 lines): paradox proof (Theorem 1,
  Corollary 1, Remark 1), three mechanisms (A/B/C), dual-head architecture,
  training procedure, experimental evaluation, LoopKit implementation,
  data availability, disclaimer/legal/privacy appendix
- Baseline comparison scripts: TextRank, LLMLingua-2, random eviction,
  kompress-v8 — real runs on 8-prompt heretic set
- kompress-v8 production model: 0.993 exact_keep_pct, 0.936 keep_rate
- Full version lineage v2–v17: 17 models, 8 teachers, 4 architectures,
  $1.76 compute. Pareto frontier ablation (λ=3/5/10)
- Marimo interactive notebook: paradox simulator, mechanism toggle,
  baseline comparison, silver-label table, compute costs
- MCP server (7 tools): read_manifest, read_section, get_baselines,
  run_baselines, get_model_info, search_paper, get_repo_status
- Interactive HTML sites (3 pages) matching pocoo.vaked.dev theme
- Loop-experiment-researcher template: scaffold.py creates a full research
  project from an idea (loop/, paper/, baselines/, mcp_server/, CI, devcontainer)
- CI workflow: LaTeX balance, TODO check, citation check, Python syntax,
  agent readiness
- GitHub Pages workflow: auto-deploys site/ to GitHub Pages
- Dev container: Python 3.12 + LaTeX + marimo + MCP + all deps
- AGENTS.md, README.md (with ELI5), LINKS.txt, CITATION.cff, LICENSE,
  CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, llms.txt, robots.txt
- Issue templates (bug report, research contribution)
- PR template with verification checklist
- FUNDING.yml (GitHub Sponsors: peterlodri-sec)

### Key results
- kompress-v8: 0.993 exact_keep_pct (vs TextRank 0.599, LLMLingua-2 0.867)
- Voting ensemble paradox: majority 2/3 collapses to 0.931 (−0.031 below best single)
- Pareto frontier: λ=3 (0.955, 15%), λ=5 (0.963, 3.7%), λ=10 (0.972, 2.8%)
- Key finding: label quality is the bottleneck, not model capacity or data quantity
- Total cost: $37.19 (DeepSeek) + $1.76 (GPU) = $38.95
