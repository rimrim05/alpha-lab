"""Deterministic, row-order-invariant smoke-manifest selection."""
import hashlib

import pandas as pd


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def select_smoke(news: pd.DataFrame, limit: int = 200, per_session: int = 10) -> pd.DataFrame:
    """Select several names on each of several sessions so quantiles are exercised."""
    if limit <= 0 or per_session < 5:
        raise ValueError("limit must be positive and per_session must be at least 5")
    required = {"published_at", "date", "ticker", "company", "headline"}
    missing = required - set(news.columns)
    if missing:
        raise ValueError(f"news missing columns: {sorted(missing)}")
    df = news.copy()
    df["_row_key"] = df.apply(
        lambda r: _hash("|".join(str(r[c]) for c in sorted(required))), axis=1)
    df = df.sort_values("_row_key").drop_duplicates(
        ["published_at", "ticker", "company", "headline"])
    eligible_dates = [d for d, g in df.groupby("date") if g["ticker"].nunique() >= per_session]
    eligible_dates = sorted(eligible_dates, key=_hash)
    need_dates = (limit + per_session - 1) // per_session
    chosen = []
    for date in eligible_dates[:need_dates]:
        g = df[df["date"] == date].drop_duplicates("ticker").head(per_session)
        chosen.append(g)
    out = pd.concat(chosen, ignore_index=True) if chosen else df.iloc[0:0].copy()
    if len(out) < limit:
        used = set(out["_row_key"])
        out = pd.concat([out, df[~df["_row_key"].isin(used)].head(limit - len(out))])
    return out.head(limit).drop(columns="_row_key").sort_values(
        ["date", "ticker", "headline"]).reset_index(drop=True)
