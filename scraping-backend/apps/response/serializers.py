from rest_framework import serializers
from django.shortcuts import get_object_or_404

from apps.request.models import RequestQueue
from .models import Response


class ResponseSerializer(serializers.ModelSerializer):
    request = serializers.PrimaryKeyRelatedField(
        queryset=RequestQueue.objects.all()
    )
    is_success = serializers.ReadOnlyField()
    is_redirect = serializers.ReadOnlyField()
    is_client_error = serializers.ReadOnlyField()
    is_server_error = serializers.ReadOnlyField()
    body_size = serializers.ReadOnlyField()
    
    class Meta:
        model = Response
        fields = (
            "id",
            "request",
            "final_url",
            "status_code",
            "headers_json",
            "fetched_at",
            "latency_ms",
            "from_cache",
            "body_path",
            "content_hash",
            "created_at",
            "updated_at",
            "is_success",
            "is_redirect",
            "is_client_error",
            "is_server_error",
            "body_size",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "is_success",
            "is_redirect", 
            "is_client_error",
            "is_server_error",
            "body_size",
        )
        
    def validate_request(self, value):
        """Ensure the user can only create responses for their own requests."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if value.job.spider.project.owner != request.user:
                raise serializers.ValidationError(
                    "You can only create responses for your own requests."
                )
        return value
        
    def validate_status_code(self, value):
        """Validate HTTP status code range."""
        if value is not None and (value < 100 or value > 599):
            raise serializers.ValidationError(
                "Status code must be between 100 and 599"
            )
        return value
        
    def validate_latency_ms(self, value):
        """Validate latency is non-negative."""
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Latency cannot be negative"
            )
        return value
        
    def validate_final_url(self, value):
        """Validate final URL format if provided."""
        if value and not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError(
                "Final URL must start with http:// or https://"
            )
        return value


class ResponseBodySerializer(serializers.Serializer):
    """Serializer for response body content (separate endpoint)."""
    body = serializers.CharField(read_only=True)
    content_type = serializers.CharField(read_only=True)
    encoding = serializers.CharField(read_only=True)
    size = serializers.IntegerField(read_only=True)


class ResponseStatsSerializer(serializers.Serializer):
    """Serializer for response statistics."""
    total_responses = serializers.IntegerField(read_only=True)
    successful_responses = serializers.IntegerField(read_only=True)
    error_responses = serializers.IntegerField(read_only=True)
    avg_latency_ms = serializers.FloatField(read_only=True)
    status_code_distribution = serializers.DictField(read_only=True)
    cache_hit_rate = serializers.FloatField(read_only=True)