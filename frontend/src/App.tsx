import { useState } from 'react';
import type { Task } from './types';
import { fetchTask, submitTask } from './api';
import TaskInput from './components/TaskInput';
import ResultPanel from './components/ResultPanel';
import ExecutionTrace from './components/ExecutionTrace';
import TaskHistory from './components/TaskHistory';
import './App.css';

function App() {
  const [activeTask, setActiveTask] = useState<Task | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [historyVersion, setHistoryVersion] = useState(0);

  async function handleSubmit(prompt: string) {
    setIsSubmitting(true);
    setError(null);
    try {
      const task = await submitTask(prompt);
      setActiveTask(task);
      setHistoryVersion((v) => v + 1);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleSelectTask(id: number) {
    setError(null);
    try {
      setActiveTask(await fetchTask(id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    }
  }

  return (
    <main className="page">
      <div className="work-pane">
        <header className="page-header">
          <h1>Task Agent</h1>
          <p>Give the agent a task. It picks a tool, runs it, and shows every step.</p>
        </header>

        <TaskInput onSubmit={handleSubmit} disabled={isSubmitting} />
        {error && <p className="error-banner">{error}</p>}

        {activeTask && (
          <section className="result-section">
            <ResultPanel task={activeTask} />
            <ExecutionTrace steps={activeTask.steps} />
          </section>
        )}
      </div>

      <TaskHistory key={historyVersion} onSelectTask={handleSelectTask} activeTaskId={activeTask?.id} />
    </main>
  );
}

export default App;
