"""Populate os.environ from alpha-lab/.env (KEY=VALUE lines), no dependency."""
import os
from pathlib import Path


def load_dotenv(path: Path | None = None) -> None:
    """An already-set env var wins (setdefault), so an explicit `export` still overrides
    the file. Quotes and #comments handled."""
    path = path or Path(__file__).resolve().parents[1] / ".env"
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
