# IC screen — 10 price/volume signals, monthly rank IC, PIT S&P 500 members (2015→2026)

Follow-up to the momentum-IC kill (F-016, `ic.md`). Same methodology, replicated exactly
before screening: 12-1 momentum through this code gives mean IC −0.0014, t −0.07, hit 50%,
n 135, identical by-year, so the pipeline matches `ic.md` to the fourth decimal.

Method: month-end trading days 2015-01→2026-03 (135 months; last month requires 63
trading days of forward data). Universe = PIT members via panel field `member`, ETFs and
^VIX excluded. Spearman rank IC of signal (computed through that close, fit-free windows,
nothing tuned) vs 21d and 63d forward close-to-close returns. t = mean/std·√n. Sector map
= `sectors.parquet` → SPDR sector ETF (XLRE from 2015-10, XLC from 2018-06; names in
those sectors drop out of sector-relative signals before the ETF exists).
Script: `robustness/ic_screen.py` (stats/by-year CSVs written next to it).

## Results

Sign convention: signal already oriented so IC > 0 = works as hypothesized
(reversal, low-vol, ivol, dispersion are pre-flipped).

| Signal | IC 21d | t 21d | hit 21d | IC 63d | t 63d | hit 63d | IC21 2015-19 | IC21 2020-24 | IC21 2025-26 |
|---|---|---|---|---|---|---|---|---|---|
| st_reversal_21d | +0.005 | 0.34 | 52% | +0.005 | 0.32 | 54% | +0.036 | −0.011 | −0.052 |
| sector_rel_mom_12_1 | +0.001 | 0.03 | 55% | +0.009 | 0.59 | 59% | −0.001 | +0.003 | −0.003 |
| residual_mom_12_1 | +0.004 | 0.27 | 53% | +0.017 | 1.22 | 61% | −0.001 | +0.010 | −0.002 |
| ivol_60d_low | +0.002 | 0.16 | 50% | +0.005 | 0.31 | 56% | +0.003 | +0.006 | −0.015 |
| dispersion_resid_21d | −0.001 | −0.09 | 49% | −0.006 | −0.61 | 48% | +0.013 | −0.005 | −0.044 |
| volume_shock | +0.001 | 0.13 | 51% | −0.003 | −0.43 | 46% | +0.006 | −0.007 | +0.010 |
| overnight_share_126d | −0.002 | −0.21 | 53% | −0.006 | −0.48 | 45% | +0.005 | −0.005 | −0.020 |
| gap_persistence_63d | +0.002 | 0.25 | 54% | +0.003 | 0.52 | 55% | +0.001 | −0.004 | +0.031 |
| low_vol_60d | −0.006 | −0.29 | 50% | −0.010 | −0.50 | 53% | +0.007 | −0.004 | −0.067 |
| high_52w_prox | −0.000 | −0.02 | 54% | +0.006 | 0.32 | 57% | −0.009 | +0.010 | −0.009 |

n = 135 months everywhere except residual_mom_12_1 (133; longest lookback chain).

## Verdict

**No candidates. Nothing reaches |t| ≥ 2 at either horizon.** The best of ten,
residual momentum at 63d (t = 1.22, hit 61%), is exactly what one draw from ten noise
signals looks like after selection, and its by-year IC track is ~0.97-correlated with
plain 12-1 momentum's (same 2016 blowup, same 2026 pop), so it is F-016's corpse with a
sector hedge, not new information.

Reading by family:

- **Momentum family (2, 3, 10):** sector-hedging or residualizing 12-1 momentum does not
  resurrect it. The by-year pattern is the raw momentum pattern at slightly lower
  amplitude. 52-week-high proximity is the same signal again (rank corr with momentum is
  high by construction).
- **Vol family (4, 9):** low-vol and low-ivol have zero mean IC and were badly negative
  in 2025 (−0.05 to −0.10). No defensive ranking power in this universe/era.
- **Reversal family (1, 5):** short-term reversal had mild positive IC 2015-19 (+0.036)
  and has been *negative* since 2020, consistent with the known post-2015 decay of STR
  in large caps. Dispersion-residual is the same story, noisier.
- **Microstructure family (6, 7, 8):** volume shock, overnight share, gap persistence,
  flat everywhere, |t| ≤ 0.52. Nothing.

Half-decade columns show the deeper problem: no signal has a stable sign across
2015-19 / 2020-24 / 2025-26. This is not "weak alpha," it is regime-flipping noise.

**Conclusion: daily open/close/volume on S&P 500 large caps post-2015 contains no
monthly-horizon cross-sectional ranking signal detectable at this sample size.** The
cross-sectional stock-selection track in this data sandbox is closed pending a new
information source (fundamentals, earnings dates, flows, small caps) or an interaction
hypothesis with a mechanism. Do not build portfolios on any row of this table.

Hypothesis-level failure entries added: F-017 (reversal family), F-018 (vol family),
F-019 (microstructure family), F-016 addendum (momentum variants) in `FAILURES.md`.
