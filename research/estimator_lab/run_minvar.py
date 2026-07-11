"""Estimator Lab walk-forward: monthly min-var books 2015->2026 on PIT S&P 500
members, judged on realized next-month vol. See PLAN.md (pre-registered)."""
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from estimators import ESTIMATORS

HERE = Path(__file__).parent
PANEL = HERE.parent / "hunt2026" / "panel_2005.parquet"
WINDOW = int(os.environ.get("EL_WINDOW", 252))  # ponytail: knob for the F-021 weak-factor reopen (n=63)
SUFFIX = "" if WINDOW == 252 else f"_w{WINDOW}"
CAP = 0.05
COST = 0.001  # 10bps/side, stocks
START = "2015-01-01"

# non-stock tickers, never in the universe (mirrors frozen pca_minvar_jse spec)
EXCLUDE = {
    "SPY", "QQQ", "IWM", "DIA", "MDY", "EFA", "EEM", "VGK", "EWJ", "TLT", "IEF",
    "SHY", "BIL", "LQD", "HYG", "TIP", "GLD", "SLV", "DBC", "USO", "UNG", "VNQ",
    "UUP", "FXE", "XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY",
    "XLRE", "XLC", "RSP", "SVXY", "^VIX",
}


def minvar_weights(Sigma, long_only):
    p = Sigma.shape[0]
    ones = np.ones(p)
    try:
        w = np.linalg.solve(Sigma, ones)
    except np.linalg.LinAlgError:
        w = np.linalg.pinv(Sigma, hermitian=True) @ ones
    # sample cov is singular (p > n): solve "succeeds" but garbage; residual check -> pinv
    if not np.isfinite(w).all() or np.linalg.norm(Sigma @ w - ones) > 1e-6 * np.sqrt(p):
        w = np.linalg.pinv(Sigma, hermitian=True, rcond=1e-10) @ ones
    if abs(w.sum()) < 1e-12:
        return None
    w = w / w.sum()
    if long_only:
        w = np.clip(w, 0.0, None)
        if w.sum() <= 0:
            return None
        w = w / w.sum()
    # ponytail: single-pass cap+renorm (house convention), not the exact capped QP
    w = np.clip(w, -CAP, CAP)
    s = w.sum()
    if abs(s) < 1e-9:
        return None
    return w / s


def main():
    panel = pd.read_parquet(PANEL)
    close, member = panel["close"], panel["member"].fillna(0.0)
    stocks = [t for t in close.columns if t not in EXCLUDE]
    rets = close[stocks].pct_change(fill_method=None)
    idx = close.index

    firsts = pd.Series(idx, index=idx).groupby(idx.to_period("M")).first()
    firsts = firsts[firsts >= pd.Timestamp(START)]
    pos = {d: i for i, d in enumerate(idx)}

    rows = []
    for m, (per, d) in enumerate(firsts.items()):
        i = pos[d]
        if i < WINDOW:
            continue
        nxt = firsts.iloc[m + 1] if m + 1 < len(firsts) else pd.Timestamp("2100-01-01")
        # weights set at close d earn d+1..nxt (harness convention); d's own return is
        # the last day of the fit window, so exclude it from the OOS hold to avoid overlap
        hold = rets.loc[(rets.index > d) & (rets.index <= nxt)]
        if len(hold) < 10:  # partial tail month
            continue
        win = rets.iloc[i - WINDOW + 1: i + 1]
        elig = (member.loc[d, stocks] > 0) & win.notna().all()
        names = list(elig.index[elig])
        if len(names) < 100:
            continue
        R = win[names].to_numpy()
        Hret = hold[names].fillna(0.0).to_numpy()  # delisted -> cash-out at 0
        for est, fn in ESTIMATORS.items():
            Sigma = fn(R)
            for lo in (False, True):
                w = minvar_weights(Sigma, lo)
                if w is None:
                    continue
                pr = Hret @ w
                rows.append({
                    "date": d, "est": est, "book": "long_only" if lo else "unconstrained",
                    "n_names": len(names),
                    "vol": pr.std(ddof=1) * np.sqrt(252),
                    "ret": pr.sum(),
                    "weights": pd.Series(w, index=names),
                })
        if m % 24 == 0:
            print(f"  {d.date()}  p={len(names)}")

    df = pd.DataFrame(rows)
    # one-side turnover vs previous month's book (union of names)
    df["turnover"] = np.nan
    for (est, book), g in df.groupby(["est", "book"]):
        prev = None
        for j in g.index:
            w = df.at[j, "weights"]
            if prev is not None:
                u = w.index.union(prev.index)
                df.at[j, "turnover"] = (w.reindex(u, fill_value=0.0)
                                        - prev.reindex(u, fill_value=0.0)).abs().sum()
            prev = w
    df["ret_net"] = df["ret"] - COST * df["turnover"].fillna(0.0)

    out = df.drop(columns="weights")
    out.to_csv(HERE / f"results{SUFFIX}.csv", index=False)

    print(f"\n=== WINDOW={WINDOW} :: JSE vs PCA paired delta (the F-021 weak-factor test) ===")
    print("negative = JSE improves (lower realized vol); this is the decisive statistic.")
    for book, g in out.groupby("book"):
        wide = g.pivot(index="date", columns="est", values="vol").dropna()
        for k in (1, 3, 5):
            j, p = f"jse{k}", f"pca{k}"
            if j in wide and p in wide:
                d = (wide[j] - wide[p]) * 100  # in vol %-points
                t, pv = stats.ttest_rel(wide[j], wide[p])
                print(f"  {book:13} k={k}: jse-pca = {d.mean():+.3f} vol%pts  t={t:+.2f} p={pv:.3f}")

    print("\n=== mean realized ann. vol per estimator (paired t vs sample) ===")
    summary = []
    for book, g in out.groupby("book"):
        wide = g.pivot(index="date", columns="est", values="vol").dropna()
        base = wide["sample"]
        for est in ESTIMATORS:
            v = wide[est]
            t, pval = (np.nan, np.nan) if est == "sample" else stats.ttest_rel(v, base)
            ge = g[g["est"] == est]
            ann = ge["ret_net"].mean() * 12
            annvol = ge["ret_net"].std(ddof=1) * np.sqrt(12)
            summary.append({
                "book": book, "est": est, "mean_vol": v.mean(),
                "t_vs_sample": t, "p_vs_sample": pval,
                "sharpe_net": ann / annvol if annvol > 0 else np.nan,
                "mean_turnover": ge["turnover"].mean(),
                "months": len(v),
            })
    sm = pd.DataFrame(summary)
    sm.to_csv(HERE / f"summary{SUFFIX}.csv", index=False)
    print(sm.to_string(index=False, float_format=lambda x: f"{x:.4f}"))


if __name__ == "__main__":
    main()
