from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.views.generic.base import TemplateView
from .forms import CategoryForm, ProductForm, StockTransactionForm, SupplierForm
from .models import Category, InventoryTransaction, Product, Supplier
from .permissions import AdminRequiredMixin
class DashboardView(LoginRequiredMixin, TemplateView):
 template_name="inventory/dashboard.html"
 def get_context_data(self,**kwargs):
  c=super().get_context_data(**kwargs); p=Product.objects.select_related("category","supplier"); c.update(total_products=p.count(),total_categories=Category.objects.count(),total_suppliers=Supplier.objects.count(),low_stock=p.filter(quantity__lte=F("reorder_level")),recent_transactions=InventoryTransaction.objects.select_related("product","user")[:8],total_stock_value=sum((x.price*x.quantity for x in p),start=0)); return c
class ProductListView(LoginRequiredMixin,ListView):
 model=Product;template_name="inventory/product_list.html";context_object_name="products";paginate_by=12
 def get_queryset(self):
  qs=Product.objects.select_related("category","supplier"); q=self.request.GET.get("q","")
  if q:qs=qs.filter(Q(name__icontains=q)|Q(sku__icontains=q))
  if x:=self.request.GET.get("category"):qs=qs.filter(category_id=x)
  if self.request.GET.get("status")=="low":qs=qs.filter(quantity__gt=0,quantity__lte=F("reorder_level"))
  if self.request.GET.get("status")=="out":qs=qs.filter(quantity=0)
  return qs
 def get_context_data(self,**kwargs):return super().get_context_data(categories=Category.objects.all(),**kwargs)
class ProductDetailView(LoginRequiredMixin,DetailView):
 model=Product;template_name="inventory/product_detail.html"
 def get_context_data(self,**kwargs):return super().get_context_data(recent_movements=self.object.transactions.select_related("user")[:5],**kwargs)
class ProductCreateView(LoginRequiredMixin,CreateView):
 model=Product;form_class=ProductForm;template_name="inventory/form.html";success_url="/products/";extra_context={"title":"Add product"}
 def form_valid(self,f):
  opening_quantity=f.cleaned_data["quantity"]
  f.instance.quantity=0
  with transaction.atomic():
   self.object=f.save()
   if opening_quantity:
    InventoryTransaction.record(product=self.object,transaction_type=InventoryTransaction.TransactionType.IN,quantity=opening_quantity,reason="Opening stock",user=self.request.user)
  messages.success(self.request,"Product created successfully. Opening stock was added to activity automatically.")
  return redirect(self.get_success_url())
class ProductUpdateView(LoginRequiredMixin,AdminRequiredMixin,UpdateView):
 model=Product;form_class=ProductForm;template_name="inventory/form.html";success_url="/products/";extra_context={"title":"Edit product"}
class ProductDeleteView(LoginRequiredMixin,AdminRequiredMixin,DeleteView):
 model=Product;template_name="inventory/confirm_delete.html";success_url="/products/"
class CategoryListView(LoginRequiredMixin,ListView):model=Category;template_name="inventory/category_list.html";context_object_name="categories"
class CategoryCreateView(LoginRequiredMixin,CreateView):
 model=Category;form_class=CategoryForm;template_name="inventory/form.html";success_url="/categories/";extra_context={"title":"Add category"}
 def form_valid(self,f):
  messages.success(self.request,"Category created successfully.");return super().form_valid(f)
class CategoryUpdateView(LoginRequiredMixin,AdminRequiredMixin,UpdateView):model=Category;form_class=CategoryForm;template_name="inventory/form.html";success_url="/categories/";extra_context={"title":"Edit category"}
class CategoryDeleteView(LoginRequiredMixin,AdminRequiredMixin,DeleteView):model=Category;template_name="inventory/confirm_delete.html";success_url="/categories/"
class SupplierListView(LoginRequiredMixin,ListView):model=Supplier;template_name="inventory/supplier_list.html";context_object_name="suppliers"
class SupplierCreateView(LoginRequiredMixin,CreateView):model=Supplier;form_class=SupplierForm;template_name="inventory/form.html";success_url="/suppliers/";extra_context={"title":"Add supplier"}
class SupplierUpdateView(LoginRequiredMixin,AdminRequiredMixin,UpdateView):model=Supplier;form_class=SupplierForm;template_name="inventory/form.html";success_url="/suppliers/";extra_context={"title":"Edit supplier"}
class SupplierDeleteView(LoginRequiredMixin,AdminRequiredMixin,DeleteView):model=Supplier;template_name="inventory/confirm_delete.html";success_url="/suppliers/"
class TransactionListView(LoginRequiredMixin,ListView):
 template_name="inventory/transaction_list.html";context_object_name="transactions";paginate_by=20
 def get_queryset(self):
  qs=InventoryTransaction.objects.select_related("product","user")
  if x:=self.request.GET.get("product"):qs=qs.filter(product_id=x)
  if x:=self.request.GET.get("type"):qs=qs.filter(transaction_type=x)
  return qs
 def get_context_data(self,**kwargs):return super().get_context_data(products=Product.objects.all(),**kwargs)
class StockTransactionCreateView(LoginRequiredMixin,CreateView):
 form_class=StockTransactionForm;template_name="inventory/form.html";success_url=reverse_lazy("stock-movement-list");extra_context={"title":"Update stock"}
 def form_valid(self,f):
  try:f.save(user=self.request.user)
  except ValidationError as e:f.add_error("quantity",e.message_dict["quantity"]);return self.form_invalid(f)
  messages.success(self.request,"Stock updated successfully. Activity was created automatically.");return redirect(self.success_url)
