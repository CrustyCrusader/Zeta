from django.db import models
from django.urls import reverse

class Video(models.Model):
    title = models.CharField(max_length=250)
    
    video_file = models.FileField(upload_to='Video/%y')
    # Add other fields as needed
    def get_absolute_url(self):
        return reverse("Video:video_detail", kwargs={"id": self.id})