from django.http import HttpResponse
from django.shortcuts import render
from accounts.models import User
from accounts.models import Follow
from Video.models import Video
from Video.utils import visible_videos_for
from blog.models import Article
from itertools import chain


def home_view(request, *args, **kwargs):
    is_following_anyone = False

    if request.user.is_authenticated:
        is_following_anyone = Follow.objects.filter(
            follower=request.user
        ).exists()

    if is_following_anyone:
        following_ids = Follow.objects.filter(
            follower=request.user
        ).values_list("following_id", flat=True)

        videos = visible_videos_for(request.user).filter(
            author_id__in=following_ids
        )
        articles = Article.objects.filter(
            author_id__in=following_ids,
            active=True,
        )
    else:
        # Not logged in, or logged in but following nobody yet —
        # fall back to public activity site-wide.
        videos = visible_videos_for(request.user).filter(
            visibility=Video.Visibility.PUBLIC
        )
        articles = Article.objects.filter(active=True)

    videos = videos.select_related("author").order_by("-created")[:30]
    articles = articles.select_related("author").order_by("-created")[:30]

    # Videos and Articles are different models with different fields,
    # so we can't sort them together in a single database query.
    # Instead, tag each one with a "kind" and merge them in Python,
    # then sort the combined list by date.
    feed_items = list(chain(
        ({"kind": "video", "obj": v, "created": v.created} for v in videos),
        ({"kind": "article", "obj": a, "created": a.created} for a in articles),
    ))

    feed_items.sort(key=lambda item: item["created"], reverse=True)
    feed_items = feed_items[:30]

    return render(
        request,
        "home.html",
        {
            "feed_items": feed_items,
            "is_following_anyone": is_following_anyone,
        },
    )


def contact_view(request, *args, **kwargs):
    return render(request, "contact.html", {})


def about_view(request, *args, **kwargs):
    my_context = {
        "title": "abc this is about us",
        "this_is_true": True,
        "my_number": 123,
        "my_list": [1313, 4231, 312, "Abc"],
        "my_html": "<h1>Hello World</h1>",
    }
    return render(request, "about.html", my_context)


def social_view(request, *args, **kwargs):
    return HttpResponse("<h1>Social Page</h1>")


def user_search(request):
    query = request.GET.get("q", "").strip()

    users = User.objects.none()

    if query:
        users = User.objects.filter(
            username__icontains=query
        ).order_by("username")

    return render(
        request,
        "pages/user_search.html",
        {
            "query": query,
            "users": users,
        },
    )