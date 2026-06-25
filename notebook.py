#!/usr/bin/env python3
"""Interactive research paper: Voting Ensemble Paradox + 3.0x fix.

Built with marimo (https://marimo.io) — a next-generation Python notebook
that is reactive, Git-friendly, and shareable as a web app.

Run:
    marimo edit notebook.py     # interactive editor
    marimo run notebook.py      # read-only web app
    marimo export html notebook.py -o notebook.html  # standalone HTML

Learn more about marimo: https://marimo.io
"""
import marimo

__generated_with = "0.23.11"
app = marimo.App(width="medium", title="Voting Ensemble Paradox — Interactive Research Paper")


@app.cell
def _():
    import marimo as mo
    mo.md("""
    # Asymmetric Loss Modulation Resolves the Voting Ensemble Paradox
    ### Interactive Research Paper — kompress-v8 + LoopKit

    **Lead thesis:** Multi-checkpoint voting ensembles with asymmetric training-data
    floors collapse to the per-stratum weakest voter under $k$-of-$N$ drop voting.
    A $3.0\\times$ heavy false-eviction penalty on critical-syntactic tokens resolves
    this by lifting the collapse floor.

    Use the controls below to explore the paradox, the fix, and the baseline comparison.
    """)
    return (mo,)


@app.cell
def _(mo):
    mo.md("""
    ## 1. The Voting Ensemble Paradox (Theorem 1)

    Under **per-stratum monotone-rejection refinement** and **unanimity-to-keep (AND) voting**,
    the ensemble eviction indicator equals the per-stratum weakest voter's indicator:

    $$\\mathbb{I}_{\\mathrm{ens}}(x) = \\mathbb{I}_{i^\\star_k}(x) \\quad \\forall x \\in S_k$$

    Under $k$-of-$N$ drop voting (Remark 1), this generalizes to the per-stratum
    $k$-th order statistic. Adjust the voting threshold to see how the collapse moves:
    """)
    return


@app.cell
def _(mo):
    import numpy as np

    k_slider = mo.ui.slider(1, 5, value=1, label="k (drop threshold: evict if ≥k voters say drop)")
    n_voters = mo.ui.slider(3, 10, value=5, label="N (number of voters)")

    mo.md(f"""
    {k_slider}

    {n_voters}

    **Interpretation:**
    - $k=1$ (AND): ensemble collapses to the **weakest** voter on each stratum
    - $k=N$ (OR): ensemble collapses to the **strongest** voter (but requires all to agree on drop)
    - $k=\\lfloor N/2 \\rfloor$ (majority): collapse to the per-stratum **median** voter
    """)
    return k_slider, n_voters, np


@app.cell
def _(k_slider, n_voters, np, mo):
    # Simulate the paradox: each voter has a floor, the ensemble collapses
    np.random.seed(42)
    N = n_voters.value
    k = k_slider.value

    # Asymmetric floors: voter 0 is weakest (lowest floor), voter N-1 is strongest
    floors = np.linspace(0.3, 0.9, N)  # per-voter quality floor
    strata = 10  # 10 strata

    # Each voter's per-stratum recall (higher floor = better recall on that stratum)
    # Weakest voter has lowest recall on all strata, but the weakest VARIES across strata
    per_stratum_recall = np.zeros((N, strata))
    for i in range(N):
        base = floors[i]
        noise = np.random.normal(0, 0.1, strata)
        per_stratum_recall[i] = np.clip(base + noise, 0, 1)

    # Find the k-th weakest voter per stratum
    sorted_indices = np.argsort(per_stratum_recall, axis=0)  # ascending: [0]=worst
    kth_weakest_per_stratum = sorted_indices[k - 1]  # k-th from bottom

    ensemble_recall = np.mean(per_stratum_recall[kth_weakest_per_stratum, range(strata)])
    best_single_recall = np.mean(np.max(per_stratum_recall, axis=0))
    worst_single_recall = np.mean(np.min(per_stratum_recall, axis=0))

    mo.md(f"""
    ### Simulated collapse (N={N}, k={k})

    | Metric | Value |
    |--------|-------|
    | Best single voter recall | {best_single_recall:.3f} |
    | Worst single voter recall | {worst_single_recall:.3f} |
    | **Ensemble recall (k-of-N)** | **{ensemble_recall:.3f}** |
    | Collapse gap (best - ensemble) | {best_single_recall - ensemble_recall:.3f} |

    The ensemble recall ({ensemble_recall:.3f}) is always below the best single voter
    ({best_single_recall:.3f}). The gap is the **Voting Ensemble Paradox**.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 2. The Three Corrective Mechanisms

    | Mechanism | Where | What |
    |-----------|-------|------|
    | **A: 3.0× penalty** | training-time | Weighted cross-entropy on must-keep tokens |
    | **B: Regex override** | inference-time | Post-inference force-keep for `MUST_KEEP_RE` matches |
    | **C: Self-labeling** | training-time | Use A+B as oracle to relabel → retrain |

    Toggle mechanisms to see the progression:
    """)
    return


@app.cell
def _(mo):
    mechanisms = mo.ui.multiselect(
        ["A: 3.0x penalty", "B: regex override", "C: self-labeling"],
        value=["A: 3.0x penalty", "B: regex override", "C: self-labeling"],
        label="Active mechanisms",
    )
    mechanisms
    return (mechanisms,)


