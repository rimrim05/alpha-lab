"""Scored headlines -> daily per-ticker signal (mean of same-day scores)."""
import pandas as pd


def daily_signal(scored: pd.DataFrame) -> pd.DataFrame:
    if scored.empty:
        raise ValueError("no scored headlines")
    df = scored.copy()
    df["date"] = pd.to_datetime(df["date"])
    return df.pivot_table(index="date", columns="ticker", values="score", aggfunc="mean")
