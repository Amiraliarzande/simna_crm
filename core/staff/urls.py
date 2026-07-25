from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.staff_dashboard, name='staff-dashboard'),
    path('list/', views.staff_list, name='staff-list'),
    path('create/', views.staff_create, name='staff-create'),
    path('<int:pk>/', views.staff_detail, name='staff-detail'),
    path('<int:pk>/edit/', views.staff_edit, name='staff-edit'),
    path('<int:pk>/delete/', views.staff_delete, name='staff-delete'),
    path('<int:pk>/toggle-status/', views.staff_toggle_status, name='staff-toggle-status'),
]