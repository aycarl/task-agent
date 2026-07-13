# task-agent

A task submitted through the UI is passed to an `AgentController`, which selects and runs a `Tool` (calculator, text processing, mock weather, days-since-a-date, current time in a city), then returns the result plus a structured execution trace. The UI shows the result, past-task history, and the step-by-step trace for any task.

**Video demo:**

https://github.com/user-attachments/assets/a7de2594-1c98-4b05-add2-8a164b3d350d



## Tech Stack and Dependencies

### Backend

- **Frameworks**: Django 6.0 + Django REST Framework
- **Runtime**: Python 3.14
- **Database**: SQLite (local development)
- **Python deps** (`backend/requirements.txt`): django-cors-headers, pytest + pytest-django, inflection, uritemplate

### Frontend

- **Framework/UI**: React 19
- **Language**: TypeScript
- **Build tool**: Vite
- **Runtime**: Node 20+
- **Node deps** (`frontend/package.json`): Oxlint

### Docker

- **Orchestration**: Docker Compose (`docker-compose.yml`)
- **Run command**: `docker compose up`
- **Services**: backend (`:8000`) and frontend (`:5173`)
- **Docker runtime note**: frontend container uses Node 22

## Running & Installation

### Quick Start

**One-command** — run both stacks with Docker. Ensure you have the latest:

```bash
docker compose up
```

Backend on `:8000` (auto-migrates, creates an `admin`/`admin1234` superuser), frontend on `:5173`.

### How to run the backend (Without Docker)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```

Runs at `http://127.0.0.1:8000/` — the homepage serves Swagger UI plus a listing of the available tools. The API lives under `/api/tasks/` (contract documented by the auto-generated OpenAPI schema at `/api/openapi.json`).

**Tests**:

```bash
cd backend
pytest
```

### How to run the frontend (Without Docker)

```bash
cd frontend
npm install
npm run dev
```

Runs at `http://localhost:5173/` and expects the backend on `http://localhost:8000` (base URL in `frontend/src/api.ts`). `npm run build` type-checks then builds; `npm run lint` runs Oxlint.

## Assumptions and tradeoffs

- **The agent is a rule-based router, not a real LLM call.** Every tool is deterministic (given the system clock — none calls an external API), so a live LLM would add an API key, latency, and non-determinism for no benefit at this scale. Tool selection sits behind a swappable interface (`backend/agent_api/agent.py`), so an LLM router could replace it without touching callers.
- **Multi-step prompts are handled by splitting the prompt on `" then "` into ordered stages, and each stage on `" and "` into parallel sub-prompts.** `" and "` sub-prompts run independently and their outputs are joined; `" then "` stages run sequentially, with each stage's joined output piped into the next stage's input before routing — so `"calculate 3 + 5 then convert to uppercase"` really does chain `CalculatorTool`'s output into `TextProcessorTool`. This is orchestration-level chaining in `AgentController`, not a real planner, and `BaseTool` stays untouched.
- **No auth/RBAC, no real-time streaming, no tool plugin registry** — deliberately cut as scope creep for three tools and three endpoints.
- **Dev-only settings**: SQLite, `DEBUG = True`, a checked-in `SECRET_KEY`. Nothing here is production-safe as-is.
- **The frontend hardcodes the backend URL** and relies on CORS (`django-cors-headers`) rather than a Vite dev proxy — one less moving part for local dev.

## Time spent

~12 hours over two day.

## What I'd improve with more time

- Swap the rule-based router for real LLM tool selection at the existing `select_tool` seam.
- An explicit `{result}` placeholder syntax for chained (`" then "`) prompts — today the previous stage's output is auto-injected by prepending it to the next stage's text; a placeholder would let the user control exactly where it lands.
- A frontend test runner (Vitest) with component tests — currently only the backend has tests.
- Streaming trace updates (SSE) so the execution trace renders live instead of after completion.
- Production-ready settings driven by environment variables (secret key, debug, allowed hosts, CORS origins).
- Pin toolchain versions (`.nvmrc`, `requires-python`).

## Documentation

- [backend/README.md](backend/README.md) — backend implementation guide (request lifecycle, code map, adding a tool)
- [frontend/README.md](frontend/README.md) — frontend implementation guide (data flow, code map)

## Project layout

```
task-agent/
├── README.md
├── docker-compose.yml             # one-command dev environment (both stacks)
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── README.md                  # backend implementation guide
│   ├── config/                    # Django project (settings/urls/wsgi)
│   └── agent_api/                 # single Django app
│       ├── models.py              # Task, ExecutionStep
│       ├── tools.py               # BaseTool + 5 tool implementations
│       ├── agent.py               # AgentController (routing + execution loop)
│       ├── serializers.py / views.py / urls.py
│       ├── templates/agent_api/home.html   # Swagger UI homepage
│       └── tests/                 # test_tools / test_agent / test_api
└── frontend/
    ├── README.md                  # frontend implementation guide
    └── src/
        ├── api.ts                 # fetch wrappers (+ dormant mock layer)
        ├── types.ts               # shapes mirroring the API responses
        ├── App.tsx
        └── components/            # TaskInput, ResultPanel, ExecutionTrace, TaskHistory
```
