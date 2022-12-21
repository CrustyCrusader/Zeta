from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import (
    DetailView,
    ListView,
    UpdateView,
    ListView,
    DeleteView
)

from .forms import VideoForm
from .models import Video


def upload_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('videos')
    else:
        form = VideoForm()
    return render(request, 'upload_video.html', {'form': form})

class VideoListView(ListView):
    template_name = 'Video_list.html'
    queryset = Video.objects.all()

class VideoDetailView(DetailView):
        template_name = 'video_detail.html'
    #queryset = Video.objects.all()

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Video, id=id_)


class VideoUpdateView(UpdateView):
    template_name = 'video_create.html'
    form_class = VideoForm

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Video, id=id_)

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)


class VideoDeleteView(DeleteView):
    template_name = 'video_delete.html'
    
    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Video, id=id_)

    def get_success_url(self):
        return reverse('Videos:Video-list')

