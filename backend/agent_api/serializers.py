"""Serializers for the agent_api app."""
from rest_framework import serializers

from agent_api.models import Task, ExecutionStep


class ExecutionStepSerializer(serializers.ModelSerializer):
    """Serializer for the ExecutionStep model. Nested only — steps have no endpoint of their own."""
    class Meta:
        model = ExecutionStep
        fields = ["step_number", "description", "tool_name", "timestamp"]


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for the Task model, including its execution steps."""
    steps = ExecutionStepSerializer(
        many=True, read_only=True, help_text="Ordered execution trace produced by the agent."
    )

    class Meta:
        model = Task
        fields = ["url", "id", "prompt", "result", "created_at", "steps"]
        read_only_fields = ["result", "created_at"]

    def validate_prompt(self, value):
        """Validate the prompt field."""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("This field may not be blank.")
        return value


class TaskListSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for listing Task model instances without execution steps."""

    class Meta:
        model = Task
        fields = ["url", "id", "prompt", "result", "created_at"]
        read_only_fields = ["result", "created_at"]
