import { useRef, useState } from 'react';
import type { FormEvent } from 'react';

interface TaskInputProps {
  onSubmit: (prompt: string) => void;
  disabled?: boolean;
}

// One chip per tool, each carrying a phrasing the router is known to match.
const TOOLS = [
  { name: 'calculator', example: '12 * (3 + 4)' },
  { name: 'text', example: "reverse 'hello world'" },
  { name: 'weather', example: 'weather in toronto' },
  { name: 'days since', example: 'days since 2024-01-15' },
  { name: 'city time', example: 'time in tokyo' },
];

export default function TaskInput({ onSubmit, disabled }: TaskInputProps) {
  const [prompt, setPrompt] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = prompt.trim();
    if (!trimmed || disabled) return;
    onSubmit(trimmed);
    setPrompt('');
  }

  function fillExample(example: string) {
    setPrompt(example);
    inputRef.current?.focus();
  }

  return (
    <div className="task-entry">
      <div className="tool-chips" role="group" aria-label="Available tools">
        <span className="tool-chips-label">Tools</span>
        {TOOLS.map((tool) => (
          <button
            key={tool.name}
            type="button"
            className="tool-chip"
            title={`Try: ${tool.example}`}
            disabled={disabled}
            onClick={() => fillExample(tool.example)}
          >
            {tool.name}
          </button>
        ))}
      </div>
      <form className="task-form" onSubmit={handleSubmit}>
        <input
          ref={inputRef}
          className="task-input"
          type="text"
          placeholder="e.g. What is 15 + 27?"
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
          disabled={disabled}
          aria-label="Task prompt"
        />
        <button className="btn-primary" type="submit" disabled={disabled || !prompt.trim()}>
          {disabled ? 'Running…' : 'Run'}
        </button>
      </form>
    </div>
  );
}
