# EWMA vs realized vol — vol_managed_qqq matched pair (EXP-2026-07-14-ewma-vol)

Identical target/band/cap code path; only the vol estimator swapped. Matched pair (com=10) decides alone; com=5 and λ=0.94 are context. Prereg: preregistrations/ewma-vol-2026-07-14.md. Both gates passed (exact frozen-spec reproduction; holdout Sharpe == published).

Baseline (frozen realized-21): full-period net 1796pp, sharpe 1.05, maxDD -35.2%, turnover/d 0.0301.

| variant | med 12m Δ (bps) | win share | windows | full Δnet (pp) | Δsharpe | ΔmaxDD (pp) | Δturnover |
|---|---|---|---|---|---|---|---|
| com=10.00 **(matched pair)** | -63.6 | 35% | 46 | -342.9 | -0.054 | +0.6 | +0.0126 |
| com=5.00 | -74.3 | 43% | 46 | -282.1 | -0.054 | +0.9 | +0.0465 |
| com=15.67 | -138.6 | 28% | 46 | -482.1 | -0.082 | +0.7 | -0.0020 |

## Verdict (matched pair, pre-committed rule): **realized better**

## Regime windows (descriptive only)

| regime | matched-pair med Δ (bps) | windows |
|---|---|---|
| china_2015 | -68.1 | 7 |
| volmageddon_2018 | +258.7 | 7 |
| covid_2020 | -323.5 | 7 |
| inflation_bear_2022 | +44.1 | 8 |
| ai_rally_2023 | -209.9 | 8 |
| expansion_2024_26 | -231.5 | 10 |

## Story

- **The registered alternative world is the real one, decisively.** The prereg hypothesized the 21d rolling window's 'ghost vol' cliff (a spike pins leverage low for exactly 21 days, then exits the window abruptly) was a defect EWMA would fix. The data says the hard forget is a FEATURE: after a vol spike the rolling window fully releverages sooner, which pays in sharp recoveries: EWMA's exponential tail never quite forgets, suppressing leverage exactly when QQQ rips back (covid_2020 −323 bps, ai_rally_2023 −210, expansion_2024-26 −232). EWMA's only regime win is volmageddon_2018 (+259), where fast releveraging into a second spike was punished.
- **Not a memory-tuning artifact:** all three registered memories lose (−63.6 / −74.3 / −138.6 bps), and the industry-default λ=0.94 is the worst. The estimator SHAPE hurts on this book.
- **Turnover footnote:** matched-pair EWMA raised turnover 42% (smooth daily drift crosses the 0.05 tolerance band more often than the window's occasional cliffs) but that is only ~+6 bps/yr of cost; the loss is exposure timing, not cost.
- **Verdict: keep the frozen realized-21 estimator.** Queue item closed; estimator-shape retests on this book are answered (FAILURES.md F-024).
