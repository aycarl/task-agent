from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TaskViewSet, ExecutionStepViewSet, ApiDocsView

router = DefaultRouter()
router.register(r"tasks", TaskViewSet)
router.register(r"steps", ExecutionStepViewSet)

urlpatterns = [
    path("docs/", ApiDocsView.as_view(), name="api-docs"),
    path("", include(router.urls)),
]
