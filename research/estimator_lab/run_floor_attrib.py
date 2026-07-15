"""Stage 2: alpha-book attribution vs known / sector-mean / vetted-residual risk.

Frozen prereg: FLOOR_ATTRIB_MEMO.md rev 2. 14 Stage-1 primary windows (starts
2022-11-21..2026-03-02, ending 2026-05-29). Per book x window: L1 raw mean -> L2 +FF4
-> L3 +11 Stage-1 sector-mean series -> L4 +label-4 x_j (4/14 windows only; L4:=L3
elsewhere; rule 4 known-unreachable). Significance: joint sign-flip permutation
(10k draws, shared across books). alpha_stress financing haircut on every alpha.
DSR at n_trials 18 AND 36. SVXY pooled-residual VRP override. Controls split:
plumbing vs uninformative. Selection-tainted history; live OOS excluded.
"""
import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "research/hunt2026"))
from core.eval.metrics import deflated_sharpe  # noqa: E402
from core.eval.run_manifest import stamp_run  # noqa: E402
import harness  # noqa: E402
from run_floor_industry import KP, build_windows, pca, residualize  # noqa: E402

ROOT = HERE.parents[1]
BOOKS = ["defensive_ensemble", "dual_momentum_gem", "dual_momentum_gold",
         "momentum_concentrated", "trend_vol_qqq", "vol_core_svxy", "vol_managed_qqq"]
PROVENANCE = {
    "vol_managed_qqq": "promoted L3; hunt-1",
    "vol_core_svxy": "promoted L3; hunt-1; SVXY ETP-menu survivorship",
    "trend_vol_qqq": "promoted L3; hunt-2 ADAPTIVE",
    "defensive_ensemble": "promoted L3; hunt-2 ADAPTIVE",
    "momentum_concentrated": "sleeve-only; WF-demoted F-015; stock book (survivorship-heavy)",
    "dual_momentum_gem": "watch; whipsaw-fragile",
    "dual_momentum_gold": "watch; HINDSIGHT-DISCOUNTED (regime artifact)",
}
N_PERM, PERM_SEED = 10_000, 7
P_SIG, SIGN_FRAC, RHO_VRP = 0.05, 0.60, 0.5
STRESS_SPREAD = 0.005                                     # +50bps/yr over RF


def alphas_for(nd, rf, win_env):
    """Per-window L1..L4 alphas + L3 residuals for one return series."""
    per = {1: [], 2: [], 3: [], 4: []}
    resid3, conds = [], []
    for e in win_env:
        r = nd.reindex(e["dates"])
        assert r.notna().all() and rf.reindex(e["dates"]).notna().all(), \
            f"invalid window {e['d0']}"
        rex = (r - rf.reindex(e["dates"])).values
        fa, sec, vet = e["fa"], e["sec"], e["vet"]
        per[1].append(float(rex.mean()))
        X2 = np.column_stack([np.ones(63), fa])
        X3 = np.column_stack([X2, sec])
        X4 = np.column_stack([X3, vet]) if e["n_l4"] else X3
        b2, *_ = np.linalg.lstsq(X2, rex, rcond=None)
        b3, *_ = np.linalg.lstsq(X3, rex, rcond=None)
        b4, *_ = np.linalg.lstsq(X4, rex, rcond=None)
        per[2].append(float(b2[0]))
        per[3].append(float(b3[0]))
        per[4].append(float(b4[0]))
        resid3.append(rex - X3 @ b3)
        conds.append(float(np.linalg.cond(X3)))
    return {k: np.array(v) for k, v in per.items()}, resid3, conds


def perm_stats(a, signs):
    null = (signs * a[None, :]).mean(axis=1)
    p = float((np.abs(null) >= abs(a.mean())).mean())
    sign = float(max((a > 0).mean(), (a < 0).mean()))
    return dict(mean=float(a.mean()), p=p, sign=sign,
                t=float(a.mean() / (a.std(ddof=1) / np.sqrt(len(a)))),
                thr95=float(np.quantile(np.abs(null), 0.95)))


def sig(g):
    return g["p"] <= P_SIG and g["sign"] >= SIGN_FRAC


