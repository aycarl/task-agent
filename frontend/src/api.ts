import type { ExecutionStep, Task, TaskSummary } from './types';

const BASE_URL = 'http://localhost:8000/api';

// Dormant mock backend kept for backend-less UI demos — flip to true to use it,
// or delete the mock section below if it's no longer wanted.
const USE_MOCK = false;

export async function submitTask(prompt: string): Promise<Task> {
  if (USE_MOCK) return mockSubmitTask(prompt);
  const res = await fetch(`${BASE_URL}/tasks/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) throw new Error((await res.json()).error || 'Request failed');
  return res.json();
}

export async function fetchTasks(): Promise<TaskSummary[]> {
  if (USE_MOCK) return mockFetchTasks();
  const res = await fetch(`${BASE_URL}/tasks/`);
  if (!res.ok) throw new Error('Request failed');
  return res.json();
}

export async function fetchTask(id: number): Promise<Task> {
  if (USE_MOCK) return mockFetchTask(id);
  const res = await fetch(`${BASE_URL}/tasks/${id}/`);
  if (!res.ok) throw new Error((await res.json()).error || 'Request failed');
  return res.json();
}

// ---- Mock layer (delete this whole section, and the USE_MOCK branches above, once the backend is live) ----

function delay(ms = 300): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function makeTask(id: number, prompt: string, createdAt: string, toolName: string | null, result: string): Task {
  const steps: ExecutionStep[] = [
    { step_number: 1, description: `Received input "${prompt}"`, tool_name: null, timestamp: createdAt },
  ];
  if (toolName) {
    steps.push({ step_number: 2, description: `Selected tool: ${toolName}`, tool_name: toolName, timestamp: createdAt });
    steps.push({ step_number: 3, description: `Tool result: ${result}`, tool_name: toolName, timestamp: createdAt });
  } else {
    steps.push({ step_number: 2, description: `No matching tool for: "${prompt}"`, tool_name: null, timestamp: createdAt });
  }
  steps.push({ step_number: steps.length + 1, description: 'Returning result to user', tool_name: null, timestamp: createdAt });
  return { id, prompt, result, created_at: createdAt, steps };
}

let nextMockId = 4;
const mockTasks: Task[] = [
  makeTask(3, "Convert 'hello world' to uppercase", '2026-07-09T09:10:00Z', 'TextProcessorTool', 'HELLO WORLD'),
  makeTask(2, 'weather in Toronto', '2026-07-09T09:05:00Z', 'WeatherMockTool', 'Toronto: 18°C, Cloudy'),
  makeTask(1, 'What is 15 + 27?', '2026-07-09T09:00:00Z', 'CalculatorTool', '42'),
];

// Whitelist-only expression, mirroring the real CalculatorTool's guard
// (backend/agent_api/tools.py): only digits/operators/parens ever reach evaluation.
const CALC_EXPR = /^[\d.\s+\-*/()]+$/;

function runCalculator(prompt: string): string | null {
  if (!/\d+\s*[+\-*/]\s*\d+/.test(prompt)) return null;
  // Non-global match() would grab the *first* whitelist-char run, which can be a
  // lone space before the real expression (e.g. "What is 15 + 27?"). Scan all runs
  // and take the first one that actually contains a digit.
  const matches = prompt.match(/[\d.\s+\-*/()]+/g) ?? [];
  const expr = matches.find((m) => /\d/.test(m))?.trim() ?? '';
  if (!expr || !CALC_EXPR.test(expr)) return null;
  try {
    const value = Function(`"use strict"; return (${expr});`)();
    return typeof value === 'number' && Number.isFinite(value) ? String(value) : null;
  } catch {
    return null;
  }
}

const MOCK_WEATHER: Record<string, string> = {
  toronto: '18°C, Cloudy',
  vancouver: '15°C, Rainy',
  montreal: '20°C, Sunny',
};

function runWeather(prompt: string): string {
  const lower = prompt.toLowerCase();
  for (const [city, forecast] of Object.entries(MOCK_WEATHER)) {
    if (lower.includes(city)) return `${city[0].toUpperCase()}${city.slice(1)}: ${forecast}`;
  }
  return 'No mock data for that city (defaulting): 20°C, Clear';
}

function runTextProcessor(prompt: string): string | null {
  const lower = prompt.toLowerCase();
  const text = lower.replace(/(convert|to|uppercase|lowercase|word count|of)/g, '').trim().replace(/^['"]|['"]$/g, '');
  if (lower.includes('uppercase')) return text.toUpperCase();
  if (lower.includes('lowercase')) return text.toLowerCase();
  if (lower.includes('word count')) return String(text.split(/\s+/).filter(Boolean).length);
  return null;
}

function routeMockPrompt(prompt: string): { toolName: string | null; result: string } {
  const calcResult = runCalculator(prompt);
  if (calcResult !== null) return { toolName: 'CalculatorTool', result: calcResult };

  const textResult = runTextProcessor(prompt);
  if (textResult !== null) return { toolName: 'TextProcessorTool', result: textResult };

  if (/weather/i.test(prompt)) return { toolName: 'WeatherMockTool', result: runWeather(prompt) };

  return { toolName: null, result: `(unhandled: ${prompt})` };
}

async function mockSubmitTask(prompt: string): Promise<Task> {
  await delay();
  const trimmed = prompt.trim();
  if (!trimmed) throw new Error('prompt is required');
  const { toolName, result } = routeMockPrompt(trimmed);
  const task = makeTask(nextMockId++, trimmed, new Date().toISOString(), toolName, result);
  mockTasks.unshift(task);
  return task;
}

async function mockFetchTasks(): Promise<TaskSummary[]> {
  await delay();
  return mockTasks.map(({ id, prompt, result, created_at }) => ({ id, prompt, result, created_at }));
}

async function mockFetchTask(id: number): Promise<Task> {
  await delay();
  const task = mockTasks.find((t) => t.id === id);
  if (!task) throw new Error('not found');
  return task;
}
