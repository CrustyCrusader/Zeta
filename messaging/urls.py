from django.urls import path

from . import views

app_name = "messaging"

urlpatterns = [
    path("", views.conversation_list, name="conversation_list"),
    path("start/<str:username>/", views.start_conversation, name="start_conversation"),
    path("group/create/", views.create_group, name="create_group"),
    path("<int:id>/", views.conversation_detail, name="conversation_detail"),
    path("panel/", views.conversation_panel, name="panel"),
    path("panel/<int:id>/messages/", views.conversation_messages_panel, name="panel_messages"),
    path("<int:id>/earlier/", views.load_earlier_messages, name="load_earlier"),
]