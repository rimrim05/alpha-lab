"""SEC EDGAR companyfacts fetch for annual total assets (free, ~10yr history).

Network, called only from scripts. EDGAR gives point-in-time annual `Assets`
(us-gaap) from 10-K filings, far more history than yfinance's ~4 years, which is
what an annual asset-growth sort needs.
"""
import time
from pathlib import Path

import pandas as pd
import requests

HEADERS = {"User-Agent": "alpha-lab research kristen@example.com"}
TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"


def ticker_to_cik() -> dict[str, int]:
    r = requests.get(TICKER_MAP_URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return {row["ticker"].upper(): int(row["cik_str"]) for row in r.json().values()}


def fetch_annual_assets(tickers: list[str], cache: Path | None = None) -> pd.DataFrame:
    """Return annual total assets as a (fiscal-year-end date x ticker) frame."""
    cik = ticker_to_cik()
    series = {}
    for t in tickers:
        c = cik.get(t.upper())
        if c is None:
            continue
        try:
            r = requests.get(FACTS_URL.format(cik=c), headers=HEADERS, timeout=30)
            r.raise_for_status()
            units = r.json()["facts"]["us-gaap"]["Assets"]["units"]["USD"]
        except Exception:
            continue
        # annual 10-K values: form 10-K, frame like CY2023Q4I (instantaneous)
        annual = {}
        for row in units:
            if row.get("form") == "10-K" and row.get("fp") == "FY" and row.get("end"):
                annual[row["end"]] = row["val"]
        if annual:
            series[t] = pd.Series(annual)
        time.sleep(0.12)  # be polite to EDGAR
    if not series:
        raise ValueError("no EDGAR asset data returned")
    df = pd.DataFrame(series)
    df.index = pd.to_datetime(df.index)
    return df.sort_index()
