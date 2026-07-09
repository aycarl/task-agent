# task-agent

> TODO: one or two sentences on what this project does.

## Stack

- **Backend**: Django 6.0 (Python 3.14), SQLite for local dev — see `backend/`
- **Frontend**: React 19 + TypeScript + Vite — see `frontend/`

The two are not yet wired together (no API routes exposed, no frontend HTTP client configured). See [docs/architecture.md](docs/architecture.md) for the current state.

## Quickstart

```bash
# backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Full setup notes: [docs/setup.md](docs/setup.md).

## Documentation

- [docs/architecture.md](docs/architecture.md) — how the pieces fit together (and don't, yet)
- [docs/setup.md](docs/setup.md) — local development setup
- [docs/api.md](docs/api.md) — API endpoints

## Project layout

```
backend/    Django project (config/) + agent_api app
frontend/   Vite + React + TypeScript app
docs/       Project-level documentation
```
