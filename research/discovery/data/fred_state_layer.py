"""Discovery Program — point-in-time FRED rates/curve + VIX/VIX3M state data layer.

THE DATA LAYER IS THE DELIVERABLE (charter Gates 1-3). No strategy is built here. Downstream
preregs may use the ALIGNED frame only after this file's audit prints VERDICT: PASS.

Design decisions (the honest PIT ones):
- Source: FRED keyless CSV (fredgraph.csv?id=). No API key. Treasury constant-maturity yields
  (DGS*), T10Y2Y, VIX, VIX3M are market/Treasury-published and effectively NOT revised (revision
  exposure LOW) — unlike GDP/CPI, which are deliberately EXCLUDED. DFF has negligible revision.
- observation_date != availability_date. Each series carries an `avail_lag_bdays`:
    rates & DFF = 1 business day (FRED publishes T+1; conservative — no same-day peeking).
    VIX / VIX3M = 0 (CBOE close is known at that day's close; using close_t at a close_t decision
    is contemporaneous, not look-ahead). Preregs add their own forecast/execution timestamps.
- Alignment: reindex to the repo trading calendar (panel_2005 index), shift each series by its
  availability lag, forward-fill ONLY across non-release gaps (never across a future gap, never
  before inception).
- VIX/VIX3M are STATE variables only. VIX3M-VIX is curve SHAPE, NOT the return to holding vol
  carry (needs futures/roll to be tradable). The report says so; no tradability is implied here.

Run: .venv/bin/python research/discovery/data/fred_state_layer.py   (fetch->build->audit->PASS/BLOCK)
"""
from __future__ import annotations
import io
import json
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = HERE / "raw"
RAW.mkdir(exist_ok=True)
PANEL = ROOT / "research" / "hunt2026" / "panel_2005.parquet"

# series_id -> (avail_lag_bdays, revision_exposure, kind)
SERIES = {
    "DGS3MO": (1, "low", "rate"), "DGS2": (1, "low", "rate"), "DGS5": (1, "low", "rate"),
    "DGS10": (1, "low", "rate"), "DGS30": (1, "low", "rate"), "DFF": (1, "low", "rate"),
    "T10Y2Y": (1, "low", "rate"),
    "VIXCLS": (0, "none", "vol"), "VXVCLS": (0, "none", "vol"),  # VXVCLS = 3-month VIX
}


def _fetch(series_id: str, retries: int = 3) -> pd.Series:
    """Latest-revised daily series from FRED keyless CSV, cached to parquet."""
    cache = RAW / f"{series_id}.parquet"
    if cache.exists():
        return pd.read_parquet(cache).iloc[:, 0]
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    for a in range(retries):
        try:
            raw = urllib.request.urlopen(url, timeout=20).read().decode()
            break
        except Exception:
            if a == retries - 1:
                raise
            time.sleep(1.5)
    df = pd.read_csv(io.StringIO(raw))
    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")  # FRED "." -> NaN
    s = df.set_index("date")["value"].rename(series_id)
    s.to_frame().to_parquet(cache)
    time.sleep(0.4)  # be polite to FRED
    return s


def fetch_all() -> tuple[dict[str, pd.Series], list[dict]]:
    """Raw series + provenance manifest (one record per series)."""
    now = pd.Timestamp.now(tz="America/New_York")
    raw, manifest = {}, []
    for sid, (lag, rev, kind) in SERIES.items():
        s = _fetch(sid)
        valid = s.dropna()
        raw[sid] = s
        manifest.append({
            "series_id": sid, "source": "FRED (fredgraph.csv, keyless)", "kind": kind,
            "avail_lag_bdays": lag, "revision_exposure": rev,
            "transformation": "level (% for rates, index for vol)",
            "inception": str(valid.index.min().date()), "last_obs": str(valid.index.max().date()),
            "n_obs": int(len(s)), "n_valid": int(valid.notna().sum()),
            "missing_pct": round(100 * (1 - valid.notna().sum() / len(s)), 2),
            "missing_policy": "FRED '.'->NaN; ffill across non-release gaps only, never pre-inception, never across a future gap",
            "timezone": "release America/New_York; obs dates are calendar",
            "retrieval_ts": now.isoformat(),
        })
    return raw, manifest


def _trading_calendar() -> pd.DatetimeIndex:
    p = pd.read_parquet(PANEL)
    idx = p.index if not isinstance(p.columns, pd.MultiIndex) else p.index
    return pd.DatetimeIndex(idx).normalize().unique().sort_values()


