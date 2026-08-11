from django.conf import settings
from django.db import models
from django.urls import reverse

class Video(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="videos",
    )

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    video = models.FileField(upload_to="videos/")

    thumbnail = models.ImageField(
        upload_to="thumbnails/"
    )

    created = models.DateTimeField(auto_now_add=True)

    updated = models.DateTimeField(auto_now=True)

    views = models.PositiveIntegerField(default=0)

    class Visibility(models.TextChoices):
        PUBLIC = "public", "Public"
        FOLLOWERS = "followers", "Followers"
        PRIVATE = "private", "Private"

    visibility = models.CharField(
        max_length=20,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
    )

    def get_absolute_url(self):
        return reverse("Video:video_details", kwargs={"id": self.id})

    def __str__(self):
        return self.title
    
    
class Like(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="video_likes",
    )

    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="likes",
    )

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "video"],
                name="unique_video_like",
            ),
        ]
        ordering = ["-created"]

    def __str__(self):
        return f"{self.user.username} likes {self.video.title}"