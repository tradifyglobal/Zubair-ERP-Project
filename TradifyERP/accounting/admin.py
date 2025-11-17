from django.contrib import admin
from .models import (
    Entity, Currency, Account, LedgerEntry, TrialBalance, ProfitLossReport,
    BalanceSheet, CashFlowForecast, CashTransaction, BankProfile, BankStatement,
    ReconciliationEntry, ReconciliationRecord, ReconciliationMatch,
    TaxRate, TaxTransaction, TaxSummary,
    Customer, Vendor, VendorInvoice, VendorPayment,
    FixedAsset, DeferredExpense, DeferredRevenue,
    PeriodLock, AuditLog,
    Stakeholder, CapitalContribution, Shareholding
)


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('code', 'name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'symbol', 'exchange_rate', 'is_active')
    list_filter = ('is_active', 'code')
    search_fields = ('code', 'name')


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'name', 'account_type', 'entity', 'is_active')
    list_filter = ('account_type', 'entity', 'is_active', 'created_at')
    search_fields = ('account_number', 'name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ('account', 'entry_date', 'entry_type', 'amount', 'is_posted')
    list_filter = ('entry_type', 'is_posted', 'entry_date', 'entity')
    search_fields = ('account__account_number', 'reference_number')
    date_hierarchy = 'entry_date'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TrialBalance)
class TrialBalanceAdmin(admin.ModelAdmin):
    list_display = ('entity', 'as_of_date', 'total_debits', 'total_credits', 'is_balanced')
    list_filter = ('entity', 'as_of_date', 'is_balanced')
    date_hierarchy = 'as_of_date'
    readonly_fields = ('created_at',)


@admin.register(ProfitLossReport)
class ProfitLossReportAdmin(admin.ModelAdmin):
    list_display = ('entity', 'period_start', 'period_end', 'net_profit')
    list_filter = ('entity', 'period_start')
    date_hierarchy = 'period_end'
    readonly_fields = ('created_at',)


@admin.register(BalanceSheet)
class BalanceSheetAdmin(admin.ModelAdmin):
    list_display = ('entity', 'as_of_date', 'total_assets', 'total_liabilities', 'total_equity')
    list_filter = ('entity', 'as_of_date')
    date_hierarchy = 'as_of_date'
    readonly_fields = ('created_at',)


@admin.register(CashFlowForecast)
class CashFlowForecastAdmin(admin.ModelAdmin):
    list_display = ('entity', 'forecast_period', 'opening_cash', 'closing_cash')
    list_filter = ('entity',)
    search_fields = ('forecast_period',)


@admin.register(CashTransaction)
class CashTransactionAdmin(admin.ModelAdmin):
    list_display = ('entity', 'transaction_date', 'transaction_type', 'amount', 'is_reconciled')
    list_filter = ('transaction_type', 'entity', 'transaction_date', 'is_reconciled')
    date_hierarchy = 'transaction_date'


@admin.register(BankProfile)
class BankProfileAdmin(admin.ModelAdmin):
    list_display = ('bank_name', 'account_number', 'entity', 'is_active')
    list_filter = ('entity', 'is_active')
    search_fields = ('bank_name', 'account_number')


@admin.register(BankStatement)
class BankStatementAdmin(admin.ModelAdmin):
    list_display = ('bank_profile', 'statement_date', 'opening_balance', 'closing_balance')
    list_filter = ('bank_profile', 'statement_date')
    date_hierarchy = 'statement_date'


@admin.register(ReconciliationEntry)
class ReconciliationEntryAdmin(admin.ModelAdmin):
    list_display = ('bank_statement', 'ledger_entry', 'matched_date')
    list_filter = ('matched_date',)
    date_hierarchy = 'matched_date'


@admin.register(ReconciliationRecord)
class ReconciliationRecordAdmin(admin.ModelAdmin):
    list_display = ('entity', 'reconciliation_date', 'status', 'total_items_reconciled', 'discrepancies_found')
    list_filter = ('entity', 'status', 'reconciliation_date')
    date_hierarchy = 'reconciliation_date'


@admin.register(ReconciliationMatch)
class ReconciliationMatchAdmin(admin.ModelAdmin):
    list_display = ('reconciliation_record', 'bank_entry_amount', 'ledger_entry_amount', 'variance')
    list_filter = ('reconciliation_record',)


@admin.register(TaxRate)
class TaxRateAdmin(admin.ModelAdmin):
    list_display = ('entity', 'tax_type', 'rate_percentage', 'effective_from', 'is_active')
    list_filter = ('entity', 'tax_type', 'is_active', 'effective_from')
    search_fields = ('tax_type',)


@admin.register(TaxTransaction)
class TaxTransactionAdmin(admin.ModelAdmin):
    list_display = ('entity', 'tax_rate', 'transaction_date', 'gross_amount', 'tax_amount')
    list_filter = ('entity', 'tax_rate', 'transaction_date')
    date_hierarchy = 'transaction_date'


