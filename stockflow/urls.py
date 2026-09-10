from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from accounts.views import landing

admin.site.site_header = "StockFlow administration"
admin.site.site_title = "StockFlow"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", landing, name="landing"),
    path("", include("inventory.urls")),
    path("api/", include("inventory.api_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
