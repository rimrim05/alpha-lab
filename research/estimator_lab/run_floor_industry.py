"""Phase 7: FF+industry known-model arm: vetted residual-factor panel for Stage 2.

Frozen prereg: FLOOR_INDUSTRY_MEMO.md (rev 2). Two arms per primary window:
A = FF3+MOM cross-sectional projection (Phase 6 rerun under the empirical screen);
B = FF3+MOM + 11 GICS sector dummies. Empirical per-rank shuffled-null screen (q99,
280 panels/arm), circular-shift nulls pooled per rank (868 draws) for D/D'/sectorR2/
a_match, per-window p/n floor rule, labels 1-5 first-match-wins.
Outputs: floor_industry.csv (per slot), FLOOR_INDUSTRY.md (report).
"""
import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))
from core.eval.run_manifest import stamp_run  # noqa: E402
from run_floor_realdata import edge_cut  # noqa: E402

ROOT = HERE.parents[1]
N_AN, N_BETA, KP, KMATCH, K_F = 63, 252, 5, 7, 4
COV_MIN, ZERO_MAX = 0.90, 0.20
N_SHUF, BASE_SEED = 50, {"A": 100, "B": 200}
HELDOUT_SEEDS = [300, 301, 302, 303, 304]
L_CUT, L_SENS = 0.50, [0.25, 0.30, 0.40, 0.50]
FACTORS = ["Mkt-RF", "SMB", "HML", "Mom"]
GICS_RESTRUCTURE = "2023-03-17"
INPUTS = ["data/raw/daily_px_statarb_wide.parquet", "data/raw/ff_factors_daily.parquet",
          "data/raw/sp500_pit.parquet", "data/raw/sp_composite_named.parquet"]


def pca(Y, k):
    p, n = Y.shape
    W = Y.T @ Y / (n * p)
    w, V = np.linalg.eigh(W)
    w, V = w[::-1], V[:, ::-1]
    theta, ell = w[:k], w[k:].mean()
    X = (Y @ V[:, :k] / np.sqrt(n * p * theta)).T @ Y
    H = Y @ V[:, :k] / np.sqrt(n * p * theta)
    return theta, ell, X, H


def r2(X, F):
    """Centered R2 of each row of X on columns of F (n x q). lstsq, clipped."""
    Xc = (X - X.mean(axis=1, keepdims=True)).T             # n x j
    Fc = np.column_stack([np.ones(F.shape[0]), F])
    beta, *_ = np.linalg.lstsq(Fc, Xc, rcond=None)
    resid = Xc - Fc @ beta
    tot = (Xc ** 2).sum(axis=0) - Xc.shape[0] * 0          # Xc already centered
    out = 1.0 - (resid ** 2).sum(axis=0) / (Xc ** 2).sum(axis=0)
    return np.clip(out, 0.0, 1.0)


def shift_scores(x, F):
    """R2 of all 62 circular shifts of x (1d, n) on F."""
    n = len(x)
    S = np.array([np.roll(x, s) for s in range(1, n)])
    return r2(S, F)


def loc_score(X):
    x2 = X ** 2
    return x2.max(axis=1) / x2.sum(axis=1)


