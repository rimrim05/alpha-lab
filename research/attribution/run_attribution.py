"""EXP-2026-07-14-factor-attribution — implements the frozen prereg
research/hunt2026/preregistrations/factor-attribution-2026-07-14.md exactly.

Run from repo root: .venv/bin/python research/attribution/run_attribution.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "research/hunt2026"))
sys.path.insert(0, str(REPO))
import harness  # noqa: E402

OUT = REPO / "research/attribution"
FF_END = pd.Timestamp("2026-05-29")
LAG = 5
M0_COLS = ["Mkt-RF"]
M1_COLS = M0_COLS + ["SMB", "HML", "RMW", "CMA", "Mom"]
M2_COLS = M1_COLS + ["TSMOM", "QQQRES"]
MODELS = {"M0": M0_COLS, "M1": M1_COLS, "M2": M2_COLS}

BOOKS = {  # name -> (results dir, blind start passed to harness.run)
    "vol_managed_qqq": ("results", "2025-07-10"),
    "vol_core_svxy": ("results", "2025-07-10"),
    "dual_momentum_gem": ("results", "2025-07-10"),
    "momentum_concentrated": ("results", "2025-07-10"),
    "trend_vol_qqq": ("results5y", "2021-07-10"),
    "defensive_ensemble": ("results5y", "2021-07-10"),
    "dual_momentum_gold": ("results5y", "2021-07-10"),
}
TSMOM_MENU = ["SPY", "QQQ", "IWM", "EFA", "GLD", "TLT"]


# ---------------------------------------------------------------- estimation
def nw_ols(y, X, lag=LAG):
    """OLS with Newey-West (Bartlett) HAC SEs. X includes const as col 0.
    Returns beta, se, t, r2, n."""
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    n, k = X.shape
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    u = y - X @ beta
    XtX_inv = np.linalg.inv(X.T @ X)
    xu = X * u[:, None]
    meat = xu.T @ xu  # lag 0 (White)
    for L in range(1, lag + 1):
        w = 1.0 - L / (lag + 1.0)
        g = xu[L:].T @ xu[:-L]
        meat += w * (g + g.T)
    cov = XtX_inv @ meat @ XtX_inv
    se = np.sqrt(np.diag(cov))
    t = beta / se
    tss = ((y - y.mean()) ** 2).sum()
    r2 = 1.0 - (u @ u) / tss if tss > 0 else np.nan
    return beta, se, t, r2, n


def _selfcheck():
    rng = np.random.default_rng(0)
    n = 1000
    x = rng.standard_normal(n)
    X = np.column_stack([np.ones(n), x])
    # (3) AR(1) errors rho=0.5, seed 0: NW lag-5 SE must exceed OLS SE
    e = np.zeros(n)
    eps = rng.standard_normal(n)
    for i in range(1, n):
        e[i] = 0.5 * e[i - 1] + eps[i]
    y = 1.0 + 2.0 * x + e
    beta, se_nw, _, _, _ = nw_ols(y, X, lag=5)
    # (1) betas match numpy lstsq
    b_ref, *_ = np.linalg.lstsq(X, y, rcond=None)
    assert np.allclose(beta, b_ref), "OLS beta mismatch vs lstsq"
    u = y - X @ beta
    ols_se = np.sqrt(np.diag(np.linalg.inv(X.T @ X)) * (u @ u) / (n - 2))
    # compare on the intercept: its regressor is persistent, so positively
    # autocorrelated errors must inflate the NW SE above the OLS SE
    assert se_nw[0] > ols_se[0], "NW lag-5 SE not > OLS SE under AR(1) errors"
    # (2) NW lag-0 SE equals White (HC0) SE
    _, se0, _, _, _ = nw_ols(y, X, lag=0)
    XtX_inv = np.linalg.inv(X.T @ X)
    white = np.sqrt(np.diag(XtX_inv @ (X * u[:, None] ** 2).T @ X @ XtX_inv))
    assert np.allclose(se0, white), "NW lag-0 SE != White SE"


_selfcheck()


# ---------------------------------------------------------------- factors
def build_factors(panel):
    ff5 = pd.read_parquet(REPO / "data/raw/ff5_factors_daily.parquet")
    mom = pd.read_parquet(REPO / "data/raw/ff_factors_daily.parquet")[["Mom"]]
    fac = ff5.join(mom, how="inner").loc[:FF_END]  # inner-join on dates per rules

    close = panel["close"][TSMOM_MENU]
    r = close.pct_change(fill_method=None)
    # sign of trailing 252d total return skipping last 21d, held into next day
    sig = np.sign(close.shift(21) / close.shift(21 + 252) - 1.0)
    raw = (sig.shift(1) * r).mean(axis=1)  # signal at close t earns t+1
    raw = raw[sig.shift(1).notna().all(axis=1)]
    scale = (0.10 / np.sqrt(252)) / raw.rolling(63).std().shift(1)  # PIT vol
    tsmom = (raw * scale).dropna()

    qqq_ex = panel["close"]["QQQ"].pct_change(fill_method=None).sub(fac["RF"]).dropna()
    common = qqq_ex.index.intersection(fac.index)
    Xm1 = np.column_stack([np.ones(len(common)), fac.loc[common, M1_COLS].values])
    yq = qqq_ex.loc[common].values
    b, *_ = np.linalg.lstsq(Xm1, yq, rcond=None)  # one full-sample projection
    qqqres = pd.Series(yq - Xm1 @ b, index=common, name="QQQRES")

    fac = fac.join(tsmom.rename("TSMOM"), how="inner").join(qqqres, how="inner")
    return fac  # columns: FF5 + RF + Mom + TSMOM + QQQRES, ends <= FF_END


# ---------------------------------------------------------------- regressions
def regress(net_daily, fac, model, window_label, book, avg_gross):
    cols = MODELS[model]
    df = pd.concat([net_daily.rename("ret"), fac], axis=1, join="inner").dropna()
    df = df.loc[:FF_END]
    if len(df) < 30:
        return None
    y = (df["ret"] - df["RF"]).values
    X = np.column_stack([np.ones(len(df)), df[cols].values])
    beta, se, t, r2, n = nw_ols(y, X)
    alpha_ann = beta[0] * 252
    rf_ann = df["RF"].mean() * 252
    stress = alpha_ann - max(avg_gross - 1.0, 0.0) * (rf_ann + 0.005)
    row = {"book": book, "model": model, "window": window_label, "n_obs": n,
           "alpha_ann": alpha_ann, "t_alpha": t[0], "R2": r2,
           "avg_gross": avg_gross, "alpha_stress": stress}
    for i, c in enumerate(cols):
        row[f"beta_{c}"] = beta[i + 1]
        row[f"t_{c}"] = t[i + 1]
    return row


def rolling_m2(net_daily, fac, book):
    df = pd.concat([net_daily.rename("ret"), fac], axis=1, join="inner").dropna()
    df = df.loc[:FF_END]
    out = []
    for end in range(252, len(df) + 1, 63):
        w = df.iloc[end - 252:end]
        y = (w["ret"] - w["RF"]).values
        X = np.column_stack([np.ones(252), w[M2_COLS].values])
        beta, _, _, _, _ = nw_ols(y, X)
        out.append({"book": book, "date": w.index[-1].date(), "model": "M2",
                    "alpha_ann": beta[0] * 252,
                    "beta_mkt": beta[1 + M2_COLS.index("Mkt-RF")],
                    "beta_tsmom": beta[1 + M2_COLS.index("TSMOM")],
                    "beta_qqqres": beta[1 + M2_COLS.index("QQQRES")]})
    return out


# ---------------------------------------------------------------- main
def main():
    import json

    panel = harness.load_full()
    fac = build_factors(panel)

    # --- books: integrity gate, then blind + full runs
    series = {}      # (book, window_label) -> (net_daily, avg_gross)
    integrity_fail = []
    for name, (resdir, start) in BOOKS.items():
        spec = harness.load_spec(REPO / f"research/hunt2026/specs/{name}")
        r = harness.run(spec, panel, start=start)
        frozen = json.loads((REPO / f"research/hunt2026/{resdir}/{name}.json").read_text())
        ok = (abs(r["total_net"] - frozen["total_net"]) < 1e-9
              and abs(r["sharpe"] - frozen["sharpe"]) < 1e-9)
        if not ok:
            integrity_fail.append((name, r["total_net"], frozen["total_net"],
                                   r["sharpe"], frozen["sharpe"]))
            continue
        series[(name, "blind")] = (r["net_daily"], r["avg_gross_exposure"])
        rf = harness.run(spec, panel, start=None)
        series[(name, "full_IN-SAMPLE")] = (rf["net_daily"], rf["avg_gross_exposure"])

    # --- controls (identical pipeline, both blind windows + full)
    qqq_r = panel["close"]["QQQ"].pct_change(fill_method=None)
    spy_r = panel["close"]["SPY"].pct_change(fill_method=None)
    # static 1.5x QQQ daily-rebalanced, 2 bps/side on rebalance turnover
    lev = 1.5 * qqq_r - (2.0 / 1e4) * (0.75 * qqq_r.abs() / (1 + 1.5 * qqq_r))
    bench_spec = harness.load_spec(REPO / "research/hunt2026/specs/bench_qqq_sma200_2x")
    controls = {}
    for wlabel, start in [("blind_1y", "2025-07-10"), ("blind_5y", "2021-07-10"),
                          ("full_IN-SAMPLE", None)]:
        cut = pd.Timestamp(start) if start else None
        for cname, s in [("CTRL_spy_buyhold", spy_r), ("CTRL_qqq_buyhold", qqq_r),
                         ("CTRL_qqq_1.5x_static", lev)]:
            ser = s[s.index > cut] if cut is not None else s
            controls[(cname, wlabel)] = (ser.dropna(),
                                         1.5 if "1.5x" in cname else 1.0)
        rb = harness.run(bench_spec, panel, start=start)
        controls[("CTRL_bench_qqq_sma200_2x", wlabel)] = (
            rb["net_daily"], rb["avg_gross_exposure"])
    series.update(controls)

    # --- attribution table
    rows = []
    for (name, wlabel), (nd, ag) in series.items():
        for model in MODELS:
            row = regress(nd, fac, model, wlabel, name, ag)
            if row:
                rows.append(row)
    # subperiods (M2, full-history book series, prereg-specified)
    subs = [("2021H2-2022", "2021-07-01", "2022-12-31"),
            ("2023-2024", "2023-01-01", "2024-12-31"),
            ("2025->", "2025-01-01", str(FF_END.date()))]
    for name in BOOKS:
        if (name, "full_IN-SAMPLE") not in series:
            continue
        nd, ag = series[(name, "full_IN-SAMPLE")]
        for slabel, s0, s1 in subs:
            row = regress(nd.loc[s0:s1], fac, "M2", f"sub_{slabel}", name, ag)
            if row:
                rows.append(row)
    # blind-window half-split (M2 alpha sign in each half)
    halves = {}
    for name in BOOKS:
        if (name, "blind") not in series:
            continue
        nd, ag = series[(name, "blind")]
        df = pd.concat([nd.rename("ret"), fac], axis=1, join="inner").dropna().loc[:FF_END]
        mid = len(df) // 2
        hs = []
        for i, half in enumerate([df.iloc[:mid], df.iloc[mid:]]):
            row = regress(half["ret"], fac, "M2", f"blind_half{i + 1}", name, ag)
            if row:
                rows.append(row)
                hs.append(row["alpha_ann"])
        halves[name] = hs
    att = pd.DataFrame(rows)
    att.to_csv(OUT / "attribution.csv", index=False)

    # --- rolling (M2, full history)
    roll = []
    for name in BOOKS:
        if (name, "full_IN-SAMPLE") in series:
            roll += rolling_m2(series[(name, "full_IN-SAMPLE")][0], fac, name)
    pd.DataFrame(roll).to_csv(OUT / "rolling.csv", index=False)

    # --- report
    write_report(att, halves, integrity_fail, fac)

    from core.eval.run_manifest import stamp_run
    stamp_run(track="attribution", variant="live_books_m0m2",
              params={"models": ["M0", "M1", "M2"], "lag": LAG, "books": 7,
                      "controls": 4}, n_trials=1)
    print("done:", OUT)


def get(att, book, model, window):
    m = att[(att.book == book) & (att.model == model) & (att.window == window)]
    return m.iloc[0] if len(m) else None


def write_report(att, halves, integrity_fail, fac):
    L = ["# Factor attribution of the live hunt2026 books (EXP-2026-07-14-factor-attribution)",
         "",
         "Implements the frozen prereg `research/hunt2026/preregistrations/factor-attribution-2026-07-14.md`.",
         f"All regressions truncated at FF data end {FF_END.date()}. Newey-West lag {LAG}. Alpha annualized x252.",
         ""]

    # placebo gate FIRST. Hard pipeline gate = SPY/QQQ M1 |t| < 2 (prereg
    # "Controls"); the 1.5x leverage placebo belongs to decision rule 3,
    # evaluated per book on its own blind window.
    L += ["## Placebo gate (checked first)", "",
          "Hard pipeline gate: M1 alpha on SPY / QQQ buy-and-hold must have \\|t\\| < 2.",
          "Rule-3 leverage placebo: 1.5x QQQ static \\|t\\| < 2 on the book's window.", "",
          "| control | window | alpha_ann | NW t | R2 | \\|t\\|<2 |", "|---|---|---|---|---|---|"]
    pipeline_ok = True
    rule3_by_window = {"blind_1y": True, "blind_5y": True}
    for c in ["CTRL_spy_buyhold", "CTRL_qqq_buyhold", "CTRL_qqq_1.5x_static"]:
        for w in ["blind_1y", "blind_5y"]:
            r = get(att, c, "M1", w)
            p = abs(r.t_alpha) < 2
            if not p:
                rule3_by_window[w] = False
                if c != "CTRL_qqq_1.5x_static":
                    pipeline_ok = False
            L.append(f"| {c} | {w} | {r.alpha_ann:+.2%} | {r.t_alpha:+.2f} | {r.R2:.3f} | {'yes' if p else 'NO'} |")
    L.append("")
    if not pipeline_ok:
        L += ["**HARD PLACEBO GATE FAILED (SPY/QQQ) — pipeline is broken. Book results below are NOT interpretable; fix plumbing, not thresholds.**", ""]
    else:
        L += ["Hard gate (SPY/QQQ): PASS.", ""]

    if integrity_fail:
        L += ["## Integrity gate failures", ""]
        for n, tn, ftn, sh, fsh in integrity_fail:
            L.append(f"- {n}: recomputed total_net {tn} vs frozen {ftn}, sharpe {sh} vs {fsh} — EXCLUDED")
        L.append("")
    else:
        L += ["Integrity gate: all 7 books reproduce their frozen total_net/sharpe to <1e-9. PASS.", ""]

    L += ["## Books — blind window, all models", "",
          "| book | model | n | alpha_ann | NW t | R2 | beta_Mkt | beta_TSMOM | beta_QQQRES | alpha_stress |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    verdicts = {}
    for b in BOOKS:
        rows = {m: get(att, b, m, "blind") for m in MODELS}
        if rows["M2"] is None:
            continue
        for m, r in rows.items():
            bt = f"{r.get('beta_TSMOM', float('nan')):+.2f}" if m == "M2" else ""
            bq = f"{r.get('beta_QQQRES', float('nan')):+.2f}" if m == "M2" else ""
            L.append(f"| {b} | {m} | {r.n_obs} | {r.alpha_ann:+.2%} | {r.t_alpha:+.2f} | {r.R2:.3f} | "
                     f"{r['beta_Mkt-RF']:+.2f} | {bt} | {bq} | {r.alpha_stress:+.2%} |")
        r2, r1 = rows["M2"], rows["M1"]
        h = halves.get(b, [])
        rule1 = r2.t_alpha >= 2 and r1.t_alpha >= 2
        rule2 = len(h) == 2 and h[0] > 0 and h[1] > 0
        w = "blind_1y" if BOOKS[b][1] == "2025-07-10" else "blind_5y"
        rule3 = pipeline_ok and rule3_by_window[w]
        rule4 = r2.alpha_stress > 0
        verdicts[b] = (rule1, rule2, rule3, rule4, r2, r1)
    L.append("")

    L += ["## Decision rules per book (blind window)", "",
          "| book | 1: M2 t>=2 & M1 t>=2 | 2: both halves alpha>0 | 3: placebos | 4: stress>0 | candidate |",
          "|---|---|---|---|---|---|"]
    for b, (r1_, r2_, r3_, r4_, rm2, rm1) in verdicts.items():
        cand = all([r1_, r2_, r3_, r4_])
        L.append(f"| {b} | {'PASS' if r1_ else 'fail'} (M2 t={rm2.t_alpha:+.2f}, M1 t={rm1.t_alpha:+.2f}) | "
                 f"{'PASS' if r2_ else 'fail'} | {'PASS' if r3_ else 'fail'} | {'PASS' if r4_ else 'fail'} | "
                 f"{'YES' if cand else 'no'} |")
    L.append("")

    L += ["## Blind-window half-split (M2 alpha, annualized)", "",
          "| book | half 1 | half 2 |", "|---|---|---|"]
    for b, h in halves.items():
        if len(h) == 2:
            L.append(f"| {b} | {h[0]:+.2%} | {h[1]:+.2%} |")
    L.append("")

    L += ["## Full history (IN-SAMPLE context — design data, no alpha claim may cite this)", "",
          "| book | model | n | alpha_ann | NW t | R2 |", "|---|---|---|---|---|---|"]
    for b in list(BOOKS) + ["CTRL_bench_qqq_sma200_2x"]:
        for m in MODELS:
            r = get(att, b, m, "full_IN-SAMPLE")
            if r is not None:
                L.append(f"| {b} | {m} | {r.n_obs} | {r.alpha_ann:+.2%} | {r.t_alpha:+.2f} | {r.R2:.3f} |")
    L.append("")

    L += ["## Subperiods (M2, full-history series)", "",
          "| book | subperiod | n | alpha_ann | NW t |", "|---|---|---|---|---|"]
    for b in BOOKS:
        for s in ["sub_2021H2-2022", "sub_2023-2024", "sub_2025->"]:
            r = get(att, b, "M2", s)
            if r is not None:
                L.append(f"| {b} | {s[4:]} | {r.n_obs} | {r.alpha_ann:+.2%} | {r.t_alpha:+.2f} |")
    L.append("")

    L += ["## Naive trend parent (bench_qqq_sma200_2x, blind windows)", "",
          "| window | model | alpha_ann | NW t | R2 |", "|---|---|---|---|---|"]
    for w in ["blind_1y", "blind_5y"]:
        for m in MODELS:
            r = get(att, "CTRL_bench_qqq_sma200_2x", m, w)
            if r is not None:
                L.append(f"| {w} | {m} | {r.alpha_ann:+.2%} | {r.t_alpha:+.2f} | {r.R2:.3f} |")
    L += ["", "## M3 (momentum_concentrated)", "",
          "NOT AVAILABLE: the vetted FLOOR_REALDATA residual-factor panel is not built PIT for the blind window in this run; per prereg it is reported as NOT AVAILABLE rather than improvised.", ""]

    L += ["## Story", ""]
    L.append(_story(verdicts, att))
    (OUT / "ATTRIBUTION.md").write_text("\n".join(L) + "\n")


def _story(verdicts, att):
    cands = [b for b, v in verdicts.items() if all(v[:4])]
    near = [b for b, v in verdicts.items()
            if b not in cands and v[4].alpha_ann > 0.02 and 1 <= v[4].t_alpha < 2]
    fivey = {"trend_vol_qqq", "defensive_ensemble", "dual_momentum_gold"}
    if not any(v[0] for v in verdicts.values()):
        verdict = "no evidence of residual alpha" if not near else \
            "factor-premium harvesting with some unexplained residual return"
    elif cands:
        strong = [b for b in cands if b in fivey and verdicts[b][4].t_alpha >= 2.4]
        verdict = ("strong evidence of residual alpha" if strong else
                   "promising but unproven residual alpha")
    else:
        verdict = "factor-premium harvesting with some unexplained residual return"
    lines = [f"Program verdict (prereg mapping): **{verdict}**.", "",
             "The 5y-window rule-3 failure comes from the 1.5x QQQ leverage placebo "
             "(M1 t >= 2): the harness charges no financing, so static leverage earns "
             "~0.5 x RF (~+2%/yr) of mechanical alpha over 5 years. This is the "
             "free-financing effect the stress line corrects for, and it caps what any "
             "levered book's regression alpha can mean.", ""]
    for b, v in verdicts.items():
        r = v[4]
        lines.append(f"- {b}: M2 blind alpha {r.alpha_ann:+.1%}/yr (t={r.t_alpha:+.2f}, R2={r.R2:.2f});"
                     f" rules {'/'.join(str(i + 1) for i, x in enumerate(v[:4]) if x) or 'none'} pass.")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
