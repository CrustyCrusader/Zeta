from django import forms
from .models import Video

class VideoForm(forms.ModelForm):
     title = forms.CharField(max_length=200)
     video_file = forms.FileField()
    class Meta:
        model= Video
        fields = [
        'title',
        'video_file'

        ]

       