def main():
    wins = build_windows()
    lab = pd.read_csv(HERE / "floor_industry.csv")
    ff = pd.read_parquet(ROOT / "data/raw/ff_factors_daily.parquet")
    px = pd.read_parquet(ROOT / "data/raw/daily_px_statarb_wide.parquet")
    px.index = pd.to_datetime(px.index)
    ret_dates = px.pct_change(fill_method=None).iloc[1:].index.intersection(ff.index)

    win_env = []
    for w in wins:
        n0 = list(ret_dates).index(pd.Timestamp(w["d0"]))
        dts = ret_dates[n0:n0 + 63]
        l4 = lab[(lab.arm == "B") & (lab.window == w["d0"])
                 & (lab.label == "detectable-candidate-residual-risk")].pc.values
        Yr, _, _, _ = residualize(w, "B")
        _, _, X, _ = pca(Yr, KP)
        vet = X[[j - 1 for j in l4]].T if len(l4) else np.empty((63, 0))
        win_env.append(dict(d0=w["d0"], dates=dts, fa=w["fa"], sec=w["sec_ret"],
                            vet=vet, n_l4=len(l4)))
    n_l4_wins = sum(1 for e in win_env if e["n_l4"])
    panel = harness.load_full()
    rf = ff["RF"]
    spy_px = panel["close"]["SPY"]
    spy_vol = np.array([spy_px.pct_change().reindex(e["dates"]).std()
                        for e in win_env])
    vol_med = np.nanmedian(spy_vol)
    hi_vol = spy_vol >= vol_med
    half1 = np.arange(len(win_env)) < len(win_env) // 2
    svxy = panel["close"]["SVXY"].pct_change()
    all_dates = pd.DatetimeIndex(np.concatenate([e["dates"] for e in win_env]))
    svxy_ex = (svxy.reindex(all_dates) - rf.reindex(all_dates)).values
    assert not np.isnan(svxy_ex).any(), "SVXY missing on window dates"
    rf_ann = float(rf.reindex(all_dates).mean() * 252)

    runs = {b: harness.run(harness.load_spec(str(ROOT / "research/hunt2026/specs" / b)),
                           panel) for b in BOOKS + ["bench_qqq_buyhold"]}
    runs["_spy_null"] = harness.spy_benchmark(panel)

    rng = np.random.default_rng(PERM_SEED)
    signs = rng.choice([-1.0, 1.0], size=(N_PERM, len(win_env)))

    rows, cls, book_a4 = [], {}, {}
    for name, res in runs.items():
        nd = res["net_daily"]
        per, resid3, conds = alphas_for(nd, rf, win_env)
        G = {k: perm_stats(per[k], signs) for k in per}
        book_a4[name] = per[4]
        rho = float(np.corrcoef(np.concatenate(resid3), svxy_ex)[0, 1])
        h1m, h2m = per[4][half1].mean(), per[4][~half1].mean()
        same_halves = np.sign(h1m) == np.sign(h2m)
        wr = nd.reindex(all_dates)
        dsr18 = deflated_sharpe(wr, n_trials=18, periods_per_year=252)
        dsr36 = deflated_sharpe(wr, n_trials=36, periods_per_year=252)
        gross = res["avg_gross_exposure"]
        stress_haircut = max(gross - 1, 0) * (rf_ann + STRESS_SPREAD)
        a4_ann = G[4]["mean"] * 252
        a4_stress = a4_ann - stress_haircut
        if abs(G[1]["t"]) < 1:
            c = "insufficient-evidence"
        elif abs(rho) >= RHO_VRP:
            c = "known-premium-VRP" + (" (long-vol)" if rho <= -RHO_VRP else "")
        elif sig(G[1]) and not sig(G[2]):
            c = "known-factor-premium"
        elif sig(G[2]) and not sig(G[3]):
            c = "industry-sector-exposure"
        elif sig(G[3]) and not sig(G[4]) and n_l4_wins >= 7:
            c = "hidden-residual-risk-exposure"        # unreachable with this panel
        elif sig(G[4]) and same_halves and dsr18 >= 0.5 and dsr36 >= 0.5 \
                and a4_stress > 0:
            c = "promising-but-unproven-residual-alpha"
        else:
            c = "insufficient-evidence"
        cls[name] = c
        suppression = (not sig(G[2])) and sig(G[3])
        rows.append({
            "book": name, "class": c, "provenance": PROVENANCE.get(name, "control"),
            **{f"L{k}_ann": round(G[k]["mean"] * 252, 4) for k in per},
            **{f"L{k}_p": round(G[k]["p"], 4) for k in per},
            "L2_t": round(G[2]["t"], 2), "L4_sign": round(G[4]["sign"], 2),
            "a4_stress_ann": round(a4_stress, 4),
            "rho_svxy": round(rho, 3),
            "half1_L4_ann": round(h1m * 252, 4), "half2_L4_ann": round(h2m * 252, 4),
            "hivol_L4_ann": round(per[4][hi_vol].mean() * 252, 4),
            "lovol_L4_ann": round(per[4][~hi_vol].mean() * 252, 4),
            "dsr18": round(dsr18, 3), "dsr36": round(dsr36, 3),
            "gross": round(gross, 2), "turnover": round(res["avg_daily_turnover"], 4),
            "cost_drag_ann": round(res["cost_drag_ann"], 4),
            "max_dd": round(res["max_dd"], 3),
            "cond_med": round(float(np.median(conds)), 1),
            "suppression_path": bool(suppression),
            "thr95_L4_ann": round(G[4]["thr95"] * 252, 4)})
    df = pd.DataFrame(rows)

    # expected false rule-5 count under the joint null (DSR/stress omitted -> upper bound)
    false5 = np.zeros(N_PERM)
    for name in BOOKS:
        a = book_a4[name]
        thr = np.quantile(np.abs((signs * a[None, :]).mean(axis=1)), 1 - P_SIG)
        null_m = (signs * a[None, :]).mean(axis=1)
        fs = np.abs(null_m) >= thr
        flipped = signs * a[None, :]
        sgn = np.maximum((flipped > 0).mean(axis=1), (flipped < 0).mean(axis=1)) >= SIGN_FRAC
        h1 = flipped[:, half1].mean(axis=1)
        h2 = flipped[:, ~half1].mean(axis=1)
        false5 += (fs & sgn & (np.sign(h1) == np.sign(h2))).astype(float)
    exp_false5 = float(false5.mean())

    bench = df[df.book == "bench_qqq_buyhold"].iloc[0]
    bench_G1_t = perm_stats(alphas_for(runs["bench_qqq_buyhold"]["net_daily"], rf,
                                       win_env)[0][1], signs)["t"]
    # plumbing asserts on the benchmark
    betas, r2s = [], []
    for e in win_env:
        r = runs["bench_qqq_buyhold"]["net_daily"].reindex(e["dates"])
        rex = (r - rf.reindex(e["dates"])).values
        X2 = np.column_stack([np.ones(63), e["fa"]])
        b, *_ = np.linalg.lstsq(X2, rex, rcond=None)
        fit = X2 @ b
        betas.append(b[1])
        r2s.append(1 - ((rex - fit) ** 2).sum() / ((rex - rex.mean()) ** 2).sum())
    plumbing = (abs(bench.L2_t) < 2 and 0.9 <= np.median(betas) <= 1.2
                and np.median(r2s) >= 0.9)
    uninformative = abs(bench_G1_t) < 1
    spy_ok = cls["_spy_null"].startswith(("insufficient", "known-"))
    if not plumbing or not spy_ok:
        verdict = "FAIL"
    elif uninformative:
        verdict = "AMBIGUOUS-CONTROL"
    else:
        verdict = "SUCCESS"
    df.to_csv(HERE / "floor_attrib.csv", index=False)
    write_report(df, verdict, plumbing, spy_ok, np.median(betas), np.median(r2s),
                 exp_false5, n_l4_wins)
    spec_hash = {b: hashlib.sha256(b"".join(
        sorted(f.read_bytes() for f in (ROOT / "research/hunt2026/specs" / b).rglob("*")
               if f.is_file()))).hexdigest()[:16] for b in BOOKS + ["bench_qqq_buyhold"]}
    stamp_run(track="estimator_lab", variant="floor_attrib",
              params={"books": BOOKS, "perm_seed": PERM_SEED, "n_perm": N_PERM,
                      "p_sig": P_SIG, "sign_frac": SIGN_FRAC, "rho_vrp": RHO_VRP,
                      "verdict": verdict, "exp_false_rule5": round(exp_false5, 3),
                      "l4_slots": [(e["d0"], int(e["n_l4"])) for e in win_env
                                   if e["n_l4"]],
                      "spec_sha256": spec_hash,
                      "input_sha256": {f: hashlib.sha256(
                          (ROOT / f).read_bytes()).hexdigest()[:16]
                          for f in ["data/raw/ff_factors_daily.parquet",
                                    "data/raw/daily_px_statarb_wide.parquet",
                                    "data/raw/sp500_pit.parquet",
                                    "data/raw/sp_composite_named.parquet",
                                    "research/estimator_lab/floor_industry.csv",
                                    "research/hunt2026/sandbox_meta.json"]},
                      "memo": "FLOOR_ATTRIB_MEMO.md#rev2"},
              n_trials=18)


