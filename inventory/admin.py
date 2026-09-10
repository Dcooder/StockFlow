from django.contrib import admin
from .models import Category, Supplier, Product, InventoryTransaction
admin.site.register([Category, Supplier, Product, InventoryTransaction])
