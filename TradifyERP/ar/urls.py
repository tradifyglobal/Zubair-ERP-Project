from django.urls import path
from . import views

app_name = 'ar'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.ARDashboardView.as_view(), name='dashboard'),
    
    # Invoices
    path('invoices/', views.CustomerInvoiceListView.as_view(), name='invoice_list'),
    path('invoices/<int:pk>/', views.CustomerInvoiceDetailView.as_view(), name='invoice_detail'),
    
    # Payments
    path('payments/', views.CustomerPaymentListView.as_view(), name='payment_list'),
    path('payments/<int:pk>/', views.CustomerPaymentDetailView.as_view(), name='payment_detail'),
    
    # Reports
    path('aging/', views.ARAgingReportView.as_view(), name='aging_report'),
]
