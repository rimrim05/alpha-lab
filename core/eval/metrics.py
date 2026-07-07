"""Performance metrics. deflated_sharpe follows Bailey & Lopez de Prado (2014)."""
import numpy as np
import pandas as pd
from scipy import stats

EULER_GAMMA = 0.5772156649015329


def sharpe(returns: pd.Series, periods_per_year: int) -> float:
    r = returns.dropna()
    if len(r) < 2 or r.std(ddof=1) == 0:
        return 0.0
    return float(r.mean() / r.std(ddof=1) * np.sqrt(periods_per_year))


def max_drawdown(returns: pd.Series) -> float:
    curve = (1 + returns.fillna(0)).cumprod()
    return float((curve / curve.cummax() - 1).min())


def hit_rate(returns: pd.Series) -> float:
    r = returns.dropna()
    return float((r > 0).mean()) if len(r) else 0.0


def deflated_sharpe(returns: pd.Series, n_trials: int, periods_per_year: int) -> float:
    """Probability the true Sharpe exceeds zero, deflating for n_trials searches."""
    r = returns.dropna()
    T = len(r)
    if T < 10:
        return 0.0
    sr = float(r.mean() / r.std(ddof=1))  # per-period SR
    sk = float(stats.skew(r))
    ku = float(stats.kurtosis(r, fisher=False))
    if n_trials <= 1:
        sr0 = 0.0
    else:
        # expected max SR of n_trials zero-skill strategies (per-period units)
        z1 = stats.norm.ppf(1 - 1.0 / n_trials)
        z2 = stats.norm.ppf(1 - 1.0 / (n_trials * np.e))
        sr0 = np.sqrt(1.0 / (T - 1)) * ((1 - EULER_GAMMA) * z1 + EULER_GAMMA * z2)
    denom = np.sqrt(max(1e-12, 1 - sk * sr + (ku - 1) / 4.0 * sr**2))
    z = (sr - sr0) * np.sqrt(T - 1) / denom
    return float(stats.norm.cdf(z))
