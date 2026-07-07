"""Shared entry/exit band logic for mean-reversion signals.

Given a standardized series (pair spread z-score, or residual s-score), take a
mean-reversion position: go long (+1) when the series is far BELOW zero (cheap,
expect reversion up), short (-1) when far ABOVE zero, and flatten when it returns
inside the exit band. Positions are stateful — held between crossings.
"""
import pandas as pd


def band_positions(series: pd.Series, entry: float = 2.0, exit_: float = 0.5,
                   long_floor: float | None = None) -> pd.Series:
    """long_floor caps how deep a LONG may go: you may only be long while the series
    is >= -long_floor. Below that (a "falling knife") you never enter, and a held long
    stops out. Default None = no floor (original behavior). Short side unaffected."""
    pos = 0
    out = []
    for v in series:
        if pd.isna(v):
            out.append(pos)
            continue
        too_deep = long_floor is not None and v < -long_floor
        if pos == 0:
            if v <= -entry and not too_deep:
                pos = 1
            elif v >= entry:
                pos = -1
        elif pos == 1 and too_deep:   # knife kept falling — stop out the long
            pos = 0
        elif abs(v) <= exit_:
            pos = 0
        out.append(pos)
    return pd.Series(out, index=series.index)
