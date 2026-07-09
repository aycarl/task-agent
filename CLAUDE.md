# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A task submitted through the frontend is passed to an `AgentController` (backend), which selects and runs a `Tool` (calculator, text processing, mock weather), then returns the final result plus a structured, timestamped execution trace. The frontend lets a user submit a task, view its result, browse past-task history, and inspect the trace for any task. Both stacks are fully implemented and wired together; the docs describe the as-built system.

## Commands

### Backend (`backend/`)

```bash
python3 -m venv .venv && source .venv/bin/activate   # first time only
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver          # http://127.0.0.1:8000/ — Swagger UI at /, API under /api/
pytest                              # run tests (NOT `manage.py test` — the suite uses pytest fixtures)
pytest agent_api/tests/test_api.py::test_create_task_returns_201_with_steps   # single test
```

### Frontend (`frontend/`)

```bash
npm install
npm run dev        # http://localhost:5173/, Vite dev server (expects backend on :8000)
npm run build      # tsc -b type-check, then vite build
npm run lint       # oxlint
npm run preview    # preview a production build
```

No frontend test runner is configured.

### Both stacks at once

```bash
docker compose up   # backend :8000 (auto-migrate, admin/admin1234 superuser), frontend :5173
```

## Architecture

**Request flow**: frontend `src/api.ts` → `POST /api/tasks/` → `TaskViewSet.perform_create` → `AgentController.run(prompt)` → prompt split on `" and "`, router picks the first `Tool` whose `can_handle(sub_prompt)` matches → tool executes → each step is persisted as an `ExecutionStep` row → `Task` + its `steps` are serialized back → frontend renders `ResultPanel` (final output) and `ExecutionTrace` (step-by-step log). Guides: `backend/README.md`, `frontend/README.md`.

**Backend** is a single Django app, `agent_api` (deliberately not split into multiple apps — three tools and three endpoints don't warrant it). Key pieces: `models.py` (`Task`, `ExecutionStep`), `tools.py` (`BaseTool` ABC + `CalculatorTool`/`TextProcessorTool`/`WeatherMockTool`), `agent.py` (`AgentController` — the routing/execution loop), `serializers.py`/`views.py`/`urls.py` (a `TaskViewSet` built from list/create/retrieve mixins behind a `DefaultRouter` — update/destroy verbs don't exist; no `/api/steps/` endpoint). Swagger UI is served at `/` from an auto-generated schema at `/api/openapi.json`. SQLite is the persistence layer; CORS is configured for the Vite dev origin.

**Frontend** is TypeScript: four focused components (`TaskInput`, `ResultPanel`, `ExecutionTrace`, `TaskHistory`) wired from `App.tsx` with plain `useState`/`useEffect` — no state library, no chat-style UI (the flow is submit → result → history → trace inspection, not conversational). `src/api.ts` holds the fetch wrappers (hardcoded `http://localhost:8000/api` base URL) plus a dormant mock backend behind `USE_MOCK = false`.

**Key design decisions** (full rationale in `docs/architecture.md`):
- The agent is a **rule-based classifier**, not a real LLM call — tool selection is a simple ordered list (`_select_tool`), first `can_handle` match wins, behind a swappable interface so a real LLM router could later replace it without touching callers.
- **Multi-step reasoning** is done by splitting the prompt on `" and "` and running each sub-prompt through the same router/tool loop — not a real planning system.
- **`CalculatorTool` evaluates via a whitelisted AST walk** (`ast.parse` + BinOp/UnaryOp/Constant only) — never `eval`.
- No dynamic tool plugin/registry, no auth/RBAC, no real-time streaming — see the "Explicitly out of scope" table in `docs/architecture.md` for what was deliberately cut and why.

**Adding a tool**: subclass `BaseTool` in `agent_api/tools.py`, append an instance to `AgentController.tools` in `agent.py` (order matters — first match wins), add tests. Nothing else changes.

**Docs map** — `docs/api.md` is the single source of truth for the API request/response contract; `backend/README.md` and `frontend/README.md` are per-stack implementation guides that reference it rather than restating shapes. When changing the contract, update `docs/api.md` first, then whichever stack guide is affected. `docs/architecture.md` holds project-scope decisions that aren't backend- or frontend-specific (system overview, what's in/out of scope and why). `docs/setup.md` is local dev setup (native and Docker Compose). Root `README.md` carries run instructions plus the assignment-facing sections (assumptions/tradeoffs, time spent, future improvements).
