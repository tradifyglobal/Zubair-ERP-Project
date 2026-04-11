from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Entity, Currency, Account, LedgerEntry, TrialBalance, ProfitLossReport,
    BalanceSheet, CashFlowForecast, CashTransaction, BankProfile, BankStatement,
    ReconciliationEntry, ReconciliationRecord, ReconciliationMatch,
    TaxRate, TaxTransaction, TaxSummary,
    Customer, Vendor, VendorInvoice, VendorPayment,
    FixedAsset, DeferredExpense, DeferredRevenue,
    PeriodLock, AuditLog,
    Stakeholder, CapitalContribution, Shareholding, UserEntity, ReportAccess,
    CashReceiptLine, CashPaymentLine, BankReceiptLine, BankPaymentLine,
    JournalVoucher, JournalVoucherLine
)
from .models_theme import Theme, UserThemePreference
from .module_permissions import ModulePermission


# ==================== Module Permissions ====================

class ModulePermissionInline(admin.TabularInline):
    """Inline admin for module permissions - allows editing permissions directly in User admin."""
    model = ModulePermission
    fk_name = 'user'  # Specify which ForeignKey to use for the inline
    extra = 0
    fields = ('module', 'can_view', 'can_add', 'can_edit', 'can_delete', 'can_review', 'can_approve', 'can_export', 'is_active')
    readonly_fields = ('module',)
    max_num = 100  # Limit to 100 inline forms to prevent exceeding field limits
    
    def get_queryset(self, request):
        """Optimize queryset to prevent too many fields."""
        qs = super().get_queryset(request)
        # Order by active status first, then by module
        # Don't slice the queryset - Django inlines handle the limit via max_num
        return qs.select_related('user').order_by('-is_active', 'module')