def write_report(df, verdict, plumbing, spy_ok, beta_med, r2_med, exp_false5, n_l4):
    lines = ["# Stage 2 — alpha-book attribution (known / sector-mean / vetted residual)", "",
             "Prereg: FLOOR_ATTRIB_MEMO.md rev 2 (frozen). 14 primary windows, starts "
             "2022-11-21 → 2026-03-02. Alphas per window, sign-flip permutation "
             "(10k joint draws). SELECTION-TAINTED history (n_trials ≥ 18, floor); "
             "live OOS excluded; 'industry' = 11-GICS-sector-MEAN controls; "
             f"residual controls in {n_l4}/14 windows — SPOT-CHECKS, not robustness; "
             "L4 survival is NOT evidence of absence of residual common risk.", "",
             f"## Verdict (pre-committed): **{verdict}**",
             f"- plumbing (bench beta {beta_med:.2f}, R² {r2_med:.2f}, |t₂| gate): "
             f"{'PASS' if plumbing else 'FAIL'}",
             f"- SPY null book benign: {'PASS' if spy_ok else 'FAIL'}",
             f"- expected false rule-5 count under joint null (upper bound, DSR/stress "
             f"omitted): {exp_false5:.2f} of 7", "",
             "## Attribution (annualized window-mean alphas; permutation p)", "",
             "| book | class | L1 | L2 +FF | L3 +sec | L4 +res | α₄ stress | ρSVXY | DSR18/36 | gross | maxDD |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in df.iterrows():
        lines.append(
            f"| {r.book} | {r['class']} | {r.L1_ann:+.1%} ({r.L1_p:.2f}) "
            f"| {r.L2_ann:+.1%} ({r.L2_p:.2f}) | {r.L3_ann:+.1%} ({r.L3_p:.2f}) "
            f"| {r.L4_ann:+.1%} ({r.L4_p:.2f}) | {r.a4_stress_ann:+.1%} "
            f"| {r.rho_svxy:+.2f} | {r.dsr18:.2f}/{r.dsr36:.2f} "
            f"| {r.gross:.2f} | {r.max_dd:.0%} |")
    lines += ["", "## Stability (L4 ann.)", "",
              "| book | half1 | half2 | hi-vol | lo-vol | sign-frac | suppression |",
              "|---|---|---|---|---|---|---|"]
    for _, r in df.iterrows():
        lines.append(f"| {r.book} | {r.half1_L4_ann:+.1%} | {r.half2_L4_ann:+.1%} "
                     f"| {r.hivol_L4_ann:+.1%} | {r.lovol_L4_ann:+.1%} "
                     f"| {r.L4_sign:.2f} | {'⚠' if r.suppression_path else '—'} |")
    lines += ["", "## Provenance", ""]
    for _, r in df.iterrows():
        lines.append(f"- {r.book}: {r.provenance}")
    lines += ["", "## Story", "", "(appended post-run)", ""]
    (HERE / "FLOOR_ATTRIB.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
