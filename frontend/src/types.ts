export interface ExecutionStep {
  step_number: number;
  description: string;
  tool_name: string | null;
  timestamp: string;
}

export interface TaskSummary {
  id: number;
  prompt: string;
  result: string;
  created_at: string;
}

export interface Task extends TaskSummary {
  steps: ExecutionStep[];
}
