from django.urls import path, include
from accounting.models import Account, Customer, Vendor
from .views import (
    DashboardView, GLDashboardView,
    AccountListView, AccountDetailView,
    LedgerEntryListView, LedgerEntryDetailView, LedgerEntryPrintView, LedgerEntryCreateView, DoubleEntryJournalView, LedgerEntryEditWorkflowView,
    TrialBalanceListView, ProfitLossListView, BalanceSheetListView,
    CustomerListView, CustomerDetailView, CustomerUpdateView, VendorListView, VendorDetailView, VendorUpdateView,
    VendorInvoiceListView, VendorInvoiceDetailView, VendorInvoiceUpdateView, VendorInvoiceStatusUpdateView, RecordVendorPaymentView, VendorPaymentListView, VendorPaymentDetailView, VendorPaymentUpdateView, VendorPaymentCreateView,
    FixedAssetListView, FixedAssetCreateView, FixedAssetUpdateView, FixedAssetDeleteView,
    AuditLogListView,
    BankProfileListView, BankProfileCreateView, BankProfileUpdateView, BankProfileDeleteView, BankStatementListView,
    CashFlowForecastListView, CashTransactionListView,
    ReconciliationEntryListView, ReconciliationRecordListView, ReconciliationMatchListView,
    TaxRateListView, TaxTransactionListView, TaxSummaryListView,
)
from accounting.views_debug import theme_debug
from .views import (
    DeferredExpenseListView, DeferredRevenueListView,
    EntityListView, EntityCreateView, EntityUpdateView, EntityDeleteView, CurrencyListView, PeriodLockListView,
    QuickAddLedgerEntryView, QuickAddCustomerView, QuickAddVendorView, QuickAddAccountView, QuickAddVendorInvoiceView,
    QuickAddVendorPaymentView, QuickAddFixedAssetView, QuickAddCashTransactionView, QuickAddBankProfileView,
    QuickAddTaxRateView, QuickAddDeferredExpenseView, QuickAddDeferredRevenueView, QuickAddReconciliationRecordView,
    GetAccountShareholderAPIView,
)
from .cash_views import (
    CashReceiptCreateView, CashReceiptListView, CashReceiptDetailView, CashReceiptPrintView,
    CashPaymentCreateView, CashPaymentListView, CashPaymentDetailView, CashPaymentPrintView,
    BankReceiptCreateView, BankReceiptListView, BankReceiptDetailView, BankReceiptPrintView,
    BankPaymentCreateView, BankPaymentListView, BankPaymentDetailView, BankPaymentPrintView
)
from .cash_workflow_views import (
    CashReceiptApprovalView, CashReceiptAuthorizationView, CashReceiptRejectView,
    CashPaymentApprovalView, CashPaymentAuthorizationView, CashPaymentRejectView,
    BankReceiptApprovalView, BankReceiptAuthorizationView, BankReceiptRejectView,
    BankPaymentApprovalView, BankPaymentAuthorizationView, BankPaymentRejectView
)
from .views_entity_selection import EntitySelectionView, EntitySwitchView
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
from .dashboard_views import main_dashboard
from .stakeholder_views import (
    StakeholderListView, StakeholderDetailView, StakeholderCreateView, StakeholderUpdateView, StakeholderDeleteView,
    CapitalContributionListView, CapitalContributionDetailView, CapitalContributionCreateView, CapitalContributionUpdateView,
    ShareholdingListView, ShareholdingDetailView, ShareholdingCreateView, ShareholdingUpdateView
)
from .user_views import (
    UserListView, UserCreateView, UserEditView, UserDetailView,
    UserApplyTemplateView, UserToggleStatusView
)
from .import_export_views import (
    BaseImportView, BaseExportView, ImportTemplateDownloadView,
    ImportExportDashboardView
)
from .import_export_implementations import (
    AccountImporter, AccountExporter,
    CustomerImporter, CustomerExporter,
    VendorImporter, VendorExporter,
    LedgerEntryExporter
)

