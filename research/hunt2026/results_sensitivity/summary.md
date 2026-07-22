# hunt2026 holdout, re-priced at measured execution cost

**Sensitivity analysis, not a re-scoring.** The blind holdout was spent on 2026-07-10;
`results/` is write-once and untouched. This re-prices the same already-seen return
streams under a harsher single-name cost. Surviving here is not passing a second test.

SPY over the same window: **+21.97%**. Pre-registered bar: 18% net.

`frozen` = 10 bps/side, the pre-registered model. `floor` = 42 bps, the
direction-independent part of measured execution. `measured` = 58 bps, its mean.
ETF costs are unchanged at 2 bps: those books measured about zero against that.

| spec | turnover/d | frozen | floor 42 | measured 58 | cost/yr at 58 | still ≥18%? |
|---|---|---|---|---|---|---|
| dual_momentum_gold | 1.20% | +79.03% | +79.03% | +79.03% | 0.06% | yes |
| dual_momentum_gem | 3.59% | +62.78% | +62.78% | +62.78% | 0.18% | yes |
| bench_qqq_sma200_2x | 2.39% | +53.68% | +53.68% | +53.68% | 0.12% | yes |
| defensive_ensemble | 4.27% | +41.12% | +41.12% | +41.12% | 0.22% | yes |
| deep_dip_reversion | 16.97% | +41.02% | +24.32% | +16.72% | 23.01% | NO |
| vol_managed_qqq | 3.08% | +40.77% | +40.77% | +40.77% | 0.16% | yes |
| composite_book | 4.20% | +40.45% | +35.79% | +33.53% | 6.13% | yes |
| vol_core_svxy | 7.56% | +39.85% | +39.85% | +39.85% | 0.38% | yes |
| gap_drift | 7.64% | +39.33% | +31.04% | +27.08% | 11.17% | yes |
| vix_panic_buyer | 1.20% | +37.49% | +37.49% | +37.49% | 0.06% | yes |
| momentum_concentrated | 3.69% | +37.07% | +33.06% | +31.10% | 5.39% | yes |
| trend_vol_qqq | 4.72% | +35.16% | +35.16% | +35.16% | 0.24% | yes |
| trend_gated_spy_2x | 2.39% | +35.14% | +35.14% | +35.14% | 0.12% | yes |
| bench_qqq_buyhold | 0.00% | +31.25% | +31.25% | +31.25% | 0.00% | yes |
| ew_levered_vix_gate | 3.93% | +29.25% | +25.22% | +23.25% | 5.75% | yes |
| breadth_gated_leverage | 5.59% | +25.61% | +25.61% | +25.61% | 0.28% | yes |
| tsmom_multi_asset | 2.07% | +25.18% | +25.18% | +25.18% | 0.10% | yes |
| pca_minvar_jse | 0.75% | +10.53% | +9.86% | +9.53% | 1.10% | NO |
| pca_minvar_raw | 0.75% | +10.41% | +9.75% | +9.41% | 1.10% | NO |
| svxy_vix_carry | 20.72% | +7.07% | +7.07% | +7.07% | 1.04% | NO |

- cleared 18% at the frozen cost: **17** of 20
- still clear it at 58 bps: **16**
- beat SPY's +21.97% at 58 bps: **16**

The gap between the first two lines is what the frozen cost model was hiding.
