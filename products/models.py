from django.conf import settings
from django.db import models
from django.urls import reverse


class Product(models.Model):
    class Kind(models.TextChoices):
        PRODUCT = "product", "Product"
        SERVICE = "service", "Service"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
    )

    title = models.CharField(max_length=120)
    kind = models.CharField(
        max_length=12,
        choices=Kind.choices,
        default=Kind.PRODUCT,
    )
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="products/", blank=True)
    featured = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse("products:product-detail", kwargs={"id": self.id})