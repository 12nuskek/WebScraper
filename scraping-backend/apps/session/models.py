from django.db import models
from django.utils import timezone


class Session(models.Model):
    """Model representing a logged-in session state for a spider."""
    
    spider = models.ForeignKey(
        "spider.Spider",
        on_delete=models.CASCADE,
        related_name="sessions",
    )
    label = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Session label (e.g., 'default', 'sellerA')"
    )
    cookies_json = models.JSONField(
        null=True,
        blank=True,
        help_text="Cookies for this session"
    )
    headers_json = models.JSONField(
        null=True,
        blank=True,
        help_text="Headers for this session"
    )
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this session expires"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=['spider']),
            models.Index(fields=['spider', 'label']),
            models.Index(fields=['valid_until']),
        ]
        unique_together = [['spider', 'label']]

    def __str__(self):
        label = self.label or "default"
        return f"Session {self.id}: {self.spider.name} ({label})"
        
    @property
    def is_expired(self):
        """Check if session has expired."""
        if not self.valid_until:
            return False
        return timezone.now() > self.valid_until
        
    @property
    def is_valid(self):
        """Check if session is valid (not expired)."""
        return not self.is_expired
        
    def extend_validity(self, hours=24):
        """Extend session validity by specified hours."""
        from datetime import timedelta
        self.valid_until = timezone.now() + timedelta(hours=hours)
        self.save(update_fields=['valid_until', 'updated_at'])
        
    @classmethod
    def get_valid_sessions(cls):
        """Get all valid (non-expired) sessions."""
        current_time = timezone.now()
        return cls.objects.filter(
            models.Q(valid_until__isnull=True) | 
            models.Q(valid_until__gt=current_time)
        )
        
    @classmethod
    def get_expired_sessions(cls):
        """Get all expired sessions."""
        current_time = timezone.now()
        return cls.objects.filter(valid_until__lt=current_time)
        
    @classmethod
    def cleanup_expired_sessions(cls):
        """Delete all expired sessions."""
        return cls.get_expired_sessions().delete()
