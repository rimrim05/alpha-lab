# Alpha Source Registry

*Agent 1 — Independent-Alpha program · 2026-07-10 · machine mirror: `alpha_sources.json`*

The unit of independence is **not the spec** — it is the alpha SOURCE: a
`(information source, mechanism, who-pays)` triple. One strategy can hold several sources;
several strategies can implement ONE source. This registry decomposes every live book and
notable research-object in the repo into its underlying sources so the program never
double-counts a re-implementation as a new edge.

Grounded in the code and ledgers (`scripts/hunt_paper_run.py` BOOKS, `ledgers/hunt2026/`)
and the frozen research record (`FAILURES.md`, `CONFIDENCE_LADDER.md`, `TRIAL_LEDGER.md`,
`robustness/*.md`, `estimator_lab/RESULTS.md`, `specs/*/MECHANISM.md`). Where a doc
contradicted the code, the code/ledgers won.

> [!warning] The headline the promoted list hides
> The **4 promoted books reduce to ONE promoted market source + ONE portfolio object.**
> `vol_managed_qqq`, `vol_core_svxy`, and `trend_vol_qqq` are **three implementations of
> AS-01** (vol-managed US large-cap equity premium) — each bolts on a minor sleeve/overlay
> (VRP sleeve = AS-04, trend gate = AS-02) onto the *same* load-bearing edge.
> `defensive_ensemble` (AS-14) is a **portfolio combination** of AS-01/02/03, not a new
> forecast. The 3 watch-tier books add AS-03 (dual momentum, a near-duplicate of AS-02) and
> AS-05 (cross-sectional stock momentum — a **falsified** signal held only to observe).

## Alpha-class legend (never conflate these)

| Class | What it is | Independent market forecast? |
|---|---|---|
| **Market** | Forecast of an asset's future return — a real edge over the market | ✅ yes |
| **Estimator** | Better estimate of a quantity (covariance, mean) — improves a portfolio | ❌ no |
| **Portfolio** | Combination / sizing of sources already held — Sharpe from diversification | ❌ no |
| **Execution** | Edge from HOW/WHEN orders are placed | ❌ no |

Evidence ladder: 0 Hypothesis · 1 literature-replicated · 2 single blind · 3 walk-forward ·
4 cross-market · 5 forward paper · 6 live capital · **falsified** = tested & refuted.

---

## Registry (all classes)

> [!info]- Full source table — 15 sources across 4 classes
>
> | ID | Source | Class | Level | Status | Implementations | Distinct? |
> |---|---|---|---|---|---|---|
> | AS-01 | Vol-managed US large-cap equity premium | Market | **3** (capped) | **promoted, live** | vol_managed_qqq · vol_core_svxy(core) · trend_vol_qqq(vol) · defensive_ensemble/A | ✅ the one promoted source |
> | AS-02 | Time-series (trend) momentum | Market | 2-3 | live (overlay/sleeve) | trend_vol_qqq(gate) · tsmom_multi_asset · defensive_ensemble/A,B | ✅ |
> | AS-03 | Dual (relative+absolute) cross-asset momentum | Market | 2 | watch, live | dual_momentum_gold · dual_momentum_gem · defensive_ensemble/C | ⚠️ near-dup of AS-02 |
> | AS-04 | Variance risk premium (short-vol carry) | Market | sleeve-only | live as sleeve | vol_core_svxy(sleeve) · svxy_vix_carry(retired) | ✅ |
> | AS-05 | Cross-sectional stock momentum (12-1, large caps) | Market | **falsified** | dead (held to observe) | momentum_concentrated | ✅ |
> | AS-06 | Post-earnings/post-shock drift (PEAD proxy) | Market | 2 | watch | gap_drift | ✅ |
> | AS-07 | Short-term reversal (large caps, daily) | Market | **falsified** | retired | deep_dip_reversion · statarb | ✅ |
> | AS-08 | Low-vol / low-beta anomaly (ranking) | Market | **falsified** | retired | — (only via AS-13 construction) | ✅ |
> | AS-09 | Overnight / close-to-close premium | Market | dormant | no tradable tilt | — | ✅ |
> | AS-10 | Participation-breadth regime timing | Market | retired | retired | breadth_gated_leverage | ✅ |
> | AS-11 | Post-panic recovery drift (VIX-spike) | Market | **falsified** | retired | vix_panic_buyer | ✅ |
> | AS-12 | Price/volume microstructure ranking | Market | **falsified** | retired | (screened only) | ✅ |
> | AS-13 | Dispersion-bias-corrected covariance (JSE/ψ̂ PCA) | **Estimator** | 2 (bounded) | research | pca_minvar_jse · pca_minvar_raw | ✅ (not a market source) |
> | AS-14 | Diversified-premia combination | **Portfolio** | 3 | **promoted, live** | defensive_ensemble | ❌ = AS-01+02+03 |
> | AS-15 | Execution alpha (open+close / intraday) | **Execution** | 0 | none harvested | (ops-reality: measurement only) | ✅ (0 sources yet) |

