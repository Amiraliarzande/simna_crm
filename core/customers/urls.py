from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    # صفحات اصلی مشتریان
    path('', views.customer_list, name='customer-list'),
    path('<int:pk>/', views.customer_detail, name='customer-detail'),
    path('create/', views.customer_create, name='customer-create'),
    path('<int:pk>/edit/', views.customer_edit, name='customer-edit'),
    path('<int:pk>/delete/', views.customer_delete, name='customer-delete'),
    path('<int:pk>/toggle-status/', views.customer_toggle_status, name='customer-toggle-status'),

    # زیرمجموعه‌ها
    path('potential/', views.potential_customers, name='potential-customers'),
    path('club/', views.customer_club, name='customer-club'),
    path('club/group/<int:pk>/', views.club_group_detail, name='club-group-detail'),
    path('club/group/create/', views.club_group_create, name='club-group-create'),
    path('club/group/<int:pk>/edit/', views.club_group_edit, name='club-group-edit'),
    path('club/group/<int:pk>/delete/', views.club_group_delete, name='club-group-delete'),

    # یادداشت‌ها
    path('note/<int:pk>/edit/', views.note_edit, name='note-edit'),
    path('note/<int:pk>/delete/', views.note_delete, name='note-delete'),
    path('note/<int:pk>/toggle-pin/', views.note_toggle_pin, name='note-toggle-pin'),

    # بررسی و غیرفعال سازی خودکار
    path('check-deactivate/', views.check_and_deactivate, name='check-deactivate'),

    path('club/group/<int:pk>/add-member/', views.club_group_add_member, name='club-group-add-member'),
    path('archived/', views.archived_customers, name='archived-customers'),
    path('<int:pk>/archive/', views.customer_archive, name='customer-archive'),
    path('<int:pk>/unarchive/', views.customer_unarchive, name='customer-unarchive'),
    path('archive/<int:pk>/delete/', views.customer_archive_delete, name='customer-archive-delete'),
]