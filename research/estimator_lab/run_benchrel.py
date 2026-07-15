"""Benchmark-relative (tracking) JSE vs PCA adjudication — EXP-2026-07-14-jse-benchrel.
Prereg: research/hunt2026/preregistrations/jse-benchrel-2026-07-14.md (frozen; run once).
Mirrors run_minvar.py conventions; only the objective (min tracking error to an EW
benchmark from a restricted basket) is new."""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from estimators import ESTIMATORS
from run_minvar import EXCLUDE, CAP, START

HERE = Path(__file__).parent
PANEL = HERE.parent / "hunt2026" / "panel_2005.parquet"
WINDOW = 63  # decisive weak-factor cell, fixed by prereg

ESTS = ["sample", "pca1", "pca3", "pca5", "jse1", "jse3", "jse5", "lw", "mp"]


def benchrel_weights(Sigma, basket_idx, w_b):
    """min (w-w_b)' Sigma (w-w_b), w supported on basket, sum w = 1;
    then house single-pass long-only clip + cap + renorm."""
    S_BB = Sigma[np.ix_(basket_idx, basket_idx)]
    c = (Sigma @ w_b)[basket_idx]
    ones = np.ones(len(basket_idx))
    try:
        Sc = np.linalg.solve(S_BB, c)
        S1 = np.linalg.solve(S_BB, ones)
    except np.linalg.LinAlgError:
        pinv = np.linalg.pinv(S_BB, hermitian=True, rcond=1e-10)
        Sc, S1 = pinv @ c, pinv @ ones
    denom = ones @ S1
    if abs(denom) < 1e-12 or not (np.isfinite(Sc).all() and np.isfinite(S1).all()):
        return None
    lam = (1.0 - ones @ Sc) / denom
    x = Sc + lam * S1
    x = np.clip(x, 0.0, None)          # long-only
    if x.sum() <= 0:
        return None
    x = x / x.sum()
    x = np.clip(x, 0.0, CAP)           # single-pass cap + renorm (house convention)
    s = x.sum()
    return x / s if s > 1e-9 else None


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
        hold = rets.loc[(rets.index > d) & (rets.index <= nxt)]
        if len(hold) < 10:
            continue
        win = rets.iloc[i - WINDOW + 1: i + 1]
        elig = (member.loc[d, stocks] > 0) & win.notna().all()
        names = sorted(elig.index[elig])
        if len(names) < 100:
            continue
        basket_idx = np.arange(0, len(names), 5)   # every 5th sorted ticker (prereg)
        w_b = np.full(len(names), 1.0 / len(names))
        R = win[names].to_numpy()
        Hret = hold[names].fillna(0.0).to_numpy()
        bench_ret = Hret @ w_b
        for est in ESTS:
            Sigma = ESTIMATORS[est](R)
            x = benchrel_weights(Sigma, basket_idx, w_b)
            if x is None:
                continue
            pr = Hret[:, basket_idx] @ x
            te = (pr - bench_ret).std(ddof=1) * np.sqrt(252)
            rows.append({"date": d, "est": est, "n_names": len(names),
                         "n_basket": len(basket_idx), "te": te,
                         "weights": pd.Series(x, index=[names[j] for j in basket_idx])})
        if m % 24 == 0:
            print(f"  {d.date()}  p={len(names)} basket={len(basket_idx)}")

    df = pd.DataFrame(rows)
    df["turnover"] = np.nan
    for est, g in df.groupby("est"):
        prev = None
        for j in g.index:
            w = df.at[j, "weights"]
            if prev is not None:
                u = w.index.union(prev.index)
                df.at[j, "turnover"] = (w.reindex(u, fill_value=0.0)
                                        - prev.reindex(u, fill_value=0.0)).abs().sum()
            prev = w
    out = df.drop(columns="weights")
    out.to_csv(HERE / "benchrel.csv", index=False)

    wide = out.pivot(index="date", columns="est", values="te").dropna()
    print(f"\n=== benchmark-relative TE, {len(wide)} months, n={WINDOW}, basket ~1/5 of universe ===")
    print(f"{'est':>8}  mean TE   med TE   mean turnover")
    tv = out.pivot(index="date", columns="est", values="turnover")
    for est in ESTS:
        if est in wide:
            print(f"{est:>8}  {wide[est].mean():7.4f}  {wide[est].median():7.4f}  {tv[est].mean():8.3f}")

    print("\n=== DECISIVE: jse_k - pca_k paired TE ===")
    for k in (1, 3, 5):
        j, p = f"jse{k}", f"pca{k}"
        dlt = wide[j] - wide[p]
        rel = (dlt / wide[p]).mean()
        t, pv = stats.ttest_rel(wide[j], wide[p])
        print(f"  k={k}: dTE mean {dlt.mean()*1e4:+.2f} bps ann  rel {rel:+.4%}  t={t:+.2f} p={pv:.4f}")
    k5 = wide["jse5"] - wide["pca5"]
    rel5 = (k5 / wide["pca5"]).mean()
    t5, pv5 = stats.ttest_rel(wide["jse5"], wide["pca5"])
    overturn = (rel5 <= -0.005) and (pv5 < 0.05) and (k5.mean() <= -0.0010)
    print(f"\nOVERTURN RULE (rel<=-0.5%, p<0.05, abs<=-10bps): {'OVERTURN' if overturn else 'VERDICT STANDS'}")


if __name__ == "__main__":
    main()
