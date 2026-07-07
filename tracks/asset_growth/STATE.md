# STATE — Asset-growth contrarian (Cooper-Gulen-Schill)

**Stage:** 1 (run on real data); result is a universe artifact, not a clean anomaly test
**Last session:** 2026-07-07

## Scope
From [[LIT — Does highest YoY growth predict returns]]: YoY total-asset growth is a
CONTRARIAN cross-sectional signal — low-asset-growth firms outperform high-growth (~20%/yr
spread, Cooper-Gulen-Schill 2008). This is the tradeable, free-data version of Kristen's
original "highest YoY growth" question (answer: highest growth predicts *negative* returns).

## Built
- `signal.py` — `asset_growth` (YoY Δ total assets), `growth_score` = −growth (low growth → long)
- `edgar.py` — SEC EDGAR companyfacts fetch for annual `Assets` (free, ~2007+, far more history than yfinance)
- `scripts/asset_growth_run.py` — score → 6-mo availability lag → monthly-held quantile L/S → scorecard
- Reuses the existing `core.backtest` quantile engine (cross-sectional, unlike StatArb). Tests 2/2 green.

## Result (2026-07-07, 60 large caps, EDGAR assets 2007+, monthly 2010–2026)
Net **Sharpe −0.78**, ann. −13.4%, **max DD −93%**, hit rate 40%. Deflated-Sharpe prob 0.08%.
Benchmark equal-weight = 1.35. Strategy strongly NEGATIVE both subperiods.

## The honest read — this is the WRONG universe, not a dead anomaly
The 60-name universe is survivorship-selected mega-caps. Over 2010–2026 the highest-asset-growth
names in that set are exactly the tech winners (NVDA, AAPL, MSFT, AMZN, TSLA) that also had the
highest *returns*. "Short the fast asset-growers" here = short the biggest winners of the decade
→ −93% path. Cooper-Gulen-Schill is a BROAD cross-section (thousands of names, effect strongest
in small caps); 60 mega-caps can't evaluate it fairly. So this run does **not** refute the anomaly
— it shows the anomaly's sign is wrong *within a basket of large-cap growth winners*, which is
almost tautological. It's a clean illustration of why universe choice dominates a cross-sectional test.

## Result — WIDE universe (2026-07-07)
S&P Composite 1500 via `core/data/universe.py` (503 large + 400 mid + 600 small); EDGAR assets
for 1495 names with data, ~1303 in the sort each month; monthly rebalance, 10bps.
**Net Sharpe −0.56, ann. −1.84%, max DD −33%, hit rate 44%.** Benchmark equal-weight 1.01.

Widening 60 mega-caps → 1495 broad names moved the strategy **−0.78 → −0.56**: the mega-cap
"short the decade's winners" artifact largely disappeared, leaving a weak *negative* — i.e. the
low-asset-growth premium is simply **absent in the 2010–2026 growth regime** on this data, not
violently inverted. Not the anomaly working; not the catastrophe either.

Data-quality note (caught + fixed this run): the raw wide run showed a −107% max DD — impossible
for a diversified book. Traced to **CHRD (Chord Energy) Nov-2020, a fake +30,991% monthly return**
(post-bankruptcy reverse split off a near-zero delisted-shell price in yfinance). Fixed by
winsorizing monthly returns to [−90%, +300%]. Free monthly price data has corporate-action landmines.

## Next
1. **Still current-membership → survivorship-biased.** A real verdict needs point-in-time membership
   (WRDS/CRSP). 2010–2026 is also a single growth-favoring regime vs the anomaly's 1968–2003 sample.
2. Neutralize size/sector before sorting (asset growth correlates with size) — feasible now with breadth.
3. Test the low-turnover annual-hold version net of Novy-Marx-Velikov costs explicitly.

## Verdict for HYP-006
**Still no premium, but no longer a universe artifact.** −0.56 on 1495 names says the contrarian
asset-growth signal didn't pay in this era/data — a weak, honest negative. A clean verdict on the
*anomaly* still needs point-in-time data + size neutralization. Kristen's Stage-4 call.