@admin.register(ModulePermission)
class ModulePermissionAdmin(admin.ModelAdmin):
    """Admin interface for managing module permissions."""
    list_display = ('user', 'module', 'permission_summary', 'is_active', 'granted_date')
    list_filter = ('module', 'is_active', 'granted_date', 'can_view', 'can_add', 'can_edit', 'can_delete')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('granted_date', 'created_at', 'updated_at', 'permission_summary')
    date_hierarchy = 'granted_date'
    
    fieldsets = (
        ('User & Module', {
            'fields': ('user', 'module')
        }),
        ('Permissions', {
            'fields': ('can_view', 'can_add', 'can_edit', 'can_delete', 'can_review', 'can_approve', 'can_export'),
            'description': 'Check the permissions this user should have for this module'
        }),
        ('Additional Info', {
            'fields': ('access_level', 'is_active', 'notes'),
            'classes': ('wide',)
        }),
        ('Audit Information', {
            'fields': ('granted_by', 'granted_date', 'created_at', 'updated_at', 'permission_summary'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Set granted_by when creating new permission."""
        if not change:  # Creating new object
            obj.granted_by = request.user
        super().save_model(request, obj, form, change)


# Unregister the default User admin and register custom one
admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Extended User admin for basic user management."""
    inlines = [ModulePermissionInline]



class EntityAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('code', 'name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserEntity)
class UserEntityAdmin(admin.ModelAdmin):
    list_display = ('user', 'entity', 'is_default', 'can_switch', 'assigned_at')
    list_filter = ('is_default', 'can_switch', 'entity', 'assigned_at')
    search_fields = ('user__username', 'user__email', 'entity__name', 'entity__code')
    readonly_fields = ('assigned_at',)
    raw_id_fields = ('user', 'entity', 'assigned_by')
    
    def save_model(self, request, obj, form, change):
        """Set assigned_by when creating new UserEntity."""
        if not change:  # Creating new object
            obj.assigned_by = request.user
        super().save_model(request, obj, form, change)


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
    
    def get_fieldsets(self, request, obj=None):
        """Dynamically add start_date and end_date fields if they exist on the model."""
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
        
        # Dynamically add Profit Calculation Dates section if fields exist
        model_field_names = [f.name for f in self.model._meta.get_fields()]
        if 'start_date' in model_field_names and 'end_date' in model_field_names:
            profit_section = (
                'Profit Calculation Dates',
                {
                    'fields': ('start_date', 'end_date'),
                    'description': 'Set the date range for profit calculation purposes (leave blank for ongoing)',
                    'classes': ('collapse',)
                }
            )
            # Insert before System section
            fieldsets = fieldsets[:-1] + (profit_section,) + (fieldsets[-1],)
        
        return fieldsets


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


# ============ CASH MANAGEMENT ADMIN ============

@admin.register(CashReceiptLine)
class CashReceiptLineAdmin(admin.ModelAdmin):
    list_display = ('date', 'entity', 'description', 'debit_amount', 'credit_amount', 'status')
    list_filter = ('entity', 'status', 'date')
    search_fields = ('description', 'reference_number')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('account',)
    
    fieldsets = (
        ('General', {
            'fields': ('entity', 'date', 'description', 'reference_number')
        }),
        ('Transaction', {
            'fields': ('account', 'debit_amount', 'credit_amount', 'status')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CashPaymentLine)
class CashPaymentLineAdmin(admin.ModelAdmin):
    list_display = ('date', 'entity', 'description', 'debit_amount', 'credit_amount', 'status')
    list_filter = ('entity', 'status', 'date')
    search_fields = ('description', 'reference_number')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('account',)
    
    fieldsets = (
        ('General', {
            'fields': ('entity', 'date', 'description', 'reference_number')
        }),
        ('Transaction', {
            'fields': ('account', 'debit_amount', 'credit_amount', 'status')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BankReceiptLine)
class BankReceiptLineAdmin(admin.ModelAdmin):
    list_display = ('date', 'entity', 'debit_amount', 'workflow_status', 'status')
    list_filter = ('entity', 'status', 'workflow_status', 'date')
    search_fields = ('description', 'reference_number')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('account', 'credit_account')
    
    fieldsets = (
        ('General', {
            'fields': ('entity', 'date', 'description', 'reference_number')
        }),
        ('Transaction', {
            'fields': ('account', 'credit_account', 'debit_amount', 'credit_amount', 'status', 'workflow_status')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BankPaymentLine)
class BankPaymentLineAdmin(admin.ModelAdmin):
    list_display = ('date', 'entity', 'debit_amount', 'workflow_status', 'status')
    list_filter = ('entity', 'status', 'workflow_status', 'date')
    search_fields = ('description', 'reference_number')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('account', 'credit_account')
    
    fieldsets = (
        ('General', {
            'fields': ('entity', 'date', 'description', 'reference_number')
        }),
        ('Transaction', {
            'fields': ('account', 'credit_account', 'debit_amount', 'credit_amount', 'status', 'workflow_status')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Theme Management Admin
@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'display_name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Theme Information', {
            'fields': ('name', 'display_name', 'description', 'is_active')
        }),
        ('Media', {
            'fields': ('thumbnail_url',),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserThemePreference)
class UserThemePreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'sidebar_color', 'layout_mode')
    list_filter = ('theme', 'layout_mode', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user', 'created_at', 'updated_at')
    
    fieldsets = (
        ('User & Theme', {
            'fields': ('user', 'theme')
        }),
        ('Layout Preferences', {
            'fields': ('sidebar_color', 'layout_mode', 'layout_size')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Prevent manual creation - preferences are auto-created by signal."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion - preferences are tied to user."""
        return False


# ==================== Journal Voucher Admin ====================

class JournalVoucherLineInline(admin.TabularInline):
    """Inline admin for Journal Voucher Lines"""
    model = JournalVoucherLine
    extra = 1
    fields = ('line_number', 'account', 'sub_account', 'entry_type', 'amount', 'description', 'cost_center', 'project', 'department')
    raw_id_fields = ('account', 'sub_account')
    
    def get_queryset(self, request):
        """Order lines by line number"""
        qs = super().get_queryset(request)
        return qs.order_by('line_number')


@admin.register(JournalVoucher)
class JournalVoucherAdmin(admin.ModelAdmin):
    """Admin interface for Journal Vouchers"""
    list_display = ('voucher_number', 'voucher_date', 'voucher_type', 'entity', 'status', 'total_debit', 'total_credit')
    list_filter = ('voucher_type', 'status', 'voucher_date', 'entity')
    search_fields = ('voucher_number', 'description', 'reference_number')
    readonly_fields = ('voucher_number', 'created_at', 'updated_at', 'posted_date', 'posted_by', 'created_by')
    inlines = [JournalVoucherLineInline]
    date_hierarchy = 'voucher_date'
    
    fieldsets = (
        ('Voucher Information', {
            'fields': ('voucher_number', 'voucher_date', 'voucher_type', 'reference_number', 'reference_type', 'entity')
        }),
        ('Details', {
            'fields': ('description', 'notes', 'attachment', 'status')
        }),
        ('Approvals', {
            'fields': ('prepared_by', 'approved_by', 'posted_by'),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('created_by', 'created_at', 'updated_at', 'posted_date'),
            'classes': ('collapse',)
        }),
    )
    
    def total_debit(self, obj):
        """Display total debit amount"""
        return f"₹{obj.get_total_debit():,.2f}"
    total_debit.short_description = 'Total Debit'
    
    def total_credit(self, obj):
        """Display total credit amount"""
        return f"₹{obj.get_total_credit():,.2f}"
    total_credit.short_description = 'Total Credit'


@admin.register(JournalVoucherLine)
class JournalVoucherLineAdmin(admin.ModelAdmin):
    """Admin interface for Journal Voucher Lines (standalone access)"""
    list_display = ('voucher', 'line_number', 'account', 'entry_type', 'amount', 'description')
    list_filter = ('entry_type', 'voucher__entity', 'voucher__voucher_date')
    search_fields = ('voucher__voucher_number', 'description', 'account__name')
    readonly_fields = ('voucher', 'created_at', 'updated_at')
    raw_id_fields = ('account', 'sub_account')
    
    fieldsets = (
        ('Voucher & Line', {
            'fields': ('voucher', 'line_number')
        }),
        ('Accounts', {
            'fields': ('account', 'sub_account', 'entry_type')
        }),
        ('Amount & Description', {
            'fields': ('amount', 'description')
        }),
        ('Dimensions', {
            'fields': ('cost_center', 'project', 'department'),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Lines should be added via inline in Journal Voucher admin"""
        return False


# ==================== Report Access Control ====================

class ReportAccessInline(admin.TabularInline):
    """Inline admin for report access - allows managing report permissions in User admin."""
    model = ReportAccess
    fk_name = 'user'
    extra = 1
    fields = ('report_type', 'access_level', 'entity', 'is_active', 'expiry_date')
    can_delete = True
    
    def get_queryset(self, request):
        """Show active permissions first."""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'entity').order_by('-is_active', 'report_type')


@admin.register(ReportAccess)
class ReportAccessAdmin(admin.ModelAdmin):
    """Admin interface for managing report access control."""
    list_display = ('user', 'report_type_display', 'access_level_display', 'entity_display', 'is_active', 'expiry_status', 'granted_at')
    list_filter = ('report_type', 'access_level', 'entity', 'is_active', 'granted_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('granted_at', 'granted_by_display')
    date_hierarchy = 'granted_at'
    
    fieldsets = (
        ('User & Report', {
            'fields': ('user', 'report_type', 'entity')
        }),
        ('Access Settings', {
            'fields': ('access_level', 'is_active', 'expiry_date')
        }),
        ('Audit Trail', {
            'fields': ('granted_at', 'granted_by_display'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset."""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'entity', 'granted_by').order_by('-granted_at')
    
    def report_type_display(self, obj):
        """Display report name instead of code."""
        return dict(ReportAccess.REPORT_CHOICES).get(obj.report_type, obj.report_type)
    report_type_display.short_description = 'Report'
    report_type_display.admin_order_field = 'report_type'
    
    def access_level_display(self, obj):
        """Display access level with color."""
        colors = {
            'view_only': 'gray',
            'edit': 'blue',
            'full_access': 'green'
        }
        color = colors.get(obj.access_level, 'gray')
        label = dict(ReportAccess.ACCESS_LEVEL_CHOICES).get(obj.access_level, obj.access_level)
        return f'<span style="color: {color}; font-weight: bold;">{label}</span>'
    access_level_display.short_description = 'Access Level'
    access_level_display.allow_tags = True
    
    def entity_display(self, obj):
        """Display entity or 'All Entities'."""
        return obj.entity.name if obj.entity else 'All Entities'
    entity_display.short_description = 'Entity'
    entity_display.admin_order_field = 'entity'
    
    def expiry_status(self, obj):
        """Display expiry status."""
        if not obj.expiry_date:
            return '✓ No expiry'
        
        from datetime import date
        if obj.expiry_date < date.today():
            return f'❌ Expired ({obj.expiry_date})'
        else:
            days_left = (obj.expiry_date - date.today()).days
            if days_left <= 7:
                return f'⚠️ {days_left} days left'
            return f'✓ {days_left} days left'
    expiry_status.short_description = 'Expiry'
    
    def granted_by_display(self, obj):
        """Display who granted the access."""
        if obj.granted_by:
            return f"{obj.granted_by.get_full_name()} ({obj.granted_by.username})"
        return "System"
    granted_by_display.short_description = 'Granted By'
    
    def save_model(self, request, obj, form, change):
        """Set granted_by to current user if not set."""
        if not obj.granted_by:
            obj.granted_by = request.user
        super().save_model(request, obj, form, change)
