# INDEPENDENCE_MATRIX.md — are the 7 paper books independent alphas or one cluster?

**Agent 7, independent-alpha program. Real computation, 2026-07-10.**
Method + reproducible script: `research/independent_alpha/independence/compute_independence.py`
(run with `.venv/bin/python`). CSVs alongside it. Paper-only; nothing here touches live specs.

## What was computed (not hand-waved)

For each of the 7 live books I reconstructed a **daily net return series** using the exact
runner path: `compute_book` → `_heal_etfs` → `harness.run(spec, panel)["net_daily"]` on
`research/hunt2026/panel_2005.parquet` (same P&L convention: held = W.shift(1), close-to-close,
costs 2/10 bps). SPY and QQQ buy-and-hold factors built the same way. Window after warm-up:
**2005-01-03 → 2026-07-10, n = 5,413 trading days** (robustness re-run on the all-books-active
window 2015-01-02 →, n = 2,896, confirms every headline below and makes them stronger).

Per-book first-active dates (why early history is thin for some): vol_managed/vol_core 2005-02,
trend_vol 2005-10, defensive_ensemble 2005-01, dual_momentum_gold/gem 2008-05, momentum_concentrated 2015-01.

## Headline numbers

| Metric | Value |
|---|---|
| **3 vol books mean RAW pairwise corr** | **0.884** |
| **3 vol books mean RESIDUAL pairwise corr** (SPY+QQQ removed) | **0.794** (0.813 on 2015+ all-active window) |
| 3 vol books mean DOWNSIDE corr (worst-decile SPY days) | 0.765 |
| Effective independent samples n_eff (raw) | **2.80 of 7** |
| Effective independent samples n_eff (residual) | **4.12 of 7** |
| **Genuinely independent clusters among the 7** | **~3** (a hard-3, with defensive_ensemble a partial 4th bridge) |

**Verdict: the expected finding is CONFIRMED, with numbers.** vol_managed_qqq / vol_core_svxy /
trend_vol_qqq collapse to ~1 factor (residual corr 0.71–0.86, mean 0.79). Removing SPY+QQQ barely
dents their co-movement: the shared thing is a *vol/trend risk-management estimator*, not market
beta. This is the same one-cluster reality already flagged in CANONICAL_STATE §2 and F-014
(trend+vol combine HALVES median excess) / F-020 (vol-management does NOT replicate cross-market,
3/7): now quantified at the return-series level.

## Raw pairwise correlation (7×7)

```
                     volMQ  volCS  trndV  defEns  dmGold  momCon  dmGem
vol_managed_qqq       1.00   0.96   0.87   0.73    0.50    0.57    0.73
vol_core_svxy         0.96   1.00   0.83   0.70    0.50    0.57    0.73
trend_vol_qqq         0.87   0.83   1.00   0.80    0.51    0.52    0.67
defensive_ensemble    0.73   0.70   0.80   1.00    0.71    0.52    0.67
dual_momentum_gold    0.50   0.50   0.51   0.71    1.00    0.49    0.65
momentum_concentrated 0.57   0.57   0.52   0.52    0.49    1.00    0.63
dual_momentum_gem     0.73   0.73   0.67   0.67    0.65    0.63    1.00
```
vol_managed ↔ vol_core = **0.96** raw. These two are near-duplicates (SVXY variance-carry sleeve
aside). Everything is positively correlated because everything is long-biased US equity risk.

## Betas & alpha (each book on 1 + SPY + QQQ, annualized alpha)

```
                      alpha_ann  beta_SPY  beta_QQQ
vol_managed_qqq          0.055    -0.390    1.383
vol_core_svxy            0.075     0.148    0.967
trend_vol_qqq            0.076    -0.490    1.086
defensive_ensemble       0.072    -0.239    0.594
dual_momentum_gold       0.081    -0.237    0.791
momentum_concentrated   -0.002    -0.025    0.432
dual_momentum_gem        0.048    -0.188    1.017
```
All the vol/trend books load heavily on QQQ (0.97–1.38) and short a little SPY, i.e. they ARE a
levered-QQQ-with-a-vol-switch. `momentum_concentrated` has ~zero alpha (−0.002) and the lowest
factor loadings, consistent with the dead-XS-momentum finding (F-015/16). Alpha here is
regression intercept, **not** an independent-alpha claim: most of it is the vol-timing estimator,
which does not survive as a cross-market market-forecast (F-020).

## Residual correlation (after removing SPY+QQQ) — the real independence test

