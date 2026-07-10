# Frontend — implementation guide

React 19 + TypeScript + Vite. Four focused components wired from `App.tsx` with plain `useState`/`useEffect` — no state library, no router, deliberately not a chat UI. The flow is: submit a task → see the result and its execution trace featured at the top → expand any earlier run in place to inspect its trace. The layout is a single centered column that never changes shape — there is no sidebar and no conditional macro-layout.

The API contract this consumes is documented by the backend's auto-generated OpenAPI schema (`/api/openapi.json`, rendered by Swagger UI at `/`); the server side is documented in [`backend/README.md`](../backend/README.md).

## Data flow

1. **`TaskInput`** (controlled form) trims the prompt and calls `App.handleSubmit`, which POSTs via `submitTask` (`src/api.ts`). While the request is in flight the form is disabled and the button reads "Running…".
2. The response (a full task with `steps`) becomes `activeTask` state in `App.tsx`, rendering **`ResultPanel`** (prompt + final result) and **`ExecutionTrace`** (the ordered step list — steps with a `tool_name` get a `tool` CSS class so tool execution is visually distinct from bookkeeping steps).
3. `App` also bumps a `historyVersion` counter used as **`TaskHistory`**'s `key` — remounting it after each submit so it refetches the list. History rows show prompt + result and expand in place (one open at a time); the first expand calls `fetchTask(id)` for the steps and caches them. The featured task (`activeTask`) is excluded from the list via `excludeTaskId`.
4. Any API error surfaces as a dismissable-by-resubmit error banner in `App`.

## Code map

| File | What's in it |
|---|---|
| `src/api.ts` | `submitTask` / `fetchTasks` / `fetchTask` fetch wrappers against `BASE_URL = http://localhost:8000/api` (hardcoded — the backend allows the Vite origin via CORS; there's no dev-server proxy). Also contains a dormant mock backend behind `USE_MOCK = false`, kept from before the real API existed — flip the flag to demo the UI without a backend, or delete the section below the marker comment. |
| `src/types.ts` | `ExecutionStep`, `TaskSummary` (list shape, no steps), and `Task extends TaskSummary` (adds `steps`) — mirrors the API response shapes (see the backend's OpenAPI schema). |
| `src/App.tsx` | State owner: `activeTask`, `isSubmitting`, `error`, `historyVersion`. Wires the four components. |
| `src/components/TaskInput.tsx` | Tool chips (one per tool, click to fill the input with a known-good example phrasing) + controlled input + submit button; ignores empty/whitespace prompts. |
| `src/components/ResultPanel.tsx` | Renders the active task's prompt and result. |
| `src/components/ExecutionTrace.tsx` | Ordered trace list; renders nothing if there are no steps. |
| `src/components/TaskHistory.tsx` | Fetches the task list on mount (with a cancellation flag to avoid setting state after unmount); renders "Earlier"/"History" rows that expand their trace inline — steps are lazily fetched on first open and cached (`'failed'` entries retry on the next expand); renders nothing only when the filtered list is empty. |
| `src/App.css`, `src/index.css` | Plain CSS — one accent color, system font stack. |

## Commands

```bash
npm install
npm run dev        # http://localhost:5173/ — expects the backend on http://localhost:8000
npm run build      # tsc -b type-check, then vite build
npm run lint       # oxlint
npm run preview    # serve a production build
```

No test runner is configured — adding Vitest + component tests is on the improvements list in the root [README](../README.md).
