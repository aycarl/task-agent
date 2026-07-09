from django.views.generic import TemplateView
from rest_framework import mixins, viewsets
from rest_framework.schemas.openapi import AutoSchema

from agent_api.agent import AgentController
from agent_api.models import Task
from agent_api.serializers import TaskSerializer, TaskListSerializer


class HomeView(TemplateView):
    template_name = "agent_api/home.html"


class TaskViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """A submitted prompt, its agent-produced result, and its execution trace.

    Only list/create/retrieve are exposed — the frontend never edits or
    deletes a task, so there's no update/destroy surface to maintain.
    """

    queryset = Task.objects.order_by("-created_at")
    schema = AutoSchema(tags=["tasks"])

    def get_serializer_class(self):
        return TaskListSerializer if self.action == "list" else TaskSerializer

    def perform_create(self, serializer):
        # Task creation is agent-driven, not a plain model save: the prompt is routed
        # through AgentController, which creates the Task itself and populates
        # result/steps. So we run the agent here and swap it in as the instance,
        # instead of letting serializer.save() persist the validated data directly.
        task = AgentController().run(serializer.validated_data["prompt"])
        serializer.instance = task

    def list(self, request, *args, **kwargs):
        """List past tasks, most recent first. Lighter payload — no execution steps."""
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Submit a prompt. Routed through the agent — result/steps come from tool execution, not the request body."""
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Fetch one task with its full execution trace."""
        return super().retrieve(request, *args, **kwargs)
