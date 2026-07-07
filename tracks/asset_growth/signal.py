"""Asset-growth contrarian signal (Cooper, Gulen & Schill 2008).

Year-over-year total-asset growth is a CONTRARIAN cross-sectional signal: low-asset-
growth firms outperform high-growth firms (~20%/yr spread in the paper). So the score
is the NEGATIVE of asset growth — low growth ranks high (long), high growth ranks low
(short). Low turnover (annual), so it survives costs (Novy-Marx & Velikov).

Directly answers the "does highest YoY growth predict returns" question: it predicts
NEGATIVE returns — see [[LIT — Does highest YoY growth predict returns]].
"""
import pandas as pd


def asset_growth(assets: pd.DataFrame) -> pd.DataFrame:
    """YoY growth of total assets, per ticker. Input: annual assets (date x ticker).
    First period (no prior year) is dropped."""
    if assets.empty:
        raise ValueError("assets frame is empty")
    g = assets.sort_index().pct_change()
    return g.iloc[1:]


def growth_score(growth: pd.DataFrame) -> pd.DataFrame:
    """Contrarian score = -asset_growth. Low growth -> high score -> long side."""
    return -growth
