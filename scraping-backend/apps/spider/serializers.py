import json
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema_field, extend_schema_serializer, OpenApiExample
from drf_spectacular.openapi import OpenApiTypes
from django.db import IntegrityError

from apps.projects.models import Project
from .models import Spider


class SpiderSettingsSerializer(serializers.Serializer):
    """Serializer for structured spider settings (legacy/internal)."""
    
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


class SpiderBlockSerializer(serializers.Serializer):
    Id = serializers.CharField(required=False, allow_blank=True)
    Name = serializers.CharField()
    Description = serializers.CharField(required=False, allow_blank=True)
    Category = serializers.CharField(required=False, allow_blank=True)
    Project = serializers.IntegerField()
    Status = serializers.CharField(required=False, allow_blank=True)
    Priority = serializers.CharField(required=False, allow_blank=True)


class TargetBlockSerializer(serializers.Serializer):
    URL = serializers.CharField()
    Scan_Sitemap = serializers.BooleanField(required=False, default=False)
    Autodetect = serializers.BooleanField(required=False, default=False)
    Sitemap_URL = serializers.CharField(required=False, allow_blank=True)
    Datascope = serializers.CharField(required=False, allow_blank=True)
    Tags = serializers.ListField(child=serializers.CharField(), required=False, default=list)


class ProxyBlockSerializer(serializers.Serializer):
    Enabled = serializers.BooleanField(required=False)
    URL = serializers.CharField(required=False, allow_blank=True)


class ExecutionBlockSerializer(serializers.Serializer):
    Method = serializers.CharField(required=False, allow_blank=True)
    Headless_Mode = serializers.BooleanField(required=False)
    Block_Images = serializers.BooleanField(required=False)
    User_Agent = serializers.CharField(required=False, allow_blank=True)
    Window_Size = serializers.CharField(required=False, allow_blank=True)
    Profile_Name = serializers.CharField(required=False, allow_blank=True)
    Parallel_Instances = serializers.IntegerField(required=False, min_value=1)
    Proxy = ProxyBlockSerializer(required=False)


class OutputBlockSerializer(serializers.Serializer):
    Filename = serializers.CharField(required=False, allow_blank=True)
    Formats = serializers.ListField(child=serializers.CharField(), required=False, default=list)


class RetryPolicyBlockSerializer(serializers.Serializer):
    Max_Retries = serializers.IntegerField(required=False, min_value=0)
    Retry_Wait = serializers.IntegerField(required=False, min_value=0)
    Close_on_Crash = serializers.BooleanField(required=False)
    Error_Logging = serializers.BooleanField(required=False)
    Result_Caching = serializers.BooleanField(required=False)


