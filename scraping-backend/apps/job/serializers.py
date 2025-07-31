from rest_framework import serializers
from django.shortcuts import get_object_or_404

from apps.spider.models import Spider
from .models import Job


class JobSerializer(serializers.ModelSerializer):
    spider = serializers.PrimaryKeyRelatedField(
        queryset=Spider.objects.all()
    )
    duration = serializers.ReadOnlyField()  # Include the calculated duration

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
        
    def validate_spider(self, value):
        """Ensure the user can only create jobs for their own spiders."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if value.project.owner != request.user:
                raise serializers.ValidationError(
                    "You can only create jobs for your own spiders."
                )
        return value