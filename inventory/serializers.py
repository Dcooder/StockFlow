from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from .models import Category, Supplier, Product, InventoryTransaction
class CategorySerializer(serializers.ModelSerializer):
    class Meta: model = Category; fields = ["id", "name", "created_at"]
class SupplierSerializer(serializers.ModelSerializer):
    class Meta: model = Supplier; fields = ["id", "name", "contact_person", "email", "phone", "address", "created_at"]
class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    class Meta:
        model = Product
        fields = ["id", "name", "sku", "description", "category", "category_name", "supplier", "supplier_name", "price", "quantity", "reorder_level", "image", "is_low_stock", "created_at", "updated_at"]
        read_only_fields = ["quantity"]
class TransactionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    class Meta: model = InventoryTransaction; fields = ["id", "product", "product_name", "transaction_type", "quantity", "reason", "user", "user_name", "created_at"]; read_only_fields = ["user"]
    def create(self, validated_data):
        try: return InventoryTransaction.record(user=self.context["request"].user, **validated_data)
        except DjangoValidationError as error: raise serializers.ValidationError(error.message_dict)
