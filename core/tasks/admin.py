# tasks/admin.py
from django.contrib import admin
from .models import Task, TaskComment, TaskNotification


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'assigned_to_display', 'priority', 'status', 'due_date']
    list_filter = ['priority', 'status']
    search_fields = ['title', 'description']

    def assigned_to_display(self, obj):
        """نمایش افراد اختصاص داده شده در لیست ادمین"""
        users = obj.assigned_to.all()
        if users.exists():
            return ', '.join([u.get_full_name() or u.username for u in users])
        return '-'

    assigned_to_display.short_description = 'اختصاص به'


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'created_at']


@admin.register(TaskNotification)
class TaskNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'is_read', 'created_at']