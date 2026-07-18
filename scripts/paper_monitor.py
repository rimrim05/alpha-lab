"""paper_monitor.py: read-only monitoring cadence + email alerts for the hunt2026 paper system.

This is the OBSERVER, not the trader. It NEVER submits/cancels/replaces orders, never recomputes
strategy targets, never writes any ledger or DEPLOYMENT_MANIFEST.md. Its ONLY writes are its own
observability artifacts under artifacts/hunt2026/paper/monitor/ (snapshots + last-alert state).
It reuses paper_status.build_status() for the (read-only) picture of the system.

Roles (chosen per launchd job, not inferred):
  --role watch    : intraday polls. Writes a snapshot every run. Emails ONLY when the alarm
                    signature CHANGES (new problem, changed problem, or recovery); no spam when
                    the same condition persists across polls.
  --role summary  : one post-close run. Always emails a concise daily summary (or the exception).

Email: SMTP (Gmail) using a credential file ~/.config/rimrimos/alpha_alert_smtp.json:
  {"user": "you@gmail.com", "app_password": "<16-char app password>", "to": "kris10harim@gmail.com"}
If that file is absent, the monitor still writes the local snapshot and logs that email is
unconfigured; it never crashes and never blocks Monday's read-only observation.

Usage: .venv/bin/python scripts/paper_monitor.py --role watch
Exit:  always 0 (a monitor must not make launchd retry); problems are reported, not raised.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.paper_status import build_status, render  # read-only status assembly

MON_DIR = ROOT / "artifacts" / "hunt2026" / "paper" / "monitor"
STATE = MON_DIR / "last_alert.json"
SMTP_CRED = Path.home() / ".config" / "rimrimos" / "alpha_alert_smtp.json"


# ---------- pure core (offline-testable) ----------

def signature(status: dict) -> str:
    """Stable fingerprint of the OPERATIONAL condition; ignores volatile dollar amounts so
    identical conditions across polls collapse to one alert. Changes when the situation changes."""
    rh = status.get("run_health", {})
    broker = status.get("broker", {})
    gate = status.get("gate", {})
    clock = status.get("clock", {})
    # alarm *categories* (prefix before ':'), sorted, not the full text with dollar figures
    cats = sorted({a.split(":", 1)[0].strip() for a in status.get("alarms", [])})
    parts = [
        rh.get("status", "?"),
        "brokerOK" if broker.get("ok") else "brokerDOWN",
        gate.get("overall", "?"),
        clock.get("state", "?"),
        f"foreign={'y' if (broker.get('ok') and broker.get('foreign_n', 0) > 0) else 'n'}",
        f"silentflat={status.get('silent_flat')}",
        "|".join(cats),
    ]
    return "; ".join(parts)


def should_email(role: str, status: dict, last_sig: str | None) -> bool:
    """summary always emails; watch emails only on a signature change (incl. recovery to clean)."""
    if role == "summary":
        return True
    return signature(status) != (last_sig or "")


def subject_line(role: str, status: dict, code: int) -> str:
    rh = status.get("run_health", {}).get("status", "?")
    n_alarms = len(status.get("alarms", []))
    if role == "summary" and code == 0:
        return "Alpha Lab daily: healthy — no action required"
    if n_alarms == 0 and code == 0:
        return "Alpha Lab: recovered — no active alarms"
    tag = "MANUAL ACTION" if code == 2 else "attention"
    return f"Alpha Lab {tag}: {n_alarms} alarm(s), run {rh}"


# ---------- I/O ----------

def _read_state() -> str | None:
    try:
        return json.loads(STATE.read_text()).get("signature")
    except Exception:
        return None


def _write_snapshot_and_state(role: str, body: str, sig: str, now: dt.datetime,
                              emailed: bool) -> Path:
    MON_DIR.mkdir(parents=True, exist_ok=True)
    snap = MON_DIR / f"{now.strftime('%Y-%m-%dT%H%M')}_{role}.txt"
    snap.write_text(body)
    # only the alert-dedup state records the signature; snapshots are the full audit trail
    STATE.write_text(json.dumps({"signature": sig, "ts": now.isoformat(timespec="seconds"),
                                 "emailed": emailed, "role": role}))
    return snap


def _send_email(subject: str, body: str) -> tuple[bool, str]:
    """Send via SMTP if the credential file exists. Returns (sent, note). Never raises."""
    if not SMTP_CRED.exists():
        return False, f"email unconfigured (no {SMTP_CRED})"
    try:
        cred = json.loads(SMTP_CRED.read_text())
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = cred["user"]
        msg["To"] = cred.get("to", cred["user"])
        msg.set_content(body)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as s:
            s.login(cred["user"], cred["app_password"])
            s.send_message(msg)
        return True, "sent"
    except Exception as e:  # bad creds / network / SMTP: log, never crash the monitor
        return False, f"email failed: {type(e).__name__}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", choices=("watch", "summary"), default="watch")
    args = ap.parse_args()

    now = dt.datetime.now()
    status, code = build_status(now)
    sig = signature(status)
    body = render(status)

    last_sig = _read_state()
    emailed, note = False, "not sent (no change)"
    if should_email(args.role, status, last_sig):
        subject = subject_line(args.role, status, code)
        emailed, note = _send_email(subject, body + f"\n\n[{args.role} · exit {code}]")

    snap = _write_snapshot_and_state(args.role, body, sig, now, emailed)
    print(f"[monitor:{args.role}] snapshot -> {snap.name}  exit_code={code}  email: {note}")
    return 0  # monitor never fails launchd; the status exit code is inside the snapshot


if __name__ == "__main__":
    sys.exit(main())
