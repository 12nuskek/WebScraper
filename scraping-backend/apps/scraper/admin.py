from django.contrib import admin
from .models import Spider


@admin.register(Spider)
class SpiderAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "created_at")
    search_fields = ("name",)
    list_filter = ("project",)