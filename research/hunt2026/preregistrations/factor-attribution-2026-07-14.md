# Preregistration — multi-factor attribution of the live hunt2026 books (EXP-2026-07-14-factor-attribution)

Written and FROZEN 2026-07-14, before any regression is run. Stage-0 authorization:
Kristen's 2026-07-14 program directive ("autonomous research-program manager… do not ask
me to approve routine next steps"), which explicitly requests this experiment. Layer B
diagnostic (measurement of frozen books; no spec, allocation, or deployment change).

## Question

Does any live hunt2026 book have residual alpha after controlling for known and credible
factor exposures — or is the book fully explained by market beta, the QQQ−SPY spread,
and standard premia (size, value, momentum, quality, trend)?

## Books (all 7 live; frozen specs, harness `net_daily`, net of the frozen 10/2 bps costs)

| book | freeze | claim-bearing (blind) window |
|---|---|---|
| vol_managed_qqq | c9e22c8 | 2025-07-11 → 2026-05-29 (FF bind; ~222 obs — LOW POWER, disclosed) |
| vol_core_svxy | c9e22c8 | same |
| dual_momentum_gem | c9e22c8 | same |
| momentum_concentrated | c9e22c8 | same |
| trend_vol_qqq | 833000d | 2021-07-12 → 2026-05-29 (~1,225 obs) |
| defensive_ensemble | 833000d | same |
| dual_momentum_gold | 833000d | same |

Full-history (2014→cut) regressions are run for context only and labeled IN-SAMPLE
(design data); no alpha claim may cite them. Live paper NAV (started 2026-07-10) is
too short to use; excluded.

## Factor models (nested; all daily, close-to-close, aligned on common dates; book excess = net_daily − RF)

- **M0** CAPM: Mkt−RF.
- **M1** known premia: FF5 (Mkt−RF, SMB, HML, RMW, CMA) + MOM (`data/raw/ff5_factors_daily.parquet`, `ff_factors_daily.parquet`; manifest-logged).
- **M2 (PRIMARY)**: M1 + TSMOM proxy + QQQ-residual.
  - TSMOM proxy: for menu {SPY, QQQ, IWM, EFA, GLD, TLT} (those present in panel_2005),
    sign of trailing 252d total return (skip last 21d) × next-day return, equal-weighted
    across assets, scaled to 10% ann. vol using trailing 63d vol. Fully PIT, prices only.
  - QQQ-residual: daily QQQ excess return orthogonalized to M1 factors over the full
    common sample (one projection, no refit). Captures the Nasdaq/growth spread as a
    known, non-alpha exposure. Classified per house rules as "likely leaked known risk,"
    never as a premium.
- **M3** (stock book momentum_concentrated only): M2 + vetted residual statistical
  factors from the FLOOR_REALDATA pipeline — screen-passing PC2–5 only, PC1 excluded
  (leakage footprint, FLOOR_REALDATA.md), leakage-flagged factors excluded, windows with
  coverage ≥ 90% only. If the vetted panel cannot be built PIT for the blind window,
  M3 is reported as NOT AVAILABLE rather than improvised.

No daily low-volatility or liquidity factor exists in our data (AQR BAB is monthly;
Pastor-Stambaugh monthly). Documented limitation: low-vol exposure is partially absorbed
by rolling market beta + TSMOM; liquidity is unmodeled.

## Estimation

- OLS on daily excess returns, Newey-West HAC t-stats, lag 5 (hand-rolled; validated
  against a published example before use — self-check required in the run script).
- Rolling 252d window (63d step) alphas and betas for stability.
- Subperiods: 2021H2–2022 (bear), 2023–2024, 2025→ (blind-1y overlap).
- Financing stress line (books hold gross up to 2x; harness charges no financing):
  alpha_stress = alpha − max(avg_gross − 1, 0) × (mean RF + 0.50%/yr). Reported next to
  every alpha; not a model change.

## Controls (identical pipeline, same windows)

- SPY buy-and-hold, QQQ buy-and-hold (calibration: M1 alpha must be ≈ 0, |t| < 2, else
  the pipeline is broken — hard gate, fix plumbing not thresholds).
- Static 1.5x QQQ daily-rebalanced (leverage placebo: leverage alone must not
  manufacture alpha).
- bench_qqq_sma200_2x frozen spec (naive trend parent: if a vol/trend book's alpha ≈
  its naive parent's alpha, the alpha is the trend premium, not engineering).

## Decision rules (pre-committed)

Book-level "residual-alpha candidate" requires ALL of:
1. M2 blind-window alpha NW-t ≥ 2 AND M1 alpha t ≥ 2 (model disagreement ⇒ M2 decides,
   no further model search);
2. blind window split in half: alpha point estimate positive in both halves;
3. placebo gates pass (SPY/QQQ |t| < 2; 1.5x QQQ |t| < 2);
4. alpha survives the financing stress line (still > 0).

Program verdict mapping (exactly one):
- **no evidence of residual alpha** — no book meets rule 1.
- **factor-premium harvesting with some unexplained residual return** — no candidate,
  but ≥1 book has M2 blind alpha > 2%/yr with 1 ≤ t < 2, or a candidate fails rules 2–4.
- **promising but unproven residual alpha** — ≥1 candidate whose only blind sample is
  the 1-year window (power-limited), or a 5y candidate failing exactly one of rules 2–4
  marginally.
- **strong evidence of residual alpha** — ≥1 candidate on the 5-year blind window with
  t ≥ 2.4 (multiplicity: 7 books ≈ 3 independent clusters per INDEPENDENCE_MATRIX,
  Bonferroni m=3) passing all rules.

## Trial accounting

One registered experiment; 4 nested models × 7 books + 4 controls, ALL reported (no
selection). Adaptive-loop flag: **yes** — targets blind-promoted books. Descriptive
diagnostic; adds no spec trial to the hunt count. Ambiguity rule: the only permitted
adjudication is the pre-specified M2-decides rule; no post-hoc factors, lags, or windows.

## Outputs

`research/attribution/` — run_attribution.py, attribution.csv (per book × model ×
window: alpha, t, betas, R²), rolling.csv, ATTRIBUTION.md (results vs this prereg),
run stamp via core.eval.run_manifest.
