from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from .models import Notification


@login_required
def notification_list(request):
    notifications_qs = request.user.notifications.select_related("actor", "content_type")
    notifications_qs.filter(is_read=False).update(is_read=True)

    paginator = Paginator(notifications_qs, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "notifications/notification_list.html",
        {"notifications": page_obj, "page_obj": page_obj},
    )


@login_required
def notification_panel(request):
    # Unchanged — the side panel stays unpaginated, just capped at 15 most recent
    notifications = request.user.notifications.select_related("actor", "content_type")[:15]
    request.user.notifications.filter(is_read=False).update(is_read=True)

    html = render_to_string(
        "notifications/_notification_items.html",
        {"notifications": notifications},
        request=request,
    )
    return JsonResponse({"html": html, "unread_count": 0})