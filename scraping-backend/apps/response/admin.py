from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Response


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = (
        "id", 
        "request_link", 
        "status_code_colored", 
        "final_url_short", 
        "latency_ms",
        "body_size_formatted",
        "from_cache",
        "fetched_at"
    )
    list_filter = (
        "status_code", 
        "from_cache", 
        "fetched_at",
        "request__job__spider__project",
        "request__job__spider"
    )
    search_fields = ("final_url", "request__url", "content_hash")
    readonly_fields = (
        "content_hash", 
        "body_size", 
        "created_at", 
        "updated_at",
        "is_success",
        "is_redirect",
        "is_client_error",
        "is_server_error"
    )
    raw_id_fields = ("request",)
    
    fieldsets = (
        (None, {
            'fields': ('request', 'final_url', 'status_code')
        }),
        ('Response Details', {
            'fields': ('headers_json', 'latency_ms', 'from_cache', 'fetched_at')
        }),
        ('Body & Content', {
            'fields': ('body_path', 'content_hash', 'body_size'),
            'classes': ('collapse',)
        }),
        ('Status Indicators', {
            'fields': ('is_success', 'is_redirect', 'is_client_error', 'is_server_error'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_cached', 'mark_not_cached', 'delete_body_files']
    
    def request_link(self, obj):
        """Display link to related request."""
        if obj.request:
            url = reverse('admin:request_requestqueue_change', args=[obj.request.pk])
            return format_html('<a href="{}">{}</a>', url, f"Request {obj.request.pk}")
        return "No Request"
    request_link.short_description = "Request"
    
    def status_code_colored(self, obj):
        """Display status code with color coding."""
        if not obj.status_code:
            return format_html('<span style="color: gray;">Unknown</span>')
            
        if obj.is_success:
            color = "green"
        elif obj.is_redirect:
            color = "orange"
        elif obj.is_client_error:
            color = "red"
        elif obj.is_server_error:
            color = "darkred"
        else:
            color = "gray"
            
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.status_code
        )
    status_code_colored.short_description = "Status Code"
    status_code_colored.admin_order_field = "status_code"
    
    def final_url_short(self, obj):
        """Display truncated final URL."""
        url = obj.final_url or obj.request.url if obj.request else "No URL"
        if len(url) > 60:
            return f"{url[:57]}..."
        return url
    final_url_short.short_description = "Final URL"
    final_url_short.admin_order_field = "final_url"
    
    def body_size_formatted(self, obj):
        """Display body size in human-readable format."""
        size = obj.body_size
        if size == 0:
            return "No body"
        elif size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    body_size_formatted.short_description = "Body Size"
    
    def mark_cached(self, request, queryset):
        """Mark selected responses as cached."""
        count = queryset.update(from_cache=True)
        self.message_user(
            request, 
            f"{count} responses marked as cached."
        )
    mark_cached.short_description = "Mark selected responses as cached"
    
    def mark_not_cached(self, request, queryset):
        """Mark selected responses as not cached."""
        count = queryset.update(from_cache=False)
        self.message_user(
            request, 
            f"{count} responses marked as not cached."
        )
    mark_not_cached.short_description = "Mark selected responses as not cached"
    
    def delete_body_files(self, request, queryset):
        """Delete body files for selected responses."""
        deleted_count = 0
        for response in queryset:
            if response.delete_body_file():
                deleted_count += 1
                response.body_path = None
                response.save(update_fields=['body_path'])
                
        self.message_user(
            request, 
            f"{deleted_count} body files deleted."
        )
    delete_body_files.short_description = "Delete body files for selected responses"
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'request__job__spider__project'
        )