---

## The market sources that are alive

> [!success]+ AS-01 — Vol-managed US large-cap equity premium (THE promoted source)
> - **Info:** 21d trailing realized vol of the index + the persistent equity premium.
> - **Mechanism:** Moreira-Muir — vol is persistent but expected return is not
>   proportionally higher in high-vol states, so inverse-variance scaling (σ target 0.25,
>   cap 2x) raises Sharpe. It is **levered equity-premium harvesting with a vol-timing kicker.**
> - **Who-pays:** bearers of equity risk; on the timing leg, investors who don't de-lever in
>   high-vol regimes.
> - **Forecast target / horizon:** risk-scaling of a US large-cap index / daily.
> - **Factor exposures:** equity beta (dominant) + short-vol/vol-timing + negative in vol spikes.
> - **Evidence:** level **3**, CAPPED. 1y blind + 82-window WF (+13.4pp median excess, 78%
>   beat-SPY, DSR 81.5%). Cross-market replication was RUN and FAILED — **F-020**, 3/7
>   clusters, p=0.77 → confirmed US-large-cap-equity-specific, level 4 refused.
> - **Failures:** F-020 · F-011 · NR-4 · NR-5.
> - **Implementations:** `vol_managed_qqq`, `vol_core_svxy`(core), `trend_vol_qqq`(vol leg),
>   `defensive_ensemble`(sleeve A). **← the three promoted directional books are all THIS.**
> - **Forward test:** live paper, promoted; needs a pre-registered horizon for level 5.

> [!success]+ AS-02 — Time-series (trend) momentum
> - **Info:** 200d SMA (index gate) or 252d return-sign (cross-asset). **Mechanism:**
>   Moskowitz-Ooi-Pedersen underreaction/autocorrelation. **Who-pays:** against-trend
>   rebalancers/hedgers.
> - **Evidence:** level 2-3. Index gate reaches 3 **only as a tail hedge inside AS-01** —
>   **F-014**: trend+vol combined HALVES median excess (+8.0pp vs +13.4pp either parent), a
>   priced tail hedge, NOT additive alpha. Cross-asset tsmom is level-2 sleeve-only. **F-020**:
>   gate replicates in 4/7 clusters (p=0.50).
> - **Failures:** F-014 · F-020 · F-012 · NR-3 · NR-5.
> - **Implementations:** `trend_vol_qqq`(gate), `tsmom_multi_asset`(sleeve), `defensive_ensemble`
>   (A gate + B), `bench_qqq_sma200_2x`, `trend_gated_spy_2x`(retired).
> - **Distinct?** ✅ one mechanism, two universes (index vs cross-asset). Its real value is
>   crisis-alpha diversification inside AS-14 — not an independent additive forecast over AS-01.

> [!warning]+ AS-03 — Dual (relative+absolute) cross-asset momentum — near-duplicate of AS-02
> - **Info:** 252d return ranked across SPY/QQQ/GLD + absolute vs BIL; TLT/BIL defensive leg
>   momentum-picked. **Mechanism:** Antonacci dual momentum — same TSMOM underreaction premium
>   with a winner-take-all crash gate.
> - **Evidence:** level 2, discounted. 5y blind (gold +29.1%, gem +17.9%) but gold-menu was
>   hindsight-tinted; WF +6.9pp median excess unremarkable. **F-020** (defensive-asset): the
>   gold third slot is a 2024-26 REGIME ARTIFACT (wins 13% of pre-2024 windows). **F-012:** the
>   12m gate protects against SLOW bears only.
> - **Implementations:** `dual_momentum_gold`, `dual_momentum_gem` (both watch-tier, live),
>   `defensive_ensemble`(sleeve C).
> - **Distinct?** ⚠️ **NO, mechanistically** — same underreaction premium & who-pays as AS-02;
>   distinguished only by relative-strength selection + regime-switch construction. Its own
>   implementation family, not an independent source. NB: gem and gold currently hold the
>   IDENTICAL position `{QQQ:1.5}` — live independence ≈ 0 right now.

