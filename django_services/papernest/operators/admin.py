from django.contrib import admin

from .models import (
    Operator,
    Coverage,
)

admin.site.register(Operator)
admin.site.register(Coverage)
