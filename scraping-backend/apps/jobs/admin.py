from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "spider", "status", "started_at", "finished_at", "created_at")
    list_filter = ("status", "spider__project", "created_at")
    search_fields = ("spider__name", "spider__project__name")
    readonly_fields = ("created_at", "duration")
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('spider', 'spider__project')