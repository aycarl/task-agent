import type { ExecutionStep } from '../types';

interface ExecutionTraceProps {
  steps?: ExecutionStep[];
}

export default function ExecutionTrace({ steps }: ExecutionTraceProps) {
  if (!steps?.length) return null;
  return (
    <ol className="trace">
      {steps.map((s) => (
        <li key={s.step_number} className={s.tool_name ? 'trace-step tool' : 'trace-step'}>
          <span className="trace-step-num">Step {s.step_number}</span>
          <span className="trace-desc">{s.description}</span>
        </li>
      ))}
    </ol>
  );
}
