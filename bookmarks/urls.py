from django.urls import path

from . import views

app_name = "bookmarks"

urlpatterns = [
    path("saved/", views.saved_items, name="saved"),
    path("<str:model_name>/<int:object_id>/toggle/", views.toggle_bookmark, name="toggle"),
]