def build_windows():
    px = pd.read_parquet(ROOT / INPUTS[0])
    px.index = pd.to_datetime(px.index)
    ff = pd.read_parquet(ROOT / INPUTS[1])
    pit = pd.read_parquet(ROOT / INPUTS[2])
    sec = pd.read_parquet(ROOT / INPUTS[3])
    smap = dict(zip(sec.ticker, sec.sector))
    ret = px.pct_change(fill_method=None).iloc[1:]
    dates = ret.index.intersection(ff.index)
    ret, ff = ret.loc[dates], ff.loc[dates]
    bounds, end = [], len(dates)
    while end - N_AN - N_BETA >= 0:
        bounds.append((end - N_AN - N_BETA, end - N_AN, end))
        end -= N_AN
    ref = pd.read_csv(HERE / "floor_realdata.csv").groupby("window").first()
    wins = []
    for b0, a0, a1 in bounds[::-1]:
        d0 = str(dates[a0].date())
        snap = pit[pit.date <= dates[a0]].iloc[-1]
        members = [m for m in snap.members if m in ret.columns]
        blk = ret.iloc[b0:a1][members]
        bwin, awin = blk.iloc[:N_BETA], blk.iloc[N_BETA:]
        ok = (bwin.notna().all() & (bwin.std() > 0) & ((bwin == 0).mean() <= ZERO_MAX)
              & awin.notna().all() & (awin.std() > 0) & ((awin == 0).mean() <= ZERO_MAX))
        names = list(blk.columns[ok])
        cov = len(names) / len(snap.members)
        if cov < COV_MIN:
            continue
        uh = hashlib.sha256(",".join(names).encode()).hexdigest()[:12]
        assert uh == ref.loc[d0, "univ_hash"], f"universe mismatch {d0}"
        f = ff.iloc[b0:a1]
        rex = blk[names].sub(f["RF"], axis=0)
        rex = rex / rex.iloc[:N_BETA].std()
        fb, fa = f.iloc[:N_BETA][FACTORS].values, f.iloc[N_BETA:][FACTORS].values
        Xb = np.column_stack([np.ones(N_BETA), fb])
        coef, *_ = np.linalg.lstsq(Xb, rex.iloc[:N_BETA].values, rcond=None)
        B = coef[1:].T
        sectors = sorted({smap[m] for m in names})
        S = np.array([[1.0 if smap[m] == s else 0.0 for s in sectors] for m in names])
        Ya = rex.iloc[N_BETA:].values.T                    # p x n, standardized excess
        sec_ret = np.stack([Ya[S[:, k] == 1].mean(axis=0) for k in range(len(sectors))],
                           axis=1)                         # n x 11, PRE-residualization
        sec_cnt = S.sum(axis=0).astype(int)
        wins.append(dict(d0=d0, names=names, uh=uh, cov=cov, B=B, S=S, Ya=Ya,
                         fa=fa, sec_ret=sec_ret, sec_cnt=sec_cnt,
                         pre_gics=d0 < GICS_RESTRUCTURE))
    return wins


def residualize(w, arm):
    M = w["B"] if arm == "A" else np.column_stack([w["B"], w["S"]])
    Q, R = np.linalg.qr(M)
    rank = int((np.abs(np.diag(R)) > 1e-10 * np.abs(R[0, 0])).sum())
    cond = float(np.linalg.cond(M))
    Yr = w["Ya"] - Q @ (Q.T @ w["Ya"])
    fhat = np.linalg.lstsq(M, w["Ya"], rcond=None)[0].T    # n x q implied factor returns
    return Yr, fhat, rank, cond


def shuffled_snr(wins, arm, base_seed, n_shuf):
    """Per-window shuffled SNR-hat arrays (n_shuf x KP)."""
    out = []
    for wi, w in enumerate(wins):
        Yr, _, _, _ = residualize(w, arm)
        rng = np.random.default_rng(base_seed * 1000 + wi)
        rows = []
        for _ in range(n_shuf):
            sh = np.array([r[rng.permutation(N_AN)] for r in Yr])
            theta, ell, Xs, _ = pca(sh, KP)
            rows.append(np.concatenate([theta / ell - 1.0, loc_score(Xs)]))
        out.append(np.array(rows))
    return out                                             # list of (n_shuf, 2*KP)


