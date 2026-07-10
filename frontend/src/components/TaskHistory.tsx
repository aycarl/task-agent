import { useEffect, useRef, useState } from 'react';
import type { TaskSummary } from '../types';
import { fetchTasks } from '../api';

interface TaskHistoryProps {
  onSelectTask: (id: number) => void;
  activeTaskId?: number | null;
}

export default function TaskHistory({ onSelectTask, activeTaskId }: TaskHistoryProps) {
  const [tasks, setTasks] = useState<TaskSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const hasShown = useRef(false);

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
  // besides the task already on screen: more than one task, or a lone task
  // with nothing displayed (e.g. after a page reload). Once shown it stays
  // for the life of this mount, so selecting that lone task doesn't
  // collapse the sidebar under the cursor.
  const shouldShow =
    !isLoading && (tasks.length > 1 || (tasks.length === 1 && activeTaskId == null));
  if (shouldShow) hasShown.current = true;
  if (!hasShown.current) return null;

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
