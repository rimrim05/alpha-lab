"""Forward alpha-isolation review layer (EXP-2026-07-14-alpha-forward).

Measurement ONLY: compares each hunt2026 book's forward paper NAV to a FROZEN
M2/M2g factor-replication benchmark (research/attribution/frozen_betas_2026-07-14.json).
Never touches weights, allocations, specs, or the trading loop.

Usage (from repo root, .venv):
  hunt_alpha_review.py --selfcheck   validate the replication chain on the blind windows (offline)
  hunt_alpha_review.py               append newly finalized days to the write-once forward
                                     ledger + write the monthly descriptive report
  hunt_alpha_review.py --evaluate    6m/12m evaluation stats (also auto-runs past due dates)

Design decisions (review-audited 2026-07-14; policies in memos/alpha-forward-setup-2026-07-14.md):
- Book daily returns come from the ledger's `ret_1d` field (the nightly `nav` is a rolling
  252d-rebased index, nav.pct_change() is NOT a daily return; found by audit, B1).
- Factor + placebo closes come from a dedicated ~550-day fresh yfinance pull so TSMOM's
  252+21+63d windows never cross the panel/fresh adjusted-close seam (audit finding 2).
- A day is finalized only when the book return AND factors exist AND the day is at least
  EMBARGO_DAYS behind the end of the FF daily file (FF revision embargo, M10).
- Forward rows embed the factor vintage at append time and are never rewritten; overlapping
  recomputations only WARN on drift. 12m review recomputes from the then-current vintage as
  a disclosed sensitivity; the ledger stays the series of record.
NETWORK on review runs (FF + ETF bars), manifest-logged; --selfcheck is offline.
"""
import argparse
import datetime as dt
import hashlib
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "research/hunt2026"))
sys.path.insert(0, str(REPO / "research/attribution"))
import harness                    # noqa: E402
import run_attribution as ra      # noqa: E402  (nw_ols self-checks assert at import)

FROZEN = json.loads((REPO / "research/attribution/frozen_betas_2026-07-14.json").read_text())
LEDGER_DIR = REPO / "ledgers/hunt2026"
FWD_DIR = LEDGER_DIR / "alpha_forward"
REPORT_DIR = REPO / "reports/alpha_forward"
FF5_URL = ("https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
           "F-F_Research_Data_5_Factors_2x3_daily_CSV.zip")
MOM_URL = ("https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
           "F-F_Momentum_Factor_daily_CSV.zip")
FWD_START = pd.Timestamp(FROZEN["forward_start"])
EMBARGO_DAYS = 10           # trading days a day must trail the FF file end before finalizing
DRIFT_WARN = 1e-4           # daily |resid| recompute drift that triggers a vintage warning


# ------------------------------------------------------------------ factors
def _french_zip(url, cols):
    raw = urllib.request.urlopen(url, timeout=60).read()
    z = zipfile.ZipFile(io.BytesIO(raw))
    txt = z.read(z.namelist()[0]).decode("latin1").splitlines()
    rows = [l.split(",") for l in txt if l.strip() and l.split(",")[0].strip().isdigit()]
    df = pd.DataFrame(rows).iloc[:, : 1 + len(cols)]
    df.columns = ["date"] + cols
    df["date"] = pd.to_datetime(df["date"].str.strip(), format="%Y%m%d")
    return df.set_index("date").astype(float) / 100.0, hashlib.sha256(raw).hexdigest()


def fetch_ff_live():
    ff5, sha5 = _french_zip(FF5_URL, ["Mkt-RF", "SMB", "HML", "RMW", "CMA", "RF"])
    mom, sham = _french_zip(MOM_URL, ["Mom"])
    fac = ff5.join(mom, how="inner")
    path = REPO / "data/raw/ff_factors_daily_live.parquet"   # frozen inputs untouched
    fac.to_parquet(path)
    with open(REPO / "data/manifest.jsonl", "a") as f:
        f.write(json.dumps({"name": "ff_factors_daily_live", "source": "ken.french dartmouth",
                            "filters": {}, "path": str(path.relative_to(REPO)),
                            "rows": len(fac), "sha256_ff5_zip": sha5, "sha256_mom_zip": sham,
                            "pulled_at": dt.datetime.now(dt.timezone.utc).isoformat()}) + "\n")
    return fac


