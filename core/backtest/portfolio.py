"""Signal scores -> dollar-neutral quantile long-short weights."""
import pandas as pd


def quantile_weights(scores: pd.DataFrame, n_quantiles: int = 5) -> pd.DataFrame:
    if scores.empty:
        raise ValueError("scores frame is empty")

    def _row(row: pd.Series) -> pd.Series:
        s = row.dropna()
        w = pd.Series(0.0, index=row.index)
        if len(s) < n_quantiles:
            return w
        q = pd.qcut(s.rank(method="first"), n_quantiles, labels=False)
        top, bot = s.index[q == n_quantiles - 1], s.index[q == 0]
        w[top], w[bot] = 1.0 / len(top), -1.0 / len(bot)
        return w

    return scores.apply(_row, axis=1)
