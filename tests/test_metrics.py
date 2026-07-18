import numpy as np
import pandas as pd
import pytest
from core.eval.metrics import sharpe, max_drawdown, deflated_sharpe, hit_rate, sharpe_bootstrap


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


def test_sharpe_bootstrap_deterministic_and_centered():
    r = _rets(mu=0.002)
    b1 = sharpe_bootstrap(r, 252, n_sims=500)
    b2 = sharpe_bootstrap(r, 252, n_sims=500)
    assert b1 == b2                                        # seeded -> reproducible
    assert b1["p05"] < b1["median"] < b1["p95"]
    # iid returns: original sits inside its own resampled distribution, not in a tail
    assert 0.05 < b1["pct_original"] < 0.95
    assert abs(b1["median"] - b1["sharpe"]) < 0.5


def test_sharpe_bootstrap_crash_risk_widens_interval():
    # negative skew (steady gains, occasional crash: the classic fragile equity curve)
    # must bootstrap WIDER than a symmetric series at the exact same point Sharpe
    rng = np.random.default_rng(7)
    z = rng.normal(size=500)
    sym = pd.Series((z - z.mean()) / z.std(ddof=1) * 0.01 + 0.00143)
    crashy = pd.Series(np.full(500, 0.0025))
    crashy.iloc[::50] = -0.06
    a = sharpe_bootstrap(sym, 252, n_sims=500)
    b = sharpe_bootstrap(crashy, 252, n_sims=500)
    assert abs(a["sharpe"] - b["sharpe"]) < 0.05           # matched point Sharpe
    assert (b["p95"] - b["p05"]) > (a["p95"] - a["p05"])   # crash risk shows as spread


def test_sharpe_bootstrap_rejects_short_series():
    with pytest.raises(ValueError):
        sharpe_bootstrap(_rets(n=30), 252, block=20)
