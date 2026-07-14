"""Alpaca (Benzinga) historical news -> the source-agnostic news schema
(date, ticker, company, headline). Network fetch lives here, called only from scripts/.

Free with any Alpaca account (paper included); history reaches back to ~2015.
Auth: APCA-API-KEY-ID / APCA-API-SECRET-KEY env vars (same keys as the paper broker).
"""
import os
import time

import pandas as pd
import requests

NEWS_URL = "https://data.alpaca.markets/v1beta1/news"
PAGE_LIMIT = 50          # API max per page
SYMBOL_CHUNK = 50        # symbols per request; keeps URLs sane on wide universes
REQUEST_PAUSE = 0.35     # seconds between requests — stays under the 200/min limit


def news_to_frame(items: list[dict], names: dict[str, str] | None = None) -> pd.DataFrame:
    """Flatten raw Alpaca news items to one row per (headline, symbol).

    `published_at` preserves the provider's UTC instant. `date` remains the US/Eastern
    calendar date for display only; evaluation must use `published_at` to prevent
    after-close/weekend headlines from trading early.
    """
    names = names or {}
    rows = []
    for it in items:
        published = pd.Timestamp(it["created_at"])
        if published.tzinfo is None:
            published = published.tz_localize("UTC")
        published = published.tz_convert("UTC")
        date = str(published.tz_convert("America/New_York").date())
        for sym in it.get("symbols", []):
            rows.append({"published_at": published.isoformat(), "date": date, "ticker": sym,
                         "company": names.get(sym, sym), "headline": it["headline"]})
    cols = ["published_at", "date", "ticker", "company", "headline"]
    df = pd.DataFrame(rows, columns=cols)
    if df.empty:
        return df
    return (df.sort_values("published_at")
              .drop_duplicates(["date", "ticker", "headline"], keep="first")
              .reset_index(drop=True))


def fetch_news_alpaca(symbols: list[str], start: str, end: str | None,
                      names: dict[str, str] | None = None) -> pd.DataFrame:
    """All headlines for `symbols` in [start, end] via the paginated news endpoint."""
    key, secret = os.environ.get("ALPACA_API_KEY_ID"), os.environ.get("ALPACA_API_SECRET_KEY")
    if not (key and secret):
        raise RuntimeError("ALPACA_API_KEY_ID / ALPACA_API_SECRET_KEY not set")
    headers = {"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": secret}

    items = []
    for i in range(0, len(symbols), SYMBOL_CHUNK):
        chunk = symbols[i:i + SYMBOL_CHUNK]
        params = {"symbols": ",".join(chunk), "start": start, "limit": PAGE_LIMIT,
                  "include_content": "false", "sort": "asc"}
        if end:
            params["end"] = end
        while True:
            resp = requests.get(NEWS_URL, headers=headers, params=params, timeout=30)
            resp.raise_for_status()
            payload = resp.json()
            items.extend(payload.get("news", []))
            token = payload.get("next_page_token")
            if not token:
                break
            params["page_token"] = token
            time.sleep(REQUEST_PAUSE)
        time.sleep(REQUEST_PAUSE)
    df = news_to_frame(items, names)
    # articles carry every symbol they mention — keep only the requested universe, or the
    # scoring run pays to score names the backtest can't trade
    return df[df["ticker"].isin(set(symbols))].reset_index(drop=True)
