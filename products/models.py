from django.conf import settings
from django.db import models
from django.urls import reverse


class Product(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
    )

    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    featured = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse("products:product-detail", kwargs={"id": self.id})