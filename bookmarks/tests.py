from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from Video.models import Video
from blog.models import Article
from products.models import Product

from .models import Bookmark


class BookmarkWorkflowTests(TestCase):
    def setUp(self):
        self.saver = User.objects.create_user(
            username="saver",
            email="saver@example.com",
            password="test-password",
        )
        self.author = User.objects.create_user(
            username="author",
            email="author@example.com",
            password="test-password",
        )
        self.video = Video.objects.create(
            author=self.author,
            title="Community film",
            video="videos/community.mp4",
            thumbnail="thumbnails/community.png",
            visibility=Video.Visibility.PUBLIC,
        )
        self.article = Article.objects.create(
            author=self.author,
            title="A short story",
            content="A story worth keeping.",
        )
        self.product = Product.objects.create(
            owner=self.author,
            title="Handmade notebook",
            kind=Product.Kind.PRODUCT,
            price="18.00",
        )
        self.client.force_login(self.saver)

    def toggle_url(self, model_name, target):
        return reverse(
            "bookmarks:toggle",
            kwargs={"model_name": model_name, "object_id": target.pk},
        )

    def test_user_can_toggle_video_article_and_product_bookmarks(self):
        targets = [
            ("video", self.video),
            ("article", self.article),
            ("product", self.product),
        ]

        for model_name, target in targets:
            with self.subTest(model=model_name):
                response = self.client.post(self.toggle_url(model_name, target))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), {"saved": True})

                response = self.client.post(self.toggle_url(model_name, target))
                self.assertEqual(response.json(), {"saved": False})

        self.assertEqual(Bookmark.objects.filter(user=self.saver).count(), 0)

    def test_unsupported_or_invisible_content_cannot_be_bookmarked(self):
        unsupported = self.client.post(
            reverse(
                "bookmarks:toggle",
                kwargs={"model_name": "user", "object_id": self.author.pk},
            )
        )
        self.assertEqual(unsupported.status_code, 404)

        self.video.visibility = Video.Visibility.PRIVATE
        self.video.save(update_fields=["visibility"])
        private_video = self.client.post(self.toggle_url("video", self.video))
        self.assertEqual(private_video.status_code, 404)

        self.article.active = False
        self.article.save(update_fields=["active"])
        inactive_article = self.client.post(self.toggle_url("article", self.article))
        self.assertEqual(inactive_article.status_code, 404)

    def test_saved_page_only_shows_current_users_visible_bookmarks(self):
        other_product = Product.objects.create(
            owner=self.author,
            title="Not in this collection",
            kind=Product.Kind.SERVICE,
            price="30.00",
        )
        content_type = ContentType.objects.get_for_model(Product)
        Bookmark.objects.create(
            user=self.saver,
            content_type=content_type,
            object_id=self.product.pk,
        )
        Bookmark.objects.create(
            user=self.author,
            content_type=content_type,
            object_id=other_product.pk,
        )

        response = self.client.get(reverse("bookmarks:saved"))

        self.assertContains(response, self.product.title)
        self.assertNotContains(response, other_product.title)
        self.assertContains(response, "Saved for later")

    def test_supported_detail_pages_show_bookmark_controls(self):
        detail_pages = [
            reverse("Video:video_details", kwargs={"id": self.video.pk}),
            reverse("articles:article-detail", kwargs={"id": self.article.pk}),
            reverse("products:product-detail", kwargs={"id": self.product.pk}),
        ]

        for path in detail_pages:
            with self.subTest(path=path):
                self.assertContains(self.client.get(path), "bookmark-toggle")

    def test_saved_page_hides_video_after_it_becomes_private(self):
        Bookmark.objects.create(
            user=self.saver,
            content_type=ContentType.objects.get_for_model(Video),
            object_id=self.video.pk,
        )
        self.video.visibility = Video.Visibility.PRIVATE
        self.video.save(update_fields=["visibility"])

        response = self.client.get(reverse("bookmarks:saved"))

        self.assertNotContains(response, self.video.title)

    def test_hidden_products_cannot_be_saved_or_seen_on_saved_page(self):
        Bookmark.objects.create(
            user=self.saver,
            content_type=ContentType.objects.get_for_model(Product),
            object_id=self.product.pk,
        )
        self.product.is_hidden = True
        self.product.save(update_fields=["is_hidden"])

        response = self.client.get(reverse("bookmarks:saved"))
        toggle_response = self.client.post(self.toggle_url("product", self.product))

        self.assertNotContains(response, self.product.title)
        self.assertEqual(toggle_response.status_code, 404)

    def test_toggle_requires_authentication_and_post(self):
        self.client.logout()
        url = self.toggle_url("video", self.video)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.saver)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)