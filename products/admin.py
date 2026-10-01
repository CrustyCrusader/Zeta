from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ("title", "owner", "kind", "price", "featured", "is_hidden")
	list_filter = ("kind", "featured", "is_hidden")
	search_fields = ("title", "description", "owner__username")