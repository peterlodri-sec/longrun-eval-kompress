# Voting Ensemble Paradox

## The claim
Multi-checkpoint voting ensembles with asymmetric training-data floors collapse to the per-stratum weakest voter under k-of-N drop voting. Adding stronger voters cannot help.

## The intuition
You have N compression checkpoints voting on which tokens to keep. Each was trained on a different quality floor — some are great, some are bad. You'd think voting together would help. It doesn't.

Under AND voting (keep only if ALL voters agree to keep), the weakest voter on each stratum vetoes every keep. The ensemble's eviction decision on each stratum is the **k-th order statistic** of the voter indicators — the k-th weakest on that stratum.

## The proof (Theorem 1)

Under per-stratum monotone-rejection refinement (Definition 2) and unanimity-to-keep voting (Definition 3):

$$\mathbb{I}_{\mathrm{ens}}(x) = \mathbb{I}_{i^\star_k}(x) \quad \forall x \in S_k$$

**Proof:** Fix stratum $S_k$ and token $x \in S_k$. By monotone-refinement, $\mathbb{I}_{i^\star_k}(x) \ge \mathbb{I}_i(x)$ for every $i$. Because each indicator is {0,1}-valued, the pointwise maximum equals the largest indicator. QED.

## The k-of-N generalization (Remark 1)

Under k-of-N drop voting, the ensemble evicts x iff ≥k voters evict. The per-stratum eviction indicator is the k-th order statistic:
- k=1 (AND): per-stratum **weakest** voter
- k=majority: per-stratum **median** voter
- k=N (OR): per-stratum **strongest** voter

The Pareto collapse holds for every k < N.

## Empirical confirmation

| Config | exact_keep_pct | Note |
|--------|---------------|------|
| v4 alone (best single) | 0.967 | — |
| Ensemble (majority 2/3) | 0.931 | **−0.031 paradox collapse** |

The 3-checkpoint majority ensemble (v3+v4+v5) scores 0.031 below the best single model.

## The fix
The 3.0× heavy false-eviction penalty on critical-syntactic tokens shrinks each voter's false-eviction set fastest on its weakest strata, lifting the collapse floor uniformly. See [[Three-Mechanisms]].

## Interactive demo
Try it yourself: https://kompress.vaked.dev/notebook/
