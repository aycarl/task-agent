from rest_framework import serializers

from .models import Task, ExecutionStep


class ExecutionStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExecutionStep
        fields = ["step_number", "description", "tool_name", "timestamp"]


class TaskSerializer(serializers.ModelSerializer):
    steps = ExecutionStepSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ["id", "prompt", "result", "created_at", "steps"]


class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "prompt", "result", "created_at"]
