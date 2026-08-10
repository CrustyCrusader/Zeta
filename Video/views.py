from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import models
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
)

from .forms import VideoForm
from .models import Video


class VideoCreateView(LoginRequiredMixin, CreateView):
    model = Video
    form_class = VideoForm
    template_name = "Video/upload_video.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "Video:video_details",
            kwargs={"id": self.object.id},
        )


class VideoListView(ListView):
    model = Video
    template_name = "Video/video_list.html"
    context_object_name = "videos"

    def get_queryset(self):
        queryset = Video.objects.select_related("author").order_by("-created")

        if self.request.user.is_authenticated:
            return queryset.filter(
                models.Q(visibility=Video.Visibility.PUBLIC)
                | models.Q(author=self.request.user)
            )

        return queryset.filter(
            visibility=Video.Visibility.PUBLIC
        )


class VideoDetailView(DetailView):
    model = Video
    template_name = "Video/video_details.html"
    context_object_name = "video"

    def get_object(self):
        return get_object_or_404(
            Video,
            id=self.kwargs.get("id")
        )


class VideoUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    UpdateView
):
    model = Video
    form_class = VideoForm
    template_name = "Video/upload_video.html"

    def get_object(self):
        return get_object_or_404(
            Video,
            id=self.kwargs.get("id")
        )

    def test_func(self):
        video = self.get_object()
        return video.author == self.request.user


class VideoDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    DeleteView
):
    model = Video
    template_name = "Video/video_delete.html"

    def get_object(self):
        return get_object_or_404(
            Video,
            id=self.kwargs.get("id")
        )

    def test_func(self):
        video = self.get_object()
        return video.author == self.request.user

    def get_success_url(self):
        return reverse("Video:video_list")