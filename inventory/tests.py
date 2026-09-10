from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient
from .models import Category, Product, InventoryTransaction
class InventoryWorkflowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("staff", password="safe-password-123")
        self.product = Product.objects.create(name="Keyboard", sku="KB-001", category=Category.objects.create(name="Hardware"), price="10.00", quantity=5)
    def test_stock_in_and_out(self):
        InventoryTransaction.record(product=self.product, transaction_type="IN", quantity=3, reason="Delivery", user=self.user)
        InventoryTransaction.record(product=self.product, transaction_type="OUT", quantity=2, reason="Sale", user=self.user)
        self.product.refresh_from_db(); self.assertEqual(self.product.quantity, 6)
    def test_opening_stock_is_logged_when_product_is_created_from_html_form(self):
        self.client.force_login(self.user)
        response = self.client.post("/products/add/", {"name":"Monitor", "sku":"MN-001", "category":self.product.category_id, "price":"99.99", "quantity":4, "reorder_level":2})
        self.assertRedirects(response, "/products/")
        product = Product.objects.get(sku="MN-001")
        self.assertEqual(product.quantity, 4)
        self.assertTrue(InventoryTransaction.objects.filter(product=product, transaction_type="IN", quantity=4, reason="Opening stock").exists())
    def test_stock_out_cannot_go_negative(self):
        with self.assertRaises(ValidationError): InventoryTransaction.record(product=self.product, transaction_type="OUT", quantity=6, reason="Sale", user=self.user)
    def test_api_requires_login_normal_user_can_create_but_cannot_delete(self):
        api = APIClient(); self.assertEqual(api.get("/api/products/").status_code, 403)
        api.force_login(self.user); self.assertEqual(api.get("/api/products/").status_code, 200)
        self.assertEqual(api.post("/api/products/", {"name":"Mouse", "sku":"MS-1", "category":self.product.category_id, "price":"2.00"}).status_code, 201)
        self.assertEqual(api.delete(f"/api/products/{self.product.pk}/").status_code, 403)
    def test_admin_can_update_and_delete_product(self):
        admin = User.objects.create_user("admin", password="safe-password-123", is_staff=True)
        api = APIClient(); api.force_login(admin)
        self.assertEqual(api.patch(f"/api/products/{self.product.pk}/", {"name":"Updated Keyboard"}).status_code, 200)
        self.assertEqual(api.delete(f"/api/products/{self.product.pk}/").status_code, 204)
