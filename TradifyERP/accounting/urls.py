from django.urls import path
from .views import (
    DashboardView, GLDashboardView,
    AccountListView, AccountDetailView,
    LedgerEntryListView, LedgerEntryCreateView, DoubleEntryJournalView,
    TrialBalanceListView, ProfitLossListView, BalanceSheetListView,
    CustomerListView, VendorListView,
    VendorInvoiceListView, VendorInvoiceDetailView, VendorInvoiceUpdateView, VendorInvoiceStatusUpdateView, RecordVendorPaymentView, VendorPaymentListView,
    FixedAssetListView,
    AuditLogListView,
    BankProfileListView, BankStatementListView,
    CashFlowForecastListView, CashTransactionListView,
    ReconciliationEntryListView, ReconciliationRecordListView, ReconciliationMatchListView,
    TaxRateListView, TaxTransactionListView, TaxSummaryListView,
    DeferredExpenseListView, DeferredRevenueListView,
    EntityListView, CurrencyListView, PeriodLockListView,
    QuickAddLedgerEntryView, QuickAddCustomerView, QuickAddVendorView, QuickAddAccountView, QuickAddVendorInvoiceView,
    QuickAddVendorPaymentView, QuickAddFixedAssetView, QuickAddCashTransactionView, QuickAddBankProfileView,
    QuickAddTaxRateView, QuickAddDeferredExpenseView, QuickAddDeferredRevenueView, QuickAddReconciliationRecordView,
)
from .views_extended import (
    QuickAddCurrencyView, QuickAddEntityView, QuickAddBankStatementView, QuickAddCashFlowForecastView,
    QuickAddTaxTransactionView, QuickAddTaxSummaryView, QuickAddPeriodLockView,
    QuickAddTrialBalanceView, QuickAddProfitLossReportView, QuickAddBalanceSheetView,
    QuickAddReconciliationEntryView, QuickAddReconciliationMatchView
)
from .views_pl import ProfitLossDetailView, ProfitLossComparisonView
from .views_analytics import (
    FinancialRatiosView, AccountsReceivableAgingView, AccountsPayableAgingView,
    VarianceAnalysisView, CostCenterAnalysisView
)
from .stakeholder_views import (
    StakeholderListView, StakeholderDetailView, StakeholderCreateView, StakeholderUpdateView, StakeholderDeleteView,
    CapitalContributionListView, CapitalContributionDetailView, CapitalContributionCreateView, CapitalContributionUpdateView,
    ShareholdingListView, ShareholdingDetailView, ShareholdingCreateView, ShareholdingUpdateView
)

app_name = 'accounting'

