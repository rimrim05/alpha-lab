"""Offline checks for research/hunt2026/xmarket.py mechanics (no network)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parents[1] / "research/hunt2026"))
import xmarket  # noqa: E402

IDX = pd.bdate_range("2015-01-01", periods=600)


def synth(seed=0, vol=0.01):
    rng = np.random.default_rng(seed)
    return pd.Series(100 * np.exp(np.cumsum(rng.normal(3e-4, vol, len(IDX)))),
                     index=IDX)


def test_vm_weight_capped_and_banded():
    w = xmarket.weights(synth(vol=0.002))["vm"]  # calm series -> wants > 2x
    assert w.max() <= xmarket.CAP + 1e-12
    assert (w.iloc[300:] > 1.0).all()  # low vol => levered


def test_gate_is_binary_and_off_in_downtrend():
    down = pd.Series(np.linspace(100, 40, len(IDX)), index=IDX)
    g = xmarket.gate_state(down)
    assert set(np.unique(g)) <= {0.0, 1.0}
    assert g.iloc[-100:].sum() == 0  # persistent downtrend => flat


def test_no_lookahead_weights_lagged():
    # a shock at the last day must not change any weight held BEFORE it,
    # and the position earning day t's return is w[t-1] (shift(1) in net_returns)
    c = synth(seed=1)
    c2 = c.copy()
    c2.iloc[-1] *= 0.5
    for k in ["vm", "gate", "combo"]:
        w1, w2 = xmarket.weights(c)[k], xmarket.weights(c2)[k]
        assert (w1.iloc[:-1] == w2.iloc[:-1]).all(), k
    gross1 = (xmarket.weights(c)["vm"].shift(1) * c.pct_change()).iloc[-1]
    gross2 = (xmarket.weights(c2)["vm"].shift(1) * c2.pct_change()).iloc[-1]
    exp = (c2.iloc[-1] / c2.iloc[-2] - 1) / (c.iloc[-1] / c.iloc[-2] - 1)
    assert np.isclose(gross2 / gross1, exp, rtol=1e-9)
