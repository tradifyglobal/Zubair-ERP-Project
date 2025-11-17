from django.contrib import admin
from .models import (
    Category, Product, Warehouse, Stock, StockMovement,
    PurchaseOrder, PurchaseOrderLine, InventoryAdjustment, InventoryAdjustmentLine
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'category', 'cost_price', 'selling_price', 'status']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['sku', 'name']
    readonly_fields = ['profit_margin', 'created_at', 'updated_at']


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'contact_person', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'location']


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'quantity_on_hand', 'quantity_reserved', 'quantity_available']
    list_filter = ['warehouse', 'product__status']
    search_fields = ['product__sku', 'product__name', 'warehouse__name']
    readonly_fields = ['product', 'warehouse', 'quantity_on_hand', 'quantity_reserved', 'quantity_available', 'created_at', 'updated_at']
    
    def has_add_permission(self, request):
        """Prevent manual stock addition. Stock levels change through movements, POs, and adjustments."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent stock deletion."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Allow viewing only, no editing."""
        return True


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'movement_type', 'quantity', 'created_at']
    list_filter = ['movement_type', 'warehouse', 'created_at']
    search_fields = ['product__sku', 'reference_number']
    readonly_fields = ['created_at']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'supplier', 'status', 'total_amount', 'expected_delivery_date']
    list_filter = ['status', 'created_at']
    search_fields = ['po_number', 'supplier']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PurchaseOrderLine)
class PurchaseOrderLineAdmin(admin.ModelAdmin):
    list_display = ['purchase_order', 'product', 'quantity_ordered', 'quantity_received', 'line_total']
    list_filter = ['purchase_order__status']
    search_fields = ['purchase_order__po_number', 'product__sku']


@admin.register(InventoryAdjustment)
class InventoryAdjustmentAdmin(admin.ModelAdmin):
    list_display = ['adjustment_number', 'warehouse', 'status', 'reason', 'created_at']
    list_filter = ['status', 'warehouse', 'created_at']
    search_fields = ['adjustment_number', 'reason']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(InventoryAdjustmentLine)
class InventoryAdjustmentLineAdmin(admin.ModelAdmin):
    list_display = ['adjustment', 'product', 'quantity_on_hand', 'quantity_counted', 'quantity_difference']
    search_fields = ['adjustment__adjustment_number', 'product__sku']