> [!success]+ AS-04 — Variance risk premium (short-vol carry) — sleeve-only
> - **Info:** VIX vs realized/median vol. **Mechanism:** implied > realized variance → selling
>   variance earns carry. **Who-pays:** buyers of tail/variance insurance.
> - **Evidence:** standalone RETIRED — **F-007** (failed both blinds; daily-close gates ate the
>   Aug-2024/Apr-2025 gaps; post-2018 SVXY at −0.5x halves the carry). Survives ONLY as the 0.3
>   sleeve inside `vol_core_svxy`.
> - **Distinct?** ✅ genuinely distinct (VRP ≠ equity premium) but gap- and capacity-limited —
>   it is why `vol_core_svxy` scores capacity/complexity 3 vs `vol_managed_qqq`'s 5.

> [!note]+ AS-06 — Post-earnings/post-shock underreaction drift (PEAD proxy) — watch
> - **Info:** 1d ≥ 2.5σ move confirmed by volume ≥ 3× median (a **free-data proxy** for an
>   earnings surprise). **Mechanism:** anchoring/slow update → ~60d drift. **Who-pays:** anchoring
>   crowd + passive flow; fast money won't warehouse 60d single-name event risk.
> - **Evidence:** level 2 watch — 1y blind +5.8% excess PASS, but 5y decayed to +12.3% and WF
>   worst −53.4% (**F-009**). **The proxy fires ~1/day and catches NON-earnings shocks; the real
>   "drift after REAL earnings surprises" was never tested — no point-in-time earnings data
>   exists in the repo.** `ic-earnings-fwd` is accruing forward-only PIT data from 2026-07-10.
> - **Implementation:** `gap_drift`. **Distinct?** ✅ (the proxy is a stand-in for a real, untested source).

---

## The market sources that are dead or dormant (do not re-run their funerals)

> [!failure]- AS-05 · AS-07 · AS-08 · AS-11 · AS-12 — falsified market sources
> - **AS-05 Cross-sectional stock momentum (12-1, large caps):** rank IC −0.001 (t=−0.07, 135
>   months); sector/residual/52w-high variants all ≈0 and 0.97-correlated with raw (**F-015,
>   F-016, +addendum, NR-2**). `momentum_concentrated`'s tolerable windows came from CONSTRUCTION,
>   not selection. Held watch-tier only to see if IC returns live.
> - **AS-07 Short-term reversal (daily):** gross real (+15.8%/yr decile spread) but turnover eats
>   it — four designs, four deaths (**F-001/003/004/008, F-017, NR-1**). Do not run a fifth at 10
>   bps/side.
> - **AS-08 Low-vol/low-beta ranking:** IC ≈ 0, negative in 2025 (**F-018**). Any residual low-vol
>   edge is variance-ESTIMATION (AS-13), not a return forecast.
> - **AS-11 Post-panic recovery drift (VIX-spike add):** WF worst −62.1% in the GFC cascade
>   (**F-013, NR-3**). Reopen only with a pre-registered regime guard whose worst window (incl.
>   2008) is > −30%.
> - **AS-12 Price/volume microstructure ranking:** flat every half-decade (**F-019**). Reopen only
>   on a higher-frequency harness.

> [!note]- AS-09 · AS-10 — dormant / retired
> - **AS-09 Overnight premium:** real (~9%/yr of the equity return) but a 126d overnight-share tilt
>   has ZERO cross-sectional power close-to-close (**F-006, F-019**). **Execution-gated** — reopens
>   only with open+close execution (see AS-15). No independent tradable forecast today.
> - **AS-10 Participation-breadth regime timing:** `breadth_gated_leverage` — WF worst −44.5%,
>   killed with the static-leverage pattern (**F-011, NR-4**). Mostly levered beta in a costume.

