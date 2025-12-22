"""
URL CONFIGURATION FOR TRIAL BALANCE
Routes for trial balance display, generation, and reporting
"""

from django.urls import path
from accounting.views_trial_balance import (
    TrialBalanceListView,
    TrialBalanceDetailView,
    TrialBalanceReportView,
    TrialBalanceComparisonView,
    TrialBalanceExportView,
    TrialBalanceDashboardView,
    MonthlyTrialBalanceListView,
)

urlpatterns = [
    # ===== TRIAL BALANCE ROUTES =====
    
    # Trial balance dashboard
    path(
        'trial-balance-dashboard/',
        TrialBalanceDashboardView.as_view(),
        name='trial_balance_dashboard'
    ),
    
    # List all trial balances
    path(
        'trial-balances/',
        TrialBalanceListView.as_view(),
        name='trial_balance_list'
    ),
    
    # View trial balance detail
    path(
        'trial-balance/<int:pk>/',
        TrialBalanceDetailView.as_view(),
        name='trial_balance_detail'
    ),
    
    # Trial balance report (formatted)
    path(
        'trial-balance-report/',
        TrialBalanceReportView.as_view(),
        name='trial_balance_report'
    ),
    
    # Compare two trial balances
    path(
        'trial-balance-comparison/',
        TrialBalanceComparisonView.as_view(),
        name='trial_balance_comparison'
    ),
    
    # Export trial balance as CSV
    path(
        'trial-balance/<int:pk>/export/',
        TrialBalanceExportView.as_view(),
        name='trial_balance_export'
    ),
    
    # ===== MONTHLY TRIAL BALANCE ROUTES =====
    
    # List monthly trial balances
    path(
        'monthly-trial-balances/',
        MonthlyTrialBalanceListView.as_view(),
        name='monthly_trial_balance_list'
    ),
]
