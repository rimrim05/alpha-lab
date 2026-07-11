"""Robustness pass: parameter stability maps, deflated Sharpe, rank IC.

A) Parameter maps — grid the two core designs' tunables and score each point by rolling
   12m walk-forward stats. This is a plateau test of the ALREADY-CHOSEN params, not a
   search: the registered params stay frozen regardless of the map (any re-pick would be
   a new trial in the ledger).
B) Deflated Sharpe (Bailey & Lopez de Prado) on the 5y window with N=18 trials — the
   probability that a survivor's Sharpe is real given how many things we tried.
C) Rank IC of the 12-1 momentum signal (signal quality before portfolio construction).
"""
import json
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd

import harness

HERE = Path(__file__).parent
OUT = HERE / "robustness"
OUT.mkdir(exist_ok=True)
ND = NormalDist()
CUT5 = "2021-07-10"


def rolling12(net):
    nav = (1 + net).cumprod()
    rets = []
    for i in range(252, len(nav), 63):
        w = net.iloc[i - 252:i]
        if (w == 0).mean() <= 0.5:
            rets.append(float((1 + w).prod() - 1))
    return np.array(rets)


def score(net):
    r = rolling12(net)
    sh = net.mean() / net.std() * np.sqrt(252) if net.std() > 0 else 0
    return {"median12": float(np.median(r)), "worst12": float(r.min()),
            "sharpe": float(sh), "pct18": float((r >= 0.18).mean())}


def qqq_voltarget_net(panel, sigma, lb, cap=2.0, band=0.05):
    q = panel["close"]["QQQ"]
    ret = q.pct_change(fill_method=None)
    rv = ret.rolling(lb).std() * np.sqrt(252)
    w_t = (sigma / rv).clip(upper=cap)
    w = w_t.copy()
    w[(w_t - w_t.shift(1)).abs() < band] = np.nan  # tolerance band approx
    w = w.ffill().fillna(0.0)
    return (w.shift(1) * ret).fillna(0) - (w.diff().abs().fillna(0) * 2e-4)


def trend_vol_net(panel, sma_w, sigma, lb=21, cap=2.0):
    q, bil = panel["close"]["QQQ"], panel["close"]["BIL"]
    qret, bret = q.pct_change(fill_method=None), bil.pct_change(fill_method=None)
    sma = q.rolling(sma_w).mean()
    state = pd.Series(np.nan, index=q.index)
    state[q > sma * 1.01] = 1.0
    state[q < sma * 0.99] = 0.0
    state = state.ffill().fillna(0.0)
    state[sma.isna()] = 0.0
    rv = qret.rolling(lb).std() * np.sqrt(252)
    wq = ((sigma / rv).clip(upper=cap) * state).fillna(0.0)
    wb = ((1 - state) * bil.notna()).astype(float)
    gross = (wq.shift(1) * qret).fillna(0) + (wb.shift(1) * bret).fillna(0)
    cost = (wq.diff().abs().fillna(0) + wb.diff().abs().fillna(0)) * 2e-4
    return gross - cost


def param_maps(panel):
    lines = ["# Parameter stability maps (plateau test — registered params stay frozen)",
             "", "Metric shown: median rolling-12m net / worst 12m / full-period Sharpe.", ""]
    lines.append("## vol_managed_qqq  (registered: sigma=0.25, lookback=21)\n")
    lines.append("| sigma \\ lookback | " + " | ".join(str(l) for l in [10, 15, 21, 42, 63]) + " |")
    lines.append("|---|---|---|---|---|---|")
    for s in [0.15, 0.20, 0.25, 0.30, 0.35]:
        row = [f"| {s:.2f}"]
        for lb in [10, 15, 21, 42, 63]:
            m = score(qqq_voltarget_net(panel, s, lb))
            row.append(f"{m['median12']:+.0%} / {m['worst12']:+.0%} / {m['sharpe']:.2f}")
        lines.append(" | ".join(row) + " |")
    lines.append("\n## trend_vol_qqq  (registered: sma=200, sigma=0.25)\n")
    lines.append("| sigma \\ sma | " + " | ".join(str(w) for w in [100, 150, 200, 250, 300]) + " |")
    lines.append("|---|---|---|---|---|---|")
    for s in [0.15, 0.20, 0.25, 0.30, 0.35]:
        row = [f"| {s:.2f}"]
        for w in [100, 150, 200, 250, 300]:
            m = score(trend_vol_net(panel, w, s))
            row.append(f"{m['median12']:+.0%} / {m['worst12']:+.0%} / {m['sharpe']:.2f}")
        lines.append(" | ".join(row) + " |")
    (OUT / "param_maps.md").write_text("\n".join(lines) + "\n")
    print("param maps written")


