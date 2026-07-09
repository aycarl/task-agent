# task-agent

A task submitted through the UI is passed to an `AgentController`, which selects and runs a `Tool` (calculator, text processing, mock weather), then returns the result plus a structured execution trace.

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

- [docs/architecture.md](docs/architecture.md) — scope, key decisions, overall build order
- [docs/setup.md](docs/setup.md) — local development setup
- [docs/api.md](docs/api.md) — API contract (request/response shapes)
- [backend/IMPLEMENTATION.md](backend/IMPLEMENTATION.md) — backend build plan
- [frontend/IMPLEMENTATION.md](frontend/IMPLEMENTATION.md) — frontend build plan

## Project layout

```
backend/    Django project (config/) + agent_api app
frontend/   Vite + React + TypeScript app
docs/       Project-level documentation
```
