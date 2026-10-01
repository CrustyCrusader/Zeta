from django.contrib import admin

from .models import Bookmark


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "content_type", "object_id", "created")
    list_filter = ("content_type", "created")
    search_fields = ("user__username",)