```
                     volMQ  volCS  trndV  defEns  dmGold  momCon  dmGem
vol_managed_qqq       1.00   0.86   0.82   0.57    0.17    0.19    0.24
vol_core_svxy         0.86   1.00   0.71   0.51    0.18    0.22    0.28
trend_vol_qqq         0.82   0.71   1.00   0.68    0.27    0.24    0.35
defensive_ensemble    0.57   0.51   0.68   1.00    0.60    0.30    0.45
dual_momentum_gold    0.17   0.18   0.27   0.60    1.00    0.31    0.50
momentum_concentrated 0.19   0.22   0.24   0.30    0.31    1.00    0.39
dual_momentum_gem     0.24   0.28   0.35   0.45    0.50    0.39    1.00
```

## Clusters (residual corr > 0.5 = same information source)

1. **Vol/trend risk-management cluster (one factor):** vol_managed_qqq, vol_core_svxy,
   trend_vol_qqq: residual corr 0.71–0.86. **These are three implementations of ONE alpha.**
2. **Cross-asset dual-momentum pair:** dual_momentum_gold ↔ dual_momentum_gem, residual 0.50.
   One mechanism, two menus (CANONICAL_STATE §2: right now they even hold an identical position).
3. **momentum_concentrated, the most independent book:** residual corr 0.19–0.39 to everything,
   the only book with near-zero residual co-movement with the vol cluster. Independent, but its
   own evidence is weak (α ≈ 0, dead XS momentum).

**defensive_ensemble is a bridge, not a 4th independent alpha.** Residual corr 0.51–0.68 to the
vol cluster AND 0.60 to dual_momentum_gold: it shares the inverse-vol/defensive mechanism with
both. It is a Portfolio-alpha sleeve (diversified premia), not an independent Market forecast.

## Four independence dimensions per pair (not one opaque score)

| Pair | Information | Mechanism | Forecast | Failure |
|---|---|---|---|---|
| vol_managed ↔ vol_core | shared (resid 0.86) | same (vol-target QQQ) | same | shared (Jaccard 0.86) |
| vol_managed ↔ trend_vol | shared (0.82) | same+trend | same | shared (0.74) |
| vol cluster ↔ defensive_ensemble | overlapping (0.5–0.68) | shared inverse-vol | overlapping | shared (0.50–0.59) |
| vol cluster ↔ dual_momentum | mostly indep (0.17–0.35) | different (mom vs vol) | independent | partial (0.42–0.67) |
| dual_gold ↔ dual_gem | shared (0.50) | same (abs+rel mom) | same | shared (0.66) |
| momentum_concentrated ↔ all | independent (0.19–0.39) | different (XS stock) | independent | independent (0.28–0.39) |

Downside (worst-decile SPY days, n=542) and shared-down-month Jaccard tables are in
`corr_downside.csv` / `shared_failure_jaccard.csv`. Crisis correlation for the 3 vol books is
0.765: **they fail together when it matters most**, so they provide no crisis diversification for
each other (the whole point of vol-management is supposed to be crisis behavior).

## Effective number of independent bets

- **n_eff (raw) = 2.80**: the 7 books carry the information of ~2.8 independent series.
- **n_eff (residual) = 4.12**: after stripping market beta, ~4.1 independent residual sources,
  but two of those "sources" (the dual-momentum pair, and defensive_ensemble's overlap) are soft.

## Bottom line

**The 7 books are NOT 7 independent alphas.** They are:
- **1 dominant cluster** = the 3 vol/trend risk-management books (residual corr 0.79, crisis corr
  0.77), one alpha wearing three tickers;
- **+ 1 dual-momentum pair** (gold/gem, one mechanism);
- **+ 1 genuinely-independent-but-weak book** (momentum_concentrated);
- **+ defensive_ensemble** as a portfolio sleeve that *bridges* the vol cluster and dual-momentum,
  not a standalone independent forecast.

**Genuinely independent clusters ≈ 3** (vol-cluster / dual-momentum / concentrated-momentum),
n_eff ≈ 2.8 raw. The promoted 4 collapse toward ONE risk-management idea plus one portfolio wrap:
exactly the concentration CANONICAL_STATE and F-014/F-020 warned about. Any capital-allocation or
"diversified book" narrative built on 7 names is overstated; it is ~3 bets, one of them dominant.

### Evidence ladder
Residualization is an **Estimator/Portfolio-alpha** diagnostic, not a market forecast: it lowers,
never raises, an independence claim. This memo supports **Level 2 (residual)** for the finding
"the vol books are one cluster"; it does not by itself grant any book a higher independent-alpha
level. Forward paper NAV (Level 5) remains the only thing that can separate the pair/bridge cases.
