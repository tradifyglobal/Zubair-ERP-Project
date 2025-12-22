"""
URL CONFIGURATION FOR TRIAL BALANCE
Routes for trial balance display, generation, and reporting
Adapted for production TrialBalance model
"""

from django.urls import path
from accounting.views_trial_balance import (
    TrialBalanceListView,
    TrialBalanceDetailView,
    TrialBalanceGenerateView,
    TrialBalanceReportView,
    TrialBalanceComparisonView,
    TrialBalanceExportView,
    TrialBalanceDashboardView,
    MonthlyTrialBalanceListView,
)

app_name = 'accounting'

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

    # Generate new trial balance
    path(
        'trial-balance/generate/',
        TrialBalanceGenerateView.as_view(),
        name='trial_balance_generate'
    ),

    # View trial balance detail
    path(
        'trial-balance/<int:pk>/',
        TrialBalanceDetailView.as_view(),
        name='trial_balance_detail'
    ),

    # Trial balance report (formatted for financial statements)
    path(
        'trial-balance/<int:pk>/report/',
        TrialBalanceReportView.as_view(),
        name='trial_balance_report'
    ),

    # Trial balance comparison (period-to-period)
    path(
        'trial-balance/comparison/',
        TrialBalanceComparisonView.as_view(),
        name='trial_balance_comparison'
    ),

    # Export trial balance as CSV
    path(
        'trial-balance/<int:pk>/export/',
        TrialBalanceExportView.as_view(),
        name='trial_balance_export'
    ),

    # Monthly trial balance archives
    path(
        'trial-balance/monthly/',
        MonthlyTrialBalanceListView.as_view(),
        name='monthly_trial_balance_list'
    ),
]
