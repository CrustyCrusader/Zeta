from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.urls import reverse

from accounts.models import Follow, User

from .models import Video
from .utils import visible_videos_for


class VisibleVideosTests(TestCase):
	def setUp(self):
		self.author = User.objects.create_user(
			username="author",
			email="author@example.com",
			password="test-password",
		)
		self.follower = User.objects.create_user(
			username="follower",
			email="follower@example.com",
			password="test-password",
		)
		self.other_user = User.objects.create_user(
			username="other",
			email="other@example.com",
			password="test-password",
		)
		self.public_video = self.create_video(Video.Visibility.PUBLIC)
		self.followers_video = self.create_video(Video.Visibility.FOLLOWERS)
		self.private_video = self.create_video(Video.Visibility.PRIVATE)

	def create_video(self, visibility):
		return Video.objects.create(
			author=self.author,
			title=visibility,
			video="videos/test.mp4",
			thumbnail="thumbnails/test.png",
			visibility=visibility,
		)

	def test_anonymous_users_only_see_public_videos(self):
		visible_ids = set(
			visible_videos_for(AnonymousUser()).values_list("id", flat=True)
		)

		self.assertEqual(visible_ids, {self.public_video.id})

	def test_follower_sees_public_and_followers_only_videos(self):
		Follow.objects.create(follower=self.follower, following=self.author)

		visible_ids = set(
			visible_videos_for(self.follower).values_list("id", flat=True)
		)

		self.assertEqual(
			visible_ids,
			{self.public_video.id, self.followers_video.id},
		)

	def test_author_sees_all_own_videos(self):
		visible_ids = set(
			visible_videos_for(self.author).values_list("id", flat=True)
		)

		self.assertEqual(
			visible_ids,
			{
				self.public_video.id,
				self.followers_video.id,
				self.private_video.id,
			},
		)

	def test_video_detail_rejects_nonfollowers_for_private_videos(self):
		self.client.force_login(self.other_user)

		response = self.client.get(
			reverse("Video:video_details", kwargs={"id": self.private_video.id})
		)

		self.assertEqual(response.status_code, 404)

	def test_video_detail_allows_followers_only_videos_to_followers(self):
		Follow.objects.create(follower=self.follower, following=self.author)
		self.client.force_login(self.follower)

		response = self.client.get(
			reverse("Video:video_details", kwargs={"id": self.followers_video.id})
		)

		self.assertEqual(response.status_code, 200)

	def test_video_detail_loads_compiled_frontend_bundle(self):
		response = self.client.get(
			reverse("Video:video_details", kwargs={"id": self.public_video.id})
		)

		self.assertContains(response, "js/app.js")
