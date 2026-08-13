from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Notification(models.Model):

    class Kind(models.TextChoices):
        FOLLOW = "follow", "Follow"
        LIKE = "like", "Like"
        COMMENT = "comment", "Comment"
        MESSAGE = "message", "Message"

    # Who receives this notification
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    # Who caused it (the follower, the liker, the commenter)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="actions",
    )

    kind = models.CharField(max_length=20, choices=Kind.choices)

    # What it's about — a Video, a Comment, or nothing (for follows).
    # Reuses the same ContentTypes pattern as the Comment model, so
    # this works for videos, articles, or anything added later
    # without needing a new field or migration.
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey("content_type", "object_id")

    is_read = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.actor.username} → {self.recipient.username} ({self.kind})"