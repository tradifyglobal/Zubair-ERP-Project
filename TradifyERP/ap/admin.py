from django.contrib import admin
from .models import (
    VendorBill, VendorBillLineItem, VendorPayment, 
    APDiscount, APAging, APReconciliation, APSettings
)


class VendorBillLineItemInline(admin.TabularInline):
    model = VendorBillLineItem
    extra = 1
    fields = ('description', 'quantity', 'unit_price', 'line_total', 'expense_account', 'po_line_item')
    readonly_fields = ('line_total',)


@admin.register(VendorBill)
class VendorBillAdmin(admin.ModelAdmin):
    list_display = ('bill_number', 'vendor', 'entity', 'bill_date', 'due_date', 'total_amount', 'payment_status', 'is_approved')
    list_filter = ('entity', 'status', 'payment_status', 'is_approved', 'bill_date', 'due_date')
    search_fields = ('bill_number', 'vendor__name')
    readonly_fields = ('created_date', 'updated_date', 'gl_entry')
    date_hierarchy = 'bill_date'
    inlines = [VendorBillLineItemInline]
    
    fieldsets = (
        ('Bill Information', {
            'fields': ('bill_number', 'vendor', 'entity', 'bill_date', 'due_date', 'status')
        }),
        ('Financial Details', {
            'fields': ('total_amount', 'amount_paid', 'payment_status', 'currency')
        }),
        ('Approval & GL', {
            'fields': ('is_approved', 'approved_by', 'gl_entry')
        }),
        ('Timestamps', {
            'fields': ('created_date', 'updated_date'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VendorBillLineItem)
class VendorBillLineItemAdmin(admin.ModelAdmin):
    list_display = ('bill', 'description', 'quantity', 'unit_price', 'line_total', 'expense_account')
    list_filter = ('bill__entity', 'expense_account')
    search_fields = ('bill__bill_number', 'description')
    readonly_fields = ('line_total',)


class APReconciliationInline(admin.TabularInline):
    model = APReconciliation
    extra = 1
    fields = ('bill', 'payment', 'matched_amount', 'matched_date')
    readonly_fields = ('matched_date',)


@admin.register(VendorPayment)
class VendorPaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_number', 'vendor', 'entity', 'payment_date', 'payment_amount', 'payment_method', 'is_approved')
    list_filter = ('entity', 'payment_method', 'payment_date', 'is_approved')
    search_fields = ('payment_number', 'vendor__name', 'check_number')
    readonly_fields = ('created_by', 'created_date', 'gl_entry')
    date_hierarchy = 'payment_date'
    inlines = [APReconciliationInline]
    filter_horizontal = ('bills',)
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_number', 'vendor', 'entity', 'payment_date', 'payment_amount')
        }),
        ('Payment Method', {
            'fields': ('payment_method', 'check_number', 'bank_account')
        }),
        ('Bills Paid', {
            'fields': ('bills',),
        }),
        ('Approval & GL', {
            'fields': ('is_approved', 'approved_by', 'gl_entry')
        }),
        ('Audit', {
            'fields': ('created_by', 'created_date'),
            'classes': ('collapse',)
        }),
    )


@admin.register(APDiscount)
class APDiscountAdmin(admin.ModelAdmin):
    list_display = ('bill', 'discount_percentage', 'discount_days', 'discount_amount', 'discount_taken')
    list_filter = ('bill__entity', 'discount_taken', 'discount_days')
    search_fields = ('bill__bill_number', 'bill__vendor__name')
    readonly_fields = ('discount_amount',)


@admin.register(APReconciliation)
class APReconciliationAdmin(admin.ModelAdmin):
    list_display = ('bill', 'payment', 'matched_amount', 'matched_date')
    list_filter = ('matched_date', 'bill__entity')
    search_fields = ('bill__bill_number', 'payment__payment_number')
    date_hierarchy = 'matched_date'
    readonly_fields = ('matched_date',)


@admin.register(APAging)
class APAgingAdmin(admin.ModelAdmin):
    list_display = ('entity', 'report_date', 'current', 'days_1_30', 'days_31_60', 'days_61_90', 'days_over_90', 'total_outstanding')
    list_filter = ('entity', 'report_date')
    date_hierarchy = 'report_date'
    readonly_fields = ('current', 'days_1_30', 'days_31_60', 'days_61_90', 'days_over_90', 'total_outstanding', 'report_date')


@admin.register(APSettings)
class APSettingsAdmin(admin.ModelAdmin):
    list_display = ('entity', 'require_po_for_bill', 'require_approval', 'enable_3way_matching')
    list_filter = ('entity', 'require_po_for_bill', 'require_approval', 'enable_3way_matching')
    search_fields = ('entity__name',)
    
    fieldsets = (
        ('Entity', {
            'fields': ('entity',)
        }),
        ('Bill Requirements', {
            'fields': ('require_po_for_bill', 'require_approval')
        }),
        ('Matching & GL', {
            'fields': ('enable_3way_matching', 'auto_post_to_gl')
        }),
        ('Discount Settings', {
            'fields': ('discount_account',)
        }),
    )
