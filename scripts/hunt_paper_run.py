"""Nightly paper-book runner for the promoted hunt2026 books.

Four books (fixed registry below), each a frozen hunt2026 spec. Every night: build a fresh
panel (panel_2005.parquet history + latest yfinance ETF bars), take each spec's target_weights
LAST row as tonight's target book, size it to an equal share of account equity, log a ledger
row (targets, fills, nav, both benchmark navs) per book, and — only with --live — submit the
book to the ALPACA PAPER account (per-book tag in each client_order_id).

DEFAULT IS --dry-run: compute + print orders, write a ledger row marked "dry", submit NOTHING.
--live submits to Alpaca paper only (never real money). Do NOT run --live unattended before review.

Usage: .venv/bin/python scripts/hunt_paper_run.py --dry-run [--equity 100000]
       .venv/bin/python scripts/hunt_paper_run.py --live
"""
import argparse
import json
import sys
from pathlib import Path

import pandas as pd

HUNT = Path(__file__).resolve().parents[1] / "research" / "hunt2026"
sys.path.insert(0, str(HUNT))
import harness  # noqa: E402

META = json.loads((HUNT / "sandbox_meta.json").read_text())
SPECS = HUNT / "specs"
PANEL = HUNT / "panel_2005.parquet"
LEDGER_DIR = Path(__file__).resolve().parents[1] / "ledgers" / "hunt2026"
NAV_WINDOW = 252  # trailing days for the nav / benchmark-nav index (base 1.0)

# Fixed registry: book -> naive benchmark. "qqq" = bench_qqq_buyhold; "6040" = 60/40 SPY/BIL;
# "spy" = SPY buy-and-hold.
BOOKS = {
    "vol_managed_qqq": "qqq",   # core
    "vol_core_svxy": "qqq",
    "trend_vol_qqq": "qqq",
    "defensive_ensemble": "6040",
    "dual_momentum_gold": "spy",       # watch-tier (gold-menu hindsight; forward test decides)
    "momentum_concentrated": "spy",    # watch-tier (rank IC ~ 0, F-015/16; construction on trial)
    "dual_momentum_gem": "spy",        # watch-tier (whipsaw-fragile per 5y; forward test decides)
}


def build_live_panel(lookback_days: int = 20) -> pd.DataFrame:
    """panel_2005 history extended with the latest yfinance ETF/^VIX bars, ETF closes ffilled.

    Only the ETF + signal columns are refreshed (every hunt2026 book here is ETF-only). ffill heals
    stray holiday-calendar NaNs in the union index that would otherwise poison rolling windows.
    NETWORK — script-only; tests pass a fixture panel to compute_book directly.
    """
    from core.data.prices import fetch_prices_yf

    panel = pd.read_parquet(PANEL)
    tickers = [t for t in META["etfs"] + META["signal_only"] if t in panel["close"].columns]
    # stock books (momentum_concentrated) need fresh member-stock closes too
    member_last = panel["member"].iloc[-1]
    tickers += [t for t in member_last.index[member_last > 0]
                if t not in tickers and t in panel["close"].columns]
    start = (panel.index[-1] - pd.Timedelta(f"{lookback_days} days")).strftime("%Y-%m-%d")
    fresh = fetch_prices_yf(tickers, start=start, end=None)  # adjusted closes
    # ponytail: adjusted-close seam between panel and fresh may jog a few bps; fine for a signal
    idx = panel.index.union(fresh.index)
    close = panel["close"].reindex(idx)
    for t in fresh.columns:
        if t in close.columns:
            close[t] = fresh[t].reindex(idx).combine_first(close[t])
    out = {f: panel[f].reindex(idx) for f in ("open", "close", "volume", "member")}
    out["close"] = close
    out["member"] = out["member"].ffill()  # membership carries onto new dates
    p = pd.concat(out, axis=1)
    p.columns.names = ["field", "ticker"]
    return _heal_etfs(p)


def _heal_etfs(panel: pd.DataFrame) -> pd.DataFrame:
    """ffill ETF/signal closes (holiday-gap NaNs poison rolling windows). Idempotent; also cleans
    a raw fixture/cached panel before feeding specs."""
    tickers = [t for t in META["etfs"] + META["signal_only"] if t in panel["close"].columns]
    close = panel["close"].copy()
    close[tickers] = close[tickers].ffill()
    panel = panel.copy()
    panel["close"] = close
    return panel


