from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404

from Video.models import Video
from Video.utils import visible_videos_for
from blog.models import Article
from products.models import Product

from .models import Bookmark


BOOKMARKABLE_MODELS = {
    "video": Video,
    "article": Article,
    "product": Product,
}


def get_bookmark_target(user, model_name, object_id):
    model = BOOKMARKABLE_MODELS.get(model_name)
    if model is None:
        raise Http404

    target = get_object_or_404(model, pk=object_id)
    if model is Video and not visible_videos_for(user).filter(pk=target.pk).exists():
        raise Http404
    if model is Article and not target.active and target.author != user:
        raise Http404
    if model is Product and target.is_hidden and target.owner != user:
        raise Http404

    return target


def is_bookmarked_by(user, target):
    if not user.is_authenticated:
        return False

    return Bookmark.objects.filter(
        user=user,
        content_type=ContentType.objects.get_for_model(target),
        object_id=target.pk,
    ).exists()