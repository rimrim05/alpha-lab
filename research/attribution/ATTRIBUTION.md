# Factor attribution of the live hunt2026 books (EXP-2026-07-14-factor-attribution)

Implements the frozen prereg `research/hunt2026/preregistrations/factor-attribution-2026-07-14.md`.
All regressions truncated at FF data end 2026-05-29. Newey-West lag 5. Alpha annualized x252.

## Placebo gate (checked first)

Hard pipeline gate: M1 alpha on SPY / QQQ buy-and-hold must have \|t\| < 2.
Rule-3 leverage placebo: 1.5x QQQ static \|t\| < 2 on the book's window.

| control | window | alpha_ann | NW t | R2 | \|t\|<2 |
|---|---|---|---|---|---|
| CTRL_spy_buyhold | blind_1y | +0.97% | +1.23 | 0.996 | yes |
| CTRL_spy_buyhold | blind_5y | +0.20% | +0.44 | 0.995 | yes |
| CTRL_qqq_buyhold | blind_1y | +3.29% | +0.98 | 0.944 | yes |
| CTRL_qqq_buyhold | blind_5y | +3.36% | +1.55 | 0.959 | yes |
| CTRL_qqq_1.5x_static | blind_1y | +7.07% | +1.42 | 0.944 | yes |
| CTRL_qqq_1.5x_static | blind_5y | +6.82% | +2.09 | 0.959 | NO |

Hard gate (SPY/QQQ): PASS.

Integrity gate: all 7 books reproduce their frozen total_net/sharpe to <1e-9. PASS.

## Books — blind window, all models

| book | model | n | alpha_ann | NW t | R2 | beta_Mkt | beta_TSMOM | beta_QQQRES | alpha_stress |
|---|---|---|---|---|---|---|---|---|---|
| vol_managed_qqq | M0 | 219 | +5.67% | +0.51 | 0.863 | +1.87 |  |  | +3.61% |
| vol_managed_qqq | M1 | 219 | +2.57% | +0.32 | 0.905 | +1.80 |  |  | +0.51% |
| vol_managed_qqq | M2 | 219 | +1.42% | +0.25 | 0.968 | +1.54 | +0.23 | +1.59 | -0.64% |
| vol_core_svxy | M0 | 219 | +1.91% | +0.25 | 0.936 | +1.90 |  |  | -1.75% |
| vol_core_svxy | M1 | 219 | +1.12% | +0.19 | 0.950 | +1.92 |  |  | -2.54% |
| vol_core_svxy | M2 | 219 | +0.54% | +0.10 | 0.966 | +1.79 | +0.12 | +0.80 | -3.12% |
| dual_momentum_gem | M0 | 219 | +22.75% | +1.53 | 0.767 | +1.75 |  |  | +20.34% |
| dual_momentum_gem | M1 | 219 | +19.18% | +1.32 | 0.781 | +1.72 |  |  | +16.76% |
| dual_momentum_gem | M2 | 219 | +15.79% | +1.12 | 0.816 | +1.18 | +0.74 | +0.63 | +13.37% |
| momentum_concentrated | M0 | 219 | +8.21% | +0.56 | 0.568 | +1.38 |  |  | +8.21% |
| momentum_concentrated | M1 | 219 | -5.83% | -0.54 | 0.736 | +0.96 |  |  | -5.83% |
| momentum_concentrated | M2 | 219 | -7.47% | -0.68 | 0.747 | +0.69 | +0.36 | +0.36 | -7.47% |
| trend_vol_qqq | M0 | 1223 | +14.67% | +1.85 | 0.337 | +0.73 |  |  | +13.15% |
| trend_vol_qqq | M1 | 1223 | +11.68% | +1.63 | 0.471 | +0.68 |  |  | +10.16% |
| trend_vol_qqq | M2 | 1223 | +9.11% | +1.50 | 0.624 | +0.48 | +0.66 | +1.31 | +7.59% |
| defensive_ensemble | M0 | 1223 | +11.66% | +2.25 | 0.332 | +0.48 |  |  | +7.84% |
| defensive_ensemble | M1 | 1223 | +9.52% | +2.01 | 0.465 | +0.46 |  |  | +5.70% |
| defensive_ensemble | M2 | 1223 | +6.72% | +1.77 | 0.686 | +0.29 | +0.76 | +0.30 | +2.91% |
| dual_momentum_gold | M0 | 1223 | +21.11% | +1.95 | 0.147 | +0.59 |  |  | +19.35% |
| dual_momentum_gold | M1 | 1223 | +17.35% | +1.63 | 0.220 | +0.55 |  |  | +15.60% |
| dual_momentum_gold | M2 | 1223 | +12.98% | +1.32 | 0.373 | +0.29 | +1.20 | +0.23 | +11.23% |

