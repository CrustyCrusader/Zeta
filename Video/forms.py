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