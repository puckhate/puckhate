# puckcurl backend

Django + Django REST Framework + MySQL, managed with [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

Configuration is read from environment variables (see the repo-root `.env.example`).
