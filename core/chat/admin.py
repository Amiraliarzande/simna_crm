from django.contrib import admin
from .models import ChatRoom, ChatMessage, ChatNotification

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'room_type', 'name', 'created_at', 'is_active']
    list_filter = ['room_type', 'is_active']
    filter_horizontal = ['participants']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['room', 'sender', 'message', 'created_at', 'is_read']
    list_filter = ['is_read']


@admin.register(ChatNotification)
class ChatNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'is_seen', 'created_at']