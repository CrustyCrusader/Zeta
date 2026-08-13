from django import forms
from .models import Video


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = [
            "title",
            "description",
            "video",
            "thumbnail",
            "visibility",
        ]
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "placeholder": "Your description",
                    "rows": 10,
                }
            ),
        }

    def clean_video(self):
        video = self.cleaned_data.get("video")
        if video:
            valid_extensions = [".mp4", ".mov"]
            if not any(video.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError(
                    "Please upload an MP4 or MOV file — other formats may not play on all devices."
                )
        return video