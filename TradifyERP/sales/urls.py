"""
Sales Module URL Configuration
Complete URL routing for sales module views.
"""

from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.SalesDashboardView.as_view(), name='dashboard'),
    
    # Customer URLs
    path('customers/', views.CustomerListView.as_view(), name='customer_list'),
    path('customers/new/', views.CustomerCreateView.as_view(), name='customer_create'),
    path('customers/<int:pk>/edit/', views.CustomerUpdateView.as_view(), name='customer_update'),
    path('customers/<int:pk>/delete/', views.CustomerDeleteView.as_view(), name='customer_delete'),
    
    # Sales Order URLs
    path('orders/', views.SalesOrderListView.as_view(), name='salesorder_list'),
    path('orders/new/', views.SalesOrderCreateView.as_view(), name='salesorder_create'),
    path('orders/<int:pk>/edit/', views.SalesOrderUpdateView.as_view(), name='salesorder_update'),
    path('orders/<int:pk>/delete/', views.SalesOrderDeleteView.as_view(), name='salesorder_delete'),
    
    # Invoice URLs
    path('invoices/', views.InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/new/', views.InvoiceCreateView.as_view(), name='invoice_create'),
    path('invoices/<int:pk>/edit/', views.InvoiceUpdateView.as_view(), name='invoice_update'),
    path('invoices/<int:pk>/delete/', views.InvoiceDeleteView.as_view(), name='invoice_delete'),
]
