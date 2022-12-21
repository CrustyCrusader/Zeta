from django.urls import path
from .views import (upload_video,
   VideoDeleteView,
   VideoDetailView,
   VideoListView,
   VideoUpdateView,
   

)

    
  

app_name ='Video'
urlpatterns = [
    path('',VideoListView.as_view(), name='video-list'),
    path('upload/', upload_video, name='upload_video'),
    path('<int:id>/',VideoDetailView.as_view(), name='video-detail'),
    path('<int:id>/update/',VideoUpdateView.as_view(), name='video-update'),
    path('<int:id>/delete/',VideoDeleteView.as_view(), name='video-delete'),

]