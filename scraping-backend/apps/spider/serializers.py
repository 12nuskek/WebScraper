from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema_field, extend_schema_serializer, OpenApiExample
from drf_spectacular.openapi import OpenApiTypes

from apps.projects.models import Project
from .models import Spider


class SpiderSettingsSerializer(serializers.Serializer):
    """Serializer for structured spider settings."""
    
    block_images = serializers.BooleanField(required=False)
    block_images_and_css = serializers.BooleanField(required=False)
    tiny_profile = serializers.BooleanField(required=False)
    profile = serializers.CharField(required=False, allow_blank=True)
    user_agent = serializers.CharField(required=False, allow_blank=True)
    window_size = serializers.CharField(required=False, allow_blank=True)
    headless = serializers.BooleanField(required=False)
    wait_for_complete_page_load = serializers.BooleanField(required=False)
    reuse_driver = serializers.BooleanField(required=False)
    max_retry = serializers.IntegerField(required=False, min_value=0)
    parallel = serializers.IntegerField(required=False, min_value=1)
    cache = serializers.BooleanField(required=False)


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Full Settings Spider",
            summary="Full Settings Spider", 
            description="A spider with all available settings",
            value={
                "project": 1,
                "name": "full-spider",
                "start_urls_json": ["https://example.com"],
                "settings_json": {
                    "block_images": True,
                    "block_images_and_css": False,
                    "tiny_profile": True,
                    "profile": "mobile",
                    "user_agent": "Mozilla/5.0 Custom Bot",
                    "window_size": "1920x1080",
                    "headless": True,
                    "wait_for_complete_page_load": False,
                    "reuse_driver": True,
                    "max_retry": 5,
                    "parallel": 4,
                    "cache": True
                },
                "parse_rules_json": {"title": "h1", "links": "a[href]"}
            }
        ),
        OpenApiExample(
            "Basic Spider",
            summary="Basic Spider",
            description="A spider with minimal settings",
            value={
                "project": 1,
                "name": "example-spider",
                "start_urls_json": ["https://example.com"],
                "settings_json": {
                    "headless": True,
                    "max_retry": 3
                },
                "parse_rules_json": {"title": "h1"}
            }
        )
    ]
)
class SpiderSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all()
    )
    
    settings_json = serializers.JSONField(
        required=False, 
        allow_null=True,
        help_text="Spider settings object with optional boolean, string, and integer fields for browser behavior configuration"
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
    
    def validate_settings_json(self, value):
        """Validate settings JSON structure."""
        if value is not None:
            if not isinstance(value, dict):
                raise ValidationError("Settings must be a valid JSON object.")
            
            # Validate using the SpiderSettingsSerializer
            settings_serializer = SpiderSettingsSerializer(data=value)
            if not settings_serializer.is_valid():
                raise ValidationError(f"Invalid settings structure: {settings_serializer.errors}")
        
        return value