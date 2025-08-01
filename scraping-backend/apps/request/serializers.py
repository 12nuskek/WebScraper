import base64
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema_field

from apps.job.models import Job
from .models import RequestQueue


class RequestQueueSerializer(serializers.ModelSerializer):
    job = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.all()
    )
    can_retry = serializers.SerializerMethodField()
    # Custom field for handling base64 encoded binary data
    body_blob = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    
    class Meta:
        model = RequestQueue
        fields = (
            "id",
            "job",
            "url",
            "method",
            "headers_json",
            "body_blob",
            "priority",
            "depth",
            "retries",
            "max_retries",
            "fingerprint",
            "scheduled_at",
            "picked_at",
            "status",
            "created_at",
            "updated_at",
            "can_retry",
        )
        read_only_fields = (
            "id", 
            "fingerprint", 
            "created_at", 
            "updated_at", 
            "can_retry"
        )
        
    @extend_schema_field(serializers.BooleanField())
    def get_can_retry(self, obj):
        """Check if request can be retried."""
        return obj.can_retry
        
    def to_representation(self, instance):
        """Custom serialization to handle binary data."""
        data = super().to_representation(instance)
        # Convert binary data to base64 for JSON serialization
        if instance.body_blob:
            data['body_blob'] = base64.b64encode(instance.body_blob).decode('utf-8')
        else:
            data['body_blob'] = None
        return data
        
    def validate_job(self, value):
        """Ensure the user can only create requests for their own jobs."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if value.spider.project.owner != request.user:
                raise serializers.ValidationError(
                    "You can only create requests for your own jobs."
                )
        return value
        
    def validate_url(self, value):
        """Validate URL format."""
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError(
                "URL must start with http:// or https://"
            )
        return value
        
    def validate_priority(self, value):
        """Validate priority range."""
        if value < -100 or value > 100:
            raise serializers.ValidationError(
                "Priority must be between -100 and 100"
            )
        return value
        
    def validate_max_retries(self, value):
        """Validate max retries."""
        if value < 0 or value > 10:
            raise serializers.ValidationError(
                "Max retries must be between 0 and 10"
            )
        return value
        
    def validate_body_blob(self, value):
        """Validate and convert base64 body_blob to binary."""
        if value:
            try:
                # Convert base64 string to binary data
                return base64.b64decode(value)
            except Exception as e:
                raise serializers.ValidationError(f'Invalid base64 data: {str(e)}')
        return value
        
    def create(self, validated_data):
        """Create a new RequestQueue instance."""
        return super().create(validated_data)
        
    def update(self, instance, validated_data):
        """Update a RequestQueue instance."""
        return super().update(instance, validated_data)