from django.contrib import admin
from django.urls import path, include
from django_learning import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("polls/", include("polls.urls")),
]

# Serve static files during development
if settings.ENVIRONMENT != "DEV":
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
