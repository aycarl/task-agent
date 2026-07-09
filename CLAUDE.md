# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A task submitted through the frontend is passed to an `AgentController` (backend), which selects and runs a `Tool` (calculator, text processing, mock weather), then returns the final result plus a structured, timestamped execution trace. The frontend lets a user submit a task, view its result, browse past-task history, and inspect the trace for any task.

## Current state

Both stacks are scaffolds — the actual implementation described below and in the docs has not been written yet:

- `backend/agent_api/` (models, tools, agent controller, views) is an empty Django app skeleton, and is **not yet registered in `INSTALLED_APPS`** (`backend/config/settings.py`).
- `backend/requirements.txt` only pins `Django==6.0.7`. The planned implementation uses Django REST Framework and pytest/pytest-django (see `backend/IMPLEMENTATION.md`) — neither is installed yet. Add them to `requirements.txt` when implementing.
- `frontend/src/` is still the unmodified Vite + React + TypeScript template — no API client, no components, no dev-server proxy to the backend.
- No test files exist yet on either side (`agent_api/tests.py` is the default Django stub; `frontend/package.json` has no test script or test framework installed).

When orienting in this repo, treat `docs/architecture.md`, `docs/api.md`, `backend/IMPLEMENTATION.md`, and `frontend/IMPLEMENTATION.md` as the plan/spec for what to build, not a description of code that already exists — always check the actual files before assuming something is implemented.

## Commands

### Backend (`backend/`)

```bash
python3 -m venv .venv && source .venv/bin/activate   # first time only
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver          # http://127.0.0.1:8000/
python manage.py test               # run tests (Django's default runner)
python manage.py test agent_api.tests.TestClassName.test_method_name   # single test
```

### Frontend (`frontend/`)

```bash
npm install
npm run dev       # http://localhost:5173/, Vite dev server
npm run build      # tsc -b type-check, then vite build
npm run lint       # oxlint
npm run preview    # preview a production build
```

No frontend test runner is configured yet.

## Architecture

**Request flow**: frontend `api.js` → `POST /api/tasks/` → Django view → `AgentController.run(prompt)` → router picks the first `Tool` whose `can_handle(prompt)` matches → tool executes → each step is persisted as an `ExecutionStep` row → `Task` + its `steps` are serialized back → frontend renders `ResultPanel` (final output) and `ExecutionTrace` (step-by-step log). This full round trip spans multiple files on both sides — see `backend/IMPLEMENTATION.md` and `frontend/IMPLEMENTATION.md` for the concrete code.

**Backend** is a single Django app, `agent_api` (deliberately not split into multiple apps — three tools and three endpoints don't warrant it). Key pieces: `models.py` (`Task`, `ExecutionStep`), `tools.py` (`BaseTool` ABC + `CalculatorTool`/`TextProcessorTool`/`WeatherMockTool`), `agent.py` (`AgentController` — the routing/execution loop), `serializers.py`/`views.py`/`urls.py` (plain DRF `APIView`s, not `ModelViewSet`/routers). SQLite is the persistence layer.

**Frontend** is four focused components (`TaskInput`, `ResultPanel`, `ExecutionTrace`, `TaskHistory`) wired from `App.jsx` with plain `useState`/`useEffect` — no state library, no chat-style UI (the flow is submit → result → history → trace inspection, not conversational).

**Key design decisions** (full rationale in `docs/architecture.md`):
- The agent is a **rule-based classifier**, not a real LLM call — tool selection is a simple ordered list (`_select_tool`), first `can_handle` match wins, behind a swappable interface so a real LLM router could later replace it without touching callers.
- **Multi-step reasoning** is done by splitting the prompt on `" and "` and running each sub-prompt through the same router/tool loop — not a real planning system.
- No dynamic tool plugin/registry, no auth/RBAC, no real-time streaming — see the "Explicitly out of scope" table in `docs/architecture.md` for what was deliberately cut and why.

**Docs map** — `docs/api.md` is the single source of truth for the API request/response contract; `backend/IMPLEMENTATION.md` and `frontend/IMPLEMENTATION.md` reference it rather than restating shapes. When changing the contract, update `docs/api.md` first, then whichever stack-side doc is affected. `docs/architecture.md` holds project-scope decisions that aren't backend- or frontend-specific (what's in/out of scope, why, overall build order). `docs/setup.md` is local dev setup instructions.
