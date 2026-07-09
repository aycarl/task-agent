# Local development setup

## Prerequisites

- Python 3.14 (see `backend/.venv/pyvenv.cfg` for the version this was created with)
- Node.js (version matching `frontend/package.json` devDependencies — no `.nvmrc` pinned yet)

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

Runs at `http://127.0.0.1:8000/`. Only `/admin/` is currently routed (`backend/config/urls.py`).

Settings live in `backend/config/settings.py`. Notable local-dev-only bits: `DEBUG = True`, a checked-in `SECRET_KEY`, `ALLOWED_HOSTS = []`. None of this is production-safe — revisit before deploying anywhere.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs at the Vite default (`http://localhost:5173/`). `npm run build` type-checks (`tsc -b`) then builds; `npm run lint` runs Oxlint.

## Running both

Two terminals, one per stack, as above. There's no dev-server proxy between them yet — see [architecture.md](architecture.md#key-decisions).
