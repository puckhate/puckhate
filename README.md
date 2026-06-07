# puckcurl

Full-stack monorepo:

- **`frontend/`** — React 19 + Vite + TypeScript + Tailwind 4 + react-router 7
- **`backend/`** — Django + Django REST Framework + MySQL, managed with [uv](https://docs.astral.sh/uv/)

## Architecture

In **production** the app is served from a **single origin** by Django:

| Path            | Served by                                          |
| --------------- | -------------------------------------------------- |
| `/api/...`      | DRF (the `api` app)                                |
| `/admin/...`    | Django admin                                       |
| `/static/...`   | WhiteNoise (hashed Vite assets + admin/DRF static) |
| everything else | the SPA's `index.html` → react-router takes over   |

The Vite build emits into `backend/spa/` (with `base=/static/`), Django's
`collectstatic` gathers it into `STATIC_ROOT`, and WhiteNoise serves it. A
catch-all Django route returns `index.html` so client-side routes resolve.

In **development** the Vite dev server (with HMR) serves the SPA at `:5173` and
proxies `/api` → Django at `:8000`.

## Development (Docker, with HMR)

```bash
cp .env.example .env
docker compose up --build
```

- Frontend (Vite, HMR): http://localhost:5173
- Backend API: http://localhost:8000/api/health/
- MySQL: localhost:3306

Run migrations once the DB is up:

```bash
docker compose run --rm backend uv run python manage.py migrate
```

## Production

The frontend image's `builder` stage emits the SPA; the backend `app` stage
pulls those assets in (as a named build context), runs `collectstatic`, and
serves everything via gunicorn + WhiteNoise on port 8000:

```bash
# 1. Build the SPA (emits the assets into the image at /backend/spa)
docker build ./frontend --target builder -t puckcurl-spa

# 2. Build the backend, pulling the built SPA from the image above
docker build ./backend --target app \
  --build-context frontend=docker-image://puckcurl-spa \
  -t puckcurl

# 3. Run it (point at a reachable MySQL via env)
docker run --rm -p 8000:8000 \
  -e DJANGO_SECRET_KEY=... \
  -e DJANGO_ALLOWED_HOSTS=your.host \
  -e DB_DEFAULT_HOST=... -e DB_DEFAULT_NAME=... \
  -e DB_DEFAULT_USER=... -e DB_DEFAULT_PASSWORD=... \
  puckcurl
```

Now `/`, `/api`, and `/admin` are all served on `:8000`. The backend image's
default (`backend`) stage is the dev image (`runserver`); the `app` stage adds
the SPA + `collectstatic` + gunicorn for production.

## Local development (without Docker)

### Frontend

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173, proxies /api to :8000
npm run build        # emits ../backend/spa for Django to serve
```

### Backend

`mysqlclient` needs the MySQL client libraries to build locally. On macOS:
`brew install mysql-client pkg-config` (and put it on `PKG_CONFIG_PATH`). Then:

```bash
cd backend
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

Configuration is read from environment variables — see `.env.example`.
