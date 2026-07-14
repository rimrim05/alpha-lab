"""Auditable headline scoring with a hard request budget and resumable SQLite cache."""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from tracks.llm_sentiment.prompt import PROMPT_VERSION, build_prompt

MODEL = "claude-haiku-4-5-20251001"
PROVIDER = "anthropic"
SCHEMA_VERSION = "sentiment-score-v1"
TEMPERATURE = 0
MAX_TOKENS = 80


def parse_response(text: str) -> int | None:
    """Strict parser: malformed/refused output is missing, never silently neutral."""
    try:
        payload = json.loads((text or "").strip())
    except (TypeError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict) or set(payload) != {"label", "reason"}:
        return None
    if not isinstance(payload["reason"], str) or not payload["reason"].strip():
        return None
    return {"YES": 1, "NO": -1, "UNKNOWN": 0}.get(payload["label"])


def mask_entity(headline: str, company: str, ticker: str) -> str:
    out = headline
    for token in filter(None, [company, ticker]):
        # match whole words of each part of the company name, case-insensitive
        for part in token.replace("(", " ").replace(")", " ").split():
            out = re.sub(rf"(?i)\b{re.escape(part)}\b", "the company", out)
    out = re.sub(r"\(\s*the company\s*\)", "", out)
    out = re.sub(r"(the company)(\s+the company)+", r"\1", out)
    return re.sub(r"\s{2,}", " ", out).strip()


def scoring_input(item: dict, masked: bool = False) -> tuple[str, str, str]:
    if masked:
        headline = mask_entity(item["headline"], item.get("company", ""), item.get("ticker", ""))
        company = "the company"
    else:
        headline = item["headline"]
        company = item.get("company", "the company")
    prompt = build_prompt(headline, company)
    material = {
        "provider": PROVIDER, "model": MODEL, "prompt_version": PROMPT_VERSION,
        "schema_version": SCHEMA_VERSION, "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS, "prompt": prompt,
    }
    key = hashlib.sha256(json.dumps(material, sort_keys=True).encode()).hexdigest()
    return key, prompt, hashlib.sha256(prompt.encode()).hexdigest()


class ScoreCache:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS scores (
              cache_key TEXT PRIMARY KEY, prompt_hash TEXT NOT NULL,
              provider TEXT NOT NULL, model_requested TEXT NOT NULL,
              model_returned TEXT, prompt_version TEXT NOT NULL,
              schema_version TEXT NOT NULL, temperature REAL NOT NULL,
              max_tokens INTEGER NOT NULL, raw_response TEXT NOT NULL,
              score INTEGER, parse_status TEXT NOT NULL, request_id TEXT,
              input_tokens INTEGER, output_tokens INTEGER,
              scored_at_utc TEXT NOT NULL, attempt_count INTEGER NOT NULL
            )
        """)
        self.db.commit()

    def get(self, key: str) -> dict | None:
        self.db.row_factory = sqlite3.Row
        row = self.db.execute("SELECT * FROM scores WHERE cache_key = ?", (key,)).fetchone()
        return dict(row) if row else None

    def put(self, row: dict) -> None:
        cols = list(row)
        sql = f"INSERT INTO scores ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})"
        with self.db:
            self.db.execute(sql, [row[c] for c in cols])

    def close(self) -> None:
        self.db.close()


def cache_misses(items: list[dict], cache: ScoreCache, masked: bool = False) -> int:
    keys = {scoring_input(it, masked)[0] for it in items}
    return sum(cache.get(key) is None for key in keys)


def _response_text(resp) -> str:
    return "".join(getattr(block, "text", "") for block in getattr(resp, "content", []))


def score_headlines(client, items: list[dict], masked: bool = False, *,
                    cache: ScoreCache | None = None, execute: bool = False,
                    max_new_calls: int = 0) -> pd.DataFrame:
    if not items:
        raise ValueError("no headlines to score")
    owned_cache = cache is None
    cache = cache or ScoreCache(":memory:")
    work = {}
    for it in items:
        key, prompt, prompt_hash = scoring_input(it, masked)
        work.setdefault(key, (prompt, prompt_hash))
    missing = [key for key in work if cache.get(key) is None]
    if missing and (not execute or client is None):
        raise RuntimeError(f"{len(missing)} uncached scores; network execution not authorized")
    if len(missing) > max_new_calls:
        raise RuntimeError(f"{len(missing)} uncached scores exceed max_new_calls={max_new_calls}")

    for key in missing:
        prompt, prompt_hash = work[key]
        resp = client.messages.create(
            model=MODEL, max_tokens=MAX_TOKENS, temperature=TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = _response_text(resp)
        score = parse_response(raw)
        usage = getattr(resp, "usage", None)
        cache.put({
            "cache_key": key, "prompt_hash": prompt_hash, "provider": PROVIDER,
            "model_requested": MODEL, "model_returned": getattr(resp, "model", None),
            "prompt_version": PROMPT_VERSION, "schema_version": SCHEMA_VERSION,
            "temperature": TEMPERATURE, "max_tokens": MAX_TOKENS,
            "raw_response": raw, "score": score,
            "parse_status": "ok" if score is not None else "invalid",
            "request_id": getattr(resp, "id", None),
            "input_tokens": getattr(usage, "input_tokens", None),
            "output_tokens": getattr(usage, "output_tokens", None),
            "scored_at_utc": datetime.now(timezone.utc).isoformat(), "attempt_count": 1,
        })

    rows = []
    for it in items:
        key, _, _ = scoring_input(it, masked)
        hit = cache.get(key)
        rows.append({**it, "score": hit["score"], "parse_status": hit["parse_status"],
                     "masked": masked, "cache_key": key, "model": hit["model_returned"]})
    if owned_cache:
        cache.close()
    return pd.DataFrame(rows)
