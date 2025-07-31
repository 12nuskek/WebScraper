from django.db import models


class Spider(models.Model):
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="spiders",
    )
    name = models.CharField(max_length=120)
    start_urls_json = models.JSONField()         # JSON array of seed URLs
    settings_json = models.JSONField(null=True, blank=True)      # timeouts, headers…
    parse_rules_json = models.JSONField(null=True, blank=True)   # CSS/XPath, pipelines…
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "name")
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.project.name} / {self.name}"