from django.contrib import admin
from django.utils.html import format_html
from .models import (
    RawMaterialCategory, Supplier, RawMaterial, Stock, StockMovement,
    PurchaseOrder, GoodsReceiptNote, AutoReorderSetting, StockAlert, MaterialConsumption
)

# =====================================================================
# Raw Material Category Admin
# =====================================================================

@admin.register(RawMaterialCategory)
class RawMaterialCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


# =====================================================================
# Supplier Admin
# =====================================================================

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['supplier_code', 'name', 'city', 'country', 'quality_rating', 'is_active']
    list_filter = ['is_active', 'country']
    search_fields = ['name', 'supplier_code', 'email', 'phone']
    fieldsets = (
        ('Basic Information', {
            'fields': ('supplier_code', 'name', 'email', 'phone')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Payment & Credit', {
            'fields': ('payment_terms', 'credit_limit', 'currency')
        }),
        ('Performance', {
            'fields': ('quality_rating', 'price_competitiveness')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    readonly_fields = ['created_at']


# =====================================================================
# Raw Material Admin  
# =====================================================================

@admin.register(RawMaterial)
class RawMaterialAdmin(admin.ModelAdmin):
    list_display = ['product_code', 'name', 'category', 'unit_of_measure', 'current_unit_price', 'is_active']
    list_filter = ['is_active', 'category', 'unit_of_measure']
    search_fields = ['product_code', 'name', 'description']
    fieldsets = (
        ('Basic Information', {
            'fields': ('product_code', 'name', 'description', 'category', 'unit_of_measure')
        }),
        ('Specifications', {
            'fields': ('hsn_code', 'density', 'is_hazardous')
        }),
        ('Supplier & Pricing', {
            'fields': ('default_supplier', 'current_unit_price')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    readonly_fields = ['created_at']


# =====================================================================
# Stock Admin
# =====================================================================

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'quantity_on_hand', 'minimum_stock_level', 'status_color']
    list_filter = ['valuation_method', 'warehouse_location']
    search_fields = ['raw_material__name', 'raw_material__product_code']
    fieldsets = (
        ('Material', {
            'fields': ('raw_material',)
        }),
        ('Quantities', {
            'fields': ('quantity_on_hand', 'quantity_reserved', 'quantity_damaged')
        }),
        ('Stock Levels', {
            'fields': ('minimum_stock_level', 'maximum_stock_level', 'reorder_quantity', 'lead_time_days')
        }),
        ('Valuation', {
            'fields': ('valuation_method', 'standard_cost')
        }),
        ('Warehouse', {
            'fields': ('warehouse_location',)
        }),
    )
    
    def status_color(self, obj):
        if obj.quantity_on_hand == 0:
            color = 'red'
            text = 'Out of Stock'
        elif obj.quantity_on_hand < obj.minimum_stock_level:
            color = 'orange'
            text = 'Low Stock'
        else:
            color = 'green'
            text = 'OK'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, text)
    status_color.short_description = 'Stock Status'


# =====================================================================
# Purchase Order Admin
# =====================================================================

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'supplier', 'raw_material', 'quantity_ordered', 'status', 'expected_delivery_date']
    list_filter = ['status', 'po_date', 'expected_delivery_date']
    search_fields = ['po_number', 'supplier__name', 'raw_material__name']
    fieldsets = (
        ('Basic Information', {
            'fields': ('po_number', 'po_date', 'supplier', 'raw_material')
        }),
        ('Order Details', {
            'fields': ('quantity_ordered', 'unit_price')
        }),
        ('Delivery', {
            'fields': ('expected_delivery_date', 'quantity_received')
        }),
        ('Status', {
            'fields': ('status',)
        }),
    )
    readonly_fields = ['po_number', 'po_date', 'created_at']


# =====================================================================
# Goods Receipt Note Admin
# =====================================================================

@admin.register(GoodsReceiptNote)
class GoodsReceiptNoteAdmin(admin.ModelAdmin):
    list_display = ['grn_number', 'purchase_order', 'quantity_received', 'quantity_accepted', 'receipt_date']
    list_filter = ['receipt_date']
    search_fields = ['grn_number', 'purchase_order__po_number']
    fieldsets = (
        ('Basic Information', {
            'fields': ('grn_number', 'purchase_order', 'receipt_date')
        }),
        ('Receipt Details', {
            'fields': ('quantity_received', 'quantity_accepted', 'quantity_rejected')
        }),
        ('Notes', {
            'fields': ('quality_notes',)
        }),
        ('Warehouse', {
            'fields': ('received_in_location',)
        }),
    )
    readonly_fields = ['grn_number', 'receipt_date']


# =====================================================================
# Stock Movement Admin
# =====================================================================

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'movement_type', 'quantity', 'unit_price', 'created_at']
    list_filter = ['movement_type', 'created_at', 'raw_material']
    search_fields = ['raw_material__name', 'production_order']
    fieldsets = (
        ('Movement Information', {
            'fields': ('raw_material', 'movement_type', 'quantity', 'unit_price', 'total_value')
        }),
        ('References', {
            'fields': ('production_order',)
        }),
    )
    readonly_fields = ['total_value', 'created_at']


# =====================================================================
# Auto Reorder Setting Admin
# =====================================================================

@admin.register(AutoReorderSetting)
class AutoReorderSettingAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'is_enabled', 'trigger_stock_level', 'auto_reorder_quantity', 'preferred_supplier']
    list_filter = ['is_enabled']
    search_fields = ['raw_material__name', 'raw_material__product_code']
    fieldsets = (
        ('Raw Material', {
            'fields': ('raw_material',)
        }),
        ('Reorder Configuration', {
            'fields': ('is_enabled', 'trigger_stock_level', 'auto_reorder_quantity', 'notify_days_before')
        }),
        ('Supplier', {
            'fields': ('preferred_supplier',)
        }),
    )
    readonly_fields = ['created_at']


# =====================================================================
# Stock Alert Admin
# =====================================================================

@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'alert_type', 'severity', 'is_active', 'created_at']
    list_filter = ['is_active', 'alert_type', 'severity', 'created_at']
    search_fields = ['raw_material__name', 'message']
    fieldsets = (
        ('Alert Information', {
            'fields': ('raw_material', 'alert_type', 'severity', 'message')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    readonly_fields = ['created_at']


# =====================================================================
# Material Consumption Admin
# =====================================================================

@admin.register(MaterialConsumption)
class MaterialConsumptionAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'production_order', 'planned_quantity', 'actual_quantity', 'consumption_date']
    list_filter = ['consumption_date', 'raw_material']
    search_fields = ['raw_material__name', 'production_order']
    fieldsets = (
        ('Production Consumption', {
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
