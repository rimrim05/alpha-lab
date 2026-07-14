"""news_to_frame: symbol fan-out, ET date attribution, company mapping, dedup. No network."""
import pandas as pd
from core.data.news import news_to_frame


def _item(created_at, symbols, headline):
    return {"created_at": created_at, "symbols": symbols, "headline": headline}


def test_fan_out_and_company_map():
    items = [_item("2026-02-02T15:00:00Z", ["AAPL", "MSFT"], "Two giants rally")]
    df = news_to_frame(items, names={"AAPL": "Apple Inc."})
    assert len(df) == 2
    apple = df[df["ticker"] == "AAPL"].iloc[0]
    assert apple["company"] == "Apple Inc."
    assert apple["published_at"] == "2026-02-02T15:00:00+00:00"
    assert df[df["ticker"] == "MSFT"].iloc[0]["company"] == "MSFT"   # fallback = ticker


def test_dates_are_us_eastern():
    # 01:00 UTC on Feb 3 is still Feb 2 evening in New York
    df = news_to_frame([_item("2026-02-03T01:00:00Z", ["AAPL"], "After-hours move")])
    assert df.iloc[0]["date"] == "2026-02-02"


def test_dedup_same_headline_same_day():
    items = [_item("2026-02-02T15:00:00Z", ["AAPL"], "Repeat"),
             _item("2026-02-02T18:00:00Z", ["AAPL"], "Repeat")]
    df = news_to_frame(items)
    assert len(df) == 1
    assert df.iloc[0]["published_at"] == "2026-02-02T15:00:00+00:00"


def test_empty_input_gives_typed_empty_frame():
    df = news_to_frame([])
    assert list(df.columns) == ["published_at", "date", "ticker", "company", "headline"] and df.empty
