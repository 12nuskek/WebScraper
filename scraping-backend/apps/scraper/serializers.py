from rest_framework import serializers
from django.shortcuts import get_object_or_404

from apps.projects.models import Project
from .models import Spider


class SpiderSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all()
    )

    class Meta:
        model = Spider
        fields = (
            "id",
            "project", 
            "name",
            "start_urls_json",
            "settings_json",
            "parse_rules_json",
            "created_at",
        )
        read_only_fields = ("id", "created_at")