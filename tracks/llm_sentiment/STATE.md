# STATE — LLM headline sentiment (Lopez-Lira & Tang)

**Stage:** 1 (Stage-0 approved; controlled smoke gated on API key)
**Last session:** 2026-07-13

## Gate decision
- **Stage 0 APPROVED by Kristen on 2026-07-13.** Research only; no paper-book or
  deployment authorization.
- LLM Council review: full council, 2026-07-13. Required a zero-call default,
  explicit request ceiling, resumable cache, deterministic smoke sample, strict parsing,
  and original publication timestamps before performance evaluation.

## Built
- `prompt.py` — paper's zero-shot YES/NO/UNKNOWN prompt
- `scorer.py` — pinned Claude Haiku scoring, strict JSON parsing, entity masking,
  content-addressed SQLite cache, and hard new-request ceiling.
- `sample.py` — deterministic, row-order-invariant 200-headline smoke manifest.
- `signal.py` — original publication instant → conservative decision session → daily signal.
- `scripts/llm_sentiment_run.py` — zero-call-by-default smoke runner; `--execute` plus an
  explicit `--max-new-calls` is required for provider traffic.
- Offline tests cover request caps, cache reuse/dedup, parser failure, smoke determinism,
  timestamp/session handling, one-day lag, and costs.

## Contamination protocol (Decision A, from spec)
1. Unmasked historical eval ONLY on post-model-cutoff windows (>= 2026-01-31).
2. Entity-masked scoring as robustness check on any window.
3. Primary evidence = live forward test (daily scoring → paper portfolio).

## News source — LIVE (timestamped refresh 2026-07-13)
Alpaca (Benzinga) news API, free with the existing paper keys, history to ~2015:
- `core/data/news.py` — paginated fetcher → source-agnostic schema (`published_at`, date,
  ticker, company, headline); original UTC instant retained, universe filter, dedup.
- `scripts/news_fetch_run.py` — S&P 500 pull → timestamped parquet + manifest row.
  Default start = model cutoff (2026-01-31), the Decision-A unmasked window; pass an
  earlier `--start` for masked-mode history.
- Company names for the masking protocol come from the Wikipedia composite (new `company`
  column in `extract_symbols`).
- Current timestamped artifact: `data/raw/news_timestamped.parquet`, 54,908 rows / 501
  tickers through 2026-07-13 ET. Frozen dry-run smoke manifest: 200 rows / 116 tickers /
  20 publication dates; score cache contains 0 rows, confirming zero provider calls.

## Blocked / Next
1. **ANTHROPIC_API_KEY** supplied securely in alpha-lab/.env or process environment.
2. With Kristen's separate request-cap approval, run the frozen 200-headline smoke with no
   more than 220 new requests. A cache-only rerun must make zero requests.
3. Only after the smoke passes: pre-register the evaluation split, then separately approve
   any larger run. No efficacy verdict comes from the smoke.
4. Later (Stage 5, only after Stage 4 promote): paper-trading loop + nightly job.

## Hard stops
- Any request-cap breach, cache-resume duplicate, missing/ambiguous publication timestamp,
  returned-model mismatch, pre-cutoff contamination, or malformed-response rate above 5%.

## Open questions
- Decay sub-hypothesis: measure rolling 6-mo Sharpe over time once history exists.