def _nav(spec_mod, panel, start) -> float:
    return 1.0 + harness.run(spec_mod, panel, start=start)["total_net"]


def _spec_from_weights(W: pd.DataFrame):
    """Wrap a fixed weight frame as a harness spec: SPY held at the book's own gross exposure
    each day (the exposure-matched SPY benchmark)."""
    exposure = W.abs().sum(axis=1)

    class _S:
        @staticmethod
        def target_weights(p):
            c = p["close"]
            df = pd.DataFrame(0.0, index=c.index, columns=["SPY"])
            df["SPY"] = exposure.reindex(c.index).fillna(0.0)
            return df

    return _S


def _naive_spec(kind: str):
    if kind == "qqq":
        return harness.load_spec(SPECS / "bench_qqq_buyhold")
    if kind == "spy":
        class _Sspy:  # SPY buy-and-hold
            @staticmethod
            def target_weights(p):
                c = p["close"]
                df = pd.DataFrame(0.0, index=c.index, columns=["SPY"])
                df.loc[c["SPY"].notna(), "SPY"] = 1.0
                return df
        return _Sspy

    class _S6040:  # 60/40 SPY/BIL buy-and-hold
        @staticmethod
        def target_weights(p):
            c = p["close"]
            df = pd.DataFrame(0.0, index=c.index, columns=["SPY", "BIL"])
            df.loc[c["SPY"].notna(), "SPY"] = 0.6
            df.loc[c["BIL"].notna(), "BIL"] = 0.4
            return df

    return _S6040


def compute_book(panel: pd.DataFrame, name: str, notional: float) -> dict:
    """Tonight's book row for `name`, offline on `panel`. No network, no broker — the testable core."""
    panel = _heal_etfs(panel)
    spec = harness.load_spec(SPECS / name)
    W = spec.target_weights(panel).astype(float).fillna(0.0)
    last = W.iloc[-1]
    targets = {t: float(w) for t, w in last.items() if abs(w) > 1e-9}
    nav_start = panel.index[-min(NAV_WINDOW, len(panel) - 1)]
    res = harness.run(spec, panel, start=nav_start)
    return {
        "date": str(panel.index[-1].date()),
        "book": name,
        "targets": targets,
        "target_dollars": {t: round(w * notional, 2) for t, w in targets.items()},
        "gross": round(float(last.abs().sum()), 4),
        "notional": round(notional, 2),
        "nav": round(1.0 + res["total_net"], 6),
        # measurement-only: today's true net daily return. The `nav` above is a rolling
        # 252d-rebased index, so nav.pct_change() is NOT the daily return — the alpha-forward
        # layer (scripts/hunt_alpha_review.py) must read ret_1d.
        "ret_1d": round(float(res["net_daily"].iloc[-1]), 8),
        "bench_spy_nav": round(_nav(_spec_from_weights(W), panel, nav_start), 6),
        "bench_naive_nav": round(_nav(_naive_spec(BOOKS[name]), panel, nav_start), 6),
    }


def _write_ledger(row: dict) -> Path:
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    path = LEDGER_DIR / f"{row['book']}.jsonl"
    # ponytail: same-date re-runs replace the day's row instead of appending a dup
    # (idempotent per book+date+mode; a --dry-run after the nightly --live must not
    # erase the live row). Full rewrite is fine — ledgers are a few hundred rows.
    kept = []
    if path.exists():
        kept = [ln for ln in path.read_text().splitlines()
                if ln.strip() and not (
                    json.loads(ln).get("date") == row["date"]
                    and json.loads(ln).get("mode") == row.get("mode"))]
    kept.append(json.dumps(row))
    path.write_text("\n".join(kept) + "\n")
    return path


def _print_row(row: dict) -> None:
    print(f"\n[{row['mode']}] {row['book']}  {row['date']}  "
          f"gross {row['gross']:.2f}  notional ${row['notional']:,.0f}")
    print(f"  nav {row['nav']:.4f}  spy(exposure-matched) {row['bench_spy_nav']:.4f}  "
          f"naive {row['bench_naive_nav']:.4f}")
    for t, d in sorted(row["target_dollars"].items()):
        print(f"    {t:<6} w={row['targets'][t]:+.3f}  ${d:>14,.2f}")