---

## The sources that are NOT market forecasts (do not count them as edges)

> [!abstract]+ AS-13 — Dispersion-bias-corrected covariance (JSE/ψ̂ PCA) · **Estimator**
> - **Info:** NO new market information — same return panel; the edge is a better covariance
>   eigenstructure. **Who-pays:** nobody — it improves the RISK estimate of a long-only min-var
>   book, it does NOT forecast return.
> - **Evidence:** level 2, BOUNDED (**F-021 RESOLVED**). DEAD at n=252 and unconstrained
>   (+14 to +31 bps vol, worse than raw); ALIVE at small-n long-only (n=63: −2.0 bps at k=3,
>   t=−6.0; helps at every n long-only, benefit −0.24 bps per unit p/n). k=1 long-only delta
>   ≈ noise (**F-010**). The publishable claim is the **boundary**, not a return.
> - **Implementations:** `pca_minvar_jse` vs `pca_minvar_raw` (matched pair). Competing estimators
>   (MP-clipping best unconstrained, LW second) are the same class.
> - **⚠️ Never count this as a market source** — a 1-2 bps vol improvement is an estimator win, not
>   an independent forecast.

> [!abstract]+ AS-14 — Diversified-premia combination (`defensive_ensemble`) · **Portfolio**
> - **Info:** the sleeve returns of AS-01/02/03 and their low pairwise correlation. **Mechanism:**
>   combine three premia surviving on different return sources at equal risk / inverse-vol, vol-
>   targeted ~18%; ensemble Sharpe > any single sleeve because the sleeves are near-uncorrelated.
> - **Evidence:** level 3 — 5y blind + WF CAPITAL-PRESERVER role: 84% positive, worst −18.3%, DSR
>   95.8%, flat 2022. But value-vs-naive only **+1.4pp median excess** — value lives in the
>   drawdown column, not in return.
> - **Distinct?** ❌ **NO** — it is a PORTFOLIO object over sources it already holds (= AS-01 +
>   AS-02 + AS-03). Its independence is real at the RISK level (diversification), not at the
>   FORECAST level. Falsifier: sleeve pairwise corr > 0.7 in a stress quarter.

> [!abstract]+ AS-15 — Execution alpha (open+close / intraday) · **Execution** · 0 sources yet
> - No execution edge harvested. `ops-reality` MEASURES drag (≤15 bps stocks / ≤5 bps ETFs, reject
>   < 2%/night, tracking drag < 30 bps/month) but harvests nothing. Two reopen hooks depend on it:
>   **F-001** (reversal at ≤2-3 bps/side) and **F-006** (overnight tilt with open+close execution).
> - An execution improvement is NOT a market forecast — placeholder class, zero current sources.

---

## Distinctness verdict

- **Genuinely distinct MARKET sources catalogued:** 12 (AS-01…AS-12).
- **Alive market sources:** 3 — AS-01 (promoted), AS-02 (overlay/sleeve, tail-hedge/diversifier),
  AS-04 (sleeve-only VRP).
- **Watch market sources:** 2 — AS-03 (⚠️ near-duplicate of AS-02) and AS-06 (proxy, real PEAD untested).
- **Falsified/retired market sources:** 7 — AS-05, AS-07, AS-08, AS-09(dormant), AS-10, AS-11, AS-12.
- **Non-market:** 1 Estimator (AS-13), 1 Portfolio (AS-14), 0 Execution sources (AS-15 is a placeholder).
- **Spec implementations mapped:** 20.

> [!warning] Bottom line for the independent-alpha program
> Across 7 live paper books and ~20 total specs there is exactly **ONE promoted, independent
> market source** (AS-01, and it is capped at level 3 with a cross-market FAIL). Everything else
> promoted is either an implementation of AS-01, a non-additive overlay of it (AS-02 trend gate,
> F-014), a gap-limited sleeve (AS-04), or a portfolio re-package of sources already held (AS-14).
> The watch books add a near-duplicate (AS-03) and a falsified signal (AS-05). **The program's
> real independent-alpha surface is far narrower than the book count suggests — the honest number
> of live, distinct, independent market forecasts is 1 (AS-01), 2 if you credit AS-02 as a
> standalone diversifier and 3 if you credit AS-04's VRP as a sleeve.**
