"""Freeze the forward alpha-isolation benchmark: per-book M2 exposures + factor
constructions. One-shot; the output JSON is write-once (refuses to overwrite).
Source of truth: attribution.csv from EXP-2026-07-14-factor-attribution (as-run).
Setup record: memos/alpha-forward-setup-2026-07-14.md."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "research/hunt2026"))
sys.path.insert(0, str(REPO / "research/attribution"))
import harness                      # noqa: E402
import run_attribution as ra        # noqa: E402

FREEZE_DATE = "2026-07-14"
OUT = Path(__file__).parent / f"frozen_betas_{FREEZE_DATE}.json"

# claim-bearing blind window per book (program convention)
BOOK_WINDOW = {
    "vol_managed_qqq": "blind", "vol_core_svxy": "blind",
    "dual_momentum_gem": "blind", "momentum_concentrated": "blind",
    "trend_vol_qqq": "blind", "defensive_ensemble": "blind",
    "dual_momentum_gold": "blind",
}
PLACEBOS = {"CTRL_spy_buyhold": "blind_5y", "CTRL_qqq_buyhold": "blind_5y",
            "CTRL_qqq_1.5x_static": "blind_5y"}
FACTORS = ["Mkt-RF", "SMB", "HML", "RMW", "CMA", "Mom", "TSMOM", "QQQRES"]


GOLD_BOOKS = ["defensive_ensemble", "dual_momentum_gold"]  # M2g amendment (factor-model review)


def _m2g_betas(panel, fac_g, name):
    """M2+GLD blind-window regression on the corrected panel (pre-forward amendment)."""
    cols = ra.M2_COLS + ["GLD"]
    r = ra.harness.run(ra.harness.load_spec(str(REPO / f"research/hunt2026/specs/{name}")),
                       panel, start="2021-07-10")
    df = pd.concat([r["net_daily"].rename("book"), fac_g], axis=1, join="inner") \
        .loc["2021-07-12":ra.FF_END].dropna()
    y = (df["book"] - df["RF"]).values
    X = np.hstack([np.ones((len(df), 1)), df[cols].values])
    b, se, t, r2, n = ra.nw_ols(y, X)
    return ({c: float(v) for c, v in zip(cols, b[1:])},
            float(b[0] * 252), float(t[0]), int(n))


def main():
    if OUT.exists():
        raise SystemExit(f"{OUT} exists — freeze file is write-once, refusing.")
    att = pd.read_csv(Path(__file__).parent / "attribution.csv")

    books = {}
    for name, win in {**BOOK_WINDOW, **PLACEBOS}.items():
        row = att[(att.book == name) & (att.model == "M2") & (att.window == win)]
        assert len(row) == 1, (name, win, len(row))
        r = row.iloc[0]
        books[name] = {
            "window": win, "n_obs": int(r.n_obs), "model": "M2",
            "alpha_ann_asrun": float(r.alpha_ann), "t_alpha_asrun": float(r.t_alpha),
            "avg_gross_asrun": float(r.avg_gross),
            "betas": {f: float(r[f"beta_{f}"]) for f in FACTORS},
            "role": "placebo" if name in PLACEBOS else "live_book",
        }

    # M2g amendment: GLD-augmented benchmark for the gold-loaded books (documented KNOWN
    # exposure per the final memo / adversarial review; amended before forward start).
    panel = harness.load_full()
    fac0 = ra.build_factors(panel)
    fac_g = fac0.join(panel["close"]["GLD"].pct_change(fill_method=None)
                      .sub(fac0["RF"]).dropna().rename("GLD"), how="inner")
    for name in GOLD_BOOKS:
        betas, a_ann, t_a, n = _m2g_betas(panel, fac_g, name)
        books[name].update({"model": "M2g", "betas": betas,
                            "alpha_ann_frozen": a_ann, "t_alpha_frozen": t_a,
                            "m2g_note": "M2+GLD refit on corrected panel, blind_5y window; "
                                        "as-run M2 alpha kept in alpha_ann_asrun"})

    # Informative QQQ placebo: M1 betas, TSMOM/QQQRES zeroed (data-integrity review M4).
    # Its residual = projection const + forward QQQRES, testing the frozen projection.
    row = att[(att.book == "CTRL_qqq_buyhold") & (att.model == "M1") & (att.window == "blind_5y")]
    assert len(row) == 1
    r = row.iloc[0]
    books["CTRL_qqq_buyhold_M1"] = {
        "window": "blind_5y", "n_obs": int(r.n_obs), "model": "M1",
        "alpha_ann_asrun": float(r.alpha_ann), "t_alpha_asrun": float(r.t_alpha),
        "avg_gross_asrun": 1.0,
        "betas": {**{f: float(r[f"beta_{f}"]) for f in
                     ["Mkt-RF", "SMB", "HML", "RMW", "CMA", "Mom"]},
                  "TSMOM": 0.0, "QQQRES": 0.0},
        "role": "placebo",
    }

    # pre-registered placebo bands (judged on these, NEVER on t-stats; miss = pipeline stop)
    books["CTRL_spy_buyhold"]["expected_resid_ann"] = {
        "center": books["CTRL_spy_buyhold"]["alpha_ann_asrun"], "band": 0.005}
    books["CTRL_qqq_buyhold"]["expected_resid_ann"] = {
        "center": books["CTRL_qqq_buyhold"]["alpha_ann_asrun"], "band": 0.005,
        "extra": "TE_ann must be < 0.5%; deterministic tautology control, never judged on t"}
    books["CTRL_qqq_buyhold_M1"]["expected_resid_ann"] = {
        "center": books["CTRL_qqq_buyhold_M1"]["alpha_ann_asrun"],
        "band": "2 * 4.9%/sqrt(n_days/252) (QQQRES vol band)",
        "extra": "the informative control: tests whether the frozen projection still describes QQQ"}
    books["CTRL_qqq_1.5x_static"]["expected_resid_ann"] = {
        "center": books["CTRL_qqq_1.5x_static"]["alpha_ann_asrun"] - 0.5 * 0.005, "band": 0.007,
        "extra": "as-run alpha minus the 50bps-spread leg now charged externally"}

    # QQQRES projection coefficients: same math as run_attribution.build_factors,
    # recomputed on the CORRECTED panel (as-run coefficients were not persisted;
    # deviation documented in the setup memo). Frozen here; never refit.
    panel = harness.load_full()
    ff5 = pd.read_parquet(REPO / "data/raw/ff5_factors_daily.parquet")
    mom = pd.read_parquet(REPO / "data/raw/ff_factors_daily.parquet")[["Mom"]]
    fac = ff5.join(mom, how="inner").loc[:ra.FF_END]
    qqq_ex = panel["close"]["QQQ"].pct_change(fill_method=None).sub(fac["RF"]).dropna()
    common = qqq_ex.index.intersection(fac.index)
    Xm1 = np.column_stack([np.ones(len(common)), fac.loc[common, ra.M1_COLS].values])
    b, *_ = np.linalg.lstsq(Xm1, qqq_ex.loc[common].values, rcond=None)
    qqqres_proj = {"const": float(b[0]),
                   **{c: float(v) for c, v in zip(ra.M1_COLS, b[1:])},
                   "fit_through": str(common[-1].date()), "fit_n": len(common)}

    payload = {
        "freeze_date": FREEZE_DATE,
        "forward_start": "2026-07-15",
        "review_dates": {"6m": "2027-01-14", "12m": "2027-07-14"},
        "source": "research/attribution/attribution.csv (EXP-2026-07-14-factor-attribution, as-run)",
        "panel_correction": "memos/panel-phantom-row-correction.md (corrected panels used for all forward accounting)",
        "model": "M2 = FF5 + Mom + TSMOM + QQQRES, daily, NW lag 5 at review",
        "tsmom_spec": {"menu": ra.TSMOM_MENU, "lookback": 252, "skip": 21,
                       "vol_target_ann": 0.10, "vol_window": 63,
                       "note": "sign(trailing 252d ret, skip 21d) at close t earns t+1; PIT vol scale"},
        "qqqres_projection": qqqres_proj,
        "financing": "daily (gross_t - 1)+ * (RF_t + 0.005/252); gross_t from the book ledger",
        "books": books,
        "attribution_csv_sha256": hashlib.sha256(
            (Path(__file__).parent / "attribution.csv").read_bytes()).hexdigest(),
    }
    OUT.write_text(json.dumps(payload, indent=1))
    print(f"frozen -> {OUT.name}: {len(books)} series "
          f"({sum(1 for b in books.values() if b['role']=='live_book')} books + "
          f"{sum(1 for b in books.values() if b['role']=='placebo')} placebos)")


if __name__ == "__main__":
    main()
