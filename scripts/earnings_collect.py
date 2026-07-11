"""EXP-IC-EARNINGS-FWD collector — forward-only point-in-time earnings-surprise panel.

Pre-registered: research/hunt2026/preregistrations/exp-ic-earnings-fwd-2026-07-10.md.
Nightly (default): pull Finnhub earnings calendar [today-3d, today+7d], fetch surprise
rows for S&P members that reported, append NEW events (dedupe symbol+period) to
data/earnings_fwd/events.jsonl. Rows from the 4-quarter history endpoint are flagged
point_in_time=False (stale-knowledge risk) and are EXCLUDED from the primary IC test.
Also snapshots the first-session open/close reaction for prior nights' events.

--report: compute the pre-registered ICs on point-in-time events collected so far.

Finnhub free tier: 60 calls/min -> 1.1s throttle. Key: ~/.config/rimrimos/finnhub.env.
"""
import argparse
import datetime as dt
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

from core.data.universe import clean_ticker

ROOT = Path(__file__).resolve().parent.parent
EVENTS_PATH = ROOT / "data" / "earnings_fwd" / "events.jsonl"
REACTIONS_PATH = ROOT / "data" / "earnings_fwd" / "reactions.jsonl"
PANEL_PATH = ROOT / "research" / "hunt2026" / "panel_2005.parquet"
KEY_PATH = Path.home() / ".config" / "rimrimos" / "finnhub.env"
BASE = "https://finnhub.io/api/v1"
THROTTLE_S = 1.1  # 60/min limit
# Pre-registered thresholds (do not edit — see preregistration)
HORIZONS = (5, 20, 60)
N_PRIMARY, N_KILL = 300, 600


