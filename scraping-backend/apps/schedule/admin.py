from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from .models import Schedule


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "id", 
        "spider_link", 
        "cron_expr",
        "timezone",
        "enabled_status", 
        "next_run_formatted",
        "time_until_next",
        "created_at"
    )
    list_filter = (
        "enabled", 
        "timezone",
        "spider__project",
        "spider__name",
        "created_at"
    )
    search_fields = ("spider__name", "cron_expr", "spider__project__name")
    readonly_fields = (
        "next_run_at",
        "created_at", 
        "updated_at",
        "time_until_next_run",
        "is_overdue",
        "is_due_now"
    )
    raw_id_fields = ("spider",)
    
    fieldsets = (
        (None, {
            'fields': ('spider', 'enabled')
        }),
        ('Schedule Configuration', {
            'fields': ('cron_expr', 'timezone')
        }),
        ('Execution Info', {
            'fields': ('next_run_at', 'time_until_next_run', 'is_overdue', 'is_due_now'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['enable_schedules', 'disable_schedules', 'recalculate_next_run']
    
    def spider_link(self, obj):
        """Display link to related spider."""
        if obj.spider:
            url = reverse('admin:spider_spider_change', args=[obj.spider.pk])
            return format_html('<a href="{}">{}</a>', url, f"{obj.spider.project.name} / {obj.spider.name}")
        return "No Spider"
    spider_link.short_description = "Spider"
    
    def enabled_status(self, obj):
        """Display enabled status with color coding."""
        if obj.enabled:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Enabled</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Disabled</span>'
            )
    enabled_status.short_description = "Status"
    enabled_status.admin_order_field = "enabled"
    
    def next_run_formatted(self, obj):
        """Display next run time with status indicators."""
        if not obj.next_run_at:
            return format_html('<span style="color: gray;">Not scheduled</span>')
            
        now = timezone.now()
        
        if obj.next_run_at <= now:
            # Overdue or due now
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠ {}</span>',
                obj.next_run_at.strftime('%Y-%m-%d %H:%M:%S %Z')
            )
        elif obj.next_run_at <= now + timezone.timedelta(hours=1):
            # Due within an hour
            return format_html(
                '<span style="color: orange; font-weight: bold;">⏰ {}</span>',
                obj.next_run_at.strftime('%Y-%m-%d %H:%M:%S %Z')
            )
        else:
            # Future run
            return format_html(
                '<span style="color: green;">{}</span>',
                obj.next_run_at.strftime('%Y-%m-%d %H:%M:%S %Z')
            )
    next_run_formatted.short_description = "Next Run"
    next_run_formatted.admin_order_field = "next_run_at"
    
    def time_until_next(self, obj):
        """Display time until next run in human-readable format."""
        time_delta = obj.time_until_next_run
        if not time_delta:
            return "N/A"
            
        if time_delta.total_seconds() <= 0:
            return format_html('<span style="color: red;">Overdue</span>')
            
        # Convert to human readable format
        total_seconds = int(time_delta.total_seconds())
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    time_until_next.short_description = "Time Until Next"
    
    def is_due_now(self, obj):
        """Show if schedule is currently due."""
        return obj.is_due()
    is_due_now.short_description = "Due Now"
    is_due_now.boolean = True
    
    def enable_schedules(self, request, queryset):
        """Enable selected schedules."""
        count = 0
        for schedule in queryset:
            if not schedule.enabled:
                schedule.enabled = True
                schedule.calculate_next_run()
                schedule.save()
                count += 1
                
        self.message_user(
            request, 
            f"{count} schedules enabled and next run times calculated."
        )
    enable_schedules.short_description = "Enable selected schedules"
    
    def disable_schedules(self, request, queryset):
        """Disable selected schedules."""
        count = queryset.filter(enabled=True).update(enabled=False, next_run_at=None)
        self.message_user(
            request, 
            f"{count} schedules disabled."
        )
    disable_schedules.short_description = "Disable selected schedules"
    
    def recalculate_next_run(self, request, queryset):
        """Recalculate next run time for selected schedules."""
        count = 0
        for schedule in queryset.filter(enabled=True):
            schedule.calculate_next_run()
            schedule.save()
            count += 1
            
        self.message_user(
            request, 
            f"Next run times recalculated for {count} enabled schedules."
        )
    recalculate_next_run.short_description = "Recalculate next run times"
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'spider__project'
        )