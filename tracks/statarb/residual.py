"""Residual mean-reversion (Avellaneda & Lee 2010, lite).

Strip systematic risk by regressing each stock's returns on factor returns
(market/sector ETFs here; the paper also uses PCA), then trade the mean-reverting
idiosyncratic residual. The trading signal is the "s-score": a standardized level
of the cumulative residual, modeled as an Ornstein-Uhlenbeck process.
"""
import numpy as np
import pandas as pd


def residual_returns(stock_rets: pd.DataFrame, factor_rets: pd.DataFrame) -> pd.DataFrame:
    """OLS-regress each stock's returns on the factor returns; return residuals.

    Full-sample regression over the passed window (the runner applies it per
    trailing window). Residuals are the idiosyncratic return orthogonal to factors.
    """
    aligned = stock_rets.join(factor_rets, how="inner").dropna()
    F = aligned[factor_rets.columns].to_numpy()
    F = np.column_stack([np.ones(len(F)), F])  # intercept
    out = {}
    for col in stock_rets.columns:
        if col not in aligned:
            continue
        y = aligned[col].to_numpy()
        beta, *_ = np.linalg.lstsq(F, y, rcond=None)
        out[col] = pd.Series(y - F @ beta, index=aligned.index)
    return pd.DataFrame(out)


def rolling_residual(stock_rets: pd.DataFrame, factor_rets: pd.DataFrame,
                     window: int = 60) -> pd.DataFrame:
    """Vectorized single-factor rolling residual across many stocks.

    `factor_rets` has the SAME columns as `stock_rets` — each column is that stock's
    matched factor return (e.g. its sector ETF). Betas are estimated on a trailing
    `window` and LAGGED one day before forming the residual, so no look-ahead.
    Fast enough for a full S&P-500+600 universe (pure DataFrame ops).
    """
    rs, fr = stock_rets.align(factor_rets, join="inner")
    mean_s = rs.rolling(window).mean()
    mean_f = fr.rolling(window).mean()
    cov = (rs * fr).rolling(window).mean() - mean_s * mean_f
    var = (fr * fr).rolling(window).mean() - mean_f ** 2
    beta = cov / var.replace(0, pd.NA)
    alpha = mean_s - beta * mean_f
    resid = rs - alpha.shift(1) - beta.shift(1) * fr
    resid[beta.shift(1).isna()] = pd.NA
    return resid


def s_score(residual: pd.Series, window: int = 60) -> pd.Series:
    """s-score of one stock's residual stream: standardize the cumulative residual
    (the OU level) over a trailing window. Negative s = residual cheap (buy)."""
    cum = residual.cumsum()
    mu = cum.rolling(window).mean()
    sd = cum.rolling(window).std()
    return (cum - mu) / sd.replace(0, np.nan)
