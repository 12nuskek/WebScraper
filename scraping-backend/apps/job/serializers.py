from rest_framework import serializers
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema_field

from apps.spider.models import Spider
from .models import Job


class JobSerializer(serializers.ModelSerializer):
    spider = serializers.PrimaryKeyRelatedField(
        queryset=Spider.objects.all()
    )
    duration = serializers.SerializerMethodField()  # Include the calculated duration

    class Meta:
        model = Job
        fields = (
            "id",
            "spider",
            "status",
            "started_at",
            "finished_at",
            "stats_json",
            "created_at",
            "duration",
        )
        read_only_fields = ("id", "created_at", "duration")
        
    @extend_schema_field(serializers.FloatField(allow_null=True))
    def get_duration(self, obj):
        """Get job duration in seconds."""
        return obj.duration
        
    def validate_spider(self, value):
        """Ensure the user can only create jobs for their own spiders."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if value.project.owner != request.user:
                raise serializers.ValidationError(
                    "You can only create jobs for your own spiders."
                )
        return value