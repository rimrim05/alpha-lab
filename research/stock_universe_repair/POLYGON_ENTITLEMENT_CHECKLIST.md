# Polygon entitlement checklist — verify BEFORE any upgrade recommendation

*Per authorization: do NOT recommend a Polygon upgrade until the official plan entitlement is verified
for the items below. This file records what was confirmed from the live API and what still requires
checking the Polygon account/pricing page. **No upgrade is recommended here.***

| item to verify | status from live API probe (current plan) | still to verify (account/pricing page) |
|---|---|---|
| historical **daily aggregates** | ❌ **NOT available** — `/v2/aggs` returns 403 NOT_AUTHORIZED (even recent AAPL 2024) | which paid tier turns daily aggregates on |
| **inactive / delisted** securities | ✅ available — `/v3/reference/tickers?active=false` returns delisted names + `delisted_utc` + `composite_figi` | whether delisted PRICE bars are included at the target tier |
| required **history depth** | unknown on current plan (no aggregates at all) | exact years by tier (Starter ≈ 2y, Developer/Advanced ≈ 5–15y+) — confirm the tier that covers the panel's 2005+ span |
| **adjusted & unadjusted** values | unverifiable (aggregates blocked); `/v2/aggs` supports an `adjusted` param when entitled | confirm both adjusted and raw are served at the target tier |
| **splits, dividends, ticker changes** | ✅ splits + dividends return 200; delisting dates present; explicit rename/ticker-change events endpoint returned 404 on this plan | confirm corporate-action + ticker-event completeness at the target tier |
| **API download limits** | current plan ~5 req/min (free/reference behaviour; hit rate-limit backoffs) | requests/min and bulk/flat-file limits at the target tier |
| **academic / student pricing** | not confirmable via API | the shinathan repo cites a 20% student discount — confirm current student/academic pricing on Polygon |

## Bottom line
The **only** thing blocking the price panel is that this plan serves no aggregates. Whether Polygon is
the right upgrade depends on confirming the rows above: especially **history depth vs the 2005+ span**
and that **delisted names' price bars** are included at whatever tier is chosen. Until those are
verified against Polygon's official plan documentation, no upgrade is recommended; evaluate it head-to-head
with the Capital IQ Pro / GFD diagnostic (`vendor_diagnostic_15.md`).
