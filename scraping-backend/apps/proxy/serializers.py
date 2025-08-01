from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from .models import Proxy


class ProxySerializer(serializers.ModelSerializer):
    """Serializer for Proxy model."""
    
    masked_uri = serializers.CharField(read_only=True)
    hostname = serializers.CharField(read_only=True)
    port = serializers.IntegerField(read_only=True)
    scheme = serializers.CharField(read_only=True)
    is_healthy = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Proxy
        fields = [
            'id',
            'uri',
            'masked_uri',
            'hostname',
            'port',
            'scheme',
            'is_active',
            'last_ok_at',
            'fail_count',
            'is_healthy',
            'success_rate',
            'meta_json',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    @extend_schema_field(serializers.BooleanField())
    def get_is_healthy(self, obj):
        """Get whether proxy is healthy."""
        return obj.is_healthy
        
    @extend_schema_field(serializers.FloatField(allow_null=True))
    def get_success_rate(self, obj):
        """Get proxy success rate."""
        return obj.success_rate
        
    def validate_uri(self, value):
        """Validate proxy URI format."""
        if not value:
            raise ValidationError("Proxy URI is required.")
            
        # Create a temporary instance to use the model's clean method
        temp_proxy = Proxy(uri=value)
        try:
            temp_proxy.clean()
        except ValidationError as e:
            raise ValidationError(e.message_dict.get('uri', ['Invalid URI format.'])[0])
            
        return value


class ProxyCreateSerializer(ProxySerializer):
    """Serializer for creating proxies with additional validation."""
    
    class Meta(ProxySerializer.Meta):
        fields = ProxySerializer.Meta.fields
        
    def validate(self, data):
        """Validate proxy data."""
        # Check for duplicate URI (excluding current instance)
        uri = data.get('uri')
        if uri:
            queryset = Proxy.objects.filter(uri=uri)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
                
            if queryset.exists():
                raise ValidationError({
                    'uri': 'A proxy with this URI already exists.'
                })
                
        return data


class ProxyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for proxy lists."""
    
    masked_uri = serializers.CharField(read_only=True)
    is_healthy = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Proxy
        fields = [
            'id',
            'masked_uri',
            'is_active',
            'last_ok_at',
            'fail_count',
            'is_healthy',
            'success_rate',
            'updated_at',
        ]
        
    @extend_schema_field(serializers.BooleanField())
    def get_is_healthy(self, obj):
        """Get whether proxy is healthy."""
        return obj.is_healthy
        
    @extend_schema_field(serializers.FloatField(allow_null=True))
    def get_success_rate(self, obj):
        """Get proxy success rate."""
        return obj.success_rate


class ProxyStatsSerializer(serializers.ModelSerializer):
    """Serializer for proxy statistics."""
    
    masked_uri = serializers.CharField(read_only=True)
    is_healthy = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()
    total_attempts = serializers.SerializerMethodField()
    successful_attempts = serializers.SerializerMethodField()
    last_success_at = serializers.SerializerMethodField()
    last_failure_at = serializers.SerializerMethodField()
    last_error = serializers.SerializerMethodField()
    
    class Meta:
        model = Proxy
        fields = [
            'id',
            'masked_uri',
            'is_active',
            'last_ok_at',
            'fail_count',
            'is_healthy',
            'success_rate',
            'total_attempts',
            'successful_attempts',
            'last_success_at',
            'last_failure_at',
            'last_error',
        ]
        
    @extend_schema_field(serializers.BooleanField())
    def get_is_healthy(self, obj):
        """Get whether proxy is healthy."""
        return obj.is_healthy
        
    @extend_schema_field(serializers.FloatField(allow_null=True))
    def get_success_rate(self, obj):
        """Get proxy success rate."""
        return obj.success_rate
        
    @extend_schema_field(serializers.IntegerField())
    def get_total_attempts(self, obj):
        """Get total attempts from metadata."""
        return obj.meta_json.get('total_attempts', 0) if obj.meta_json else 0
        
    @extend_schema_field(serializers.IntegerField())
    def get_successful_attempts(self, obj):
        """Get successful attempts from metadata."""
        return obj.meta_json.get('successful_attempts', 0) if obj.meta_json else 0
        
    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_last_success_at(self, obj):
        """Get last success time from metadata."""
        return obj.meta_json.get('last_success_at') if obj.meta_json else None
        
    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_last_failure_at(self, obj):
        """Get last failure time from metadata."""
        return obj.meta_json.get('last_failure_at') if obj.meta_json else None
        
    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_last_error(self, obj):
        """Get last error from metadata."""
        return obj.meta_json.get('last_error') if obj.meta_json else None


class ProxyMarkResultSerializer(serializers.Serializer):
    """Serializer for marking proxy success/failure."""
    
    error_message = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Error message for failures"
    )