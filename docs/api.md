# API Contract

Single source of truth for backend↔frontend integration. `backend/IMPLEMENTATION.md` and `frontend/IMPLEMENTATION.md` both reference this instead of restating request/response shapes — update it first if the contract changes, then update whichever stack plan is affected.

Base URL (dev): `http://localhost:8000/api`

## `POST /api/tasks/`

Submit a task for the agent to process.

Request:

```json
{ "prompt": "What is 15 + 27?" }
```

Response `201 Created`:

```json
{
  "id": 1,
  "prompt": "What is 15 + 27?",
  "result": "42",
  "created_at": "2026-07-09T12:00:00Z",
  "steps": [
    { "step_number": 1, "description": "Received input \"What is 15 + 27?\"", "tool_name": null, "timestamp": "2026-07-09T12:00:00Z" },
    { "step_number": 2, "description": "Selected tool: CalculatorTool", "tool_name": "CalculatorTool", "timestamp": "2026-07-09T12:00:00Z" },
    { "step_number": 3, "description": "Tool result: 42", "tool_name": "CalculatorTool", "timestamp": "2026-07-09T12:00:00Z" },
    { "step_number": 4, "description": "Returning result to user", "tool_name": null, "timestamp": "2026-07-09T12:00:00Z" }
  ]
}
```

Response `400 Bad Request` (empty/missing prompt):

```json
{ "error": "prompt is required" }
```

## `GET /api/tasks/`

List past tasks for the history view, most recent first. Lighter payload — no `steps` (avoids pulling every task's full trace just to render a list).

Response `200 OK`:

```json
[
  { "id": 2, "prompt": "weather in Toronto", "result": "Toronto: 18°C, Cloudy", "created_at": "2026-07-09T12:05:00Z" },
  { "id": 1, "prompt": "What is 15 + 27?", "result": "42", "created_at": "2026-07-09T12:00:00Z" }
]
```

## `GET /api/tasks/{id}/`

Fetch one task with its full execution trace — used when a history row is clicked.

Response `200 OK`: same shape as the `POST` response above (includes `steps`).

Response `404 Not Found`:

```json
{ "error": "not found" }
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
