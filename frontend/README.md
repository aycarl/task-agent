# Frontend — implementation guide

React 19 + TypeScript + Vite. Four focused components wired from `App.tsx` with plain `useState`/`useEffect` — no state library, no router, deliberately not a chat UI. The flow is: submit a task → see the result and its execution trace → browse history → click a past task to inspect its trace.

The API contract this consumes is defined in [`docs/api.md`](../docs/api.md); the server side is documented in [`backend/README.md`](../backend/README.md).

## Data flow

1. **`TaskInput`** (controlled form) trims the prompt and calls `App.handleSubmit`, which POSTs via `submitTask` (`src/api.ts`). While the request is in flight the form is disabled and the button reads "Running…".
2. The response (a full task with `steps`) becomes `activeTask` state in `App.tsx`, rendering **`ResultPanel`** (prompt + final result) and **`ExecutionTrace`** (the ordered step list — steps with a `tool_name` get a `tool` CSS class so tool execution is visually distinct from bookkeeping steps).
3. `App` also bumps a `historyVersion` counter used as **`TaskHistory`**'s `key` — remounting it after each submit so it refetches the list. History rows show prompt + result; clicking one calls `fetchTask(id)` and swaps that task (with its trace) in as `activeTask`.
4. Any API error surfaces as a dismissable-by-resubmit error banner in `App`.

## Code map

| File | What's in it |
|---|---|
| `src/api.ts` | `submitTask` / `fetchTasks` / `fetchTask` fetch wrappers against `BASE_URL = http://localhost:8000/api` (hardcoded — the backend allows the Vite origin via CORS; there's no dev-server proxy). Also contains a dormant mock backend behind `USE_MOCK = false`, kept from before the real API existed — flip the flag to demo the UI without a backend, or delete the section below the marker comment. |
| `src/types.ts` | `ExecutionStep`, `TaskSummary` (list shape, no steps), and `Task extends TaskSummary` (adds `steps`) — mirrors [`docs/api.md`](../docs/api.md). |
| `src/App.tsx` | State owner: `activeTask`, `isSubmitting`, `error`, `historyVersion`. Wires the four components. |
| `src/components/TaskInput.tsx` | Controlled input + submit button; ignores empty/whitespace prompts. |
| `src/components/ResultPanel.tsx` | Renders the active task's prompt and result. |
| `src/components/ExecutionTrace.tsx` | Ordered trace list; renders nothing if there are no steps. |
| `src/components/TaskHistory.tsx` | Fetches the task list on mount (with a cancellation flag to avoid setting state after unmount); loading/empty states; row click reports the id up via `onSelectTask`. |
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
