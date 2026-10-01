from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase
from django.urls import reverse

from accounts.models import User
from Video.models import Video
from blog.models import Article
from comments.models import Comment
from products.models import Product

from .admin import hide_content
from .models import Report
from .utils import get_reportable_object


class ReportWorkflowTests(TestCase):
    def setUp(self):
        self.reporter = User.objects.create_user(
            username="reporter",
            email="reporter@example.com",
            password="test-password",
        )
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="test-password",
        )
        self.video = Video.objects.create(
            author=self.owner,
            title="Public clip",
            video="videos/public.mp4",
            thumbnail="thumbnails/public.png",
            visibility=Video.Visibility.PUBLIC,
        )
        self.article = Article.objects.create(
            author=self.owner,
            title="Public story",
            content="A story.",
            active=True,
        )
        self.product = Product.objects.create(
            owner=self.owner,
            title="Public product",
            kind=Product.Kind.PRODUCT,
            price="12.00",
        )
        self.comment = Comment.objects.create(
            author=self.owner,
            content_type=ContentType.objects.get_for_model(Video),
            object_id=self.video.pk,
            content="A public comment.",
        )
        self.client.force_login(self.reporter)

    def report_url(self, model_name, target):
        return reverse(
            "reports:create",
            kwargs={"model_name": model_name, "object_id": target.pk},
        )

    def test_user_can_report_each_supported_content_type(self):
        targets = [
            ("video", self.video),
            ("article", self.article),
            ("product", self.product),
            ("comment", self.comment),
        ]

        for model_name, target in targets:
            with self.subTest(model=model_name):
                response = self.client.post(
                    self.report_url(model_name, target),
                    {"reason": Report.Reason.SPAM, "details": "Please review this."},
                )
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, "reports/submitted.html")

        self.assertEqual(Report.objects.filter(reporter=self.reporter).count(), 4)
        self.assertTrue(
            Report.objects.filter(status=Report.Status.PENDING).exists()
        )

    def test_duplicate_report_is_not_created(self):
        url = self.report_url("video", self.video)
        data = {"reason": Report.Reason.HARASSMENT}

        self.client.post(url, data)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 409)
        self.assertContains(response, "already reported", status_code=409)
        self.assertEqual(Report.objects.filter(reporter=self.reporter).count(), 1)

    def test_users_cannot_report_unsupported_own_or_hidden_content(self):
        own_content = Video.objects.create(
            author=self.reporter,
            title="My clip",
            video="videos/mine.mp4",
            thumbnail="thumbnails/mine.png",
        )
        unsupported = self.client.get(
            reverse(
                "reports:create",
                kwargs={"model_name": "user", "object_id": self.owner.pk},
            )
        )
        own_report = self.client.get(self.report_url("video", own_content))
        self.video.visibility = Video.Visibility.PRIVATE
        self.video.save(update_fields=["visibility"])
        hidden_report = self.client.get(self.report_url("video", self.video))

        self.assertEqual(unsupported.status_code, 404)
        self.assertEqual(own_report.status_code, 404)
        self.assertEqual(hidden_report.status_code, 404)

    def test_hidden_article_and_product_cannot_be_reported(self):
        self.article.active = False
        self.article.save(update_fields=["active"])
        self.product.is_hidden = True
        self.product.save(update_fields=["is_hidden"])

        self.assertEqual(self.client.get(self.report_url("article", self.article)).status_code, 404)
        self.assertEqual(self.client.get(self.report_url("product", self.product)).status_code, 404)

    def test_hidden_content_disappears_from_public_pages(self):
        self.article.active = False
        self.article.save(update_fields=["active"])
        self.product.is_hidden = True
        self.product.save(update_fields=["is_hidden"])
        self.comment.is_hidden = True
        self.comment.save(update_fields=["is_hidden"])

        self.assertEqual(
            self.client.get(self.article.get_absolute_url()).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(self.product.get_absolute_url()).status_code,
            404,
        )
        video_response = self.client.get(self.video.get_absolute_url())
        self.assertNotContains(video_response, self.comment.content)

    def test_other_users_see_report_links_on_detail_pages(self):
        detail_pages = [
            self.video.get_absolute_url(),
            self.article.get_absolute_url(),
            self.product.get_absolute_url(),
        ]

        for path in detail_pages:
            with self.subTest(path=path):
                self.assertContains(self.client.get(path), "report-content-link")

    def test_admin_hide_action_hides_content_and_resolves_reports(self):
        class ActionAdmin:
            def message_user(self, request, message, level):
                self.message = message

        targets = [self.video, self.article, self.product, self.comment]
        reports = [
            Report.objects.create(
                reporter=self.reporter,
                content_type=ContentType.objects.get_for_model(target),
                object_id=target.pk,
                reason=Report.Reason.OTHER,
            )
            for target in targets
        ]
        request = RequestFactory().post("/admin/reports/report/")
        admin_action = ActionAdmin()

        hide_content(
            admin_action,
            request,
            Report.objects.filter(pk__in=[report.pk for report in reports]),
        )

        self.video.refresh_from_db()
        self.article.refresh_from_db()
        self.product.refresh_from_db()
        self.comment.refresh_from_db()
        self.assertEqual(self.video.visibility, Video.Visibility.PRIVATE)
        self.assertFalse(self.article.active)
        self.assertTrue(self.product.is_hidden)
        self.assertTrue(self.comment.is_hidden)
        self.assertFalse(
            Report.objects.filter(status=Report.Status.PENDING).exists()
        )

    def test_report_form_requires_login_and_post(self):
        url = self.report_url("video", self.video)
        self.client.logout()
        self.assertEqual(self.client.get(url).status_code, 302)

        self.client.force_login(self.reporter)
        self.assertEqual(self.client.get(url).status_code, 200)