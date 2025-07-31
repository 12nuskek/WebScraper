import hashlib
from django.db import models
from django.utils import timezone


class RequestQueue(models.Model):
    """Model representing a queued HTTP request for a spider job."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('error', 'Error'),
        ('skipped', 'Skipped'),
    ]
    
    METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
        ('HEAD', 'HEAD'),
        ('OPTIONS', 'OPTIONS'),
    ]
    
    job = models.ForeignKey(
        "job.Job",
        on_delete=models.CASCADE,
        related_name="requests",
    )
    url = models.URLField(max_length=2000)  # Handle long URLs
    method = models.CharField(
        max_length=10,
        choices=METHOD_CHOICES,
        default='GET'
    )
    headers_json = models.JSONField(null=True, blank=True)
    body_blob = models.BinaryField(null=True, blank=True)  # For POST/PUT data
    priority = models.IntegerField(default=0)  # Higher = sooner
    depth = models.IntegerField(default=0)  # Crawl depth
    retries = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    fingerprint = models.CharField(max_length=64)  # MD5 hash
    scheduled_at = models.DateTimeField(default=timezone.now)
    picked_at = models.DateTimeField(null=True, blank=True)  # When worker dequeued it
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority", "scheduled_at"]  # High priority first, then FIFO
        constraints = [
            models.UniqueConstraint(
                fields=['job', 'fingerprint'],
                name='unique_job_fingerprint'
            )
        ]
        indexes = [
            models.Index(
                fields=['job', 'status', '-priority', 'scheduled_at'],
                name='idx_job_status_priority'
            ),
            models.Index(fields=['status', 'scheduled_at']),
            models.Index(fields=['fingerprint']),
        ]

    def __str__(self):
        return f"Request {self.id}: {self.method} {self.url[:50]}... ({self.status})"
        
    def save(self, *args, **kwargs):
        """Auto-generate fingerprint if not provided."""
        if not self.fingerprint:
            self.fingerprint = self.generate_fingerprint()
        super().save(*args, **kwargs)
        
    def generate_fingerprint(self):
        """Generate a unique fingerprint for this request."""
        # Normalize URL and create hash from URL + method + body
        url_normalized = self.url.lower().strip()
        body_hash = ""
        if self.body_blob:
            body_hash = hashlib.md5(self.body_blob).hexdigest()
        
        fingerprint_data = f"{url_normalized}:{self.method}:{body_hash}"
        return hashlib.md5(fingerprint_data.encode('utf-8')).hexdigest()
        
    @property
    def can_retry(self):
        """Check if this request can be retried."""
        return self.retries < self.max_retries
        
    def mark_in_progress(self):
        """Mark request as in progress and set picked_at timestamp."""
        self.status = 'in_progress'
        self.picked_at = timezone.now()
        self.save(update_fields=['status', 'picked_at', 'updated_at'])
        
    def mark_done(self):
        """Mark request as completed."""
        self.status = 'done'
        self.save(update_fields=['status', 'updated_at'])
        
    def mark_error(self, increment_retry=True):
        """Mark request as error and optionally increment retry count."""
        if increment_retry:
            self.retries += 1
        self.status = 'error'
        self.save(update_fields=['status', 'retries', 'updated_at'])
        
    def mark_skipped(self):
        """Mark request as skipped."""
        self.status = 'skipped'
        self.save(update_fields=['status', 'updated_at'])
        
    def reset_for_retry(self):
        """Reset request status for retry."""
        if self.can_retry:
            self.status = 'pending'
            self.picked_at = None
            self.save(update_fields=['status', 'picked_at', 'updated_at'])
            return True
        return False