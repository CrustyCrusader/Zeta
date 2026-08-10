from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User, Follow

from .forms import ProfileForm
from .models import Profile


@login_required
def profile_detail(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    videos = request.user.videos.all().order_by("-created")

    return render(
        request,
        "profiles/profile_detail.html",
        {
            "profile": profile,
            "videos": videos,
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
    profile_user = get_object_or_404(
        User,
        username=username,
    )

    profile, created = Profile.objects.get_or_create(
        user=profile_user
    )

    videos = profile_user.videos.all().order_by("-created")

    is_following = False

    if request.user.is_authenticated:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=profile_user,
        ).exists()

    return render(
        request,
        "profiles/public_profile.html",
        {
            "profile": profile,
            "profile_user": profile_user,
            "videos": videos,
            "is_following": is_following,
            "follower_count": profile_user.followers.count(),
            "following_count": profile_user.following.count(),
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

