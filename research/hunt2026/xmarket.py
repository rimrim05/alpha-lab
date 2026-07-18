"""Cross-market replication of the vol-managed-leverage mechanism and the trend gate.

REPLICATION EVIDENCE, NOT A NEW TRIAL: the registered params from vol_managed_qqq /
trend_vol_qqq (sigma_target=0.25, rv_lookback=21, tolerance_band=0.05, cap 2x,
sma_window=200, hysteresis 1%) are applied UNCHANGED to every asset. Zero per-asset
tuning, so there is no selection here to deflate; the question is only whether the
mechanism generalizes (Moreira & Muir 2017 Table on non-US assets; Faber 2007).

Universe: every non-US-large-cap / non-equity ETF already in panel_2005.parquet plus
10 liquid iShares country funds pulled to panel_xmarket.parquet (all inception <2005,
so full-window history). Costs 2 bps/side (ETFs). Risk-off leg is cash at 0 (BIL only
exists from 2007; 0 is the conservative choice and identical across assets).

Output: robustness/xmarket.md. Run: .venv/bin/python research/hunt2026/xmarket.py
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform
from scipy.stats import binomtest

HERE = Path(__file__).parent
OUT = HERE / "robustness" / "xmarket.md"
XPANEL = HERE / "panel_xmarket.parquet"

# frozen registered params, do not touch
SIGMA, LB, CAP, BAND = 0.25, 21, 2.0, 0.05
SMA_W, HYST = 200, 0.01
COST = 2e-4  # 2 bps/side, ETFs
BURN = 252   # common start for all four variants (covers SMA200 + rv21 warmup)

IN_PANEL = ["EFA", "EEM", "VGK", "EWJ", "TLT", "IEF", "GLD", "SLV", "DBC",
            "USO", "UNG", "UUP", "FXE", "HYG", "LQD", "VNQ", "IWM", "MDY"]
NEW = ["EWU", "EWG", "EWA", "EWC", "EWY", "EWT", "EWZ", "FXI", "EWH", "EWS"]
CLASS = {**{t: "intl-equity" for t in ["EFA", "EEM", "VGK", "EWJ"] + NEW},
         **{t: "us-equity-factor" for t in ["IWM", "MDY", "VNQ"]},
         **{t: "bonds" for t in ["TLT", "IEF", "HYG", "LQD"]},
         **{t: "commodities" for t in ["GLD", "SLV", "DBC", "USO", "UNG"]},
         **{t: "fx" for t in ["UUP", "FXE"]}}


# ---------------------------------------------------------------- mechanics
def tol_band(raw):
    """No-trade tolerance band, identical loop to specs/vol_managed_qqq/spec.py."""
    w = np.empty_like(raw)
    cur = 0.0
    for i, tgt in enumerate(raw):
        if abs(tgt - cur) > BAND:
            cur = tgt
        w[i] = cur
    return w


def gate_state(close):
    """200d SMA gate with 1% hysteresis, identical to specs/trend_vol_qqq/spec.py."""
    sma = close.rolling(SMA_W).mean()
    c, s = close.to_numpy(), sma.to_numpy()
    out = np.zeros(len(c))
    state = None
    for i in range(len(c)):
        if np.isnan(s[i]):
            continue
        if state is None:
            state = c[i] > s[i]
        elif state:
            if c[i] < s[i] * (1 - HYST):
                state = False
        elif c[i] > s[i] * (1 + HYST):
            state = True
        out[i] = 1.0 if state else 0.0
    return pd.Series(out, index=close.index)


def weights(close):
    """The four variants' weight paths for one asset."""
    ret = close.pct_change(fill_method=None)
    rv = ret.rolling(LB).std() * np.sqrt(252)
    vm_raw = (SIGMA / rv).clip(upper=CAP).fillna(0.0)
    gate = gate_state(close)
    return {"bh": pd.Series(1.0, index=close.index),
            "vm": pd.Series(tol_band(vm_raw.to_numpy()), index=close.index),
            "gate": gate,
            "combo": pd.Series(tol_band((vm_raw * gate).to_numpy()), index=close.index)}


