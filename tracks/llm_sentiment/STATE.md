# STATE — LLM headline sentiment (Lopez-Lira & Tang)

**Stage:** 0 → 1 (hypothesis drafted, pipeline built, no real data run yet)
**Last session:** 2026-07-06

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

## Blocked / Next
1. **Historical news source** — need one of: Refinitiv/LSEG news export (Kristen,
   on-campus, save CSV → convert to parquet with columns date,ticker,company,headline),
   or Alpaca news API history (needs ALPACA keys).
2. **ANTHROPIC_API_KEY** in env for scoring runs.
3. **HYP-003 sign-off** (vault) — Stage 0 gate, Kristen approves before verdicts count.
4. Then: first masked backfill run + unmasked post-cutoff run, compare.
5. Later (Stage 5, only after Stage 4 promote): Alpaca paper-trading live loop + nightly job.

## Open questions
- Which news source for the live loop (Alpaca free tier vs scraping RSS) — decide when keys exist.
- decay sub-hypothesis: measure rolling 6-mo Sharpe over time once history exists.
