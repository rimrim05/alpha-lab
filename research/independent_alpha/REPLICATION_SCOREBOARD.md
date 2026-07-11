# REPLICATION_SCOREBOARD.md — what has and has NOT replicated (2026-07-10)

Agent 8 (independent-alpha program). Compiles replication evidence across **independent
dimensions** — markets, eras/regimes, correlation clusters, sign, effect size, failure
regimes, data vendor — for the live vol/trend cluster and the three watch-tier momentum
books. Reuses, does not rebuild: CONFIDENCE_LADDER.md, FAILURES.md (F-014/15/16/20/21),
robustness/{xmarket,defensive_asset}.md, walkforward/summary.md, results5y/summary.md,
memos/hunt2026-walkforward.md.

**Ladder recap (robustness axis, CONFIDENCE_LADDER.md):** 0 idea · 1 lit-replicated ·
2 single blind · 3 multi-window walk-forward · 4 cross-market · 5 live paper · 6 live capital.
**Repo ceiling today = level 3.** Level 4 was RUN and REFUSED for the vol family (F-020).

**Two things the whole repo shares as replication gaps** (apply to every row below):
- **Single data vendor.** Everything is EODHD prices → `panel_2005.parquet`. No second-vendor
  or second-data-build replication exists anywhere. Data-vendor sensitivity is **UNTESTED** for
  every source; treat vendor robustness as an open hole, not a pass.
- **No point-in-time fundamentals.** No PIT earnings/analyst data in the repo, so any
  earnings/estimate-conditioned reopen (F-016) cannot be tested here.
- **Overlapping windows.** 252d window / 63d step → 82 windows ≈ ~20 independent draws
  (~4x fewer than the raw count). Every "N-window" claim below is discounted accordingly.

---

## 1. Scoreboard (one row per independent source; correlated ETFs = ONE cluster)

| source | class of alpha | markets/eras tested | independent clusters | sign consistent? | effect-size consistent? | replicates? | level |
|---|---|---|---|---|---|---|---|
| **US large-cap vol/trend cluster** (vol_managed_qqq, vol_core_svxy, trend_vol_qqq — 3 implementations of ONE mechanism) | Market (risk-mgmt / levered equity premium) | US large-cap equity only; 8 regimes GFC→2024-26 via 82 WF windows | **1** (all three trade QQQ/SPY; NOT three markets) | **Yes** in-domain: +median excess every WF era | **Partly** — level, not universal (see §2) | **Yes, in-domain only**. Cross-market NO (F-020, 3/7 clusters, p=0.77) | **3** (capped; L4 refused) |
| **defensive_ensemble** | **Portfolio** (multi-asset inverse-vol sleeve) | multi-asset ETFs; 80 WF windows, 8 regimes | portfolio construction, not a market forecast — **not an independent market signal** | Yes (84% positive) | Yes but small: +1.4pp median excess; value is drawdown (worst −18.3%) | **Yes as a capital-preserver role**; NOT as an 18%/yr market alpha | **3** |
| **dual_momentum_gold** | Market (cross-asset dual momentum) | SPY/QQQ/GLD menu; 70 WF windows + 5y blind | 1 (absolute/relative mom on an equity-led menu) | Mixed | **NO** — edge is regime-conditional | **Era-conditional only** (see §3) | **2** (discounted) |
| **dual_momentum_gem** | Market (cross-asset dual momentum) | Global equity / bonds GEM; 70 WF windows | 1 (same family as gold; currently holds identical QQQ position) | Yes-ish (+9.3pp WF median excess) | Not durable — retired for fragility (F-012) | **Not independently**; whipsaw-favorable draw | **2 (retired-in-ledger, live for forward evidence only)** |
| **momentum_concentrated** | Market (cross-sectional stock momentum) | S&P 500 stocks 2014+; 44 WF windows + IC screen | 1 (12-1 XS momentum) | **NO** — dies out of sample | **NO** — −4.6pp median excess; rank IC ≈ 0 | **FAILED to replicate** (F-015 return space + F-016 signal space) | **2 (capped, sleeve-only)** |

---

## 2. Vol/trend cluster — universal FAILURE vs conditional-domain SUCCESS

