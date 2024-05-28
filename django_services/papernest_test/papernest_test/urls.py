from django.contrib import admin
from django.urls import path, include
from papernest_test import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("operators/", include("operators.urls")),
]

# Serve static files during development
if settings.ENVIRONMENT != "DEV":
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
