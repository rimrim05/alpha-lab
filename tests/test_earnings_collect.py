import datetime as dt
import json

import pandas as pd
import pytest

import scripts.earnings_collect as ec


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setattr(ec, "EVENTS_PATH", tmp_path / "events.jsonl")
    monkeypatch.setattr(ec, "REACTIONS_PATH", tmp_path / "reactions.jsonl")
    return tmp_path


def test_append_dedupes_on_symbol_period(store):
    rows = [{"symbol": "AAPL", "period": "2026-06-30", "x": 1},
            {"symbol": "MSFT", "period": "2026-06-30", "x": 2}]
    assert ec.append_new_events(ec.EVENTS_PATH, rows) == 2
    assert ec.append_new_events(ec.EVENTS_PATH, rows + [
        {"symbol": "AAPL", "period": "2026-03-31", "x": 3}]) == 1
    assert len(ec.load_jsonl(ec.EVENTS_PATH)) == 3


def test_collect_flags_only_fresh_row_point_in_time(store, monkeypatch):
    monkeypatch.setattr(ec, "sp500_members", lambda: {"DAL", "AAPL"})
    calendar = {"earningsCalendar": [
        {"symbol": "DAL", "date": "2026-07-09", "hour": "bmo",
         "epsActual": 2.1, "epsEstimate": 2.0},
        {"symbol": "AAPL", "date": "2026-07-15", "hour": "amc",   # not yet reported
         "epsActual": None, "epsEstimate": 1.5},
        {"symbol": "ZZZZ", "date": "2026-07-09", "hour": "bmo",   # non-member
         "epsActual": 9.9, "epsEstimate": 9.0},
    ]}
    history = [
        {"symbol": "DAL", "period": "2026-06-30", "estimate": 2.0, "actual": 2.1,
         "surprise": 0.1, "surprisePercent": 5.0},
        {"symbol": "DAL", "period": "2026-03-31", "estimate": 1.8, "actual": 1.7,
         "surprise": -0.1, "surprisePercent": -5.6},
    ]

    def fake_get(path, **params):
        if path == "calendar/earnings":
            return calendar
        assert params["symbol"] == "DAL"
        return history
    monkeypatch.setattr(ec, "_get", fake_get)
    monkeypatch.setattr(ec, "snapshot_reactions", lambda today: 0)

    summary = ec.collect(today=dt.date(2026, 7, 10))
    assert summary["events_added"] == 2
    events = {e["period"]: e for e in ec.load_jsonl(ec.EVENTS_PATH)}
    assert events["2026-06-30"]["point_in_time"] is True
    assert events["2026-06-30"]["report_date"] == "2026-07-09"
    assert events["2026-03-31"]["point_in_time"] is False
    assert events["2026-03-31"]["report_date"] is None
    assert summary["upcoming_members"] == ["AAPL"]


def test_reaction_session_bmo_vs_amc():
    assert ec.reaction_session("2026-07-09", "bmo") == dt.date(2026, 7, 9)
    assert ec.reaction_session("2026-07-09", "amc") == dt.date(2026, 7, 10)
    assert ec.reaction_session("2026-07-09", None) == dt.date(2026, 7, 10)


def test_sue_scaling_rules():
    ev = pd.DataFrame([
        # A has 2 prior surprises -> scale = std of them
        {"symbol": "A", "period": "2025-12-31", "estimate": 1.0, "actual": 1.1, "surprise": 0.1},
        {"symbol": "A", "period": "2026-03-31", "estimate": 1.0, "actual": 0.7, "surprise": -0.3},
        {"symbol": "A", "period": "2026-06-30", "estimate": 2.0, "actual": 2.4, "surprise": 0.4},
        # B has no history -> scale = |estimate|
        {"symbol": "B", "period": "2026-06-30", "estimate": -2.0, "actual": -1.0, "surprise": 1.0},
    ])
    sue = ec.compute_sue(ev)
    expected_a = 0.4 / pd.Series([0.1, -0.3]).std()
    assert sue[2] == pytest.approx(expected_a)
    assert sue[3] == pytest.approx(0.5)  # (-1 - -2) / |-2|


def test_report_accumulating_state_with_no_pit_events(store):
    # history-only store: everything excluded from the primary test
    ec.append_new_events(ec.EVENTS_PATH, [
        {"pulled_at": "x", "symbol": "A", "period": "2025-12-31", "report_date": None,
         "hour": None, "estimate": 1.0, "actual": 1.2, "surprise": 0.2,
         "surprise_pct": 20.0, "point_in_time": False}])
    out = ec.report()
    assert out["events_point_in_time"] == 0
    assert out["events_excluded_stale"] == 1
    assert out["state"].startswith("ACCUMULATING")
    assert out["ic"] == {}


def test_report_ic_on_synthetic_events():
    # 6 PIT events, forward return perfectly monotone in SUE -> IC == 1
    events, reactions = [], []
    prices = {}
    dates = pd.bdate_range("2026-07-01", periods=80)
    for i, sym in enumerate(["A", "B", "C", "D", "E", "F"]):
        events.append({"pulled_at": "x", "symbol": sym, "period": "2026-06-30",
                       "report_date": "2026-07-01", "hour": "bmo",
                       "estimate": 1.0, "actual": 1.0 + 0.1 * i,
                       "surprise": 0.1 * i, "surprise_pct": 10.0 * i,
                       "point_in_time": True})
        reactions.append({"symbol": sym, "period": "2026-06-30",
                          "reaction_date": "2026-07-01", "open": 100.0,
                          "close": 101.0, "pulled_at": "x"})
        # price drifts up at a rate increasing with i
        prices[sym] = pd.Series(100 * (1 + 0.001 * i) ** pd.RangeIndex(80).values,
                                index=dates)
    out = ec.report(events=events, reactions=reactions,
                    prices=pd.DataFrame(prices))
    for h in ("5d", "20d", "60d"):
        assert out["ic"][h]["ic"] == pytest.approx(1.0)
        assert out["ic"][h]["n"] == 6
    assert "20d_confirmed_positive" in out["ic"]
    assert out["state"].startswith("ACCUMULATING")  # n=6 << 300
