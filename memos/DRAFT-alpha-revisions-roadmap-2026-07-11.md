# DRAFT — Alpha lane roadmap + EPS-revision entitlement probe (2026-07-11)

> **STATUS: DRAFT. NOT FROZEN. NOT A DEPLOYMENT ARTIFACT.**
> Read-only session. No strategy, allocation, scheduler, panel, broker, dataset, or frozen
> spec was modified. The preregistration below is a **DATA-BLOCKED draft** and must NOT be
> copied into `research/discovery/prereg/` or `research/hunt2026/preregistrations/` until
> Kristen approves the post-probe design. The earnings-surprise experiment
> (EXP-IC-EARNINGS-FWD) is **unchanged and separate**.

## Decision state
- Roadmap directionally accepted; **analyst EPS estimate revisions** is the preferred next
  distinct alpha lane.
- Entitlement/schema probe authorized and run (read-only, 10 symbols). Result below.
- Verdict: **DATA-BLOCKED** — no entitled dedicated forward-EPS-estimate feed on current plans.
- Do **not** freeze or implement. Recommendation-revision is **not** a fallback here (it would
  need its own preregistration and trial).

### Addendum 2026-07-13 — Capital IQ support email (Reva) does **not** clear the block
S&P replied that CIQ has historical consensus estimates limited to analysts Berkeley
subscribes to. That is **genuinely promising for this lane**, but it is **not** a confirmed
unblock. Keep `DATA-BLOCKED` until a live sample shows both:

1. **"Historical" = true PIT** (frozen as-of-day snapshot), not a restated past view. The
   in-app CIQ probe already found Recent Changes entitlement-gated pending broker validation —
   the email may describe that surface post-validation, or a different one. Verify, don't assume.
2. **Analyst coverage ≥ 3** at both ends of the frozen 60-day revision window under Berkeley's
   actual subscription. "The analysts your university subscribes to" fails the prereg if that
   means 1–2 visible brokers.

Separately: Reva's "current index members only, not PIT" caveat is a **non-issue for
stock-universe-repair** (membership history already lives in the frozen panel; CIQ was only
needed to price the 382 missing names — identity pilot 6/6 PASS). That caveat must not be
imported into this lane's decision, and this lane's open questions must not block universe repair.

---

## 1. Entitlement / schema probe findings

**Method:** read-only GET, ~10 S&P symbols (AAPL, MSFT, NVDA, JPM, XOM, WMT, TSLA, CVNA, MRNA,
ATVI — chosen to span positive / near-zero / negative / sign-change / split (NVDA 10:1, WMT 3:1
2024) / inactive (ATVI delisted 2023)). Existing keys only. Nothing written to any collection store.

| Field requested | Finnhub `/stock/eps-estimate` | EODHD fundamentals `Earnings::Trend` |
|---|---|---|
| Endpoint & HTTP status | `finnhub.io/api/v1/stock/eps-estimate` — **403** (all 10) | `eodhd.com/api/fundamentals/{t}.US?filter=Earnings::Trend` — **403** (all 10) |
| Entitlement result | **NOT ENTITLED.** Body: `{"error":"You don't have access to this resource."}`. Key VALID (control: `/quote`→200, `/calendar/earnings`→200). | **NOT ENTITLED.** Body: `Only EOD data allowed for free users.` `/user`→`subscriptionType:"free"`. Key VALID (control: `/eod`→200). |
| Exact returned fields | Not observable (403) | Not observable (403) |
| Current-consensus-only vs dated history | Not observable | Not observable (docs suggest `epsTrend` current/7/30/60/90d-ago, but **unverified — not entitled**) |
| Vendor observation/as-of timestamp | Not observable | Not observable |
| Fiscal-period id & period-end | Not observable | Not observable |
| mean / median / high / low / analyst count | Not observable | Not observable |
| Currency & adjustment basis | Not observable | Not observable |
| Inactive securities supported | Not observable (ATVI 403 like the rest) | Not observable (ATVI 403) |
| Two-snapshot same-period comparison | Not observable | Not observable |
| Missingness across symbols | N/A — 100% 403 (entitlement, not coverage) | N/A — 100% 403 (entitlement, not coverage) |
| Rate limits / pagination | Free tier 60 calls/min (from working endpoints); no pagination seen on entitled calls | Free tier daily API-request cap (`/user` shows request counter); fundamentals cost multiple credits; not reached — blocked before that |

