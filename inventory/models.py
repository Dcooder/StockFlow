from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["name"]
    def __str__(self): return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=150, unique=True)
    contact_person = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["name"]
    def __str__(self): return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="products", null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)
    image = models.ImageField(upload_to="products/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering = ["name"]; indexes = [models.Index(fields=["sku"]), models.Index(fields=["name"])]
    @property
    def is_low_stock(self): return self.quantity <= self.reorder_level
    def __str__(self): return f"{self.name} ({self.sku})"

class InventoryTransaction(models.Model):
    class TransactionType(models.TextChoices): IN = "IN", "Stock in"; OUT = "OUT", "Stock out"
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="transactions")
    transaction_type = models.CharField(max_length=3, choices=TransactionType.choices)
    quantity = models.PositiveIntegerField()
    reason = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="inventory_transactions")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["-created_at"]
    def clean(self):
        if self.quantity <= 0: raise ValidationError({"quantity": "Quantity must be greater than zero."})
    @classmethod
    def record(cls, *, product, transaction_type, quantity, reason, user):
        if quantity <= 0: raise ValidationError({"quantity": "Quantity must be greater than zero."})
        with transaction.atomic():
            locked = Product.objects.select_for_update().get(pk=product.pk)
            if transaction_type == cls.TransactionType.OUT and locked.quantity < quantity:
                raise ValidationError({"quantity": "Insufficient stock for this transaction."})
            delta = quantity if transaction_type == cls.TransactionType.IN else -quantity
            Product.objects.filter(pk=locked.pk).update(quantity=F("quantity") + delta)
            return cls.objects.create(product=locked, transaction_type=transaction_type, quantity=quantity, reason=reason, user=user)
