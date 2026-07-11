"""paper_publish.py — publish the read-only paper STATUS to GitHub as an insights surface.

Option A (local): a launchd job runs this on a schedule. It reuses paper_status.build_status()
+ render() (the SAME reconciliation / gate / broker-snapshot text you get on the CLI), wraps it
into STATUS.md at the repo root, and commits + pushes ONLY when the text actually changed.

Why a separate script (not paper_status.py): paper_status is STRICTLY READ-ONLY and test-enforced.
The one write (STATUS.md) and all git plumbing live here so that guarantee stays intact.

Keys stay on this Mac: build_status() loads them from .env via core.env.load_dotenv(); .env is
gitignored, so the published STATUS.md carries positions/equity/gate — never credentials.

Robustness: git network ops are best-effort with prompts disabled and a timeout. If push fails
(offline, auth), the local commit persists and the next run carries it — the job never hangs and
never crashes launchd.

Usage:
  .venv/bin/python scripts/paper_publish.py            # write STATUS.md, commit+push on change
  .venv/bin/python scripts/paper_publish.py --dry-run  # write STATUS.md only, no git
  .venv/bin/python scripts/paper_publish.py --selfcheck # offline assert on the markdown wrapper
"""
from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

STATUS_MD = ROOT / "STATUS.md"
PAGES_DASHBOARD = "https://rimrim05.github.io/alpha-lab/dashboard.html"


def render_markdown(status_text: str, generated: str, code: int) -> str:
    """Pure: wrap the plaintext paper_status report into the committed STATUS.md.
    GitHub renders this file directly — it IS the insights dashboard (Alpaca stays the live view)."""
    verdict = {0: "🟢 nominal", 1: "🟡 operational alarm", 2: "🔴 manual action / source unreachable"}
    return (
        "# Paper status — Alpha Lab hunt2026\n\n"
        f"**{verdict.get(code, '⚪ unknown')}** · refreshed `{generated}` "
        "(auto, from Kristen's Mac — hourly, commits only on change)\n\n"
        f"This is the read-only reconciliation / gate / broker snapshot. "
        f"Live trading view → [Alpaca paper dashboard](https://app.alpaca.markets/paper/dashboard/overview) · "
        f"project overview → [dashboard.html]({PAGES_DASHBOARD}).\n\n"
        "```text\n"
        f"{status_text.rstrip()}\n"
        "```\n"
    )


def _git(args: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=timeout,
        env={"GIT_TERMINAL_PROMPT": "0", "PATH": "/usr/bin:/bin:/usr/local/bin"},
    )


def publish(now: dt.datetime, dry_run: bool = False) -> int:
    from scripts.paper_status import build_status, render  # read-only status assembly

    status, code = build_status(now)
    md = render_markdown(render(status), status["generated"], code)
    STATUS_MD.write_text(md, encoding="utf-8")

    if dry_run:
        print(f"[publish] wrote {STATUS_MD.name} (dry-run, no git) exit_code={code}")
        return 0

    _git(["add", "STATUS.md"])
    if _git(["diff", "--cached", "--quiet"]).returncode == 0:
        print(f"[publish] STATUS.md unchanged — nothing to commit  exit_code={code}")
        return 0

    _git(["commit", "-m", f"status: {status['generated']}"])
    # best-effort sync (the cloud paper-bot also pushes to main); never hang, never crash launchd
    pull = _git(["pull", "--rebase", "--autostash", "origin", "main"], timeout=90)
    push = _git(["push", "origin", "main"], timeout=90)
    ok = push.returncode == 0
    note = "pushed" if ok else f"push deferred ({(push.stderr or pull.stderr).strip().splitlines()[-1:] or ['?']}"
    print(f"[publish] committed STATUS.md · {note}  exit_code={code}")
    return 0


def _selfcheck() -> int:
    md = render_markdown("ALPHA LAB PAPER STATUS   generated: X\n  broker ok", "2026-07-11T12:00", 0)
    assert md.startswith("# Paper status"), "missing title"
    assert "🟢 nominal" in md and "```text" in md, "missing verdict/fence"
    assert "ALPHA LAB PAPER STATUS" in md, "status text not embedded"
    assert "app.alpaca.markets" in md, "missing live-view pointer"
    print("[publish] selfcheck OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="write STATUS.md, skip all git")
    ap.add_argument("--selfcheck", action="store_true", help="offline assert on the wrapper, no IO")
    args = ap.parse_args()
    if args.selfcheck:
        return _selfcheck()
    return publish(dt.datetime.now(), dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
