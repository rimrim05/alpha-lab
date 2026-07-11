"""Successor / rename resolution for the 175 ever-S&P members Polygon left unmatched.

IDENTIFIER + CORPORATE-EVENT REPAIR ONLY — NOT a price-panel repair. It builds a NEW additive
CANDIDATE file (`rename_candidates.csv`); it never edits the frozen panel or the curated `id_map.csv`
(cross-checked, not overwritten). It does NOT join predecessor↔successor price series and does NOT
assume economic continuity unless a same-security rename is supported (per authorization restrictions).

Sources (each kept separate in the `sources` field; robots for StockAnalysis checked = general
access allowed, but it is used only as a documented MANUAL cross-check, not scraped here):
  - curated_id_map        : research/stock_universe_repair/id_map.csv (authoritative hand curation)
  - polygon_reference     : the cached delisted-ticker set (name / delisted_utc / composite_figi),
                            matched after conservative normalization (bankruptcy 'Q', share-class, warrant)
  - sec_company_tickers   : SEC current ticker→CIK/name (successor CIK; reuse flagged, not assumed)
NOTE: SEC offers no delisted-ticker→CIK lookup, so `old_cik` is usually blank → manual review.

Run: .venv/bin/python research/stock_universe_repair/resolve_renames.py
"""
from __future__ import annotations
import json
import urllib.request
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = HERE / "polygon_raw"
UA = {"User-Agent": "alpha-lab research (kris10harim@gmail.com)"}


def load_polygon_delisted() -> dict:
    """ticker -> {name, delisted_utc, composite_figi} from the cached reference pull."""
    out = {}
    for p in sorted(RAW.glob("delisted_*.json")):
        for r in json.loads(p.read_text()).get("results", []):
            out[r.get("ticker")] = {"name": r.get("name"), "delisted_utc": (r.get("delisted_utc") or "")[:10],
                                    "figi": r.get("composite_figi")}
    return out


def sec_current_tickers() -> dict:
    """current TICKER -> (cik, name) from SEC (cached)."""
    cache = HERE / "sec_company_tickers.json"
    if cache.exists():
        data = json.loads(cache.read_text())
    else:
        data = json.loads(urllib.request.urlopen(
            urllib.request.Request("https://www.sec.gov/files/company_tickers.json", headers=UA)).read())
        cache.write_text(json.dumps(data))
    return {v["ticker"]: (v["cik_str"], v["title"]) for v in data.values()}


def normalize_variants(t: str) -> list[str]:
    """Conservative ticker variants to probe against the Polygon delisted set."""
    v = {t}
    if len(t) > 1 and t.endswith("Q"):
        v.add(t[:-1])                 # bankruptcy Q-suffix: AAMRQ -> AAMR
    for sep in (".", "-"):
        if sep in t:
            v.add(t.split(sep)[0])    # share-class / warrant base: AFS-A -> AFS
    v.add(t.replace("-", "."))        # dash<->dot share-class form
    return [x for x in v if x]


def classify_event(t: str, id_action: str | None) -> str:
    if id_action:
        return {"rename": "rename", "acquire": "acquisition", "merge": "acquisition",
                "delist": "uncertain", "spinoff": "spinoff"}.get(id_action, id_action)
    if len(t) > 1 and t.endswith("Q"):
        return "bankruptcy"           # Chapter-11 Q-suffix convention
    if any(s in t for s in (".WS", ".WT", ".U", "+")):
        return "share-class change"   # warrant/unit
    if any(t.endswith(sfx) for sfx in ("-A", "-B", ".A", ".B", "-P")):
        return "share-class change"
    return "uncertain"


def continuity(event: str) -> object:
    return {"rename": True, "share-class change": True,
            "acquisition": False, "bankruptcy": False, "relisting": "uncertain",
            "spinoff": False}.get(event, "uncertain")


