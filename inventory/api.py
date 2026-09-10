from rest_framework import viewsets
from .models import Category, Supplier, Product, InventoryTransaction
from .permissions import AdminWriteOrAuthenticatedCreate, TransactionPermission
from .serializers import CategorySerializer, SupplierSerializer, ProductSerializer, TransactionSerializer
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all(); serializer_class = CategorySerializer; permission_classes = [AdminWriteOrAuthenticatedCreate]
class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all(); serializer_class = SupplierSerializer; permission_classes = [AdminWriteOrAuthenticatedCreate]
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer; permission_classes = [AdminWriteOrAuthenticatedCreate]
    def get_queryset(self): return Product.objects.select_related("category", "supplier")
class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer; permission_classes = [TransactionPermission]
    def get_queryset(self): return InventoryTransaction.objects.select_related("product", "user")
