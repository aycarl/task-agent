# Architecture

A task submitted through the UI is passed to an `AgentController`, which selects and runs a `Tool`, and returns both the final result and a structured execution trace.

## System overview

The full round trip, as built:

1. The React frontend (`frontend/src/`) POSTs a prompt to `POST /api/tasks/`.
2. A DRF viewset hands the prompt to `AgentController` (`backend/agent_api/agent.py`), which splits it on `" and "`, routes each sub-prompt to the first `Tool` whose `can_handle` matches (calculator, text processing, or mock weather), and persists every step as a timestamped `ExecutionStep` row.
3. The response carries the task, its result, and the ordered trace; the frontend renders the result (`ResultPanel`), the trace (`ExecutionTrace`), and a clickable history of past tasks (`TaskHistory`).

The backend also serves Swagger UI at `/` (backed by an auto-generated OpenAPI schema at `/api/openapi.json`) and the Django admin at `/admin/`.

Stack-level guides to the code: [`backend/README.md`](../backend/README.md), [`frontend/README.md`](../frontend/README.md). API contract: [`api.md`](api.md).

## Project layout

```
task-agent/
├── README.md
├── docker-compose.yml             # one-command dev environment (both stacks)
├── docs/                          # architecture / api contract / setup
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── README.md                  # backend implementation guide
│   ├── config/                    # Django project (settings/urls/wsgi)
│   └── agent_api/                 # single Django app
│       ├── models.py              # Task, ExecutionStep
│       ├── tools.py               # BaseTool + 3 tool implementations
│       ├── agent.py               # AgentController (routing + execution loop)
│       ├── serializers.py / views.py / urls.py
│       ├── templates/agent_api/home.html   # Swagger UI homepage
│       └── tests/                 # test_tools / test_agent / test_api
└── frontend/
    ├── README.md                  # frontend implementation guide
    └── src/
        ├── api.ts                 # fetch wrappers (+ dormant mock layer)
        ├── types.ts               # shapes mirroring docs/api.md
        ├── App.tsx
        └── components/            # TaskInput, ResultPanel, ExecutionTrace, TaskHistory
```

## Key decisions

**Agent reasoning engine: rule-based, not a real LLM call.**
Every tool here is deterministic (`WeatherMockTool` is mock data — no external API involved), and a live LLM call would add an API key dependency, network latency, and non-determinism for no real benefit at this scale. A rule-based classifier behind a swappable interface (`_select_tool(prompt) -> Tool`, see `backend/agent_api/agent.py`) demonstrates the actual skill this project is exercising — tool routing / orchestration — while leaving a clean seam where a real LLM router could be swapped in without touching callers.

**A DRF viewset behind a router, trimmed to only the verbs the frontend uses.** `Task` uses a `HyperlinkedModelSerializer` (every task carries a `url` to itself) but only exposes `list`/`create`/`retrieve` — built from individual mixins, not `ModelViewSet`, so `update`/`partial_update`/`destroy` don't exist rather than being blocked. `ExecutionStep` has no endpoint or hyperlink of its own; it's nested inside a task's `steps` array as a plain object. An intermediate version gave both models full `ModelViewSet`s (matching DRF's idiomatic default, including a standalone `/api/steps/` resource that existed solely so `ExecutionStep`'s hyperlink field had somewhere to resolve to) — trimmed back down once actual frontend usage made clear that surface was unused, landing close to the original plain-`APIView` minimalism but via DRF's viewset/router machinery instead of hand-rolled views.

**Multi-step support via `" and "` splitting**, not a real planning/loop system — demonstrates chaining more than one tool without over-building.

**No dynamic tool plugin/registry.** Three tools; an ordered list is sufficient.

## Explicitly out of scope

| Feature | Reason skipped |
|---|---|
| Real LLM call for intent parsing | Tools here are deterministic by design; a live call adds an API key/latency/non-determinism for no real benefit |
| Real-time streaming (SSE/WS) | High implementation risk for a feature that only needs post-hoc clarity |
| RBAC / auth | No login/auth requirement in scope — inventing one would be pure scope creep |
| Dynamic tool plugin/registry system | Three tools; a list is sufficient, a plugin system solves a problem that doesn't exist yet |
| Retry-with-backoff in the agent | Tools are pure functions with no transient failure modes to retry against; errors are caught and logged as a trace step instead |

## Build order (as executed)

Backend first — models → tools → agent → tests → API layer — verified with `pytest` and `curl` before any UI work. Then the frontend against the live API: `api.ts` → `TaskInput` → `ResultPanel` → `ExecutionTrace` → `TaskHistory` (an in-memory mock backend in `api.ts` let the UI develop in parallel; it's still there behind a `USE_MOCK = false` flag). Docs, the root README, and the Docker Compose setup landed last.

## Why docs are split this way

- [`api.md`](api.md) is the single source of truth for request/response shapes — both stack guides reference it instead of restating it, so the contract can't drift between them.
- [`backend/README.md`](../backend/README.md) and [`frontend/README.md`](../frontend/README.md) hold stack-local implementation detail (code map, request/data flow, how to extend) — colocated with the code they describe.
- This file holds everything that's a project-scope decision rather than a backend-or-frontend one: what's in/out of scope and why, and how the pieces fit together.
