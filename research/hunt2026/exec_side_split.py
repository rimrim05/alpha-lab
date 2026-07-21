"""Is the dedicated book's execution cost real, or an artifact of the price it is scored against?

EXP-OPS-REALITY measures slippage against the run-date reference close, which the drift/exec split
in scripts/hunt_paper_reconcile.py separates into the overnight gap a fill inherits and what
execution cost after the opening auction. That exec leg came back at roughly +58 bps on
momentum_concentrated against a frozen cost model assuming 10 bps/side for single names, while the
shared ETF book read about zero. This decides whether to believe it.

The discriminator: a real cost is paid on both sides, so side-adjusted exec stays positive whether
we bought or sold. A mis-anchored price is the same direction for everybody and only the side
adjustment flips, so it shows up as a sign flip between buys and sells. Splitting again by the
crossing session's own direction separates a spread (indifferent to the tape) from a fill landing
after the opening print (charged the move).

Read-only: get_orders only, and nothing is written. Result as of 2026-07-21, 25 fills:

    buy   n=22  mean +62.1     sell  n=3   mean +25.0
    buy, tape fell   n=16  +42.1        buy, tape rose  n=6  +115.5
    sell, tape fell  n=3   +25.0        sell, tape rose n=0

No cell is negative, so the anchor explanation is out. The tape dependence says the fills land
after the open rather than at it. Caveats that bound all of it: three sell fills is not a sample,
a momentum book correlates side with tape by construction, and Alpaca's paper fill engine is a
simulation, so this bounds the backtest-vs-paper question and says nothing about live execution.

Usage: .venv/bin/python research/hunt2026/exec_side_split.py [--since 2026-07-15]
"""
import argparse
import datetime as dt
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from core.data.prices import fetch_closes_and_opens_yf   # noqa: E402
from core.env import load_dotenv                          # noqa: E402
from scripts.hunt_paper_reconcile import (MC_BOOK, MC_CRED_NAMES, bucket_orders,  # noqa: E402
                                          load_ledger_rows, opens_by_session,
                                          orders_from_client)


def mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def collect(since: str) -> list[dict]:
    """One row per comparable fill: its exec and drift legs, plus the tape it crossed into."""
    import os

    load_dotenv()
    key, secret = os.environ.get(MC_CRED_NAMES[0]), os.environ.get(MC_CRED_NAMES[1])
    if not (key and secret):
        sys.exit(f"needs {MC_CRED_NAMES[0]} / {MC_CRED_NAMES[1]} in env or .env")
    from alpaca.trading.client import TradingClient

    ledger = load_ledger_rows()
    tc = TradingClient(key, secret, paper=True)          # read-only: get_orders
    orders = orders_from_client(tc, since=since, statuses="all")
    dates = sorted(d for d in ledger if d >= since and MC_BOOK in ledger[d])
    buckets = bucket_orders(orders, dates)

    symbols = sorted({o["ticker"] for o in orders})
    start = (dt.date.fromisoformat(since) - dt.timedelta(days=7)).isoformat()
    px, op = fetch_closes_and_opens_yf(symbols, start=start, end=None)
    opens = opens_by_session(op)
    closes = {str(d)[:10]: {s: float(v) for s, v in row.items() if v == v}
              for d, row in px.iterrows()}

    rows = []
    for d in dates:
        # the reference the reconcile scores against: last session at or before the run date
        eligible = [s for s in closes if s <= d]
        if not eligible:
            continue
        ref_session = max(eligible)
        for o in buckets.get(d, []):
            sess = o.get("filled_session")
            if not (o["fill_price"] and o["filled_qty"] and sess):
                continue
            ref = closes[ref_session].get(o["ticker"])
            open_px = (opens.get(sess) or {}).get(o["ticker"])
            sess_close = (closes.get(sess) or {}).get(o["ticker"])
            if not (ref and open_px and sess_close):
                continue
            sign = 1.0 if o["side"] == "buy" else -1.0
            rows.append({
                "sym": o["ticker"], "side": o["side"], "run_date": d, "session": sess,
                "exec_bps": sign * (o["fill_price"] - open_px) / ref * 1e4,
                "drift_bps": sign * (open_px - ref) / ref * 1e4,
                "tape_bps": (sess_close - open_px) / open_px * 1e4,   # the session's own move
            })
    return rows


def report(rows: list[dict]) -> None:
    if not rows:
        print("no comparable fills")
        return
    print(f"{MC_BOOK}: {len(rows)} fills\n")
    for side in ("buy", "sell"):
        xs = [r["exec_bps"] for r in rows if r["side"] == side]
        if xs:
            print(f"  {side:<4} n={len(xs):<3} exec mean {mean(xs):+8.1f}  median "
                  f"{sorted(xs)[len(xs) // 2]:+8.1f}  min {min(xs):+8.1f}  max {max(xs):+8.1f}")

    print("\n  by side and by the crossing session's direction "
          "(a real cost is positive in every cell):")
    cells = defaultdict(list)
    for r in rows:
        cells[(r["side"], r["tape_bps"] > 0)].append(r["exec_bps"])
    for (side, up), xs in sorted(cells.items()):
        print(f"    {side:<4} tape {'rose' if up else 'fell'}  n={len(xs):<3} mean {mean(xs):+8.1f}")

    print("\n  per fill:")
    for r in sorted(rows, key=lambda r: (r["run_date"], r["sym"])):
        print(f"    {r['run_date']}  {r['sym']:<5} {r['side']:<4} exec {r['exec_bps']:+8.1f}  "
              f"drift {r['drift_bps']:+8.1f}  tape {r['tape_bps']:+8.1f}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-07-15",
                    help="first run date to include (default: the dedicated-account cutover)")
    report(collect(ap.parse_args().since))


if __name__ == "__main__":
    main()