def dry_run(equity: float) -> None:
    panel = build_live_panel()
    notional = equity / len(BOOKS)
    for name in BOOKS:
        row = compute_book(panel, name, notional)
        row["mode"], row["fills"] = "dry", []
        _print_row(row)
        _write_ledger(row)
    print(f"\nledgers -> {LEDGER_DIR}/  (dry-run: nothing submitted)")


def live_run() -> None:
    import os

    from core.env import load_dotenv
    from core.broker.alpaca import alpaca_paper_broker, snapshot_price_fn

    load_dotenv()
    key, secret = os.environ.get("ALPACA_API_KEY_ID"), os.environ.get("ALPACA_API_SECRET_KEY")
    if not (key and secret):
        sys.exit("--live needs ALPACA_API_KEY_ID / ALPACA_API_SECRET_KEY (paper keys) in env or .env")
    from alpaca.data.historical import StockHistoricalDataClient

    panel = build_live_panel()
    # every tradable symbol across the books (^VIX is signal-only, never held) PLUS every
    # currently-held name: reconcile must be able to price stale/foreign positions to
    # flatten them, or they silently persist (the price_fn returns None -> symbol skipped)
    symbols = sorted({t for name in BOOKS
                      for t in compute_book(panel, name, 1.0)["targets"]
                      if t not in META["signal_only"]})
    dc = StockHistoricalDataClient(key, secret)
    from alpaca.trading.client import TradingClient
    held_syms = [p.symbol for p in TradingClient(key, secret, paper=True).get_all_positions()]
    symbols = sorted(set(symbols) | set(held_syms))
    broker = alpaca_paper_broker(snapshot_price_fn(dc, symbols))   # repo's current-quote path
    acct = broker.account()
    equity = float(getattr(acct, "equity", None) or acct.cash)
    notional = equity / len(BOOKS)
    print(f"Alpaca paper equity ${equity:,.0f} -> ${notional:,.0f}/book across {len(BOOKS)} books")

    # Books are virtual: the account holds their SUM. Reconciling per book against shared
    # account positions would sell sibling books' shares (and zero any name the current book
    # doesn't hold), so aggregate all books into ONE account-level target and submit once.
    broker.cancel_all_orders()   # clear leftovers so the run is idempotent
    agg: dict[str, float] = {}
    rows = []
    for name in BOOKS:
        row = compute_book(panel, name, notional)
        row["mode"], row["fills"] = "live", []
        for t, d in row["target_dollars"].items():
            agg[t] = agg.get(t, 0.0) + d
        rows.append(row)
    broker.submit_targets(agg, tag="h26")
    fills = [f for f in broker.fills()
             if str(f.get("client_order_id") or "").startswith("h26")]
    errs = broker.order_errors()
    if errs:
        print(f"  account: {len(errs)} order(s) rejected (e.g. {errs[0]['ticker']}: "
              f"{errs[0]['error'][:70]})")
    for row in rows:
        _print_row(row)
        _write_ledger(row)
    _write_ledger({"date": rows[0]["date"], "book": "_account", "mode": "live",
                   "targets": {}, "target_dollars": {t: round(d, 2) for t, d in sorted(agg.items())},
                   "gross": round(sum(abs(d) for d in agg.values()) / equity, 4),
                   "notional": round(equity, 2), "nav": None, "bench_spy_nav": None,
                   "bench_naive_nav": None, "fills": fills})
    print(f"\nledgers -> {LEDGER_DIR}/  (live: one aggregate submission to Alpaca PAPER)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="compute + print, ledger marked dry, submit nothing")
    ap.add_argument("--live", action="store_true", help="submit tonight's books to Alpaca PAPER (needs keys)")
    ap.add_argument("--equity", type=float, default=100_000.0, help="dry-run: notional account equity to split")
    args = ap.parse_args()
    if args.live:
        live_run()
    else:  # default: dry-run (never submits)
        dry_run(args.equity)


if __name__ == "__main__":
    main()
