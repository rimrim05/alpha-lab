# Cutover plan — isolate `momentum_concentrated` into its own Alpaca paper account

**Date drafted:** 2026-07-15 · **Type:** execution-accounting change only (NOT a new alpha experiment;
does not touch the frozen forward alpha-isolation test) · **Status:** plan → implement → review → dry-run.

## Why

All seven hunt2026 books are virtual; the live runner sums them into ONE account-level target and
submits once (`hunt_paper_run.py::live_run`, tag `h26`). Single-stock fills for `momentum_concentrated`
are netted into the ETF aggregate and are **not broker-attributable**. It is the one book where broker
marks matter (single-name fills/slippage, survivorship, delistings booking 0 in the virtual ledger).
Isolating it gives an exact, broker-marked reality series for that book. The other six trade liquid
ETFs where combined execution costs nothing.

## Current architecture

- `live_run()` sizes `notional = equity / len(BOOKS)` (= equity/7), builds each book's dollar targets,
  **aggregates all 7 into `agg`**, `broker.submit_targets(agg, tag="h26")` to the shared paper account
  (`ALPACA_API_KEY_ID/SECRET`). One `_account` ledger row records the aggregate + real fills.
- `hunt_paper_reconcile.py` reconciles that one shared account; per-book drag is **pro-rated** by each
  book's share of the aggregate target (BANDS `book_drag_bps_month = 30`).

## Target architecture

- **Shared account (unchanged creds):** the six ETF books only —
  `vol_managed_qqq, vol_core_svxy, trend_vol_qqq, dual_momentum_gem, dual_momentum_gold,
  defensive_ensemble`. Aggregated and submitted with tag `h26`, exactly as today.
- **Dedicated account (`ALPACA_MC_API_KEY_ID/SECRET`):** `momentum_concentrated` only. Submitted with
  tag `h26mc`. It is the sole book in that account, so fills/positions/marks attribute to it exactly.
- Book strategy rule, weights, leverage, universe, rebalance timing, cost model, and the factor-adjusted
  forward-alpha benchmark are **unchanged**.

## Allocation / capital-sizing logic (the "mirror" rule)

