"""StatArb residual mean-reversion (Avellaneda & Lee 2010, ETF variant), wide universe.

For each stock: rolling single-factor regression on its SECTOR ETF (betas lagged, no
look-ahead) -> idiosyncratic residual -> s-score of the cumulative residual. Trade the
mean-reversion: long when s <= -1.25 (residual cheap), short when s >= +1.25, flat inside
+/-0.5. Dollar-neutral, equal-weight across active names, net of costs -> shared scorecard.

Reuses the daily prices cached by scripts/statarb_run.py --universe wide.
Usage: .venv/bin/python scripts/statarb_residual_run.py [--window 60 --entry 1.25 --exit 0.5]
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.data.prices import daily_returns, fetch_prices_yf
from core.data.registry import register
from core.data.universe import (fetch_sp_composite, fetch_sp500_pit_changes,
                                 membership_mask, ever_members)
from core.eval.scorecard import scorecard, to_markdown
from tracks.statarb.bands import band_positions
from tracks.statarb.residual import rolling_residual

SECTOR_ETF = {
    "Information Technology": "XLK", "Financials": "XLF", "Health Care": "XLV",
    "Consumer Discretionary": "XLY", "Consumer Staples": "XLP", "Energy": "XLE",
    "Industrials": "XLI", "Materials": "XLB", "Utilities": "XLU",
    "Real Estate": "XLRE", "Communication Services": "XLC",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", type=int, default=60)
    ap.add_argument("--entry", type=float, default=1.25)
    ap.add_argument("--exit", type=float, default=0.5, dest="exit_")
    ap.add_argument("--cost-bps", type=float, default=5.0)
    ap.add_argument("--n-trials", type=int, default=20,
                    help="declared # of strategy variants tried, for the deflated-Sharpe haircut")
    ap.add_argument("--skip", type=int, default=1,
                    help="days between signal close and execution — defends against "
                         "bid-ask bounce / same-close reversal (0 reproduces the naive run)")
    ap.add_argument("--cap", choices=["all", "large", "small"], default="all",
                    help="large = S&P 500 only, small = S&P 600 only")
    ap.add_argument("--start", default="2018-01-01")
    ap.add_argument("--pit", action="store_true",
                    help="point-in-time S&P 500: trade each name only on its actual index-"
                         "membership days (removes inclusion look-ahead). Universe = names "
                         "EVER in the S&P 500; forces --cap large semantics. NOTE: cannot fix "
                         "delisting survivorship (dead names have no free price data) — the "
                         "resulting Sharpe is an UPPER BOUND on the true point-in-time Sharpe.")
    args = ap.parse_args()

    out = Path("artifacts/statarb")
    out.mkdir(parents=True, exist_ok=True)

    comp = fetch_sp_composite(cache=Path("data/raw/sp_composite.parquet"))
    pit_changes = None
    if args.pit:
        pit_changes = fetch_sp500_pit_changes(cache=Path("data/raw/sp500_pit_changes.parquet"))
        keep_set = ever_members(pit_changes)          # every ticker ever in the S&P 500
        sector = dict(zip(comp["ticker"], comp["sector"]))  # sectors from full composite
    else:
        keep = {"large": ["500"], "small": ["600"], "all": ["500", "600"]}[args.cap]
        comp = comp[comp["index"].isin(keep)]
        sector = dict(zip(comp["ticker"], comp["sector"]))
        keep_set = set(comp["ticker"])

    px_cache = Path("data/raw/daily_px_statarb_wide.parquet")
    prices = pd.read_parquet(px_cache) if px_cache.exists() else fetch_prices_yf(
        sorted(keep_set), args.start, None)
    prices = prices[[c for c in prices.columns if c in keep_set]]
    # winsorize daily returns against bad ticks / halts (a delisted small-cap's price
    # glitch can fake a huge residual + a fake reversion profit). Real daily moves rarely
    # exceed -50% / +100%.
    rets = daily_returns(prices).clip(lower=-0.5, upper=1.0)

    etf_px = fetch_prices_yf(["SPY"] + sorted(set(SECTOR_ETF.values())), args.start, None)
    etf_ret = daily_returns(etf_px).reindex(rets.index)

    # each stock's factor = its sector ETF return (fallback SPY where sector/ETF missing)
    factor = {}
    for t in rets.columns:
        etf = SECTOR_ETF.get(sector.get(t, ""), "SPY")
        s = etf_ret[etf] if etf in etf_ret else etf_ret["SPY"]
        factor[t] = s.fillna(etf_ret["SPY"])
    factors = pd.DataFrame(factor).reindex(rets.index)

    resid = rolling_residual(rets, factors, window=args.window)
    # s-score = standardized cumulative residual (same logic as residual.s_score, vectorized)
    cum = resid.cumsum()
    s = (cum - cum.rolling(args.window).mean()) / cum.rolling(args.window).std()

    positions = s.apply(lambda col: band_positions(col, entry=args.entry, exit_=args.exit_))
    if args.pit:
        # gate trading to actual index-membership days: a name is forced flat when it was
        # not in the S&P 500 (turnover on entry/exit is charged realistically via .diff()).
        mask = membership_mask(pit_changes, positions.index, positions.columns)
        positions = positions.where(mask, 0)
    # execute `skip` days after the signal close (skip>=1 breaks the bid-ask-bounce channel:
    # you can't both measure the signal on and trade at the same close)
    held = positions.shift(1 + args.skip)
    active = held.abs()
    n_active = active.sum(axis=1).replace(0, pd.NA)
    gross = (held * resid).sum(axis=1) / n_active
    turnover = positions.diff().abs()
    cost = (turnover * args.cost_bps / 1e4 * 2).sum(axis=1) / n_active  # stock + ETF leg
    net = (gross - cost).fillna(0)
    net = net[net.ne(0).cumsum() > 0]  # drop leading warm-up

    med_active = int(active.sum(axis=1).replace(0, pd.NA).dropna().median())
    tag = "point-in-time membership" if args.pit else f"{args.cap} cap"
    title = (f"StatArb residual reversion (Avellaneda-Lee) — {tag}, {rets.shape[1]} names, "
             f"~{med_active} pos/day, skip={args.skip}, {args.cost_bps}bps")
    bench = {"equal_weight_universe": rets.mean(axis=1)}
    card = scorecard(net, bench, n_trials=args.n_trials, periods_per_year=252)
    stem = "residual_pit" if args.pit else "residual"
    (out / f"{stem}_scorecard.md").write_text(to_markdown(card, title))
    net.to_frame("net").to_parquet(out / f"{stem}_pnl.parquet")
    register(Path("data/manifest.jsonl"), name="statarb_" + stem, source="yfinance",
             filters={"window": args.window, "entry": args.entry, "names": int(rets.shape[1]),
                      "pit": bool(args.pit)},
             path=str(out / f"{stem}_pnl.parquet"), rows=int(net.ne(0).sum()))
    print(to_markdown(card, title))


if __name__ == "__main__":
    main()