**This is the central distinction.** The mechanism is real *where it lives* and refuted *as a
universal law*. Both are true; report both.

> [!success] Conditional-domain success — level 3, US large-cap equity
> - **Era replication (the strong evidence):** vol_managed_qqq beats SPY in **78% of 82 WF
>   windows**, +13.4pp median excess, ≥18% in 59%, positive across GFC / euro-2011 / china-2015 /
>   volmageddon-2018 / COVID / inflation-2022. vol_core_svxy 85% beat-SPY, +12.4pp. This survives
>   the `oos_*` clean-subset restriction (memos/hunt2026-walkforward.md).
> - **Sign consistency in-domain:** positive median excess in every era bucket tested. Not one
>   regime flips it negative in US equity.
> - **Two blind eras confirm:** 1y blind (round-1) and 5y blind 2021-26 (round-2, trend_vol_qqq
>   +24.7% CAGR, non-overlapping fit ≤2021-07-10) — genuinely non-overlapping holdout eras.

> [!failure] Universal failure — level 4 refused (F-020, robustness/xmarket.md)
> - **Cross-market:** frozen params sprayed unchanged onto 28 assets → **7 correlation clusters**.
>   Vol management improves cluster-median Sharpe in **3/7** (sign-test p=0.77), trend gate 4/7
>   (p=0.50), combo 4/7 (p=0.50) — indistinguishable from a coin flip.
> - **The 14 intl-equity + IWM/MDY/VNQ/HYG funds are ONE global-equity draw, not 18.** Ticker-level
>   "14/28 improved" is not 14 independent replications — this is the single most important
>   correction on the scoreboard.
> - **Effect size:** class-median ΔSharpe tiny and mixed-sign (intl-eq −0.01, bonds +0.03,
>   commod +0.02, fx +0.01). Isolated wins (VNQ +0.18, UNG, DBC) are cherry-picks — the gate
>   "wins" on disasters by owning less of a melting asset.
> - **Verdict:** the edge is levered **equity-premium harvesting**, confirmed US-large-cap-specific.
>   It does not travel. Level 4 is not unattempted — it was tested and **refused**.

**Internal replication caveat (F-014, NR-5):** the *combination* trend+vol does NOT replicate as
additive alpha — combo +8.0pp median vs +13.4pp for **either** naive parent alone. The combo buys
tail relief (worst −22% vs −31%), not return. trend_vol_qqq is level-3 **robust** but its economic
value claim is capped: a priced hedge, not independent estimator/market alpha.

**Cluster-count honesty:** the four "promoted" books are **one market-alpha mechanism + one
portfolio sleeve**, not four independent survivors. vol_managed / vol_core / trend_vol are three
expressions of US-equity vol/trend risk management (correlated → one cluster); defensive_ensemble
is a Portfolio-alpha construction, not an independent market forecast. Counting them as "4 alphas"
would overstate independence ~3x.

---

## 3. Era/regime-conditional sources (did NOT reach level 3)

> [!warning] dual_momentum_gold — REGIME ARTIFACT (defensive_asset.md, pre-registered)
> - The GLD third slot beats the {SPY,QQQ} NONE menu in **21% of all 70 windows, 13% pre-2024**
>   (pre-2024 median delta −0.61%). The **entire** edge sits in 10 windows ending 2024-26 (70%
>   wins, +18.6% median delta); by-year, the only big positive years are 2025 (+62%) and 2026 (+51%).
> - Pre-registered rule → **regime artifact CONFIRMED** (pre-2024 win share ≤52% and median delta
>   ≤+0.5%). For ~15 years the third slot was a net DRAG whatever filled it; NONE has the best
>   median excess (+11.3%) of all 10 variants.
> - **Replication verdict:** fails the era test. Its 5y-blind +29.1% is a single favorable draw of a
>   regime-timed menu. Stays level **2 (discounted)**, live for forward evidence only under the
>   watch-tier kill rule (demote-to-flat on 2 consecutive quarters below exposure-matched SPY).

