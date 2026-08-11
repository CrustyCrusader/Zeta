from django.urls import path
from . import views

app_name = "comments"

urlpatterns = [
    path("add/<int:content_type_id>/<int:object_id>/", views.add_comment, name="add_comment"),
    path("<int:comment_id>/delete/", views.delete_comment, name="delete_comment"),
]