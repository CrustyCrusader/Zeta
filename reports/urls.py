from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("<str:model_name>/<int:object_id>/", views.create_report, name="create"),
]