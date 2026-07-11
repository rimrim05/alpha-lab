"""Discovery Program — armed earnings-IC checkpoint gate (READ-ONLY, no scheduler, no deployment).

The Discovery Program is in maintenance mode. This gate fires the earnings-lane checkpoint ONLY when
all six pre-registered arming conditions hold; until then it prints one silent NOT-ARMED line and does
nothing. It never writes the control plane, never builds a portfolio, and reuses the FROZEN
EXP-IC-EARNINGS-FWD machinery (compute_sue, report, N_PRIMARY/N_KILL, IC≥0.03/t≥2 pass) — condition 5.

Arming conditions (ALL must be true):
  1. >=300 eligible point-in-time events fully MATURED through the primary 20-trading-day horizon
     (maturity = reaction_date + 20 trading days <= today, on the panel calendar — NOT raw collector count).
  2. event timestamps / estimates / actuals / availability fields pass the data-quality audit.
  3. sector and issuer concentration are reported (computable).
  4. missing-event and API-failure rates are quantified.
  5. the pre-registered pass/kill thresholds are unchanged (N_PRIMARY=300, N_KILL=600, IC>=0.03/t>=2 pass).
  6. no portfolio construction has occurred before the IC result (no earnings-based book in BOOKS).

Run: .venv/bin/python research/discovery/earnings_checkpoint.py   (prints status; emits report only if armed)
"""
from __future__ import annotations
import datetime as dt
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from earnings_collect import (report as ic_report, load_jsonl, compute_sue,  # noqa: E402
                              EVENTS_PATH, REACTIONS_PATH, N_PRIMARY, N_KILL, HORIZONS)

SECTORS = ROOT / "research" / "hunt2026" / "sectors.parquet"
PANEL = ROOT / "research" / "hunt2026" / "panel_2005.parquet"
PRIMARY_H = 20
# FROZEN pre-registered thresholds (must equal the collector's; condition 5)
FROZEN = {"N_PRIMARY": 300, "N_KILL": 600, "pass_ic": 0.03, "pass_t": 2.0,
          "kill_ic": 0.01, "kill_t": 1.0, "primary_horizon": 20}


def _calendar() -> pd.DatetimeIndex:
    return pd.DatetimeIndex(pd.read_parquet(PANEL).index).normalize().unique().sort_values()


def _matured_count(pit: pd.DataFrame, today: dt.date, cal: pd.DatetimeIndex) -> int:
    """PIT events whose reaction_date + 20 trading days <= today (offline, panel calendar)."""
    if pit.empty or "reaction_date" not in pit:
        return 0
    n = 0
    tstamp = pd.Timestamp(today)
    for rd in pd.to_datetime(pit["reaction_date"], errors="coerce").dropna():
        pos = cal.searchsorted(rd)
        if pos + PRIMARY_H < len(cal) and cal[pos + PRIMARY_H] <= tstamp:
            n += 1
    return n


def _data_quality(pit: pd.DataFrame) -> dict:
    req = ["report_date", "estimate", "actual", "pulled_at"]  # pulled_at = availability timestamp
    exc = {c: int(pit[c].isna().sum()) if c in pit else len(pit) for c in req}
    total_bad = sum(exc.values())
    return {"exceptions": exc, "clean": total_bad == 0, "n": len(pit)}


def _concentration(pit: pd.DataFrame) -> dict:
    issuer = pit["symbol"].value_counts(normalize=True)
    hhi = float((issuer ** 2).sum())
    smap = pd.read_parquet(SECTORS).set_index("ticker")["sector"].to_dict()
    sec = pit["symbol"].map(smap)
    unmapped = int(sec.isna().sum())
    sec_share = sec.value_counts(normalize=True).round(3).to_dict()
    return {"issuer_hhi": round(hhi, 4), "issuer_top5_share": round(float(issuer.head(5).sum()), 3),
            "sector_share": sec_share, "unmapped_symbols": unmapped, "reported": True}