> [!warning] dual_momentum_gem — FRAGILE (F-012, ledger #6)
> - WF median excess +9.3pp looks fine, but retired-in-ledger for fragility: the 1y-blind star was
>   whipsaw-favorable; the 12m gate gave COVID −41% in-train, 2022 −25.5% blind (NR-3: slow gates
>   don't stop fast crashes). Currently holds an **identical position to gold** (both {QQQ:1.5}) —
>   real independence between the two is ~0 at this instant. Level **2**, forward-evidence only.

> [!failure] momentum_concentrated — FAILED cross-regime + cross-space (NR-2)
> - **Two independent measurement spaces, same kill:** F-015 (return space, 44-window WF: −4.6pp
>   median excess, beats SPY 41%, the 2015-20 momentum winter dominates) **and** F-016 (signal space:
>   monthly rank IC −0.001, t=−0.07, 135 months, measured before any portfolio construction).
> - The tolerable windows came from **construction** (concentration + vol targeting), not selection
>   skill. F-016 addendum: sector-relative / residual / 52w-high variants all die with it (IC by-year
>   ~0.97-correlated — same dead signal, lower amplitude).
> - **Replication verdict:** cross-sectional stock momentum is dead in large caps post-2015. Its 1y
>   blind is a favorable draw. Level **2 (capped, sleeve-only)** — kept only as a near-uncorrelated
>   diversifier, never standalone. Reopen only on small caps / interaction conditioning / live IC return.

---

## 4. Replication dimensions — matrix

Legend: ✓ replicated · ~ partial/small · ✗ failed · — untested.

| dimension | vol/trend cluster | defensive_ensemble | dual_mom_gold | dual_mom_gem | mom_concentrated |
|---|---|---|---|---|---|
| **Eras/regimes (WF)** | ✓ 78-85% beat-SPY, 8 regimes | ✓ 84% positive | ✗ edge only 2024-26 | ~ +9.3pp but fragile | ✗ −4.6pp, 2015-20 winter |
| **Non-overlapping holdout eras** | ✓ 1y + 5y blind (round-2 fit ≤2021) | ✓ 5y blind +19.9% | ~ 5y blind pass but regime-timed | ✗ whipsaw draw | ✗ 1y draw refuted by WF |
| **Independent clusters (cross-market)** | ✗ 3/7, p=0.77 (F-020) | n/a (portfolio) | ✗ 1 cluster | ✗ 1 cluster (=gold) | ✗ 1 signal, dead by IC |
| **Sign consistency** | ✓ in-domain / ✗ cross-market | ✓ | ✗ | ~ | ✗ |
| **Effect-size consistency** | ~ level in-domain, mixed-sign out | ~ small (+1.4pp) | ✗ | ✗ | ✗ |
| **Additivity of layers (internal)** | ✗ combo ≤ parent (F-014) | ~ sleeve-mix | — | — | ✗ construction, not selection |
| **Failure regime named** | GFC serial VIX spikes; all non-US classes | shallow-DD, low ≥18% | pre-2024 (15y drag) | fast crashes (COVID/2022) | post-2015 momentum winter |
| **Data-vendor sensitivity** | — single vendor | — | — | — | — |

---

## 5. Answer to the task

**Reached level 3 (multi-window walk-forward, in-domain):**
- **The US large-cap vol/trend cluster** — vol_managed_qqq, vol_core_svxy, trend_vol_qqq. ONE
  mechanism, three expressions. Level 3 and **capped there** — cross-market replication was run
  and refused (F-020), so no level 4. trend_vol_qqq is robustness-3 but economic-value-capped
  (F-014: hedge, not additive alpha).
- **defensive_ensemble** — level 3 in its **Portfolio / capital-preserver role only**, not as an
  independent market alpha (it is portfolio construction, not a market forecast).

**Era/regime-conditional (did NOT reach level 3):**
- **dual_momentum_gold** — regime artifact (defensive_asset.md); entire edge in 2024-26. Level 2.
- **dual_momentum_gem** — fragile, whipsaw-favorable draw; identical live position to gold. Level 2.
- **momentum_concentrated** — failed both return-space and signal-space replication (NR-2);
  cross-sectional large-cap momentum is dead post-2015. Level 2, sleeve-only.

**Repo-wide:** nothing is above level 3. No level-4 cross-market result exists (the only attempt,
F-020, failed). Data-vendor replication (a distinct independent dimension) is UNTESTED for every
source — the single largest un-run replication check remaining.
