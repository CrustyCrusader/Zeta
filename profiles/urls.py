from django.urls import path

from .views import (
    profile_detail,
    profile_edit,
    public_profile,
    follow_user,
    unfollow_user,
)


urlpatterns = [
    path("", profile_detail, name="profile"),
    path("edit/", profile_edit, name="profile_edit"),
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
]

