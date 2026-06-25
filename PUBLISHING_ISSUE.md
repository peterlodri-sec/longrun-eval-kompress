---
name: Publishing roadmap — arXiv → ICLR 2027
about: Pinned human checklist for taking this manuscript from repo to published
title: "[PUBLISHING] arXiv → ICLR 2027 — human followup checklist"
labels: research, pinned
assignees: []
---

> **This is a pinned, human-owned checklist. Do not auto-complete.**
> **Each checkbox is a decision, not a task.**
>
> Motto: *Be the example you want to see in the world.*

## Current state ✅

- [x] Manuscript complete (9 files, 1592 lines, 13 tables, 10/10 envs balanced)
- [x] Baselines run (kompress-v8 0.993 vs TextRank 0.599 vs LLMLingua-2 0.867 vs random 0.910)
- [x] Version lineage v2-v17 (17 models, 8 teachers, 4 architectures, $1.76 compute)
- [x] Pareto frontier ablation (λ=3/5/10 → v8/v17/v16)
- [x] Genesis seal verified
- [x] CI all green (3 workflows)
- [x] GitHub Pages live
- [x] Wiki populated (11 pages)
- [x] No PII, no secrets
- [x] Marimo notebook
- [x] MCP server
- [x] Template scaffold
- [x] Community health files (CITATION.cff, FUNDING, CoC, issue/PR templates)
- [x] Editor's review complete (REVIEW.md — 10 weaknesses, 5 must-fix items)

---

## Phase 1: Compile & Polish (human, ~2 hours)

- [ ] **1.1** Install LaTeX or use the devcontainer:
  ```bash
  cd paper && latexmk -pdf main.tex
  ```
  If `iclr2027_conference.sty` is unavailable, use the article class fallback (already in main.tex).

- [ ] **1.2** Read the compiled PDF end-to-end. Mark any:
  - Numbers that don't match the blog logs or baseline_results.json
  - Claims that feel stronger than the evidence supports
  - Paragraphs that read like a blog post instead of academic prose
  - Missing cross-references (?? in the PDF)

- [ ] **1.3** Verify every number in every table against the source (see PUBLISHING_TODO.md §1.3 for the full list of 13 tables with sources)

- [ ] **1.4** Check for `\tbd` or TODO (should be zero):
  ```bash
  grep -rn '\\tbd' paper/*.tex
  grep -rn 'TODO' paper/*.tex
  ```

- [ ] **1.5** Address the 5 must-fix items from REVIEW.md:
  - [ ] Run ensemble on 32-prompt set (does paradox hold at scale?)
  - [ ] Formalize Pareto collapse proof (full, not sketch)
  - [ ] Cut §5 LoopKit to ≤1 page or move to appendix
  - [ ] Remove cost mentions from abstract
  - [ ] Run AND voting experiment (theorem is about AND, experiment uses majority)

- [ ] **1.6** Write the author block. For ICLR double-blind: keep "Anonymous Authors". For arXiv: uncomment the real author block in main.tex.

---

## Phase 2: External Review (human + AI, ~1 day)

- [ ] **2.1** Review with Claude Opus (or strongest available model):
  - Feed the full manuscript as context
  - Ask it to act as a hostile ICLR reviewer (Review #2)
  - Specifically: "What would you reject this paper for?"
  - Paste the review into this issue

- [ ] **2.2** Review with GLM (different perspective):
  - Same manuscript, prompt: "Act as meta-reviewer. Top 3 weaknesses?"
  - Paste the review into this issue

- [ ] **2.3** Address every actionable point from both reviews:
  - Both flag same issue → fix before submission
  - One flags, other doesn't → judgment call
  - Document what changed and what rejected in this issue

---

## Phase 3: arXiv Preprint (~1 hour)

- [ ] **3.1** Uncomment the real author block in main.tex
- [ ] **3.2** Compile final PDF: `cd paper && latexmk -pdf main.tex`
- [ ] **3.3** Create arXiv submission:
  - Go to https://arxiv.org/submit
  - Category: cs.LG (Machine Learning)
  - Upload the PDF and source files (.tex + .bib)
  - Title: "Asymmetric Loss Modulation Resolves the Voting Ensemble Paradox in Learned Context-Pruning Ensembles"
  - Abstract: copy from main.tex
  - Comments: "Submitted to ICLR 2027."
- [ ] **3.4** Once arXiv assigns an identifier, add it to:
  - `CITATION.cff` (preferred-citation)
  - `README.md` (badges section)
  - `paper/main.tex` (footnote)

---

## Phase 4: ICLR 2027 Submission

- [ ] **4.1** Download the official ICLR 2027 style file when it opens
- [ ] **4.2** Replace `\documentclass` in main.tex with `\documentclass{iclr2027_conference}`
- [ ] **4.3** Re-anonymize: author block says "Anonymous Authors", no self-identification in text
- [ ] **4.4** Check page limit (9 pages + references + appendix). Trim if needed:
  - LoopKit §5 → move to appendix if over limit
  - Disclaimer §A → remove for ICLR, keep on arXiv only
- [ ] **4.5** Submit via OpenReview
- [ ] **4.6** After submission: do not update repo until reviews arrive

---

## Phase 5: Post-Review

- [ ] **5.1** When reviews arrive, create a new issue "ICLR rebuttal"
- [ ] **5.2** Address each reviewer concern
- [ ] **5.3** Update repo after rebuttal period: merge changes, update CHANGELOG, tag release
- [ ] **5.4** If accepted: add "Accepted at ICLR 2027" badge to README
- [ ] **5.5** If rejected: resubmit to TMLR (rolling review)

---

## Phase 6: Closing the loop (ongoing)

- [ ] **6.1** Submit marimo notebook to the marimo/alphaXiv competition (deadline Jun 28)
- [ ] **6.2** Add repo topics: `ml`, `compression`, `loop-engineering`, `context-pruning`, `modernbert`, `ensemble`, `open-science`
- [ ] **6.3** Create a Zenodo archival DOI
- [ ] **6.4** When v18+ lands: update lineage table, CHANGELOG, notebook. Tag a release.
- [ ] **6.5** When someone uses the template: celebrate it. Link to their repo. Be the example.

---

*This checklist is pinned. It is human-owned. Do not auto-complete items.*
*Each checkbox is a decision, not a task.*
*— "Be the example you want to see in the world."*
