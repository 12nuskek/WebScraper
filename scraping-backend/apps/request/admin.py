from django.contrib import admin
from django.utils.html import format_html
from .models import RequestQueue


@admin.register(RequestQueue)
class RequestQueueAdmin(admin.ModelAdmin):
    list_display = (
        "id", 
        "job", 
        "method", 
        "short_url", 
        "status", 
        "priority", 
        "depth",
        "retry_info",
        "scheduled_at",
        "picked_at"
    )
    list_filter = (
        "status", 
        "method", 
        "priority", 
        "depth",
        "job__spider__project",
        "created_at"
    )
    search_fields = ("url", "job__spider__name", "fingerprint")
    readonly_fields = ("fingerprint", "created_at", "updated_at", "can_retry")
    raw_id_fields = ("job",)
    
    fieldsets = (
        (None, {
            'fields': ('job', 'url', 'method', 'status')
        }),
        ('Request Details', {
            'fields': ('headers_json', 'body_blob', 'fingerprint'),
            'classes': ('collapse',)
        }),
        ('Queue Management', {
            'fields': ('priority', 'depth', 'retries', 'max_retries', 'can_retry')
        }),
        ('Timing', {
            'fields': ('scheduled_at', 'picked_at', 'created_at', 'updated_at')
        }),
    )
    
    actions = ['mark_pending', 'mark_done', 'mark_error', 'mark_skipped']
    
    def short_url(self, obj):
        """Display truncated URL."""
        if len(obj.url) > 50:
            return f"{obj.url[:47]}..."
        return obj.url
    short_url.short_description = "URL"
    
    def retry_info(self, obj):
        """Display retry information with color coding."""
        if obj.retries == 0:
            return "0"
        elif obj.retries >= obj.max_retries:
            return format_html(
                '<span style="color: red;">{}/{}</span>',
                obj.retries, obj.max_retries
            )
        else:
            return format_html(
                '<span style="color: orange;">{}/{}</span>',
                obj.retries, obj.max_retries
            )
    retry_info.short_description = "Retries"
    
    def mark_pending(self, request, queryset):
        """Mark selected requests as pending."""
        count = 0
        for req in queryset:
            if req.reset_for_retry():
                count += 1
        self.message_user(
            request, 
            f"{count} requests marked as pending."
        )
    mark_pending.short_description = "Mark selected requests as pending"
    
    def mark_done(self, request, queryset):
        """Mark selected requests as done."""
        count = queryset.update(status='done')
        self.message_user(
            request, 
            f"{count} requests marked as done."
        )
    mark_done.short_description = "Mark selected requests as done"
    
    def mark_error(self, request, queryset):
        """Mark selected requests as error."""
        count = queryset.update(status='error')
        self.message_user(
            request, 
            f"{count} requests marked as error."
        )
    mark_error.short_description = "Mark selected requests as error"
    
    def mark_skipped(self, request, queryset):
        """Mark selected requests as skipped."""
        count = queryset.update(status='skipped')
        self.message_user(
            request, 
            f"{count} requests marked as skipped."
        )
    mark_skipped.short_description = "Mark selected requests as skipped"