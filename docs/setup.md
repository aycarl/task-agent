# Local development setup

## Prerequisites

- Python 3.14 (see `backend/.venv/pyvenv.cfg` for the version this was created with)
- Node.js 20+ (the Docker setup uses Node 22)
- Or just Docker, if you use the [Compose route](#docker-compose) below

## Backend

```bash
cd backend
python3 -m venv .venv          # skip if .venv already exists
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```

Runs at `http://127.0.0.1:8000/`:

- `/` — Swagger UI plus a listing of the available agent tools
- `/api/tasks/` — the task API ([api.md](api.md))
- `/api/openapi.json` — auto-generated OpenAPI schema
- `/admin/` — Django admin

Tests (pytest + pytest-django — the fixture-based suite needs `pytest`, not `manage.py test`):

```bash
cd backend
pytest
```

Settings live in `backend/config/settings.py`. Notable local-dev-only bits: `DEBUG = True`, a checked-in `SECRET_KEY`, `ALLOWED_HOSTS = []`. None of this is production-safe — revisit before deploying anywhere.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs at the Vite default (`http://localhost:5173/`) and talks to the backend at `http://localhost:8000` (base URL in `frontend/src/api.ts`). There's no dev-server proxy — the backend's CORS config (`CORS_ALLOWED_ORIGINS` in `settings.py`) already allows the Vite origin, so the two just need to be running at their default ports.

`npm run build` type-checks (`tsc -b`) then builds; `npm run lint` runs Oxlint.

## Running both

Two terminals, one per stack, as above — start the backend first so the frontend has something to talk to.

## Docker Compose

One command from the repo root:

```bash
docker compose up
```

- **backend** on `:8000` — installs requirements, runs migrations, creates an `admin`/`admin1234` superuser, then `runserver`
- **frontend** on `:5173` — `npm install` + Vite dev server (Node 22)

Both mount the local source, so edits hot-reload the same as running natively.
