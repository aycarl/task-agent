# API Contract

Single source of truth for backend↔frontend integration. `backend/IMPLEMENTATION.md` and `frontend/IMPLEMENTATION.md` both reference this instead of restating request/response shapes — update it first if the contract changes, then update whichever stack plan is affected.

Base URL (dev): `http://localhost:8000/api`

Built on DRF `ModelViewSet`s behind a `DefaultRouter`, with `HyperlinkedModelSerializer`s — every object carries a `url` to itself instead of (well, in addition to) a bare `id`. `GET /api/` is the DRF browsable API root, linking to `tasks` and `steps`.

## `POST /api/tasks/`

Submit a task for the agent to process. The prompt is routed through `AgentController`, not saved as-is — `result` and `steps` are populated by tool execution and are **read-only** on the client side (rejected/ignored if sent).

Request:

```json
{ "prompt": "What is 15 + 27?" }
```

Response `201 Created`:

```json
{
  "url": "http://localhost:8000/api/tasks/1/",
  "id": 1,
  "prompt": "What is 15 + 27?",
  "result": "42",
  "created_at": "2026-07-09T12:00:00Z",
  "steps": [
    { "url": "http://localhost:8000/api/steps/1/", "step_number": 1, "description": "Received input \"What is 15 + 27?\"", "tool_name": null, "timestamp": "2026-07-09T12:00:00Z" },
    { "url": "http://localhost:8000/api/steps/2/", "step_number": 2, "description": "Selected tool: CalculatorTool", "tool_name": "CalculatorTool", "timestamp": "2026-07-09T12:00:00Z" },
    { "url": "http://localhost:8000/api/steps/3/", "step_number": 3, "description": "Tool result: 42", "tool_name": "CalculatorTool", "timestamp": "2026-07-09T12:00:00Z" },
    { "url": "http://localhost:8000/api/steps/4/", "step_number": 4, "description": "Returning result to user", "tool_name": null, "timestamp": "2026-07-09T12:00:00Z" }
  ]
}
```

Response `400 Bad Request` (empty, missing, or whitespace-only prompt) — standard DRF field-error shape:

```json
{ "prompt": ["This field may not be blank."] }
```

## `GET /api/tasks/`

List past tasks for the history view, most recent first. Lighter payload — no `steps` (avoids pulling every task's full trace just to render a list).

Response `200 OK`:

```json
[
  { "url": "http://localhost:8000/api/tasks/2/", "id": 2, "prompt": "weather in Toronto", "result": "Toronto: 18°C, Cloudy", "created_at": "2026-07-09T12:05:00Z" },
  { "url": "http://localhost:8000/api/tasks/1/", "id": 1, "prompt": "What is 15 + 27?", "result": "42", "created_at": "2026-07-09T12:00:00Z" }
]
```

## `GET /api/tasks/{id}/`

Fetch one task with its full execution trace — used when a history row is clicked.

Response `200 OK`: same shape as the `POST` response above (includes `steps`).

Response `404 Not Found` — standard DRF detail shape:

```json
{ "detail": "No Task matches the given query." }
```

## `PUT` / `PATCH /api/tasks/{id}/`

Edit a task's `prompt`. Only `prompt` is writable — `result`, `created_at`, and `steps` are read-only, so editing does **not** re-run the agent. Same `400`/`404` shapes as above.

## `DELETE /api/tasks/{id}/`

Delete a task. Cascades to delete its execution steps. Response `204 No Content`.

## `GET /api/steps/` / `GET /api/steps/{id}/`

Read-only. Steps are only ever produced by `AgentController` — there's no client-initiated create/update/delete, so this viewset only exposes `list`/`retrieve` (`POST`/`PUT`/`PATCH`/`DELETE` return `405`). Useful for following a step's `url` out of a task's `steps` array, or browsing steps across all tasks.

Response `200 OK` (single step):

```json
{ "url": "http://localhost:8000/api/steps/1/", "step_number": 1, "description": "Received input \"What is 15 + 27?\"", "tool_name": null, "timestamp": "2026-07-09T12:00:00Z" }
```

## Execution step shape

Matches this format:

```
Step 1: Received input "Convert to uppercase"
Step 2: Selected tool: TextProcessorTool
Step 3: Tool result: HELLO
Step 4: Returning result to user
```

`tool_name` is `null` on bookkeeping steps (received input / returning result) and set on tool-selection and tool-result steps. The frontend's `ExecutionTrace` component uses this to visually distinguish tool-execution steps from bookkeeping ones — see `frontend/IMPLEMENTATION.md`.

Multi-step prompts (e.g. "What is 2 + 2 and weather in Toronto") produce one selected-tool/tool-result pair per matched sub-prompt, all under the same `Task`, still ordered by `step_number`.

## OpenAPI spec

A hand-written OpenAPI 3.0 document covering all of the above lives at `backend/agent_api/static/agent_api/openapi.yaml`, served at `/static/agent_api/openapi.yaml` and rendered via Swagger UI at `/api/docs/`.
