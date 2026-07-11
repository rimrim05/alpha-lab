# Deflated Sharpe — 5y window, N=18 trials (adaptive loops make true N larger; see ledger)

Expected max daily Sharpe from luck alone: 0.0334 (annualized ≈ 0.53)

| spec | ann Sharpe | DSR = P(SR > luck-max) | P(SR > 0) |
|---|---|---|---|
| defensive_ensemble | 1.32 | 95.8% | 99.8% |
| trend_vol_qqq | 1.11 | 89.8% | 99.2% |
| dual_momentum_gold | 1.07 | 87.7% | 99.0% |
| vol_managed_qqq | 0.94 | 81.5% | 98.1% |
| vol_core_svxy | 0.93 | 81.2% | 98.0% |
| tsmom_multi_asset | 0.91 | 79.8% | 97.8% |
| vix_panic_buyer | 0.83 | 74.9% | 96.9% |
| momentum_concentrated | 0.80 | 72.4% | 96.1% |
| trend_gated_spy_2x | 0.80 | 72.4% | 96.1% |
| dual_momentum_gem | 0.74 | 68.2% | 95.1% |
| breadth_gated_leverage | 0.61 | 57.3% | 91.6% |
| composite_book | 0.61 | 57.1% | 91.2% |
| gap_drift | 0.56 | 52.7% | 89.5% |
| pca_minvar_jse | 0.55 | 52.0% | 89.0% |
| pca_minvar_raw | 0.55 | 51.6% | 88.9% |
| ew_levered_vix_gate | 0.53 | 49.8% | 88.0% |
| svxy_vix_carry | 0.26 | 27.5% | 71.5% |
| deep_dip_reversion | 0.22 | 24.1% | 68.5% |

DSR reads: probability the spec's Sharpe exceeds what the LUCKIEST of 18
independent tries would show by chance. Round-1 specs are in-sample-tinted on
this window; only round-2 rows are clean. P(SR>0) ignores selection entirely
(upper bound on honesty).