def build():
    dm = pd.read_csv(HERE / "delisting_map.csv")
    unmatched = dm[~dm["polygon_found"]]["ticker"].tolist()          # the 175
    idmap = pd.read_csv(HERE / "id_map.csv").set_index("old_ticker")
    poly = load_polygon_delisted()
    cur = sec_current_tickers()

    rows = []
    for t in unmatched:
        src, succ, eff, pred_name, succ_name = [], None, None, None, None
        old_cik = new_cik = figi = None
        id_action = None
        # 1) curated id_map (authoritative; cross-check, never overwrite)
        if t in idmap.index:
            r = idmap.loc[t]
            id_action = str(r.get("action")) if pd.notna(r.get("action")) else None
            succ = r.get("successor_ticker") if pd.notna(r.get("successor_ticker")) else None
            eff = str(r.get("effective_date"))[:10] if pd.notna(r.get("effective_date")) else None
            pred_name = str(r.get("note")) if pd.notna(r.get("note")) else None
            src.append("curated_id_map")
        # 2) polygon reference via conservative normalization
        for v in normalize_variants(t):
            if v in poly:
                pred_name = pred_name or poly[v]["name"]
                eff = eff or (poly[v]["delisted_utc"] or None)
                figi = figi or poly[v]["figi"]
                src.append(f"polygon_reference:{v}")
                break
        # 3) SEC current-ticker map — successor CIK if successor is a current ticker; flag reuse
        if succ and succ in cur:
            new_cik, succ_name = f"{cur[succ][0]:010d}", cur[succ][1]
            src.append("sec_company_tickers:successor")
        if t in cur:                      # historical ticker is a CURRENT ticker -> possible reuse/rename
            src.append("sec_company_tickers:ticker-active(reuse?)")

        event = classify_event(t, id_action)
        cont = continuity(event)
        high = "curated_id_map" in src and event in ("rename", "share-class change")
        conf = "high" if high else ("medium" if ("curated_id_map" in src or any("polygon" in s for s in src)) else "low")
        manual = not (high and succ)      # anything not a clean curated same-security rename needs review
        rows.append({
            "historical_ticker": t, "proposed_successor_ticker": succ,
            "predecessor_name": pred_name, "successor_name": succ_name,
            "effective_date": eff, "event_type": event,
            "old_cik": old_cik, "new_cik": new_cik, "figi": figi,
            "sources": ";".join(src) if src else "none",
            "confidence": conf if src else "uncertain",
            "price_continuity_valid": cont, "manual_review_required": bool(manual),
        })
    out = pd.DataFrame(rows)
    out.to_csv(HERE / "rename_candidates.csv", index=False)
    return out


CATEGORIES = {
    "safe_rename_same_security": lambda r: r["event_type"] == "rename" and r["price_continuity_valid"] is True,
    "share_class_change": lambda r: r["event_type"] == "share-class change",
    "acquisition_old_terminated": lambda r: r["event_type"] == "acquisition",
    "bankruptcy_liquidation": lambda r: r["event_type"] == "bankruptcy",
    "relisting_reorg": lambda r: r["event_type"] in ("relisting", "spinoff"),
    "unresolved": lambda r: r["event_type"] == "uncertain",
}

if __name__ == "__main__":
    df = build()
    print(f"unmatched names processed: {len(df)}")
    print(f"any source found: {(df['sources'] != 'none').sum()} | manual_review_required: {df['manual_review_required'].sum()}")
    print("\ncategory counts:")
    counted = pd.Series(0, index=list(CATEGORIES))
    for _, r in df.iterrows():
        for name, fn in CATEGORIES.items():
            if fn(r):
                counted[name] += 1
                break
    for k, v in counted.items():
        print(f"  {k:28s} {v}")
    print(f"  {'TOTAL':28s} {counted.sum()}")
    # self-check: a known curated rename resolves as continuous same-security
    abc = df[df["historical_ticker"] == "ABC"]
    if not abc.empty:
        assert abc.iloc[0]["price_continuity_valid"] is True, abc.to_dict("records")
        print("\nself-check OK: ABC (AmerisourceBergen->Cencora) = rename, continuity valid")
    print("wrote rename_candidates.csv")
