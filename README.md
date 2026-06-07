# PUCKCURL!

PUCKCURL! tracks fan-reported charitable donations made as part of a "donate in protest"
campaign in the PWHL: when a particular player scores, fans are encouraged to donate to
trans-supporting charities, and this app records those donations so the campaign's
cumulative impact is publicly visible.

It **records** donations made elsewhere, but it does not accept, process, or facilitate
payments.

See **[docs/OVERVIEW.md](docs/OVERVIEW.md)** for the full picture (including scope and
constraints).

## Documentation

More detail lives in [`docs/`](docs/):

- **[OVERVIEW.md](docs/OVERVIEW.md)** — what the product is, the draft → approve flow, scope and legal constraints
- **[ROADMAP.md](docs/ROADMAP.md)** — what's built vs. planned, and what's out of scope
- **[DESIGN.md](docs/DESIGN.md)** — color palette and typography
- **[API.md](docs/API.md)** — the DRF endpoints under `/api/` and their response shapes

## Disclaimer

PUCKCURL! is an independent, fan-organized initiative. It is not affiliated with,
endorsed by, or sponsored by the Professional Women's Hockey League (PWHL), any of its
teams, or any of its players. Any commentary reflects the opinions of its organizers
only. All trademarks, team names, league names, and player names belong to their
respective owners and are used solely for identification and commentary.

The in-app **Disclaimer** (`frontend/src/views/Disclaimer.tsx`) is the authoritative,
user-facing version.

## Stack

- **`frontend/`** — React 19 + Vite + TypeScript + Tailwind 4 + react-router 7
- **`backend/`** — Django + Django REST Framework + MySQL

## Architecture

In **production** the app is served from a **single origin** by Django:

| Path                 | Served by                                          |
| -------------------- | -------------------------------------------------- |
| `/api/...`           | DRF (the `api` app)                                |
| `/admin/...`         | Django admin                                       |
| `/static/...`        | WhiteNoise (hashed Vite assets + admin/DRF static) |
| `/private-media/...` | Staff-only view (donation receipts; never public)  |
| everything else      | the SPA's `index.html` → react-router takes over   |

The Vite build emits into `backend/spa/` (with `base=/static/`), Django's
`collectstatic` gathers it into `STATIC_ROOT`, and WhiteNoise serves it. Any path that
no backend route claims is served `index.html` by `SPAFallbackMiddleware` so client-side
routes resolve.

In **development** the Vite dev server (with HMR) serves the SPA at `:5173` and proxies
`/api` → Django at `:8000`.

## Development (Docker, with HMR)

```bash
cp .env.example .env
docker compose up --build
docker compose run --rm backend uv run python manage.py migrate
```

- Frontend (Vite, HMR): http://localhost:5173
- Backend API: http://localhost:8000/api/health/
- MySQL: localhost:3306

Configuration is read from environment variables — see `.env.example`.

## Django operations

Run Django management commands against the local environment. Two equivalent forms:
prefix with `docker compose run --rm backend` (uses the Dockerized backend + MySQL), or
run from `cd backend` directly once you've `uv sync`'d and have MySQL reachable.

```bash
# Create migrations from model changes (api app)
docker compose run --rm backend uv run python manage.py makemigrations

# Apply migrations to the database
docker compose run --rm backend uv run python manage.py migrate

# Create an admin/organizer login for the Django admin (interactive)
docker compose run --rm backend uv run python manage.py createsuperuser

# Run any management command (e.g. shell, dbshell, collectstatic)
docker compose run --rm backend uv run python manage.py <command> [args]
```

The created superuser can sign in at http://localhost:8000/admin/ to review and approve
donation drafts.

## Production

Two images compose via a named build context: the frontend `builder` stage emits the
SPA, then the backend `app` stage pulls it in, runs `collectstatic`, and serves
everything via gunicorn + WhiteNoise on `:8000`.

```bash
docker build ./frontend --target builder -t puckcurl-spa
docker build ./backend  --target app \
  --build-context frontend=docker-image://puckcurl-spa \
  -t puckcurl

docker run --rm -p 8000:8000 \
  -e DJANGO_SECRET_KEY=... \
  -e DJANGO_ALLOWED_HOSTS=your.host \
  -e DB_DEFAULT_HOST=... -e DB_DEFAULT_NAME=... \
  -e DB_DEFAULT_USER=... -e DB_DEFAULT_PASSWORD=... \
  puckcurl
```

`/`, `/api`, and `/admin` are then all served on `:8000`. (The backend image's default
`backend` stage is the dev image that runs `runserver`.)
