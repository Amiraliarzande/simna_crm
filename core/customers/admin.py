from django.contrib import admin
from .models import Customer, CustomerNote, CustomerGroup


@admin.register(CustomerGroup)
class CustomerGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'discount_percent', 'bonus_points', 'member_count', 'is_active']
    list_filter = ['is_active', 'department']
    search_fields = ['name', 'department', 'description']
    ordering = ['name']

    def member_count(self, obj):
        return obj.customers.count()

    member_count.short_description = 'تعداد اعضا'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'company', 'phone', 'group', 'department', 'customer_type', 'is_active']
    list_filter = ['customer_type', 'is_active', 'is_potential', 'group', 'department']
    search_fields = ['first_name', 'last_name', 'company', 'email', 'phone']
    ordering = ['-created_at']


@admin.register(CustomerNote)
class CustomerNoteAdmin(admin.ModelAdmin):
    list_display = ['customer', 'created_by', 'created_at', 'is_pinned']
    list_filter = ['is_pinned']
    search_fields = ['note', 'customer__first_name', 'customer__last_name']