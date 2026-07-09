"""Models module for the agent API."""
from django.db import models


class Task(models.Model):
    """Model representing a task executed by the agent API."""
    prompt = models.TextField(
        help_text="Natural-language instruction for the agent, e.g. \"What is 15 + 27?\"."
    )
    result = models.TextField(
        blank=True,
        default="",
        help_text="Agent's final output. Read-only — populated by tool execution, not set by the client.",
    )
    created_at = models.DateTimeField(auto_now_add=True)


class ExecutionStep(models.Model):
    """Model representing a single step in the execution of a task."""
    task = models.ForeignKey(Task, related_name="steps", on_delete=models.CASCADE)
    step_number = models.PositiveIntegerField(
        help_text="1-indexed position of this step within the task's execution trace."
    )
    description = models.CharField(
        max_length=255,
        help_text="Human-readable narration of this step, e.g. \"Selected tool: CalculatorTool\".",
    )
    tool_name = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="Tool that produced this step; null on bookkeeping steps (received input / returning result).",
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["step_number"]