def align(raw: dict[str, pd.Series], cal: pd.DatetimeIndex | None = None) -> pd.DataFrame:
    """PIT-aligned frame on the trading calendar: each series shifted by its availability lag,
    ffilled forward only. Value at trading date t = latest obs whose availability_date <= t."""
    if cal is None:
        cal = _trading_calendar()
    out = {}
    for sid, s in raw.items():
        lag = SERIES[sid][0]
        s = s.dropna().sort_index()
        # availability date = observation date + lag business days
        avail = s.copy()
        if lag:
            avail.index = avail.index + pd.tseries.offsets.BDay(lag)
        # calendar-daily series (e.g. DFF) collapse many obs onto one business availability date;
        # keep the LAST obs for that date (the most recent info available then)
        avail = avail[~avail.index.duplicated(keep="last")].sort_index()
        # reindex onto union then ffill, then restrict to calendar (no ffill across a future gap:
        # reindex to sorted union guarantees monotonic forward fill only)
        u = avail.index.union(cal)
        out[sid] = avail.reindex(u).ffill().reindex(cal)
    df = pd.DataFrame(out, index=cal)
    # derived STATE features (documented as inputs, not signals; VIX terms are curve SHAPE only)
    df["slope_2s10s"] = df["DGS10"] - df["DGS2"]
    df["slope_3m10y"] = df["DGS10"] - df["DGS3MO"]
    df["term_spread_10y_ff"] = df["DGS10"] - df["DFF"]          # financing/term spread input
    df["rolldown_10y5y_proxy"] = (df["DGS10"] - df["DGS5"]) / 5  # transparent roll proxy (input)
    df["vol_ts_spread"] = df["VXVCLS"] - df["VIXCLS"]            # VIX3M - VIX (SHAPE, not carry return)
    df["vol_ts_ratio"] = df["VXVCLS"] / df["VIXCLS"]
    return df


# ---------------- Gate 2: leakage audit ----------------
def audit(raw: dict[str, pd.Series], aligned: pd.DataFrame, cal: pd.DatetimeIndex) -> dict:
    res = {}

    # (a) availability: no aligned value at t may come from an obs with availability_date > t
    ok_avail = True
    for sid in SERIES:
        lag = SERIES[sid][0]
        s = raw[sid].dropna()
        avail = s.copy()
        if lag:
            avail.index = avail.index + pd.tseries.offsets.BDay(lag)
        for t in cal[::250]:  # sample dates for speed
            v = aligned.loc[t, sid]
            if pd.isna(v):
                continue
            past = avail[avail.index <= t]
            if past.empty or not np.isclose(past.iloc[-1], v):
                ok_avail = False
                break
    res["availability_no_lookahead"] = ok_avail

    # (b) future-poison: NaN every raw obs after cutoff; aligned values at t<=cutoff unchanged
    cutoff = cal[int(len(cal) * 0.6)]
    poisoned = {sid: s.copy() for sid, s in raw.items()}
    for sid in poisoned:
        poisoned[sid][poisoned[sid].index > cutoff] = np.nan
    ap = align(poisoned, cal)
    base = aligned.loc[:cutoff, list(SERIES)]
    comp = ap.loc[:cutoff, list(SERIES)]
    res["future_poison_stable"] = bool(np.allclose(base.fillna(-999), comp.fillna(-999)))

    # (c) truncation: build with data truncated at T; aligned at t<=T matches full build
    T = cal[int(len(cal) * 0.75)]
    trunc = {sid: s[s.index <= T] for sid, s in raw.items()}
    at = align(trunc, cal)
    res["truncation_stable"] = bool(np.allclose(
        aligned.loc[:T, list(SERIES)].fillna(-999), at.loc[:T, list(SERIES)].fillna(-999)))

    # (d) calendar alignment: index is exactly the trading calendar, monotonic, unique
    res["calendar_aligned"] = bool(aligned.index.equals(cal) and aligned.index.is_monotonic_increasing
                                   and aligned.index.is_unique)

    # (e) VIX cross-check vs in-repo panel ^VIX (should be ~1 correlation)
    try:
        p = pd.read_parquet(PANEL)
        vix_panel = (p["close"]["^VIX"] if isinstance(p.columns, pd.MultiIndex) else p["^VIX"]).dropna()
        j = pd.concat([aligned["VIXCLS"], vix_panel.rename("panel")], axis=1).dropna()
        res["vix_panel_corr"] = round(float(j["VIXCLS"].corr(j["panel"])), 4)
    except Exception as e:
        res["vix_panel_corr"] = f"skip ({type(e).__name__})"

    # (f) staleness: max consecutive ffilled days per series (a huge run = a data hole)
    stale = {}
    for sid in SERIES:
        col = aligned[sid]
        changed = col.ne(col.shift())
        runs = (~changed).astype(int).groupby(changed.cumsum()).cumsum()
        stale[sid] = int(runs.max())
    res["max_stale_run_days"] = stale
    return res


def main():
    cal = _trading_calendar()
    raw, manifest = fetch_all()
    aligned = align(raw, cal)
    (HERE / "provenance.jsonl").write_text("\n".join(json.dumps(m) for m in manifest) + "\n")
    aligned.to_parquet(HERE / "state_aligned.parquet")
    a = audit(raw, aligned, cal)

    gates = [a["availability_no_lookahead"], a["future_poison_stable"], a["truncation_stable"],
             a["calendar_aligned"], isinstance(a["vix_panel_corr"], float) and a["vix_panel_corr"] > 0.98]
    verdict = "PASS" if all(gates) else "BLOCK"

    print(f"calendar {cal[0].date()}..{cal[-1].date()} n={len(cal)}")
    print(f"aligned cols: {list(aligned.columns)}")
    print("earliest all-rates valid:", aligned[["DGS3MO","DGS2","DGS10","DFF"]].dropna().index.min().date())
    print("earliest +vol valid:     ", aligned[["DGS10","VIXCLS","VXVCLS"]].dropna().index.min().date())
    print("\nAUDIT")
    for k, v in a.items():
        print(f"  {k}: {v}")
    print(f"\nVERDICT: {verdict}")
    return verdict, a


if __name__ == "__main__":
    main()