**One accessible-but-insufficient datapoint (reported, not adopted):** the already-entitled
Finnhub `/calendar/earnings` endpoint (used by the surprise collector) returns an `epsEstimate`
field = **current consensus per upcoming earnings event**. It is (a) event-clustered, not a
continuous daily cross-section of all members; (b) a single latest value, **not** dated revision
history. A revision series could only be *built by us* by forward-snapshotting that consensus over
≥60 days — a different design (event-clustered coverage, self-constructed history), not a
vendor-provided estimate feed. **EXCLUDED from this experiment:** adopting calendar-consensus
snapshots would be a *separate event-clustered consensus-drift hypothesis* requiring its own
preregistration and trial. It is not a substitute inside EXP-IC-REVISIONS-FWD and is not folded in.

**Conclusion:** dedicated forward-EPS-estimate/revision data is **DATA-BLOCKED** on Finnhub and
EODHD current plans (probe accepted as conclusive for these plans). Options to unblock (Kristen's
call, none actioned): entitled Finnhub/EODHD paid tier, FactSet/CIQ Estimates (currently 403),
WRDS I/B/E/S (unavailable), or the forward-snapshot-the-calendar-consensus route (separate design).

**Do not purchase an estimates product yet.** Any candidate source must first demonstrate, via a
live sample or trial (not marketing/docs), ALL of:
1. **dated point-in-time estimate observations** (as-of timestamps, not current consensus only);
2. **stable fiscal-period identity + period-end** (so two snapshots reference the same period);
3. **analyst count** per estimate;
4. **currency + split-adjustment basis** (explicit, matchable to the price panel);
5. **inactive-security support** (delisted/renamed names retrievable);
6. **adequate universe coverage** of S&P 500 members;
7. **reproducible export or API access** (repeatable pull, not a one-off screen).
A source that cannot show all seven on a live sample does not unblock the experiment.

---

## 2. Corrected preregistration — EXP-IC-REVISIONS-FWD (DATA-BLOCKED DRAFT, NOT FROZEN)

Revised per Kristen's 9 post-probe requirements. Ready to freeze only when an entitled estimate
source exists AND Kristen approves. **Do not implement.**

**ID:** EXP-2026-07-11-ic-revisions-fwd · **State:** DATA-BLOCKED (no entitled estimate feed) ·
**Alpha-type tag:** market (cross-sectional single-name) · **Layer:** A (new information source).

**Hypothesis:** Positive analyst EPS-estimate *revision momentum* — the change in consensus mean
forward-fiscal-period EPS over a trailing window, price-scaled — predicts positive 20-trading-day
forward excess return cross-sectionally among USD-reporting S&P 500 members, because the market
underreacts to the gradual diffusion of analyst information (Chan-Jegadeesh-Lakonishok 1996;
Gleason-Lee 2003). Distinct from the discrete post-earnings-surprise drift under separate test.

**(Req 8) Relationship to EXP-IC-EARNINGS-FWD:** the earnings-surprise experiment is **unchanged
and fully separate** — different signal, store, and checkpoint. This experiment neither edits nor
depends on it; the only shared asset is the read-only membership/price panel.

**(Req 1) Prospective warm-up:** no revision signal exists until **≥60 calendar days of forward
consensus snapshots** have accrued (the first ΔÊ over the frozen 60-day window). No IC is computed,
and no signal is defined to exist, before the warm-up completes. History from any vendor is
`point_in_time:false` and excluded.

**Data source (frozen at a future Stage-1 gate — one source, chosen by availability not result):**
an entitled forward EPS-estimate feed returning, per (symbol, fiscal-period, snapshot-date): mean
estimate, analyst count, currency, adjustment basis. **None currently entitled → DATA-BLOCKED.**
Prices from `panel_2005.parquet` + forward yfinance.

