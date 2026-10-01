from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    title = forms.CharField(
        max_length=120,
        widget=forms.TextInput(attrs={"placeholder": "A clear name for your offer"}),
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "placeholder": "What makes it useful? Include details buyers need to know.",
                "rows": 7,
            }
        ),
    )
    price = forms.DecimalField(
        min_value=0,
        widget=forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
    )

    class Meta:
        model = Product
        fields = ["title", "kind", "description", "price", "image", "featured"]