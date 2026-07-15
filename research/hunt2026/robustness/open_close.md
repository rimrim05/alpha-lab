# Open+close execution — overnight premium at frozen costs (EXP-2026-07-14-open-close)

Leg-compounded open/close engine, frozen 2 bps/side, full panel 2005-01-04 → 2026-07-10. Both gates passed (harness nesting < 1e-12; per-day leg composition < 1e-12). Prereg: preregistrations/open-close-2026-07-14.md.

## SPY

| book | gross total | gross CAGR | net total | net CAGR | net sharpe | net maxDD |
|---|---|---|---|---|---|---|
| overnight | +439% | +8.16% | -38% | -2.22% | -0.14 | -55.9% |
| intraday | +73% | +2.58% | -80% | -7.26% | -0.44 | -81.7% |
| buy_hold | +830% | +10.94% | +830% | +10.94% | 0.64 | -55.2% |

Overnight gross CAGR share of buy-and-hold: **75%** · approx break-even per-side cost: **-0.6 bps** (frozen model: 2.0 bps).

## QQQ

| book | gross total | gross CAGR | net total | net CAGR | net sharpe | net maxDD |
|---|---|---|---|---|---|---|
| overnight | +948% | +11.56% | +20% | +0.87% | 0.13 | -35.3% |
| intraday | +106% | +3.42% | -76% | -6.50% | -0.29 | -78.5% |
| buy_hold | +2058% | +15.38% | +2058% | +15.38% | 0.77 | -53.4% |

Overnight gross CAGR share of buy-and-hold: **75%** · approx break-even per-side cost: **-0.8 bps** (frozen model: 2.0 bps).

## Verdict (pre-committed rule): **premium real, NOT EXPLOITABLE at frozen costs**

Per the prereg kill condition: one run of the six registered books; the frozen cost model is the cost model; the stock cross-section tilt stays closed by arithmetic (10 bps/side × 2/day ≈ 50%/yr). The open+close engine remains a research tool; harness.py keeps the close-to-close convention.

## Story

- **The premium is real and matches F-006:** overnight carries 75% of both ETFs' gross CAGR over 2005–2026 (F-006 measured ~69% on the stock panel). The reopen-by-design promise is honored — the convention constraint is gone, the effect is measured under real open+close execution.
- **The surprise: costs turned out to be moot.** The pre-registered arithmetic framed this as premium (~9%/yr) vs costs (~10%/yr). The measured break-even per-side cost is NEGATIVE (−0.6 / −0.8 bps): even free execution loses to buy-and-hold, because overnight-only still forgoes the intraday leg's +2.6–3.4%/yr gross. 'Most of the return happens overnight' is true; 'all of it' — the version the trade needs — is false. 75% of the return with ~100% of the drawdown (SPY overnight maxDD −55.9% vs buy-hold −55.2%) is strictly worse, before a single basis point of cost.
- **Intraday-only is the weak leg confirmed:** +2.6–3.4%/yr gross, annihilated net (−6.5 to −7.3%/yr). Descriptive only.
- **F-006 closes finally (F-025):** not exploitable under the daily convention (F-006), and now not exploitable under the convention built for it either. Any future reopen needs an instrument that avoids both legs' round-trip — e.g. futures basis — not a cheaper cost assumption.
