from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RegistrationForm
from .models import Follow, User


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegistrationForm()

    return render(request, "accounts/register.html", {"form": form})

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)

    if user_to_follow != request.user:
        Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow,
        )

    return redirect("public_profile", username=username)


@login_required
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)

    Follow.objects.filter(
        follower=request.user,
        following=user_to_unfollow,
    ).delete()

    return redirect("public_profile", username=username)


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    next_page = "home"