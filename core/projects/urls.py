# projects/urls.py
from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list, name='project-list'),
    path('select-type/', views.project_select_type, name='project-select-type'),
    path('create/<str:project_type>/', views.project_create, name='project-create'),
    path('<int:pk>/', views.project_detail, name='project-detail'),
    path('<int:pk>/edit/', views.project_edit, name='project-edit'),
    path('<int:pk>/delete/', views.project_delete, name='project-delete'),
    path('<int:pk>/change-status/', views.project_change_status, name='project-change-status'),
]