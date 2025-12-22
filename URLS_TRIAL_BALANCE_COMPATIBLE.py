"""
URLs for Trial Balance Views - Compatible with Production Models
"""

from django.urls import path
from .views_trial_balance_compatible import (
    TrialBalanceListView,
    TrialBalanceDetailView,
    TrialBalanceGenerateView,
    TrialBalanceReportView,
    TrialBalanceComparisonView,
    TrialBalanceExportView,
    TrialBalanceDashboardView,
    MonthlyTrialBalanceListView,
)

urlpatterns = [
    # Dashboard
    path('trial-balance-dashboard/', TrialBalanceDashboardView.as_view(), name='trial-balance-dashboard'),
    
    # List views
    path('trial-balance/', TrialBalanceListView.as_view(), name='trial-balance-list'),
    path('trial-balance/monthly/', MonthlyTrialBalanceListView.as_view(), name='monthly-trial-balance-list'),
    
    # Detail view
    path('trial-balance/<int:pk>/', TrialBalanceDetailView.as_view(), name='trial-balance-detail'),
    
    # Generate
    path('trial-balance/generate/', TrialBalanceGenerateView.as_view(), name='trial-balance-generate'),
    
    # Report
    path('trial-balance/report/', TrialBalanceReportView.as_view(), name='trial-balance-report'),
    
    # Comparison
    path('trial-balance/comparison/', TrialBalanceComparisonView.as_view(), name='trial-balance-comparison'),
    
    # Export
    path('trial-balance/<int:pk>/export/', TrialBalanceExportView.as_view(), name='trial-balance-export'),
]
