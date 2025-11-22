from django.contrib import admin
from .models import (
    PurchaseOrder, POLineItem, GoodsReceipt, GoodsReceiptLineItem,
    ThreeWayMatching, RequestForQuotation, VendorQuotation, ProcurementSettings
)


class POLineItemInline(admin.TabularInline):
    model = POLineItem
    extra = 1
    fields = ('description', 'quantity_ordered', 'unit_price', 'quantity_received', 'quantity_invoiced', 'inventory_product')
    readonly_fields = ('quantity_received', 'quantity_invoiced')


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('po_number', 'vendor', 'entity', 'po_date', 'expected_delivery_date', 'total_amount', 'status')
    list_filter = ('entity', 'status', 'po_date', 'expected_delivery_date')
    search_fields = ('po_number', 'vendor__name')
    readonly_fields = ('po_date', 'amount_received', 'amount_invoiced', 'created_date', 'updated_date')
    date_hierarchy = 'po_date'
    inlines = [POLineItemInline]
    
    fieldsets = (
        ('PO Information', {
            'fields': ('po_number', 'vendor', 'entity', 'po_date', 'expected_delivery_date', 'status')
        }),
        ('Financial Details', {
            'fields': ('total_amount', 'amount_received', 'amount_invoiced', 'currency')
        }),
        ('Timestamps', {
            'fields': ('created_date', 'updated_date'),
            'classes': ('collapse',)
        }),
    )


@admin.register(POLineItem)
class POLineItemAdmin(admin.ModelAdmin):
    list_display = ('po', 'description', 'quantity_ordered', 'unit_price', 'quantity_received', 'quantity_invoiced')
    list_filter = ('po__entity', 'po__status')
    search_fields = ('po__po_number', 'description')
    readonly_fields = ('quantity_received', 'quantity_invoiced')


class GoodsReceiptLineItemInline(admin.TabularInline):
    model = GoodsReceiptLineItem
    extra = 1
    fields = ('po_line', 'quantity_received', 'quantity_accepted', 'quantity_rejected', 'rejection_reason')


@admin.register(GoodsReceipt)
class GoodsReceiptAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'po', 'receipt_date', 'status', 'carrier', 'tracking_number')
    list_filter = ('receipt_date', 'status', 'po__vendor', 'po__entity')
    search_fields = ('receipt_number', 'po__po_number', 'tracking_number')
    readonly_fields = ('receipt_date', 'created_date', 'gl_entry')
    date_hierarchy = 'receipt_date'
    inlines = [GoodsReceiptLineItemInline]
    
    fieldsets = (
        ('Receipt Information', {
            'fields': ('receipt_number', 'po', 'receipt_date', 'status')
        }),
        ('Shipment Details', {
            'fields': ('carrier', 'tracking_number')
        }),
        ('GL', {
            'fields': ('gl_entry',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_date',),
            'classes': ('collapse',)
        }),
    )


@admin.register(GoodsReceiptLineItem)
class GoodsReceiptLineItemAdmin(admin.ModelAdmin):
    list_display = ('receipt', 'po_line', 'quantity_received', 'quantity_accepted', 'quantity_rejected')
    list_filter = ('receipt__po__entity', 'receipt__status')
    search_fields = ('receipt__receipt_number', 'po_line__po__po_number')
    readonly_fields = ('quantity_received',)


class ThreeWayMatchingInline(admin.TabularInline):
    model = ThreeWayMatching
    extra = 0
    fields = ('po', 'po_amount', 'receipt_amount', 'invoice_amount', 'quantity_variance', 'price_variance', 'discrepancy_notes')
    readonly_fields = ('po_amount', 'receipt_amount', 'invoice_amount')


@admin.register(ThreeWayMatching)
class ThreeWayMatchingAdmin(admin.ModelAdmin):
    list_display = ('po', 'po_amount', 'receipt_amount', 'invoice_amount', 'quantity_variance', 'price_variance', 'resolved')
    list_filter = ('resolved', 'po__entity', 'po__po_date')
    search_fields = ('po__po_number',)
    readonly_fields = ('po_amount', 'receipt_amount', 'invoice_amount', 'quantity_variance', 'price_variance')
    
    fieldsets = (
        ('Documents', {
            'fields': ('po', 'po_line', 'receipt_line', 'bill_line')
        }),
        ('Amounts', {
            'fields': ('po_amount', 'receipt_amount', 'invoice_amount')
        }),
        ('Variances', {
            'fields': ('quantity_variance', 'price_variance')
        }),
        ('Discrepancy Tracking', {
            'fields': ('discrepancy_notes', 'resolved', 'resolution_notes')
        }),
    )


class VendorQuotationInline(admin.TabularInline):
    model = VendorQuotation
    extra = 1
    fields = ('vendor', 'quote_number', 'quote_date', 'quote_amount', 'delivery_days', 'score')
    readonly_fields = ('quote_date',)


@admin.register(RequestForQuotation)
class RequestForQuotationAdmin(admin.ModelAdmin):
    list_display = ('rfq_number', 'entity', 'response_deadline', 'awarded_to', 'award_date')
    list_filter = ('entity', 'response_deadline', 'awarded_to', 'award_date')
    search_fields = ('rfq_number', 'awarded_to__name')
    readonly_fields = ('created_date',)
    date_hierarchy = 'response_deadline'
    inlines = [VendorQuotationInline]
    filter_horizontal = ('vendors',)
    
    fieldsets = (
        ('RFQ Information', {
            'fields': ('rfq_number', 'entity', 'vendors', 'response_deadline')
        }),
        ('Award Details', {
            'fields': ('awarded_to', 'award_date')
        }),
        ('Timestamps', {
            'fields': ('created_date',),
            'classes': ('collapse',)
        }),
    )


@admin.register(VendorQuotation)
class VendorQuotationAdmin(admin.ModelAdmin):
    list_display = ('rfq', 'vendor', 'quote_number', 'quote_date', 'quote_amount', 'delivery_days', 'score', 'status')
    list_filter = ('status', 'quote_date', 'rfq__entity')
    search_fields = ('quote_number', 'vendor__name', 'rfq__rfq_number')
    readonly_fields = ('quote_date',)
    date_hierarchy = 'quote_date'
    
    fieldsets = (
        ('Quote Information', {
            'fields': ('rfq', 'vendor', 'quote_number', 'quote_date', 'status')
        }),
        ('Financial Terms', {
            'fields': ('quote_amount', 'delivery_days', 'payment_terms')
        }),
        ('Evaluation', {
            'fields': ('score', 'evaluation_notes')
        }),
    )


@admin.register(ProcurementSettings)
class ProcurementSettingsAdmin(admin.ModelAdmin):
    list_display = ('entity', 'require_rfq_for_po', 'require_po_for_receipt', 'enable_3way_matching')
    list_filter = ('entity', 'require_rfq_for_po', 'require_po_for_receipt', 'enable_3way_matching')
    search_fields = ('entity__name',)
    
    fieldsets = (
        ('Entity', {
            'fields': ('entity',)
        }),
        ('Policy Requirements', {
            'fields': ('require_rfq_for_po', 'require_po_for_receipt', 'enable_3way_matching', 'require_po_approval')
        }),
        ('Approval Thresholds', {
            'fields': ('po_approval_threshold',)
        }),
        ('Tolerance Settings', {
            'fields': ('quantity_variance_tolerance', 'price_variance_tolerance')
        }),
    )
