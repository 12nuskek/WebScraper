from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "spider", "status", "created_at", "started_at", "finished_at")
    list_filter = ("status", "created_at", "spider__project")
    search_fields = ("spider__name", "spider__project__name")
    readonly_fields = ("created_at", "duration")
    raw_id_fields = ("spider",)
    
    fieldsets = (
        (None, {
            'fields': ('spider', 'status')
        }),
        ('Timing', {
            'fields': ('created_at', 'started_at', 'finished_at', 'duration')
        }),
        ('Statistics', {
            'fields': ('stats_json',),
            'classes': ('collapse',)
        }),
    )
    
    def duration(self, obj):
        """Display job duration in admin."""
        duration = obj.duration
        if duration is not None:
            return f"{duration:.2f} seconds"
        return "-"
    duration.short_description = "Duration"