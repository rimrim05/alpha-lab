# Estimator Lab — results (run 2026-07-10)

137 months, 2015-02 → 2026-06, PIT S&P 500 members (369–487 eligible names/month),
trailing 252d windows, one-month holds. Raw per-month data: `results.csv`,
summary: `summary.csv`. Pre-registration: `PLAN.md`.

**Holding-window alignment:** weights set at close `d` earn returns `d+1 … next_d`
(harness convention). Day `d`'s own return is the last day of the fit window, so it is
excluded from the OOS hold — no fit/eval overlap. (An earlier draft included day `d`;
correcting it moved every number by ≤ a few bps and changed no ranking.)

## Mean realized ann. vol (primary metric)

### Unconstrained (sum w = 1, shorts, |w| ≤ 5%)

| est | mean vol | t vs sample | p | net Sharpe | mean turnover |
|---|---|---|---|---|---|
| sample | 14.40% | — | — | 0.15 | 8.66 |
| pca1 | 14.95% | +1.55 | 0.124 | 0.39 | 0.29 |
| pca3 | 13.09% | −3.72 | <0.001 | 0.80 | 0.99 |
| pca5 | 12.08% | −7.29 | <0.001 | 0.70 | 1.16 |
| jse1 | 15.26% | +2.33 | 0.022 | 0.39 | 0.30 |
| jse3 | 13.27% | −3.15 | 0.002 | 0.79 | 1.01 |
| jse5 | 12.22% | −6.77 | <0.001 | 0.70 | 1.18 |
| lw | 11.64% | −10.89 | <0.001 | 0.35 | 3.23 |
| **mp** | **11.27%** | −11.82 | <0.001 | 0.71 | 1.10 |

### Long-only

| est | mean vol | t vs sample | p | net Sharpe | mean turnover |
|---|---|---|---|---|---|
| sample | 14.16% | — | — | 0.72 | 0.83 |
| **pca1** | **11.69%** | −9.55 | <0.001 | 0.77 | 0.11 |
| pca3 | 11.95% | −13.90 | <0.001 | 0.85 | 0.24 |
| pca5 | 12.11% | −15.22 | <0.001 | 0.75 | 0.27 |
| jse1 | 11.69% | −9.50 | <0.001 | 0.77 | 0.11 |
| jse3 | 11.95% | −13.90 | <0.001 | 0.85 | 0.24 |
| jse5 | 12.10% | −15.22 | <0.001 | 0.75 | 0.27 |
| lw | 13.70% | −8.73 | <0.001 | 0.73 | 0.45 |
| mp | 13.13% | −9.99 | <0.001 | 0.76 | 0.28 |

## The pre-registered JSE test (paired, jse_k − pca_k, ann. vol)

| book | k | Δvol | t | p |
|---|---|---|---|---|
| unconstrained | 1 | +31 bps | +11.7 | <0.001 |
| unconstrained | 3 | +18 bps | +9.6 | <0.001 |
| unconstrained | 5 | +14 bps | +7.9 | <0.001 |
| long_only | 1 | +0.0 bps | +0.2 | 0.84 |
| long_only | 3 | −0.6 bps | −8.2 | <0.001 |
| long_only | 5 | −0.5 bps | −8.7 | <0.001 |

## Verdict vs pre-registration

| expectation | outcome |
|---|---|
| sample worst by far (1.5–3x, >15%) | **Partly wrong.** Sample is worst or near-worst, but only ~14%, not catastrophic — the pinv min-norm solution plus the 5% cap is itself a regularizer. Its **8.7** monthly turnover is the real tell (unusable; net Sharpe 0.15). |
| pca k improves, k=3/5 ≥ k=1 | **Held unconstrained** (14.9% → 12.1% as k grows); **reversed long-only** (k=1 best at 11.69%, degrades in k). |
| jse_k < pca_k with gap growing in k | **Rejected.** Unconstrained, JSE is significantly *worse* at every k (+14 to +31 bps, t ≈ 8–12), and the gap *shrinks* in k. Long-only, the difference is statistically significant at k=3,5 but economically zero (< 1 bp). |
| lw competitive, mp ≈ lw | **Held, understated.** MP clipping is the best unconstrained estimator (11.27%), LW second — both beat every factor model. Long-only they fall behind PCA. |
| long-only compresses differences | **Held.** JSE−PCA collapses to ~0; all estimators land in 11.7–14.2%. |

**Bottom line:** the Goldberg bridge does not carry at k>1 on this design. Diagnosis
(checked, not assumed): with n=252 and ~450 strong S&P names, estimated ψ per factor is
0.93–0.997 (median 0.95–0.997; verified across all 137 months), so the dispersion bias
the correction targets is nearly absent; the rotation
only perturbs the eigenvectors and, in the unconstrained book, adds realized vol. The
muted k=1 hunt2026 result was the honest signal, not a fluke. The theory's live regime is
small n / weak factors (the factor_lab demo uses n=60); a follow-up with 60–90d windows
would test *that* regime rather than this one.

**Skeptic pass (repo rule):** no estimator posts implausibly low vol (all ≥ 11.3%), JSE
does not beat LW, and the one initially-suspicious cell (sample only ~14%, not 3x worse)
is explained by the pinv+cap regularization and confirmed by its 8.7 turnover. Nothing
here reads as too-good-to-be-true.

Runtime: ~20s single-core for the full 9-estimator × 2-book × 137-month grid.
