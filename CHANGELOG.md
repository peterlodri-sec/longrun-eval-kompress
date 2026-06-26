# Changelog

## [2026-06-26] — initial

### Added

- feat: add 6 E2E loop-engineering examples, 2 new CI agents, ralph-loop (`37c9554`)
- feat: baseline runner + CI agents (citation-guard, metric-watchdog) (`868eb12`)

### Fixed

- fix: sync LINKS.txt with all file references, whitelist reference links (`41fe70f`)
- fix: update all URLs, add linker CI agent (`cc02954`)

### Documentation

- docs: add blog cross-link template + update README links (`f1cce06`)
- docs: add ENTHEA-BG.md self-hosting guide + kompress.vaked.dev to LINKS (`c2b81cd`)
- docs: add researcher loop prompt for GPU collaborator (`9f12a90`)
- docs: add deepseek quote to README (`338eb63`)

### Other

- feat(site): ENTHEA as landing page, marimo notebook at /notebook/ (`0bf2480`)
- fix(taskfile): remove redundant cp commands (files already in site/) (`bee0555`)
- fix(taskfile): quote template variables, replace unicode dashes (`9ef5400`)
- feat(seo): full SEO/AI upgrade for kompress.vaked.dev + pocoo templates (`a996ef1`)
- feat(bg): ENTHEA self-hostable shader with AGPL-3.0 attribution (`411e699`)
- fix(bg): correct GLSL uniform name, add steganographic signature (`d77082b`)
- feat(site): add ENTHEA-inspired WebGL neural field background (`bec73b6`)
- fix(notebook): rename locals to avoid multiple-defs warnings (`6273351`)
- fix(notebook): use raw strings for LaTeX markdown cells (`7114306`)
- fix(notebook): merge duplicate mo import cells (`e385e18`)
- fix(taskfile): use uv run/uvx for all python commands, fix macOS sed (`fa4f0ea`)
- fix(site): add visible navigation links to marimo notebook (`90f6e56`)
- fix(paper): address Opus review — Corollary 1, Def 2 remark, Sapir-Whorf demotion, host PDF (`842a3a5`)
- fix(tex): convert SVG figures to PDF for pdflatex compatibility (`60d60f3`)
- fix(tex): renewcommand Pr instead of newcommand (`24d3cd4`)
- feat(paper): add figures, blog refs, CI agents to manuscript + README (`0c192e2`)
- feat(agents): add 5-agent CI suite with CLI + MCP abstraction (`81bc079`)
- feat(ci): add devops doc-sync bot agent with DeepSeek v4-flash (`b36eea2`)
- Update README + wiki: Taskfile, Nix flake, marimo WASM site (`8573965`)
- SOTA Nix flake: treefmt + pre-commit hooks + apps + checks (`775cab7`)
- Add _AUTHOR.md: experimentation and knowledge sharing, nothing else (`f1cb970`)
- Add Nix flake and Taskfile for reproducible dev environment (`a7861d2`)
- Declare missing remark theorem environment (`0968a93`)
- Remove algpseudocode and microtype (unavailable in TeX Live) (`442db9c`)
- Update genesis seal (paper changes) (`a8cf81d`)
- Remove algorithm.sty dependency, add site links to paper (`1bf3ac5`)
- Fix page title and meta description for SEO (`276048c`)
- Replace static site with marimo WASM notebook export (`72627a5`)
- Fix Pages 404: remove paths filter so workflow triggers on every push (`9a1efa2`)
- Add publishing roadmap issue + announcement templates (X, HF, blog, Reddit) (`ebe49d0`)
- Fix stale /bin/zsh.55 → .76 in intro + disclaimer, push wiki, verify no PII (`f84d46a`)
- Fix all CI cosmetics, add wiki content, bump action versions (`94c44b9`)
- Update genesis seal to match current state (CI-regenerated) (`edaff0c`)
- Fix CI: YAML colon in echo, bulk HEAD link check, graceful Pages skip, seal regenerate (`7dd975a`)
- Add genesis seal + DNS link check, fix typos/orphaned bib/broken links, OG tags (`daf773d`)
- Add community health files: CITATION.cff, FUNDING, CoC, issue/PR templates, Pages, CHANGELOG (`af8e041`)
- Add CI workflow, devcontainer, and loop-experiment-researcher template (`0f25918`)
- Add interactive HTML sites matching pocoo.vaked.dev theme (`6846974`)
- Add Pareto frontier table to README, upgrade marimo notebook + marimo.io integration (`a426c97`)
- Add baselines, marimo notebook, MCP server, AGENTS.md, repo docs + v15-v17 Pareto frontier (`3a9bbc0`)
- Add disclaimer/legal/privacy appendix, fill training procedure + acknowledgments (`79fb168`)
- Update v8 to C3 self-distillation, add v9-v14 lineage, silver-label per-domain data (`3da4c8b`)
- Add v8 production model, outer-loop origin (vaked/ultrawhale), compute costs (`c927016`)
- Add ICLR 2027 manuscript skeleton: Voting Ensemble Paradox + 3.0x fix (`c9661d2`)

