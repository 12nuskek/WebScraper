from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Proxy


@admin.register(Proxy)
class ProxyAdmin(admin.ModelAdmin):
    """Admin interface for Proxy model."""
    
    list_display = [
        'id',
        'masked_uri_display',
        'scheme',
        'hostname',
        'port',
        'status_display',
        'health_display',
        'fail_count',
        'success_rate_display',
        'last_ok_at',
        'updated_at',
    ]
    list_filter = [
        'is_active',
        'fail_count',
        'last_ok_at',
        'created_at',
    ]
    search_fields = [
        'uri',
    ]
    readonly_fields = [
        'id',
        'masked_uri_display',
        'hostname',
        'port',
        'scheme',
        'created_at',
        'updated_at',
        'health_display',
        'success_rate_display',
        'total_attempts',
        'successful_attempts',
    ]
    fieldsets = [
        ('Basic Information', {
            'fields': ['id', 'uri', 'masked_uri_display', 'is_active']
        }),
        ('Connection Details', {
            'fields': ['hostname', 'port', 'scheme']
        }),
        ('Health & Statistics', {
            'fields': [
                'fail_count', 'last_ok_at', 'health_display', 
                'success_rate_display', 'total_attempts', 'successful_attempts'
            ]
        }),
        ('Metadata', {
            'fields': ['meta_json'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    ordering = ['fail_count', '-last_ok_at']
    
    def masked_uri_display(self, obj):
        """Display masked URI."""
        return obj.masked_uri
    masked_uri_display.short_description = 'URI (Masked)'
    
    def status_display(self, obj):
        """Display proxy status with color coding."""
        if obj.is_active:
            return format_html(
                '<span style="color: green;">Active</span>'
            )
        else:
            return format_html(
                '<span style="color: red;">Inactive</span>'
            )
    status_display.short_description = 'Status'
    
    def health_display(self, obj):
        """Display proxy health with color coding."""
        if obj.is_healthy:
            return format_html(
                '<span style="color: green;">Healthy</span>'
            )
        else:
            return format_html(
                '<span style="color: red;">Unhealthy</span>'
            )
    health_display.short_description = 'Health'
    
    def success_rate_display(self, obj):
        """Display success rate with color coding."""
        rate = obj.success_rate
        if rate is None:
            return format_html('<span style="color: gray;">No data</span>')
        
        if rate >= 90:
            color = 'green'
        elif rate >= 70:
            color = 'orange'
        else:
            color = 'red'
            
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color,
            rate
        )
    success_rate_display.short_description = 'Success Rate'
    
    def total_attempts(self, obj):
        """Display total attempts from metadata."""
        if obj.meta_json:
            return obj.meta_json.get('total_attempts', 0)
        return 0
    total_attempts.short_description = 'Total Attempts'
    
    def successful_attempts(self, obj):
        """Display successful attempts from metadata."""
        if obj.meta_json:
            return obj.meta_json.get('successful_attempts', 0)
        return 0
    successful_attempts.short_description = 'Successful Attempts'
    
    actions = [
        'mark_as_active',
        'mark_as_inactive',
        'reset_statistics',
        'cleanup_failed_proxies'
    ]
    
    def mark_as_active(self, request, queryset):
        """Admin action to mark proxies as active."""
        count = queryset.update(is_active=True)
        self.message_user(
            request,
            f'Successfully activated {count} proxies.'
        )
    mark_as_active.short_description = 'Mark selected proxies as active'
    
    def mark_as_inactive(self, request, queryset):
        """Admin action to mark proxies as inactive."""
        count = queryset.update(is_active=False)
        self.message_user(
            request,
            f'Successfully deactivated {count} proxies.'
        )
    mark_as_inactive.short_description = 'Mark selected proxies as inactive'
    
    def reset_statistics(self, request, queryset):
        """Admin action to reset proxy statistics."""
        count = 0
        for proxy in queryset:
            proxy.reset_stats()
            count += 1
        
        self.message_user(
            request,
            f'Successfully reset statistics for {count} proxies.'
        )
    reset_statistics.short_description = 'Reset statistics for selected proxies'
    
    def cleanup_failed_proxies(self, request, queryset):
        """Admin action to cleanup failed proxies."""
        deleted_count, _ = Proxy.cleanup_failed_proxies()
        self.message_user(
            request,
            f'Successfully deleted {deleted_count} failed proxies.'
        )
    cleanup_failed_proxies.short_description = 'Delete all failed proxies (20+ failures)'
