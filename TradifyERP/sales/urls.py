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
    
    # Quotation URLs (Phase 1)
    path('quotations/', views.QuotationListView.as_view(), name='quotation_list'),
    path('quotations/new/', views.QuotationCreateView.as_view(), name='quotation_create'),
    path('quotations/<int:pk>/edit/', views.QuotationUpdateView.as_view(), name='quotation_update'),
    path('quotations/<int:pk>/delete/', views.QuotationDeleteView.as_view(), name='quotation_delete'),
    
    # Pricing Rule URLs (Phase 1)
    path('pricing-rules/', views.PricingRuleListView.as_view(), name='pricing_rule_list'),
    path('pricing-rules/new/', views.PricingRuleCreateView.as_view(), name='pricing_rule_create'),
    path('pricing-rules/<int:pk>/edit/', views.PricingRuleUpdateView.as_view(), name='pricing_rule_update'),
    path('pricing-rules/<int:pk>/delete/', views.PricingRuleDeleteView.as_view(), name='pricing_rule_delete'),
    
    # Discount Policy URLs (Phase 1)
    path('discount-policies/', views.DiscountPolicyListView.as_view(), name='discount_policy_list'),
    path('discount-policies/new/', views.DiscountPolicyCreateView.as_view(), name='discount_policy_create'),
    path('discount-policies/<int:pk>/edit/', views.DiscountPolicyUpdateView.as_view(), name='discount_policy_update'),
    path('discount-policies/<int:pk>/delete/', views.DiscountPolicyDeleteView.as_view(), name='discount_policy_delete'),
    
    # Customer Segment URLs (Phase 1)
    path('customer-segments/', views.CustomerSegmentListView.as_view(), name='customer_segment_list'),
    path('customer-segments/new/', views.CustomerSegmentCreateView.as_view(), name='customer_segment_create'),
    path('customer-segments/<int:pk>/edit/', views.CustomerSegmentUpdateView.as_view(), name='customer_segment_update'),
    path('customer-segments/<int:pk>/delete/', views.CustomerSegmentDeleteView.as_view(), name='customer_segment_delete'),
]
