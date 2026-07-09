from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from rest_framework.renderers import JSONOpenAPIRenderer

from .views import TaskViewSet, ExecutionStepViewSet, ApiDocsView

router = DefaultRouter()
router.register(r"tasks", TaskViewSet)
router.register(r"steps", ExecutionStepViewSet)

# JSON-only renderer: avoids adding pyyaml as a dependency just for the
# equivalent YAML output. Auto-generated from the router/viewsets/serializers
# above, so it can't drift out of sync the way a hand-written file would.
schema_view = get_schema_view(
    title="Task Agent API",
    description=(
        "Rule-based task agent: submit a natural-language prompt, get back a "
        "result plus a step-by-step execution trace of which tool ran."
    ),
    version="1.0.0",
    renderer_classes=[JSONOpenAPIRenderer],
)

urlpatterns = [
    path("openapi.json", schema_view, name="openapi-schema"),
    path("docs/", ApiDocsView.as_view(), name="api-docs"),
    path("", include(router.urls)),
]
