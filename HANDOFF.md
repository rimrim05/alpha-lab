# HANDOFF — Alpha Lab state (2026-07-11)

One-read orientation for a new session. Everything below is committed. **DEPLOYMENT_MANIFEST.md is the
single authority on live/deployment state; where anything disagrees, the manifest wins.**

## Governance (read first)
- **Single-writer control plane** (DEPLOYMENT_MANIFEST.md § Governance): one Coordinator owns
  `scripts/hunt_paper_run.py`, `DEPLOYMENT_MANIFEST.md`, `research/hunt2026/STATUS.md`, `ledgers/**`,
  scheduler config. Other sessions write **isolated research artifacts only** and must not touch the control plane.
- **Multiple sessions run concurrently** in this repo (a red-team/director session has been active). Prefer
  additive new files; don't edit another session's in-flight files.
- Paper-only throughout. No real-money path. Never `--live` by hand. Keys live in gitignored `.env`.

## Program states
- **Paper books:** 7 live, equal-weight (~$14.4k each), **FROZEN through the +3-month gate**. Classified
  (manifest): core-evidence (vol_managed_qqq, vol_core_svxy, trend_vol_qqq) + capital-preservation sleeve
  (defensive_ensemble) + 3 shadow-research controls (dual_momentum_gold/gem, momentum_concentrated).
  **Not seven independent alphas** — n_eff ≈ 2.8.
- **Independent-Alpha program** (`research/independent_alpha/`): **1 provisional, era-replicated market
  cluster (AS-01, US vol/trend risk-management)** — Level 3, no Level-4/5 yet. See `CANONICAL_STATE.md`,
  `INDEPENDENCE_MATRIX.md`, `memos/independent-alpha-program-2026-07-10.md`.
- **Discovery program** (`research/discovery/`): **maintenance mode** (CHARTER.md). EXP-A bond-carry
  **REJECTED** (mechanical duration, F-022); EXP-B conditional-vol **MECHANISM UNSUPPORTED** (F-020
  addendum). Orthogonality Benchmark v2 = the permanent independence gate (`orthogonality_benchmark.py`).
  **Earnings checkpoint armed but dormant** (`earnings_checkpoint.py`, 0/300 matured) — the one live signal.
- **Stock-universe repair** (`research/stock_universe_repair/`): survivorship gap = **382 of 1,202
  ever-S&P members missing** from panel_2005. Polygon reference/delisting layer done (`delisting_map.csv`,
  205/382 dated). Rename candidates (`rename_candidates.csv`) — all `pattern_candidate`, continuity=False,
  manual-review. **CIQ Pro pilot: 4/6 identity traps PASS** (`PILOT_RESULTS_CIQ.md`) — provisionally PASSING.

## Data sources / keys (in gitignored `.env`)
- **Polygon** (`POLYGON_API_KEY`): reference-only tier — delisted tickers/dates/FIGI/splits/dividends work;
  **price bars 403** (need paid tier). See `research/stock_universe_repair/POLYGON_ENTITLEMENT_CHECKLIST.md`.
- **FactSet** (`FACTSET_USERNAME_SERIAL=HAAS-2415100` + key): auth OK, **Entity Report Builder only**;
  Prices/Fundamentals/Estimates = 403 not entitled. `research/discovery/data/FACTSET_STATUS.md`.
- **FRED/VIX state layer**: built + audited **PASS** (`research/discovery/data/fred_state_layer.py`,
  `DATA_QUALITY_REPORT.md`). Rates 2005+, VIX/VIX3M state-only. No revised macro (GDP/CPI) without ALFRED.
- **Capital IQ Pro** (Berkeley): live access; **CIQ SPA resists browser automation** (never-idle + custom
  search) — pilot run manually/by the parallel session. **Finaeon**: reachable via institutional anonymous login.

## Open items / next actions
1. **Stock-universe repair — finish the pilot:** KD (spinoff), HTZ (relisting continuity), **Finaeon**
   (WAMUQ/GM-MTLQQ are the decisive coverage tell), and the **CIQ estimates PIT test** (look for
   As-Of/Snapshot/Revision/Point-in-Time labels). Spec + template: `PILOT_6_SECURITY.md` +
   `BERKELEY_ENTITLEMENT_PROTOCOL.md`. **Panel unchanged until the pilot produces entitlement evidence.**
2. **Price source decision** (repair's real blocker): Polygon price-tier upgrade vs GFD/Finaeon vs Capital IQ
   — pending the pilot. WRDS/CRSP + I/B/E/S are unavailable (reference standards only).
3. **Discovery**: stays maintenance mode; keep the earnings collector accruing toward n≥300; no new free-data hunt.
4. **Operational**: see the latest memo in `memos/` for the Monday 2026-07-13 operational-transition / flatten gate.

## Entry-point files
`DEPLOYMENT_MANIFEST.md` · `research/independent_alpha/CANONICAL_STATE.md` · `research/discovery/CHARTER.md`
+ `FINDINGS.md` · `research/stock_universe_repair/PILOT_6_SECURITY.md` + `PILOT_RESULTS_CIQ.md` · `memos/`
· `research/hunt2026/{STATUS,TRIAL_LEDGER,FAILURES}.md`.
