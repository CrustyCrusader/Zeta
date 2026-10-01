from django.contrib import admin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	list_display = ("author", "content_type", "object_id", "is_hidden", "created")
	list_filter = ("is_hidden", "content_type", "created")
	search_fields = ("author__username", "content")
