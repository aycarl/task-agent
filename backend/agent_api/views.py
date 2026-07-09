from django.views.generic import TemplateView
from rest_framework import viewsets

from agent_api.agent import AgentController
from agent_api.models import Task, ExecutionStep
from agent_api.serializers import TaskSerializer, TaskListSerializer, ExecutionStepSerializer


class HomeView(TemplateView):
    template_name = "agent_api/home.html"


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.order_by("-created_at")

    def get_serializer_class(self):
        return TaskListSerializer if self.action == "list" else TaskSerializer

    def perform_create(self, serializer):
        # Task creation is agent-driven, not a plain model save: the prompt is routed
        # through AgentController, which creates the Task itself and populates
        # result/steps. So we run the agent here and swap it in as the instance,
        # instead of letting serializer.save() persist the validated data directly.
        task = AgentController().run(serializer.validated_data["prompt"])
        serializer.instance = task


class ExecutionStepViewSet(viewsets.ReadOnlyModelViewSet):
    # Steps are only ever produced by AgentController — no client-initiated
    # create/update/delete, so this stays read-only.
    queryset = ExecutionStep.objects.select_related("task")
    serializer_class = ExecutionStepSerializer