## [2026-06-26] — initial

### Added

- feat: add 6 E2E loop-engineering examples, 2 new CI agents, ralph-loop (`37c9554`)
- feat: baseline runner + CI agents (citation-guard, metric-watchdog) (`868eb12`)

### Fixed

- fix: sync LINKS.txt with all file references, whitelist reference links (`41fe70f`)
- fix: update all URLs, add linker CI agent (`cc02954`)

### Documentation

- docs: add blog cross-link template + update README links (`f1cce06`)
- docs: add ENTHEA-BG.md self-hosting guide + kompress.vaked.dev to LINKS (`c2b81cd`)
- docs: add researcher loop prompt for GPU collaborator (`9f12a90`)
- docs: add deepseek quote to README (`338eb63`)

### Other

- feat(site): ENTHEA as landing page, marimo notebook at /notebook/ (`0bf2480`)
- fix(taskfile): remove redundant cp commands (files already in site/) (`bee0555`)
- fix(taskfile): quote template variables, replace unicode dashes (`9ef5400`)
- feat(seo): full SEO/AI upgrade for kompress.vaked.dev + pocoo templates (`a996ef1`)
- feat(bg): ENTHEA self-hostable shader with AGPL-3.0 attribution (`411e699`)
- fix(bg): correct GLSL uniform name, add steganographic signature (`d77082b`)
- feat(site): add ENTHEA-inspired WebGL neural field background (`bec73b6`)
- fix(notebook): rename locals to avoid multiple-defs warnings (`6273351`)
- fix(notebook): use raw strings for LaTeX markdown cells (`7114306`)
- fix(notebook): merge duplicate mo import cells (`e385e18`)
- fix(taskfile): use uv run/uvx for all python commands, fix macOS sed (`fa4f0ea`)
- fix(site): add visible navigation links to marimo notebook (`90f6e56`)
- fix(paper): address Opus review — Corollary 1, Def 2 remark, Sapir-Whorf demotion, host PDF (`842a3a5`)
- fix(tex): convert SVG figures to PDF for pdflatex compatibility (`60d60f3`)
- fix(tex): renewcommand Pr instead of newcommand (`24d3cd4`)
- feat(paper): add figures, blog refs, CI agents to manuscript + README (`0c192e2`)
- feat(agents): add 5-agent CI suite with CLI + MCP abstraction (`81bc079`)
- feat(ci): add devops doc-sync bot agent with DeepSeek v4-flash (`b36eea2`)
- Update README + wiki: Taskfile, Nix flake, marimo WASM site (`8573965`)
- SOTA Nix flake: treefmt + pre-commit hooks + apps + checks (`775cab7`)
- Add _AUTHOR.md: experimentation and knowledge sharing, nothing else (`f1cb970`)
- Add Nix flake and Taskfile for reproducible dev environment (`a7861d2`)
- Declare missing remark theorem environment (`0968a93`)
- Remove algpseudocode and microtype (unavailable in TeX Live) (`442db9c`)
- Update genesis seal (paper changes) (`a8cf81d`)
- Remove algorithm.sty dependency, add site links to paper (`1bf3ac5`)
- Fix page title and meta description for SEO (`276048c`)
- Replace static site with marimo WASM notebook export (`72627a5`)
- Fix Pages 404: remove paths filter so workflow triggers on every push (`9a1efa2`)
- Add publishing roadmap issue + announcement templates (X, HF, blog, Reddit) (`ebe49d0`)
- Fix stale /bin/zsh.55 → .76 in intro + disclaimer, push wiki, verify no PII (`f84d46a`)
- Fix all CI cosmetics, add wiki content, bump action versions (`94c44b9`)
- Update genesis seal to match current state (CI-regenerated) (`edaff0c`)
- Fix CI: YAML colon in echo, bulk HEAD link check, graceful Pages skip, seal regenerate (`7dd975a`)
- Add genesis seal + DNS link check, fix typos/orphaned bib/broken links, OG tags (`daf773d`)
- Add community health files: CITATION.cff, FUNDING, CoC, issue/PR templates, Pages, CHANGELOG (`af8e041`)
- Add CI workflow, devcontainer, and loop-experiment-researcher template (`0f25918`)
- Add interactive HTML sites matching pocoo.vaked.dev theme (`6846974`)
- Add Pareto frontier table to README, upgrade marimo notebook + marimo.io integration (`a426c97`)
- Add baselines, marimo notebook, MCP server, AGENTS.md, repo docs + v15-v17 Pareto frontier (`3a9bbc0`)
- Add disclaimer/legal/privacy appendix, fill training procedure + acknowledgments (`79fb168`)
- Update v8 to C3 self-distillation, add v9-v14 lineage, silver-label per-domain data (`3da4c8b`)
- Add v8 production model, outer-loop origin (vaked/ultrawhale), compute costs (`c927016`)
- Add ICLR 2027 manuscript skeleton: Voting Ensemble Paradox + 3.0x fix (`c9661d2`)

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
