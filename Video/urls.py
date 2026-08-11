from django.urls import path
from . import views
from .views import (
    VideoCreateView,
    VideoDeleteView,
    VideoDetailView,
    VideoListView,
    VideoUpdateView,
)

app_name = 'Video'

urlpatterns = [
    path('', VideoListView.as_view(), name='video_list'),
    path('upload/', VideoCreateView.as_view(), name='video_upload'),
    path('<int:id>/', VideoDetailView.as_view(), name='video_details'),
    path('<int:id>/update/', VideoUpdateView.as_view(), name='video_update'),
    path('<int:id>/delete/', VideoDeleteView.as_view(), name='video_delete'),
    path("<int:id>/like/", views.toggle_like, name="toggle_like"),
    path("liked/<str:username>/", views.liked_videos, name="liked_videos"),
]