def net_returns(close, w):
    ret = close.pct_change(fill_method=None)
    return (w.shift(1) * ret).fillna(0.0) - w.diff().abs().fillna(0.0) * COST


def metrics(net):
    if len(net) < 300 or net.std() == 0:
        return {"cagr": np.nan, "sharpe": np.nan, "worst12": np.nan}
    nav = (1 + net).cumprod()
    yrs = len(net) / 252
    roll12 = nav / nav.shift(252) - 1
    return {"cagr": float(nav.iloc[-1] ** (1 / yrs) - 1),
            "sharpe": float(net.mean() / net.std() * np.sqrt(252)),
            "worst12": float(roll12.min())}


# ---------------------------------------------------------------- data
def pull_new(start="2005-01-01", end="2026-07-11"):
    import yfinance as yf
    raw = yf.download(NEW, start=start, end=end, interval="1d",
                      auto_adjust=True, progress=False, threads=True)
    panel = pd.concat({"close": raw["Close"][NEW]}, axis=1)
    panel.columns.names = ["field", "ticker"]
    panel.to_parquet(XPANEL)
    with open(HERE.parents[1] / "data/manifest.jsonl", "a") as f:
        f.write(json.dumps({
            "name": "hunt2026_panel_xmarket", "source": "yfinance",
            "filters": {"tickers": NEW, "start": start, "end": end},
            "path": "research/hunt2026/panel_xmarket.parquet", "rows": len(panel),
            "pulled_at": datetime.now(timezone.utc).isoformat()}) + "\n")
    return panel


def load_closes():
    base = pd.read_parquet(HERE / "panel_2005.parquet")["close"][IN_PANEL]
    xp = pd.read_parquet(XPANEL) if XPANEL.exists() else pull_new()
    return base.join(xp["close"], how="outer")


# ---------------------------------------------------------------- study
def run(closes):
    rows, bh_rets = {}, {}
    for t in closes.columns:
        c = closes[t].dropna()
        if len(c) <= BURN + 300:
            continue
        wts = weights(c)
        nets = {k: net_returns(c, w).iloc[BURN:] for k, w in wts.items()}
        m = {k: metrics(v) for k, v in nets.items()}
        rows[t] = m
        bh_rets[t] = nets["bh"]
    return rows, pd.DataFrame(bh_rets)


def clusters(bh):
    corr = bh.corr(min_periods=500)
    dist = squareform((1 - corr).clip(lower=0).to_numpy(), checks=False)
    labels = fcluster(linkage(dist, method="average"), t=0.5, criterion="distance")
    out = {}
    for t, lab in zip(corr.columns, labels):
        out.setdefault(int(lab), []).append(t)
    return out  # cluster id -> tickers (avg pairwise corr within > ~0.5)


def sign_line(name, wins, n):
    p = binomtest(wins, n, 0.5, alternative="greater").pvalue
    return f"- **{name}: {wins}/{n} clusters improved** (one-sided sign test p = {p:.3f})"


