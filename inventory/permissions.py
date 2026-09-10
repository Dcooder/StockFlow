from django.contrib.auth.mixins import UserPassesTestMixin
from rest_framework.permissions import BasePermission

def is_admin(user): return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self): return is_admin(self.request.user)
class AdminWriteOrAuthenticatedCreate(BasePermission):
    def has_permission(self, request, view): return bool(request.user and request.user.is_authenticated and (request.method in ("GET", "HEAD", "OPTIONS", "POST") or is_admin(request.user)))
class TransactionPermission(AdminWriteOrAuthenticatedCreate): pass
