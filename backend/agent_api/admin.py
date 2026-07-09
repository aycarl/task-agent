from django.contrib import admin

from .models import Task, ExecutionStep

admin.site.register(Task)
admin.site.register(ExecutionStep)
