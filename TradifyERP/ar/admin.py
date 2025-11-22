from django.contrib import admin
from .models import (
    CustomerInvoice, InvoiceLineItem, CustomerPayment, ARDiscount,
    ARReconciliation, ARAging, ARSettings
)


class InvoiceLineItemInline(admin.TabularInline):
    """Inline editing for invoice line items."""
    model = InvoiceLineItem
    extra = 1
    fields = ['description', 'quantity', 'unit_price', 'line_total', 'revenue_account', 'cost_center']
    readonly_fields = ['line_total']


class ARReconciliationInline(admin.TabularInline):
    """Inline editing for reconciliations."""
    model = ARReconciliation
    extra = 0
    fields = ['payment', 'matched_amount', 'is_matched', 'matched_date']
    readonly_fields = ['matched_date']


@admin.register(CustomerInvoice)
class CustomerInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer', 'entity', 'invoice_date', 'total_amount', 'amount_paid', 'status']
    list_filter = ['status', 'entity', 'invoice_date', 'is_approved']
    search_fields = ['invoice_number', 'customer__customer_name', 'po_number']
    readonly_fields = ['created_date', 'updated_date', 'created_by', 'approved_date']
    inlines = [InvoiceLineItemInline]
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'entity', 'customer', 'invoice_date', 'due_date', 'po_number')
        }),
        ('Amounts', {
            'fields': ('subtotal_amount', 'tax_amount', 'total_amount', 'amount_paid')
        }),
        ('Status & Approval', {
            'fields': ('status', 'is_approved', 'approved_by', 'approved_date')
        }),
        ('GL Integration', {
            'fields': ('gl_entry',)
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_date', 'updated_date'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(InvoiceLineItem)
class InvoiceLineItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'description', 'quantity', 'unit_price', 'line_total', 'revenue_account']
    list_filter = ['invoice__entity', 'revenue_account']
    search_fields = ['description', 'invoice__invoice_number']
    
    fieldsets = (
        ('Line Item Details', {
            'fields': ('invoice', 'description', 'quantity', 'unit_price', 'line_total')
        }),
        ('GL Coding', {
            'fields': ('revenue_account', 'cost_center')
        }),
    )


@admin.register(CustomerPayment)
class CustomerPaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_number', 'customer', 'entity', 'payment_date', 'payment_amount', 'payment_method']
    list_filter = ['payment_method', 'entity', 'payment_date']
    search_fields = ['payment_number', 'customer__customer_name', 'reference_number']
    readonly_fields = ['created_date', 'updated_date', 'created_by', 'approved_date']
    inlines = [ARReconciliationInline]
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_number', 'entity', 'customer', 'payment_date', 'payment_amount')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'reference_number', 'bank_account')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_date')
        }),
        ('GL Integration', {
            'fields': ('gl_entry',)
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_date', 'updated_date'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ARDiscount)
class ARDiscountAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'discount_percentage', 'discount_days', 'discount_amount', 'is_eligible']
    list_filter = ['discount_percentage', 'discount_days']
    search_fields = ['invoice__invoice_number']
    
    fieldsets = (
        ('Discount Details', {
            'fields': ('invoice', 'discount_percentage', 'discount_days', 'discount_amount')
        }),
        ('GL Coding', {
            'fields': ('discount_account',)
        }),
    )
    
    def is_eligible(self, obj):
        return obj.is_eligible()
    is_eligible.boolean = True


@admin.register(ARReconciliation)
class ARReconciliationAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'payment', 'matched_amount', 'is_matched', 'matched_date']
    list_filter = ['entity', 'is_matched', 'matched_date']
    search_fields = ['invoice__invoice_number', 'payment__payment_number']
    readonly_fields = ['matched_date']
    
    fieldsets = (
        ('Reconciliation Details', {
            'fields': ('entity', 'invoice', 'payment', 'matched_amount', 'is_matched', 'matched_date')
        }),
    )


@admin.register(ARAging)
class ARAgingAdmin(admin.ModelAdmin):
    list_display = ['customer', 'entity', 'as_of_date', 'age_bucket', 'outstanding_amount', 'invoice_count']
    list_filter = ['entity', 'as_of_date', 'age_bucket']
    search_fields = ['customer__customer_name']
    readonly_fields = ['as_of_date']
    
    fieldsets = (
        ('Aging Information', {
            'fields': ('entity', 'customer', 'as_of_date', 'age_bucket', 'outstanding_amount', 'invoice_count')
        }),
    )


@admin.register(ARSettings)
class ARSettingsAdmin(admin.ModelAdmin):
    list_display = ['entity', 'require_approval', 'enable_credit_limit_check', 'auto_post_to_gl']
    list_filter = ['entity', 'require_approval', 'auto_post_to_gl']
    
    fieldsets = (
        ('Entity Configuration', {
            'fields': ('entity',)
        }),
        ('Approval & Validation', {
            'fields': ('require_po_for_invoice', 'require_approval', 'enable_credit_limit_check')
        }),
        ('GL Integration', {
            'fields': ('auto_post_to_gl', 'discount_account', 'revenue_account', 'receivable_account')
        }),
    )