@admin.register(TaxSummary)
class TaxSummaryAdmin(admin.ModelAdmin):
    list_display = ('entity', 'tax_type', 'period_start', 'period_end', 'total_tax')
    list_filter = ('entity', 'tax_type', 'period_start')
    date_hierarchy = 'period_end'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_code', 'name', 'entity', 'email', 'is_active')
    list_filter = ('entity', 'is_active', 'created_at')
    search_fields = ('customer_code', 'name', 'email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('vendor_code', 'name', 'entity', 'email', 'is_active')
    list_filter = ('entity', 'is_active', 'created_at')
    search_fields = ('vendor_code', 'name', 'email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(VendorInvoice)
class VendorInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'vendor', 'invoice_date', 'total_amount', 'status')
    list_filter = ('entity', 'status', 'invoice_date')
    search_fields = ('invoice_number', 'vendor__name')
    date_hierarchy = 'invoice_date'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(VendorPayment)
class VendorPaymentAdmin(admin.ModelAdmin):
    list_display = ('vendor_invoice', 'payment_date', 'amount', 'payment_method')
    list_filter = ('entity', 'payment_method', 'payment_date')
    date_hierarchy = 'payment_date'


@admin.register(FixedAsset)
class FixedAssetAdmin(admin.ModelAdmin):
    list_display = ('asset_code', 'name', 'category', 'purchase_cost', 'book_value', 'is_active')
    list_filter = ('entity', 'category', 'is_active', 'purchase_date')
    search_fields = ('asset_code', 'name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DeferredExpense)
class DeferredExpenseAdmin(admin.ModelAdmin):
    list_display = ('entity', 'description', 'amount', 'deferral_date', 'expiry_date')
    list_filter = ('entity', 'expense_type', 'expiry_date')
    date_hierarchy = 'expiry_date'


@admin.register(DeferredRevenue)
class DeferredRevenueAdmin(admin.ModelAdmin):
    list_display = ('entity', 'description', 'amount', 'deferral_date', 'recognition_date')
    list_filter = ('entity', 'revenue_type', 'recognition_date')
    date_hierarchy = 'recognition_date'


@admin.register(PeriodLock)
class PeriodLockAdmin(admin.ModelAdmin):
    list_display = ('entity', 'period_start', 'period_end', 'is_locked', 'locked_at')
    list_filter = ('entity', 'is_locked', 'period_start')
    readonly_fields = ('created_at',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('entity', 'action', 'model_name', 'object_id', 'user', 'timestamp')
    list_filter = ('entity', 'action', 'model_name', 'timestamp')
    search_fields = ('model_name', 'object_id', 'user')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp', 'entity', 'action', 'model_name', 'object_id', 'user', 'description', 'old_values', 'new_values')


@admin.register(Stakeholder)
class StakeholderAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'entity', 'stakeholder_type', 'status', 'email', 'phone_number', 'created_at')
    list_filter = ('entity', 'stakeholder_type', 'status', 'created_at')
    search_fields = ('first_name', 'last_name', 'company_name', 'email', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('entity', 'stakeholder_type', 'status')
        }),
        ('Personal Details', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'gender', 'nationality', 'occupation'),
            'classes': ('collapse',)
        }),
        ('Corporate Details', {
            'fields': ('company_name', 'registration_number', 'company_type', 'relationship_to_company'),
            'classes': ('collapse',)
        }),
        ('Contact Information', {
            'fields': ('email', 'phone_number', 'secondary_phone', 'fax')
        }),
        ('Address', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state_province', 'postal_code', 'country')
        }),
        ('Tax & Legal', {
            'fields': ('tax_identification_number', 'tax_id_type')
        }),
        ('Additional', {
            'fields': ('joined_date', 'notes'),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CapitalContribution)
class CapitalContributionAdmin(admin.ModelAdmin):
    list_display = ('stakeholder', 'contribution_date', 'amount', 'status', 'payment_mode', 'created_at')
    list_filter = ('entity', 'status', 'payment_mode', 'contribution_date', 'created_at')
    search_fields = ('stakeholder__first_name', 'stakeholder__last_name', 'reference_number', 'payment_method_details')
    date_hierarchy = 'contribution_date'
    readonly_fields = ('created_at', 'updated_at', 'amount_company_currency', 'amount_usd')
    fieldsets = (
        ('Contribution Details', {
            'fields': ('entity', 'stakeholder', 'contribution_date', 'status', 'reference_number')
        }),
        ('Amount Information', {
            'fields': ('currency', 'amount', 'currency_destination', 'amount_company_currency', 'exchange_rate', 'amount_usd')
        }),
        ('Payment Method', {
            'fields': ('payment_mode', 'payment_method_details')
        }),
        ('Bank Information', {
            'fields': ('paying_bank_name', 'paying_account_number', 'paying_account_holder')
        }),
        ('Accounting', {
            'fields': ('equity_account', 'cash_account'),
            'classes': ('collapse',)
        }),
        ('Documentation', {
            'fields': ('document_file',),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Shareholding)
class ShareholdingAdmin(admin.ModelAdmin):
    list_display = ('stakeholder', 'number_of_shares', 'share_type', 'acquisition_date', 'created_at')
    list_filter = ('entity', 'share_type', 'share_class', 'acquisition_date', 'created_at', 'is_active')
    search_fields = ('stakeholder__first_name', 'stakeholder__last_name', 'certificate_number')
    date_hierarchy = 'acquisition_date'
    readonly_fields = ('created_at', 'updated_at', 'ownership_percentage', 'total_value_at_acquisition')
    fieldsets = (
        ('Share Details', {
            'fields': ('entity', 'stakeholder', 'number_of_shares', 'share_type', 'share_class', 'par_value')
        }),
        ('Acquisition', {
            'fields': ('acquisition_date', 'acquisition_price', 'acquisition_currency', 'vesting_schedule')
        }),
        ('Vesting Schedule', {
            'fields': ('vesting_start_date', 'vesting_end_date')
        }),
        ('Rights & Terms', {
            'fields': ('voting_rights_percentage', 'dividend_rights_percentage', 'is_active', 'is_transferable', 'is_redeemable', 'redemption_price')
        }),
        ('Certification', {
            'fields': ('certificate_number', 'certificate_file')
        }),
        ('Accounting', {
            'fields': ('stock_ledger_account',),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
