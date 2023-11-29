from django import forms
from .models import Video
from django.utils import timezone
class VideoForm(forms.ModelForm):
     title = forms.CharField(max_length=250)
     description = forms.CharField(
                        required=False, 
                        widget=forms.Textarea(
                                attrs={
                                    "placeholder": "Your description",
                                    "class": "new-class-name two",
                                    "id": "my-id-for-textarea",
                                    "rows": 20,
                                    'cols': 120
                                }
                            )
                        )
     video_file = forms.FileField()
     thumbnail = forms.FileField()
     date_posted = forms.DateTimeField()
     class Meta:
        model= Video
        fields = [
        'title',
        'description',
        'video_file',

        ]

       