## Decision rules per book (blind window)

| book | 1: M2 t>=2 & M1 t>=2 | 2: both halves alpha>0 | 3: placebos | 4: stress>0 | candidate |
|---|---|---|---|---|---|
| vol_managed_qqq | fail (M2 t=+0.25, M1 t=+0.32) | fail | PASS | fail | no |
| vol_core_svxy | fail (M2 t=+0.10, M1 t=+0.19) | fail | PASS | fail | no |
| dual_momentum_gem | fail (M2 t=+1.12, M1 t=+1.32) | fail | PASS | PASS | no |
| momentum_concentrated | fail (M2 t=-0.68, M1 t=-0.54) | fail | PASS | fail | no |
| trend_vol_qqq | fail (M2 t=+1.50, M1 t=+1.63) | PASS | fail | PASS | no |
| defensive_ensemble | fail (M2 t=+1.77, M1 t=+2.01) | PASS | fail | PASS | no |
| dual_momentum_gold | fail (M2 t=+1.32, M1 t=+1.63) | fail | fail | PASS | no |

## Blind-window half-split (M2 alpha, annualized)

| book | half 1 | half 2 |
|---|---|---|
| vol_managed_qqq | +8.48% | -7.09% |
| vol_core_svxy | +3.27% | -2.95% |
| dual_momentum_gem | -9.41% | +39.68% |
| momentum_concentrated | -9.01% | -9.14% |
| trend_vol_qqq | +15.17% | +7.05% |
| defensive_ensemble | +3.66% | +10.93% |
| dual_momentum_gold | -6.82% | +33.58% |

## Full history (IN-SAMPLE context — design data, no alpha claim may cite this)

| book | model | n | alpha_ann | NW t | R2 |
|---|---|---|---|---|---|
| vol_managed_qqq | M0 | 2779 | +9.92% | +2.11 | 0.667 |
| vol_managed_qqq | M1 | 2779 | +9.15% | +2.22 | 0.754 |
| vol_managed_qqq | M2 | 2779 | +9.47% | +3.21 | 0.861 |
| vol_core_svxy | M0 | 2779 | +10.96% | +2.42 | 0.720 |
| vol_core_svxy | M1 | 2779 | +10.66% | +2.41 | 0.751 |
| vol_core_svxy | M2 | 2779 | +10.96% | +2.89 | 0.802 |
| dual_momentum_gem | M0 | 2779 | +5.42% | +1.27 | 0.727 |
| dual_momentum_gem | M1 | 2779 | +2.93% | +0.78 | 0.786 |
| dual_momentum_gem | M2 | 2779 | +3.56% | +1.18 | 0.844 |
| momentum_concentrated | M0 | 2779 | -0.98% | -0.25 | 0.572 |
| momentum_concentrated | M1 | 2779 | -3.27% | -1.00 | 0.742 |
| momentum_concentrated | M2 | 2779 | -2.90% | -0.93 | 0.760 |
| trend_vol_qqq | M0 | 2779 | +11.54% | +2.08 | 0.357 |
| trend_vol_qqq | M1 | 2779 | +10.12% | +1.90 | 0.440 |
| trend_vol_qqq | M2 | 2779 | +10.85% | +2.59 | 0.609 |
| defensive_ensemble | M0 | 2779 | +4.77% | +1.42 | 0.409 |
| defensive_ensemble | M1 | 2779 | +3.44% | +1.14 | 0.530 |
| defensive_ensemble | M2 | 2779 | +4.29% | +1.93 | 0.737 |
| dual_momentum_gold | M0 | 2779 | +8.79% | +1.32 | 0.368 |
| dual_momentum_gold | M1 | 2779 | +5.56% | +0.89 | 0.459 |
| dual_momentum_gold | M2 | 2779 | +6.90% | +1.25 | 0.578 |
| CTRL_bench_qqq_sma200_2x | M0 | 2779 | +14.37% | +2.00 | 0.404 |
| CTRL_bench_qqq_sma200_2x | M1 | 2779 | +12.20% | +1.78 | 0.485 |
| CTRL_bench_qqq_sma200_2x | M2 | 2779 | +13.03% | +2.41 | 0.629 |

## Subperiods (M2, full-history series)

