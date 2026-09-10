from django import forms
from .models import Category, Product, Supplier, InventoryTransaction
class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values(): field.widget.attrs["class"] = "form-control"
class ProductForm(StyledModelForm):
    class Meta: model = Product; fields = ["name", "sku", "description", "category", "supplier", "price", "quantity", "reorder_level", "image"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Quantity is changed only by a stock operation, never by editing a product.
        if self.instance and self.instance.pk:
            self.fields.pop("quantity")
class CategoryForm(StyledModelForm):
    class Meta: model = Category; fields = ["name"]
class SupplierForm(StyledModelForm):
    class Meta: model = Supplier; fields = ["name", "contact_person", "email", "phone", "address"]
class StockTransactionForm(StyledModelForm):
    class Meta: model = InventoryTransaction; fields = ["product", "transaction_type", "quantity", "reason"]
    def save(self, user, commit=True):
        return InventoryTransaction.record(user=user, **self.cleaned_data)