def main():
    wins = build_windows()
    nw = len(wins)
    arms = {}
    for arm in ("A", "B"):
        arms[arm] = [residualize(w, arm) for w in wins]
        for w, (_, _, rank, cond) in zip(wins, arms[arm]):
            if arm == "B":
                exp_rank = K_F + w["S"].shape[1]
                assert rank == exp_rank, f"rank {rank} != {exp_rank} at {w['d0']}"
    # screen nulls
    shuf = {arm: shuffled_snr(wins, arm, BASE_SEED[arm], N_SHUF) for arm in ("A", "B")}
    q99 = {arm: np.quantile(np.vstack(shuf[arm])[:, :KP], 0.99, axis=0)
           for arm in ("A", "B")}
    shuf_L = {arm: np.vstack(shuf[arm])[:, KP:] for arm in ("A", "B")}
    # held-out calibration (arm B screen, pooled + per-rank)
    ho = np.vstack([np.vstack(shuffled_snr(wins, "B", s, 4)) for s in HELDOUT_SEEDS])
    ho_exc = (ho[:, :KP] > q99["B"][None, :])
    # per-window pipelines
    rows, null_pool = [], {("A" if a else "B", sc, r): [] for a in (0, 1)
                           for sc in ("D", "Dp", "sec", "am") for r in range(KMATCH)}
    per_win = []
    for wi, w in enumerate(wins):
        rec = {}
        for arm in ("A", "B"):
            Yr, fhat, rank, cond = arms[arm][wi]
            # stats ALWAYS at k=KP so SNR/floor match the k=KP shuffled null
            # (bug fixed post-adversarial: k=KMATCH ell inflated arm-B SNR ~6%)
            theta, ell, X, H = pca(Yr, KP)
            if arm == "B":
                _, _, X7, _ = pca(Yr, KMATCH)
            snr = theta / ell - 1.0
            floor_raw = ell / theta
            p = Yr.shape[0]
            pn_ok = p / N_AN >= 7
            floor_rep = floor_raw + (0.5 * N_AN / p if pn_ok else 0.0)
            reg = w["fa"] if arm == "A" else np.column_stack([w["fa"], w["sec_ret"]])
            D = r2(X[:KP], reg)
            Dp = r2(X[:KP], fhat)
            sec = r2(X[:KP], w["sec_ret"])
            L = loc_score(X[:KP])
            exact_p = np.zeros(KP)
            for j in range(KP):
                nul_D = shift_scores(X[j], reg)
                nul_Dp = shift_scores(X[j], fhat)
                nul_sec = shift_scores(X[j], w["sec_ret"])
                null_pool[(arm, "D", j)].append(nul_D)
                null_pool[(arm, "Dp", j)].append(nul_Dp)
                null_pool[(arm, "sec", j)].append(nul_sec)
                exact_p[j] = (1 + (nul_D >= D[j]).sum()) / (1 + len(nul_D))
            rec[arm] = dict(snr=snr, floor_raw=floor_raw, floor_rep=floor_rep,
                            pn_ok=pn_ok, D=D, Dp=Dp, sec=sec, L=L, X=X, H=H,
                            exact_p=exact_p, cond=cond,
                            shuf_max=float(shuf[arm][wi][:, :KP].max()))
            if arm == "B":
                rec[arm]["X7"] = X7
        # a_match: arm-A slots vs arm-B top-7 series
        am = r2(rec["A"]["X"][:KP], rec["B"]["X7"].T)
        for j in range(KP):
            null_pool[("A", "am", j)].append(shift_scores(rec["A"]["X"][j],
                                                          rec["B"]["X7"].T))
        rec["am"] = am
        per_win.append(rec)
    # pooled per-rank null quantiles
    NQ = {}
    for (arm, sc, r), vals in null_pool.items():
        if vals:
            v = np.concatenate(vals)
            NQ[(arm, sc, r)] = {q: float(np.quantile(v, q)) for q in (0.75, 0.95, 0.99)}
    # labels
    for wi, (w, rec) in enumerate(zip(wins, per_win)):
        for arm in ("A", "B"):
            r_ = rec[arm]
            for j in range(KP):
                det = bool(r_["snr"][j] > q99[arm][j])
                D, Dp, sec, L = r_["D"][j], r_["Dp"][j], r_["sec"][j], r_["L"][j]
                disap = (arm == "A" and det
                         and rec["am"][j] < NQ[("A", "am", j)][0.95]
                         and sec >= NQ[("A", "sec", j)][0.99])
                if not det:
                    lab = "noise-like"
                elif disap:
                    lab = "explained-by-industry-or-known"
                elif D >= NQ[(arm, "D", j)][0.99]:
                    lab = "high-known-association"
                elif (D < NQ[(arm, "D", j)][0.75] and Dp < NQ[(arm, "Dp", j)][0.99]
                      and L <= L_CUT):
                    lab = "detectable-candidate-residual-risk"
                else:
                    lab = "mixed-uncertain"
                rows.append({
                    "window": w["d0"], "arm": arm, "pc": j + 1, "p": len(w["names"]),
                    "coverage": round(w["cov"], 3), "univ_hash": w["uh"],
                    "pre_gics_restructure": w["pre_gics"],
                    "snrhat": round(float(r_["snr"][j]), 4),
                    "screen_q99": round(float(q99[arm][j]), 4),
                    "c4_flag": bool(r_["snr"][j] > edge_cut(len(w["names"]), N_AN)),
                    "win_shuf_max": round(r_["shuf_max"], 3),
                    "detectable": det,
                    "floor_raw": round(float(r_["floor_raw"][j]), 4),
                    "floor_rep": round(float(r_["floor_rep"][j]), 4),
                    "corrected": bool(r_["pn_ok"]),
                    "D": round(float(D), 4), "Dp": round(float(Dp), 4),
                    "sec_r2": round(float(sec), 4), "L": round(float(L), 4),
                    "exact_p": round(float(r_["exact_p"][j]), 4),
                    "a_match": round(float(rec["am"][j]), 4) if arm == "A" else np.nan,
                    "screen_fail_high_known": bool(
                        not det and D >= NQ[(arm, "D", j)][0.99]),
                    "cond": round(r_["cond"], 1),
                    "sec_min_count": int(w["sec_cnt"].min()),
                    "label": lab})
    df = pd.DataFrame(rows)
    # recurrence: label-4 arm-B slots vs adjacent window label-4 loadings (common names)
    df["recurrent"] = False
    l4 = df[(df.arm == "B") & (df.label == "detectable-candidate-residual-risk")]
    for wi in range(nw - 1):
        a, b = wins[wi], wins[wi + 1]
        ja = l4[l4.window == a["d0"]].pc.values - 1
        jb = l4[l4.window == b["d0"]].pc.values - 1
        if not len(ja) or not len(jb):
            continue
        common = sorted(set(a["names"]) & set(b["names"]))
        ia = [a["names"].index(m) for m in common]
        ib = [b["names"].index(m) for m in common]
        Ha = per_win[wi]["B"]["H"][ia][:, ja]
        Hb = per_win[wi + 1]["B"]["H"][ib][:, jb]
        Ha /= np.linalg.norm(Ha, axis=0)
        Hb /= np.linalg.norm(Hb, axis=0)
        sim = np.abs(Ha.T @ Hb)
        for x, j in enumerate(ja):
            if sim[x].max() >= 0.5:
                df.loc[(df.arm == "B") & (df.window == a["d0"])
                       & (df.pc == j + 1), "recurrent"] = True
        for y, j in enumerate(jb):
            if sim[:, y].max() >= 0.5:
                df.loc[(df.arm == "B") & (df.window == b["d0"])
                       & (df.pc == j + 1), "recurrent"] = True
    df.to_csv(HERE / "floor_industry.csv", index=False)

    # controls
    w_last, rec_last = wins[-1], per_win[-1]
    _, _, Xp, _ = pca(w_last["Ya"], KP)
    theta_p, ell_p, _, _ = pca(w_last["Ya"], KP)
    snr_pos = (theta_p / ell_p - 1.0)[0]
    r2_mkt = float(r2(Xp[:1], w_last["fa"][:, :1])[0])
    pos_pass = bool(snr_pos > q99["B"][0] and r2_mkt >= 0.7)
    detA = df[(df.arm == "A") & df.detectable & (df.pc > 1)]
    detB = df[(df.arm == "B") & df.detectable & (df.pc > 1)]
    medA = float(detA.sec_r2.median()) if len(detA) else np.nan
    # frozen reference: sector-R2 null draws pooled across ranks 2-5, arm A
    pooled_sec = np.concatenate([np.concatenate(null_pool[("A", "sec", j)])
                                 for j in range(1, KP)])
    sec_null_q75 = float(np.quantile(pooled_sec, 0.75))
    ind_testable = len(detA) > 0 and medA >= sec_null_q75    # validity FIRST
    medB = float(detB.sec_r2.median()) if len(detB) else np.nan
    if not ind_testable:
        ind_pass = None
    elif not len(detB):
        ind_pass = True
    else:
        ind_pass = bool((medA - medB) / medA >= 0.5)
    cal_pooled = float(ho_exc.mean())
    cal_rank = ho_exc.mean(axis=0)
    cal_pass = bool(cal_pooled <= 0.03)
    det_all = df[df.detectable]
    valid = float(((det_all.floor_rep >= 0) & (det_all.floor_rep <= 1)
                   & det_all.floor_rep.notna()).mean()) if len(det_all) else 1.0
    evaluable = [pos_pass, cal_pass] + ([ind_pass] if ind_testable else [])
    if not all(evaluable):
        verdict = "FAIL"
    elif valid >= 0.95:
        verdict = "SUCCESS"
    else:
        verdict = "AMBIGUOUS"

    # sensitivity table
    sens = {}
    B_det = df[(df.arm == "B") & df.detectable]
    for lc in L_SENS:
        n4 = 0
        for _, s in B_det.iterrows():
            j = s.pc - 1
            if (s.D < NQ[("B", "D", j)][0.75] and s.Dp < NQ[("B", "Dp", j)][0.99]
                    and s.L <= lc):
                n4 += 1
        sens[lc] = n4

    write_report(df, dict(pos_snr=float(snr_pos), pos_r2=r2_mkt, pos_pass=pos_pass,
                          medA=medA, medB=medB, ind_testable=ind_testable,
                          ind_pass=ind_pass, cal_pooled=cal_pooled,
                          cal_rank=cal_rank, valid=valid), verdict, sens, q99,
                 {arm: np.quantile(shuf_L[arm], [0.5, 0.9, 0.99]) for arm in ("A", "B")})
    stamp_run(track="estimator_lab", variant="floor_industry",
              params={"n_an": N_AN, "n_beta": N_BETA, "kp": KP, "kmatch": KMATCH,
                      "n_shuf": N_SHUF, "base_seeds": BASE_SEED,
                      "heldout_seeds": HELDOUT_SEEDS, "l_cut": L_CUT,
                      "verdict": verdict,
                      "sector_asof": "2026-07 (asserted; no embedded date)",
                      "input_sha256": {f: hashlib.sha256(
                          (ROOT / f).read_bytes()).hexdigest()[:16] for f in INPUTS},
                      "memo": "FLOOR_INDUSTRY_MEMO.md#rev2"},
              n_trials=1)


