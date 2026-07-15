# Project Overview

## What this is

**PUCKHATE!** tracks fan-reported charitable donations made as part of a "donate in
protest" campaign in the PWHL.

The campaign responds to a particular PWHL player whose public views many fans regard
as transphobic. Historically fans have booed this player. This project channels that
energy into something constructive instead: when that player scores, fans are
encouraged to donate to trans-supporting charities. PUCKHATE! records those donations so
the cumulative impact of the campaign is publicly visible.

## What it does

- Fans **self-report** donations they've already made, including a receipt.
- Reported donations are stored as **drafts**. Submissions containing a banned word
  are silently discarded before they are stored (see [MODERATION.md](./MODERATION.md)).
- An **organizer** (a staff user with a login to the Django backend/admin) reviews each
  draft and, if it looks legitimate based on the receipt details, **approves** it.
- Approved donations roll up into the **public totals** shown on the site (amount
  raised, number of donors, goals/scores answered).

See [MODERATION.md](./MODERATION.md) for the full submission → screening → queue →
approval flow.

## What it explicitly does not do

- It does **not** accept, process, or facilitate donations. PUCKHATE! is a **record** of
  donations made elsewhere — it is not a charity, a fundraising platform, or a payment
  processor. This is out of scope by design.

## Constraints

- **No copyrighted material.** Do not use PWHL or team logos, marks, or other
  copyrighted/branded assets anywhere in the app. This is a fan project and must avoid
  creating legal liability for the league, teams, or the player.
- **Only publicly verifiable claims.** Any statement about a person — especially the
  player — must be grounded in publicly documented, verifiable sources (e.g. their own
  public statements or reputable reporting), and framed as opinion/commentary on those
  facts, not as new assertions of fact. This is what keeps the project protected speech;
  unverifiable or embellished claims expose us to libel or harassment accusations. When
  in doubt, leave it out.

## Status

The MVP described above is the target but **not yet fully built** — see
[ROADMAP.md](./ROADMAP.md) for what's implemented vs. planned.

## Related docs

- [MODERATION.md](./MODERATION.md) — submission screening, the review queue, and approval
- [DESIGN.md](./DESIGN.md) — palette and typography
- [ROADMAP.md](./ROADMAP.md) — implementation status and future work
