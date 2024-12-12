from django.contrib import admin
from .models import PincodeMapping

@admin.register(PincodeMapping)
class PincodeMappingAdmin(admin.ModelAdmin):
    list_display = ("old_pincode", "new_pincode")
    search_fields = ("old_pincode", "new_pincode")
