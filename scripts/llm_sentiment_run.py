"""Controlled Stage-1 LLM-sentiment smoke run; zero provider calls by default.

Examples:
  .venv/bin/python scripts/llm_sentiment_run.py --news data/raw/news.parquet
  .venv/bin/python scripts/llm_sentiment_run.py --news data/raw/news.parquet \
      --execute --max-new-calls 220 --limit 200
"""
import argparse
import os
import sys
from pathlib import Path

import pandas as pd

from core.backtest.engine import backtest
from core.backtest.portfolio import quantile_weights
from core.data.prices import daily_returns, fetch_prices_yf
from core.data.registry import register
from core.env import load_dotenv
from core.eval.scorecard import scorecard, to_markdown
from tracks.llm_sentiment.sample import select_smoke
from tracks.llm_sentiment.scorer import MODEL, ScoreCache, cache_misses, score_headlines
from tracks.llm_sentiment.signal import daily_signal

MODEL_CUTOFF_UTC = pd.Timestamp("2026-01-31T00:00:00Z")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--news", required=True)
    ap.add_argument("--masked", action="store_true")
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--max-new-calls", type=int, default=0)
    ap.add_argument("--execute", action="store_true", help="permit provider requests")
    ap.add_argument("--cache-only", action="store_true", help="fail if any score is uncached")
    ap.add_argument("--cost-bps", type=float, default=10.0)
    ap.add_argument("--cache", default="artifacts/llm_sentiment/scores.sqlite")
    ap.add_argument("--manifest", default="artifacts/llm_sentiment/smoke_manifest.parquet")
    args = ap.parse_args()
    if args.execute and args.cache_only:
        sys.exit("choose either --execute or --cache-only")
    if args.max_new_calls < 0:
        sys.exit("--max-new-calls must be nonnegative")

    load_dotenv()
    news = pd.read_parquet(args.news)
    required = {"published_at", "date", "ticker", "company", "headline"}
    missing = required - set(news.columns)
    if missing:
        sys.exit(f"news file missing {sorted(missing)}; refetch with timestamp-preserving collector")
    published = pd.to_datetime(news["published_at"], utc=True, errors="coerce")
    if published.isna().any():
        sys.exit("news contains missing or invalid published_at timestamps")
    if not args.masked:
        news = news[published >= MODEL_CUTOFF_UTC]
    if news.empty:
        sys.exit("no eligible headlines")

    sample = select_smoke(news, limit=args.limit)
    manifest = Path(args.manifest)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    sample.to_parquet(manifest, index=False)
    cache = ScoreCache(args.cache)
    items = sample.to_dict("records")
    misses = cache_misses(items, cache, masked=args.masked)
    print(f"model={MODEL} eligible={len(news)} selected={len(sample)} "
          f"tickers={sample['ticker'].nunique()} sessions={sample['date'].nunique()} "
          f"cache_misses={misses} max_new_calls={args.max_new_calls}")
    print(f"manifest -> {manifest}")

    if not args.execute and not args.cache_only:
        print("dry-run only: zero provider requests; add --execute with an explicit cap")
        return
    if args.cache_only and misses:
        sys.exit(f"cache-only blocked: {misses} scores are missing")
    if args.execute:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            sys.exit("ANTHROPIC_API_KEY not set; zero provider requests made")
        if misses > args.max_new_calls:
            sys.exit(f"{misses} cache misses exceed --max-new-calls={args.max_new_calls}")
        import anthropic
        client = anthropic.Anthropic()
    else:
        client = None

    scored = score_headlines(client, items, masked=args.masked, cache=cache,
                             execute=args.execute, max_new_calls=args.max_new_calls)
    out = Path("artifacts/llm_sentiment")
    label = "masked" if args.masked else "unmasked"
    scored_path = out / f"scored_{label}.parquet"
    scored.to_parquet(scored_path, index=False)
    invalid_rate = (scored["parse_status"] != "ok").mean()
    if invalid_rate > 0.05:
        sys.exit(f"hard stop: malformed response rate {invalid_rate:.1%} exceeds 5%")
    returned = set(scored["model"].dropna())
    if returned and returned != {MODEL}:
        sys.exit(f"hard stop: returned model mismatch {sorted(returned)}")

    sig = daily_signal(scored)
    px = fetch_prices_yf(sorted(sig.columns), str(sig.index.min().date()), None)
    rets = daily_returns(px)
    weights = quantile_weights(sig.reindex(rets.index).ffill(limit=1))
    res = backtest(weights, rets, args.cost_bps)
    card = scorecard(res["net"], {"equal_weight_long": rets.mean(axis=1)},
                     n_trials=1, periods_per_year=252)
    (out / f"scorecard_{label}.md").write_text(
        to_markdown(card, f"LLM sentiment smoke ({label}; no efficacy verdict)"))
    register(Path("data/manifest.jsonl"), name="llm_scored_smoke",
             source="anthropic+" + args.news,
             filters={"cutoff_utc": MODEL_CUTOFF_UTC.isoformat(), "masked": args.masked,
                      "model": MODEL, "limit": args.limit, "cost_bps": args.cost_bps},
             path=str(scored_path), rows=len(scored))
    print(f"smoke complete: {len(scored)} rows; no efficacy verdict permitted")


if __name__ == "__main__":
    main()
