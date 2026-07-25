# chat/urls.py
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # چت
    path('', views.chat_list, name='chat-list'),
    path('room/<int:room_id>/', views.chat_room, name='chat-room'),
    path('start/', views.chat_start, name='chat-start'),
    path('message/<int:message_id>/save/', views.chat_save_message, name='chat-save-message'),
    path('room/<int:room_id>/pin/', views.chat_toggle_pin, name='chat-toggle-pin'),
    path('saved/', views.chat_saved_messages, name='chat-saved-messages'),
    path('message/<int:message_id>/delete/', views.chat_delete_message, name='chat-delete-message'),
    path('message/<int:message_id>/edit/', views.chat_edit_message, name='chat-edit-message'),
    path('notifications/', views.chat_notifications, name='chat-notifications'),

    # یادداشت‌ها
    path('notes/', views.note_list, name='note-list'),
    path('notes/create/', views.note_create, name='note-create'),
    path('notes/<int:pk>/edit/', views.note_edit, name='note-edit'),
    path('notes/<int:pk>/delete/', views.note_delete, name='note-delete'),
    path('notes/<int:pk>/pin/', views.note_toggle_pin, name='note-toggle-pin'),
    path('notes/<int:pk>/archive/', views.note_archive, name='note-archive'),
    path('notes/archived/', views.note_archived_list, name='note-archived-list'),
    path('notes/<int:pk>/unarchive/', views.note_unarchive, name='note-unarchive'),

    # تقویم
    path('calendar/', views.calendar_view, name='calendar-view'),
    path('calendar/<int:year>/<int:month>/', views.calendar_view, name='calendar-view-month'),
    path('calendar/event/create/', views.calendar_event_create, name='calendar-event-create'),
    path('calendar/event/<int:pk>/edit/', views.calendar_event_edit, name='calendar-event-edit'),
    path('calendar/event/<int:pk>/delete/', views.calendar_event_delete, name='calendar-event-delete'),
    path('calendar/events/json/<int:year>/<int:month>/', views.calendar_events_json, name='calendar-events-json'),
]