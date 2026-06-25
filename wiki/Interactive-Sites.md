# Interactive Sites

## HTML demos (GitHub Pages)
- **Landing:** https://peterlodri-sec.github.io/longrun-eval-kompress/
- **Paradox simulator:** https://peterlodri-sec.github.io/longrun-eval-kompress/paradox.html
- **Baselines & Pareto:** https://peterlodri-sec.github.io/longrun-eval-kompress/baselines.html

All three match the pocoo.vaked.dev theme (#070b16 background, animated canvas waves).

## Marimo notebook
```bash
marimo edit notebook.py      # interactive editor
marimo run notebook.py       # read-only web app
marimo export html notebook.py -o notebook.html  # standalone HTML
```

Built with [marimo](https://marimo.io) — reactive Python notebooks that are Git-friendly and reproducible.

## The paradox simulator
Adjust N voters, k threshold, floor spread, and strata count to watch the ensemble collapse in real time. See why adding voters makes your ensemble worse.

## The baseline comparison
Visual bars for kompress-v8 vs TextRank, LLMLingua-2, random eviction. Pareto frontier cards for the λ-ablation. Full v2–v17 lineage table with status badges.
