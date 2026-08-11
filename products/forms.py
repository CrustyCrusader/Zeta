from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    title = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Your title"}),
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "placeholder": "Your description",
                "rows": 10,
            }
        ),
    )
    price = forms.DecimalField(initial=199.99)

    class Meta:
        model = Product
        fields = ["title", "description", "price"]