def _api_key() -> str:
    for line in KEY_PATH.read_text().splitlines():
        if line.startswith("FINNHUB_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError(f"FINNHUB_API_KEY not found in {KEY_PATH}")


def _get(path: str, **params) -> dict | list:
    """One throttled Finnhub GET. Monkeypatched in tests."""
    params["token"] = _api_key()
    url = f"{BASE}/{path}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=30) as r:
        out = json.load(r)
    time.sleep(THROTTLE_S)
    return out


def sp500_members() -> set[str]:
    df = pd.read_parquet(PANEL_PATH, columns=None)
    m = df["member"].iloc[-1]
    return set(m[m.astype(bool)].index)


# ---------------------------------------------------------------- events store

def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def append_new_events(path: Path, rows: list[dict]) -> int:
    """Append rows whose (symbol, period) is not already stored. Returns count added."""
    seen = {(r["symbol"], r["period"]) for r in load_jsonl(path)}
    new = [r for r in rows if (r["symbol"], r["period"]) not in seen]
    if new:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a") as f:
            for r in new:
                f.write(json.dumps(r) + "\n")
    return len(new)


def collect(today: dt.date | None = None) -> dict:
    """Nightly pull. Returns a summary dict (also printed by main)."""
    today = today or dt.date.today()
    frm, to = today - dt.timedelta(days=3), today + dt.timedelta(days=7)
    members = sp500_members()
    cal = _get("calendar/earnings", **{"from": frm.isoformat(), "to": to.isoformat()})
    cal_rows = cal.get("earningsCalendar", []) if isinstance(cal, dict) else []
    member_cal = [r for r in cal_rows if clean_ticker(r["symbol"]) in members]
    reported = [r for r in member_cal
                if r.get("epsActual") is not None and r["date"] <= today.isoformat()]

    pulled_at = dt.datetime.now().isoformat(timespec="seconds")
    rows = []
    for c in reported:
        sym = clean_ticker(c["symbol"])
        hist = _get("stock/earnings", symbol=c["symbol"])
        if not isinstance(hist, list) or not hist:
            continue
        latest_period = max(h["period"] for h in hist if h.get("period"))
        for h in hist:
            if not h.get("period"):
                continue
            fresh = h["period"] == latest_period
            rows.append({
                "pulled_at": pulled_at,
                "symbol": sym,
                "period": h["period"],
                # report_date only verifiably known for the event we watched happen
                "report_date": c["date"] if fresh else None,
                "hour": c.get("hour") if fresh else None,
                "estimate": h.get("estimate"),
                "actual": h.get("actual"),
                "surprise": h.get("surprise"),
                "surprise_pct": h.get("surprisePercent"),
                # ponytail: PIT = we saw the calendar row go actual within the pull
                # window; the 4-quarter backfill is stale-knowledge, primary-excluded
                "point_in_time": fresh,
            })
    added = append_new_events(EVENTS_PATH, rows)
    snapped = snapshot_reactions(today)
    summary = {"calendar_rows": len(cal_rows), "member_rows": len(member_cal),
               "reported_members": len(reported), "events_added": added,
               "reactions_snapped": snapped,
               "upcoming_members": sorted({clean_ticker(r["symbol"]) for r in member_cal
                                           if r["date"] > today.isoformat()})}
    return summary


# ---------------------------------------------------------- reaction snapshots

def reaction_session(report_date: str, hour: str | None) -> dt.date:
    """First session whose open/close reflect the report: bmo -> report day,
    amc/unknown -> next calendar day (yfinance lookup slides over weekends)."""
    d = dt.date.fromisoformat(report_date)
    return d if hour == "bmo" else d + dt.timedelta(days=1)


def snapshot_reactions(today: dt.date) -> int:
    """Fetch open/close of the reaction session for PIT events lacking one. Network."""
    events = [e for e in load_jsonl(EVENTS_PATH)
              if e.get("point_in_time") and e.get("report_date")]
    have = {(r["symbol"], r["period"]) for r in load_jsonl(REACTIONS_PATH)}
    todo = [e for e in events if (e["symbol"], e["period"]) not in have
            and reaction_session(e["report_date"], e.get("hour")) < today]
    if not todo:
        return 0
    import yfinance as yf
    rows = []
    for e in todo:
        sess = reaction_session(e["report_date"], e.get("hour"))
        px = yf.download(e["symbol"], start=sess.isoformat(),
                         end=(sess + dt.timedelta(days=5)).isoformat(),
                         progress=False, auto_adjust=False)
        if px.empty:
            continue
        first = px.iloc[0]
        rows.append({"symbol": e["symbol"], "period": e["period"],
                     "reaction_date": px.index[0].date().isoformat(),
                     "open": float(first["Open"].iloc[0] if hasattr(first["Open"], "iloc") else first["Open"]),
                     "close": float(first["Close"].iloc[0] if hasattr(first["Close"], "iloc") else first["Close"]),
                     "pulled_at": dt.datetime.now().isoformat(timespec="seconds")})
    return append_new_events(REACTIONS_PATH, rows)


# ------------------------------------------------------------------ IC report

def compute_sue(events: pd.DataFrame) -> pd.Series:
    """Pre-registered SUE: (actual-estimate)/scale; scale = std of the symbol's prior
    (earlier-period) surprises when >=2 exist, else |estimate|. History rows (non-PIT)
    may feed the scale — they are past data at event time — but never the test set."""
    ev = events.sort_values("period")
    out = pd.Series(index=ev.index, dtype=float)
    for i, row in ev.iterrows():
        prior = ev[(ev["symbol"] == row["symbol"]) & (ev["period"] < row["period"])]
        s = prior["surprise"].dropna().tail(4)
        scale = s.std() if len(s) >= 2 else abs(row["estimate"] or 0)
        if not scale or pd.isna(scale):
            scale = abs(row["estimate"]) if row["estimate"] else None
        raw = (row["actual"] - row["estimate"]) if pd.notna(row["actual"]) and pd.notna(row["estimate"]) else None
        out[i] = raw / scale if raw is not None and scale else float("nan")
    return out


def rank_ic(sue: pd.Series, fwd: pd.Series) -> tuple[float, float, int]:
    """Pooled Spearman IC + t-stat + n on paired non-null observations."""
    ok = sue.notna() & fwd.notna()
    n = int(ok.sum())
    if n < 3:
        return float("nan"), float("nan"), n
    ic = sue[ok].rank().corr(fwd[ok].rank())
    t = ic * (n - 2) ** 0.5 / (1 - ic ** 2) ** 0.5 if abs(ic) < 1 else float("inf")
    return float(ic), float(t), n


def report(events: list[dict] | None = None, reactions: list[dict] | None = None,
           prices: pd.DataFrame | None = None) -> dict:
    """Pre-registered IC report on point-in-time events. prices: close, dates x symbols
    (injected in tests; yfinance-fetched live when enough events exist)."""
    events = load_jsonl(EVENTS_PATH) if events is None else events
    reactions = load_jsonl(REACTIONS_PATH) if reactions is None else reactions
    all_ev = pd.DataFrame(events, columns=["pulled_at", "symbol", "period", "report_date",
                                           "hour", "estimate", "actual", "surprise",
                                           "surprise_pct", "point_in_time"])
    pit = all_ev[all_ev["point_in_time"].astype(bool)].copy()
    out = {"events_total": len(all_ev), "events_point_in_time": len(pit),
           "events_excluded_stale": int(len(all_ev) - len(pit)),
           "n_primary_threshold": N_PRIMARY, "n_kill_threshold": N_KILL, "ic": {}}
    if pit.empty:
        out["state"] = ("ACCUMULATING — 0 point-in-time events; forward-only collection "
                        "started 2026-07-10, no historical backfill is scoreable by design")
        return out

    rx = pd.DataFrame(reactions, columns=["symbol", "period", "reaction_date", "open",
                                          "close", "pulled_at"])
    pit = pit.merge(rx.drop(columns=["pulled_at"]), on=["symbol", "period"], how="left")
    # SUE computed on the full store (history rows feed the trailing-std scale),
    # then sliced to the PIT test set by original index
    pit["sue"] = compute_sue(all_ev).loc[
        all_ev.index[all_ev["point_in_time"].astype(bool)]].values
    pit["confirmed"] = pit["close"] >= pit["open"]

    if prices is None:
        if len(pit) < 3 or pit["reaction_date"].isna().all():
            out["state"] = (f"ACCUMULATING — {len(pit)} point-in-time events, "
                            f"forward returns not yet computable; need n>={N_PRIMARY} "
                            "for the primary test")
            return out
        import yfinance as yf
        syms = sorted(pit["symbol"].unique())
        start = min(pit["reaction_date"].dropna())
        px = yf.download(syms, start=start, progress=False, auto_adjust=True)["Close"]
        prices = px.to_frame(syms[0]) if isinstance(px, pd.Series) else px

    dates = prices.index
    for h in HORIZONS:
        fwd = pd.Series(index=pit.index, dtype=float)
        for i, row in pit.iterrows():
            if pd.isna(row["reaction_date"]) or row["symbol"] not in prices.columns:
                continue
            col = prices[row["symbol"]].dropna()
            pos = col.index.searchsorted(pd.Timestamp(row["reaction_date"]))
            if pos + h < len(col):
                fwd[i] = col.iloc[pos + h] / col.iloc[pos] - 1
        ic, t, n = rank_ic(pit["sue"], fwd)
        out["ic"][f"{h}d"] = {"ic": ic, "t": t, "n": n}
        if h == 20:
            pos_conf = pit["confirmed"] & (pit["sue"] > 0)
            ic_c, t_c, n_c = rank_ic(pit.loc[pos_conf, "sue"], fwd[pos_conf])
            out["ic"]["20d_confirmed_positive"] = {"ic": ic_c, "t": t_c, "n": n_c}

    n20 = out["ic"].get("20d", {}).get("n", 0)
    if n20 < N_PRIMARY:
        out["state"] = f"ACCUMULATING — n={n20} scoreable at 20d, primary test at n>={N_PRIMARY}"
    else:
        ic20, t20 = out["ic"]["20d"]["ic"], out["ic"]["20d"]["t"]
        if n20 >= N_KILL and (ic20 < 0.01 or t20 < 1):
            out["state"] = "KILL — pre-registered kill condition met"
        elif ic20 >= 0.03 and t20 >= 2:
            out["state"] = "PASS — pre-registered primary threshold met"
        else:
            out["state"] = "INDETERMINATE — between pass and kill thresholds"
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", action="store_true",
                    help="compute pre-registered ICs on point-in-time events")
    args = ap.parse_args()
    result = report() if args.report else collect()
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
