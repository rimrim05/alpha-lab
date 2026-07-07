import numpy as np
import pandas as pd
from core.eval.scorecard import scorecard, to_markdown


def test_scorecard_structure():
    rng = np.random.default_rng(1)
    idx = pd.date_range("2022-01-01", periods=400, freq="B")
    net = pd.Series(rng.normal(0.0005, 0.01, 400), index=idx)
    bench = {"buy_and_hold": pd.Series(rng.normal(0.0003, 0.01, 400), index=idx)}
    res = scorecard(net, bench, n_trials=10, periods_per_year=252)
    assert set(res) >= {"sharpe", "deflated_sharpe_prob", "max_drawdown", "hit_rate",
                        "ann_return", "subperiods", "benchmarks"}
    assert len(res["subperiods"]) == 2
    md = to_markdown(res, "Test Strategy")
    assert "Test Strategy" in md and "deflated" in md.lower()
