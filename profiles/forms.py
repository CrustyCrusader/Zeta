from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            "avatar",
            "banner",
            "bio",
            "website",
            "location",
            "birth_date",
            "likes_public",
        )
        widgets = {
            "birth_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }