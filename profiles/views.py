from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Follow, User

from .forms import ProfileForm
from .models import Profile


@login_required
def profile_detail(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    videos = request.user.videos.all().order_by("-created")
    
    articles = request.user.articles.filter(active=True).order_by("-created")
    
    likes_count = request.user.video_likes.count()

    return render(
        request,
        "profiles/profile_detail.html",
    {
        "profile": profile,
        "videos": videos,
        "articles": articles,
        "likes_count": likes_count,
    },
)

@login_required
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile,
        )

        if form.is_valid():
            form.save()
            return redirect("profile")

    else:
        form = ProfileForm(instance=profile)

    return render(
        request,
        "profiles/profile_edit.html",
        {"form": form},
    )



def public_profile(request, username):
    user = get_object_or_404(
        User,
        username=username,
    )

    profile, created = Profile.objects.get_or_create(
        user=user
    )

    videos = user.videos.all().order_by("-created")
    
    articles = user.articles.filter(active=True).order_by("-created")

    follower_count = user.followers.count()
    following_count = user.following.count()
    likes_count = user.video_likes.count()

    is_following = False
    is_owner = request.user.is_authenticated and request.user == user

    if request.user.is_authenticated:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=user,
        ).exists()

    return render(
    request,
    "profiles/public_profile.html",
    {
        "profile": profile,
        "profile_user": user,
        "videos": videos,
        "articles": articles,
        "follower_count": follower_count,
        "following_count": following_count,
        "likes_count": likes_count,
        "is_following": is_following,
        "is_owner": is_owner,
    },
)




@login_required
def follow_user(request, username):
    profile_user = get_object_or_404(
        User,
        username=username,
    )

    if request.user != profile_user:
        Follow.objects.get_or_create(
            follower=request.user,
            following=profile_user,
        )

    return redirect(
        "public_profile",
        username=profile_user.username,
    )


@login_required
def unfollow_user(request, username):
    profile_user = get_object_or_404(
        User,
        username=username,
    )

    Follow.objects.filter(
        follower=request.user,
        following=profile_user,
    ).delete()

    return redirect(
        "public_profile",
        username=profile_user.username,
    )

def followers_list(request, username):
    profile_user = get_object_or_404(
        User,
        username=username,
    )

    follows = (
        Follow.objects
        .filter(following=profile_user)
        .select_related("follower")
        .order_by("-created")
    )

    followers = [follow.follower for follow in follows]

    return render(
        request,
        "profiles/followers.html",
        {
            "profile_user": profile_user,
            "followers": followers,
        },
    )


def following_list(request, username):
    profile_user = get_object_or_404(
        User,
        username=username,
    )

    follows = (
        Follow.objects
        .filter(follower=profile_user)
        .select_related("following")
        .order_by("-created")
    )

    following = [follow.following for follow in follows]

    return render(
        request,
        "profiles/following.html",
        {
            "profile_user": profile_user,
            "following": following,
        },
    )