**Point-in-time rules:** forward-only from arming. A snapshot enters only when pulled on/after its
dissemination date, tagged `point_in_time:true`; dedupe on (symbol, fiscal-period, snapshot-date).
No historical backfill is ever scored.

**(Req 2) Fiscal-period matching:** a revision is `ΔÊ = Ê_{t}(fp) − Ê_{t−60}(fp)` for the
**identical fiscal-period identifier fp** (same fiscal-period-end). **No fiscal-year rollover
comparisons** — when the tracked period rolls (e.g., FY1→FY2), the 60-day window resets; the
pre/post periods must carry the same period-end or the observation is dropped.

**(Req 3) Value handling (all pre-committed):**
- **Scaling:** primary signal is **price-scaled** revision `s_raw = ΔÊ(fp) / P_{t}` (revision in
  forward-earnings-yield units) — sidesteps near-zero and negative denominators entirely. Then
  cross-sectionally z-scored per formation date.
- **Near-zero estimate:** no division by the estimate level; price-scaling removes the blow-up.
  Names with `P_t` missing are dropped (never zero-filled).
- **Negative estimates / sign changes:** handled naturally by ΔÊ (a loss shrinking toward profit is
  a positive revision). Loss→profit sign-change events are **flagged and reported as a separate
  robustness bucket**, not special-cased into the signal.
- **Splits:** `Ê_{t−60}` and `P_{t−60}` must be on the **same split-adjustment basis** as `Ê_t`,
  `P_t`. Pre-commit to the vendor's split-adjusted estimate series; assert its adjustment basis
  matches the price panel; if the feed is unadjusted, apply the panel split factor to `Ê_{t−60}`
  before differencing. Any snapshot pair straddling a split with mismatched basis is dropped.
- **Currencies:** restrict to **USD-reporting** members; record currency + adjustment basis per
  name; drop non-USD (no FX conversion in v1).
- **Analyst-count changes:** require `analyst_count ≥ 3` at **both** `t−60` and `t`. Report `Δcount`;
  compute a robustness IC that **excludes coverage-change events** (initiation/drop), so a revision
  is consensus updating, not a change in who is counted.

**(Req 4) Formation schedule (frozen):** **monthly** (last business day) for any portfolio
formation and for the primary IC formation dates. Snapshots may be **collected more frequently**
(e.g., daily/weekly) but the frozen formation cadence is monthly; higher-frequency formation is a
labelled secondary robustness view only.

**Target return:** `y_{i,d} = r_{i,d→d+20} − r_{eq-wt panel, d→d+20}` (market-neutral by construction),
20 trading days; 5d/60d as decay diagnostics; **decision horizon = 20d**.

**(Req 5) Primary statistic & inference:** the primary unit is the **per-formation-date
cross-sectional Spearman IC** `IC_d = corr_rank(s_{·,d}, y_{·,d})`. The statistic is the **mean of
`IC_d` across formation dates**. Inference is **date-clustered / stationary block-bootstrap over
formation dates** with block length ≥ the 20-day horizon to respect forward-return overlap. **All
firm-date observations are NOT treated as independent**; the pooled firm-date t-stat is explicitly
forbidden as the primary test (reported only as a naive upper bound). Overlapping daily-formation
IC is a secondary diagnostic with the same block-bootstrap correction.

**(Req 6) Qualifying formation dates + minimum sample (BOTH required):**
- **Qualifying formation date:** a formation date enters the primary `IC_d` series **only if ≥ 100
  eligible stocks** are present on that date (eligible = USD member with a valid same-period
  revision, `analyst_count ≥ 3`, and a computable 20d forward return). Dates below 100 are dropped
  from the primary series (logged, not counted).
- **Minimums:** the primary test fires only when **(a) ≥ 300 matured firm-level observations**
  (snapshot + 20 trading days ≤ today) **AND (b) ≥ 24 qualifying formation dates** (non-overlapping,
  ≈ monthly ⇒ ~2 years). Neither alone suffices.
- **Report at arming:** median universe coverage per qualifying date and sector concentration
  (GICS shares + issuer/sector HHI), so a thin or sector-skewed panel cannot pass unexamined.

