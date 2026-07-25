# tasks/urls.py
from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list, name='task-list'),
    path('create/', views.task_create, name='task-create'),
    path('<int:pk>/', views.task_detail, name='task-detail'),
    path('<int:pk>/edit/', views.task_edit, name='task-edit'),
    path('<int:pk>/delete/', views.task_delete, name='task-delete'),
    path('<int:pk>/change-status/', views.task_change_status, name='task-change-status'),
    path('my-tasks/', views.task_my_tasks, name='task-my-tasks'),
]