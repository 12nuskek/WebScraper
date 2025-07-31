import re
from datetime import datetime, timedelta
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import zoneinfo


class Schedule(models.Model):
    """Model representing a scheduled spider execution using cron expressions."""
    
    spider = models.ForeignKey(
        "spider.Spider",
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    cron_expr = models.CharField(
        max_length=100,
        help_text="Cron expression (e.g., '0 */6 * * *' for every 6 hours)"
    )
    timezone = models.CharField(
        max_length=50,
        default='Australia/Brisbane',
        help_text="Timezone for schedule execution"
    )
    enabled = models.BooleanField(default=True)
    next_run_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["next_run_at", "-created_at"]
        indexes = [
            models.Index(fields=['spider', 'enabled']),
            models.Index(fields=['enabled', 'next_run_at']),
            models.Index(fields=['next_run_at']),
        ]

    def __str__(self):
        status = "enabled" if self.enabled else "disabled"
        return f"Schedule {self.id}: {self.spider.name} ({self.cron_expr}) - {status}"
        
    def clean(self):
        """Validate cron expression and timezone."""
        super().clean()
        
        # Validate cron expression
        if not self.is_valid_cron_expression(self.cron_expr):
            raise ValidationError({'cron_expr': 'Invalid cron expression format'})
            
        # Validate timezone
        try:
            zoneinfo.ZoneInfo(self.timezone)
        except zoneinfo.ZoneInfoNotFoundError:
            raise ValidationError({'timezone': f'Unknown timezone: {self.timezone}'})
            
    def save(self, *args, **kwargs):
        """Override save to calculate next_run_at."""
        self.clean()
        
        # Calculate next run time if enabled
        if self.enabled and not self.next_run_at:
            self.calculate_next_run()
            
        super().save(*args, **kwargs)
        
    @staticmethod
    def is_valid_cron_expression(cron_expr):
        """Validate cron expression format (minute hour day month weekday)."""
        if not cron_expr or not isinstance(cron_expr, str):
            return False
            
        parts = cron_expr.strip().split()
        if len(parts) != 5:
            return False
            
        # Define valid ranges for each cron field
        ranges = [
            (0, 59),    # minute
            (0, 23),    # hour  
            (1, 31),    # day
            (1, 12),    # month
            (0, 7),     # weekday (0 and 7 are Sunday)
        ]
        
        for i, part in enumerate(parts):
            if not Schedule.is_valid_cron_field(part, ranges[i]):
                return False
                
        return True
        
    @staticmethod
    def is_valid_cron_field(field, valid_range):
        """Validate individual cron field."""
        min_val, max_val = valid_range
        
        # Handle special characters
        if field == '*':
            return True
            
        # Handle step values (*/n)
        if field.startswith('*/'):
            try:
                step = int(field[2:])
                return step > 0 and step <= max_val
            except ValueError:
                return False
                
        # Handle ranges (n-m)
        if '-' in field:
            try:
                start, end = map(int, field.split('-'))
                return min_val <= start <= end <= max_val
            except (ValueError, TypeError):
                return False
                
        # Handle lists (n,m,o)
        if ',' in field:
            try:
                values = [int(x.strip()) for x in field.split(',')]
                return all(min_val <= val <= max_val for val in values)
            except (ValueError, TypeError):
                return False
                
        # Handle single values
        try:
            value = int(field)
            return min_val <= value <= max_val
        except ValueError:
            return False
            
    def calculate_next_run(self, from_time=None):
        """Calculate the next run time based on cron expression."""
        if not self.enabled:
            self.next_run_at = None
            return
            
        if from_time is None:
            from_time = timezone.now()
            
        # Convert to target timezone
        try:
            target_tz = zoneinfo.ZoneInfo(self.timezone)
        except zoneinfo.ZoneInfoNotFoundError:
            # Fallback to UTC if timezone is invalid
            target_tz = timezone.utc
            
        if timezone.is_aware(from_time):
            local_time = from_time.astimezone(target_tz)
        else:
            local_time = timezone.make_aware(from_time, target_tz)
            
        # Parse cron expression
        minute, hour, day, month, weekday = self.cron_expr.split()
        
        # Start from next minute to avoid immediate execution
        next_time = local_time.replace(second=0, microsecond=0) + timedelta(minutes=1)
        
        # Find next valid time (simple implementation - could be optimized)
        max_iterations = 366 * 24 * 60  # Max 1 year of minutes
        
        for _ in range(max_iterations):
            if self._matches_cron_time(next_time, minute, hour, day, month, weekday):
                # Convert back to UTC
                if target_tz != timezone.utc:
                    self.next_run_at = next_time.astimezone(timezone.utc)
                else:
                    self.next_run_at = next_time
                return
                
            next_time += timedelta(minutes=1)
            
        # If no match found, disable schedule
        self.next_run_at = None
        self.enabled = False
        
    def _matches_cron_time(self, dt, minute, hour, day, month, weekday):
        """Check if datetime matches cron expression."""
        return (
            self._matches_cron_field(dt.minute, minute, 0, 59) and
            self._matches_cron_field(dt.hour, hour, 0, 23) and
            self._matches_cron_field(dt.day, day, 1, 31) and
            self._matches_cron_field(dt.month, month, 1, 12) and
            self._matches_cron_field(dt.weekday() + 1, weekday, 0, 7)  # Convert to Sunday=0
        )
        
    def _matches_cron_field(self, value, pattern, min_val, max_val):
        """Check if value matches cron field pattern."""
        if pattern == '*':
            return True
            
        if pattern.startswith('*/'):
            step = int(pattern[2:])
            return value % step == 0
            
        if '-' in pattern:
            start, end = map(int, pattern.split('-'))
            return start <= value <= end
            
        if ',' in pattern:
            values = [int(x.strip()) for x in pattern.split(',')]
            return value in values
            
        return value == int(pattern)
        
    def update_next_run(self):
        """Update next_run_at to the next scheduled time."""
        if self.enabled:
            self.calculate_next_run(self.next_run_at)
        else:
            self.next_run_at = None
            
    def is_due(self, current_time=None):
        """Check if schedule is due for execution."""
        if not self.enabled or not self.next_run_at:
            return False
            
        if current_time is None:
            current_time = timezone.now()
            
        return current_time >= self.next_run_at
        
    def mark_executed(self):
        """Mark schedule as executed and calculate next run time."""
        if self.enabled:
            # Calculate next run from current next_run_at to ensure we move to next slot
            self.calculate_next_run(from_time=self.next_run_at)
            self.save(update_fields=['next_run_at', 'updated_at'])
            
    @property
    def time_until_next_run(self):
        """Get time until next run as timedelta."""
        if not self.next_run_at:
            return None
            
        now = timezone.now()
        if self.next_run_at > now:
            return self.next_run_at - now
        return timedelta(0)
        
    @property
    def is_overdue(self):
        """Check if schedule is overdue."""
        if not self.next_run_at:
            return False
            
        return timezone.now() > self.next_run_at
        
    @classmethod
    def get_due_schedules(cls):
        """Get all schedules that are due for execution."""
        current_time = timezone.now()
        return cls.objects.filter(
            enabled=True,
            next_run_at__lte=current_time
        ).select_related('spider__project')
        
    @classmethod
    def get_upcoming_schedules(cls, hours=24):
        """Get schedules due within the next N hours."""
        current_time = timezone.now()
        future_time = current_time + timedelta(hours=hours)
        
        return cls.objects.filter(
            enabled=True,
            next_run_at__gte=current_time,
            next_run_at__lte=future_time
        ).select_related('spider__project').order_by('next_run_at')