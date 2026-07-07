import numpy as np
import pandas as pd
from core.eval.metrics import sharpe, max_drawdown, deflated_sharpe, hit_rate


def _rets(mu=0.001, sigma=0.01, n=500, seed=7):
    rng = np.random.default_rng(seed)
    return pd.Series(rng.normal(mu, sigma, n))


def test_sharpe_known():
    r = pd.Series([0.01, -0.01] * 100)
    assert abs(sharpe(r, 252)) < 0.5  # mean ~0


def test_max_drawdown_negative():
    assert max_drawdown(_rets()) <= 0


def test_deflated_sharpe_bounds_and_monotonic_in_trials():
    r = _rets(mu=0.002)
    d1, d50 = deflated_sharpe(r, 1, 252), deflated_sharpe(r, 50, 252)
    assert 0 <= d50 <= d1 <= 1  # more trials -> lower confidence


def test_hit_rate():
    assert hit_rate(pd.Series([1.0, -1.0, 2.0, 3.0])) == 0.75
