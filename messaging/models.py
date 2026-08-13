from django.conf import settings
from django.db import models


class Conversation(models.Model):
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="conversations",
    )

    is_group = models.BooleanField(default=False)
    name = models.CharField(max_length=120, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_conversations",
        null=True,
    )

    created = models.DateTimeField(auto_now_add=True)

    def get_display_name(self, viewer):
        """
        Group chats show their name. 1:1 chats show the other
        person's username — there's no stored "title" for those,
        so we look up whoever isn't the person viewing it.
        """
        if self.is_group:
            return self.name or "Group Chat"

        other = self.participants.exclude(id=viewer.id).first()
        return other.username if other else "Conversation"

    def __str__(self):
        return self.name or f"Conversation {self.id}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("messaging:conversation_detail", kwargs={"id": self.id})


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )

    content = models.TextField(max_length=2000)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created"]

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"