"""Shared entry/exit band logic for mean-reversion signals.

Given a standardized series (pair spread z-score, or residual s-score), take a
mean-reversion position: go long (+1) when the series is far BELOW zero (cheap,
expect reversion up), short (-1) when far ABOVE zero, and flatten when it returns
inside the exit band. Positions are stateful — held between crossings.
"""
import pandas as pd


def band_positions(series: pd.Series, entry: float = 2.0, exit_: float = 0.5) -> pd.Series:
    pos = 0
    out = []
    for v in series:
        if pd.isna(v):
            out.append(pos)
            continue
        if pos == 0:
            if v <= -entry:
                pos = 1
            elif v >= entry:
                pos = -1
        else:
            if abs(v) <= exit_:
                pos = 0
        out.append(pos)
    return pd.Series(out, index=series.index)
