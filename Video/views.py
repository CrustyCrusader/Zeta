from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from django.http import Http404, JsonResponse
from accounts.models import User
from .models import Video, Like
from comments.models import Comment
from comments.forms import CommentForm
from notifications.utils import notify
from bookmarks.utils import is_bookmarked_by
from django.contrib.contenttypes.models import ContentType
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
)

from .forms import VideoForm
from .utils import visible_videos_for




@login_required
def toggle_like(request, id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    video = get_object_or_404(Video, id=id)
    like, created = Like.objects.get_or_create(user=request.user, video=video)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        notify(recipient=video.author, actor=request.user, kind="like", target=video)

    return JsonResponse({
        "liked": liked,
        "count": video.likes.count(),
    })


def liked_videos(request, username):
    profile_user = get_object_or_404(User, username=username)

    is_owner = request.user.is_authenticated and request.user == profile_user

    if not is_owner and not profile_user.profile.likes_public:
        raise Http404("This user's likes are private.")

    likes = Like.objects.filter(
        user=profile_user,
        video__in=visible_videos_for(request.user),
    ).select_related("video", "video__author")

    return render(
        request,
        "Video/liked_videos.html",
        {
            "profile_user": profile_user,
            "likes": likes,
            "is_owner": is_owner,
        },
    )


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
    paginate_by = 12
    
    def get_queryset(self):
        return visible_videos_for(self.request.user).order_by("-created")


class VideoDetailView(DetailView):
    model = Video
    template_name = "Video/video_details.html"
    context_object_name = "video"

    def get_object(self):
        return get_object_or_404(
            visible_videos_for(self.request.user),
            id=self.kwargs.get("id"),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context["user_has_liked"] = Like.objects.filter(
                user=self.request.user, video=self.object
            ).exists()

        context["is_bookmarked"] = is_bookmarked_by(
            self.request.user,
            self.object,
        )

        content_type = ContentType.objects.get_for_model(Video)
        context["content_type_id"] = content_type.id
        context["comments"] = Comment.objects.filter(
            content_type=content_type,
            object_id=self.object.id,
            is_hidden=False,
        ).select_related("author")
        context["comment_form"] = CommentForm()

        return context


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