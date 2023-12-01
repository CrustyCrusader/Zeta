from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.core.validators import FileExtensionValidator

class Video(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    video_file = models.FileField(upload_to='Video/', validators = [FileExtensionValidator(allowed_extensions=['mp4','webm'])])
    thumbnail = models.FileField(blank = True, null = True, upload_to='thumbnails/', validators = [FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])])
    date_posted = models.DateTimeField(default=timezone.now)
    # Add other fields as needed
    def get_absolute_url(self):
        return reverse("Video:video_details", kwargs={"id": self.id})