def fetch_factor_closes():
    """~550 calendar days of fresh adjusted closes for every factor/placebo ticker,
    one consistent adjustment vintage, no panel seam inside any TSMOM window."""
    from core.data.prices import fetch_prices_yf
    menu = FROZEN["tsmom_spec"]["menu"]
    tickers = sorted(set(menu) | {"QQQ", "SPY", "GLD"})
    start = (pd.Timestamp.today() - pd.Timedelta("550D")).strftime("%Y-%m-%d")
    return fetch_prices_yf(tickers, start=start, end=None)


def forward_factors(fac_ff, closes):
    """TSMOM + QQQRES + GLD per the FROZEN constructions; returns full factor frame."""
    spec = FROZEN["tsmom_spec"]
    close = closes[spec["menu"]]
    r = close.pct_change(fill_method=None)
    sig = np.sign(close.shift(spec["skip"]) / close.shift(spec["skip"] + spec["lookback"]) - 1.0)
    raw = (sig.shift(1) * r).mean(axis=1)
    raw = raw[sig.shift(1).notna().all(axis=1)]
    scale = (spec["vol_target_ann"] / np.sqrt(252)) / raw.rolling(spec["vol_window"]).std().shift(1)
    tsmom = (raw * scale).dropna().rename("TSMOM")

    proj = FROZEN["qqqres_projection"]
    qqq_ex = closes["QQQ"].pct_change(fill_method=None).sub(fac_ff["RF"]).dropna()
    common = qqq_ex.index.intersection(fac_ff.index)
    fit = proj["const"] + sum(proj[c] * fac_ff.loc[common, c] for c in ra.M1_COLS)
    qqqres = (qqq_ex.loc[common] - fit).rename("QQQRES")
    gld = closes["GLD"].pct_change(fill_method=None).sub(fac_ff["RF"]).dropna().rename("GLD")

    fac = fac_ff.join(tsmom, how="inner").join(qqqres, how="inner").join(gld, how="inner")
    if len(fac) > EMBARGO_DAYS:                    # FF-revision embargo (policy M10)
        fac = fac.iloc[:-EMBARGO_DAYS]
    return fac


# ------------------------------------------------------------------ series
def book_returns(name):
    """Daily net returns from the ledger's ret_1d field (live preferred over dry per date).
    Rows without ret_1d (pre-2026-07-14 schema) are ignored; they predate the forward window."""
    path = LEDGER_DIR / f"{name}.jsonl"
    recs = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    rows = [r for r in recs if r.get("mode") in ("live", "dry") and "ret_1d" in r]
    rows.sort(key=lambda r: (r["date"], r.get("mode") == "live"))   # live wins per date
    df = pd.DataFrame([{"date": r["date"], "ret": r["ret_1d"], "gross": r.get("gross", np.nan)}
                       for r in rows]).drop_duplicates("date", keep="last")
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    return df[df.index >= FWD_START]


def placebo_returns(name, closes, fac):
    q = closes["QQQ"].pct_change(fill_method=None)
    s = closes["SPY"].pct_change(fill_method=None)
    if name == "CTRL_spy_buyhold":
        r, g = s, 1.0
    elif name in ("CTRL_qqq_buyhold", "CTRL_qqq_buyhold_M1"):
        r, g = q, 1.0
    else:  # CTRL_qqq_1.5x_static: financing charged ONCE, by residual_frame (audit M3)
        r, g = 1.5 * q, 1.5
    out = pd.DataFrame({"ret": r, "gross": g}).dropna(subset=["ret"])
    return out[out.index >= FWD_START]


def residual_frame(name, rets, fac):
    """Per finalized day: replication, financing, residual. Finalized = ret AND factors exist.
    Financing is charged on gross held DURING the day (prior close's target, audit M7)."""
    spec = FROZEN["books"][name]
    b = spec["betas"]
    idx = rets.index.intersection(fac.index)
    f = fac.loc[idx]
    repl = f["RF"] + sum(beta * f[k] for k, beta in b.items())
    gross_held = pd.to_numeric(rets["gross"], errors="coerce").shift(1) \
        .reindex(idx).fillna(spec["avg_gross_asrun"])
    fin = np.maximum(gross_held - 1.0, 0.0) * (f["RF"] + 0.005 / 252)
    resid = rets.loc[idx, "ret"] - repl - fin
    return pd.DataFrame({"ret_net": rets.loc[idx, "ret"], "repl_ret": repl,
                         "fin": fin, "resid_net": resid, "gross": gross_held})


