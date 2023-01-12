from django.urls import path
from .views import ( 
    VideoCreateView,
   VideoDeleteView,
   VideoDetailView,
   VideoListView,
   VideoUpdateView,
   

)

    
  

app_name ='Video'
urlpatterns = [
    path('',VideoListView.as_view(), name='video_list'),
    path('upload/', VideoCreateView.as_view(), name='upload_video'),
    path('<int:id>/',VideoDetailView.as_view(), name='video_detail'),
    path('<int:id>/update/',VideoUpdateView.as_view(), name='video_update'),
    path('<int:id>/delete/',VideoDeleteView.as_view(), name='video_delete'),

]