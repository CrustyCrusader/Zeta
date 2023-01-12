from django.db import models
from django.urls import reverse

class Video(models.Model):
    title = models.CharField(max_length=200)
    video_file = models.FileField(upload_to='videos/')
    # Add other fields as needed
    def get_absolute_url(self):
        return reverse("articles:article-detail", kwargs={"id": self.id})