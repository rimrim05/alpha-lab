# Robustness — dual_momentum_gold third-menu-slot (EXP-2026-07-10-defensive-asset)

Pre-registered: preregistrations/defensive-asset-2026-07-10.md. Frozen framework
(252d lookback, 1.5x winner-take-all risk leg, BIL gate, momentum-picked TLT/BIL
defensive leg at 1.0x), ONLY the third risk-menu asset varies. panel_2005.parquet,
rolling 12m windows / quarterly steps; 70 common windows
(2009-01-02 to 2026-04-16; BIL data start 2007-05 binds all variants).
All 10 registered variants reported, nothing dropped.

## Verdict: **REGIME ARTIFACT**

## Variant table (common windows)

| third asset | median 12m | >=18% | >0 | worst | med excess vs SPY | third picked (% month-ends) | (% of risk-on picks) |
|---|---|---|---|---|---|---|---|
| NONE | +26.6% | 56% | 84% | -16.3% | +11.3% | 0% | 0% |
| UUP | +24.9% | 53% | 74% | -27.3% | +10.9% | 15% | 16% |
| DBC | +26.6% | 57% | 77% | -58.7% | +8.5% | 18% | 20% |
| GLD | +17.7% | 50% | 71% | -25.7% | +6.9% | 31% | 34% |
| XLP | +15.7% | 43% | 83% | -17.2% | +4.9% | 21% | 23% |
| VNQ | +16.6% | 46% | 77% | -25.7% | +4.6% | 28% | 32% |
| EQW | +14.5% | 44% | 74% | -25.3% | +2.8% | 20% | 21% |
| TLT | +14.8% | 43% | 76% | -26.7% | +1.3% | 24% | 26% |
| SLV | +14.4% | 47% | 67% | -47.0% | +0.7% | 31% | 35% |
| XLU | +10.5% | 40% | 73% | -20.2% | -0.6% | 27% | 29% |

## Marginal contribution of the slot

12m windows split by whether the third asset was actually held at any month-end
inside the window.

| third asset | n windows w/ 3rd held | win rate | median 12m | n without | win rate | median 12m |
|---|---|---|---|---|---|---|
| GLD | 47 | 60% | +4.6% | 23 | 96% | +31.0% |
| TLT | 41 | 71% | +7.8% | 29 | 83% | +31.3% |
| DBC | 31 | 68% | +25.4% | 39 | 85% | +26.8% |
| XLU | 52 | 67% | +6.4% | 18 | 89% | +38.2% |
| XLP | 46 | 78% | +8.3% | 24 | 92% | +36.3% |
| UUP | 28 | 36% | -3.9% | 42 | 100% | +34.0% |
| SLV | 48 | 62% | +11.4% | 22 | 77% | +20.6% |
| VNQ | 48 | 73% | +13.4% | 22 | 86% | +33.2% |
| EQW | 38 | 66% | +8.5% | 32 | 84% | +29.0% |

## Per-regime medians (12m windows ending in regime)

| variant | GFC | euro_2011 | china_2015 | volmageddon_2018 | covid_2020 | inflation_bear_2022 | ai_rally_2023 | expansion_2024_26 |
|---|---|---|---|---|---|---|---|---|
| GLD | -5.9% | +29.7% | +12.9% | +35.2% | +18.8% | -3.4% | -11.9% | +61.2% |
| TLT | +39.1% | +22.2% | +0.4% | +35.2% | +20.4% | +1.5% | +0.9% | +34.2% |
| DBC | -42.1% | +21.2% | +12.9% | +31.0% | +51.5% | +48.0% | -2.8% | +34.2% |
| XLU | -5.1% | +23.3% | -6.6% | +35.2% | +48.9% | +17.8% | +0.4% | +29.5% |
| XLP | +2.1% | +27.3% | +12.1% | +35.2% | +56.2% | +8.3% | -5.5% | +30.5% |
| UUP | -19.1% | +33.9% | +4.2% | +35.2% | +40.3% | +6.3% | -6.7% | +34.2% |
| SLV | -31.9% | +106.5% | +12.9% | +35.2% | +19.3% | -0.1% | -20.9% | +33.2% |
| VNQ | +4.7% | +37.0% | +7.6% | +35.2% | +47.1% | -7.5% | -5.2% | +30.5% |
| NONE | +4.7% | +33.9% | +12.9% | +35.2% | +51.5% | +1.5% | +0.9% | +34.2% |
| EQW | +14.2% | +24.5% | +12.9% | +35.2% | +22.3% | +1.5% | +0.9% | +30.5% |

