from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import Notification


class NotificationReadTests(TestCase):
	def setUp(self):
		self.recipient = User.objects.create_user(
			username="recipient",
			email="recipient@example.com",
			password="test-password",
		)
		self.actor = User.objects.create_user(
			username="actor",
			email="actor@example.com",
			password="test-password",
		)
		self.notification = Notification.objects.create(
			recipient=self.recipient,
			actor=self.actor,
			kind=Notification.Kind.FOLLOW,
		)
		self.client.force_login(self.recipient)

	def test_notification_list_renders_unread_state_before_marking_read(self):
		response = self.client.get(reverse("notifications:notification_list"))

		self.assertContains(response, "notification-item unread")
		self.notification.refresh_from_db()
		self.assertTrue(self.notification.is_read)

	def test_notification_panel_renders_unread_state_before_marking_read(self):
		response = self.client.get(reverse("notifications:panel"))

		self.assertIn("notification-item unread", response.json()["html"])
		self.notification.refresh_from_db()
		self.assertTrue(self.notification.is_read)