class AdvancedBlockSerializer(serializers.Serializer):
    Wait_For_Complete_Page_Load = serializers.BooleanField(required=False)
    Reuse_Driver = serializers.BooleanField(required=False)


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Nested Spider Payload",
            summary="Create or update a spider with nested configuration",
            description="Payload with nested sections for Spider metadata, target, execution, output, retry policy, and advanced options",
            value={
                "Spider": {
                    "Id": "full-spider",
                    "Name": "Full Spider Job",
                    "Description": "",
                    "Category": "",
                    "Project": 1,
                    "Status": "In Progress",
                    "Priority": ""
                },
                "Target": {
                    "URL": "https://example.com",
                    "Scan_Sitemap": False,
                    "Autodetect": False,
                    "Sitemap_URL": "",
                    "Datascope": "",
                    "Tags": []
                },
                "Execution": {
                    "Method": "",
                    "Headless_Mode": True,
                    "Block_Images": True,
                    "User_Agent": "Mozilla/5.0 Custom Bot",
                    "Window_Size": "1920x1080",
                    "Profile_Name": "mobile",
                    "Parallel_Instances": 4,
                    "Proxy": {
                        "Enabled": False,
                        "URL": ""
                    }
                },
                "Output": {
                    "Filename": "output",
                    "Formats": ["json", "csv"]
                },
                "RetryPolicy": {
                    "Max_Retries": 5,
                    "Retry_Wait": 10,
                    "Close_on_Crash": True,
                    "Error_Logging": True,
                    "Result_Caching": True
                },
                "Advanced": {
                    "Wait_For_Complete_Page_Load": False,
                    "Reuse_Driver": True
                }
            }
        )
    ]
)
class SpiderSerializer(serializers.Serializer):
    Spider = SpiderBlockSerializer()
    Target = TargetBlockSerializer()
    Execution = ExecutionBlockSerializer()
    Output = OutputBlockSerializer(required=False)
    RetryPolicy = RetryPolicyBlockSerializer(required=False)
    Advanced = AdvancedBlockSerializer(required=False)

    def validate(self, attrs):
        spider_block = attrs.get("Spider", {}) or {}
        project_id = spider_block.get("Project")
        name = spider_block.get("Name")

        # Validate uniqueness within (project, name)
        if project_id and name:
            qs = Spider.objects.filter(project_id=project_id, name=name)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError({
                    "Spider": {
                        "Name": ["A spider with this name already exists in this project."]
                    }
                })
        return attrs

    def _build_settings_from_blocks(self, execution, retry_policy, advanced):
        settings = {
            "block_images": execution.get("Block_Images"),
            "profile": execution.get("Profile_Name"),
            "user_agent": execution.get("User_Agent"),
            "window_size": execution.get("Window_Size"),
            "headless": execution.get("Headless_Mode"),
            "wait_for_complete_page_load": (advanced or {}).get("Wait_For_Complete_Page_Load") if advanced else None,
            "reuse_driver": (advanced or {}).get("Reuse_Driver") if advanced else None,
            "max_retry": (retry_policy or {}).get("Max_Retries") if retry_policy else None,
            "parallel": execution.get("Parallel_Instances"),
            "cache": (retry_policy or {}).get("Result_Caching") if retry_policy else None,
        }
        # Drop None values
        return {k: v for k, v in settings.items() if v is not None}

    def create(self, validated_data):
        spider_block = validated_data.get("Spider", {})
        target_block = validated_data.get("Target", {})
        execution_block = validated_data.get("Execution", {})
        output_block = validated_data.get("Output") or {}
        retry_block = validated_data.get("RetryPolicy") or {}
        advanced_block = validated_data.get("Advanced") or {}

        # Prefer project injected by the view (permission-checked); fallback to payload
        project_obj = validated_data.get("project")
        project_id = project_obj.id if project_obj is not None else spider_block["Project"]
        name = spider_block["Name"]
        start_url = target_block.get("URL")
        start_urls_json = [start_url] if start_url else []

        settings_json = self._build_settings_from_blocks(execution_block, retry_block, advanced_block)

        try:
            instance = Spider.objects.create(
                project_id=project_id,
                name=name,
                external_id=spider_block.get("Id"),
                description=spider_block.get("Description", ""),
                category=spider_block.get("Category", ""),
                status=spider_block.get("Status", ""),
                priority=spider_block.get("Priority", ""),
                start_urls_json=start_urls_json,
                settings_json=settings_json or None,
                parse_rules_json=None,
                target_json=target_block or None,
                execution_json=execution_block or None,
                output_json=output_block or None,
                retry_policy_json=retry_block or None,
                advanced_json=advanced_block or None,
            )
        except IntegrityError:
            # Safety net for race conditions
            raise ValidationError({
                "Spider": {
                    "Name": ["A spider with this name already exists in this project."]
                }
            })
        return instance

    def update(self, instance, validated_data):
        spider_block = validated_data.get("Spider", {})
        target_block = validated_data.get("Target", {})
        execution_block = validated_data.get("Execution", {})
        output_block = validated_data.get("Output") or {}
        retry_block = validated_data.get("RetryPolicy") or {}
        advanced_block = validated_data.get("Advanced") or {}

        if "Project" in spider_block:
            instance.project_id = spider_block["Project"]
        if "Name" in spider_block:
            instance.name = spider_block["Name"]
        instance.external_id = spider_block.get("Id", instance.external_id)
        instance.description = spider_block.get("Description", instance.description)
        instance.category = spider_block.get("Category", instance.category)
        instance.status = spider_block.get("Status", instance.status)
        instance.priority = spider_block.get("Priority", instance.priority)

        if target_block:
            start_url = target_block.get("URL")
            if start_url:
                instance.start_urls_json = [start_url]
            instance.target_json = target_block or instance.target_json

        if execution_block:
            instance.execution_json = execution_block

        if output_block:
            instance.output_json = output_block

        if retry_block:
            instance.retry_policy_json = retry_block

        if advanced_block:
            instance.advanced_json = advanced_block

        settings_json = self._build_settings_from_blocks(execution_block or {}, retry_block or {}, advanced_block or {})
        if settings_json:
            # Merge with existing settings to avoid dropping unrelated keys
            merged = dict(instance.settings_json or {})
            merged.update(settings_json)
            instance.settings_json = merged

        instance.save()
        return instance

    def to_representation(self, instance):
        # Helper to coerce stored JSON fields into dicts
        def _coerce_dict(value):
            if isinstance(value, dict) or value is None:
                return value or {}
            if isinstance(value, str):
                try:
                    parsed = json.loads(value)
                    return parsed if isinstance(parsed, dict) else {}
                except Exception:
                    return {}
            return {}

        # Base values from stored JSON blocks, coerced to dicts
        target = _coerce_dict(instance.target_json)
        execution = _coerce_dict(instance.execution_json)
        output = _coerce_dict(instance.output_json)
        retry = _coerce_dict(instance.retry_policy_json)
        advanced = _coerce_dict(instance.advanced_json)

        # Backfill from primitive fields if missing
        if instance.start_urls_json and not target.get("URL"):
            target = dict(target)
            target["URL"] = instance.start_urls_json[0]

        # Derive missing execution/advanced/retry values from settings_json for compatibility
        settings = _coerce_dict(instance.settings_json)
        execution = {
            **({} if not execution else execution),
            **{k: v for k, v in {
                "Block_Images": settings.get("block_images"),
                "User_Agent": settings.get("user_agent"),
                "Window_Size": settings.get("window_size"),
                "Profile_Name": settings.get("profile"),
                "Headless_Mode": settings.get("headless"),
                "Parallel_Instances": settings.get("parallel"),
            }.items() if v is not None}
        }

        advanced = {
            **({} if not advanced else advanced),
            **{k: v for k, v in {
                "Wait_For_Complete_Page_Load": settings.get("wait_for_complete_page_load"),
                "Reuse_Driver": settings.get("reuse_driver"),
            }.items() if v is not None}
        }

        retry = {
            **({} if not retry else retry),
            **{k: v for k, v in {
                "Max_Retries": settings.get("max_retry"),
                "Result_Caching": settings.get("cache"),
            }.items() if v is not None}
        }

        return {
            "Spider": {
                "Pk": instance.id,
                "Id": instance.external_id or "",
                "Name": instance.name,
                "Description": instance.description or "",
                "Category": instance.category or "",
                "Project": instance.project_id,
                "Status": instance.status or "",
                "Priority": instance.priority or "",
            },
            "Target": target,
            "Execution": execution,
            "Output": output,
            "RetryPolicy": retry,
            "Advanced": advanced,
        }