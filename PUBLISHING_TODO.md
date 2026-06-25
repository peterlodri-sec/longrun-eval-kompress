# Publishing TODO — ICLR 2027 Submission

> **Pinned checklist for taking this manuscript from repo to arXiv to ICLR.
> Human-owned. Do not auto-complete.**

---

## Phase 1: Compile & Polish (human, ~2 hours)

- [ ] **1.1** Install LaTeX locally or use the devcontainer:
  ```bash
  cd paper && latexmk -pdf main.tex
  ```
  If `iclr2027_conference.sty` is not available, use the article class
  fallback (already in main.tex). For the real submission, download the
  ICLR style file from the official site.

- [ ] **1.2** Read the compiled PDF end-to-end. Mark any:
  - Numbers that don't match the blog logs or baseline_results.json
  - Claims that feel stronger than the evidence supports
  - Paragraphs that read like a blog post instead of academic prose
  - Missing cross-references (?? in the PDF)

- [ ] **1.3** Verify every number in every table against the source:
  - Table 1 (v2→v3): heretic 0.942, keep_rate 0.728 — source: heretic blog
  - Table 2 (override): v3 0.911→0.965, v4 0.961→0.965 — source: loop-engineering-applied blog
  - Table 3 (self-labeling): v4 mk_in_ref 0.823, heretic 0.967 — source: iterative-self-labeling blog
  - Table 4 (ensemble): majority 0.931, regression 0.031 — source: loop-engineering-applied blog
  - Table 5 (per-prompt): 8 prompts, average 0.942→0.969 — source: heretic blog
  - Table 6 (32-prompt): v4/v6/v7 within 0.002 — source: heretic blog
  - Table 7 (v8 results): 0.955, mk_in_ref 1.000 — source: v8 HF datacard
  - Table 8 (lineage v2-v17): all heretic values — source: HF datacards + LoopKit blog
  - Table 9 (Pareto λ): v8 0.955/15%, v17 0.963/3.7%, v16 0.972/2.8% — source: v16/v17 HF datacards
  - Table 10 (baselines): v8 0.993, random 0.910, LLMLingua-2 0.867, TextRank 0.599 — source: baseline_results.json
  - Table 11 (silver label): 9 domains, avg 0.43 — source: silver-label blog
  - Table 12 (loop mapping): 4 tiers — source: LoopKit blog + LangChain blog
  - Table 13 (ecosystem mapping): Greyling conventions — source: Greyling repo

- [ ] **1.4** Fix any `\tbd` or placeholder (should be zero after baselines, verify)
  ```bash
  grep -rn '\\tbd' paper/*.tex
  grep -rn 'TODO' paper/*.tex
  ```

- [ ] **1.5** Check that AutoCompressors and Gisting are honestly mentioned
  as deferred (not claimed as run). They need GPU infrastructure we don't have.

- [ ] **1.6** Write the author block. For ICLR double-blind: keep "Anonymous
  Authors". For arXiv: uncomment the real author block in main.tex.

---

## Phase 2: External Review (human + AI, ~1 day)

- [ ] **2.1** Create a GitHub issue titled "Manuscript review — pre-submission"
  with the label `research`. Use this as the central review thread.

- [ ] **2.2** Run an automated self-review:
  ```bash
  # LaTeX environment balance
  cd paper && for env in theorem proof corollary definition remark abstract document itemize table algorithm; do
    b=$(grep -c "\\\\begin{$env}" *.tex | awk -F: '{s+=$2} END{print s}')
    e=$(grep -c "\\\\end{$env}" *.tex | awk -F: '{s+=$2} END{print s}')
    echo "$env: begin=$b end=$e $([ "$b" = "$e" ] && echo OK || echo MISMATCH)"
  done

  # Citation check
  grep -rn 'VERIFY' paper/references.bib

  # Cross-reference check (compile and look for ??)
  latexmk -pdf main.tex 2>&1 | grep 'Warning.*undefined'
  ```