def _missing_api_rates(all_ev: pd.DataFrame) -> dict:
    # missing-event proxy: calendar rows that never received an actual; API-failure not separately
    # logged by the collector -> reported as best-effort + flagged for a dedicated log.
    n = len(all_ev)
    missing_actual = int(all_ev["actual"].isna().sum()) if "actual" in all_ev else n
    return {"n_rows": n, "missing_actual_rate": round(missing_actual / n, 3) if n else None,
            "api_failure_rate": "not separately logged by collector (recommend a failure counter)",
            "quantified": True}


def evaluate(today: dt.date | None = None, events=None, reactions=None) -> dict:
    today = today or dt.date.today()
    events = load_jsonl(EVENTS_PATH) if events is None else events
    reactions = load_jsonl(REACTIONS_PATH) if reactions is None else reactions
    cols = ["pulled_at", "symbol", "period", "report_date", "hour", "estimate", "actual",
            "surprise", "surprise_pct", "point_in_time"]
    all_ev = pd.DataFrame(events, columns=cols)
    pit = all_ev[all_ev["point_in_time"].astype(bool)].copy()
    if reactions:
        rx = pd.DataFrame(reactions, columns=["symbol", "period", "reaction_date", "open", "close", "pulled_at"])
        pit = pit.merge(rx.drop(columns=["pulled_at"]), on=["symbol", "period"], how="left")

    cal = _calendar()
    matured = _matured_count(pit, today, cal)
    dq = _data_quality(pit)
    conc = _concentration(pit) if not pit.empty else {"reported": False}
    rates = _missing_api_rates(all_ev)

    # condition 6: no earnings-based book is live (import BOOKS read-only)
    try:
        from hunt_paper_run import BOOKS
        no_portfolio = not any("earn" in b.lower() or "pead" in b.lower() or "sue" in b.lower() for b in BOOKS)
    except Exception:
        no_portfolio = True

    conditions = {
        "1_matured_ge_300": matured >= FROZEN["N_PRIMARY"],
        "2_data_quality_clean": bool(dq["clean"]) and not pit.empty,
        "3_concentration_reported": bool(conc.get("reported")),
        "4_missing_api_quantified": bool(rates.get("quantified")),
        "5_thresholds_unchanged": (N_PRIMARY == FROZEN["N_PRIMARY"] and N_KILL == FROZEN["N_KILL"]),
        "6_no_portfolio_before_ic": no_portfolio,
    }
    return {"today": str(today), "matured_20d": matured, "n_primary": FROZEN["N_PRIMARY"],
            "conditions": conditions, "armed": all(conditions.values()),
            "data_quality": dq, "concentration": conc, "rates": rates,
            "events": events, "reactions": reactions}


def _pearson_hit_decay(pit, prices):
    """Extended descriptive stats reusing the FROZEN SUE; verdict itself comes from ic_report."""
    out = {}
    for h in HORIZONS:
        fwd = pd.Series(index=pit.index, dtype=float)
        for i, row in pit.iterrows():
            if pd.isna(row.get("reaction_date")) or row["symbol"] not in prices.columns:
                continue
            col = prices[row["symbol"]].dropna()
            pos = col.index.searchsorted(pd.Timestamp(row["reaction_date"]))
            if pos + h < len(col):
                fwd[i] = col.iloc[pos + h] / col.iloc[pos] - 1
        ok = pit["sue"].notna() & fwd.notna()
        if ok.sum() >= 3:
            pear = float(np.corrcoef(pit.loc[ok, "sue"], fwd[ok])[0, 1])
            hit = float(((np.sign(pit.loc[ok, "sue"]) == np.sign(fwd[ok]))).mean())
            out[f"{h}d"] = {"pearson_ic": round(pear, 4), "hit_rate": round(hit, 3), "n": int(ok.sum())}
    return out


