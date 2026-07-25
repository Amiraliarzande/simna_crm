from django.contrib import admin
from .models import Contract, ContractNotification

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['title', 'employee', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['title', 'employee__username', 'employee__first_name']
    readonly_fields = ['admin_signed_at', 'employee_signed_at', 'created_at', 'updated_at']


@admin.register(ContractNotification)
class ContractNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'contract', 'is_read', 'created_at']
    list_filter = ['is_read']