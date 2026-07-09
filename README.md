# task-agent

A task submitted through the UI is passed to an `AgentController`, which selects and runs a `Tool` (calculator, text processing, mock weather), then returns the result plus a structured execution trace. The UI shows the result, past-task history, and the step-by-step trace for any task.

## Stack

- **Backend**: Django 6.0 + Django REST Framework (Python 3.14), SQLite for local dev — see `backend/`
- **Frontend**: React 19 + TypeScript + Vite — see `frontend/`

## How to run the backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Runs at `http://127.0.0.1:8000/` — the homepage serves Swagger UI plus a listing of the available tools. The API lives under `/api/tasks/` (contract in [docs/api.md](docs/api.md)).

Tests:

```bash
cd backend
pytest
```

## How to run the frontend

```bash
cd frontend
npm install
npm run dev
```

Runs at `http://localhost:5173/` and expects the backend on `http://localhost:8000` (base URL in `frontend/src/api.ts`). `npm run build` type-checks then builds; `npm run lint` runs Oxlint.

**One-command alternative** — run both stacks with Docker:

```bash
docker compose up
```

Backend on `:8000` (auto-migrates, creates an `admin`/`admin1234` superuser), frontend on `:5173`.

## Dependencies

**Backend** (`backend/requirements.txt`): Django 6.0, Django REST Framework, django-cors-headers, pytest + pytest-django, and inflection/uritemplate for OpenAPI schema generation. Requires Python 3.14. Storage is SQLite — no database server needed.

**Frontend** (`frontend/package.json`): React 19, TypeScript, Vite, Oxlint. Requires Node 20+ (the Docker setup uses Node 22).

## Assumptions and tradeoffs

Full rationale in [docs/architecture.md](docs/architecture.md); the short version:

- **The agent is a rule-based router, not a real LLM call.** All three tools are deterministic, so a live LLM would add an API key, latency, and non-determinism for no benefit at this scale. Tool selection sits behind a swappable interface (`backend/agent_api/agent.py`), so an LLM router could replace it without touching callers.
- **Multi-step prompts are handled by splitting on `" and "`** and running each part through the same router — it demonstrates chaining tools without pretending to be a planner.
- **No auth/RBAC, no real-time streaming, no tool plugin registry** — deliberately cut as scope creep for three tools and three endpoints.
- **Dev-only settings**: SQLite, `DEBUG = True`, a checked-in `SECRET_KEY`. Nothing here is production-safe as-is.
- **The frontend hardcodes the backend URL** and relies on CORS (`django-cors-headers`) rather than a Vite dev proxy — one less moving part for local dev.

## Time spent

~6–8 hours over one day.

## What I'd improve with more time

- Swap the rule-based router for real LLM tool selection at the existing `select_tool` seam.
- A real planning loop for multi-step prompts instead of `" and "` splitting.
- A frontend test runner (Vitest) with component tests — currently only the backend has tests.
- Streaming trace updates (SSE) so the execution trace renders live instead of after completion.
- Production-ready settings driven by environment variables (secret key, debug, allowed hosts, CORS origins).
- Pin toolchain versions (`.nvmrc`, `requires-python`).

## Documentation

- [docs/architecture.md](docs/architecture.md) — scope, key decisions, overall build order
- [docs/setup.md](docs/setup.md) — local development setup
- [docs/api.md](docs/api.md) — API contract (request/response shapes)
- [backend/README.md](backend/README.md) — backend implementation guide (request lifecycle, code map, adding a tool)
- [frontend/README.md](frontend/README.md) — frontend implementation guide (data flow, code map)

## Project layout

```
backend/    Django project (config/) + agent_api app
frontend/   Vite + React + TypeScript app
docs/       Project-level documentation
```
