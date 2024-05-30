from django.urls import path

from .views import (
    IndexView,
    operators_cvg,
)

app_name = "operators"
urlpatterns = [
    path("", IndexView.as_view(), name="operators"),
    path("coverage/", operators_cvg, name="operators_coverage"),
]
