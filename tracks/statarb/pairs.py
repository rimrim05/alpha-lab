"""Distance-based pairs trading (Gatev, Goetzmann & Rouwenhorst 2006).

Form pairs by minimum sum-of-squared-deviation between normalized price paths in
a formation window; trade divergences of the normalized spread in the next window.
Runs on daily EOD closes — the most free-data-replicable StatArb strategy.
"""
import pandas as pd
from tracks.statarb.bands import band_positions


def normalize_prices(prices: pd.DataFrame) -> pd.DataFrame:
    """Normalize each price series to start at 1 (a cumulative-return index)."""
    first = prices.ffill().bfill().iloc[0]
    return prices.divide(first, axis=1)


def select_pairs(prices: pd.DataFrame, n_pairs: int = 20) -> list[tuple[str, str]]:
    """Pick the n_pairs tickers with the smallest sum-of-squared normalized-price gap."""
    norm = normalize_prices(prices.dropna(axis=1, how="any"))
    cols = list(norm.columns)
    dists = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            ssd = float(((norm[cols[i]] - norm[cols[j]]) ** 2).sum())
            dists.append((ssd, cols[i], cols[j]))
    dists.sort(key=lambda t: t[0])
    return [(a, b) for _, a, b in dists[:n_pairs]]


def spread_zscore(a: pd.Series, b: pd.Series, window: int | None = None) -> pd.Series:
    """Z-score of the normalized-price spread between two series."""
    pair = pd.concat([a, b], axis=1).dropna()
    norm = normalize_prices(pair)
    spread = norm.iloc[:, 0] - norm.iloc[:, 1]
    if window:
        mu = spread.rolling(window).mean()
        sd = spread.rolling(window).std()
    else:
        mu, sd = spread.mean(), spread.std()
    return (spread - mu) / sd.replace(0, pd.NA)


def pair_pnl(positions: pd.Series, ret_a: pd.Series, ret_b: pd.Series) -> pd.Series:
    """Daily P&L of a pair. position +1 = long A / short B. Position lagged one day
    (formed on yesterday's close, earns today's spread return) — no look-ahead."""
    df = pd.concat([positions.rename("pos"), ret_a.rename("a"), ret_b.rename("b")], axis=1).dropna()
    held = df["pos"].shift(1).fillna(0)
    return held * (df["a"] - df["b"])
