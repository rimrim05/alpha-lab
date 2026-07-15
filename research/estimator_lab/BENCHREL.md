# Benchmark-relative (tracking) JSE vs PCA — EXP-2026-07-14-jse-benchrel

One-shot adjudication of the last UNTESTED cell in JSE_BOUNDARY_MAP.md §5, requested by
the adversarial review. Prereg: research/hunt2026/preregistrations/jse-benchrel-2026-07-14.md
(frozen thresholds). 138 months 2015-02→2026-06, n=63, PIT S&P 500, EW benchmark over all
eligible names, tracking basket = every 5th sorted ticker (~74–98 names), min-TE closed form
+ house long-only clip/5% cap. Raw data: benchrel.csv.

## Result

| est | mean TE | med TE | mean turnover |
|---|---|---|---|
| sample | 4.00% | 3.70% | 1.66 |
| pca1 | 2.57% | 2.43% | 1.04 |
| pca3 | 2.43% | 2.32% | 1.06 |
| pca5 | 2.41% | 2.33% | 1.09 |
| jse1 | 2.57% | 2.42% | 1.03 |
| jse3 | 2.43% | 2.31% | 1.06 |
| jse5 | 2.41% | 2.33% | 1.09 |
| lw | 2.38% | 2.29% | 1.16 |
| **mp** | **2.33%** | **2.22%** | 1.02 |

Decisive paired deltas (jse_k − pca_k, annualized TE):
k=1 +0.06 bps (t +0.77, p 0.44) · k=3 −0.04 bps (t −0.89, p 0.38) · k=5 −0.04 bps (t −0.81, p 0.42).

## Verdict (pre-committed rule): **VERDICT STANDS — no overturn**

Overturn required rel ΔTE ≤ −0.5% with p < 0.05 AND ≤ −10 bps absolute; observed rel
−0.02%, p 0.42, −0.04 bps. The benchmark-relative cell now reads like every other cell:
JSE ≈ PCA to measurement noise, and spectrum shrinkage (MP, LW) beats both.

## Story

TE, like min-var vol, turns out to be dominated by the subspace and the spectrum, not the
within-subspace eigenvector directions — consistent with the subspace-invariance diagnosis
(min-var is a subspace functional; evidently min-TE against a spanned-ish EW benchmark is
too). The one theoretical opening for JSE here (active weights depend on eigenvector
directions through (Σ w_b)_B) does not materialize at S&P scale because ψ̂ ≈ 1: the corrected
and raw leading eigenvectors are nearly identical, and the weak factors' corrections are
noise-dominated rotations that wash out of the basket solve. Boundary map §5's
benchmark-relative row: UNTESTED → tested, same sign as everything else.

No further benchmark-relative variants are permitted under this prereg (one shot).
