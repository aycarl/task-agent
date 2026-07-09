# Backend Implementation Plan

Django + DRF, SQLite. Scope and cross-cutting decisions (why rule-based over a real LLM call, what's explicitly out of scope, feature priority) live in [`docs/architecture.md`](../docs/architecture.md) — this doc is build detail for `backend/` only. Request/response shapes live in [`docs/api.md`](../docs/api.md), not here.

## File layout

```
backend/
├── manage.py
├── requirements.txt
├── config/                    # Django project (settings/urls/wsgi)
│   ├── settings.py
│   └── urls.py
└── agent_api/                 # single Django app — no need for more
    ├── models.py               # Task, ExecutionStep
    ├── tools.py                # BaseTool + 3 tool implementations
    ├── agent.py                # AgentController (routing + execution loop)
    ├── serializers.py
    ├── views.py                 # ModelViewSet + ReadOnlyModelViewSet, routed via DefaultRouter
    ├── urls.py
    └── tests/
        ├── test_tools.py
        ├── test_agent.py
        └── test_api.py
```

## `models.py`

`ExecutionStep` is shaped as a narrative log (matching the example trace format in [`docs/api.md`](../docs/api.md)), not just raw tool I/O — this lets both the single-tool case and multi-step case reuse the same structure without a later refactor.

```python
from django.db import models

class Task(models.Model):
    prompt = models.TextField()
    result = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

class ExecutionStep(models.Model):
    task = models.ForeignKey(Task, related_name="steps", on_delete=models.CASCADE)
    step_number = models.PositiveIntegerField()
    description = models.CharField(max_length=255)   # e.g. "Selected tool: CalculatorTool"
    tool_name = models.CharField(max_length=64, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["step_number"]
```

## `tools.py`

Minimal ABC. No dynamic discovery, no plugin registry — three tools don't need one.

```python
from abc import ABC, abstractmethod
import re

class BaseTool(ABC):
    name: str

    @abstractmethod
    def can_handle(self, prompt: str) -> bool:
        """Cheap keyword/regex check — used by the agent's router."""

    @abstractmethod
    def run(self, prompt: str) -> str:
        """Execute and return a plain-text result. Raise ToolError on bad input."""


class ToolError(Exception):
    pass


class CalculatorTool(BaseTool):
    name = "CalculatorTool"
    _EXPR = re.compile(r"^[\d\.\s\+\-\*\/\(\)]+$")

    def can_handle(self, prompt: str) -> bool:
        return bool(re.search(r"\d+\s*[\+\-\*/]\s*\d+", prompt))

    def run(self, prompt: str) -> str:
        # findall (not search) — search grabs the *first* whitelist-char run, which
        # can be a lone space before the real expression (e.g. "What is 15 + 27?").
        matches = re.findall(r"[\d\.\s\+\-\*/\(\)]+", prompt)
        expr = next((m.strip() for m in matches if re.search(r"\d", m)), "")
        if not expr or not self._EXPR.match(expr):
            raise ToolError(f"Could not parse a valid arithmetic expression from: {prompt!r}")
        try:
            # Safe: _EXPR whitelists digits/operators/parens only, builtins stripped.
            return str(eval(expr, {"__builtins__": {}}, {}))
        except ZeroDivisionError:
            raise ToolError("Division by zero")


class TextProcessorTool(BaseTool):
    name = "TextProcessorTool"

    def can_handle(self, prompt: str) -> bool:
        return any(k in prompt.lower() for k in ["uppercase", "lowercase", "word count"])

    def run(self, prompt: str) -> str:
        lower = prompt.lower()
        text = re.sub(r"(convert|to|uppercase|lowercase|word count|of)", "", lower, flags=re.I).strip(" '\"")
        if "uppercase" in lower:
            return text.upper()
        if "lowercase" in lower:
            return text.lower()
        if "word count" in lower:
            return str(len(text.split()))
        raise ToolError("No recognized text operation in prompt")


class WeatherMockTool(BaseTool):
    name = "WeatherMockTool"
    _MOCK_DATA = {"toronto": "18°C, Cloudy", "vancouver": "15°C, Rainy", "montreal": "20°C, Sunny"}

    def can_handle(self, prompt: str) -> bool:
        return "weather" in prompt.lower()

    def run(self, prompt: str) -> str:
        for city, forecast in self._MOCK_DATA.items():
            if city in prompt.lower():
                return f"{city.title()}: {forecast}"
        return "No mock data for that city (defaulting): 20°C, Clear"
```

## `agent.py`

This is the most important piece of the system — where task interpretation and tool routing actually happen. Router is a simple ordered list — first tool whose `can_handle` matches, wins. Multi-step support: split on `" and "` so a prompt can trigger more than one tool, demonstrating chained tool use without a real planning/loop system.

```python
from .tools import BaseTool, CalculatorTool, TextProcessorTool, WeatherMockTool, ToolError
from .models import Task, ExecutionStep

class AgentController:
    def __init__(self):
        self.tools: list[BaseTool] = [CalculatorTool(), TextProcessorTool(), WeatherMockTool()]

    def _select_tool(self, sub_prompt: str) -> BaseTool | None:
        return next((t for t in self.tools if t.can_handle(sub_prompt)), None)

    def run(self, prompt: str) -> Task:
        task = Task.objects.create(prompt=prompt)
        step_num = 1

        def log(description, tool_name=None):
            nonlocal step_num
            ExecutionStep.objects.create(
                task=task, step_number=step_num, description=description, tool_name=tool_name
            )
            step_num += 1

        log(f'Received input "{prompt}"')

        sub_prompts = [p.strip() for p in prompt.split(" and ") if p.strip()]
        outputs = []
        for sub in sub_prompts:
            tool = self._select_tool(sub)
            if tool is None:
                log(f'No matching tool for: "{sub}"')
                outputs.append(f"(unhandled: {sub})")
                continue
            log(f"Selected tool: {tool.name}", tool_name=tool.name)
            try:
                result = tool.run(sub)
                log(f"Tool result: {result}", tool_name=tool.name)
                outputs.append(result)
            except ToolError as e:
                log(f"Tool error: {e}", tool_name=tool.name)
                outputs.append(f"(error: {e})")

        final_result = " | ".join(outputs)
        log("Returning result to user")

        task.result = final_result
        task.save(update_fields=["result"])
        return task
```

**Why not a fancier fallback/retry mechanism:** this satisfies basic retry/error-handling expectations at a reasonable level — errors are caught, logged as a visible trace step, and don't crash the request. A real retry-with-backoff loop would be over-engineering for tools that are pure functions with no transient failure modes to retry against.

## `serializers.py` / `views.py` / `urls.py`

`HyperlinkedModelSerializer` + `ModelViewSet` behind a `DefaultRouter` — every object carries a `url` to itself, and the endpoint set follows DRF's standard viewset conventions (including `PUT`/`PATCH`/`DELETE` on tasks) rather than a hand-rolled subset. `ExecutionStep` gets its own read-only viewset (`ReadOnlyModelViewSet`) purely so its `url` field has something to resolve to — steps are still only ever produced by `AgentController`, never client-authored. Exact request/response fields: [`docs/api.md`](../docs/api.md).

**Why the reversal from plain `APIView`s:** the original design avoided `ModelViewSet`/routers to keep the endpoint surface minimal (no unused verbs, no auto-pagination). That's a reasonable default, but hyperlinked, fully RESTful resources are the more idiomatic DRF shape and were requested explicitly — the trade-off (a larger verb surface on `/tasks/{id}/`, an extra `/steps/` resource) is accepted deliberately here rather than by accident.

```python
# serializers.py
from rest_framework import serializers
from .models import Task, ExecutionStep

class ExecutionStepSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ExecutionStep
        fields = ["url", "step_number", "description", "tool_name", "timestamp"]

class TaskSerializer(serializers.HyperlinkedModelSerializer):
    steps = ExecutionStepSerializer(many=True, read_only=True)
    class Meta:
        model = Task
        fields = ["url", "id", "prompt", "result", "created_at", "steps"]
        read_only_fields = ["result", "created_at"]

    def validate_prompt(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("This field may not be blank.")
        return value

class TaskListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Task
        fields = ["url", "id", "prompt", "result", "created_at"]  # no steps — keep list payload light
        read_only_fields = ["result", "created_at"]
```

```python
# views.py
from rest_framework import viewsets
from .models import Task, ExecutionStep
from .serializers import TaskSerializer, TaskListSerializer, ExecutionStepSerializer
from .agent import AgentController

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.order_by("-created_at")

    def get_serializer_class(self):
        return TaskListSerializer if self.action == "list" else TaskSerializer

    def perform_create(self, serializer):
        # Creation is agent-driven: AgentController creates the Task itself and
        # populates result/steps, so we run it here instead of serializer.save().
        task = AgentController().run(serializer.validated_data["prompt"])
        serializer.instance = task

class ExecutionStepViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExecutionStep.objects.select_related("task")
    serializer_class = ExecutionStepSerializer
```

```python
# urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, ExecutionStepViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet)
router.register(r"steps", ExecutionStepViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
```

Router basenames are left to auto-infer (`task`, `executionstep`) rather than being passed explicitly — `HyperlinkedModelSerializer`'s default `view_name` for a field is `"{model_name}-detail"`, and `DefaultRouter.get_default_basename` derives the same `{model_name}` from `queryset.model._meta.object_name.lower()`. Passing a custom `basename` (e.g. `"step"` for `/steps/`) would desync the two and break hyperlink resolution, so the URL prefix (`steps/`) and the basename (`executionstep`) are intentionally allowed to differ.

## Tests

Given Django fluency, this is cheap to write and worth doing early rather than as an afterthought.

```python
# tests/test_tools.py
from agent_api.tools import CalculatorTool, TextProcessorTool, WeatherMockTool, ToolError
import pytest

def test_calculator_basic():
    assert CalculatorTool().run("What is 15 + 27?") == "42"

def test_calculator_bad_input_raises():
    with pytest.raises(ToolError):
        CalculatorTool().run("what is the meaning of life")

def test_text_processor_uppercase():
    assert TextProcessorTool().run("convert 'hello world' to uppercase") == "HELLO WORLD"

def test_weather_known_city():
    assert "Toronto" in WeatherMockTool().run("weather in Toronto")
```

```python
# tests/test_agent.py — verifies routing + trace shape, not just tool output
from agent_api.agent import AgentController

def test_single_tool_trace_has_expected_steps(db):
    task = AgentController().run("Convert 'hi' to uppercase")
    descriptions = [s.description for s in task.steps.all()]
    assert descriptions[0].startswith("Received input")
    assert "TextProcessorTool" in descriptions[1]
    assert task.result == "HI"

def test_multi_step_chains_two_tools(db):
    task = AgentController().run("What is 2 + 2 and weather in Toronto")
    tool_names = [s.tool_name for s in task.steps.all() if s.tool_name]
    assert "CalculatorTool" in tool_names and "WeatherMockTool" in tool_names
```

`test_api.py` covers the two endpoints with Django's `APIClient` — 201 on valid POST, 400 on empty prompt, 404 on missing task ID.

## Build order

1. Models + tools + agent controller, exercised via Django shell/`manage.py test` before any HTTP layer exists.
2. `tests/test_tools.py` + `tests/test_agent.py`.
3. Serializers + views + urls; verify with `curl`/Postman against the shapes in [`docs/api.md`](../docs/api.md).
4. `tests/test_api.py`.
5. Multi-step prompt support in `agent.py` (already included above — verify it end-to-end).

Frontend build starts once step 3 is verified — see `frontend/IMPLEMENTATION.md`.
