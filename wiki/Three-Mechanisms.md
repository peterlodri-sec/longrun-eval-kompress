# Three Mechanisms

## Mechanism A: 3.0× training penalty (Sapir-Whorf term)

**Where:** training-time
**What:** 3× weighted cross-entropy on must-keep tokens during fine-tuning

$$\mathcal{L} = \mathcal{L}_{\mathrm{base}} + 3.0 \cdot \mathcal{L}_{\mathrm{crit}}$$

`L_crit` penalizes false evictions of protected tokens (numbers, paths, error codes, CamelCase identifiers). The penalty is stratum-agnostic in definition but stratum-targeted in effect — false evictions concentrate on each voter's weakest strata.

## Mechanism B: post-inference regex override

**Where:** inference-time
**What:** After the model scores each token, a sliding window checks dropped tokens against `MUST_KEEP_RE`. Matching tokens are force-kept.

- Surgical: can only prevent an eviction, never cause one
- Cost: ~0.1ms per chunk (one regex pass)
- The 0.911→0.965 table measures THIS mechanism, not A

## Mechanism C: self-labeling loop

**Where:** training-time
**What:** Use A+B as an oracle to relabel the training data, then retrain.

- v3 (trained on noisy labels, mk_in_ref=0.72) → v4 (self-labeled, mk_in_ref=0.823)
- v4 internalized the override: override_delta = 0.000
- v5 added noise (0.967→0.961) → correctable loop invariant halted at v4
- v8 uses C3 self-distillation (Collect-Curate-Compress) with a Qwen2.5-7B teacher instead

## The Pareto frontier (λ-ablation)

| λ | Model | Heretic | Compression |
|---|-------|---------|-------------|
| 3.0 | v8 | 0.955 | 15% (production) |
| 5.0 | v17 | 0.963 | 3.7% |
| 10.0 | v16 | 0.972 | 2.8% |

Each +1.0 in λ buys ~0.01 precision at ~10% compression cost. λ=3 is the knee.
