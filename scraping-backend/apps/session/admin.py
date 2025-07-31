from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Session


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    """Admin interface for Session model."""
    
    list_display = [
        'id',
        'spider',
        'label',
        'validity_status',
        'has_cookies',
        'has_headers',
        'valid_until',
        'updated_at',
    ]
    list_filter = [
        'spider',
        'valid_until',
        'created_at',
        'updated_at',
    ]
    search_fields = [
        'label',
        'spider__name',
        'spider__project__name',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'validity_status',
        'cookie_count',
        'header_count',
    ]
    fieldsets = [
        ('Basic Information', {
            'fields': ['id', 'spider', 'label', 'validity_status']
        }),
        ('Session Data', {
            'fields': ['cookies_json', 'headers_json', 'cookie_count', 'header_count']
        }),
        ('Validity', {
            'fields': ['valid_until']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    ordering = ['-updated_at']
    
    def validity_status(self, obj):
        """Display validity status with color coding."""
        if obj.is_expired:
            return format_html(
                '<span style="color: red;">Expired</span>'
            )
        elif obj.valid_until:
            return format_html(
                '<span style="color: green;">Valid until {}</span>',
                obj.valid_until.strftime('%Y-%m-%d %H:%M')
            )
        else:
            return format_html(
                '<span style="color: blue;">No expiry</span>'
            )
    validity_status.short_description = 'Status'
    
    def has_cookies(self, obj):
        """Display whether session has cookies."""
        return bool(obj.cookies_json)
    has_cookies.boolean = True
    has_cookies.short_description = 'Cookies'
    
    def has_headers(self, obj):
        """Display whether session has headers."""
        return bool(obj.headers_json)
    has_headers.boolean = True
    has_headers.short_description = 'Headers'
    
    def cookie_count(self, obj):
        """Display number of cookies."""
        if obj.cookies_json:
            return len(obj.cookies_json)
        return 0
    cookie_count.short_description = 'Cookie Count'
    
    def header_count(self, obj):
        """Display number of headers."""
        if obj.headers_json:
            return len(obj.headers_json)
        return 0
    header_count.short_description = 'Header Count'
    
    actions = ['cleanup_expired_sessions', 'extend_validity_24h']
    
    def cleanup_expired_sessions(self, request, queryset):
        """Admin action to cleanup expired sessions."""
        deleted_count, _ = Session.cleanup_expired_sessions()
        self.message_user(
            request,
            f'Successfully deleted {deleted_count} expired sessions.'
        )
    cleanup_expired_sessions.short_description = 'Delete all expired sessions'
    
    def extend_validity_24h(self, request, queryset):
        """Admin action to extend validity by 24 hours."""
        count = 0
        for session in queryset:
            session.extend_validity(hours=24)
            count += 1
        
        self.message_user(
            request,
            f'Successfully extended validity for {count} sessions by 24 hours.'
        )
    extend_validity_24h.short_description = 'Extend validity by 24 hours'
