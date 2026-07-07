import numpy as np
import pandas as pd
from tracks.asset_growth.signal import asset_growth, growth_score


def test_asset_growth_yoy():
    # annual total assets, date x ticker
    idx = pd.to_datetime(["2021-12-31", "2022-12-31", "2023-12-31"])
    assets = pd.DataFrame({"A": [100.0, 120.0, 132.0], "B": [200.0, 200.0, 100.0]}, index=idx)
    g = asset_growth(assets)
    assert np.isclose(g.loc[idx[1], "A"], 0.20)   # 100->120
    assert np.isclose(g.loc[idx[2], "B"], -0.50)  # 200->100
    assert g.index.equals(idx[1:])                # first year has no prior -> dropped


def test_growth_score_is_contrarian():
    # low asset growth should score HIGH (long), high growth should score LOW (short)
    idx = pd.to_datetime(["2022-12-31"])
    g = pd.DataFrame({"A": [0.50], "B": [-0.10]}, index=idx)
    score = growth_score(g)
    assert score.loc[idx[0], "B"] > score.loc[idx[0], "A"]  # B (low growth) ranks above A
