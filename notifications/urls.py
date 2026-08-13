from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.notification_list, name="notification_list"),
    path("panel/", views.notification_panel, name="panel"),
]