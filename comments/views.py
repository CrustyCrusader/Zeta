from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from .models import Comment
from .forms import CommentForm


from notifications.utils import notify

@login_required
def add_comment(request, content_type_id, object_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    content_type = get_object_or_404(ContentType, id=content_type_id)
    model = content_type.model_class()
    obj = get_object_or_404(model, id=object_id)

    form = CommentForm(request.POST)

    if not form.is_valid():
        return JsonResponse({"error": "Comment cannot be empty."}, status=400)

    comment = form.save(commit=False)
    comment.author = request.user
    comment.content_type = content_type
    comment.object_id = obj.id
    comment.save()

    # obj.author covers Video and Article — both have that field
    if hasattr(obj, "author") and obj.author:
        notify(recipient=obj.author, actor=request.user, kind="comment", target=obj)

    html = render_to_string(
        "comments/_comment.html",
        {"comment": comment, "request": request},
    )

    count = Comment.objects.filter(
        content_type=content_type,
        object_id=obj.id,
        is_hidden=False,
    ).count()

    return JsonResponse({"html": html, "count": count})


@login_required
def delete_comment(request, comment_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author != request.user:
        return JsonResponse({"error": "Not allowed."}, status=403)

    content_type = comment.content_type
    object_id = comment.object_id
    comment.delete()

    count = Comment.objects.filter(
        content_type=content_type,
        object_id=object_id,
        is_hidden=False,
    ).count()

    return JsonResponse({"deleted": True, "count": count})