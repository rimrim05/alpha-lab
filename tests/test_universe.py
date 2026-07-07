import pandas as pd
import pytest
from core.data.universe import (clean_ticker, extract_symbols, membership_mask,
                                ever_members)


def test_clean_ticker():
    assert clean_ticker("BRK.B") == "BRK-B"
    assert clean_ticker(" aapl ") == "AAPL"
    assert clean_ticker("BF.B") == "BF-B"


def test_extract_symbols_finds_symbol_and_sector():
    tables = [
        pd.DataFrame({"Foo": [1, 2]}),  # decoy table, no symbol column
        pd.DataFrame({"Symbol": ["AAPL", "BRK.B"],
                      "Security": ["Apple", "Berkshire"],
                      "GICS Sector": ["Tech", "Financials"]}),
    ]
    out = extract_symbols(tables)
    assert list(out["ticker"]) == ["AAPL", "BRK-B"]
    assert list(out["sector"]) == ["Tech", "Financials"]


def test_extract_symbols_handles_ticker_column_name():
    tables = [pd.DataFrame({"Ticker symbol": ["MSFT"], "Company": ["Microsoft"]})]
    out = extract_symbols(tables)
    assert list(out["ticker"]) == ["MSFT"]
    assert list(out["sector"]) == ["Unknown"]


def test_extract_symbols_raises_when_no_symbol():
    with pytest.raises(ValueError):
        extract_symbols([pd.DataFrame({"Foo": [1], "Bar": [2]})])


def test_membership_mask_forward_fills_snapshots():
    # two change dates: AAPL always in; GOOG added on the 2nd date, MSFT dropped then.
    changes = pd.DataFrame({
        "date": pd.to_datetime(["2020-01-01", "2020-06-01"]),
        "members": [["AAPL", "MSFT"], ["AAPL", "GOOG"]],
    })
    dates = pd.to_datetime(["2020-03-01", "2020-06-15"])  # one in each regime
    mask = membership_mask(changes, dates, ["AAPL", "MSFT", "GOOG"])
    assert mask.loc["2020-03-01"].tolist() == [True, True, False]   # snapshot 1
    assert mask.loc["2020-06-15"].tolist() == [True, False, True]   # snapshot 2 (MSFT out, GOOG in)
    assert ever_members(changes) == {"AAPL", "MSFT", "GOOG"}


def test_membership_mask_before_first_change_is_false():
    changes = pd.DataFrame({"date": pd.to_datetime(["2020-01-01"]), "members": [["AAPL"]]})
    mask = membership_mask(changes, pd.to_datetime(["2019-06-01"]), ["AAPL"])
    assert mask.loc["2019-06-01"].tolist() == [False]  # no look-ahead before membership begins
