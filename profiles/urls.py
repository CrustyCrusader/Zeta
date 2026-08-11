from django.urls import path

from .views import (
    profile_detail,
    profile_edit,
    public_profile,
    follow_user,
    unfollow_user,
    followers_list,
    following_list,
)


urlpatterns = [
    path("", profile_detail, name="profile"),

    path(
        "edit/",
        profile_edit,
        name="profile_edit",
    ),

    path(
        "<str:username>/",
        public_profile,
        name="public_profile",
    ),

    path(
        "<str:username>/follow/",
        follow_user,
        name="follow_user",
    ),

    path(
        "<str:username>/unfollow/",
        unfollow_user,
        name="unfollow_user",
    ),

    path(
        "<str:username>/followers/",
        followers_list,
        name="followers_list",
    ),

    path(
        "<str:username>/following/",
        following_list,
        name="following_list",
    ),
]