import { useEffect, useState } from 'react';
import type { ExecutionStep, TaskSummary } from '../types';
import { fetchTask, fetchTasks } from '../api';
import ExecutionTrace from './ExecutionTrace';

interface TaskHistoryProps {
  excludeTaskId?: number | null;
}

export default function TaskHistory({ excludeTaskId }: TaskHistoryProps) {
  const [tasks, setTasks] = useState<TaskSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [openId, setOpenId] = useState<number | null>(null);
  // Traces are fetched lazily on first expand and cached; 'failed' allows a
  // retry on the next expand instead of caching the error.
  const [traces, setTraces] = useState<Record<number, ExecutionStep[] | 'failed'>>({});

  useEffect(() => {
    let cancelled = false;
    fetchTasks()
      .then((data) => {
        if (!cancelled) setTasks(data);
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const rows = tasks.filter((task) => task.id !== excludeTaskId);
  if (isLoading || rows.length === 0) return null;

  function toggle(id: number) {
    if (openId === id) {
      setOpenId(null);
      return;
    }
    setOpenId(id);
    if (Array.isArray(traces[id])) return;
    fetchTask(id)
      .then((task) => setTraces((prev) => ({ ...prev, [id]: task.steps ?? [] })))
      .catch(() => setTraces((prev) => ({ ...prev, [id]: 'failed' })));
  }

  return (
    <section className="task-history">
      <h2>{excludeTaskId != null ? 'Earlier' : 'History'}</h2>
      <ul className="history-list">
        {rows.map((task) => {
          const isOpen = task.id === openId;
          const trace = traces[task.id];
          return (
            <li key={task.id} className={isOpen ? 'history-row open' : 'history-row'}>
              <button
                type="button"
                className="history-toggle"
                aria-expanded={isOpen}
                onClick={() => toggle(task.id)}
              >
                <span className="history-chevron" aria-hidden="true">
                  ▶
                </span>
                <span className="history-prompt">{task.prompt}</span>
                <span className="history-result">{task.result}</span>
              </button>
              {isOpen && (
                <div className="history-fold">
                  {trace === undefined && <p className="history-status">Loading…</p>}
                  {trace === 'failed' && (
                    <p className="history-status">Couldn't load the trace. Click to retry.</p>
                  )}
                  {Array.isArray(trace) && <ExecutionTrace steps={trace} />}
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </section>
  );
}
