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


def sharpe_bootstrap(returns: pd.Series, periods_per_year: int, n_sims: int = 1000,
                     block: int = 20, seed: int = 0) -> dict:
    """Circular block bootstrap of net returns -> resampled annualized-Sharpe distribution.

    Path-luck check, complementary to deflated_sharpe (selection across trials) and the
    perturbation red-team (parameter sensitivity): how much does the point Sharpe depend on
    this particular composition of the return path? Read p05 against the repo kill bar
    (net Sharpe < 0.5 is dead) — a wide interval or p05 < 0 means the headline number leans
    on a few lucky returns. Blocks preserve short-range autocorrelation.
    """
    r = returns.dropna().to_numpy(dtype=float)
    T = len(r)
    if T < 2 * block:
        raise ValueError(f"need >= {2 * block} obs for block={block}, got {T}")
    rng = np.random.default_rng(seed)
    n_blocks = -(-T // block)                                   # ceil
    starts = rng.integers(0, T, size=(n_sims, n_blocks, 1))
    idx = (starts + np.arange(block)) % T                       # circular wrap
    sims = r[idx.reshape(n_sims, -1)[:, :T]]
    std = sims.std(axis=1, ddof=1)
    sr = np.where(std > 0, sims.mean(axis=1) / np.where(std > 0, std, 1.0), 0.0)
    sr = np.sort(sr * np.sqrt(periods_per_year))
    original = sharpe(returns, periods_per_year)
    return {
        "sharpe": original,
        "p05": float(np.quantile(sr, 0.05)),
        "median": float(np.quantile(sr, 0.50)),
        "p95": float(np.quantile(sr, 0.95)),
        "pct_original": float(np.searchsorted(sr, original) / n_sims),
        "n_sims": n_sims, "block": block,
    }


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
