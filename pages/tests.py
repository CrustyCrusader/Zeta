from django.test import TestCase
from django.urls import reverse

from accounts.models import User


class SharedLayoutTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username="layout-user",
			email="layout-user@example.com",
			password="test-password",
		)

	def test_home_uses_dashboard_layout(self):
		response = self.client.get(reverse("home"))

		self.assertContains(response, "home-dashboard")
		self.assertContains(response, "home-market-panel")
		self.assertContains(response, "site-footer")

	def test_signed_in_app_pages_share_the_site_shell(self):
		self.client.force_login(self.user)
		page_names = [
			"profile",
			"profile_edit",
			"Video:video_upload",
			"articles:article-create",
			"products:product-create",
			"notifications:notification_list",
			"messaging:conversation_list",
			"messaging:create_group",
			"user_search",
		]

		for page_name in page_names:
			with self.subTest(page=page_name):
				response = self.client.get(reverse(page_name))
				self.assertEqual(response.status_code, 200)
				self.assertContains(response, "site-footer")
