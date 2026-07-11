# Successor / rename resolution — identifier & corporate-event repair (2026-07-11)

**This is an identifier and corporate-event repair, NOT a price-panel repair.** It produces a NEW
additive candidate file (`rename_candidates.csv`); it does not modify the frozen panel, does not
overwrite the curated `id_map.csv`, does not join predecessor↔successor price series, and does not
assume economic continuity unless a same-security rename is supported. Builder: `resolve_renames.py`.

## Scope & compliance with the authorized restrictions
- Target: the **175** ever-S&P members Polygon left unmatched (identifier gap, not the 207 dated ones).
- **StockAnalysis:** robots checked (`User-agent: * Disallow:` — general access allowed). Not scraped:
  a 3-name probe (AAMRQ, AKS, LEHMQ) returned **404** — its free pages do not serve long-delisted
  names, so it adds nothing here. Left as a documented manual source only.
- Every source kept **separate** in the `sources` column; each inference is labelled.
- Continuity is asserted **only** for same-security renames/share-class; acquisitions, bankruptcies,
  and uncertain cases are `price_continuity_valid = False`/`uncertain` and `manual_review_required = True`.
- SEC has **no delisted-ticker→CIK lookup** (verified: browse-edgar returns an empty page for AKS/ABS/
  AHM), so `old_cik` is generally blank → manual review. `new_cik` is filled only when a curated
  successor ticker is a current SEC ticker.

## Sources (authoritative, local, no scraping)
`curated_id_map` (hand curation, cross-checked not overwritten) · `polygon_reference` (cached delisted
set — name/delisted_utc/composite_figi, matched after conservative normalization: bankruptcy `Q`,
share-class `-A/-B`, warrant `.WS`) · `sec_company_tickers` (current ticker→CIK/name for successors;
ticker-reuse flagged, never assumed).

## Persisted fields (per candidate, in `rename_candidates.csv`)
historical_ticker · proposed_successor_ticker · predecessor_name · successor_name · effective_date ·
event_type (rename / acquisition / bankruptcy / relisting / share-class change / spinoff / uncertain) ·
old_cik · new_cik · figi · sources · confidence · price_continuity_valid · manual_review_required.

## Category counts (of 175)
| category | count |
|---|---|
| safe ticker rename (same continuing security) | **0** |
| share-class change | **9** |
| acquisition (old security terminated) | **0** |
| bankruptcy / liquidation (Q-suffix convention) | **28** |
| relisting / reorganization | **0** |
| **unresolved** (uncertain — needs licensed source or manual) | **138** |
| **total** | 175 |

**62 of 175** got authoritative data (Polygon-normalized name/date/FIGI or curated id_map); **all 175**
are flagged `manual_review_required` (conservative by design — no continuity is assumed). The 0s for
safe-rename / acquisition are honest: those events cannot be confirmed from a bare delisted ticker
without a company name, and the local sources rarely supply one for these old names — hence the large
`unresolved` bucket. This is expected: **free/local data resolves identity for the tractable subset
(bankruptcy Q-tickers, share classes) and flags the rest for a licensed source.**

## Next step (does NOT alter the panel)
The 138 unresolved + the nameless subset need a licensed source with delisted coverage — see
`vendor_diagnostic_15.md` (a 15-security manual test for Capital IQ Pro and GFD/Finaeon). No panel
change is made until provenance and completeness are documented per the authorization.