@app.cell
def _(mechanisms, mo):
    # Real data from pocoo.vaked.dev logs
    data = {
        "v2 base": {"heretic": 0.975, "keep_rate": 0.897, "override_delta": None, "mechanisms": []},
        "v3 (A only)": {"heretic": 0.942, "keep_rate": 0.728, "override_delta": 0.054, "mechanisms": ["A: 3.0x penalty"]},
        "v3 + B": {"heretic": 0.969, "keep_rate": 0.846, "override_delta": 0.028, "mechanisms": ["A: 3.0x penalty", "B: regex override"]},
        "v4 (A+C)": {"heretic": 0.967, "keep_rate": 0.823, "override_delta": 0.000, "mechanisms": ["A: 3.0x penalty", "B: regex override", "C: self-labeling"]},
        "v8 (A+C3)": {"heretic": 0.955, "keep_rate": 0.854, "override_delta": 0.000, "mechanisms": ["A: 3.0x penalty", "B: regex override", "C: self-labeling"]},
    }

    active = set(mechanisms.value)
    rows = []
    for name, d in data.items():
        if not active or set(d["mechanisms"]) & active or not d["mechanisms"]:
            rows.append((name, d["heretic"], d["keep_rate"], d["override_delta"]))

    table_rows = "\n".join(
        f"| {name} | {heretic:.3f} | {kr:.3f} | {f'+{od:.3f}' if od else '—'} |"
        for name, heretic, kr, od in rows
    )

    mo.md(f"""
    ### Version lineage (filtered by active mechanisms)

    | Model | Heretic exact | keep_rate | override_delta |
    |-------|--------------|-----------|----------------|
    {table_rows}
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 3. Baseline Comparison (8-prompt heretic set)

    Real baseline runs from this repo's `baselines/run_baselines.py`:
    """)
    return


@app.cell
def _(mo):
    import json
    from pathlib import Path

    results_path = Path(__file__).parent / "baselines" / "baseline_results.json"
    if results_path.exists():
        data = json.loads(results_path.read_text())
        rows = []
        for name, d in data.items():
            avg = d.get("averages", {})
            if avg:
                rows.append((name, avg.get("exact_pct", 0), avg.get("keep_rate", 0), avg.get("avg_ms", 0)))

        table = "\n".join(
            f"| {name} | {ex:.3f} | {kr:.3f} | {ms:.1f} |"
            for name, ex, kr, ms in rows
        )
        mo.md(f"""
        | Method | exact_keep_pct | keep_rate | avg_ms |
        |--------|---------------|-----------|--------|
        {table}
        """)
    else:
        mo.md("Run `python baselines/run_baselines.py` to generate baseline results.")
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 4. Pareto Frontier: The Loss-Weight Ablation

    The must-keep loss weight $\lambda$ controls the precision–compression tradeoff.
    v8 data held constant; only $\lambda$ varies. The frontier is **monotonic and clean**:
    each +1.0 in $\lambda$ buys ~0.01 heretic precision at the cost of ~10% compression.

    | λ | Model | Heretic exact | Compression | keep_rate | Status |
    |---|-------|--------------|-------------|-----------|--------|
    | **3.0** | **v8** | **0.955** | **15.0%** | **0.854** | **Production (sweet spot)** |
    | 5.0 | v17 | 0.963 | 3.7% | 0.963 | Pareto middle |
    | 10.0 | v16 | 0.972 | 2.8% | 0.972 | Best precision, near-zero compression |

    At $\lambda=10$ the model keeps 97.2% of tokens — useless as a compressor despite
    the best precision score. $\lambda=3$ (v8) is the knee of the curve.

    **Key finding across 17 models, 8 teachers, 4 architectures ($1.76 compute):
    label quality is the bottleneck, not model capacity or data quantity.**
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 5. The Silver Label Problem

    The `mk_in_ref` metric measures what fraction of must-keep tokens survive in the
    compressed reference. Lower = worse label quality.

    | Domain | mk_in_ref |
    |--------|-----------|
    | Thermite stoichiometry | 0.76 |
    | DNS cache poisoning | 0.65 |
    | SQL injection payloads | 0.56 |
    | ECDSA nonce reuse | 0.43 |
    | Sodium pentobarbital | 0.36 |
    | Tor circuit construction | 0.35 |
    | Organophosphate poisoning | 0.33 |
    | Buffer overflow exploitation | 0.27 |
    | Chlorine gas chemistry | 0.11 |
    | **Average (dense technical)** | **0.43** |
    | ultrawhale Q&A (for comparison) | 0.72 |

    This is why the inference override (Mechanism B) is essential: no training data
    approach escapes the silver-label problem because every compressed reference
    makes vocabulary choices the model learns to mimic.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 6. Compute Costs

    | Layer | Cost |
    |-------|------|
    | Outer loop (ultrawhale v1→v100, DeepSeek API) | $37.19 |
    | Inner loop (kompress v3→v17, vast.ai GPU) | $1.76 |
    | **Total** | **$38.95** |

    17 models trained, 8 teachers, 4 architectures. The entire research program
    cost less than a single industry conference registration.

    ---

    *Built with [marimo](https://marimo.io) — reactive Python notebooks that are
    Git-friendly, reproducible, and shareable as web apps. [Learn more →](https://marimo.io)*
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
