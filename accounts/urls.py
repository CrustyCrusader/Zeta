from django.urls import path

from .views import (
    UserLoginView,
    UserLogoutView,
    register,
    follow_user,
    unfollow_user,
)

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),

    path(
        "follow/<str:username>/",
        follow_user,
        name="follow_user",
    ),

    path(
        "unfollow/<str:username>/",
        unfollow_user,
        name="unfollow_user",
    ),
]

