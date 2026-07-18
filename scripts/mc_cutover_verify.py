"""One-shot post-cutover verification for the momentum_concentrated account isolation
(memos/mc-account-isolation-cutover-2026-07-15.md). Pure ledger-file reads, no creds, no network,
no orders. Emits PASS/FAIL per check and exits non-zero on any failure.

Checks (for the latest live run date):
  1. shared _account row: written, submit_ok, targets are all ETFs (no single-stock leak)
  2. dedicated _account_mc row: written, submit_ok, targets are all momentum stocks (no ETF leak)
  3. both ledger rows exist for the same date
  4. no submit_ok=false on either account
  5. shared reconcile has the date and raises no FOREIGN/silent-flat alarm about MC stocks
  6. MC reconcile has the date and raises no alarm

Usage: .venv/bin/python scripts/mc_cutover_verify.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LED = ROOT / "ledgers" / "hunt2026"
META = json.loads((ROOT / "research" / "hunt2026" / "sandbox_meta.json").read_text())
ETFS = set(META["etfs"]) | set(META["signal_only"])


def _last_live(name):
    p = LED / f"{name}.jsonl"
    if not p.exists():
        return None
    rows = [json.loads(x) for x in p.read_text().splitlines() if json.loads(x).get("mode") == "live"]
    return rows[-1] if rows else None


def _last_reconcile(name):
    p = LED / f"{name}.jsonl"
    if not p.exists():
        return None
    lines = p.read_text().splitlines()
    return json.loads(lines[-1]) if lines else None


def main() -> int:
    acct = _last_live("_account")
    mc = _last_live("_account_mc")
    checks = []   # (ok, label)

    checks.append((acct is not None, "shared _account row written"))
    checks.append((mc is not None, "dedicated _account_mc row written"))
    if acct is None or mc is None:
        _report(checks)
        return 1

    date = acct["date"]
    checks.append((mc["date"] == date, f"both rows same date ({date} vs {mc['date']})"))
    checks.append((acct.get("submit_ok", True) is True, "shared submit_ok"))
    checks.append((mc.get("submit_ok", True) is True, "MC submit_ok"))

    shared_syms = set(acct.get("target_dollars", {}))
    mc_syms = set(mc.get("target_dollars", {}))
    checks.append((shared_syms <= ETFS, f"shared targets all ETFs (offenders: {sorted(shared_syms - ETFS)})"))
    checks.append((not (mc_syms & ETFS), f"MC targets carry no ETF (offenders: {sorted(mc_syms & ETFS)})"))
    checks.append((not (shared_syms & mc_syms), f"no symbol in both accounts (overlap: {sorted(shared_syms & mc_syms)})"))

    rec = _last_reconcile("_reconcile")
    checks.append((rec is not None and rec.get("date") == date, "shared reconcile ran for the date"))
    if rec:
        mc_book = "momentum_concentrated"
        checks.append((mc_book not in rec.get("books", {}), "MC excluded from shared reconcile"))
        bad = [a for a in rec.get("alarms", []) if "FOREIGN" in a or "SILENT" in a]
        checks.append((not bad, f"shared reconcile clean (alarms: {bad})"))

    mcr = _last_reconcile("_reconcile_mc")
    checks.append((mcr is not None and mcr.get("date") == date, "MC reconcile ran for the date"))
    if mcr:
        checks.append((not mcr.get("alarms"), f"MC reconcile clean (alarms: {mcr.get('alarms')})"))

    ok = _report(checks)
    print(f"\ncutover date under test: {date}")
    return 0 if ok else 1


def _report(checks) -> bool:
    all_ok = True
    for ok, label in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
        all_ok = all_ok and ok
    print(f"\n{'ALL CHECKS PASS' if all_ok else 'SOME CHECKS FAILED'}")
    return all_ok


if __name__ == "__main__":
    sys.exit(main())
