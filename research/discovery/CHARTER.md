# Additional Discovery Program — sandbox charter

*Stood up 2026-07-10. A sandboxed research feeder, separate from the frozen 7-book paper
portfolio and the Core Evidence Program. Full governing charter: the Director brief (chat).
This file is the on-disk operating record.*

## Mission
Discover whether Alpha Lab can find **one genuinely independent economic return source** —
distinct information, distinct mechanism, positive residual return after controlling for the
existing portfolio — that is NOT another expression of the US-equity / QQQ / trend / vol-scaling
/ leverage / momentum complex. The ideal output is **one replicated research object**, not
another strategy that makes 20% by owning QQQ.

## Hard boundaries (may / may-not)
**May:** generate hypotheses, collect new data, build measurement experiments, run frozen
historical tests, create shadow-paper candidates, propose research objects.
**May NOT** (control plane owned by the Deployment Coordinator — DEPLOYMENT_MANIFEST.md § Governance):
alter the 7-book manifest, change allocations, touch schedulers, edit frozen live specs, add an
8th funded book, reinterpret watch-tier as validated, bypass the Failure DB / Red Team, or
promote anything to deployment. Any discovery exits only through Research Director → Red Team →
Stage-4 approval.

## Discovery funnel (a candidate advances stage by stage)
0 Hypothesis (mechanism only) · 1 Measurement (does the phenomenon exist? IC/decay/stability or
TS residual relationship) · 2 Independent replication (era / dataset / market / prospective) ·
3 Portfolio construction (naive vs sophisticated) · 4 **Residual independence** (the
[orthogonality_benchmark.py](orthogonality_benchmark.py) gate — not U.S. beta with new timing) ·
5 Stress & Red Team · 6 Shadow paper (separate ledger, no funded allocation) · 7 Main-program review.

## Verdict vocabulary (every completed experiment ends on one)
`REJECTED` · `MECHANISM UNSUPPORTED` · `MEASUREMENT SUPPORTED` · `REPLICATION REQUIRED` ·
`PORTFOLIO CANDIDATE` · `SHADOW-PAPER CANDIDATE` · `NOT INDEPENDENT` · `BLOCKED BY DATA` ·
`BLOCKED BY EXECUTION`.

## What is genuinely new (else it's rejected by default)
New **information** (earnings/revisions/short-interest/options/term-structure/carry/macro/flows),
NOT a new transform of close/volume/vol/MA. Plus a **distinct mechanism** (who makes it, who pays,
why it persists, what arbitrages it away) and **residual independence** vs SPY/QQQ/trend/vol/the
7 books/sectors. Reject-by-default list: another MA length, another momentum horizon, another
residual-momentum transform, another low-vol ranking, another dual-momentum menu asset, another
VIX-panic or levered-QQQ wrapper, indiscriminate ETF replication, HFT without an execution model,
auto-generation without mechanism review, parameter search, retrospective regime selection,
short-history live adaptation.

## Backlog reuse (do not regenerate)
Hypotheses already generated, deduped, and ranked live in
[../independent_alpha/HYPOTHESIS_QUEUE.md](../independent_alpha/HYPOTHESIS_QUEUE.md) +
[EXPERIMENT_QUEUE.md](../independent_alpha/EXPERIMENT_QUEUE.md); dead ends in
[../hunt2026/FAILURES.md](../hunt2026/FAILURES.md). The Discovery lanes 1-6 map onto the existing
lanes A-F — this program **extends** that backlog, it does not re-run hypothesis generation.
See [INITIAL_PROGRAM_DEDUP.md](INITIAL_PROGRAM_DEDUP.md) for the Experiment 1-5 reconciliation.

---

## Maintenance mode (entered 2026-07-10)

After EXP-A (REJECTED) and EXP-B (MECHANISM UNSUPPORTED on the current panel), the Discovery Program
shifts from active hunting to maintenance. Standing rules:

1. **Keep accumulating point-in-time earnings events** (Finnhub collector, enabled + read-only,
   toward n≥300 — the highest-value unresolved lane).
2. **Maintain the data + orthogonality infrastructure** (FRED/VIX state layer; Orthogonality
   Benchmark v2). Keep the data-layer gate: no revised macro (GDP/CPI/payrolls) without ALFRED
   vintages; VIX/VIX3M state-only.
3. **A genuine data upgrade is required before reopening carry** (FX/commodity term-structure or
   futures/roll data) — NOT another free-data ETF-yield variation.
4. **Do not launch another broad free-data hypothesis hunt.** In-repo price/volume is exhausted;
   free-data carry and cross-asset vol-management are closed on their tested panels.
5. **Keep all candidates outside the funded seven-book roster.** Nothing promotes to paper without
   Research Director → Red Team → Stage-4.

Do not reopen EXP-A or EXP-B with nearby parameter variations (charter § 5).

## Current Discovery conclusion (2026-07-10)

- **No validated independent return source has been found.**
- **Free-data bond carry is REJECTED in the tested Treasury-ETF form** (mechanical duration; fails
  orthogonality via risk-off rolling-corr breach). Not a general disproof.
- **Volatility management remains market-specific**, not a mechanistically transportable rule (F-020
  narrowed, not overturned; insufficient cluster-level power).
- **Earnings and revisions remain the highest-value unresolved lane** — data-gated, accruing.
- **Further progress now depends more on new data than on new transformations.**
