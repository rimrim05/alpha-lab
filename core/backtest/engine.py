"""Weights + returns -> gross/net daily P&L. Weights at t apply to returns at t+1."""
import pandas as pd


def backtest(weights: pd.DataFrame, returns: pd.DataFrame, cost_bps: float) -> pd.DataFrame:
    weights, returns = weights.align(returns, join="inner")
    if weights.empty:
        raise ValueError("no overlapping dates between weights and returns")
    held = weights.shift(1).fillna(0.0)
    gross = (held * returns.fillna(0.0)).sum(axis=1)
    turnover = (weights.fillna(0.0) - held).abs().sum(axis=1)
    net = gross - turnover * cost_bps / 1e4
    return pd.DataFrame({"gross": gross, "net": net, "turnover": turnover})
