import numpy as np
import pandas as pd
from core.backtest.portfolio import quantile_weights
from core.backtest.engine import backtest


def test_quantile_weights_dollar_neutral():
    idx = pd.date_range("2024-01-01", periods=2)
    scores = pd.DataFrame([[1, 2, 3, 4, 5]] * 2, index=idx, columns=list("ABCDE"))
    w = quantile_weights(scores, n_quantiles=5)
    assert np.isclose(w.sum(axis=1), 0).all()
    assert np.isclose(w.clip(lower=0).sum(axis=1), 1).all()
    assert w.loc[idx[0], "E"] > 0 and w.loc[idx[0], "A"] < 0


def test_backtest_no_lookahead_and_costs():
    idx = pd.date_range("2024-01-01", periods=3)
    w = pd.DataFrame({"A": [1.0, 1.0, 1.0], "B": [-1.0, -1.0, -1.0]}, index=idx)
    r = pd.DataFrame({"A": [0.0, 0.02, 0.01], "B": [0.0, 0.01, 0.0]}, index=idx)
    res = backtest(w, r, cost_bps=10)
    # day2 gross = w(day1)·r(day2) = 0.02 - 0.01 = 0.01
    assert np.isclose(res.loc[idx[1], "gross"], 0.01)
    # first day turnover = full gross book = 2.0
    assert np.isclose(res.loc[idx[0], "turnover"], 2.0)
    assert res["net"].iloc[0] < res["gross"].iloc[0] + 1e-12
