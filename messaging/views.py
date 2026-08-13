from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.template.loader import render_to_string

from accounts.models import User

from .forms import GroupCreateForm
from .models import Conversation
from .utils import is_mutual_follow


@login_required
def conversation_list(request):
    conversations_qs = request.user.conversations.annotate(
        last_message_at=Max("messages__created")
    ).order_by("-last_message_at")

    conversations = []
    for conversation in conversations_qs:
        conversations.append({
            "conversation": conversation,
            "display_name": conversation.get_display_name(request.user),
            "last_message": conversation.messages.order_by("-created").first(),
        })

    return render(
        request,
        "messaging/conversation_list.html",
        {"conversations": conversations},
    )


@login_required
def start_conversation(request, username):
    other_user = get_object_or_404(User, username=username)

    if other_user == request.user:
        return redirect("messaging:conversation_list")

    if not is_mutual_follow(request.user, other_user):
        return redirect("public_profile", username=username)

    conversation = (
        Conversation.objects.filter(is_group=False, participants=request.user)
        .filter(participants=other_user)
        .first()
    )

    if not conversation:
        conversation = Conversation.objects.create(
            is_group=False, created_by=request.user
        )
        conversation.participants.add(request.user, other_user)

    return redirect("messaging:conversation_detail", id=conversation.id)


@login_required
def create_group(request):
    if request.method == "POST":
        form = GroupCreateForm(request.POST, user=request.user)
        if form.is_valid():
            conversation = Conversation.objects.create(
                is_group=True,
                name=form.cleaned_data["name"],
                created_by=request.user,
            )
            conversation.participants.add(
                request.user, *form.cleaned_data["participants"]
            )
            return redirect("messaging:conversation_detail", id=conversation.id)
    else:
        form = GroupCreateForm(user=request.user)

    return render(request, "messaging/create_group.html", {"form": form})


@login_required
def conversation_detail(request, id):
    conversation = get_object_or_404(Conversation, id=id, participants=request.user)

    recent = list(
        conversation.messages.select_related("sender").order_by("-created")[:50]
    )
    recent.reverse()  # oldest-first for display

    has_more = conversation.messages.count() > 50

    return render(
        request,
        "messaging/conversation_detail.html",
        {
            "conversation": conversation,
            "messages": recent,
            "display_name": conversation.get_display_name(request.user),
            "has_more": has_more,
        },
    )


@login_required
def load_earlier_messages(request, id):
    conversation = get_object_or_404(Conversation, id=id, participants=request.user)
    before_id = request.GET.get("before")

    qs = conversation.messages.select_related("sender").order_by("-created")
    if before_id:
        qs = qs.filter(id__lt=before_id)

    batch = list(qs[:50])
    has_more = qs[50:51].exists()
    batch.reverse()

    html = render_to_string(
        "messaging/_message_items.html", {"messages": batch}, request=request
    )

    return JsonResponse({
        "html": html,
        "has_more": has_more,
        "earliest_id": batch[0].id if batch else None,
    })
    
@login_required
def conversation_panel(request):
    conversations_qs = request.user.conversations.annotate(
        last_message_at=Max("messages__created")
    ).order_by("-last_message_at")

    conversations = []
    for conversation in conversations_qs:
        conversations.append({
            "conversation": conversation,
            "display_name": conversation.get_display_name(request.user),
            "last_message": conversation.messages.order_by("-created").first(),
        })

    html = render_to_string(
        "messaging/_conversation_items.html",
        {"conversations": conversations},
        request=request,
    )
    return JsonResponse({"html": html})


@login_required
def conversation_messages_panel(request, id):
    conversation = get_object_or_404(Conversation, id=id, participants=request.user)
    messages = conversation.messages.select_related("sender").all()

    html = render_to_string(
        "messaging/_message_items.html",
        {"messages": messages},
        request=request,
    )
    return JsonResponse({
        "html": html,
        "display_name": conversation.get_display_name(request.user),
    })