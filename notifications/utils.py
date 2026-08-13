from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.contenttypes.models import ContentType

from .models import Notification


def notify(recipient, actor, kind, target=None):
    if recipient == actor:
        return

    content_type = None
    object_id = None

    if target is not None:
        content_type = ContentType.objects.get_for_model(target)
        object_id = target.id

    Notification.objects.create(
        recipient=recipient,
        actor=actor,
        kind=kind,
        content_type=content_type,
        object_id=object_id,
    )

    unread_count = Notification.objects.filter(
        recipient=recipient, is_read=False
    ).count()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notifications_{recipient.id}",
        {
            "type": "notify",  # maps to the `notify` method on the consumer
            "unread_count": unread_count,
            "kind": kind,
            "actor": actor.username,
        },
    )