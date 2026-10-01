from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import Product


class ProductStoreTests(TestCase):
	def setUp(self):
		self.seller = User.objects.create_user(
			username="maker",
			email="maker@example.com",
			password="test-password",
		)
		self.other_user = User.objects.create_user(
			username="visitor",
			email="visitor@example.com",
			password="test-password",
		)

	def create_product(self, **overrides):
		values = {
			"owner": self.seller,
			"title": "Handmade mug",
			"kind": Product.Kind.PRODUCT,
			"description": "A ceramic mug.",
			"price": "24.00",
		}
		values.update(overrides)
		return Product.objects.create(**values)

	def test_store_search_and_kind_filter(self):
		product = self.create_product()
		service = self.create_product(
			title="Studio photography",
			kind=Product.Kind.SERVICE,
		)

		response = self.client.get(
			reverse("products:product-list"),
			{"q": "studio", "kind": Product.Kind.SERVICE},
		)

		self.assertContains(response, service.title)
		self.assertNotContains(response, product.title)
		self.assertContains(response, "1 offer")

	def test_create_listing_assigns_authenticated_owner(self):
		self.client.force_login(self.seller)

		response = self.client.post(
			reverse("products:product-create"),
			{
				"title": "Brand photography",
				"kind": Product.Kind.SERVICE,
				"description": "Product photography for small makers.",
				"price": "150.00",
				"featured": "on",
			},
		)

		product = Product.objects.get(title="Brand photography")
		self.assertEqual(product.owner, self.seller)
		self.assertRedirects(response, product.get_absolute_url())

	def test_only_owner_can_update_or_delete_listing(self):
		product = self.create_product()
		self.client.force_login(self.other_user)

		update_response = self.client.get(
			reverse("products:product-update", kwargs={"id": product.id})
		)
		delete_response = self.client.post(
			reverse("products:product-delete", kwargs={"id": product.id})
		)

		self.assertEqual(update_response.status_code, 404)
		self.assertEqual(delete_response.status_code, 404)
		self.assertTrue(Product.objects.filter(id=product.id).exists())

	def test_owner_can_update_and_delete_with_post(self):
		product = self.create_product()
		self.client.force_login(self.seller)

		update_response = self.client.post(
			reverse("products:product-update", kwargs={"id": product.id}),
			{
				"title": "Updated mug",
				"kind": Product.Kind.PRODUCT,
				"description": "Updated details.",
				"price": "28.00",
				"featured": "on",
			},
		)
		product.refresh_from_db()
		self.assertRedirects(update_response, product.get_absolute_url())
		self.assertEqual(product.title, "Updated mug")

		delete_response = self.client.post(
			reverse("products:product-delete", kwargs={"id": product.id})
		)
		self.assertRedirects(delete_response, reverse("products:product-list"))
		self.assertFalse(Product.objects.filter(id=product.id).exists())
