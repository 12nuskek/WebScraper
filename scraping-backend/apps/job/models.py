from django.db import models


class Job(models.Model):
    """Model representing a spider job execution."""
    
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('done', 'Done'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    ]
    
    spider = models.ForeignKey(
        "spider.Spider",
        on_delete=models.CASCADE,
        related_name="jobs",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='queued'
    )
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    stats_json = models.JSONField(null=True, blank=True)  # counters, durations
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=['spider', 'status']),
        ]

    def __str__(self):
        return f"Job {self.id} ({self.spider.name}) - {self.status}"
        
    @property
    def duration(self):
        """Calculate job duration if both started_at and finished_at are set."""
        if self.started_at and self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None