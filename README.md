# PUCKCURL!

PUCKCURL! tracks fan-reported charitable donations made as part of a "donate in protest"
campaign in the PWHL: when a particular player scores, fans are encouraged to donate to
trans-supporting charities, and this app records those donations so the campaign's
cumulative impact is publicly visible.

This app records donations made elsewhere, but it does not accept, process, or facilitate
payments itself.

See **[OVERVIEW.md](docs/OVERVIEW.md)** for the full picture (including scope and
constraints).

## Documentation

More detail lives in [`docs/`](docs/):

- **[OVERVIEW.md](docs/OVERVIEW.md)** — what the product is, the approval flow, scope and legal constraints
- **[ROADMAP.md](docs/ROADMAP.md)** — what's planned, and what's out of scope
- **[DESIGN.md](docs/DESIGN.md)** — color palette and typography
- **[API.md](docs/API.md)** — the DRF endpoints under `/api/` and their response shapes
- **[CONTRIBUTING.md](docs/CONTRIBUTING.md)** — how to contribute, conventions, and the project's ground rules

## Disclaimer

PUCKCURL! is an independent, fan-organized initiative. It is not affiliated with,
endorsed by, or sponsored by the Professional Women's Hockey League (PWHL), any of its
teams, or any of its players. Any commentary reflects the opinions of its organizers
only. All trademarks, team names, league names, and player names belong to their
respective owners and are used solely for identification and commentary.

The in-app disclaimer (`frontend/src/views/Disclaimer.tsx`) is the authoritative,
user-facing version.

## Stack

- **`frontend/`** — React 19 + Vite + TypeScript + Tailwind 4 + react-router 7
- **`backend/`** — Django + Django REST Framework + MySQL

## Architecture

In production the app is served from a single origin by Django:

| Path                 | Served by                                            |
| -------------------- | ---------------------------------------------------- |
| `/api/...`           | DRF (the `api` app)                                  |
| `/admin/...`         | Django admin                                         |
| `/static/...`        | WhiteNoise (hashed Vite assets + admin/DRF static)   |
| `/private-media/...` | Staff-only view (donation receipts; never public)    |
| everything else      | the frontend's `index.html`(react-router takes over) |

The Vite build emits into `backend/spa/`, Django's
`collectstatic` gathers it into `STATIC_ROOT`, and WhiteNoise serves it. Any path that
no backend route claims is served `index.html` by `SPAFallbackMiddleware` so client-side
routes resolve.

In development the Vite dev server (with HMR) serves the SPA at `:5173` and proxies
`/api` to Django at `:8000`.

## Development (Requires Docker)

### Quick Start:

```bash
cp .env.example .env  # swap out default passwords as needed
docker compose up --build
docker compose run --rm backend uv run python manage.py migrate
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/health/
- Backend admin: http://localhost:8000/admin/
- MySQL: localhost:3306

Configuration is read from the `.env` file, see `docker-compose.yml` for how values are passed to the containers.

### Django operations

You will need to run Django management commands against the local environment for many operations,
such as creating migrations, applying migrations, and creating superusers. A few examples:

```bash
# Create migrations from model changes
docker compose run --rm backend uv run python manage.py makemigrations

# Apply migrations to the local database
docker compose run --rm backend uv run python manage.py migrate

# Create an admin login for the Django admin (interactive)
docker compose run --rm backend uv run python manage.py createsuperuser

# Run any management command (e.g. shell)
docker compose run --rm backend uv run python manage.py <command> [args]

# Run the development server with cron scheduler
docker compose --profile scheduler up
```

The created superuser can sign in at http://localhost:8000/admin/ to review and approve
donation drafts.

## Contributing

Contributions are welcome. Fork this repo, make your change, run the lint/format/type
checks, and open a pull request against `master`.

Because this is a protest project, a few ground rules are non-negotiable: only
publicly verifiable claims, no threats or harassment, and no copyrighted/branded
assets (including PWHL or team logos). See **[CONTRIBUTING.md](docs/CONTRIBUTING.md)**
for the full workflow, conventions, and these rules in detail.
