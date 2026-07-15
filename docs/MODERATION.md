# Moderation

Every donation on PUCKHATE! is **fan-reported**, so nothing reaches the public
totals until a human organizer has vetted it. This doc describes the path a
submission takes from intake to approval, and the automated banned-word screen
that sits in front of the human queue.

## Moderation flow

```
Submission                 POST /api/donations/
    │
    ▼
Banned-word check          automatic, silent
    │
    ├─► match ────────────► silently discarded (nothing stored, never queued)
    │
    ▼
Human moderation queue     Django admin, unverified drafts
    │
    ▼
Approval                   rolls into the public totals
```

1. **Submission.** POST to `POST /api/donations/` (see
   [API.md](./API.md)). The donation is stored as a **draft** — a `Donation`
   row with `verified = NULL`. An unrecognized charity name creates a new
   `Charity` as **unapproved** (to be vetted separately).
2. **Banned-word check.** Before anything is persisted, the intake serializer
   screens the `name` and `charity` fields against a banned-word list. On a
   match the submission is **silently discarded** and never enters the queue
   (see [below](#banned-word-screening)).
3. **Human moderation queue.** Surviving drafts wait in the Django admin for an
   organizer. Drafts are not public — they are excluded from
   `GET /api/donations/` and from every total until approved. Organizers are
   nudged by the pending-review summary emails (see [EMAIL.md](./EMAIL.md)).
4. **Approval.** An organizer reviews the receipt and either **approves**
   (the donation becomes verified and rolls into the public totals) or
   **rejects** (the draft is deleted).

## Banned words

The banned words list for the second step banned-word check is located at `backend/api/banned_words.json`.
It is formatted as a JSON list of string, and kept encrypted with git-secret to avoid exposing it in plaintext.

```json
["gambling", "drugs", "politics", "guns"]
```

## Charity moderation

A donation may name a charity that doesn't exist yet; intake creates it with
`approved = False`. Approving the _donation_ does **not** approve the _charity_ —
that is a separate step at **Admin → Charities** (the **"Approve selected
charities"** action). `GET /api/charities/` and the log-donation typeahead only
list approved charities. Unapproved charities left with no donations are removed
by the nightly `cleanup_orphan_charities` job.

## Related docs

- [OVERVIEW.md](./OVERVIEW.md) — the product and its approval-based model
- [API.md](./API.md) — the intake endpoints (`/api/donations/`, `/api/receipts/`)
- [EMAIL.md](./EMAIL.md) — the pending-review summary emails that notify organizers
