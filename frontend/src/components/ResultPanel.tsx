import type { Task } from '../types';

interface ResultPanelProps {
  task: Task;
}

export default function ResultPanel({ task }: ResultPanelProps) {
  return (
    <div className="result-panel">
      <p className="result-prompt">{task.prompt}</p>
      <p className="result-value">{task.result}</p>
    </div>
  );
}