def deflated_sharpe(panel):
    """DSR: P(true Sharpe > 0 | N=18 trials). Uses each spec's 5y daily net."""
    nets, srs = {}, {}
    for d in sorted((HERE / "specs").iterdir()):
        if not (d / "spec.py").exists() or (d / "benchmark").exists():
            continue
        try:
            r = harness.run(harness.load_spec(d), panel, start=CUT5)
            nets[d.name] = r["net_daily"]
            srs[d.name] = r["net_daily"].mean() / r["net_daily"].std()
        except Exception as e:
            print(d.name, "skip:", e)
    N = len(srs)
    sr_arr = np.array(list(srs.values()))
    em = 0.5772156649
    sr0 = sr_arr.std(ddof=1) * ((1 - em) * ND.inv_cdf(1 - 1 / N)
                                + em * ND.inv_cdf(1 - 1 / (N * np.e)))
    lines = [f"# Deflated Sharpe — 5y window, N={N} trials (adaptive loops make true N larger; see ledger)",
             "", f"Expected max daily Sharpe from luck alone: {sr0:.4f} "
             f"(annualized ≈ {sr0 * np.sqrt(252):.2f})", "",
             "| spec | ann Sharpe | DSR = P(SR > luck-max) | P(SR > 0) |", "|---|---|---|---|"]
    rows = []
    for name, net in nets.items():
        sr = srs[name]
        T = len(net)
        g3, g4 = float(net.skew()), float(net.kurt()) + 3
        denom = np.sqrt(max(1e-12, 1 - g3 * sr + (g4 - 1) / 4 * sr ** 2))
        dsr = ND.cdf((sr - sr0) * np.sqrt(T - 1) / denom)
        p0 = ND.cdf(sr * np.sqrt(T - 1) / denom)
        rows.append((name, sr * np.sqrt(252), dsr, p0))
    for name, s, dsr, p0 in sorted(rows, key=lambda x: -x[2]):
        lines.append(f"| {name} | {s:.2f} | {dsr:.1%} | {p0:.1%} |")
    lines += ["", "DSR reads: probability the spec's Sharpe exceeds what the LUCKIEST of 18",
              "independent tries would show by chance. Round-1 specs are in-sample-tinted on",
              "this window; only round-2 rows are clean. P(SR>0) ignores selection entirely",
              "(upper bound on honesty)."]
    (OUT / "deflated.md").write_text("\n".join(lines) + "\n")
    print("deflated written")


def rank_ic(panel):
    """Monthly rank IC of 12-1 momentum among PIT members, plus horizon decay."""
    close, member = panel["close"], panel["member"]
    etf = set(harness.META["etfs"] + harness.META["signal_only"])
    stocks = [c for c in close.columns if c not in etf]
    px = close[stocks]
    sig = px.shift(21) / px.shift(252) - 1
    month_ends = px.resample("ME").last().index
    month_ends = [d for d in month_ends if d >= px.index[0] + pd.Timedelta(days=400)]
    horizons = {"21d": 21, "42d": 42, "63d": 63}
    ics = {h: [] for h in horizons}
    dates = []
    idx = px.index
    for d in month_ends:
        pos = idx.searchsorted(d, side="right") - 1
        if pos < 252 or pos + 63 >= len(idx):
            continue
        t = idx[pos]
        m = member[stocks].iloc[pos] > 0
        s = sig.iloc[pos][m].dropna()
        if len(s) < 100:
            continue
        dates.append(t)
        for h, k in horizons.items():
            fwd = px.iloc[pos + k][s.index] / px.iloc[pos][s.index] - 1
            both = pd.concat([s, fwd], axis=1).dropna()
            ics[h].append(float(both.iloc[:, 0].rank().corr(both.iloc[:, 1].rank())))
    lines = ["# Rank IC — 12-1 momentum, monthly, PIT S&P 500 members (2015+)", ""]
    for h in horizons:
        a = np.array(ics[h])
        t = a.mean() / a.std() * np.sqrt(len(a))
        lines.append(f"- {h} forward: mean IC {a.mean():+.4f}, std {a.std():.3f}, "
                     f"t={t:.2f}, hit rate {(a > 0).mean():.0%}, n={len(a)} months")
    a = np.array(ics["21d"])
    by_year = pd.Series(a, index=pd.DatetimeIndex(dates)[:len(a)]).groupby(lambda d: d.year).mean()
    lines += ["", "21d IC by year: " + ", ".join(f"{y}: {v:+.3f}" for y, v in by_year.items())]
    (OUT / "ic.md").write_text("\n".join(lines) + "\n")
    print("ic written")


if __name__ == "__main__":
    panel = pd.read_parquet(HERE / "panel_2005.parquet")
    param_maps(panel)
    rank_ic(panel)
    deflated_sharpe(panel)
