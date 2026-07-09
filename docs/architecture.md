# Architecture

A task submitted through the UI is passed to an `AgentController`, which selects and runs a `Tool`, and returns both the final result and a structured execution trace.

## Current state

Both stacks are scaffolded but not yet implemented against the plan below:

- **`backend/`** — stock `django-admin startproject` (Django 6.0, project name `config`) plus one app, `agent_api`, generated via `startapp` and not yet registered in `INSTALLED_APPS`. `agent_api/models.py` and `agent_api/views.py` are empty. `backend/config/urls.py` only exposes `/admin/`.
- **`frontend/`** — stock Vite + React + TypeScript template. No API client, no fetch calls, no dev-server proxy to the backend.

Build detail for each stack: [`backend/IMPLEMENTATION.md`](../backend/IMPLEMENTATION.md), [`frontend/IMPLEMENTATION.md`](../frontend/IMPLEMENTATION.md). API contract: [`api.md`](api.md).

## Project layout

```
task-agent/
├── README.md
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── IMPLEMENTATION.md
│   ├── config/                    # Django project (settings/urls/wsgi)
│   └── agent_api/                 # single Django app
│       ├── models.py              # Task, ExecutionStep
│       ├── tools.py               # BaseTool + 3 tool implementations
│       ├── agent.py               # AgentController (routing + execution loop)
│       ├── serializers.py / views.py / urls.py
│       └── tests/
└── frontend/
    ├── IMPLEMENTATION.md
    └── src/
        ├── api.js
        └── components/            # TaskInput, TaskHistory, ResultPanel, ExecutionTrace
```

## Key decisions

**Agent reasoning engine: rule-based, not a real LLM call.**
Every tool here is deterministic (`WeatherMockTool` is mock data — no external API involved), and a live LLM call would add an API key dependency, network latency, and non-determinism for no real benefit at this scale. A rule-based classifier behind a swappable interface (`select_tool(prompt) -> Tool`, see `agent.py`) demonstrates the actual skill this project is exercising — tool routing / orchestration — without that risk. Worth noting the swap-in point in the root README as a future improvement.

**DRF `ModelViewSet`s behind a router, with `HyperlinkedModelSerializer`s.** Every object carries a `url` to itself; `Task` gets full CRUD via `ModelViewSet`, `ExecutionStep` gets a read-only viewset (`ReadOnlyModelViewSet`) so its `url` field has something to resolve to, since steps are still only ever produced by `AgentController`. This reverses an earlier decision to use plain `APIView`s to keep the endpoint surface minimal — the hyperlinked/viewset shape was chosen deliberately over that minimalism for a more idiomatic, fully RESTful API.

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

## Priority for optional/stretch features (highest to lowest signal-per-effort)

1. **Tests** — cheap, and testability is the whole point of the tool abstraction.
2. **Retry/fallback handling in the agent** — basic failure handling in the agent loop (satisfied at the catch-and-log level; see Key Decisions).
3. **Multi-step reasoning** (chaining >1 tool) — demonstrates tool-calling/orchestration beyond a single call.
4. **Dockerfile** — near-free polish, do last if time remains.
5. **Skipped**: real-time streaming and RBAC — see table above.

## Overall build order

1–5. Backend: models → tools → agent → tests → API layer. Detail: [`backend/IMPLEMENTATION.md`](../backend/IMPLEMENTATION.md).
6. Frontend: `api.js` → `TaskInput` → `ResultPanel` → `ExecutionTrace` → `TaskHistory`. Detail: [`frontend/IMPLEMENTATION.md`](../frontend/IMPLEMENTATION.md).
7. Root `README.md`: run instructions, dependencies, **assumptions/tradeoffs, time spent, what you'd improve** — cheap, and directly demonstrates thoughtfulness, practicality, and documentation clarity.
8. If time remains: Dockerfile for backend + frontend.

## Why docs are split this way

- [`api.md`](api.md) is the single source of truth for request/response shapes — both stack docs reference it instead of restating it, so the contract can't drift between them.
- [`backend/IMPLEMENTATION.md`](../backend/IMPLEMENTATION.md) and [`frontend/IMPLEMENTATION.md`](../frontend/IMPLEMENTATION.md) hold stack-local build detail (code, file layout, stack-specific build order) — colocated with the code they describe.
- This file holds everything that's a project-scope decision rather than a backend-or-frontend one: what's in/out of scope, why, and the order to build in.
