"""IC-first signal screen — rank IC of 10 fit-free signals on PIT S&P 500 members.

Methodology replicates robustness/ic.md (F-016): monthly (month-end trading days),
PIT members via panel field 'member' (ETFs/^VIX excluded), Spearman rank IC vs 21d
and 63d forward close-to-close returns, 2015->2026. Measurement only, no portfolios.
Run:  .venv/bin/python research/hunt2026/robustness/ic_screen.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tracks.statarb.residual import rolling_beta  # noqa: E402

HERE = Path(__file__).resolve().parent
HUNT = HERE.parent

SECTOR_ETF = {
    "Materials": "XLB", "Energy": "XLE", "Financials": "XLF", "Industrials": "XLI",
    "Information Technology": "XLK", "Consumer Staples": "XLP", "Utilities": "XLU",
    "Health Care": "XLV", "Consumer Discretionary": "XLY", "Real Estate": "XLRE",
    "Communication Services": "XLC",
}


def load():
    panel = pd.read_parquet(HUNT / "panel_2005.parquet")
    sectors = pd.read_parquet(HUNT / "sectors.parquet").set_index("ticker")["sector"]
    import json
    meta = json.loads((HUNT / "sandbox_meta.json").read_text())
    non_stock = set(meta["etfs"]) | set(meta["signal_only"])
    return panel, sectors, non_stock


def build_signals(panel, sectors, stocks):
    """Each signal: DataFrame (dates x stocks), value known at date t's close.
    Higher signal = predicted higher forward return (sign baked in)."""
    close = panel["close"][stocks]
    open_ = panel["open"][stocks]
    vol = panel["volume"][stocks]
    rets = close.pct_change(fill_method=None)

    # per-stock matched sector-ETF price/returns (aligned columns)
    etf_of = sectors.reindex(stocks).map(SECTOR_ETF)
    all_close = panel["close"]
    sec_close = pd.DataFrame(
        {t: all_close[e] if pd.notna(e) and e in all_close.columns else np.nan
         for t, e in etf_of.items()}, index=close.index)
    sec_rets = sec_close.pct_change(fill_method=None)

    sig = {}

    # 1. short-term reversal
    sig["st_reversal_21d"] = -(close / close.shift(21) - 1)

    # 2. sector-relative 12-1 momentum
    mom = close.shift(21) / close.shift(252) - 1
    sec_mom = sec_close.shift(21) / sec_close.shift(252) - 1
    sig["sector_rel_mom_12_1"] = mom - sec_mom

    # 3. residual momentum: 12-1 cumulative residual return vs sector ETF (60d beta, lagged)
    beta = rolling_beta(rets, sec_rets, 60).shift(1)
    resid = rets - beta * sec_rets
    sig["residual_mom_12_1"] = resid.rolling(231).sum().shift(21)

    # 4. idiosyncratic vol (60d residual vol), low-minus-high
    sig["ivol_60d_low"] = -resid.rolling(60).std()

    # 5. dispersion residual: deviation of 21d return from sector median, sign-flipped
    r21 = close / close.shift(21) - 1
    sec_of = sectors.reindex(stocks)
    sec_med = r21.T.groupby(sec_of).transform("median").T
    sig["dispersion_resid_21d"] = -(r21 - sec_med)

    # 6. volume shock
    sig["volume_shock"] = vol.rolling(21).mean() / vol.rolling(252).mean()

    # 7. overnight-vs-intraday share: 126d cum log overnight minus cum log intraday
    log_on = np.log(open_ / close.shift(1))
    log_intra = np.log(close / open_)
    sig["overnight_share_126d"] = (log_on - log_intra).rolling(126).sum()

    # 8. gap persistence: count of >2-sigma up-gaps held (close>=open), 63d
    gap = open_ / close.shift(1) - 1
    gap_sig = gap.rolling(252).std().shift(1)
    held = ((gap > 2 * gap_sig) & (close >= open_)).astype(float)
    sig["gap_persistence_63d"] = held.rolling(63).sum()

    # 9. low-vol (60d total vol, low-minus-high)
    sig["low_vol_60d"] = -rets.rolling(60).std()

    # 10. 52-week-high proximity
    sig["high_52w_prox"] = close / close.rolling(252).max()

    return sig


def rank_ic(sig_df, fwd, member, dates):
    """Spearman IC per date over PIT members with valid signal + forward return."""
    out = []
    for d in dates:
        m = member.loc[d] == 1
        s = sig_df.loc[d][m]
        f = fwd.loc[d][m]
        ok = s.notna() & f.notna()
        if ok.sum() < 50:
            out.append(np.nan)
            continue
        out.append(s[ok].rank().corr(f[ok].rank()))
    return pd.Series(out, index=dates)


def main():
    panel, sectors, non_stock = load()
    member = panel["member"]
    stocks = [t for t in member.columns if t not in non_stock]
    member = member[stocks]
    close = panel["close"][stocks]

    # monthly rebalance dates: last trading day of each month, 2015+, with 63d fwd available
    dates = pd.Series(close.index, index=close.index).resample("ME").last().dropna()
    dates = dates[(dates >= "2015-01-01")].tolist()
    n = {h: close.shift(-h) / close - 1 for h in (21, 63)}
    dates = [d for d in dates if n[63].loc[d].notna().sum() > 0]

    signals = build_signals(panel, sectors, stocks)

    rows, byyear, byhalf = {}, {}, {}
    ics21 = {}
    for name, s in signals.items():
        ic21 = rank_ic(s, n[21], member, dates).dropna()
        ic63 = rank_ic(s, n[63], member, dates).dropna()
        ics21[name] = ic21

        def stats(ic):
            t = ic.mean() / ic.std() * np.sqrt(len(ic))
            return ic.mean(), t, (ic > 0).mean(), len(ic)

        rows[name] = (*stats(ic21), *stats(ic63))
        byyear[name] = ic21.groupby(ic21.index.year).mean()
        half = pd.cut(ic21.index.year, [2014, 2019, 2024, 2026],
                      labels=["2015-19", "2020-24", "2025-26"])
        byhalf[name] = ic21.groupby(half, observed=True).mean()

    res = pd.DataFrame(rows, index=["ic21", "t21", "hit21", "n21",
                                    "ic63", "t63", "hit63", "n63"]).T
    pd.set_option("display.width", 200)
    print(res.round(4))
    print()
    print(pd.DataFrame(byhalf).T.round(4))
    print()
    print(pd.DataFrame(byyear).T.round(3))

    res.to_csv(HERE / "ic_screen_stats.csv")
    pd.DataFrame(byhalf).T.to_csv(HERE / "ic_screen_byhalf.csv")
    pd.DataFrame(byyear).T.to_csv(HERE / "ic_screen_byyear.csv")


if __name__ == "__main__":
    # self-check: replicating F-016 momentum IC must give ~-0.001 (t~-0.07)
    main()
