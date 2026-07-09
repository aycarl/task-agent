"""Serializers for the agent_api app."""
from rest_framework import serializers

from agent_api.models import Task, ExecutionStep


class ExecutionStepSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for the ExecutionStep model."""
    class Meta:
        model = ExecutionStep
        fields = ["url", "step_number", "description", "tool_name", "timestamp"]


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for the Task model, including its execution steps."""
    steps = ExecutionStepSerializer(many=True, read_only=True)

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
