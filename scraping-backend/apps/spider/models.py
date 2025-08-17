from django.db import models


class Spider(models.Model):
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="spiders",
    )
    name = models.CharField(max_length=120)
    external_id = models.CharField(max_length=120, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=120, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    priority = models.CharField(max_length=50, null=True, blank=True)
    start_urls_json = models.JSONField()         # JSON array of seed URLs
    settings_json = models.JSONField(null=True, blank=True)      # timeouts, headers…
    parse_rules_json = models.JSONField(null=True, blank=True)   # CSS/XPath, pipelines…
    target_json = models.JSONField(null=True, blank=True)
    execution_json = models.JSONField(null=True, blank=True)
    output_json = models.JSONField(null=True, blank=True)
    retry_policy_json = models.JSONField(null=True, blank=True)
    advanced_json = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "name")
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.project.name} / {self.name}"