from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
import zoneinfo

from apps.spider.models import Spider
from .models import Schedule


class ScheduleSerializer(serializers.ModelSerializer):
    spider = serializers.PrimaryKeyRelatedField(
        queryset=Spider.objects.all()
    )
    time_until_next_run = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    is_due = serializers.SerializerMethodField()
    
    class Meta:
        model = Schedule
        fields = (
            "id",
            "spider",
            "cron_expr",
            "timezone",
            "enabled",
            "next_run_at",
            "created_at",
            "updated_at",
            "time_until_next_run",
            "is_overdue",
            "is_due",
        )
        read_only_fields = (
            "id",
            "next_run_at",
            "created_at",
            "updated_at",
            "time_until_next_run",
            "is_overdue",
            "is_due",
        )
        
    @extend_schema_field(serializers.FloatField(allow_null=True))
    def get_time_until_next_run(self, obj):
        """Get seconds until next run."""
        td = obj.time_until_next_run
        return td.total_seconds() if td is not None else None
        
    @extend_schema_field(serializers.BooleanField())
    def get_is_overdue(self, obj):
        """Check if schedule is overdue."""
        return obj.is_overdue
        
    @extend_schema_field(serializers.BooleanField())
    def get_is_due(self, obj):
        """Check if schedule is currently due."""
        return obj.is_due()
        
    def validate_spider(self, value):
        """Ensure the user can only create schedules for their own spiders."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if value.project.owner != request.user:
                raise serializers.ValidationError(
                    "You can only create schedules for your own spiders."
                )
        return value
        
    def validate_cron_expr(self, value):
        """Validate cron expression format."""
        if not Schedule.is_valid_cron_expression(value):
            raise serializers.ValidationError(
                "Invalid cron expression. Use format: 'minute hour day month weekday' "
                "(e.g., '0 */6 * * *' for every 6 hours)"
            )
        return value.strip()
        
    def validate_timezone(self, value):
        """Validate timezone."""
        try:
            zoneinfo.ZoneInfo(value)
            return value
        except zoneinfo.ZoneInfoNotFoundError:
            raise serializers.ValidationError(f"Unknown timezone: {value}")
            
    def create(self, validated_data):
        """Create schedule and calculate initial next_run_at."""
        schedule = super().create(validated_data)
        if schedule.enabled:
            schedule.calculate_next_run()
            schedule.save(update_fields=['next_run_at'])
        return schedule
        
    def update(self, instance, validated_data):
        """Update schedule and recalculate next_run_at if needed."""
        # Check if cron_expr, timezone, or enabled status changed
        cron_changed = 'cron_expr' in validated_data and validated_data['cron_expr'] != instance.cron_expr
        timezone_changed = 'timezone' in validated_data and validated_data['timezone'] != instance.timezone
        enabled_changed = 'enabled' in validated_data and validated_data['enabled'] != instance.enabled
        
        instance = super().update(instance, validated_data)
        
        if cron_changed or timezone_changed or enabled_changed:
            instance.calculate_next_run()
            instance.save(update_fields=['next_run_at'])
            
        return instance


class ScheduleStatsSerializer(serializers.Serializer):
    """Serializer for schedule statistics."""
    total_schedules = serializers.IntegerField(read_only=True)
    enabled_schedules = serializers.IntegerField(read_only=True)
    disabled_schedules = serializers.IntegerField(read_only=True)
    due_schedules = serializers.IntegerField(read_only=True)
    overdue_schedules = serializers.IntegerField(read_only=True)
    upcoming_24h = serializers.IntegerField(read_only=True)
    timezone_distribution = serializers.DictField(read_only=True)


class CronExpressionHelpSerializer(serializers.Serializer):
    """Serializer for cron expression help and examples."""
    examples = serializers.DictField(read_only=True)
    fields = serializers.DictField(read_only=True)
    special_characters = serializers.DictField(read_only=True)
    common_patterns = serializers.DictField(read_only=True)