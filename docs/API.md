# API

DRF endpoints under the `api` app, mounted at `/api/`. All are session/CSRF
auth with `AllowAny` permission unless noted.

| Method | Path              | Name         | Description                     |
| ------ | ----------------- | ------------ | ------------------------------- |
| GET    | `/api/health/`    | `health`     | Liveness probe                  |
| GET    | `/api/stats/`     | `site-stats` | Public campaign stats           |
| GET    | `/api/donations/` | `donations`  | List of verified donations      |
| POST   | `/api/donations/` | `donations`  | Report a donation (as a draft)  |
| POST   | `/api/receipts/`  | `receipts`   | Upload a proof-of-donation file |
| GET    | `/api/charities/` | `charities`  | List of approved charities      |

## GET `/api/health`

```json
{ "status": "ok" }
```

## GET `/api/stats/`

```json
{
  "verified_total": "0.00",
  "verified_count": 0,
  "goals_scored": 0
}
```

- `verified_total` — sum of `amount` across verified donations (string; DRF
  serializes `DecimalField` to preserve precision).
- `verified_count` — number of verified donations.
- `goals_scored` — from the hand-maintained `SiteStats` singleton.

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

## POST `/api/receipts/`

Accepts a single proof-of-donation upload (`multipart/form-data`) and returns
its id. The frontend uploads the receipt as soon as it's dropped — while the
user finishes the form — then attaches the returned `id` to the donation on
submit. A receipt that no donation ever claims is reaped by the orphan-cleanup
job.

Request (multipart):

- `file` — image or PDF, ≤ 10 MB. Other types/sizes are rejected (mirrors the
  dropzone limits).

Response (`201 Created`):

```json
{
  "id": 7,
  "created": "2026-06-07T18:30:00Z"
}
```

The file is **write-only** — it is never echoed back. Receipts are private and
reachable only via the staff-gated `/private-media/` route.

## POST `/api/donations/`

Reports a fan donation. Lands as a **draft** (unverified) for an organizer to
review; it does not appear in `GET /api/donations/` or the totals until
approved.

Request (JSON):

```json
{
  "amount": "50.00",
  "charity": "Trevor Project",
  "name": "Sam R.",
  "receipt": 7
}
```

- `amount` — required, must be greater than zero.
- `charity` — required charity **name**. Matched case-insensitively against
  existing charities; an unknown name creates a new charity as **unapproved**
  (a proposal) for an organizer to vet.
- `name` — optional donor display name; blank shows as `"Anonymous"`.
- `receipt` — optional id from `POST /api/receipts/`. Rejected if already
  claimed by another donation.

Response (`201 Created`) echoes the accepted fields (`id`, `amount`, `name`,
`charity` name, `receipt`). Validation errors return `400` with per-field
messages.

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
