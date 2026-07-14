"""Scored headlines -> decision-session per-ticker signal, with conservative timing."""
import datetime as dt
from zoneinfo import ZoneInfo

import pandas as pd

NY = ZoneInfo("America/New_York")
HOLIDAYS = {
    # NYSE full-day closures covering the stored news window.
    "2025-11-27", "2025-12-25",
    "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25",
    "2026-06-19", "2026-07-03", "2026-09-07", "2026-11-26", "2026-12-25",
}


def _trading_day(day: dt.date) -> bool:
    return day.weekday() < 5 and day.isoformat() not in HOLIDAYS


def decision_session(published_at: str) -> str:
    """First close at which the headline can safely enter a signal.

    Before 16:00 ET on a trading day -> that close. At/after close, weekends, and
    holidays -> next trading close. The shared backtest then lags weights once, so
    positions cannot earn a return window that began before the headline existed.
    """
    ts = pd.Timestamp(published_at)
    if ts.tzinfo is None:
        raise ValueError("published_at must be timezone-aware")
    local = ts.tz_convert(NY)
    day = local.date()
    if _trading_day(day) and local.time() < dt.time(16, 0):
        return day.isoformat()
    day += dt.timedelta(days=1)
    while not _trading_day(day):
        day += dt.timedelta(days=1)
    return day.isoformat()


def daily_signal(scored: pd.DataFrame) -> pd.DataFrame:
    if scored.empty:
        raise ValueError("no scored headlines")
    if "published_at" not in scored:
        raise ValueError("published_at required for look-ahead-safe evaluation")
    df = scored.copy()
    df["decision_session"] = pd.to_datetime(df["published_at"].map(decision_session))
    return df.pivot_table(index="decision_session", columns="ticker", values="score",
                          aggfunc="mean")
