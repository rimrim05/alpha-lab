import numpy as np
import pandas as pd
import pytest
from core.data.prices import validate_prices, daily_returns


def _prices():
    idx = pd.date_range("2024-01-01", periods=5, freq="B")
    return pd.DataFrame({"AAA": [100, 101, 102, 101, 103], "BBB": [50, 50, 51, 52, 52]}, index=idx)


def test_validate_ok():
    assert validate_prices(_prices()) is not None


def test_validate_rejects_empty():
    with pytest.raises(ValueError):
        validate_prices(pd.DataFrame())


def test_validate_rejects_duplicate_dates():
    df = _prices()
    df = pd.concat([df, df.iloc[[0]]])
    with pytest.raises(ValueError):
        validate_prices(df)


def test_daily_returns():
    r = daily_returns(_prices())
    assert np.isclose(r.iloc[0]["AAA"], 0.01)
    assert len(r) == 4
