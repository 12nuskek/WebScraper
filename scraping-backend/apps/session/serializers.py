from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from .models import Session


class SessionSerializer(serializers.ModelSerializer):
    """Serializer for Session model."""
    
    is_expired = serializers.SerializerMethodField()
    is_valid = serializers.SerializerMethodField()
    spider_name = serializers.CharField(source='spider.name', read_only=True)
    
    class Meta:
        model = Session
        fields = [
            'id',
            'spider',
            'spider_name',
            'label',
            'cookies_json',
            'headers_json',
            'valid_until',
            'is_expired',
            'is_valid',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    @extend_schema_field(serializers.BooleanField())
    def get_is_expired(self, obj):
        """Get whether session is expired."""
        return obj.is_expired
        
    @extend_schema_field(serializers.BooleanField())
    def get_is_valid(self, obj):
        """Get whether session is valid."""
        return obj.is_valid
        
    def validate(self, data):
        """Validate session data."""
        spider = data.get('spider')
        label = data.get('label')
        
        # Check for duplicate spider + label combination (excluding current instance)
        queryset = Session.objects.filter(spider=spider, label=label)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
            
        if queryset.exists():
            raise ValidationError({
                'label': f'Session with label "{label}" already exists for this spider.'
            })
            
        return data
        
    def validate_valid_until(self, value):
        """Validate that valid_until is in the future."""
        if value and value <= timezone.now():
            raise ValidationError("Session expiry must be in the future.")
        return value


class SessionCreateSerializer(SessionSerializer):
    """Serializer for creating sessions with extended validation."""
    
    class Meta(SessionSerializer.Meta):
        fields = SessionSerializer.Meta.fields
        
    def validate_cookies_json(self, value):
        """Validate cookies JSON structure."""
        if value is not None:
            if not isinstance(value, dict):
                raise ValidationError("Cookies must be a valid JSON object.")
        return value
        
    def validate_headers_json(self, value):
        """Validate headers JSON structure."""
        if value is not None:
            if not isinstance(value, dict):
                raise ValidationError("Headers must be a valid JSON object.")
        return value


class SessionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for session lists."""
    
    is_expired = serializers.SerializerMethodField()
    spider_name = serializers.CharField(source='spider.name', read_only=True)
    
    class Meta:
        model = Session
        fields = [
            'id',
            'spider',
            'spider_name',
            'label',
            'valid_until',
            'is_expired',
            'updated_at',
        ]
        
    @extend_schema_field(serializers.BooleanField())
    def get_is_expired(self, obj):
        """Get whether session is expired."""
        return obj.is_expired


class SessionExtendValiditySerializer(serializers.Serializer):
    """Serializer for extending session validity."""
    
    hours = serializers.IntegerField(
        min_value=1,
        max_value=8760,  # 1 year
        default=24,
        help_text="Number of hours to extend validity by"
    )