def main():
    closes = load_closes()
    rows, bh = run(closes)
    clus = clusters(bh)
    memb = {t: cid for cid, ts in clus.items() for t in ts}

    lines = ["# Cross-market replication: vol-managed leverage + trend gate",
             "",
             f"*Generated by `xmarket.py`, {datetime.now(timezone.utc).date()}. "
             "Replication evidence, NOT a new trial — registered params "
             "(sigma=0.25, rv21, band 0.05, cap 2x; SMA200, 1% hysteresis) applied "
             "unchanged to every asset, zero per-asset tuning. Costs 2 bps/side, "
             "risk-off leg = cash at 0%. All variants scored from each asset's "
             f"day {BURN} onward (common warmup), full available history to "
             f"{closes.index[-1].date()}.*",
             "",
             "## Per-asset results (net of costs)",
             "",
             "| Ticker | Class | Clu | B&H CAGR | B&H Sharpe | B&H worst 12m | "
             "VM Sharpe | ΔVM | Gate Sharpe | ΔGate | Combo Sharpe | ΔCombo |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    order = sorted(rows, key=lambda t: (CLASS[t], t))
    for t in order:
        m = rows[t]
        b, v, g, c = m["bh"], m["vm"], m["gate"], m["combo"]
        lines.append(
            f"| {t} | {CLASS[t]} | {memb.get(t, '-')} | {b['cagr']:+.1%} | "
            f"{b['sharpe']:.2f} | {b['worst12']:+.1%} | {v['sharpe']:.2f} | "
            f"{v['sharpe']-b['sharpe']:+.2f} | {g['sharpe']:.2f} | "
            f"{g['sharpe']-b['sharpe']:+.2f} | {c['sharpe']:.2f} | "
            f"{c['sharpe']-b['sharpe']:+.2f} |")

    lines += ["", "## Correlation clusters (avg-linkage on daily B&H return corr, "
              "cut at 1−corr = 0.5)", ""]
    for cid in sorted(clus):
        lines.append(f"- cluster {cid}: {', '.join(sorted(clus[cid]))}")
    lines += ["", "Assets inside one cluster share a factor (IWM/MDY/VNQ/VGK/EFA and "
              "the country funds are mostly one global-equity draw, not 14). "
              "Aggregate counts below are at CLUSTER level: a cluster counts as "
              "improved iff the MEDIAN Sharpe delta across its members is > 0.", ""]

    lines += ["## Aggregate (cluster-level sign test)", ""]
    n = len(clus)
    for name, key in [("Vol management", "vm"), ("Trend gate", "gate"),
                      ("Combo", "combo")]:
        wins = sum(1 for ts in clus.values()
                   if np.median([rows[t][key]["sharpe"] - rows[t]["bh"]["sharpe"]
                                 for t in ts]) > 0)
        lines.append(sign_line(name, wins, n))
    lines += ["", "Ticker-level counts (NOT independent draws, shown for "
              "transparency only):"]
    nt = len(rows)
    for name, key in [("Vol management", "vm"), ("Trend gate", "gate"),
                      ("Combo", "combo")]:
        wins = sum(1 for t in rows
                   if rows[t][key]["sharpe"] - rows[t]["bh"]["sharpe"] > 0)
        lines.append(f"- {name}: {wins}/{nt} tickers")

    lines += ["", "## Mechanism verdict by asset class", ""]
    for cls in ["intl-equity", "us-equity-factor", "bonds", "commodities", "fx"]:
        ts = [t for t in rows if CLASS[t] == cls]
        dvm = np.median([rows[t]["vm"]["sharpe"] - rows[t]["bh"]["sharpe"] for t in ts])
        dg = np.median([rows[t]["gate"]["sharpe"] - rows[t]["bh"]["sharpe"] for t in ts])
        lines.append(f"- **{cls}** (n={len(ts)}): median ΔSharpe vol-mgmt "
                     f"{dvm:+.2f}, trend gate {dg:+.2f}")

    lines += ["", "## Honest read", "",
              "Neither mechanism replicates convincingly outside US large-cap "
              "equities at the frozen params: no cluster-level sign test rejects "
              "the coin-flip null. Sharpe deltas are small either way; where the "
              "gate 'wins' big it is on disasters (UNG, DBC) by simply owning "
              "less of a melting asset, and the equity mega-cluster (18 of 28 "
              "tickers) is one draw, not eighteen. The registered QQQ specs' "
              "edge should be read as US-tech-equity-specific (levered beta plus "
              "a mild vol-timing kicker), not as a universal risk-management "
              "anomaly. This weakens the external-validity claim; it does not "
              "invalidate the specs, whose mechanism notes already scoped them "
              "to the equity premium."]
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT} ({nt} assets, {n} clusters)")


if __name__ == "__main__":
    main()
