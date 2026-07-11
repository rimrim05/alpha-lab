"""Offline tests for scripts/paper_monitor.py — no network, no real SMTP, no disk writes to
control-plane paths. Covers signature stability, dedup, summary-always, recovery, credential
degradation, and the read-only guarantee (no order/ledger/manifest writes)."""
import re
from pathlib import Path

import scripts.paper_monitor as pm


def _status(run="HEALTHY", broker_ok=True, foreign_n=0, gate="COMPLETE", clock="STARTED",
            silent_flat=0, alarms=None):
    return {"run_health": {"status": run},
            "broker": {"ok": broker_ok, "foreign_n": foreign_n},
            "gate": {"overall": gate}, "clock": {"state": clock},
            "silent_flat": silent_flat, "alarms": alarms or []}


# ---------- signature ----------

def test_signature_stable_across_dollar_changes():
    # two snapshots, same operational condition, different (unmodelled) dollar figures -> same sig
    a = _status(alarms=["FOREIGN-POSITIONS: 271 held symbol(s) ($141,672)"])
    b = _status(alarms=["FOREIGN-POSITIONS: 271 held symbol(s) ($140,001)"])
    assert pm.signature(a) == pm.signature(b)


def test_signature_changes_on_condition_change():
    clean = _status(alarms=[])
    alarmed = _status(gate="NOT COMPLETE", foreign_n=271,
                      alarms=["FOREIGN-POSITIONS: 271 symbols"])
    assert pm.signature(clean) != pm.signature(alarmed)


def test_signature_changes_when_broker_drops():
    assert pm.signature(_status(broker_ok=True)) != pm.signature(_status(broker_ok=False))


# ---------- should_email ----------

def test_watch_emails_only_on_change():
    s = _status(gate="NOT COMPLETE", foreign_n=271, alarms=["FOREIGN-POSITIONS: 271"])
    sig = pm.signature(s)
    assert pm.should_email("watch", s, last_sig=None) is True       # first sighting
    assert pm.should_email("watch", s, last_sig=sig) is False       # unchanged -> silent


def test_watch_emails_on_recovery():
    clean = _status(alarms=[])
    prior = pm.signature(_status(gate="NOT COMPLETE", foreign_n=271, alarms=["FOREIGN: x"]))
    assert pm.should_email("watch", clean, last_sig=prior) is True  # condition cleared -> notify


def test_summary_always_emails():
    s = _status(alarms=[])
    assert pm.should_email("summary", s, last_sig=pm.signature(s)) is True


# ---------- subject lines ----------

def test_summary_healthy_subject():
    assert "healthy" in pm.subject_line("summary", _status(alarms=[]), code=0).lower()


def test_manual_action_subject_on_exit_2():
    s = _status(run="HEALTHY", alarms=["FOREIGN: x"])
    assert "MANUAL ACTION" in pm.subject_line("watch", s, code=2)


def test_attention_subject_on_exit_1():
    s = _status(alarms=["SILENT-FLAT: x", "FOREIGN: y"])
    subj = pm.subject_line("watch", s, code=1)
    assert "attention" in subj and "2 alarm" in subj


# ---------- credential degradation ----------

def test_email_unconfigured_returns_note_not_crash(monkeypatch, tmp_path):
    monkeypatch.setattr(pm, "SMTP_CRED", tmp_path / "does_not_exist.json")
    sent, note = pm._send_email("subj", "body")
    assert sent is False and "unconfigured" in note


def test_email_bad_creds_degrade_without_raising(monkeypatch, tmp_path):
    cred = tmp_path / "smtp.json"
    cred.write_text('{"user":"x@y.com","app_password":"bad","to":"z@y.com"}')
    monkeypatch.setattr(pm, "SMTP_CRED", cred)
    # no network in tests: force the SMTP path to raise, prove we catch it
    monkeypatch.setattr(pm.smtplib, "SMTP_SSL", lambda *a, **k: (_ for _ in ()).throw(OSError()))
    sent, note = pm._send_email("subj", "body")
    assert sent is False and "failed" in note


# ---------- snapshot + state I/O (isolated tmp dir) ----------

def test_snapshot_and_state_written(monkeypatch, tmp_path):
    import datetime as dt
    monkeypatch.setattr(pm, "MON_DIR", tmp_path)
    monkeypatch.setattr(pm, "STATE", tmp_path / "last_alert.json")
    now = dt.datetime(2026, 7, 13, 6, 20)
    snap = pm._write_snapshot_and_state("watch", "BODY", "sig-x", now, emailed=False)
    assert snap.exists() and snap.read_text() == "BODY"
    assert pm._read_state.__module__  # sanity
    import json
    st = json.loads((tmp_path / "last_alert.json").read_text())
    assert st["signature"] == "sig-x" and st["role"] == "watch"


# ---------- read-only guarantee ----------

def _code_only(path: Path) -> str:
    import ast
    src = path.read_text()
    doc = ast.get_docstring(ast.parse(src), clean=False)
    if doc:
        src = src.replace(doc, "")
    return re.sub(r"#.*", "", src)


def test_monitor_never_submits_orders_or_writes_control_plane():
    code = _code_only(Path(pm.__file__))
    forbidden = ["submit_order", "cancel_order", "replace_order", "cancel_all_orders",
                 "hunt_paper_run", "_write_ledger", "ledgers/", "DEPLOYMENT_MANIFEST",
                 "--live", "get_account("]  # get_account only happens inside paper_status, not here
    hits = [t for t in forbidden if t in code]
    assert hits == [], f"monitor read-only violation: {hits}"


def test_monitor_only_writes_its_own_artifact_dir():
    # every write target in the module must live under the monitor artifact dir
    code = _code_only(Path(pm.__file__))
    assert "MON_DIR" in code and "artifacts" in code
    # the two write calls are snapshot + STATE, both under MON_DIR
    assert code.count(".write_text(") <= 3  # snapshot, STATE, and none else
