from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Report(models.Model):
    class Reason(models.TextChoices):
        SPAM = "spam", "Spam or scam"
        HARASSMENT = "harassment", "Harassment or bullying"
        HATEFUL = "hateful", "Hateful content"
        INAPPROPRIATE = "inappropriate", "Inappropriate content"
        COPYRIGHT = "copyright", "Copyright concern"
        OTHER = "other", "Something else"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending review"
        RESOLVED = "resolved", "Resolved"
        DISMISSED = "dismissed", "Dismissed"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reports_submitted",
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="content_reports",
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    reason = models.CharField(max_length=20, choices=Reason.choices)
    details = models.TextField(max_length=1000, blank=True)
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]
        constraints = [
            models.UniqueConstraint(
                fields=["reporter", "content_type", "object_id"],
                name="unique_reporter_content_report",
            ),
        ]

    def __str__(self):
        return f"{self.get_reason_display()} report on {self.content_object}"