- [ ] **2.3** Review with Claude Opus (or strongest available model):
  - Feed the full manuscript (all .tex files concatenated) as context
  - Ask it to act as a hostile ICLR reviewer (Review #2)
  - Specifically ask:
    1. "What is the one claim this paper defends? Is it clear?"
    2. "Is the Voting Ensemble Paradox proof correct? Check the indicator-function algebra."
    3. "Are the baseline comparisons fair? Is LLMLingua-2's keep_rate >1.0 honestly documented?"
    4. "Is the 'Sapir-Whorf' framing defensible, or will reviewers see it as metaphor hand-waving?"
    5. "What would you reject this paper for?"
  - Paste the review into the GitHub issue

- [ ] **2.4** Review with GLM (current model, different perspective):
  - Same manuscript, different prompt:
    1. "Act as a meta-reviewer. What are the top 3 weaknesses?"
    2. "Is the three-mechanism separation (A/B/C) clear, or does it conflate?"
    3. "Does the LoopKit section add or distract from the core claim?"
    4. "Is the $38.95 cost framing relevant to the scientific contribution, or a distraction?"
  - Paste the review into the GitHub issue

- [ ] **2.5** Address every actionable point from both reviews:
  - If both reviewers flag the same issue → fix it before submission
  - If one reviewer flags something the other doesn't → judgment call
  - Document what you changed and what you rejected, in the GitHub issue

---

## Phase 3: arXiv Preprint (~1 hour)

- [ ] **3.1** Uncomment the real author block in main.tex (arXiv is not blind)
- [ ] **3.2** Compile final PDF: `cd paper && latexmk -pdf main.tex`
- [ ] **3.3** Create arXiv submission:
  - Go to https://arxiv.org/submit
  - Category: cs.LG (Machine Learning) or cs.CL (Computation and Language)
  - Upload the PDF and source files (.tex + .bib + .sty)
  - Title: "Asymmetric Loss Modulation Resolves the Voting Ensemble Paradox in Learned Context-Pruning Ensembles"
  - Abstract: copy from main.tex
  - Comments: "21 pages, 13 tables, 1 algorithm. Submitted to ICLR 2027."
- [ ] **3.4** Once arXiv assigns a DOI/identifier, add it to:
  - `CITATION.cff` (preferred-citation)
  - `README.md` (badges section)
  - `paper/main.tex` (as a footnote or in the metadata)

---

## Phase 4: ICLR 2027 Submission (~1 day before deadline)

- [ ] **4.1** Download the official ICLR 2027 style file (`iclr2027_conference.sty`)
  from the ICLR website when it opens
- [ ] **4.2** Replace the `\documentclass` line in main.tex:
  ```latex
  % Remove: \documentclass[10pt,letterpaper]{article}
  % Add:    \documentclass{iclr2027_conference}
  ```
  And remove the manual geometry package (ICLR style handles margins)
- [ ] **4.3** Re-anonymize: ensure the author block says "Anonymous Authors"
  and the text doesn't self-identify (no "as we showed in our blog at pocoo.vaked.dev")
- [ ] **4.4** Check page limit: ICLR typically allows 9 pages + references + appendix
  - Main content (§1-§6): trim if over 9 pages
  - Appendix A (disclaimer/legal/privacy): moves to appendix
  - LoopKit §5: trim if needed — the paradox is the star, not the substrate
- [ ] **4.5** Submit via OpenReview:
  - Go to the ICLR 2027 OpenReview portal
  - Upload PDF + source
  - Fill in metadata (title, abstract, author identities for the system, but anonymized in the PDF)
  - Select subject areas: Optimization, Representation Learning, Systems
- [ ] **4.6** After submission: do not update the repo until reviews arrive
  (ICLR has a strict no-update policy during review)

---

## Phase 5: Post-Review (~during rebuttal period)

- [ ] **5.1** When reviews arrive, create a new GitHub issue "ICLR rebuttal"
- [ ] **5.2** Address each reviewer concern:
  - Run any requested experiments (e.g., AutoCompressors if GPU access is obtained)
  - Add analysis to the manuscript
  - Write the rebuttal document
- [ ] **5.3** Update the repo after the rebuttal period:
  - Merge any manuscript changes
  - Update CHANGELOG.md
  - Tag a release: `git tag v1.1.0 -m "Post-rebuttal update"`
- [ ] **5.4** If accepted: update README with "Accepted at ICLR 2027" badge
- [ ] **5.5** If rejected: resubmit to TMLR (rolling review, no deadline pressure)

---

## Phase 6: Closing the loop (ongoing)

- [ ] **6.1** Enable GitHub Discussions for Q&A from readers
- [ ] **6.2** Submit the marimo notebook to the marimo/alphaXiv competition
  (deadline June 28 — https://marimo.io)
- [ ] **6.3** Enable GitHub Pages (Settings → Pages → Source: GitHub Actions)
  so the site/ HTML pages are live at
  `https://peterlodri-sec.github.io/longrun-eval-kompress/`
- [ ] **6.4** Add repo topics: `ml`, `compression`, `loop-engineering`,
  `context-pruning`, `modernbert`, `ensemble`, `open-science`
  (Settings → General → Topics)
- [ ] **6.5** Create a Zenodo archival DOI for long-term citability
- [ ] **6.6** When v18+ lands from the experiment loop: update the lineage
  table, CHANGELOG, and notebook. Tag a new release.
- [ ] **6.7** When someone uses the template to scaffold their own project:
  celebrate it. Link to their repo. Be the example.

---

*This checklist is pinned. It is human-owned. Do not auto-complete items.
Each checkbox is a decision, not a task. — "Be the example you want to see in the world."*
