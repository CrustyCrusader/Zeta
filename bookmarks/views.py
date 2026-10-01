from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from Video.models import Video
from Video.utils import visible_videos_for
from blog.models import Article
from products.models import Product

from .models import Bookmark
from .utils import BOOKMARKABLE_MODELS, get_bookmark_target


@login_required
@require_POST
def toggle_bookmark(request, model_name, object_id):
    target = get_bookmark_target(request.user, model_name, object_id)
    content_type = ContentType.objects.get_for_model(target)
    bookmark = Bookmark.objects.filter(
        user=request.user,
        content_type=content_type,
        object_id=target.pk,
    ).first()

    if bookmark:
        bookmark.delete()
        saved = False
    else:
        Bookmark.objects.create(
            user=request.user,
            content_type=content_type,
            object_id=target.pk,
        )
        saved = True

    return JsonResponse({"saved": saved})


@login_required
def saved_items(request):
    content_types = ContentType.objects.get_for_models(*BOOKMARKABLE_MODELS.values())
    bookmarks = (
        request.user.bookmarks
        .filter(content_type__in=content_types.values())
        .select_related("content_type")
        .prefetch_related("content_object")
    )
    visible_video_ids = set(
        visible_videos_for(request.user).values_list("pk", flat=True)
    )
    saved = []

    for bookmark in bookmarks:
        target = bookmark.content_object
        if target is None:
            continue

        model_name = bookmark.content_type.model
        if model_name == "video" and target.pk not in visible_video_ids:
            continue
        if model_name == "article" and not target.active and target.author != request.user:
            continue
        if model_name == "product" and target.is_hidden and target.owner != request.user:
            continue

        saved.append({
            "bookmark": bookmark,
            "object": target,
            "kind": model_name,
            "kind_label": {
                "video": "Video",
                "article": "Story",
                "product": "Market offer",
            }[model_name],
        })

    return render(request, "bookmarks/saved_items.html", {"saved_items": saved})