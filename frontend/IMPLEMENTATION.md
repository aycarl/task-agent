# Frontend Implementation Plan

React + Vite. Scope and cross-cutting decisions live in [`docs/architecture.md`](../docs/architecture.md) — this doc is build detail for `frontend/` only. Request/response shapes come from [`docs/api.md`](../docs/api.md), not restated here.

## File layout

```
frontend/
├── package.json
├── index.html
└── src/
    ├── main.jsx
    ├── App.jsx
    ├── api.js                  # fetch wrapper
    ├── components/
    │   ├── TaskInput.jsx
    │   ├── TaskHistory.jsx
    │   ├── ResultPanel.jsx
    │   └── ExecutionTrace.jsx
    └── styles.css
```

No `AppLayout`/sidebar shell abstraction, no separate `AgentChatArea` — a "chat area" implies conversational UI this project doesn't need (the flow is: enter task → submit → view result → view history → inspect trace). Four focused components cover that exactly.

## `api.js`

```javascript
const BASE_URL = "http://localhost:8000/api";

export async function submitTask(prompt) {
  const res = await fetch(`${BASE_URL}/tasks/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) throw new Error((await res.json()).error || "Request failed");
  return res.json();
}

export async function fetchTasks() {
  const res = await fetch(`${BASE_URL}/tasks/`);
  return res.json();
}

export async function fetchTask(id) {
  const res = await fetch(`${BASE_URL}/tasks/${id}/`);
  return res.json();
}
```

## Components

- **`TaskInput`** — text input + submit button. Calls `submitTask`, hands the resulting task up to `App`.
- **`ResultPanel`** — renders the active task's `result` (final output).
- **`TaskHistory`** — calls `fetchTasks` on mount, renders the list; row click calls `fetchTask(id)` and sets it as the active task.
- **`ExecutionTrace`** — the most important component in the frontend; execution trace quality and transparency is the whole point of showing the agent's work:

```jsx
export default function ExecutionTrace({ steps }) {
  if (!steps?.length) return null;
  return (
    <ol className="trace">
      {steps.map((s) => (
        <li key={s.step_number} className={s.tool_name ? "trace-step tool" : "trace-step"}>
          <span className="trace-step-num">Step {s.step_number}</span>
          <span className="trace-desc">{s.description}</span>
        </li>
      ))}
    </ol>
  );
}
```

`App.jsx` wires `TaskInput` → `submitTask` → sets active task state → renders `ResultPanel` + `ExecutionTrace`; `TaskHistory` calls `fetchTasks` on mount and `fetchTask(id)` on row click. Standard `useState`/`useEffect`, no state library needed for four components.

## Styling

Plain CSS: one accent color, system font stack or a single imported font, consistent spacing scale. No glassmorphism/animation work — that time is better spent on trace legibility and the README.

## Build order

Starts once the backend's `POST`/`GET /api/tasks/` endpoints are live and verified (`backend/IMPLEMENTATION.md`, step 3):

1. `api.js` — wire against the running backend, confirm shapes match `docs/api.md`.
2. `TaskInput` → submit flow working end-to-end.
3. `ResultPanel` — display the result.
4. `ExecutionTrace` — display the trace (the most important frontend piece).
5. `TaskHistory` — list + click-to-inspect past tasks.

README and Dockerfile (if time remains) are cross-cutting — see the overall build order in [`docs/architecture.md`](../docs/architecture.md).
