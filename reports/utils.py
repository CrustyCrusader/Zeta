from django.http import Http404
from django.shortcuts import get_object_or_404

from Video.models import Video
from Video.utils import visible_videos_for
from blog.models import Article
from comments.models import Comment
from products.models import Product


REPORTABLE_MODELS = {
    "video": Video,
    "article": Article,
    "product": Product,
    "comment": Comment,
}


def is_visible_to(user, target, visited=None):
    if visited is None:
        visited = set()
    key = (type(target), target.pk)
    if key in visited:
        return False
    visited.add(key)

    if isinstance(target, Video):
        return visible_videos_for(user).filter(pk=target.pk).exists()
    if isinstance(target, Article):
        return target.active or target.author == user
    if isinstance(target, Product):
        return not target.is_hidden or target.owner == user
    if isinstance(target, Comment):
        parent = target.content_object
        return (
            not target.is_hidden
            and parent is not None
            and is_visible_to(user, parent, visited)
        )
    return False


def get_reportable_object(user, model_name, object_id):
    model = REPORTABLE_MODELS.get(model_name)
    if model is None:
        raise Http404

    target = get_object_or_404(model, pk=object_id)
    if not is_visible_to(user, target):
        raise Http404

    owner = getattr(target, "author", None) or getattr(target, "owner", None)
    if owner == user:
        raise Http404

    return target


def get_report_target_url(target):
    if isinstance(target, Comment):
        parent = target.content_object
        if parent is None:
            raise Http404
        return parent.get_absolute_url()
    return target.get_absolute_url()