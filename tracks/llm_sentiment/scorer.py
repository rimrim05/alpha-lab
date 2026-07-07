"""Headline scoring via an anthropic-compatible client. Entity masking supports the
contamination robustness check (Decision A in the spec)."""
import re
import pandas as pd
from tracks.llm_sentiment.prompt import build_prompt

MODEL = "claude-haiku-4-5-20251001"


def parse_response(text: str) -> int:
    first = (text or "").strip().splitlines()[0].strip().upper() if text else ""
    return {"YES": 1, "NO": -1}.get(first, 0)


def mask_entity(headline: str, company: str, ticker: str) -> str:
    out = headline
    for token in filter(None, [company, ticker]):
        # match whole words of each part of the company name, case-insensitive
        for part in token.replace("(", " ").replace(")", " ").split():
            out = re.sub(rf"(?i)\b{re.escape(part)}\b", "the company", out)
    out = re.sub(r"\(\s*the company\s*\)", "", out)
    out = re.sub(r"(the company)(\s+the company)+", r"\1", out)
    return re.sub(r"\s{2,}", " ", out).strip()


def score_headlines(client, items: list[dict], masked: bool = False) -> pd.DataFrame:
    if not items:
        raise ValueError("no headlines to score")
    rows = []
    for it in items:
        if masked:
            headline = mask_entity(it["headline"], it.get("company", ""), it.get("ticker", ""))
            company = "the company"
        else:
            headline = it["headline"]
            company = it.get("company", "the company")
        resp = client.messages.create(
            model=MODEL, max_tokens=50,
            messages=[{"role": "user", "content": build_prompt(headline, company)}],
        )
        rows.append({**it, "score": parse_response(resp.content[0].text), "masked": masked})
    return pd.DataFrame(rows)
