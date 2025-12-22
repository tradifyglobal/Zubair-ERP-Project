"""
URL CONFIGURATION FOR PAYMENT VOUCHERS
Routes for cash and bank payment workflows
"""

from django.urls import path
from accounting.views_payment import (
    # Cash Payment Views
    CashPaymentListView,
    CashPaymentDetailView,
    CashPaymentCreateView,
    CashPaymentApprovalView,
    CashPaymentAuthorizationView,
    
    # Bank Payment Views
    BankPaymentListView,
    BankPaymentDetailView,
    BankPaymentCreateView,
    BankPaymentApprovalView,
    BankPaymentAuthorizationView,
    
    # Payment Reporting
    PaymentDashboardView,
)

app_name = 'accounting'

urlpatterns = [
    # ===== CASH PAYMENT VOUCHER ROUTES =====
    
    # List all cash payments
    path(
        'cash-payments/',
        CashPaymentListView.as_view(),
        name='cash_payment_list'
    ),
    
    # Create new cash payment
    path(
        'cash-payment/create/',
        CashPaymentCreateView.as_view(),
        name='cash_payment_create'
    ),
    
    # View cash payment details
    path(
        'cash-payment/<int:pk>/',
        CashPaymentDetailView.as_view(),
        name='cash_payment_detail'
    ),
    
    # Approve cash payment (Checker)
    path(
        'cash-payment/<int:pk>/approve/',
        CashPaymentApprovalView.as_view(),
        name='cash_payment_approval'
    ),
    
    # Authorize cash payment (Approver)
    path(
        'cash-payment/<int:pk>/authorize/',
        CashPaymentAuthorizationView.as_view(),
        name='cash_payment_authorization'
    ),
    
    # ===== BANK PAYMENT VOUCHER ROUTES =====
    
    # List all bank payments
    path(
        'bank-payments/',
        BankPaymentListView.as_view(),
        name='bank_payment_list'
    ),
    
    # Create new bank payment
    path(
        'bank-payment/create/',
        BankPaymentCreateView.as_view(),
        name='bank_payment_create'
    ),
    
    # View bank payment details
    path(
        'bank-payment/<int:pk>/',
        BankPaymentDetailView.as_view(),
        name='bank_payment_detail'
    ),
    
    # Approve bank payment (Checker)
    path(
        'bank-payment/<int:pk>/approve/',
        BankPaymentApprovalView.as_view(),
        name='bank_payment_approval'
    ),
    
    # Authorize bank payment (Approver)
    path(
        'bank-payment/<int:pk>/authorize/',
        BankPaymentAuthorizationView.as_view(),
        name='bank_payment_authorization'
    ),
    
    # ===== PAYMENT REPORTING ROUTES =====
    
    # Payment dashboard
    path(
        'payment-dashboard/',
        PaymentDashboardView.as_view(),
        name='payment_dashboard'
    ),
]
