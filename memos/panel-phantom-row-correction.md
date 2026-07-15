# Correction memo — phantom 2026-05-25 row in the hunt2026 holdout panels (2026-07-14)

Found by the factor-attribution integrity audit (research/attribution/INTEGRITY_AUDIT.md,
FAIL item 1). Frozen results/*.json and results5y/*.json are write-once and were NOT
modified; this memo is the correction of record. Corrected recomputations below are
memo-only — every citation of the frozen numbers should now carry this memo as a footnote.

## Root cause

`build_sandbox.py` set the panel calendar to the union of all tickers' dates
(`cal = close.index`). yfinance returned a 2026-05-25 (Memorial Day, market closed) row
for ^VIX only, so the calendar gained a phantom day with NaN closes for every tradable
ticker. `extend_panel.py` already guarded against exactly this ("^VIX-only holidays from
the calendar union"), which is why `panel_2005.parquet` was clean; the guard was never
mirrored into the train/holdout builder. Effects of the phantom row: the harness booked
0 P&L across 05-25/26 (a real +1.9% day for defensive_ensemble scored as 0), and the NaN
poisoned rolling vol/SMA windows in the specs for weeks afterward, distorting June-2026
gating and sizing.

## Fix (2026-07-14)

1. `build_sandbox.py`: rows with no non-signal close are now dropped before the
   train/holdout split (same guard as extend_panel.py).
2. `holdout.parquet` (252→251 rows) and `holdout5y.parquet` (1256→1255): the single
   phantom row was dropped surgically — no refetch, every other value bit-identical
   (asserted). Pre-fix originals archived at
   `research/hunt2026/archive/holdout{,5y}_phantom20260525.parquet` so the frozen JSONs
   remain reproducible against their as-run inputs.
3. `sandbox_meta.json`: row counts updated + correction key.

Not affected (verified): `panel_2005.parquet`, `train.parquet`, `train5y.parquet` (scanned:
no near-empty rows); everything built on panel_2005 — walk-forward, estimator lab,
independence matrix, live paper loop (`hunt_paper_run.py` uses panel_2005 + fresh bars
with ffill healing). The factor-attribution experiment: the audit already reran affected
cells with the row healed — no conclusion flips (its FF window also ends 2026-05-29).

## Corrected numbers (harness rerun on fixed panels vs frozen JSONs)

SPY benchmark (1y blind): **+21.97%, Sharpe 1.65, maxDD −8.9%** (was +21.17% / 1.59).
SPY 5y: +85.5% total ≈ 13.1% CAGR (was 13.0%) — effectively unchanged.

### 1y blind (results/), corrected net and beta-matched excess (avg_gross × SPY convention)

| spec | frozen net | corrected net | Δ pp | corrected excess (was) |
|---|---|---|---|---|
| dual_momentum_gem | +58.56% | +62.78% | +4.2 | **+29.8% (+26.8%)** |
| momentum_concentrated | +35.44% | +37.07% | +1.6 | **+18.9% (+16.6%)** — Sharpe 1.21→1.46 |
| deep_dip_reversion | +27.55% | +41.02% | **+13.5** | **+8.1% (−4.2%) SIGN FLIP** |
| vol_managed_qqq | +42.51% | +40.77% | −1.7 | +7.1% (+12.3%) — avg gross 1.43→1.53 |
| gap_drift | +37.52% | +39.33% | +1.8 | +6.4% (+5.8%) |
| vix_panic_buyer | +36.05% | +37.49% | +1.4 | +3.2% (+3.2%) |
| vol_core_svxy | +36.10% | +39.85% | +3.7 | +1.2% (−1.1%) SIGN FLIP |
| composite_book | +38.97% | +40.45% | +1.5 | −3.5% (−3.3%) |
| trend_gated_spy_2x | +31.47% | +35.14% | +3.7 | −7.8% (−4.5%) |
| breadth_gated_leverage | +28.24% | +25.61% | −2.6 | −8.3% (−2.1%) |
| ew_levered_vix_gate | +28.16% | +29.25% | +1.1 | −12.7% (−12.3%) |
| svxy_vix_carry | +5.88% | +7.07% | +1.2 | −14.9% (−15.3%) |
| pca_minvar_jse | +12.96% | +10.53% | −2.4 | −33.4% (−29.4%) |
| pca_minvar_raw | +12.81% | +10.41% | −2.4 | −33.5% (−29.5%) |

### 5y blind (results5y/), corrected totals (selected; full rerun in this memo's source run)

| spec | frozen total | corrected | Δ pp |
|---|---|---|---|
| dual_momentum_gold | +258.5% | +268.1% | +9.6 |
| vol_core_svxy | +196.4% | +204.5% | +8.2 |
| dual_momentum_gem | +128.3% | +134.4% | +6.1 |
| trend_gated_spy_2x | +114.2% | +120.2% | +6.0 |
| deep_dip_reversion | +11.0% | +22.7% | +11.7 |
| defensive_ensemble | +147.6% | +146.6% | −1.0 |
| trend_vol_qqq | +201.1% | +200.9% | −0.2 |
| vol_managed_qqq | +184.5% | +181.1% | −3.5 |
| pca_minvar_jse − raw | +79 bps | +72 bps | direction unchanged |

## Does anything flip?

- **Pass/fail sets: no change** on either bar (1y ≥ +18% and 5y CAGR ≥ 18% memberships
  identical).
- **Promoted live books: no change warranted.** Top of the excess ranking is unchanged
  (gem, momentum_concentrated lead; momentum_concentrated strengthens: +18.9% excess at
  0.83x gross, Sharpe 1.46). vol_managed_qqq's 1y excess drops 12.3→7.1% but its case was
  always the 82-window walk-forward (panel_2005, unaffected).
- **Two excess SIGN FLIPS, both on non-promoted specs.** deep_dip_reversion's blind-year
  excess goes −4.2% → +8.1% (the "reversion is dead money" 1y line is retracted); its
  retirement rests on the 5y result, which stands (+22.7% total over 5 years). vol_core_svxy
  −1.1% → +1.2% (cosmetic).
- **JSE matched pair: direction and magnitude story unchanged** (1y +15→+12 bps,
  5y +79→+72 bps; both books' totals drop ~2.4pp in parallel).
- **Factor-attribution program verdicts: unchanged** (audit quantified pre-emptively;
  the program's blind regressions end 2026-05-29/22 and barely touch the corrupt stretch).

## Rules note

Frozen results files remain as-run (write-once). Any future document citing a frozen
number for the 2026-05-25→2026-07-10 stretch must cite the corrected value from this memo.
The next full sandbox rebuild will produce clean panels by construction (builder guard).
