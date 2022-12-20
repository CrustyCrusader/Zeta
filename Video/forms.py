from django import forms

class VideoForm(forms.Form):
    title = forms.CharField(max_length=200)
    video_file = forms.FileField()
