from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add-tenant/', views.add_tenant, name='add_tenant'),
    path('generate-bill/<int:tenant_id>/', views.generate_bill, name='generate_bill'),
    path('bills/<int:tenant_id>/', views.tenant_bills, name='tenant_bills'),
    path('send-whatsapp/<int:record_id>/', views.send_whatsapp_bill, name='send_whatsapp'),
    
    path('record-payment/<int:record_id>/', views.record_payment, name='record_payment'),
    path('mark-paid/<int:record_id>/', views.mark_as_paid, name='mark_paid'),
    path('edit-payment/<int:record_id>/', views.edit_payment, name='edit_payment'),

    # Expense
    path('expenses/', views.expense_list, name='expense_list'),
    path('add-expense/', views.add_expense, name='add_expense'),
]
