from rest_framework.routers import DefaultRouter
from .api import CategoryViewSet, SupplierViewSet, ProductViewSet, TransactionViewSet
router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("suppliers", SupplierViewSet)
# These viewsets build their querysets dynamically, so DRF needs explicit names.
router.register("products", ProductViewSet, basename="product")
router.register("stock-movements", TransactionViewSet, basename="stock-movement")
router.register("transactions", TransactionViewSet, basename="transaction")
urlpatterns = router.urls