# ------------------------------------------------------------------ ledger (write-once)
def _read_forward_lines(path):
    good, torn = [], 0
    for l in path.read_text().splitlines():
        if not l.strip():
            continue
        try:
            good.append(json.loads(l))
        except json.JSONDecodeError:
            torn += 1
    if torn:
        print(f"WARNING: {path.name}: {torn} unparsable line(s) skipped (torn write?) — "
              "inspect manually; appends continue after the last valid date")
    return good


def append_forward(name, df):
    FWD_DIR.mkdir(parents=True, exist_ok=True)
    path = FWD_DIR / f"{name}.jsonl"
    existing = _read_forward_lines(path) if path.exists() else []
    last = pd.Timestamp(existing[-1]["date"]) if existing else None
    # vintage-drift check on overlap: warn, never rewrite (policy M10)
    if existing:
        old = pd.Series({pd.Timestamp(r["date"]): r["resid_net"] for r in existing})
        both = old.index.intersection(df.index)
        if len(both):
            drift = (df.loc[both, "resid_net"] - old.loc[both]).abs().max()
            if drift > DRIFT_WARN:
                print(f"WARNING: {name}: recomputed resid drifts up to {drift:.2e}/day vs "
                      "stored rows (factor vintage change). Ledger unchanged (write-once).")
    new = df[df.index > last] if last is not None else df
    if new.empty:
        return 0
    batch = "".join(json.dumps({"date": str(d.date()),
                                **{k: round(float(v), 8) for k, v in row.items()}}) + "\n"
                    for d, row in new.iterrows())
    with open(path, "a") as f:
        f.write(batch)                                   # single write (torn-line guard)
    return len(new)


def load_forward(name):
    path = FWD_DIR / f"{name}.jsonl"
    if not path.exists():
        return pd.DataFrame()
    df = pd.DataFrame(_read_forward_lines(path))
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"])
    return df.set_index("date").sort_index()


# ------------------------------------------------------------------ stats
def descriptive(df):
    if df.empty:
        return {}
    resid, ret = df["resid_net"], df["ret_net"]
    cum = (1 + resid).cumprod()
    return {"days": len(df), "cum_resid": float(cum.iloc[-1] - 1),
            "resid_ann": float(resid.mean() * 252),
            "te_ann": float((ret - df["repl_ret"]).std(ddof=1) * np.sqrt(252)),
            "resid_dd": float((cum / cum.cummax() - 1).min()),
            "mean_gross": float(df["gross"].mean()),
            "fin_ann": float(df["fin"].mean() * 252),
            "pos_month_share": float((resid.resample("ME").sum() > 0).mean())}


def evaluate(df):
    """6m/12m review stats (NW lag 5). Descriptive only, no decision automation."""
    if df.empty:
        return {}
    stats = descriptive(df)
    if len(df) < 40:
        stats["note"] = "insufficient finalized days for inference"
        return stats
    y = df["resid_net"].values
    beta, se, t, _, _ = ra.nw_ols(y, np.ones((len(y), 1)))
    resid_vol = df["resid_net"].std(ddof=1) * np.sqrt(252)
    stats.update({"alpha_ann": float(beta[0] * 252), "t_nw": float(t[0]),
                  "resid_sharpe": float(beta[0] * 252 / resid_vol) if resid_vol > 0 else np.nan})
    return stats


