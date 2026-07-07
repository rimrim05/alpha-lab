# STATE — GKX signal rotation (Gu-Kelly-Xiu, lite)

**Stage:** 1 (data + model ladder run on public CZ data); firm-level GKX blocked on WRDS
**Last session:** 2026-07-07

## Scope decision (Decision B in spec)
Full GKX predicts the firm-level cross-section from ~94 characteristics — that needs
CRSP/Compustat (WRDS), which isn't available yet. Instead this track runs GKX-lite: the
same expanding-window ML method applied at the SIGNAL level, using the Chen-Zimmermann
Open Source Asset Pricing published long-short portfolios (212 signals). It's a factor-
timing study (predict next month's signal returns, rotate), not the firm-level replication.

## Built
- `cz_data.py` — `download_cz_portfolios` (openassetpricing `dl_port('op')`),
  `load_cz_long_short` (filters port=='LS', converts percent→decimal), `validate_panel`
- `models.py` — features (12m factor momentum, 12m vol) → next-month return;
  expanding window, **annual refit** (`refit_every=12`), models OLS/Ridge/GBRT
- `scripts/gkx_run.py` — download → ladder → signal-rotation L/S → scorecard
- Tests 4/4 green.

## Data notes (learned this session)
- `dl_port('op')` returns DECILE portfolios (port "01".."10") + long-short ("LS") per
  signal, `ret` in PERCENT. Use LS only, /100. (First run mis-fed all deciles as one
  series — fixed.)
- Monthly GBRT refit measured at **886s** (~15 min) — impractical and not what GKX does.
  GKX retrains ANNUALLY on an expanding window; `refit_every=12` matches the paper and
  cuts runtime ~12×. 212 signals × 540 months (1980+ default window).

## Alignment (verified with a toy check, in-session)
`expanding_window_predict` returns y_true[t] = forward (t→t+1) return that score[t]
forecasts. `core.backtest` lags weights internally, so the runner feeds `actual.shift(1)`
— pairing weight(t) with y_true(t), realization dated t+1. No look-ahead.

## Result (2026-07-07, LS panel 1980+, 212 signals, 504 monthly obs, annual refit)
Best model = OLS. Signal-rotation L/S (long top-quintile predicted, short bottom), net of 5bps:
- Net Sharpe **0.78**, ann. return 13.4%, **max DD −52%**, hit rate 65%
- Deflated-Sharpe prob 100% (clears the 3-model multiple-testing haircut)
- Subperiods: 0.93 (1982–2003) → 0.61 (2003–2024) — real decay
- **Benchmark: equal-weight ALL signals = Sharpe 2.10** ← the punchline

**Honest read:** the rotation *badly underperforms just holding every anomaly equally*
(0.78 vs 2.10) and carries a 52% drawdown. Timing the factor zoo with 12m-momentum/vol
features adds negative value versus naive diversification here. Passes HYP-004's literal
kill thresholds (Sharpe > 0.3, deflated > 50%) but **fails the benchmark test** — which is
the one that matters. Caveats: (a) apples-to-oranges — rotation is signal-neutral L/S,
benchmark is net-long all anomalies harvesting the average premium; (b) CZ "op" = in-sample
original-paper portfolios, so the 2.10 benchmark is gross and in-sample-flattered; (c) no
cost on the benchmark. Still: no evidence the ML timing beats diversification.

## Next
1. Verdict for HYP-004: leaning **dead-for-me** (doesn't beat equal-weight). Kristen's Stage-4 call.
2. If pursued: richer features (factor BM/value spread, macro state, cross-signal momentum),
   and a fairer benchmark (best single signal, 60/40 rotation-vs-hold blend).
3. Full firm-level GKX remains gated on WRDS — the real replication, deferred.
