from django.contrib import admin
from main.models import Commission


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    pass
