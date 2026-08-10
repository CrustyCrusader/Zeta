from django.conf import settings
from django.db import models


class Profile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    avatar = models.ImageField(
        upload_to="avatars/",
        default="avatars/default.png"
    )

    banner = models.ImageField(
        upload_to="banners/",
        blank=True,
        null=True
    )

    bio = models.TextField(blank=True)

    website = models.URLField(blank=True)

    location = models.CharField(
        max_length=100,
        blank=True
    )

    birth_date = models.DateField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username