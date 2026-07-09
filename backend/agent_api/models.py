"""Models module for the agent API."""
from django.db import models


class Task(models.Model):
    """Model representing a task executed by the agent API."""
    prompt = models.TextField()
    result = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)


class ExecutionStep(models.Model):
    """Model representing a single step in the execution of a task."""
    task = models.ForeignKey(Task, related_name="steps", on_delete=models.CASCADE)
    step_number = models.PositiveIntegerField()
    description = models.CharField(max_length=255)
    tool_name = models.CharField(max_length=64, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["step_number"]
