"""Shared equity universe: current S&P Composite 1500 (large + mid + small cap).

Fetches current index membership from Wikipedia — real breadth across the cap
spectrum, including genuine small caps (S&P 600). IMPORTANT LIMITATION: this is
*current* membership, so it is still survivorship-biased (names dropped after
declining are excluded). It fixes the "too narrow / mega-cap only" problem but NOT
survivorship — only point-in-time membership (WRDS/CRSP) does that.
"""
import io
from pathlib import Path

import pandas as pd
import requests

SP_WIKI = {
    "500": "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
    "400": "https://en.wikipedia.org/wiki/List_of_S%26P_400_companies",
    "600": "https://en.wikipedia.org/wiki/List_of_S%26P_600_companies",
}
HEADERS = {"User-Agent": "alpha-lab research (kristen@example.com)"}


def clean_ticker(t: str) -> str:
    """Normalize to yfinance form: uppercase, class dots -> dashes (BRK.B -> BRK-B)."""
    return str(t).strip().upper().replace(".", "-").replace("$", "")


def extract_symbols(tables: list[pd.DataFrame]) -> pd.DataFrame:
    """From the tables on a Wikipedia constituents page, pull the one with a
    symbol/ticker column into a (ticker, sector) frame."""
    for df in tables:
        cols = {str(c).lower(): c for c in df.columns}
        sym = next((cols[k] for k in cols if k in ("symbol", "ticker symbol", "ticker")), None)
        if sym is None:
            continue
        out = pd.DataFrame({"ticker": df[sym].map(clean_ticker)})
        sec = next((cols[k] for k in cols if "sector" in k), None)
        out["sector"] = df[sec].astype(str).values if sec else "Unknown"
        return out
    raise ValueError("no symbol/ticker column found in any table")


def fetch_sp_composite(which=("500", "400", "600"), cache: Path | None = None) -> pd.DataFrame:
    """Return current S&P composite constituents as (ticker, sector, index). Network."""
    if cache and Path(cache).exists():
        return pd.read_parquet(cache)
    frames = []
    for idx in which:
        resp = requests.get(SP_WIKI[idx], headers=HEADERS, timeout=30)
        resp.raise_for_status()
        tables = pd.read_html(io.StringIO(resp.text))
        frames.append(extract_symbols(tables).assign(index=idx))
    df = (pd.concat(frames, ignore_index=True)
          .drop_duplicates("ticker", keep="first")
          .sort_values("ticker")
          .reset_index(drop=True))
    df = df[df["ticker"].str.match(r"^[A-Z][A-Z-]*$")]  # drop malformed rows
    if cache:
        Path(cache).parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(cache)
    return df


# Point-in-time S&P 500 membership (fja05680, maintained). Full constituent snapshot
# at each change date — forward-filled it reconstructs membership on any past day.
# This is the free-data fix for INCLUSION look-ahead (trading a name before it joined).
# It does NOT fix delisting survivorship: names acquired/failed have no price data in
# yfinance at all, so they can't be re-added. Point-in-time PRICES need CRSP/WRDS.
PIT_SP500_URL = ("https://raw.githubusercontent.com/fja05680/sp500/master/"
                 "S%26P%20500%20Historical%20Components%20%26%20Changes%20(Updated).csv")


def fetch_sp500_pit_changes(cache: Path | None = None) -> pd.DataFrame:
    """S&P 500 membership change-log as [date, members] — members is a sorted list of
    cleaned tickers effective on that date (a full snapshot, not a delta). Network."""
    if cache and Path(cache).exists():
        return pd.read_parquet(cache)
    resp = requests.get(PIT_SP500_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    raw = pd.read_csv(io.StringIO(resp.text))
    raw["date"] = pd.to_datetime(raw["date"])
    raw = raw.sort_values("date").reset_index(drop=True)
    members = [sorted({clean_ticker(t) for t in str(row).split(",")}) for row in raw["tickers"]]
    df = pd.DataFrame({"date": raw["date"], "members": members})
    if cache:
        Path(cache).parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(cache)
    return df


def membership_mask(changes: pd.DataFrame, dates, tickers) -> pd.DataFrame:
    """Daily boolean frame (dates x tickers): True where the ticker was an S&P 500
    member. Forward-fills each change-date snapshot onto the trading calendar."""
    tickers = list(tickers)
    dates = pd.DatetimeIndex(dates)
    rows = [[t in set(m) for t in tickers] for m in changes["members"]]
    mat = pd.DataFrame(rows, index=pd.to_datetime(changes["date"].values), columns=tickers)
    mat = mat[~mat.index.duplicated(keep="last")].sort_index()
    daily = mat.reindex(mat.index.union(dates)).ffill().reindex(dates)
    return daily.fillna(False).astype(bool)


def ever_members(changes: pd.DataFrame) -> set:
    """Set of tickers that were an S&P 500 member at any point in the change-log."""
    out = set()
    for m in changes["members"]:
        out |= set(m)
    return out
