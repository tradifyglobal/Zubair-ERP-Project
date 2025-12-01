from django.urls import path
from . import views

app_name = 'ar'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.ARDashboardView.as_view(), name='dashboard'),
    
    # Invoices
    path('invoices/', views.CustomerInvoiceListView.as_view(), name='invoice_list'),
    path('invoices/create/', views.CustomerInvoiceCreateView.as_view(), name='invoice_create'),
    path('invoices/<int:pk>/', views.CustomerInvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/<int:pk>/edit/', views.CustomerInvoiceUpdateView.as_view(), name='invoice_edit'),
    
    # Payments
    path('payments/', views.CustomerPaymentListView.as_view(), name='payment_list'),
    path('payments/create/', views.CustomerPaymentCreateView.as_view(), name='payment_create'),
    path('payments/<int:pk>/', views.CustomerPaymentDetailView.as_view(), name='payment_detail'),
    
    # Reports
    path('aging/', views.ARAgingReportView.as_view(), name='aging_report'),
]