app_name = 'accounting'

urlpatterns = [
    # Debug - Theme Test
    path('theme-debug/', theme_debug, name='theme_debug'),
    
    # Entity Selection
    path('select-entity/', EntitySelectionView.as_view(), name='select-entity'),
    path('switch-entity/', EntitySwitchView.as_view(), name='switch-entity'),
    
    # Main dashboards
    path('', DashboardView.as_view(), name='main_dashboard'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    # GL Dashboard - Accounting specific
    path('gl-dashboard/', GLDashboardView.as_view(), name='gl_dashboard'),
    
    # Accounts
    path('accounts/', AccountListView.as_view(), name='account_list'),
    path('accounts/<int:pk>/', AccountDetailView.as_view(), name='account_detail'),
    
    # Ledger Entries
    path('ledger-entries/', LedgerEntryListView.as_view(), name='ledger_entry_list'),
    path('ledger-entries/<int:pk>/', LedgerEntryDetailView.as_view(), name='ledger_entry_detail'),
    path('ledger-entries/<int:pk>/print/', LedgerEntryPrintView.as_view(), name='ledger_entry_print'),
    path('ledger-entries/<int:pk>/edit-workflow/', LedgerEntryEditWorkflowView.as_view(), name='ledger_entry_edit_workflow'),
    path('ledger-entries/create/', DoubleEntryJournalView.as_view(), name='ledger_entry_create'),
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
    
    # API Endpoints
    path('api/account-shareholder/', GetAccountShareholderAPIView.as_view(), name='api_account_shareholder'),
    
    # Financial Reports
    path('trial-balances/', TrialBalanceListView.as_view(), name='trial_balance_list'),
    path('profit-loss/', ProfitLossListView.as_view(), name='profit_loss_list'),
    path('profit-loss-detail/', ProfitLossDetailView.as_view(), name='profit_loss_detail'),
    path('profit-loss-comparison/', ProfitLossComparisonView.as_view(), name='profit_loss_comparison'),
    path('balance-sheets/', BalanceSheetListView.as_view(), name='balance_sheet_list'),
    
    # Customers & Vendors
    path('customers/', CustomerListView.as_view(), name='customer_list'),
    path('customers/<int:pk>/', CustomerDetailView.as_view(), name='customer_detail'),
    path('customers/<int:pk>/edit/', CustomerUpdateView.as_view(), name='customer_edit'),
    path('vendors/', VendorListView.as_view(), name='vendor_list'),
    path('vendors/<int:pk>/', VendorDetailView.as_view(), name='vendor_detail'),
    path('vendors/<int:pk>/edit/', VendorUpdateView.as_view(), name='vendor_edit'),
    
    # Invoices & Payments
    path('vendor-invoices/', VendorInvoiceListView.as_view(), name='vendor_invoice_list'),
    path('vendor-invoices/<int:pk>/', VendorInvoiceDetailView.as_view(), name='vendor_invoice_detail'),
    path('vendor-invoices/<int:pk>/edit/', VendorInvoiceUpdateView.as_view(), name='vendor_invoice_edit'),
    path('vendor-invoices/<int:pk>/update-status/', VendorInvoiceStatusUpdateView.as_view(), name='vendor_invoice_update_status'),
    path('vendor-invoices/<int:pk>/record-payment/', RecordVendorPaymentView.as_view(), name='record_vendor_payment'),
    path('vendor-payments/', VendorPaymentListView.as_view(), name='vendor_payments_list'),
    path('vendor-payments/create/', VendorPaymentCreateView.as_view(), name='vendor_payment_create'),
    path('vendor-payments/<int:pk>/edit/', VendorPaymentUpdateView.as_view(), name='vendor_payment_edit'),
    path('vendor-payments/<int:pk>/', VendorPaymentDetailView.as_view(), name='vendor_payment_detail'),
    
    # Fixed Assets
    path('fixed-assets/', FixedAssetListView.as_view(), name='fixed_asset_list'),
    path('fixed-assets/create/', FixedAssetCreateView.as_view(), name='fixed_asset_create'),
    path('fixed-assets/<int:pk>/edit/', FixedAssetUpdateView.as_view(), name='fixed_asset_edit'),
    path('fixed-assets/<int:pk>/delete/', FixedAssetDeleteView.as_view(), name='fixed_asset_delete'),
    
    # Banking
    path('bank-profiles/', BankProfileListView.as_view(), name='bank_profiles_list'),
    path('bank-profiles/create/', BankProfileCreateView.as_view(), name='bank_profile_create'),
    path('bank-profiles/<int:pk>/edit/', BankProfileUpdateView.as_view(), name='bank_profile_edit'),
    path('bank-profiles/<int:pk>/delete/', BankProfileDeleteView.as_view(), name='bank_profile_delete'),
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
    path('entities/create/', EntityCreateView.as_view(), name='entity_create'),
    path('entities/<int:pk>/edit/', EntityUpdateView.as_view(), name='entity_edit'),
    path('entities/<int:pk>/delete/', EntityDeleteView.as_view(), name='entity_delete'),
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
    
    # User Management with Module Permissions
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/edit/', UserEditView.as_view(), name='user_edit'),
    path('users/<int:pk>/apply-template/', UserApplyTemplateView.as_view(), name='user_apply_template'),
    path('users/<int:pk>/toggle-status/', UserToggleStatusView.as_view(), name='user_toggle_status'),
    
    # Import/Export Dashboard
    path('import-export/', ImportExportDashboardView.as_view(), name='import_export_dashboard'),
    
    # Account Import/Export
    path('accounts/import/', BaseImportView.as_view(
        importer_class=AccountImporter,
        module_name='accounting',
        success_url='/accounting/accounts/'
    ), name='account_import'),
    path('accounts/export/', BaseExportView.as_view(
        exporter_class=AccountExporter,
        module_name='accounting'
    ), name='account_export'),
    path('accounts/import-template/', ImportTemplateDownloadView.as_view(
        model_class=Account,
        template_fields=['account_number', 'account_name', 'account_type', 'description', 'parent_account', 'is_active'],
        module_name='accounting'
    ), name='account_import_template'),
    
    # Customer Import/Export
    path('customers/import/', BaseImportView.as_view(
        importer_class=CustomerImporter,
        module_name='accounting',
        success_url='/accounting/customers/'
    ), name='customer_import'),
    path('customers/export/', BaseExportView.as_view(
        exporter_class=CustomerExporter,
        module_name='accounting'
    ), name='customer_export'),
    path('customers/import-template/', ImportTemplateDownloadView.as_view(
        model_class=Customer,
        template_fields=['name', 'email', 'phone', 'address', 'city', 'state', 'country', 'postal_code', 'tax_id', 'credit_limit', 'is_active'],
        module_name='accounting'
    ), name='customer_import_template'),
    
    # Vendor Import/Export
    path('vendors/import/', BaseImportView.as_view(
        importer_class=VendorImporter,
        module_name='accounting',
        success_url='/accounting/vendors/'
    ), name='vendor_import'),
    path('vendors/export/', BaseExportView.as_view(
        exporter_class=VendorExporter,
        module_name='accounting'
    ), name='vendor_export'),
    path('vendors/import-template/', ImportTemplateDownloadView.as_view(
        model_class=Vendor,
        template_fields=['name', 'email', 'phone', 'address', 'city', 'state', 'country', 'postal_code', 'tax_id', 'payment_terms', 'is_active'],
        module_name='accounting'
    ), name='vendor_import_template'),
    
    # Ledger Entry Export (export only)
    path('ledger-entries/export/', BaseExportView.as_view(
        exporter_class=LedgerEntryExporter,
        module_name='accounting'
    ), name='ledger_entry_export'),
    
    # Cash Receipts
    path('cash-receipts/', CashReceiptListView.as_view(), name='cash_receipt_list'),
    path('cash-receipts/create/', CashReceiptCreateView.as_view(), name='cash_receipt_create'),
    path('cash-receipts/<int:pk>/', CashReceiptDetailView.as_view(), name='cash_receipt_detail'),
    path('cash-receipts/<int:pk>/print/', CashReceiptPrintView.as_view(), name='cash_receipt_print'),
    path('cash-receipts/<int:pk>/approve/', CashReceiptApprovalView.as_view(), name='cash_receipt_approve'),
    path('cash-receipts/<int:pk>/authorize/', CashReceiptAuthorizationView.as_view(), name='cash_receipt_authorize'),
    path('cash-receipts/<int:pk>/reject/', CashReceiptRejectView.as_view(), name='cash_receipt_reject'),
    
    # Cash Payments
    path('cash-payments/', CashPaymentListView.as_view(), name='cash_payment_list'),
    path('cash-payments/create/', CashPaymentCreateView.as_view(), name='cash_payment_create'),
    path('cash-payments/<int:pk>/', CashPaymentDetailView.as_view(), name='cash_payment_detail'),
    path('cash-payments/<int:pk>/print/', CashPaymentPrintView.as_view(), name='cash_payment_print'),
    path('cash-payments/<int:pk>/approve/', CashPaymentApprovalView.as_view(), name='cash_payment_approve'),
    path('cash-payments/<int:pk>/authorize/', CashPaymentAuthorizationView.as_view(), name='cash_payment_authorize'),
    path('cash-payments/<int:pk>/reject/', CashPaymentRejectView.as_view(), name='cash_payment_reject'),
    
    # Bank Receipts
    path('bank-receipts/', BankReceiptListView.as_view(), name='bank_receipt_list'),
    path('bank-receipts/create/', BankReceiptCreateView.as_view(), name='bank_receipt_create'),
    path('bank-receipts/<int:pk>/', BankReceiptDetailView.as_view(), name='bank_receipt_detail'),
    path('bank-receipts/<int:pk>/print/', BankReceiptPrintView.as_view(), name='bank_receipt_print'),
    path('bank-receipts/<int:pk>/approve/', BankReceiptApprovalView.as_view(), name='bank_receipt_approve'),
    path('bank-receipts/<int:pk>/authorize/', BankReceiptAuthorizationView.as_view(), name='bank_receipt_authorize'),
    path('bank-receipts/<int:pk>/reject/', BankReceiptRejectView.as_view(), name='bank_receipt_reject'),
    
    # Bank Payments
    path('bank-payments/', BankPaymentListView.as_view(), name='bank_payment_list'),
    path('bank-payments/create/', BankPaymentCreateView.as_view(), name='bank_payment_create'),
    path('bank-payments/<int:pk>/', BankPaymentDetailView.as_view(), name='bank_payment_detail'),
    path('bank-payments/<int:pk>/print/', BankPaymentPrintView.as_view(), name='bank_payment_print'),
    path('bank-payments/<int:pk>/approve/', BankPaymentApprovalView.as_view(), name='bank_payment_approve'),
    path('bank-payments/<int:pk>/authorize/', BankPaymentAuthorizationView.as_view(), name='bank_payment_authorize'),
    path('bank-payments/<int:pk>/reject/', BankPaymentRejectView.as_view(), name='bank_payment_reject'),
]

# Import dashboard views
from .views_dashboard import AccountingDashboardView, CashPositionView

# Add capital & cash position URLs
urlpatterns += [
    # Capital & Cash Position Dashboards
    path('accounting-dashboard/', AccountingDashboardView.as_view(), name='accounting_dashboard'),
    path('cash-position/', CashPositionView.as_view(), name='cash_position'),
    path('theme/', include('accounting.urls_theme')),
]
