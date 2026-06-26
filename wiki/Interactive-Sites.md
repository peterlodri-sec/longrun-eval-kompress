# Interactive Sites

## ENTHEA landing page (live)

**URL:** https://kompress.vaked.dev

Full psychedelic neural-field visualizer derived from elder-plinius/ENTHEA (AGPL-3.0).

## marimo WASM paper (live)

**URL:** https://kompress.vaked.dev/notebook/

A standalone marimo notebook exported to WebAssembly — runs entirely in the browser, no server needed. Contains:

- **Paradox simulator** — adjust k (voting threshold) and N (voters) to watch the ensemble collapse
- **Mechanism toggle** — filter the version lineage by which mechanisms (A/B/C) are active
- **Baseline comparison** — live results from `baseline_results.json`
- **Silver-label table** — per-domain `mk_in_ref` showing why label quality is the bottleneck
- **Pareto frontier** — the λ-ablation (3→5→10) with compression tradeoffs
- **Compute costs** — the $38.95 breakdown

### Rebuilding the site

```bash
# With task
task site:build

# Or manually
marimo export html-wasm notebook.py -o site --no-execute --no-show-code -f
```

The site is deployed automatically via GitHub Actions on every push to `main`.

## Local notebook

```bash
marimo edit notebook.py      # interactive editor
marimo run notebook.py       # read-only web app
```

Built with [marimo](https://marimo.io) — reactive Python notebooks that are Git-friendly and reproducible.
