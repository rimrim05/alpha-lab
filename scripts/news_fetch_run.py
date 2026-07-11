"""Pull historical headlines from the Alpaca (Benzinga) news API into the source-agnostic
news parquet that scripts/llm_sentiment_run.py consumes (columns: date, ticker, company,
headline). Free with the existing Alpaca paper keys; history reaches ~2015.

Usage: .venv/bin/python scripts/news_fetch_run.py [--start 2026-02-01] [--end YYYY-MM-DD]
       [--universe mega|wide] [--out data/raw/news.parquet]

Default start is the scoring model's training cutoff (unmasked evaluation is only valid
after it — Decision A in the track spec); pass an earlier --start for masked-mode history.
"""
import argparse
from pathlib import Path

from core.data.news import fetch_news_alpaca
from core.data.registry import register
from core.data.universe import fetch_sp_composite
from core.env import load_dotenv

MODEL_CUTOFF = "2026-01-31"  # keep in sync with scripts/llm_sentiment_run.py


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default=MODEL_CUTOFF)
    ap.add_argument("--end", default=None)
    ap.add_argument("--universe", choices=["mega", "wide"], default="mega",
                    help="mega = S&P 500, wide = S&P 1500")
    ap.add_argument("--out", default="data/raw/news.parquet")
    args = ap.parse_args()

    load_dotenv()
    comp = fetch_sp_composite(cache=Path("data/raw/sp_composite_named.parquet"))
    if args.universe == "mega":
        comp = comp[comp["index"] == "500"]
    names = dict(zip(comp["ticker"], comp["company"]))
    symbols = sorted(names)
    print(f"fetching Alpaca news: {len(symbols)} symbols, {args.start} -> {args.end or 'now'}")
    news = fetch_news_alpaca(symbols, args.start, args.end, names=names)
    if news.empty:
        raise SystemExit("no headlines returned — check keys/window")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    news.to_parquet(out)
    register(Path("data/manifest.jsonl"), name="news_alpaca", source="alpaca+benzinga",
             filters={"universe": args.universe, "start": args.start, "end": args.end},
             path=str(out), rows=len(news))
    per_day = news.groupby("date").size()
    print(f"wrote {len(news)} rows -> {out}")
    print(f"coverage: {news['ticker'].nunique()} tickers, {per_day.index.min()} -> "
          f"{per_day.index.max()}, median {per_day.median():.0f} headlines/day")


if __name__ == "__main__":
    main()
