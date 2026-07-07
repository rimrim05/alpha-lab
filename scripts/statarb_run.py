"""StatArb Stage-1 run on free daily data (Gatev-Goetzmann-Rouwenhorst pairs).

Walk-forward: form pairs on a trailing formation window (min sum-squared distance),
trade the normalized-spread z-score over the next trading window, roll. Equal capital
per pair, costs charged on every position change. Net daily return -> shared scorecard.

Usage: .venv/bin/python scripts/statarb_run.py [--formation 252 --trading 126 --n-pairs 20]
Documented limitation: 60-name large-cap universe (survivorship-biased placeholder),
shared with the PEAD track. A real run needs a point-in-time universe (WRDS).
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.data.prices import daily_returns, fetch_prices_yf
from core.data.registry import register
from core.eval.scorecard import scorecard, to_markdown
from tracks.pead.universe import UNIVERSE
from tracks.statarb.bands import band_positions
from tracks.statarb.pairs import pair_pnl, pair_zscore_oos, select_pairs


def run_pairs(prices: pd.DataFrame, rets: pd.DataFrame, formation: int, trading: int,
             n_pairs: int, entry: float, exit_: float, cost_bps: float) -> pd.Series:
    dates = prices.index
    daily = pd.Series(0.0, index=dates)
    start = formation
    while start + 1 < len(dates):
        stop = min(start + trading, len(dates))
        form_win = prices.iloc[start - formation:start]
        trade_win = prices.iloc[start:stop]
        pairs = select_pairs(form_win, n_pairs=n_pairs)
        pair_rets = []
        for a, b in pairs:
            if a not in trade_win or b not in trade_win:
                continue
            # z-score standardized by FORMATION-window spread stats (no look-ahead)
            z = pair_zscore_oos(form_win[a], form_win[b], trade_win[a], trade_win[b])
            pos = band_positions(z, entry=entry, exit_=exit_)
            gross = pair_pnl(pos, rets[a].reindex(trade_win.index), rets[b].reindex(trade_win.index))
            turnover = pos.diff().abs().fillna(0)
            net = gross - turnover * cost_bps / 1e4 * 2  # two legs
            pair_rets.append(net)
        if pair_rets:
            daily.loc[trade_win.index] = pd.concat(pair_rets, axis=1).mean(axis=1).reindex(trade_win.index).fillna(0)
        start = stop
    return daily


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--formation", type=int, default=252)
    ap.add_argument("--trading", type=int, default=126)
    ap.add_argument("--n-pairs", type=int, default=20)
    ap.add_argument("--entry", type=float, default=2.0)
    ap.add_argument("--exit", type=float, default=0.5, dest="exit_")
    ap.add_argument("--cost-bps", type=float, default=5.0)
    ap.add_argument("--start", default="2018-01-01")
    args = ap.parse_args()

    out = Path("artifacts/statarb")
    out.mkdir(parents=True, exist_ok=True)
    prices = fetch_prices_yf(UNIVERSE, args.start, None)
    rets = daily_returns(prices)
    prices = prices.reindex(rets.index)

    daily = run_pairs(prices, rets, args.formation, args.trading, args.n_pairs,
                      args.entry, args.exit_, args.cost_bps).loc[rets.index].fillna(0)
    daily = daily[daily.ne(0).cumsum() > 0]  # drop leading formation-only zeros

    bench = {"equal_weight_universe": rets.mean(axis=1)}
    card = scorecard(daily, bench, n_trials=1, periods_per_year=252)
    (out / "scorecard.md").write_text(to_markdown(card, "StatArb pairs (GGR)"))
    daily.to_frame("net").to_parquet(out / "pairs_pnl.parquet")
    register(Path("data/manifest.jsonl"), name="statarb_pairs", source="yfinance",
             filters={"formation": args.formation, "trading": args.trading, "n_pairs": args.n_pairs},
             path=str(out / "pairs_pnl.parquet"), rows=int(daily.ne(0).sum()))
    print(to_markdown(card, "StatArb pairs (GGR)"))


if __name__ == "__main__":
    main()