| book | subperiod | n | alpha_ann | NW t |
|---|---|---|---|---|
| vol_managed_qqq | 2021H2-2022 | 379 | +6.02% | +1.05 |
| vol_managed_qqq | 2023-2024 | 502 | +3.79% | +0.91 |
| vol_managed_qqq | 2025-> | 348 | +1.65% | +0.25 |
| vol_core_svxy | 2021H2-2022 | 379 | +4.34% | +0.74 |
| vol_core_svxy | 2023-2024 | 502 | +5.50% | +1.24 |
| vol_core_svxy | 2025-> | 348 | +1.39% | +0.18 |
| dual_momentum_gem | 2021H2-2022 | 379 | -8.42% | -0.74 |
| dual_momentum_gem | 2023-2024 | 502 | -1.28% | -0.17 |
| dual_momentum_gem | 2025-> | 348 | +9.13% | +0.87 |
| momentum_concentrated | 2021H2-2022 | 379 | +3.15% | +0.51 |
| momentum_concentrated | 2023-2024 | 502 | -5.45% | -0.83 |
| momentum_concentrated | 2025-> | 348 | -3.72% | -0.45 |
| trend_vol_qqq | 2021H2-2022 | 379 | +7.76% | +0.84 |
| trend_vol_qqq | 2023-2024 | 502 | +0.12% | +0.02 |
| trend_vol_qqq | 2025-> | 348 | +1.46% | +0.12 |
| defensive_ensemble | 2021H2-2022 | 379 | +6.74% | +1.32 |
| defensive_ensemble | 2023-2024 | 502 | -5.80% | -1.03 |
| defensive_ensemble | 2025-> | 348 | +15.83% | +2.40 |
| dual_momentum_gold | 2021H2-2022 | 379 | -8.54% | -0.87 |
| dual_momentum_gold | 2023-2024 | 502 | +1.35% | +0.15 |
| dual_momentum_gold | 2025-> | 348 | +38.27% | +1.66 |

## Naive trend parent (bench_qqq_sma200_2x, blind windows)

| window | model | alpha_ann | NW t | R2 |
|---|---|---|---|---|
| blind_1y | M0 | +12.38% | +0.77 | 0.725 |
| blind_1y | M1 | +7.38% | +0.58 | 0.776 |
| blind_1y | M2 | +5.80% | +0.54 | 0.865 |
| blind_5y | M0 | +18.42% | +1.75 | 0.354 |
| blind_5y | M1 | +15.60% | +1.64 | 0.474 |
| blind_5y | M2 | +12.42% | +1.55 | 0.623 |

## M3 (momentum_concentrated)

NOT AVAILABLE: the vetted FLOOR_REALDATA residual-factor panel is not built PIT for the blind window in this run; per prereg it is reported as NOT AVAILABLE rather than improvised.

## Story

Program verdict (prereg mapping): **factor-premium harvesting with some unexplained residual return**.

The 5y-window rule-3 failure comes from the 1.5x QQQ leverage placebo (M1 t >= 2): the harness charges no financing, so static leverage earns ~0.5 x RF (~+2%/yr) of mechanical alpha over 5 years. This is the free-financing effect the stress line corrects for, and it caps what any levered book's regression alpha can mean.

- vol_managed_qqq: M2 blind alpha +1.4%/yr (t=+0.25, R2=0.97); rules 3 pass.
- vol_core_svxy: M2 blind alpha +0.5%/yr (t=+0.10, R2=0.97); rules 3 pass.
- dual_momentum_gem: M2 blind alpha +15.8%/yr (t=+1.12, R2=0.82); rules 3/4 pass.
- momentum_concentrated: M2 blind alpha -7.5%/yr (t=-0.68, R2=0.75); rules 3 pass.
- trend_vol_qqq: M2 blind alpha +9.1%/yr (t=+1.50, R2=0.62); rules 2/4 pass.
- defensive_ensemble: M2 blind alpha +6.7%/yr (t=+1.77, R2=0.69); rules 2/4 pass.
- dual_momentum_gold: M2 blind alpha +13.0%/yr (t=+1.32, R2=0.37); rules 4 pass.

## M3 addendum (run 2026-07-14, after residual_factors.parquet landed)

Prereg M3 cell (momentum_concentrated blind window + vetted residual factors). Coverage
deviation, disclosed: x2 has zero vetted days in the blind window (its windows kept no
factors there), so the full x2–x5 design is infeasible; run on the coverage the vetting
produced, no gates relaxed.

| design | n days | M2 alpha (same days) | M3 alpha | M3 t | residual-factor t's |
|---|---|---|---|---|---|
| M2 + x4,x5 | 122 | −14.77% (t −0.95) | −10.72% | −0.64 | x4 −0.50, x5 +1.19 |
| M2 + x3,x4,x5 | 59 | −8.47% (t −0.58) | +3.21% | +0.23 | x3 −2.54, x4 +2.21, x5 +3.00 |

Verdict unchanged: no residual-alpha candidate. Vetted residual statistical factors absorb
some variance (R² 0.754→0.764, 0.894→0.908) but reveal no positive alpha; the only cells
where they load significantly are the n=59 low-power subset. Rule 1 remains failed for
momentum_concentrated under every model M0–M3.
