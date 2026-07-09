import { useState } from 'react';
import type { FormEvent } from 'react';

interface TaskInputProps {
  onSubmit: (prompt: string) => void;
  disabled?: boolean;
}

export default function TaskInput({ onSubmit, disabled }: TaskInputProps) {
  const [prompt, setPrompt] = useState('');

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = prompt.trim();
    if (!trimmed || disabled) return;
    onSubmit(trimmed);
    setPrompt('');
  }

  return (
    <form className="task-form" onSubmit={handleSubmit}>
      <input
        className="task-input"
        type="text"
        placeholder="e.g. What is 15 + 27?"
        value={prompt}
        onChange={(event) => setPrompt(event.target.value)}
        disabled={disabled}
        aria-label="Task prompt"
      />
      <button className="btn-primary" type="submit" disabled={disabled || !prompt.trim()}>
        {disabled ? 'Running…' : 'Submit'}
      </button>
    </form>
  );
}
