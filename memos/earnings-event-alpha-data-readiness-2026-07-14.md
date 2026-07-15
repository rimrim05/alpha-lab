# MEMO — Point-in-time earnings-event alpha: data-readiness verdict

**Date:** 2026-07-14
**Research lead:** autonomous run (Kristen's directive)
**Scope:** new event-driven cross-sectional alpha line. Does NOT touch the price-only
trend / momentum / vol / VIX-timing / JSE lines — those are separate closed research.
**Bottom line up front: DATA GATE NOT MET. 8 valid point-in-time events vs a
pre-registered 300 minimum. Stop. Do not backtest. Let the forward panel accrue.**

---

## 0. What already exists (do not rebuild)

This project is already scoped, pre-registered, and collecting in this repo. A new parallel
build would violate the repo's own dedup discipline. The existing line is:

- **Spec / prereg:** `research/hunt2026/preregistrations/exp-ic-earnings-fwd-2026-07-10.md`
  (EXP-IC-EARNINGS-FWD, frozen 2026-07-10).
- **Collector:** `scripts/earnings_collect.py` — forward-only PIT earnings-surprise panel,
  Finnhub free tier, nightly.
- **Job:** `com.rimrim.earnings-collect` — **loaded and healthy** in launchctl
  (`LastExitStatus=0`, plist in `~/Library/LaunchAgents`, last pull 2026-07-14 caught the
  bank-cluster reports). Collection is live, not stalled.
- **Data store:** `data/earnings_fwd/events.jsonl` (32 rows) + `reactions.jsonl`.
- **Reporter:** `earnings_collect.py --report` prints the pre-registered ICs and an honest
  `ACCUMULATING` state until n ≥ 300.

The directive's Hypothesis #1 (standardized EPS surprise → 5–20d abnormal return) **is
already the pre-registered primary hypothesis of this line.** Nothing new needs designing.
The only thing missing is data.

---

## 1. Data-readiness verdict

**NOT READY.** 8 point-in-time (PIT) tradable events after cleaning, against a
pre-registered primary threshold of 300 and a kill threshold of 600. Any backtest on 8
events is uninterpretable (a single name moves the pooled IC by more than its own
confidence interval), so per the directive's own stop-rule, no signal is proposed, tested,
or scored. The deliverable is this memo.

The shortfall is not fixable with cleaning or a better query. It is structural: **free
point-in-time earnings-surprise history does not exist.** The consensus estimate *as it was
known the day before the release* is the paid product (IBES / Refinitiv / Zacks); every
free API returns the *restated* estimate/actual as known today, which is look-ahead-
contaminated and survivorship-biased. WRDS/IBES — the one gold-standard PIT source — is
access-blocked for this user. So the only honest PIT data is what the collector *watches
happen going forward*, which began 2026-07-10.

---

## 2. Chosen hypothesis and economic mechanism

Per the ordered list, and because it is the only one the available data can ever support
PIT-cleanly, the chosen hypothesis is **#1: standardized EPS surprise predicts 5–20 trading-
day abnormal return** (the already-pre-registered spec). #2 (surprise + estimate revision)
and #3 (guidance surprise) are rejected at the gate: Finnhub free gives no PIT revision
history and no structured guidance, so neither is collectible without look-ahead.

- **Signal:** SUE = (actual − estimate) / scale, scale = trailing std of the symbol's last
  ≤4 surprises when ≥2 exist, else |estimate|.
- **Mechanism:** post-earnings-announcement drift — under-reaction to fundamental news that
  has not been fully arbitraged at the large-cap horizon.
- **Why it is not the momentum line:** the signal is a discrete fundamental-information event
  (a surprise vs consensus at a known timestamp), not a trailing-price-return factor. It
  enters only in the days after a report, holds a fixed 5/20/60d window, and is orthogonal
  by construction to the 12-1 price momentum book (`momentum_concentrated`). SUE can be high
  on a name with poor price momentum and vice-versa.
- **Benchmark / controls (pre-registered):** zero-IC null on the same event panel; planned
  factor controls = market, GICS sector (sector-relative SUE), plus the dispersion-regime
  split. Size/value/mom/low-vol attribution deferred until the panel is scoreable.

---

## 3. Exact point-in-time timing convention (already implemented)

Conservative, and already coded in `earnings_collect.py::reaction_session`:

- **Before-market (bmo) release:** first tradable reaction = the **report-day** session
  open/close. Entry uses that session's close (next observable close after the news).
- **After-market (amc) release:** first tradable reaction = the **next calendar session**.
- **Unknown timestamp:** treated as amc → **next session** (the conservative default).
- **Forward returns** are measured from the reaction-session close (never from a price that
  precedes the announcement). Weekend/holiday report dates slide to the next session via the
  yfinance lookup.
- **PIT flag:** an event is `point_in_time=true` ONLY if the collector observed its calendar
  row flip forecast→actual within its own pull window. The 4-quarter Finnhub backfill is
  flagged `point_in_time=false` and **excluded** from the primary test.

No timestamp-quality shortcut is taken: unknown hour ⇒ next session, always.

---

## 4. Event count and coverage table

| Bucket | Count | Scoreable as PIT alpha? |
| --- | --- | --- |
| Total rows in `events.jsonl` | 32 | — |
| **Point-in-time events (`point_in_time=true`)** | **8** | ✅ the only test set |
| Stale/backfill rows (`point_in_time=false`) | 24 | ❌ excluded (restated) |
| Unique PIT symbols | 8 | — |
| Reaction snapshots recorded | 2 | (rest pending next snapshot pass) |
| **Pre-registered primary threshold** | **300** | gate |
| Pre-registered kill threshold | 600 | gate |

PIT events by report date: 2026-07-09 (1), 2026-07-10 (1), 2026-07-14 (6). Pulls landed
2026-07-10 and 2026-07-14; the 07-14 pull caught the start of Q2 bank-earnings season.

**Independent validity audit (Data Integrity Agent): all 8 PIT events clean, 0 flawed.**
No duplicate (symbol, period) pairs; no missing/null report dates; no event whose
report_date is after its pulled_at (the 6 same-day 07-14 rows are confirmed *not* leakage —
all `hour=bmo`, i.e. released pre-open, and pulled at 21:15 after the close, so the actual
was already public); estimate/actual/surprise present on all 8; all 8 valid S&P 500 tickers
(`C` = Citigroup, legitimate single-letter). One data-quality watch, not a validity failure:
GS shows a +45% surprise (est 14.46 → act 20.98) — worth a manual filing check before it ever
enters a test, but the row is well-formed. Reaction snapshots: 2/8 recorded (DAL, PEP); the
other 6 are correctly un-snapped (their bmo reaction session is the report day itself, which
`snapshot_reactions` only captures once it is strictly in the past) and snap on the next run.

**Separate historical placeholder — not counted, not scoreable:** `artifacts/pead/drift.md`
reports 530 events with a large CAR spread (5.69% @ 20d), but on a **60-name survivorship-
biased universe** using **restated (non-PIT) surprises**. Both biases flatter drift (the
consensus/actuals are as-known-today, and crashed-then-delisted names are absent). It is a
pipeline sanity check, **not evidence of alpha**, and is correctly walled off from the PIT
line (they share no data).

---

## 5. Held-out performance and factor-adjusted results

**Not run.** With n = 8 PIT events there is no held-out period and no meaningful factor
attribution — the directive's own rule ("fewer than 300 … stop … rather than forcing a weak
backtest") terminates the pipeline here. Running an event-study, factor-attribution,
implementation, and statistical pass on 8 events would manufacture false precision, so those
agents were not dispatched. `earnings_collect.py --report` currently returns the honest
`ACCUMULATING — n=… scoreable at 20d, primary test at n≥300` state, as designed.

## 6. Costs, liquidity, turnover, capacity

**Deferred (gate not met).** Pre-committed assumptions already live in the spec/engine for
when the panel is scoreable: S&P 500 universe (liquid, borrowable large caps), 10 bps costs,
$5M ADV floor, 20%/2% sector/name caps — inherited from the audited residual engine. Turnover
is event-paced (entries only in the days after a report, fixed 5/20/60d exits), so gross
turnover is bounded by earnings-season clustering, not daily rebalancing. Full capacity math
waits for a scoreable panel.

## 7. Placebo and adversarial-review findings

**Placebos not run** (n = 8). They are pre-registered and will run at n ≥ 300: shuffled event
dates, delayed entry, randomized surprise ranks, momentum-matched control, sector-relative
demeaning, and the dispersion-regime split.

**Adversarial review of the data design itself (this is the live value):**
- *Look-ahead / timestamp leakage:* controlled by construction — PIT flag requires watching
  the forecast→actual flip; unknown timestamps default to next session; returns start at the
  post-announcement close. No historical backfill is ever scored.
- *Post-event gap capture:* the convention deliberately forgoes the announcement gap (entry
  is the first observable close *after* the news), so any measured drift cannot be the
  overnight jump.
- *Selection / survivorship:* PIT panel uses point-in-time S&P membership; the only
  survivorship-flattered artifact (`artifacts/pead`) is explicitly excluded.
- *The one unavoidable caveat:* forward-only collection means the eventual test period and
  the "training" period are the same short forward window — there is no independent historical
  holdout, only forward accrual. That is a genuine limitation of the free-data regime, not a
  bug, and it caps the strongest possible classification at "promising" (never "robust")
  without a later paper-forward confirmation.

---

## 8. Classification

**No evidence of event alpha — insufficient data (data gate not met).** This is not a
rejection of the hypothesis; it is the pre-registered `ACCUMULATING` state. The hypothesis
remains open and correctly instrumented. It cannot advance to "promising but unproven" until
n ≥ 300 PIT events with a positive held-out factor-adjusted net IC that survives placebos.

---

## 9. One recommended next action

**Do nothing new — the panel is already accruing correctly and the primary test is close.
Just re-report at the n ≥ 300 checkpoint.** Concretely: leave `com.rimrim.earnings-collect`
loaded (it is healthy) through the current Q2 season, and re-run `earnings_collect.py --report`
when it crosses n ≥ 300 — expected in **~2–4 weeks** (see accrual). No code change, no data
purchase, no allocation change is warranted. This is the cheapest possible next step: wait
out one earnings season that is *already running*.

*Paying for a panel is not justified here.* Because n ≥ 300 is only weeks away via free
forward accrual, a one-time paid PIT-consensus panel (IBES/Zacks/Refinitiv, or unblocking
WRDS) buys mainly a genuine *historical holdout* — worth considering later if the forward
read is promising and you want independent confirmation, but not worth a spend now. Flagged,
not taken.

---

### Accrual ETA (assumption-stated; Data Integrity Agent estimate)

Assumption: ~500 S&P 500 reporters/quarter, ~85% concentrated in the ~4-week core of each
season (Q2 core ≈ 2026-07-15 → 08-08); collector runs nightly without gaps; ~1 PIT event per
reporter per quarter.

- **n = 300** (primary test): reached organically **within the current Q2 season — roughly
  early-to-mid August 2026**, as the 07-21 → 07-31 mega-cap peak lands (300 is ~60% of one
  season's ~500). So the first honest primary read is **~2–4 weeks out**, not next year.
- **n = 600** (kill test): exceeds a single season's ~500, so it rolls into the Q3 wave
  (reports begin mid-October) → **~late October 2026.**

Key risk to this ETA: the collector's pull window is [today−3d, today+7d] and it only records
a reporter it actually observes flip to actual — a multi-day job outage during the peak, or
reporters slipping past the ±window, would slow accrual. The job is currently healthy; a quick
weekly `--report` glance during the peak confirms the count is climbing as expected. (My
initial estimate of late-2026/early-2027 was too pessimistic — it under-counted single-season
yield; superseded by the above.)

*No live allocation was changed. No trade was proposed. No data was purchased.*
