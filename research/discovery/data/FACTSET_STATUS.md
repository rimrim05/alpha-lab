# FactSet REST entitlement probe (HAAS-2415100) — 2026-07-11

*Credential stored in gitignored `.env` (`FACTSET_USERNAME_SERIAL=HAAS-2415100`, `FACTSET_API_KEY`).
REST auth = HTTP Basic (username-serial : api-key). This records what the account can actually reach
so nobody re-probes. The MCP (OAuth) she set up runs only in her interactive session, not here.*

## Result: credential authenticates; bulk-data APIs NOT entitled
| API (REST) | status | meaning |
|---|---|---|
| `/report/entity/v1/structure` (Entity Report Builder) | **200 OK** | ✅ entitled — returns corporate-structure tables |
| `/content/factset-prices/v1/prices` | 403 notAuthorized | ❌ not entitled |
| `/content/factset-fundamentals/v2/...` | 403 notAuthorized | ❌ not entitled |
| `/content/factset-estimates/v2/surprise` | 403 notAuthorized | ❌ not entitled |
| `/report/ownership/v1/holders` | 403 notAuthorized | ❌ not entitled |
| `/report/estimates/v1/...` | base recognized, endpoint name not found by probing | entitlement undetermined |

**Auth is valid** (403s say `haas-2415100 does not have permission…`, not an auth failure). The account
is a Report-Builder-tier academic key: **Entity Report Builder works; the bulk content APIs (Prices,
Fundamentals, Estimates) return 403.**

## Consequence for the two research needs
- **Survivorship price repair** (needs bulk daily OHLCV for ~150 delisted names): FactSet Prices = 403;
  Entity RB has no prices. **FactSet via this account does NOT supply the price panel.** Price track
  stays BLOCKED → Polygon price-tier upgrade, Tiingo, or CRSP.
- **Earnings-IC lane** (needs a forward-collected PIT estimates/surprise panel): Estimates content = 403.
  Even an entitled Estimates Report Builder returns *current-vintage per-entity consensus tables*, which
  the frozen EXP-IC-EARNINGS-FWD prereg **explicitly excludes** (no vendor backfill; PIT only). So
  FactSet does not change the earnings-lane design — the forward collector remains the correct, gated path.

## What the entitled piece (Entity Report Builder) COULD do
`/report/entity/v1/structure` returns entity corporate-structure tables — usable to resolve
successor/predecessor linkage for the repair's 175 unmatched rename/M&A names (e.g. ABX→GOLD), a
complement to the Polygon delist dates. Not prices. Build only if worth it vs a real price source.

## To confirm the full entitlement set (authoritative, not guessed)
Check EITHER the FactSet developer portal (the API catalog shows which APIs this key is subscribed to)
OR the FactSet MCP tool list in an interactive `claude` session (OAuth enumerates the entitled tools).
Probing endpoint names blind is not worth it.
