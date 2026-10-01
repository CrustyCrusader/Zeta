from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import Conversation, Message


class ConversationPageTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username="chat-user",
			email="chat-user@example.com",
			password="test-password",
		)
		self.conversation = Conversation.objects.create(
			is_group=False,
			created_by=self.user,
		)
		self.conversation.participants.add(self.user)
		self.client.force_login(self.user)

	def test_chat_page_loads_bundle_and_earlier_message_cursor(self):
		Message.objects.bulk_create([
			Message(
				conversation=self.conversation,
				sender=self.user,
				content=f"Message {index}",
			)
			for index in range(51)
		])

		response = self.client.get(
			reverse(
				"messaging:conversation_detail",
				kwargs={"id": self.conversation.id},
			)
		)

		self.assertContains(response, "js/app.js")
		self.assertContains(response, "id=\"chat-status\"")
		self.assertContains(response, "data-url=\"/messages/1/earlier/\"")
		self.assertContains(response, "data-before-id=")
