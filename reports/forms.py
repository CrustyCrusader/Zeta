from django import forms

from .models import Report


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ("reason", "details")
        widgets = {
            "reason": forms.Select(),
            "details": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Add context that may help the moderation team.",
                }
            ),
        }