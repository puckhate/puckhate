# Email

PUCKHATE! sends transactional email to **admins** (the organizers who review
donations).

Today there are two emails, both summaries of the donation approval queue, each
driven by a scheduled management command.

## Templates

Templates live in `backend/templates/emails/`.

- **`admin_base.html`** — the shared base shell for every admin email. It is
  cross-client email markup (table layout, fully inlined styles, Outlook MSO
  conditionals). **Do not** move the styles to an external stylesheet or run a
  CSS bundler over it — email clients strip `<style>`/`<link>`. New admin emails
  should `{% extends "emails/admin_base.html" %}` and override its blocks:
  `preheader`, `eyebrow`, `heading`, `body`, `detail`, `cta`, `help_note`,
  `footer_note`. The call-to-action button renders automatically from the
  `cta_url` / `cta_label` context variables.
- Each email has an HTML template (extending the base) and a plain-text
  `.txt` sibling; both are sent as alternatives of one message.

## Sending

`send_admin_email(subject, template, context, recipients)` in
`backend/api/emails.py` is the single send path. Given an explicit `recipients`
list, it renders the `.html` and `.txt` variants of `emails/<template>` and
sends a multipart message. It returns the number of recipients, and
short-circuits to `0` (no render, no send) when `recipients` is empty.

## The two summary emails

Both are management commands under
`backend/api/management/commands/`, scheduled via the ofelia labels on the
`backend` service in the `docker-compose*.yml` files (the `scheduler` compose
profile must be running — see the README). Both accept `--dry-run` to report
what they would send without sending.

### `hourly_email_summary`

Runs **every hour**. Counts the donations that entered the pending-approval
queue in the past hour (`Donation.pending_count(since=...)`) and emails that
number. If **no** new donations arrived in the window it sends **nothing**, to
avoid an empty hourly message.

### `daily_email_summary`

Runs **once a day**. Reports the **total** number of donations currently
pending review regardless of when they were logged
(`Donation.pending_count()`). If the queue is **empty** it sends **nothing**.

## Adding another admin email

1. Add an HTML template that extends `admin_base.html` and a `.txt` sibling in
   `backend/templates/emails/`.
2. Resolve the recipient list at the call site (e.g.
   `get_donation_review_recipients()`, or a different audience for a different
   email type) and call
   `send_admin_email(subject, "<template-name>", context, recipients)` from
   wherever it is triggered (a command, a signal, a view). Pass `cta_url` in the
   context if you want the button rendered.