`notional_per_book = shared_account_equity / 7` — computed once from the shared account, **identical to
today's formula**. The six ETF books use it (submitted to the shared account, which therefore holds ~1/7
as idle cash — nothing about the ETF books' dollar sizing changes). `momentum_concentrated` uses the
**same** `notional`, submitted to the dedicated account. Rationale: this reproduces MC's exact current
1/7 dollar share at cutover and keeps it a constant 1/7 of the canonical capital base — matching how the
virtual ledger already sizes it, so broker-vs-model tracking is apples-to-apples. The dedicated account's
own equity is a **buying-power constraint only** (fail closed if it can't support `notional × gross`),
not the sizing driver. Divisor stays **7**, never 6 — dividing by 6 would silently lever the ETF books.

## Cutover timing

- Cutover = the first `--live` nightly run after (a) `.env` has `ALPACA_MC_*`, (b) reviewers pass, and
  (c) one offline dry-run is inspected. Target: next weekday evening after review, ~2026-07-16 20:30 local
  (the nightly job window; must run after 16:00 ET). Exact timestamp stamped into this memo at cutover.
  **FIRED `2026-07-15T20:31:21-07:00`** — one window earlier than the target, because the keys were in
  `.env` by that evening's run. See §Final status for the stamp and its evidence.
- Before the first dedicated-account submit, any pre-existing MC positions in the SHARED account are
  flattened by the normal reconcile/flatten path (MC leaving the shared target set makes its old shares
  "foreign" → flattened), so MC is not double-held across accounts.

## What stays continuous vs what begins at cutover

- **Continuous (never rewritten):** every per-book model ledger incl. `momentum_concentrated.jsonl`; the
  frozen factor-adjusted forward-alpha ledger (`ledgers/hunt2026/alpha_forward/`). These are model-marked
  and independent of execution venue — the cutover does not touch them.
- **Begins at cutover (new series):** `momentum_concentrated`'s **broker-marked execution-reality**
  series — the `_account_mc` ledger rows and the dedicated MC reconciliation. No pre-cutover broker
  attribution is claimed or backfilled; MC broker evidence starts the day the dedicated account goes live.
- The shared `_account` row and shared reconcile continue, now covering six books instead of seven.

## Safety checks (all fail closed, live path only)

1. `ALPACA_MC_*` missing → abort live (no partial submission).
2. Shared and MC key-ids identical → abort (prevents both routing to the same account).
3. MC endpoint not paper → abort (broker factory already asserts paper).
4. Any symbol present in BOTH the shared aggregate and the MC target set → abort (no symbol double-routed).
5. MC account buying power < MC gross notional → abort.
6. Dry-run produces BOTH account target sets and submits nothing.

## Rollback

Revert the `hunt_paper_run.py` / `hunt_paper_reconcile.py` / `core/broker/alpaca.py` changes (single
commit, tagged), and the next nightly run reverts to the seven-book single-account aggregate. Flatten the
dedicated MC account manually from the Alpaca paper UI. Model ledgers and the forward-alpha ledger are
untouched by rollback (they were never modified). No historical data is lost.

## Known limitations

- Mirror sizing couples MC's notional to the shared account's equity by design; if capital is later
  re-based, both accounts re-derive from the shared equity.
- The dedicated MC account may hold idle cash (its equity > MC notional); reconcile compares at the
  **position/sleeve** level (marked value of MC positions vs model), not account-NAV growth, so idle
  cash does not distort the tracking-drag signal.
- Broker-marked MC evidence has no history until cutover; the 30 bps/month tripwire needs a few weeks to
  be meaningful.
- ~~The cutover leaves `paper_status.py` monitoring only the shared account: the dedicated account's live
  state and its `_reconcile_mc.jsonl` alarms are invisible to the status report and its exit code, so a
  broken MC leg would still read HEALTHY.~~ **Closed 2026-07-16** — status now snapshots both accounts and
  folds MC reconcile alarms into the exit code (gated on a live `_account_mc` row, so pre-cutover trees are
  unaffected). The shared four-part flatten gate stays shared-only by design: it tracks legacy residue in
  the shared account, not MC's own tracking error.
- Post-cutover the whole-share rounding in `submit_targets` is now visible per-name against MC's own
  ~$7.1k target set: on 2026-07-16, 6 of 22 names (CAT, FIX, LITE, MU, SNDK, STX) rounded to 0 shares,
  leaving MC ~82% deployed ($5,842 held vs $7,128 target). This is pre-existing behavior, NOT a cutover
  regression — the same `round(target/price)` ran when MC was inside the aggregate. Flagged for Kristen
  (Stage 0 sizing call); shorts cannot be fractional, so it is not a free fix.

## Final status (written 2026-07-15 pre-cutover; cutover timestamp stamped in 2026-07-16)

- **Implemented + pushed** (commit on `main`): `route_targets` split + no-cross-leak invariant;
  two-account `live_run` with fail-closed guards (missing `ALPACA_MC_*`, shared==MC key id, symbol
  overlap, MC buying power < gross, non-paper endpoint); per-leg fail-safe submission (`submit_leg`)
  so one account's failure never loses the other's ledger row; `_account_mc` execution-reality row;
  exact dedicated MC reconcile (`_reconcile_mc.jsonl`, 30 bps/mo band, order-state census).
- **Sizing used:** `notional = shared_equity / 7` for every book (UNCHANGED). MC trades exactly its
  1/7 dollar share; ETF books unchanged.
- **Tests:** 228 passed, 1 skipped (full suite). 14 new offline tests in `tests/test_mc_isolation.py`
  (routing split, no-cross-leak fail, sizing invariant, shared-reconcile MC exclusion, MC reconcile
  alarms, per-leg fail-safe, second-account cred wiring).
- **Reviewers:** two independent audits (routing/safety + data-integrity). One Critical (no
  atomicity/record-loss on a mid-submit exception) and one low-severity (`--since` replay backfilling
  pre-cutover MC rows) — both fixed and retested. Data-integrity reviewer confirmed sizing continuity,
  ledger continuity (no history rewritten), and forward-test integrity.
- **Dry-run (offline, $100k):** SHARED = 16 ETF names, gross $111,108 (levered ETF books). DEDICATED =
  24 single stocks, gross $14,286 = exactly equity/7 (14.3%). Zero symbol overlap between the two sets.
- **Shared account excludes MC:** confirmed — the six ETF books aggregate to the shared account;
  MC's old shares there flatten as foreign; the shared reconcile no longer judges MC.
- **Dedicated account receives only MC:** confirmed — `momentum_concentrated` alone, tag `h26mc`.
- **Exact cutover timestamp:** **`2026-07-15T20:31:21-07:00`** (= `2026-07-16T03:31:21Z`) — stamped
  2026-07-16. This is the moment the first `h26mc` order was created in the dedicated account
  (`h26mc-AMD-cedf4062`, AMD buy 1), i.e. the first successful `--live` run after the keys landed in
  `.env`, one nightly window EARLIER than the ~2026-07-16 target in §Cutover timing.
  Evidence, four independent sources agreeing:
  - broker: the dedicated account's 16 orders are all `h26mc`, all created 20:31:21–20:31:22 local
    on 2026-07-15; `h26mc-AMD-cedf4062` is the earliest order the account has ever held.
  - runner ledger: `_account_mc.jsonl` has exactly one live row, `date 2026-07-15`, `submit_ok: true`,
    22 targets, `gross 0.0714`, `mc_buying_power $400,000`.
  - shared reconcile: `_reconcile.jsonl` `run_at 2026-07-15T20:31:27` — 6s after the MC submit, same run.
  - scheduler: `artifacts/hunt2026/paper/nightly.log` mtime `2026-07-15 20:31`, containing
    `[2026-07-15] momentum_concentrated (dedicated account)`.
  Orders were created after the 16:00 ET close, so they queued and **filled at the 2026-07-16 open**;
  the same run's shared-account leg flattened MC's old shares there. Both accounts confirmed
  `foreign: 0` on 2026-07-16. The MC broker-marked series therefore starts 2026-07-16.
- **Rollback:** `git revert` this commit; next nightly run reverts to the seven-book single-account
  aggregate. Flatten the dedicated MC account from the Alpaca paper UI. Model + forward-alpha ledgers
  are untouched by rollback.