## Decisive statistic (pre-registered): GLD variant vs NONE ({SPY,QQQ}) per window

| slice | n windows | GLD wins | median delta (GLD - NONE) |
|---|---|---|---|
| all | 70 | 21% | +0.00% |
| window ends < 2024-01-01 | 60 | 13% | -0.61% |
| window ends >= 2024-01-01 | 10 | 70% | +18.62% |

Pre-registered rule: regime artifact if pre-2024 win share <= 52% OR pre-2024
median delta <= +0.5%; structural if >= 55% AND >= +1.5%; else indeterminate.

## Pre/post-2024 median 12m per variant

| variant | median 12m, windows ending < 2024 | ending >= 2024 |
|---|---|---|
| DBC | +20.7% | +34.2% |
| NONE | +20.5% | +34.2% |
| UUP | +16.7% | +34.2% |
| VNQ | +15.7% | +30.5% |
| EQW | +13.8% | +30.5% |
| GLD | +13.0% | +61.2% |
| XLP | +12.9% | +30.5% |
| SLV | +12.9% | +33.2% |
| TLT | +11.2% | +34.2% |
| XLU | +8.9% | +29.5% |

## GLD - NONE delta by window-end year (median)

| year | median delta | n |
|---|---|---|
| 2009 | -10.59% | 4 |
| 2010 | +21.37% | 4 |
| 2011 | -21.16% | 4 |
| 2012 | -18.71% | 4 |
| 2013 | +0.00% | 4 |
| 2014 | +0.00% | 4 |
| 2015 | +0.00% | 4 |
| 2016 | -0.61% | 4 |
| 2017 | -34.39% | 4 |
| 2018 | +0.00% | 4 |
| 2019 | +0.00% | 4 |
| 2020 | -21.30% | 4 |
| 2021 | -15.72% | 4 |
| 2022 | -3.85% | 4 |
| 2023 | -10.88% | 4 |
| 2024 | -1.81% | 4 |
| 2025 | +62.43% | 4 |
| 2026 | +50.53% | 2 |

## Interpretation

- Fidelity check: the GLD variant reproduces the official frozen-spec walk-forward
  exactly (walkforward/dual_momentum_gold.json: 70w, median +17.7%, >=18% 50%,
  excess +6.9%, worst -25.7%). The comparison is apples-to-apples.
- The pre-registered hypothesis (regime artifact) is CONFIRMED, and more strongly than
  expected: GLD beats the two-asset {SPY,QQQ} menu in only 21% of all windows and 13%
  of pre-2024 windows (pre-2024 median delta -0.61%). The entire GLD edge sits in the
  10 windows ending 2024-2026 (70% wins, median delta +18.6%; by-year table: the only
  big positive years are 2025 +62% and 2026 +51%, plus one +21% blip in 2010).
- Stronger than "gold won recently": for ~15 years the third slot was a net DRAG under
  this framework, whatever filled it. NONE has the best median excess vs SPY (+11.3%)
  of all ten variants; every third asset except UUP/DBC lowers it, and those two only
  match NONE because they are rarely picked (16-20% of risk-on picks) - DBC also brings
  a -58.7% worst window (GFC). Windows where GLD was actually held: 60% positive,
  median +4.6%; windows where it wasn't: 96% positive, median +31.0%. (Not causal -
  third assets get picked when equities are weak - but the same split holds for every
  candidate, so the slot is not buying crisis protection either: the defensive TLT/BIL
  leg already does that job in the NONE variant.)
- Caveat: adjacent 12m windows overlap (63d step) -> roughly 4x fewer independent
  draws; 13% vs a 50% null is still decisive.

## Stage-4 flag (no action taken)

This experiment recommends AGAINST trusting the GLD slot, and mechanically the NONE
variant dominates historically - but the LIVE dual_momentum_gold book stays exactly as
frozen. Changing the menu mid-forward-test invalidates the forward test, and per the
pre-registered kill rule, picking a replacement third asset from this table would
itself be hindsight. Decision for Kristen at Stage 4: keep dual_momentum_gold's
"survivor (discounted)" status with this evidence attached, or retire the gold slot at
the next legitimate re-freeze point.
