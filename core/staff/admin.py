# staff/admin.py
from django.contrib import admin
from .models import StaffProfile


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'position', 'department', 'is_active']
    list_filter = ['position', 'department', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'phone', 'user__email']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('اطلاعات کاربری', {
            'fields': ('user', 'phone', 'avatar', 'address')
        }),
        ('وضعیت شغلی', {
            'fields': ('position', 'position_other', 'department', 'department_other', 'hire_date')
        }),
        ('وضعیت', {
            'fields': ('is_active',)
        }),
        ('دسترسی‌ها', {
            'fields': ('can_manage_staff', 'can_manage_customers', 'can_manage_sales',
                       'can_manage_warehouse', 'can_manage_accounting', 'can_manage_support',
                       'can_view_reports')
        }),
        ('اطلاعات سیستمی', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )