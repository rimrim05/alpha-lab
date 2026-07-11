"""EXP-2026-07-10-defensive-asset: vary ONLY the third risk-menu asset of the frozen
dual_momentum_gold framework (spec.py untouched). 10 registered variants, all reported.

Writes robustness/defensive_asset.md. See preregistrations/defensive-asset-2026-07-10.md.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parents[1]
sys.path.insert(0, str(HERE))
import harness
from walk_forward import REGIMES, rolling_windows

PARAMS = {"lookback": 252, "risk_leverage": 1.5, "defensive_leverage": 1.0}
DEFENSIVE_MENU = ["TLT", "BIL"]
SPLIT = pd.Timestamp("2024-01-01")  # pre-registered pre/post split

VARIANTS = {  # name -> third risk-menu asset (None = two-asset menu, "EQW" = synthetic)
    "GLD": "GLD", "TLT": "TLT", "DBC": "DBC", "XLU": "XLU", "XLP": "XLP",
    "UUP": "UUP", "SLV": "SLV", "VNQ": "VNQ", "NONE": None, "EQW": "EQW",
}
EQW_LEGS = ["GLD", "TLT", "BIL"]


class MenuSpec:
    """Frozen dual_momentum_gold logic (spec.py 2026 freeze), third menu slot swapped."""

    def __init__(self, third):
        self.third = third

    def target_weights(self, panel):
        lb, risk_lev, def_lev = PARAMS["lookback"], PARAMS["risk_leverage"], PARAMS["defensive_leverage"]
        third = self.third
        risk_menu = ["SPY", "QQQ"] + ([third] if third not in (None, "EQW") else [])
        cols = sorted(set(risk_menu + DEFENSIVE_MENU + (EQW_LEGS if third == "EQW" else [])))
        close = panel["close"][cols]
        idx = close.index

        mom = close / close.shift(lb) - 1.0
        mom_cols = list(mom.columns)
        if third == "EQW":
            # synthetic daily-rebalanced equal-weight GLD+TLT+BIL third asset
            eqw_nav = (1 + close[EQW_LEGS].pct_change(fill_method=None).mean(axis=1)).cumprod()
            mom = mom.assign(EQW=eqw_nav / eqw_nav.shift(lb) - 1.0)
            risk_menu = ["SPY", "QQQ", "EQW"]
            mom_cols = list(mom.columns)

        month_end = idx[:-1][idx[1:].month != idx[:-1].month]
        rebal = pd.DataFrame(index=month_end, columns=cols, dtype=float)
        picks = pd.Series(index=month_end, dtype=object)  # which slot was chosen (diagnostics)
        for t in month_end:
            m = mom.loc[t]
            row = pd.Series(0.0, index=cols)
            if not m[mom_cols].isna().any():
                best = m[risk_menu].idxmax()
                if m[best] > m["BIL"]:
                    if best == "EQW":
                        row[EQW_LEGS] = risk_lev / len(EQW_LEGS)
                    else:
                        row[best] = risk_lev
                    picks.loc[t] = best
                else:
                    d = m[DEFENSIVE_MENU].idxmax()
                    row[d] = def_lev
                    picks.loc[t] = "DEF"
            rebal.loc[t] = row
        self.picks = picks.dropna()
        return rebal.reindex(idx).ffill().fillna(0.0)


def main():
    panel = pd.read_parquet(HERE / "panel_2005.parquet")
    spy_windows = dict(rolling_windows(harness.spy_benchmark(panel)["net_daily"]))

    results = {}
    for name, third in VARIANTS.items():
        spec = MenuSpec(third)
        r = harness.run(spec, panel)
        wins = rolling_windows(r["net_daily"])
        results[name] = {"windows": dict(wins), "picks": spec.picks, "run": r}
        print(f"{name}: {len(wins)}w median {np.median([v for _, v in wins]):+.1%}")

    # common window set (BIL binds all variants identically, but be exact)
    common = sorted(set.intersection(*[set(v["windows"]) for v in results.values()]))
    assert len(common) >= 60, f"only {len(common)} common windows"

    rows, marginal_rows = [], []
    for name, res in results.items():
        rets = np.array([res["windows"][d] for d in common])
        vs_spy = np.array([res["windows"][d] - spy_windows[d] for d in common if d in spy_windows])
        picks = res["picks"]
        third_label = "EQW" if name == "EQW" else name
        n_risk_on = int((picks != "DEF").sum())
        third_share_all = float((picks == third_label).mean()) if name != "NONE" else 0.0
        third_share_riskon = float((picks == third_label).sum() / n_risk_on) if (name != "NONE" and n_risk_on) else 0.0
        rows.append({"variant": name, "median": np.median(rets), "ge18": (rets >= 0.18).mean(),
                     "pos": (rets > 0).mean(), "worst": rets.min(),
                     "med_excess": np.median(vs_spy),
                     "third_moends": third_share_all, "third_riskon": third_share_riskon})
        # marginal contribution: windows where the third asset was held at any month-end inside
        if name != "NONE":
            sel_w, unsel_w = [], []
            for d in common:
                start = d - pd.DateOffset(months=12)
                inwin = picks[(picks.index > start) & (picks.index <= d)]
                (sel_w if (inwin == third_label).any() else unsel_w).append(res["windows"][d])
            marginal_rows.append({"variant": name,
                                  "n_sel": len(sel_w), "win_sel": np.mean([r > 0 for r in sel_w]) if sel_w else np.nan,
                                  "med_sel": np.median(sel_w) if sel_w else np.nan,
                                  "n_unsel": len(unsel_w), "win_unsel": np.mean([r > 0 for r in unsel_w]) if unsel_w else np.nan,
                                  "med_unsel": np.median(unsel_w) if unsel_w else np.nan})

    # regime medians
    regime_tbl = {}
    for name, res in results.items():
        regime_tbl[name] = {}
        for rname, a, b in REGIMES:
            rr = [res["windows"][d] for d in common if pd.Timestamp(a) <= d <= pd.Timestamp(b)]
            regime_tbl[name][rname] = np.median(rr) if rr else np.nan

    # decisive statistic: GLD vs NONE per window, split at 2024-01-01
    g, n = results["GLD"]["windows"], results["NONE"]["windows"]
    delta = pd.Series({d: g[d] - n[d] for d in common}).sort_index()
    pre, post = delta[delta.index < SPLIT], delta[delta.index >= SPLIT]
    stats = {
        "n": len(delta), "win_all": float((delta > 0).mean()), "med_all": float(delta.median()),
        "n_pre": len(pre), "win_pre": float((pre > 0).mean()), "med_pre": float(pre.median()),
        "n_post": len(post), "win_post": float((post > 0).mean()), "med_post": float(post.median()),
    }
    print("\nGLD vs NONE:", {k: round(v, 4) for k, v in stats.items()})

    # verdict per pre-registered rule
    if stats["win_pre"] <= 0.52 or stats["med_pre"] <= 0.005:
        verdict = "REGIME ARTIFACT"
    elif stats["win_pre"] >= 0.55 and stats["med_pre"] >= 0.015:
        verdict = "STRUCTURAL"
    else:
        verdict = "WEAK / INDETERMINATE"

    # pre/post medians per variant (context for the verdict)
    prepost = {}
    for name, res in results.items():
        w = pd.Series({d: res["windows"][d] for d in common}).sort_index()
        prepost[name] = (w[w.index < SPLIT].median(), w[w.index >= SPLIT].median())

    write_report(rows, marginal_rows, regime_tbl, stats, verdict, delta, prepost, len(common), common)
    print("verdict:", verdict)


def write_report(rows, marginal_rows, regime_tbl, stats, verdict, delta, prepost, n_common, common):
    pc = lambda v: "" if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v:+.1%}"
    p0 = lambda v: "" if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v:.0%}"
    L = ["# Robustness — dual_momentum_gold third-menu-slot (EXP-2026-07-10-defensive-asset)",
         "",
         "Pre-registered: preregistrations/defensive-asset-2026-07-10.md. Frozen framework",
         "(252d lookback, 1.5x winner-take-all risk leg, BIL gate, momentum-picked TLT/BIL",
         f"defensive leg at 1.0x), ONLY the third risk-menu asset varies. panel_2005.parquet,",
         f"rolling 12m windows / quarterly steps; {n_common} common windows",
         f"({common[0].date()} to {common[-1].date()}; BIL data start 2007-05 binds all variants).",
         "All 10 registered variants reported, nothing dropped.",
         "",
         f"## Verdict: **{verdict}**",
         "",
         "## Variant table (common windows)",
         "",
         "| third asset | median 12m | >=18% | >0 | worst | med excess vs SPY | third picked (% month-ends) | (% of risk-on picks) |",
         "|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: -r["med_excess"]):
        L.append(f"| {r['variant']} | {pc(r['median'])} | {p0(r['ge18'])} | {p0(r['pos'])} "
                 f"| {pc(r['worst'])} | {pc(r['med_excess'])} | {p0(r['third_moends'])} | {p0(r['third_riskon'])} |")
    L += ["",
          "## Marginal contribution of the slot",
          "",
          "12m windows split by whether the third asset was actually held at any month-end",
          "inside the window.",
          "",
          "| third asset | n windows w/ 3rd held | win rate | median 12m | n without | win rate | median 12m |",
          "|---|---|---|---|---|---|---|"]
    for m in marginal_rows:
        L.append(f"| {m['variant']} | {m['n_sel']} | {p0(m['win_sel'])} | {pc(m['med_sel'])} "
                 f"| {m['n_unsel']} | {p0(m['win_unsel'])} | {pc(m['med_unsel'])} |")
    L += ["", "## Per-regime medians (12m windows ending in regime)", ""]
    regs = [r[0] for r in REGIMES]
    L.append("| variant | " + " | ".join(regs) + " |")
    L.append("|---|" + "---|" * len(regs))
    for name, rt in regime_tbl.items():
        L.append(f"| {name} | " + " | ".join(pc(rt[r]) for r in regs) + " |")
    L += ["",
          "## Decisive statistic (pre-registered): GLD variant vs NONE ({SPY,QQQ}) per window",
          "",
          "| slice | n windows | GLD wins | median delta (GLD - NONE) |",
          "|---|---|---|---|",
          f"| all | {stats['n']} | {stats['win_all']:.0%} | {stats['med_all']:+.2%} |",
          f"| window ends < 2024-01-01 | {stats['n_pre']} | {stats['win_pre']:.0%} | {stats['med_pre']:+.2%} |",
          f"| window ends >= 2024-01-01 | {stats['n_post']} | {stats['win_post']:.0%} | {stats['med_post']:+.2%} |",
          "",
          "Pre-registered rule: regime artifact if pre-2024 win share <= 52% OR pre-2024",
          "median delta <= +0.5%; structural if >= 55% AND >= +1.5%; else indeterminate.",
          "",
          "## Pre/post-2024 median 12m per variant",
          "",
          "| variant | median 12m, windows ending < 2024 | ending >= 2024 |",
          "|---|---|---|"]
    for name, (a, b) in sorted(prepost.items(), key=lambda kv: -kv[1][0]):
        L.append(f"| {name} | {pc(a)} | {pc(b)} |")
    yearly = delta.groupby(delta.index.year).median()
    L += ["", "## GLD - NONE delta by window-end year (median)", "",
          "| year | median delta | n |", "|---|---|---|"]
    for y, v in yearly.items():
        L.append(f"| {y} | {v:+.2%} | {int((delta.index.year == y).sum())} |")
    (HERE / "robustness" / "defensive_asset.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
