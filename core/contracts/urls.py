from django.urls import path
from . import views

app_name = 'contracts'

urlpatterns = [
    path('', views.contract_list, name='contract-list'),
    path('create/', views.contract_create, name='contract-create'),
    path('<int:pk>/', views.contract_detail, name='contract-detail'),
    path('<int:pk>/delete/', views.contract_delete, name='contract-delete'),
    path('<int:pk>/sign-admin/', views.contract_sign_admin, name='contract-sign-admin'),
    path('<int:pk>/sign-employee/', views.contract_sign_employee, name='contract-sign-employee'),
    path('<int:pk>/send-to-employee/', views.contract_send_to_employee, name='contract-send-to-employee'),
    path('<int:pk>/reject/', views.contract_reject, name='contract-reject'),
    path('<int:pk>/employee-respond/', views.contract_employee_respond, name='contract-employee-respond'),
    path('my-contracts/', views.contract_employee_list, name='contract-employee-list'),
]