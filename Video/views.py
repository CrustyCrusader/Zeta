from django.shortcuts import render, get_object_or_404,redirect
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    ListView,
    DeleteView
)

from .forms import VideoForm
from .models import Video

class VideoCreateView(CreateView):
    template_name = 'Video/upload_video.html'
    form_class = VideoForm
    queryset = Video.objects.all()

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)

class VideoListView(ListView):
    template_name = 'Video/Video_list.html'
    queryset = Video.objects.all()

class VideoDetailView(DetailView):
    template_name = 'Video/video_details.html'
    
    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Video, id=id_)


class VideoUpdateView(UpdateView):
    template_name = 'Video/video_create.html'
    form_class = VideoForm

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Video, id=id_)

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)


class VideoDeleteView(DeleteView):
    template_name = 'Video/video_delete.html'
    
    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Video, id=id_)

    def get_success_url(self):
        return reverse('Videos:Video_list')