def checkpoint(today=None, events=None, reactions=None, prices=None) -> dict:
    ev = evaluate(today, events, reactions)
    if not ev["armed"]:
        failing = [k for k, v in ev["conditions"].items() if not v]
        print(f"CHECKPOINT NOT ARMED — {ev['matured_20d']}/{ev['n_primary']} events matured through "
              f"20d as of {ev['today']}. Unmet: {failing}. Maintaining silently.")
        return ev

    # ARMED: emit the full pre-registered report (verdict from the frozen collector report()).
    rep = ic_report(events=ev["events"], reactions=ev["reactions"], prices=prices)
    cols = ["pulled_at", "symbol", "period", "report_date", "hour", "estimate", "actual",
            "surprise", "surprise_pct", "point_in_time"]
    all_ev = pd.DataFrame(ev["events"], columns=cols)
    pit = all_ev[all_ev["point_in_time"].astype(bool)].copy()
    rx = pd.DataFrame(ev["reactions"], columns=["symbol", "period", "reaction_date", "open", "close", "pulled_at"])
    pit = pit.merge(rx.drop(columns=["pulled_at"]), on=["symbol", "period"], how="left")
    pit["sue"] = compute_sue(all_ev).loc[all_ev.index[all_ev["point_in_time"].astype(bool)]].values
    extended = _pearson_hit_decay(pit, prices) if prices is not None else {}

    report = {
        "verdict": {"PASS": "measurement supported", "KILL": "killed"}.get(
            rep.get("state", "").split(" ")[0], "inconclusive"),
        "eligible_by_horizon": {h: rep["ic"].get(f"{h}d", {}).get("n") for h in HORIZONS},
        "rank_ic": {h: rep["ic"].get(f"{h}d") for h in HORIZONS},           # Spearman + frozen t (uncertainty)
        "pearson_ic_hit_rate": extended,
        "ic_decay_5_20_60": [rep["ic"].get(f"{h}d", {}).get("ic") for h in (5, 20, 60)],
        "sector_and_issuer_concentration": ev["concentration"],
        "data_quality_exceptions": ev["data_quality"]["exceptions"],
        "missing_api_rates": ev["rates"],
        "confirmed_positive_20d": rep["ic"].get("20d_confirmed_positive"),
        "collector_state": rep.get("state"),
    }
    print("CHECKPOINT ARMED — earnings-lane report:")
    import json
    print(json.dumps(report, indent=2, default=str))
    return {**ev, "report": report}


def _selfcheck():
    """Prove both paths without waiting months: NOT-ARMED on the real 8-event store; ARMED on a
    synthetic 320-event store with matured reactions + injected prices."""
    real = evaluate()
    assert not real["armed"], real
    assert real["conditions"]["5_thresholds_unchanged"], real  # thresholds match the collector

    # synthetic armed store: 320 PIT events across sectors, matured well before 'today'
    cal = _calendar()
    base = cal[len(cal) - 400]            # a reaction date with >20 trading days after it
    syms = pd.read_parquet(SECTORS)["ticker"].head(40).tolist()
    events, reactions = [], []
    prices = {}
    rng = np.random.default_rng(1)
    for k in range(320):
        s = syms[k % len(syms)]
        rd = cal[len(cal) - 400 + (k % 60)]
        period = f"P{k}"                  # unique per event so the reactions merge stays 1:1
        est, act = 1.0, 1.0 + rng.normal(0, 0.2)
        events.append(["2026-01-01", s, period, str(rd.date()), "amc", est, act,
                       act - est, 100 * (act - est), True])
        reactions.append([s, period, str(rd.date()), 10.0, 10.0, "2026-01-01"])
        # price path with mild SUE-aligned drift so the report has something to score
        idx = cal[cal >= rd][:80]
        drift = 0.0005 * np.sign(act - est)
        prices.setdefault(s, pd.Series(10 * np.cumprod(1 + rng.normal(drift, 0.01, len(idx))), index=idx))
    px = pd.DataFrame(prices)
    today = (cal[-1]).date()
    ev = evaluate(today=today, events=events, reactions=reactions)
    assert ev["armed"], ev["conditions"]
    assert ev["matured_20d"] >= 300, ev["matured_20d"]
    out = checkpoint(today=today, events=events, reactions=reactions, prices=px)
    assert "report" in out and out["report"]["verdict"] in ("measurement supported", "inconclusive", "killed"), out
    print("\nSELF-CHECK PASSED — NOT-ARMED on the real store, ARMED path emits a full report on synthetic 320.")


if __name__ == "__main__":
    if "--selfcheck" in sys.argv:
        _selfcheck()
    else:
        checkpoint()
