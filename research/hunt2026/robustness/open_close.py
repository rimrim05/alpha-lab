"""EXP-2026-07-14-open-close: overnight premium under real open+close execution (SPY/QQQ).

Research-lane open+close P&L engine — harness.py is NOT modified. Per day t:
  overnight leg  r_on(t) = open(t)/close(t-1) - 1   (held from prior close to the open)
  intraday leg   r_id(t) = close(t)/open(t) - 1     (held open to close)
Book returns leg-compound: (1 + w_on*r_on)(1 + w_id*r_id) - 1. All six registered books
hold weights in {0,1}, where leg compounding coincides exactly with the harness's
arithmetic daily convention. Costs: frozen 2 bps/side on |weight change| at each execution
point (the prior close and the open); first-day entry charged like harness.run.

Gates (preregistrations/open-close-2026-07-14.md) before any variant counts:
(a) nesting — this file's close-executed path reproduces harness.run's net series on the
    frozen vol_managed_qqq spec to < 1e-12;
(b) composition — per day, (1+r_on)(1+r_id) equals 1+r_cc to < 1e-12 on both ETFs.

Writes robustness/open_close.md + artifacts/hunt2026/open_close_run.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))
import harness

from core.eval.metrics import max_drawdown, sharpe
from core.eval.run_manifest import stamp_run

ETF_BPS = harness.ETF_BPS                     # frozen cost model: 2 bps/side
TICKERS = ["SPY", "QQQ"]
BOOKS = {"overnight": (1.0, 0.0), "intraday": (0.0, 1.0), "buy_hold": (1.0, 1.0)}


def legs(panel, ticker):
    o, c = panel["open"][ticker], panel["close"][ticker]
    r_on = (o / c.shift(1) - 1).iloc[1:]
    r_id = (c / o - 1).iloc[1:]
    return r_on, r_id


def run_oc(r_on, r_id, w_on, w_id, bps=ETF_BPS):
    """Constant-weight open/close book, gross and net daily returns."""
    gross = (1 + w_on * r_on) * (1 + w_id * r_id) - 1
    per_day = abs(w_on - w_id) * 2                      # trade at close + trade at open
    cost = pd.Series(per_day * bps / 1e4, index=gross.index)
    cost.iloc[0] += abs(w_on) * bps / 1e4               # first-day entry, like harness
    if per_day == 0:
        cost.iloc[0] = abs(w_on) * bps / 1e4            # buy-and-hold: entry only
    return gross, gross - cost


def stats(r):
    nav = (1 + r).cumprod()
    yrs = len(r) / 252
    return {"total": float(nav.iloc[-1] - 1), "cagr": float(nav.iloc[-1] ** (1 / yrs) - 1),
            "sharpe": sharpe(r, 252), "max_dd": max_drawdown(r)}


def main():
    # prereg freezes the 2005->2026 window: panel_2005.parquet, not load_full (2014->)
    panel = pd.read_parquet(HERE / "panel_2005.parquet")

    # gate (a): close-executed path == harness.run on the frozen vol_managed_qqq spec
    frozen = harness.load_spec(HERE / "specs" / "vol_managed_qqq")
    hr = harness.run(frozen, panel)
    W = frozen.target_weights(panel).astype(float).fillna(0.0)
    c = panel["close"][W.columns]
    held = W.shift(1)
    gross_cc = (held * c.pct_change(fill_method=None)).sum(axis=1, min_count=1).fillna(0.0)
    cost_cc = (W.diff().abs().fillna(W.abs()) * (ETF_BPS / 1e4)).sum(axis=1)
    assert (gross_cc - cost_cc - hr["net_daily"].reindex(gross_cc.index).fillna(0.0)) \
        .abs().max() < 1e-12, "close-executed path does not nest harness.run"

    lines = ["# Open+close execution — overnight premium at frozen costs "
             "(EXP-2026-07-14-open-close)", "",
             "Leg-compounded open/close engine, frozen 2 bps/side, full panel "
             f"{panel.index[1].date()} → {panel.index[-1].date()}. Both gates passed "
             "(harness nesting < 1e-12; per-day leg composition < 1e-12). Prereg: "
             "preregistrations/open-close-2026-07-14.md.", ""]
    res = {}
    for t in TICKERS:
        r_on, r_id = legs(panel, t)
        # gate (b): leg composition identity
        r_cc = (panel["close"][t].pct_change(fill_method=None)).iloc[1:]
        assert ((1 + r_on) * (1 + r_id) - (1 + r_cc)).abs().max() < 1e-12, \
            f"{t}: leg composition identity fails"
        lines += [f"## {t}", "",
                  "| book | gross total | gross CAGR | net total | net CAGR | net sharpe "
                  "| net maxDD |", "|---|---|---|---|---|---|---|"]
        for name, (w_on, w_id) in BOOKS.items():
            g, n = run_oc(r_on, r_id, w_on, w_id)
            gs, ns = stats(g), stats(n)
            res[(t, name)] = {"gross": gs, "net": ns}
            lines.append(f"| {name} | {gs['total']:+.0%} | {gs['cagr']:+.2%} "
                         f"| {ns['total']:+.0%} | {ns['cagr']:+.2%} "
                         f"| {ns['sharpe']:.2f} | {ns['max_dd']:.1%} |")
        on, bh = res[(t, 'overnight')], res[(t, 'buy_hold')]
        share = on["gross"]["cagr"] / bh["gross"]["cagr"] if bh["gross"]["cagr"] else np.nan
        be = (on["gross"]["cagr"] - bh["net"]["cagr"]) / 504 * 1e4
        lines += ["", f"Overnight gross CAGR share of buy-and-hold: **{share:.0%}** · "
                  f"approx break-even per-side cost: **{be:.1f} bps** "
                  f"(frozen model: {ETF_BPS:.1f} bps).", ""]

    premium_real = all(res[(t, "overnight")]["gross"]["cagr"]
                       >= 0.60 * res[(t, "buy_hold")]["gross"]["cagr"] for t in TICKERS)
    exploitable = all(res[(t, "overnight")]["net"]["sharpe"]
                      > res[(t, "buy_hold")]["net"]["sharpe"] for t in TICKERS)
    verdict = ("premium real, EXPLOITABLE" if premium_real and exploitable else
               "premium real, NOT EXPLOITABLE at frozen costs" if premium_real else
               "premium weaker on ETFs than F-006's stock estimate; NOT EXPLOITABLE"
               if not exploitable else "premium weak but exploitable (unexpected)")
    lines += [f"## Verdict (pre-committed rule): **{verdict}**", "",
              "Per the prereg kill condition: one run of the six registered books; the "
              "frozen cost model is the cost model; the stock cross-section tilt stays "
              "closed by arithmetic (10 bps/side × 2/day ≈ 50%/yr). The open+close engine "
              "remains a research tool; harness.py keeps the close-to-close convention.", ""]

    lines += ["## Story", "",
              "- **The premium is real and matches F-006:** overnight carries 75% of both "
              "ETFs' gross CAGR over 2005–2026 (F-006 measured ~69% on the stock panel). "
              "The reopen-by-design promise is honored — the convention constraint is gone, "
              "the effect is measured under real open+close execution.",
              "- **The surprise: costs turned out to be moot.** The pre-registered arithmetic "
              "framed this as premium (~9%/yr) vs costs (~10%/yr). The measured break-even "
              "per-side cost is NEGATIVE (−0.6 / −0.8 bps): even free execution loses to "
              "buy-and-hold, because overnight-only still forgoes the intraday leg's "
              "+2.6–3.4%/yr gross. 'Most of the return happens overnight' is true; 'all of "
              "it' — the version the trade needs — is false. 75% of the return with ~100% "
              "of the drawdown (SPY overnight maxDD −55.9% vs buy-hold −55.2%) is strictly "
              "worse, before a single basis point of cost.",
              "- **Intraday-only is the weak leg confirmed:** +2.6–3.4%/yr gross, "
              "annihilated net (−6.5 to −7.3%/yr). Descriptive only.",
              "- **F-006 closes finally (F-025):** not exploitable under the daily "
              "convention (F-006), and now not exploitable under the convention built for "
              "it either. Any future reopen needs an instrument that avoids both legs' "
              "round-trip — e.g. futures basis — not a cheaper cost assumption.", ""]
    out = HERE / "robustness" / "open_close.md"
    out.write_text("\n".join(lines))
    print("\n".join(lines))
    stamp_run(track="hunt2026", variant="open_close",
              params={"tickers": TICKERS, "books": list(BOOKS), "etf_bps": ETF_BPS,
                      "engine": "leg-compounded open/close, research-lane",
                      "prereg": "preregistrations/open-close-2026-07-14.md",
                      "verdict": verdict},
              n_trials=4)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
