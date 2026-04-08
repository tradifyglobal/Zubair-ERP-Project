from django.contrib import admin
from .models import (RawMaterialCategory, Supplier, RawMaterial, Stock, 
                     StockMovement, PurchaseOrder, GoodsReceiptNote, 
                     AutoReorderSetting, StockAlert, MaterialConsumption)

@admin.register(RawMaterialCategory)
class RawMaterialCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['supplier_code', 'name', 'city', 'country', 'is_active', 'quality_rating']
    search_fields = ['name', 'supplier_code', 'email', 'phone']
    fieldsets = (
        ('Basic Information', {
            'fields': ('supplier_code', 'name', 'email', 'phone')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'country')
        }),
        ('Payment Terms & Credit', {
            'fields': ('payment_terms', 'credit_limit', 'currency')
        }),
        ('Quality Rating', {
            'fields': ('quality_rating',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    readonly_fields = ['created_at']

@admin.register(RawMaterial)
class RawMaterialAdmin(admin.ModelAdmin):
    list_display = ['product_code', 'name', 'category', 'unit_of_measure', 'current_unit_price', 'is_active']
    search_fields = ['product_code', 'name', 'description']
    fieldsets = (
        ('Basic Information', {
            'fields': ('product_code', 'name', 'description', 'category', 'unit_of_measure')
        }),
        ('Regulatory Information', {
            'fields': ('hsn_code',)
        }),
        ('Supplier & Pricing', {
            'fields': ('default_supplier', 'current_unit_price')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    readonly_fields = ['created_at']

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'quantity_on_hand', 'minimum_stock_level', 'maximum_stock_level']
    search_fields = ['raw_material__name', 'raw_material__product_code']
    fieldsets = (
        ('Material', {
            'fields': ('raw_material',)
        }),
        ('Inventory Quantities', {
            'fields': ('quantity_on_hand', 'quantity_reserved', 'quantity_damaged')
        }),
        ('Stock Levels', {
            'fields': ('minimum_stock_level', 'maximum_stock_level', 'reorder_quantity', 'lead_time_days')
        }),
        ('Valuation', {
            'fields': ('valuation_method', 'standard_cost')
        }),
        ('Location', {
            'fields': ('warehouse_location',)
        }),
    )
    readonly_fields = ['updated_at']

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'movement_type', 'quantity', 'created_at']
    search_fields = ['raw_material__name', 'production_order']
    fieldsets = (
        ('Material', {
            'fields': ('raw_material',)
        }),
        ('Movement Details', {
            'fields': ('movement_type', 'quantity', 'unit_price', 'total_value')
        }),
        ('Production Information', {
            'fields': ('production_order',)
        }),
    )
    readonly_fields = ['created_at', 'created_by']

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'supplier', 'raw_material', 'quantity_ordered', 'status']
    search_fields = ['po_number', 'supplier__name', 'raw_material__name']
    fieldsets = (
        ('Purchase Order Details', {
            'fields': ('po_number', 'po_date', 'supplier', 'raw_material')
        }),
        ('Quantities & Pricing', {
            'fields': ('quantity_ordered', 'unit_price')
        }),
        ('Delivery Information', {
            'fields': ('expected_delivery_date', 'quantity_received')
        }),
        ('Status', {
            'fields': ('status',)
        }),
    )
    readonly_fields = ['po_number', 'po_date', 'created_at']

@admin.register(GoodsReceiptNote)
class GoodsReceiptNoteAdmin(admin.ModelAdmin):
    list_display = ['grn_number', 'purchase_order', 'quantity_received', 'quantity_accepted']
    search_fields = ['grn_number', 'purchase_order__po_number']
    fieldsets = (
        ('GRN Information', {
            'fields': ('grn_number', 'purchase_order')
        }),
        ('Receipt Quantities', {
            'fields': ('quantity_received', 'quantity_accepted', 'quantity_rejected')
        }),
        ('Storage & Comments', {
            'fields': ('received_in_location', 'quality_notes')
        }),
    )
    readonly_fields = ['receipt_date', 'created_by']

@admin.register(AutoReorderSetting)
class AutoReorderSettingAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'is_enabled', 'trigger_stock_level', 'auto_reorder_quantity']
    search_fields = ['raw_material__name', 'raw_material__product_code']
    fieldsets = (
        ('Material', {
            'fields': ('raw_material',)
        }),
        ('Auto Reorder Settings', {
            'fields': ('is_enabled', 'trigger_stock_level', 'auto_reorder_quantity')
        }),
        ('Supplier & Notification', {
            'fields': ('preferred_supplier', 'notify_days_before')
        }),
    )
    readonly_fields = ['created_at']

@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'alert_type', 'severity', 'is_active']
    search_fields = ['raw_material__name', 'raw_material__product_code']
    fieldsets = (
        ('Material', {
            'fields': ('raw_material',)
        }),
        ('Alert Details', {
            'fields': ('alert_type', 'severity', 'message')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    readonly_fields = ['created_at']

@admin.register(MaterialConsumption)
class MaterialConsumptionAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'production_order', 'planned_quantity', 'actual_quantity']
    search_fields = ['raw_material__name', 'production_order']
    fieldsets = (
        ('Material & Production', {
            'fields': ('raw_material', 'production_order')
        }),
        ('Quantities', {
            'fields': ('planned_quantity', 'actual_quantity')
        }),
        ('Costing', {
            'fields': ('cost_per_unit',)
        }),
    )
    readonly_fields = ['consumption_date']