# ------------------------------------------------------------------ modes
def selfcheck():
    """Offline: frozen-beta replication must reproduce the freeze-time alphas.
    Tolerance 2.5%/yr: as-run M2 alphas came from the PRE-correction panel while this
    reruns books on the corrected one (audit-measured moves up to ~2pp), plus small
    QQQRES-coefficient drift. Wiring bugs (sign/date misalignment) produce 5-50% deltas
    and still fail loudly. M2g books compare against alpha_ann_frozen (same panel, ~0)."""
    panel = harness.load_full()
    fac = ra.build_factors(panel)
    fac = fac.join(panel["close"]["GLD"].pct_change(fill_method=None)
                   .sub(fac["RF"]).dropna().rename("GLD"), how="inner")
    print("selfcheck: mean(resid) ann vs frozen alpha")
    worst = 0.0
    for name, spec in FROZEN["books"].items():
        if spec["role"] != "live_book":
            continue
        start = "2025-07-10" if spec["n_obs"] < 400 else "2021-07-10"
        r = harness.run(harness.load_spec(str(REPO / f"research/hunt2026/specs/{name}")),
                        panel, start=start)
        rets = pd.DataFrame({"ret": r["net_daily"]})
        idx = rets.index.intersection(fac.index)
        f = fac.loc[idx]
        repl_ex = sum(beta * f[k] for k, beta in spec["betas"].items())
        resid = rets.loc[idx, "ret"] - f["RF"] - repl_ex      # no financing: matches regression alpha
        ref = spec.get("alpha_ann_frozen", spec["alpha_ann_asrun"])
        tol = 0.005 if "alpha_ann_frozen" in spec else 0.025
        delta = resid.mean() * 252 - ref
        worst = max(worst, abs(delta))
        print(f"  {name:24} ({spec['model']}) mean resid {resid.mean()*252:+.2%}  "
              f"frozen {ref:+.2%}  delta {delta:+.3%}")
        assert abs(delta) < tol, f"{name}: replication chain broken (delta {delta:+.3%})"
    print(f"selfcheck PASS (worst |delta| {worst:.3%})")


def review(do_eval):
    fac_ff = fetch_ff_live()
    closes = fetch_factor_closes()
    fac = forward_factors(fac_ff, closes)
    today = pd.Timestamp.today().normalize()
    lines = [f"# Alpha-forward review — {today.date()}",
             f"Frozen benchmark: frozen_betas_{FROZEN['freeze_date']}.json · forward start "
             f"{FROZEN['forward_start']} · factors finalized through {fac.index[-1].date()} "
             f"(embargo {EMBARGO_DAYS}d behind FF end {fac_ff.index[-1].date()})",
             "", "Descriptive only. No parameter, hedge, or allocation change is permitted "
             "from this report. Reviews: 6m 2027-01-14, 12m 2027-07-14. Decision rules, "
             "placebo bands, and disclosures: memos/alpha-forward-setup-2026-07-14.md.", ""]
    hdr = ("| series | days | cum resid | resid ann | TE ann | resid DD | gross | fin/yr | +mo share |"
           if not do_eval else
           "| series | days | resid ann | NW t | resid Sharpe | cum resid | resid DD | TE | +mo share |")
    lines += [hdr, "|" + "---|" * 9]
    for name, spec in FROZEN["books"].items():
        rets = (book_returns(name) if spec["role"] == "live_book"
                else placebo_returns(name, closes, fac))
        if rets.empty:
            lines.append(f"| {name} | 0 | — no forward book days yet |" + " |" * 6)
            continue
        df = residual_frame(name, rets, fac)
        n_new = append_forward(name, df)
        full = load_forward(name)
        s = evaluate(full) if do_eval else descriptive(full)
        if not s:
            lines.append(f"| {name} | 0 | — awaiting finalized days (FF publication lag) |" + " |" * 6)
            continue
        if do_eval and "alpha_ann" in s:
            lines.append(f"| {name} | {s['days']} | {s['resid_ann']:+.2%} | {s['t_nw']:+.2f} | "
                         f"{s['resid_sharpe']:+.2f} | {s['cum_resid']:+.2%} | {s['resid_dd']:+.2%} | "
                         f"{s['te_ann']:.2%} | {s['pos_month_share']:.0%} |")
        else:
            lines.append(f"| {name} | {s['days']} | {s['cum_resid']:+.2%} | {s['resid_ann']:+.2%} | "
                         f"{s['te_ann']:.2%} | {s['resid_dd']:+.2%} | {s['mean_gross']:.2f} | "
                         f"{s['fin_ann']:.2%} | {s['pos_month_share']:.0%} |")
        print(f"{name}: +{n_new} finalized days appended (total {s.get('days', 0)})")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORT_DIR / f"{today:%Y-%m}{'-eval' if do_eval else ''}.md"
    out.write_text("\n".join(lines) + "\n")
    print(f"report -> {out.relative_to(REPO)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--evaluate", action="store_true")
    a = ap.parse_args()
    if a.selfcheck:
        selfcheck()
    else:
        due = pd.Timestamp.today() >= pd.Timestamp(FROZEN["review_dates"]["6m"])
        review(do_eval=a.evaluate or due)