urlpatterns = [
    # Main dashboards
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('gl-dashboard/', GLDashboardView.as_view(), name='gl_dashboard'),
    
    # Accounts
    path('accounts/', AccountListView.as_view(), name='account_list'),
    path('accounts/<int:pk>/', AccountDetailView.as_view(), name='account_detail'),
    
    # Ledger Entries
    path('ledger-entries/', LedgerEntryListView.as_view(), name='ledger_entry_list'),
    path('ledger-entries/create/', LedgerEntryCreateView.as_view(), name='ledger_entry_create'),
    path('journal-entries/create/', DoubleEntryJournalView.as_view(), name='journal_entry_create'),
    path('quick-add-entry/', QuickAddLedgerEntryView.as_view(), name='quick_add_entry'),
    
    # Quick Add Views
    path('quick-add-customer/', QuickAddCustomerView.as_view(), name='quick_add_customer'),
    path('quick-add-vendor/', QuickAddVendorView.as_view(), name='quick_add_vendor'),
    path('quick-add-account/', QuickAddAccountView.as_view(), name='quick_add_account'),
    path('quick-add-vendor-invoice/', QuickAddVendorInvoiceView.as_view(), name='quick_add_vendor_invoice'),
    path('quick-add-vendor-payment/', QuickAddVendorPaymentView.as_view(), name='quick_add_vendor_payment'),
    path('quick-add-fixed-asset/', QuickAddFixedAssetView.as_view(), name='quick_add_fixed_asset'),
    path('quick-add-cash-transaction/', QuickAddCashTransactionView.as_view(), name='quick_add_cash_transaction'),
    path('quick-add-bank-profile/', QuickAddBankProfileView.as_view(), name='quick_add_bank_profile'),
    path('quick-add-tax-rate/', QuickAddTaxRateView.as_view(), name='quick_add_tax_rate'),
    path('quick-add-deferred-expense/', QuickAddDeferredExpenseView.as_view(), name='quick_add_deferred_expense'),
    path('quick-add-deferred-revenue/', QuickAddDeferredRevenueView.as_view(), name='quick_add_deferred_revenue'),
    path('quick-add-reconciliation-record/', QuickAddReconciliationRecordView.as_view(), name='quick_add_reconciliation_record'),
    
    # Extended Quick Add Views (from views_extended.py)
    path('quick-add-currency/', QuickAddCurrencyView.as_view(), name='quick_add_currency'),
    path('quick-add-entity/', QuickAddEntityView.as_view(), name='quick_add_entity'),
    path('quick-add-bank-statement/', QuickAddBankStatementView.as_view(), name='quick_add_bank_statement'),
    path('quick-add-cash-flow-forecast/', QuickAddCashFlowForecastView.as_view(), name='quick_add_cash_flow_forecast'),
    path('quick-add-tax-transaction/', QuickAddTaxTransactionView.as_view(), name='quick_add_tax_transaction'),
    path('quick-add-tax-summary/', QuickAddTaxSummaryView.as_view(), name='quick_add_tax_summary'),
    path('quick-add-period-lock/', QuickAddPeriodLockView.as_view(), name='quick_add_period_lock'),
    path('quick-add-trial-balance/', QuickAddTrialBalanceView.as_view(), name='quick_add_trial_balance'),
    path('quick-add-profit-loss-report/', QuickAddProfitLossReportView.as_view(), name='quick_add_profit_loss_report'),
    path('quick-add-balance-sheet/', QuickAddBalanceSheetView.as_view(), name='quick_add_balance_sheet'),
    path('quick-add-reconciliation-entry/', QuickAddReconciliationEntryView.as_view(), name='quick_add_reconciliation_entry'),
    path('quick-add-reconciliation-match/', QuickAddReconciliationMatchView.as_view(), name='quick_add_reconciliation_match'),
    
    # Financial Reports
    path('trial-balances/', TrialBalanceListView.as_view(), name='trial_balance_list'),
    path('profit-loss/', ProfitLossListView.as_view(), name='profit_loss_list'),
    path('profit-loss-detail/', ProfitLossDetailView.as_view(), name='profit_loss_detail'),
    path('profit-loss-comparison/', ProfitLossComparisonView.as_view(), name='profit_loss_comparison'),
    path('balance-sheets/', BalanceSheetListView.as_view(), name='balance_sheet_list'),
    
    # Customers & Vendors
    path('customers/', CustomerListView.as_view(), name='customer_list'),
    path('vendors/', VendorListView.as_view(), name='vendor_list'),
    
    # Invoices & Payments
    path('vendor-invoices/', VendorInvoiceListView.as_view(), name='vendor_invoice_list'),
    path('vendor-invoices/<int:pk>/', VendorInvoiceDetailView.as_view(), name='vendor_invoice_detail'),
    path('vendor-invoices/<int:pk>/edit/', VendorInvoiceUpdateView.as_view(), name='vendor_invoice_edit'),
    path('vendor-invoices/<int:pk>/update-status/', VendorInvoiceStatusUpdateView.as_view(), name='vendor_invoice_update_status'),
    path('vendor-invoices/<int:pk>/record-payment/', RecordVendorPaymentView.as_view(), name='record_vendor_payment'),
    path('vendor-payments/', VendorPaymentListView.as_view(), name='vendor_payments_list'),
    
    # Fixed Assets
    path('fixed-assets/', FixedAssetListView.as_view(), name='fixed_asset_list'),
    
    # Banking
    path('bank-profiles/', BankProfileListView.as_view(), name='bank_profiles_list'),
    path('bank-statements/', BankStatementListView.as_view(), name='bank_statements_list'),
    path('cash-transactions/', CashTransactionListView.as_view(), name='cash_transactions_list'),
    path('cash-flow-forecast/', CashFlowForecastListView.as_view(), name='cash_flow_forecast_list'),
    
    # Reconciliation
    path('reconciliation-entries/', ReconciliationEntryListView.as_view(), name='reconciliation_entries_list'),
    path('reconciliation-records/', ReconciliationRecordListView.as_view(), name='reconciliation_records_list'),
    path('reconciliation-matches/', ReconciliationMatchListView.as_view(), name='reconciliation_matches_list'),
    
    # Tax Management
    path('tax-rates/', TaxRateListView.as_view(), name='tax_rates_list'),
    path('tax-transactions/', TaxTransactionListView.as_view(), name='tax_transactions_list'),
    path('tax-summaries/', TaxSummaryListView.as_view(), name='tax_summaries_list'),
    
    # Deferred Items
    path('deferred-expenses/', DeferredExpenseListView.as_view(), name='deferred_expenses_list'),
    path('deferred-revenues/', DeferredRevenueListView.as_view(), name='deferred_revenues_list'),
    
    # Administration
    path('entities/', EntityListView.as_view(), name='entities_list'),
    path('currencies/', CurrencyListView.as_view(), name='currencies_list'),
    path('period-locks/', PeriodLockListView.as_view(), name='period_locks_list'),
    
    # Audit Logs
    path('audit-logs/', AuditLogListView.as_view(), name='audit_log_list'),
    
    # Stakeholder Management
    path('stakeholders/', StakeholderListView.as_view(), name='stakeholder_list'),
    path('stakeholders/<int:pk>/', StakeholderDetailView.as_view(), name='stakeholder_detail'),
    path('stakeholders/create/', StakeholderCreateView.as_view(), name='stakeholder_create'),
    path('stakeholders/<int:pk>/edit/', StakeholderUpdateView.as_view(), name='stakeholder_edit'),
    path('stakeholders/<int:pk>/delete/', StakeholderDeleteView.as_view(), name='stakeholder_delete'),
    
    # Capital Contributions
    path('capital-contributions/', CapitalContributionListView.as_view(), name='capital_contribution_list'),
    path('capital-contributions/<int:pk>/', CapitalContributionDetailView.as_view(), name='capital_contribution_detail'),
    path('capital-contributions/create/', CapitalContributionCreateView.as_view(), name='capital_contribution_create'),
    path('capital-contributions/create/<int:stakeholder_id>/', CapitalContributionCreateView.as_view(), name='capital_contribution_create_for_stakeholder'),
    path('capital-contributions/<int:pk>/edit/', CapitalContributionUpdateView.as_view(), name='capital_contribution_edit'),
    
    # Shareholdings
    path('shareholdings/', ShareholdingListView.as_view(), name='shareholding_list'),
    path('shareholdings/<int:pk>/', ShareholdingDetailView.as_view(), name='shareholding_detail'),
    path('shareholdings/create/', ShareholdingCreateView.as_view(), name='shareholding_create'),
    path('shareholdings/create/<int:stakeholder_id>/', ShareholdingCreateView.as_view(), name='shareholding_create_for_stakeholder'),
    path('shareholdings/<int:pk>/edit/', ShareholdingUpdateView.as_view(), name='shareholding_edit'),
    
    # Advanced Analytics & Reports
    path('financial-ratios/', FinancialRatiosView.as_view(), name='financial_ratios'),
    path('ar-aging/', AccountsReceivableAgingView.as_view(), name='ar_aging'),
    path('ap-aging/', AccountsPayableAgingView.as_view(), name='ap_aging'),
    path('variance-analysis/', VarianceAnalysisView.as_view(), name='variance_analysis'),
    path('cost-center-analysis/', CostCenterAnalysisView.as_view(), name='cost_center_analysis'),
]
