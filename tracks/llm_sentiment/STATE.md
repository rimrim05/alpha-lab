# STATE — LLM headline sentiment (Lopez-Lira & Tang)

**Stage:** 1 (news data flowing; scoring gated on API key + Stage-0 sign-off)
**Last session:** 2026-07-10

## Built
- `prompt.py` — paper's zero-shot YES/NO/UNKNOWN prompt
- `scorer.py` — Claude scoring (haiku), response parsing, entity masking for the
  contamination robustness check
- `signal.py` — scored headlines → daily per-ticker signal
- `scripts/llm_sentiment_run.py` — full run: score → L/S quantile portfolio → scorecard.
  Enforces Decision A: refuses unmasked evaluation on pre-cutoff (< 2026-01-31) headlines.
- All offline-tested (mocked client); 4/4 tests green.

## Contamination protocol (Decision A, from spec)
1. Unmasked historical eval ONLY on post-model-cutoff windows (>= 2026-01-31).
2. Entity-masked scoring as robustness check on any window.
3. Primary evidence = live forward test (daily scoring → paper portfolio).

## News source — LIVE (2026-07-10)
Alpaca (Benzinga) news API, free with the existing paper keys, history to ~2015:
- `core/data/news.py` — paginated fetcher → source-agnostic schema (date, ticker, company,
  headline); ET-date attribution (no look-ahead), universe filter, dedup. Unit-tested offline.
- `scripts/news_fetch_run.py` — S&P 500 pull → `data/raw/news.parquet` + manifest row.
  Default start = model cutoff (2026-01-31), the Decision-A unmasked window; pass an
  earlier `--start` for masked-mode history.
- Company names for the masking protocol come from the Wikipedia composite (new `company`
  column in `extract_symbols`).

## Blocked / Next
1. **ANTHROPIC_API_KEY** in alpha-lab/.env for scoring runs (runner now reads .env).
2. **HYP-003 sign-off** (vault) — Stage 0 gate, Kristen approves before verdicts count.
   Then: `.venv/bin/python scripts/llm_sentiment_run.py --news data/raw/news.parquet`
   (post-cutoff unmasked primary; add `--masked` for the contamination check).
4. Then: first masked backfill run + unmasked post-cutoff run, compare.
5. Later (Stage 5, only after Stage 4 promote): Alpaca paper-trading live loop + nightly job.

## Open questions
- Which news source for the live loop (Alpaca free tier vs scraping RSS) — decide when keys exist.
- decay sub-hypothesis: measure rolling 6-mo Sharpe over time once history exists.
