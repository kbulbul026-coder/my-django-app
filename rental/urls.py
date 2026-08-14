from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add-tenant/', views.add_tenant, name='add_tenant'),
    path('generate-bill/<int:tenant_id>/', views.generate_bill, name='generate_bill'),
    path('bills/<int:tenant_id>/', views.tenant_bills, name='tenant_bills'),
    path('send-whatsapp/<int:record_id>/', views.send_whatsapp_bill, name='send_whatsapp'),
    
    path('record-payment/<int:record_id>/', views.record_payment, name='record_payment'),
    path('edit-payment/<int:record_id>/', views.edit_payment, name='edit_payment'),
    path('edit-single-payment/<int:payment_id>/', views.edit_single_payment, name='edit_single_payment'),
    path('delete-payment/<int:payment_id>/', views.delete_payment, name='delete_payment'),
    path('move-out/<int:tenant_id>/', views.move_out_tenant, name='move_out'),
    path('inactive-tenants/', views.inactive_tenants, name='inactive_tenants'),

    # Documents
    path('documents/<int:tenant_id>/', views.tenant_documents, name='tenant_documents'),
    path('delete-document/<int:document_id>/', views.delete_document, name='delete_document'),

    # Expense
    path('expenses/', views.expense_list, name='expense_list'),
    path('add-expense/', views.add_expense, name='add_expense'),
]
