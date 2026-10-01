from django.db.models import Q

from accounts.models import Follow

from .models import Video


def visible_videos_for(user):
    videos = Video.objects.select_related("author")

    if not user.is_authenticated:
        return videos.filter(visibility=Video.Visibility.PUBLIC)

    followed_authors = Follow.objects.filter(
        follower=user
    ).values("following_id")

    return videos.filter(
        Q(visibility=Video.Visibility.PUBLIC)
        | Q(
            visibility=Video.Visibility.FOLLOWERS,
            author_id__in=followed_authors,
        )
        | Q(author=user)
    )