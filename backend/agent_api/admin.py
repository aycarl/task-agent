from django.contrib import admin

from agent_api.models import Task, ExecutionStep

admin.site.register(Task)
admin.site.register(ExecutionStep)
