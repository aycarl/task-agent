from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .agent import AgentController
from .models import Task
from .serializers import TaskSerializer, TaskListSerializer


class TaskListCreateView(APIView):
    def get(self, request):
        tasks = Task.objects.order_by("-created_at")
        return Response(TaskListSerializer(tasks, many=True).data)

    def post(self, request):
        prompt = request.data.get("prompt", "").strip()
        if not prompt:
            return Response({"error": "prompt is required"}, status=status.HTTP_400_BAD_REQUEST)
        task = AgentController().run(prompt)
        return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)


class TaskDetailView(APIView):
    def get(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({"error": "not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(TaskSerializer(task).data)
