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

  // The sidebar only earns its space once there is something to browse
  // besides the current task.
  if (isLoading || tasks.length <= 1) return null;

  return (
    <aside className="history-pane">
      <h2>History</h2>
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
    </aside>
  );
}
