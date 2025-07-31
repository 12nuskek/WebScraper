from rest_framework import serializers
from django.shortcuts import get_object_or_404

from apps.scraper.models import Spider
from .models import Job


class JobSerializer(serializers.ModelSerializer):
    spider = serializers.PrimaryKeyRelatedField(
        queryset=Spider.objects.all()
    )
    duration = serializers.ReadOnlyField()

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