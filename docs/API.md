# API

DRF endpoints under the `api` app, mounted at `/api/`. All are session/CSRF
auth with `AllowAny` permission unless noted.

| Method | Path                  | Name            | Description                     |
| ------ | --------------------- | --------------- | ------------------------------- |
| GET    | `/api/health/`        | `health`        | Liveness probe                  |
| GET    | `/api/stats/`         | `site-stats`    | Public campaign stats           |
| GET    | `/api/exchange-rate/` | `exchange-rate` | Current USD→CAD exchange rate   |
| GET    | `/api/donations/`     | `donations`     | List of verified donations      |
| POST   | `/api/donations/`     | `donations`     | Report a donation (as a draft)  |
| POST   | `/api/receipts/`      | `receipts`      | Upload a proof-of-donation file |
| GET    | `/api/charities/`     | `charities`     | List of approved charities      |

## GET `/api/health/`

```json
{ "status": "ok" }
```

## GET `/api/stats/`

```json
{
  "verified_total": "0.00",
  "verified_count": 0,
  "goals_scored": 0,
  "ca_exchange_rate": "1.0000"
}
```

- `verified_total` — sum of `amount` across verified donations (string; DRF
  serializes `DecimalField` to preserve precision).
- `verified_count` — number of verified donations.
- `goals_scored` — goals scored since campaign start, from the `SiteStats` singleton.
- `ca_exchange_rate` — Canadian dollars per 1 USD, from the `SiteStats`
  singleton.

## GET `/api/exchange-rate/`

The current exchange rate on its own, for clients that need only the rate (the
donation list) without the full stats payload.

```json
{
  "ca_exchange_rate": "1.0000"
}
```

- `ca_exchange_rate` — Canadian dollars per 1 USD (string; `DecimalField`),
  from the `SiteStats` singleton.

## GET `/api/donations/`

All verified donations, most-recently-verified first.

```json
[
  {
    "id": 12,
    "created": "2026-06-04T18:30:00Z",
    "amount": "50.00",
    "name": "Sam R.",
    "charity": "Trevor Project"
  }
]
```

- `created` — when the donation was reported (ISO 8601).
- `amount` — donation amount (string; `DecimalField`, precision preserved).
- `name` — donor's display name, or `"Anonymous"` when left blank.
- `charity` — the attributed charity's name.

No PII (receipt file, verifier) is exposed.

### Query parameters

- `top` — return the top _N_ verified donations by `amount` (descending)
  instead of the full most-recently-verified list. Must be a positive integer.
  Example: `GET /api/donations/?top=3` returns the three largest donations. A
  non-integer or value below `1` responds with `400`:

  ```json
  { "top": ["Must be a positive integer."] }
  ```

## POST `/api/donations/`

Reports a fan donation. Lands as a **draft** (unverified) for an organizer to
review; it does not appear in `GET /api/donations/` or the totals until
approved.

Request (JSON):

```json
{
  "amount": "50.00",
  "currency": "CAD",
  "charity": "Trevor Project",
  "name": "Sam R.",
  "receipt": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6"
}
```

- `amount` — required, must be greater than zero. Interpreted in `currency`.
- `currency` — optional, `"USD"` or `"CAD"` (defaults to `"USD"`). Amounts are
  stored in USD: a `"CAD"` amount is converted using `ca_exchange_rate` from
  `SiteStats` before storage. Not persisted as a field — only the converted USD
  `amount` is kept.
- `charity` — required charity **name**. Matched case-insensitively against
  existing charities; an unknown name creates a new charity as **unapproved**
  (a proposal) for an organizer to vet.
- `name` — optional donor display name; blank shows as `"Anonymous"`.
- `receipt` — claim `token` from `POST /api/receipts/`. Rejected if
  already claimed by another donation.

Response (`201 Created`) echoes the accepted fields (`id`, `amount`, `name`,
`charity` name, `receipt` token); `amount` is the stored USD value. Validation
errors return `400` with per-field messages. This endpoint is rate-limited per
client IP.

Submissions are screened for banned words in the `name`/`charity` fields. A
match is **silently discarded**: the response is still `201 Created` but with an
**empty body**, nothing is persisted, and the submission never reaches the
review queue. This is deliberately indistinguishable from success. See
[MODERATION.md](./MODERATION.md).

## POST `/api/receipts/`

Accepts a single proof-of-donation upload (`multipart/form-data`) and returns
a claim token. The frontend uploads the receipt, while the user finishes the form.
The token is attached to the donation on submit. A receipt that no donation ever claims is
reaped by the orphan-cleanup job.

Request (multipart):

- `file` — image or PDF, ≤ 10 MB. Type is validated by both extension and
  content (leading-byte signature); other types/sizes are rejected.
  Oversized requests are rejected up front with `413`.

Response (`201 Created`):

```json
{
  "token": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
  "created": "2026-06-07T18:30:00Z"
}
```

The file is **write-only**. Receipts are private and
reachable only via the staff-gated `/private-media/` route.

This endpoint is rate-limited per client IP.

## GET `/api/charities/`

All approved charities, alphabetical by name.

```json
[
  {
    "id": 3,
    "name": "Trevor Project",
    "url": "https://www.thetrevorproject.org/"
  }
]
```

- `name` — the charity's display name.
- `url` — the charity's website.
