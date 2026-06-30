# Currency (USD / CAD)

PUCKHATE! operates in the US and Canada. Donations can be reported in USD or
CAD, are always stored in USD, and are displayed in the viewer's local
currency.

The rate is always expressed as Canadian dollars per 1 USD (e.g. `1.3700`
means 1 USD = 1.37 CAD). It lives on the `SiteStats` singleton as
`ca_exchange_rate`.

It is refreshed automatically by the `update_exchange_rate` management command,
which fetches USD to CAD from CurrencyLayer (`backend/libraries/currencylayer/`).

## 1. Reporting

- The donation form picks the currency from the viewer's locale
  (`getLocaleCurrency`, `frontend/src/utils/currency.ts`): a Canadian locale gives `CAD`,
  everything else `USD`.
- On submit, `POST /api/donations/` includes a `currency` field
  (`"USD"` | `"CAD"`, optional, defaults to `"USD"`). See [API.md](./API.md).

## 2. Storage

Every stored amount is USD.

- For a `CAD` donation, converts to USD before saving.
- For a `USD` report, stores the amount unchanged.
- Records the rate that was applied on the donation as `effective_exchange_rate`

## 3. Display

- The current rate is exposed two ways: inside `GET /api/stats/` (next to the
  totals) and via a dedicated lightweight `GET /api/exchange-rate/`.
- `ExchangeRateProvider` (`frontend/src/providers/ExchangeRateProvider.tsx`)
  shares the rate across views so each page doesn't refetch it:
  - the home page populates it from its existing `/api/stats/` call (`setRate`);
  - a page reached directly (e.g. the donations list) calls `ensureRate()`,
    which fetches `/api/exchange-rate/` only if the rate isn't known yet.
- `convertFromUSD(usd, ca_exchange_rate)` returns the USD value unchanged for US
  viewers, or `usd * ca_exchange_rate` for Canadian viewers.

So a US viewer sees stored USD values as-is; a Canadian viewer sees the same
values converted to CAD at the current rate.
