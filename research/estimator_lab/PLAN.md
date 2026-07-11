# Estimator Lab — pre-registration

Written 2026-07-10, BEFORE running anything. The `expected` column below was filled
in first; RESULTS.md reports against it.

## Question

Which covariance estimator produces minimum-variance portfolios with the lowest
realized out-of-sample volatility on S&P 500 daily returns?

This is the Goldberg research bridge: the hunt2026 `pca_minvar_jse` vs `pca_minvar_raw`
pair showed a muted +15bps at k=1; this lab runs the pre-registered k>1 JSE test,
judged on realized RISK, not returns.

## Setup

- Panel: `research/hunt2026/panel_2005.parquet`, PIT S&P 500 members
  (member flag > 0, ETF/index tickers excluded per the frozen spec's exclusion set).
- Walk-forward: first trading day of each month, 2015-01 → 2026-06 (~138 months).
- Estimation window: trailing 252 return days; eligibility = member on rebalance
  date + complete 252d return history. Universe ~500 names (p > n by design).
- Portfolios, per estimator, per month:
  - **Unconstrained min-var**: w ∝ Σ⁻¹1, sum w = 1, shorts allowed, then per-name
    |w| clipped at 5% and renormalized (single-pass, matching house cap convention;
    not the exact QP).
  - **Long-only min-var**: same, negatives clipped to 0, 5% cap, renormalized.
- Hold one month (fixed weights within the month). Delisted/missing next-month
  returns treated as 0 (cash-out).
- Primary metric: realized annualized vol of the next month's daily portfolio
  returns, averaged over months, paired per month across estimators.
  Significance: paired t-test vs sample covariance.
- Secondary: full-period realized Sharpe (net of 10bps/side stock costs on
  monthly turnover) and mean monthly one-side turnover.

## Estimators (all: cov(returns_window) -> Sigma)

| id | description |
|---|---|
| sample | sample covariance (singular since p > n; min-var via pseudoinverse) |
| pca1 / pca3 / pca5 | k-factor PCA: Σ = Σᵢ (σᵢ²/n) hᵢhᵢ' + diag(idio residual var) |
| jse1 / jse3 / jse5 | same, but each hᵢ rotated toward the equal-weight direction q with ψᵢ² = max(τ, 1 − p·δ²/σᵢ²), τ = 0.01 — the hunt2026 pca_minvar_jse correction generalized to k>1 (factor_lab ψ-hat form) |
| lw | Ledoit-Wolf shrinkage to scaled identity (closed form; sklearn 1.9.0 is installed, used as implementation) |
| mp | Marchenko-Pastur eigenvalue clipping: eigenvalues below λ₊ = σ̄²(1+√(p/n))² replaced by their mean (trace-preserving) |

## Pre-registered expectations (filled BEFORE running)

Realized ann. vol, unconstrained book, relative to sample covariance:

| estimator | expected |
|---|---|
| sample | Worst by far. p > n ⇒ pseudoinverse min-var overfits noise directions; expect realized vol 1.5–3x the structured estimators, possibly > 15% ann. |
| pca1 | Large improvement over sample; roughly 8–11% ann. vol. |
| pca3 | ≈ pca1 or slightly better (1–5% relative); more structure captured, little overfit at k=3. |
| pca5 | ≈ pca3; diminishing returns, maybe flat or marginally worse than pca3. |
| jse1 | Slightly below pca1 (0–2% relative vol reduction) — consistent with the muted k=1 hunt result. |
| jse3 | The interesting cell: expect the JSE edge to be a bit larger than at k=1 (1–3% relative vs pca3), since more factors ⇒ more dispersion bias to correct. Statistically, may still not clear p < 0.05 over ~138 months. |
| jse5 | Same direction as jse3; correction on weak factors is floor-limited (τ), so gain similar to jse3, not bigger. |
| lw | Competitive with pca3, within ±3% relative; LW-to-identity is a blunt target so likely slightly worse than the factor models. |
| mp | ≈ lw, maybe marginally better (keeps the top of the spectrum intact). |

Long-only: all estimators compress toward each other (the constraint is itself a
shrinkage); expect JSE-vs-PCA differences to shrink to ~nothing, ordering vs
sample preserved but smaller.

Verdict rule: an estimator "beats" sample covariance if mean realized vol is lower
with paired t-test p < 0.05. JSE "confirms the Goldberg bridge" if jse_k < pca_k
mean vol at every k with the gap growing in k; "muted again" otherwise.