def write_report(df, c, verdict, sens, q99, shufL):
    A, B = df[df.arm == "A"], df[df.arm == "B"]
    lines = ["# Phase 7 — FF+industry arm: vetted residual-factor panel", "",
             "Descriptive only. Prereg: FLOOR_INDUSTRY_MEMO.md rev 2 (frozen). "
             f"{df.window.nunique()} primary windows, arms A (FF) / B (FF+11 GICS).", "",
             f"## Verdict (pre-committed): **{verdict}**", "",
             "## Controls",
             f"- positive: PC1 SNR̂ {c['pos_snr']:.1f} vs rank-1 screen q99 "
             f"{q99['B'][0]:.2f}, R² vs Mkt−RF {c['pos_r2']:.3f} (bar 0.7) → "
             f"{'PASS' if c['pos_pass'] else 'FAIL'}",
             f"- industry: med sector-R² arm-A {c['medA']:.3f} → arm-B "
             f"{c['medB'] if c['medB'] == c['medB'] else float('nan'):.3f} "
             f"({'not testable' if not c['ind_testable'] else 'PASS' if c['ind_pass'] else 'FAIL'})",
             f"- screen calibration-consistency: held-out exceedance {c['cal_pooled']:.2%} "
             f"(bar ≤ 3%) → {'PASS' if c['cal_pooled'] <= 0.03 else 'FAIL'}; per-rank: "
             f"{np.array2string(c['cal_rank'], precision=3)}",
             f"- floor validity (detectable slots): {c['valid']:.1%}", "",
             "## Screen (empirical per-rank q99; C4 kept as descriptive column)",
             f"- arm A q99 by rank: {np.array2string(q99['A'], precision=2)}",
             f"- arm B q99 by rank: {np.array2string(q99['B'], precision=2)}",
             f"- detectable slots: arm A {int(A.detectable.sum())}/70, "
             f"arm B {int(B.detectable.sum())}/70 "
             f"(C4 would pass: A {int(A.c4_flag.sum())}, B {int(B.c4_flag.sum())})",
             f"- screen-fail-high-known-assoc (mostly rank-1 insensitivity): "
             f"A {int(A.screen_fail_high_known.sum())}, "
             f"B {int(B.screen_fail_high_known.sum())}", "",
             "## Label counts", "", "| label | arm A | arm B |", "|---|---|---|"]
    for lab in ["noise-like", "explained-by-industry-or-known", "high-known-association",
                "detectable-candidate-residual-risk", "mixed-uncertain"]:
        lines.append(f"| {lab} | {int((A.label == lab).sum())} "
                     f"| {int((B.label == lab).sum())} |")
    l4 = B[B.label == "detectable-candidate-residual-risk"]
    lines += ["", "## Arm-A slot flow under industry",
              f"- arm-A detectable: {int(A.detectable.sum())}; of those "
              f"explained-by-industry-or-known: "
              f"{int((A.label == 'explained-by-industry-or-known').sum())}",
              f"- arm-A a_match (vs arm-B top-7): median "
              f"{A[A.detectable].a_match.median():.3f}", "",
              "## Vetted panel for Stage 2 (arm-B label 4)",
              f"- {len(l4)} slots across {l4.window.nunique()} windows; recurrent: "
              f"{int(l4.recurrent.sum())}",
              f"- floors: median {l4.floor_rep.median():.3f}" if len(l4) else
              "- (empty panel — Stage 2 L4 runs with no residual controls)",
              f"- L-cut sensitivity (label-4 count at L ≤ 0.25/0.30/0.40/0.50): "
              f"{[sens[k] for k in sorted(sens)]}",
              f"- shuffled-panel L quantiles (q50/q90/q99): "
              f"A {np.array2string(shufL['A'], precision=2)}, "
              f"B {np.array2string(shufL['B'], precision=2)}", "",
              "## Story", "", "(appended post-run)", ""]
    (HERE / "FLOOR_INDUSTRY.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