**(Req 7) Factor controls — PIT-supported only:** neutralize/attribute the IC using **only controls
backed by genuinely point-in-time data**. **Required where reliably PIT:** GICS sector, market beta,
size (log market cap, where the PIT cap is reliable), prior price momentum (12-1), realized
volatility, liquidity (ADV / Amihud) — all derivable from the existing PIT price/membership panel.
**Conditional (only if PIT fundamentals are actually available):** value, quality, profitability,
earnings-yield — these are **not** required unless a PIT fundamentals source exists; without one they
are omitted and that omission is stated, not proxied with non-PIT data. **The seven live-book return
series are NOT used as raw cross-sectional regressors** (they are portfolio returns, not stock-level
exposures — a category error). Independence from the live books is tested **separately at the
eventual portfolio stage**, by running the strategy's own return series through the frozen
Orthogonality Benchmark v2 — never by regressing a stock cross-section on book returns.

**Success threshold:** mean 20d `IC_d ≥ 0.03` with block-bootstrap `t ≥ 2`, at ≥300 matured obs and
≥24 qualifying formation dates (≥100 stocks each), **AND** the sector/factor-neutralized IC (PIT
controls only) retains ≥ ⅔ of the raw IC.

**Kill threshold:** at ≥600 matured obs and ≥24 qualifying formation dates, mean 20d `IC_d < 0.01` **OR**
block-bootstrap `t < 1` **OR** factor-neutral IC ≤ 0 → FAILURES.md; no revision spec proposed; data
accrues as infrastructure only. No new scaling, window, horizon, or slice may be added to rescue a null.

**Multiple-testing:** 1 hypothesis + 1 secondary (incremental-over-SUE) + 2 pre-registered
conditioners (sector-relative; high/low dispersion regime), logged in the trial ledger at arming.

**No-retuning / reopening:** 60d window, 20d horizon, monthly formation, thresholds all frozen here.
Reopening after a kill requires a materially different data source or a preregistered new
conditioner — not a nearby parameter variant.

**(Req 9) Timeline:** **UNDETERMINED.** No completion date is stated until an entitled estimate
source, its symbol coverage, and the achievable snapshot frequency are observed. All prior
"months-to-n=300" estimates are withdrawn.

**Operational requirements (when unblocked):** read-only snapshot collector → its own store
(`data/estimates_fwd/`), an isolated read-only checkpoint gate cloned from `earnings_checkpoint.py`
(warm-up + the two sample minimums + data-quality + no-portfolio conditions), offline test, trial
ledger row. No scheduler, no book, no capital path until IC passes AND a separate Stage-4 approval.

---

## 3. Roadmap (unchanged from accepted version — summary)

- **Now:** this probe (done → DATA-BLOCKED); keep the surprise collector accruing; Monday =
  operational transition only. **H-xmkt-etf-staleness stays QUEUED — do NOT run before the first
  clean operational cycle** completes.
- **After panel_stocks_v2:** rerun momentum_concentrated as a new prereg; open FINRA short-interest
  on small/mid-caps. **Price source = Capital IQ (provisional)** — approval requires, first, a
  **physical single-security export** and then a **multi-security scale test** before the panel is
  built. No panel change until both pass.
- **After 300 matured earnings events:** fire the surprise checkpoint.
- **After 3–6m clean forward paper:** first execution-alpha read.
- **Avoid:** new QQQ/vol/trend/leverage variants; EXP-A/B parameter reopens; options/VRP;
  filing-text NLP; index-inclusion; broad sweeps; minute-bar work.

## 4. Decisions for Kristen
1. Approve the post-probe (DATA-BLOCKED) design above? (No freeze/implement yet.)
2. How to unblock estimates: paid Finnhub/EODHD tier · FactSet/CIQ Estimates entitlement · defer the
   lane. (Calendar-consensus snapshotting is a *separate* hypothesis, not an unblock for this one.)
3. Price source for panel_stocks_v2: **Capital IQ provisional**, pending single-security export +
   multi-security scale test (independent of this lane).
4. H-xmkt-etf-staleness: **held** until the first clean operational cycle — not run now.
