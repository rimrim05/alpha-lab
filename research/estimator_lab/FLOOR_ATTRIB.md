# Stage 2 — alpha-book attribution (known / sector-mean / vetted residual)

Prereg: FLOOR_ATTRIB_MEMO.md rev 2 (frozen). 14 primary windows, starts 2022-11-21 → 2026-03-02. Alphas per window, sign-flip permutation (10k joint draws). SELECTION-TAINTED history (n_trials ≥ 18, floor); live OOS excluded; 'industry' = 11-GICS-sector-MEAN controls; residual controls in 4/14 windows — SPOT-CHECKS, not robustness; L4 survival is NOT evidence of absence of residual common risk.

## Verdict (pre-committed): **SUCCESS**
- plumbing (bench beta 1.19, R² 0.94, |t₂| gate): PASS
- SPY null book benign: PASS
- expected false rule-5 count under joint null (upper bound, DSR/stress omitted): 0.33 of 7

## Attribution (annualized window-mean alphas; permutation p)

| book | class | L1 | L2 +FF | L3 +sec | L4 +res | α₄ stress | ρSVXY | DSR18/36 | gross | maxDD |
|---|---|---|---|---|---|---|---|---|---|---|
| defensive_ensemble | known-factor-premium | +20.3% (0.01) | +2.8% (0.61) | +1.6% (0.77) | +1.9% (0.75) | -2.6% | -0.05 | 0.87/0.80 | 1.85 | -26% |
| dual_momentum_gem | known-factor-premium | +30.4% (0.00) | -2.0% (0.79) | -2.5% (0.63) | -2.0% (0.70) | -3.7% | -0.04 | 0.73/0.62 | 1.32 | -41% |
| dual_momentum_gold | known-factor-premium | +42.2% (0.01) | +20.4% (0.21) | +10.1% (0.41) | +10.8% (0.38) | +9.0% | -0.07 | 0.87/0.80 | 1.33 | -41% |
| momentum_concentrated | known-factor-premium | +17.0% (0.03) | -5.3% (0.25) | -5.0% (0.25) | -4.3% (0.35) | -4.3% | +0.01 | 0.52/0.41 | 0.97 | -31% |
| trend_vol_qqq | known-factor-premium | +29.3% (0.01) | -3.4% (0.47) | -5.4% (0.37) | -5.1% (0.40) | -7.0% | +0.00 | 0.78/0.68 | 1.37 | -31% |
| vol_core_svxy | known-factor-premium | +35.1% (0.00) | +1.3% (0.71) | +1.8% (0.60) | +2.3% (0.51) | -1.1% | +0.12 | 0.82/0.74 | 1.65 | -34% |
| vol_managed_qqq | known-factor-premium | +33.0% (0.00) | -1.5% (0.65) | -2.6% (0.60) | -2.3% (0.64) | -4.7% | -0.00 | 0.80/0.71 | 1.46 | -35% |
| bench_qqq_buyhold | known-factor-premium | +24.5% (0.00) | +1.6% (0.54) | +0.3% (0.82) | +0.4% (0.79) | +0.4% | -0.04 | 0.82/0.73 | 1.00 | -35% |
| _spy_null | known-factor-premium | +16.0% (0.00) | -0.4% (0.26) | +0.3% (0.47) | +0.3% (0.41) | +0.3% | -0.01 | 0.76/0.66 | 1.00 | -34% |

## Stability (L4 ann.)

| book | half1 | half2 | hi-vol | lo-vol | sign-frac | suppression |
|---|---|---|---|---|---|---|
| defensive_ensemble | -2.8% | +6.7% | -5.6% | +9.4% | 0.79 | — |
| dual_momentum_gem | -0.0% | -3.9% | -4.0% | +0.1% | 0.71 | — |
| dual_momentum_gold | +1.0% | +20.6% | +4.8% | +16.8% | 0.64 | — |
| momentum_concentrated | -0.9% | -7.6% | -8.7% | +0.2% | 0.57 | — |
| trend_vol_qqq | +1.3% | -11.4% | -10.7% | +0.6% | 0.50 | — |
| vol_core_svxy | +10.5% | -5.9% | +1.9% | +2.8% | 0.57 | — |
| vol_managed_qqq | +3.8% | -8.4% | -5.2% | +0.6% | 0.57 | — |
| bench_qqq_buyhold | +1.6% | -0.8% | +2.1% | -1.3% | 0.57 | — |
| _spy_null | +0.4% | +0.3% | +0.8% | -0.1% | 0.57 | — |

## Provenance

- defensive_ensemble: promoted L3; hunt-2 ADAPTIVE
- dual_momentum_gem: watch; whipsaw-fragile
- dual_momentum_gold: watch; HINDSIGHT-DISCOUNTED (regime artifact)
- momentum_concentrated: sleeve-only; WF-demoted F-015; stock book (survivorship-heavy)
- trend_vol_qqq: promoted L3; hunt-2 ADAPTIVE
- vol_core_svxy: promoted L3; hunt-1; SVXY ETP-menu survivorship
- vol_managed_qqq: promoted L3; hunt-1
- bench_qqq_buyhold: control
- _spy_null: control

## Story

(appended post-run)
