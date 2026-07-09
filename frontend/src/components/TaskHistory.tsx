import { useEffect, useState } from 'react';
import type { TaskSummary } from '../types';
import { fetchTasks } from '../api';

interface TaskHistoryProps {
  onSelectTask: (id: number) => void;
  activeTaskId?: number | null;
}

export default function TaskHistory({ onSelectTask, activeTaskId }: TaskHistoryProps) {
  const [tasks, setTasks] = useState<TaskSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);

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

  return (
    <section className="task-history">
      <h2>History</h2>
      {isLoading && <p className="history-empty">Loading…</p>}
      {!isLoading && tasks.length === 0 && <p className="history-empty">No tasks yet.</p>}
      {tasks.length > 0 && (
        <ul className="history-list">
          {tasks.map((task) => (
            <li key={task.id}>
              <button
                type="button"
                className={task.id === activeTaskId ? 'history-item active' : 'history-item'}
                onClick={() => onSelectTask(task.id)}
              >
                <span className="history-prompt">{task.prompt}</span>
                <span className="history-result">{task.result}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
